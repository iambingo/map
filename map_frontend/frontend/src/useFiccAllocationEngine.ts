import { computed, type ComputedRef } from 'vue';

export type FiccDimKey = 'position' | 'duration' | 'equity';
export type FiccProductKey = 'lowVol' | 'midLowVol';

export interface FiccBallotScore {
  position: number;
  duration: number;
  equity: number;
}

export interface FiccProductDecision {
  position: string;
  duration: string;
  equity: string;
}

interface UseFiccAllocationEngineParams {
  ficcProductDecisions: Record<FiccProductKey, FiccProductDecision>;
  ficcSelfVoteSubmitted: ComputedRef<FiccBallotScore | null>;
  ficcDraftScores: ComputedRef<FiccBallotScore>;
  FICC_PRODUCT_LABELS: Record<FiccProductKey, string>;
  FICC_PRODUCT_COLORS: Record<FiccProductKey, string>;
}

export function useFiccAllocationEngine(params: UseFiccAllocationEngineParams) {
  const FICC_POSITION_TIERS = [
    { label: '低配', lo: 0, hi: 33 },
    { label: '平配', lo: 34, hi: 66 },
    { label: '高配', lo: 67, hi: 100 },
  ];
  const FICC_DURATION_TIERS = [
    { label: '谨慎', range: '20%-35%', lo: 0, hi: 35 },
    { label: '中性偏谨', range: '35%-50%', lo: 36, hi: 50 },
    { label: '中性', range: '50%-70%', lo: 51, hi: 70 },
    { label: '中性偏乐', range: '70%-90%', lo: 71, hi: 90 },
    { label: '乐观', range: '90%-110%', lo: 91, hi: 100 },
  ];
  const FICC_EQUITY_TIERS = [
    { label: '谨慎', range: '0-20%', lo: 0, hi: 20 },
    { label: '中性偏谨', range: '20-40%', lo: 21, hi: 40 },
    { label: '中性', range: '40-60%', lo: 41, hi: 60 },
    { label: '中性偏乐', range: '60-80%', lo: 61, hi: 80 },
    { label: '乐观', range: '80-100%', lo: 81, hi: 100 },
  ];

  const FICC_DIM_TIERS: Record<FiccDimKey, { label: string; value: number }[]> = {
    position: FICC_POSITION_TIERS.map(t => ({ label: t.label, value: Math.round((t.lo + t.hi) / 2) })),
    duration: FICC_DURATION_TIERS.map(t => ({ label: t.label, value: Math.round((t.lo + t.hi) / 2) })),
    equity: FICC_EQUITY_TIERS.map(t => ({ label: t.label, value: Math.round((t.lo + t.hi) / 2) })),
  };

  const FICC_POSITION_TRANSLATION: Record<FiccProductKey, Record<string, number>> = {
    lowVol: { '低配': 70, '平配': 75, '高配': 80 },
    midLowVol: { '低配': 20, '平配': 25, '高配': 30 },
  };

  const FICC_DURATION_MAP: Record<FiccProductKey, Record<string, string>> = {
    lowVol: { '谨慎': '0.05-0.09', '中性偏谨': '0.09-0.13', '中性': '0.13-0.18', '中性偏乐': '0.18-0.23', '乐观': '0.23-0.28' },
    midLowVol: { '谨慎': '0.30-0.53', '中性偏谨': '0.53-0.75', '中性': '0.75-1.05', '中性偏乐': '1.05-1.35', '乐观': '1.35-1.65' },
  };

  const FICC_EQUITY_MAP: Record<FiccProductKey, Record<string, string>> = {
    lowVol: { '谨慎': '0%', '中性偏谨': '0%', '中性': '0%', '中性偏乐': '0%', '乐观': '0%' },
    midLowVol: { '谨慎': '0-0.6%', '中性偏谨': '0.6-1.2%', '中性': '1.2-1.8%', '中性偏乐': '1.8-2.4%', '乐观': '2.4-3%' },
  };

  function ficcTierForScore(dim: FiccDimKey, score: number): string {
    const tiers = dim === 'position' ? FICC_POSITION_TIERS : dim === 'duration' ? FICC_DURATION_TIERS : FICC_EQUITY_TIERS;
    const found = tiers.find(t => score >= t.lo && score <= t.hi);
    return found ? found.label : tiers[0].label;
  }

  function ficcPositionFromTier(productKey: FiccProductKey, tier: string): number {
    return FICC_POSITION_TRANSLATION[productKey]?.[tier] ?? 0;
  }

  function ficcDurationUsageRange(tier: string): string {
    return FICC_DURATION_TIERS.find(x => x.label === tier)?.range ?? '—';
  }

  function ficcEquityUsageRange(tier: string): string {
    return FICC_EQUITY_TIERS.find(x => x.label === tier)?.range ?? '—';
  }

  function ficcDecisionHint(productKey: FiccProductKey, dim: FiccDimKey, tier: string): string {
    if (!tier) return '请选择档位';
    if (dim === 'position') return `对应仓位 ${ficcPositionFromTier(productKey, tier)}%`;
    if (dim === 'duration') return `对应久期上限 ${ficcDurationUsageRange(tier)}`;
    return `对应含权上限 ${ficcEquityUsageRange(tier)}`;
  }

  function parseRangeCenter(raw: string): number {
    if (!raw || raw === '—') return 0;
    const cleaned = raw.replace(/%/g, '').trim();
    if (cleaned.includes('-')) {
      const [a, b] = cleaned.split('-').map(v => Number(v));
      if (!Number.isFinite(a) || !Number.isFinite(b)) return 0;
      return (a + b) / 2;
    }
    const n = Number(cleaned);
    return Number.isFinite(n) ? n : 0;
  }

  function fmtPct(val: number): string {
    return Number.isInteger(val) ? `${val}%` : `${val.toFixed(2)}%`;
  }

  const selfVoteSuggestion = computed(() => {
    const base = params.ficcSelfVoteSubmitted.value ?? params.ficcDraftScores.value;
    const positionTier = ficcTierForScore('position', base.position);
    const durationTier = ficcTierForScore('duration', base.duration);
    const equityTier = ficcTierForScore('equity', base.equity);
    return {
      positionTier,
      durationTier,
      equityTier,
      positionPct: ficcPositionFromTier('lowVol', positionTier),
      durationLowVol: FICC_DURATION_MAP.lowVol[durationTier] ?? '—',
      durationMidLowVol: FICC_DURATION_MAP.midLowVol[durationTier] ?? '—',
      equityLowVol: FICC_EQUITY_MAP.lowVol[equityTier] ?? '—',
      equityMidLowVol: FICC_EQUITY_MAP.midLowVol[equityTier] ?? '—',
    };
  });

  const ficcGuidanceTable = computed(() => (Object.keys(params.FICC_PRODUCT_LABELS) as FiccProductKey[]).map(pk => {
    const d = params.ficcProductDecisions[pk];
    const posPct = ficcPositionFromTier(pk, d.position);
    const durRange = FICC_DURATION_MAP[pk]?.[d.duration] || '—';
    const eqCap = FICC_EQUITY_MAP[pk]?.[d.equity] || '—';
    return {
      product: params.FICC_PRODUCT_LABELS[pk],
      color: params.FICC_PRODUCT_COLORS[pk],
      key: pk,
      position: posPct,
      positionTier: d.position || '—',
      durationRange: durRange,
      durationTier: d.duration || '—',
      equityCap: eqCap,
      equityTier: d.equity || '—',
    };
  }));

  const FICC_POSITION_BASE = {
    lowVol: {
      liquidity: 6,
      stableAsset: 75,
      constantDurationCredit: 19,
      unifiedAdjustment: 0,
      activeTrading: 0,
      equityUsage: 0,
      durationCenter: 0.15,
    },
    midLowVol: {
      liquidity: 6,
      stableAsset: 25,
      unifiedAdjustment: 6,
      constantDurationCredit: 46.85,
      activeTrading: 9.9,
      equityUsage: 1.5,
      durationCenter: 0.9,
    },
  } as const;

  const ficcAllocationDetailRows = computed(() => (Object.keys(params.FICC_PRODUCT_LABELS) as FiccProductKey[]).map(pk => {
    const decision = params.ficcProductDecisions[pk];
    const base = FICC_POSITION_BASE[pk];
    const selectedStable = ficcPositionFromTier(pk, decision.position);
    const stableDelta = selectedStable - base.stableAsset;
    const durationRange = FICC_DURATION_MAP[pk]?.[decision.duration] || '—';
    const durationTarget = decision.duration ? parseRangeCenter(durationRange) : base.durationCenter;
    const equityRange = FICC_EQUITY_MAP[pk]?.[decision.equity] || '—';
    const equityTarget = decision.equity ? parseRangeCenter(equityRange) : base.equityUsage;

    const row = {
      key: pk,
      product: params.FICC_PRODUCT_LABELS[pk],
      color: params.FICC_PRODUCT_COLORS[pk],
      liquidity: base.liquidity,
      stableAsset: selectedStable || base.stableAsset,
      unifiedAdjustment: base.unifiedAdjustment,
      constantDurationCredit: base.constantDurationCredit,
      activeTrading: base.activeTrading,
      equityUsage: equityTarget,
      durationBase: base.durationCenter,
      durationTarget,
      durationRange,
      stableDelta,
      unifiedDelta: 0,
      durationDeviationPct: base.durationCenter > 0 ? ((durationTarget - base.durationCenter) / base.durationCenter) * 100 : 0,
    };

    if (pk === 'lowVol') {
      row.constantDurationCredit = base.constantDurationCredit - stableDelta;
    } else {
      row.unifiedAdjustment = base.unifiedAdjustment - stableDelta;
      row.unifiedDelta = row.unifiedAdjustment - base.unifiedAdjustment;
    }
    return row;
  }));

  const ficcDeviationWarnings = computed(() => {
    const warnings: string[] = [];
    for (const row of ficcAllocationDetailRows.value) {
      if (Math.abs(row.durationDeviationPct) > 5) {
        warnings.push(`${row.product}：组合久期偏离 ${row.durationDeviationPct.toFixed(1)}%，超过 ±5% 控制线`);
      }
      if (Math.abs(row.stableDelta) > 5) {
        warnings.push(`${row.product}：稳定资产偏离 ${row.stableDelta.toFixed(1)}%，超过 ±5% 控制线`);
      }
      if (row.key === 'midLowVol') {
        if (Math.abs(row.unifiedDelta) > 1) {
          warnings.push(`${row.product}：统一调节仓位偏离 ${row.unifiedDelta.toFixed(1)}%，超过 ±1%`);
        }
        if (Math.abs(row.durationDeviationPct) > 10) {
          warnings.push(`${row.product}：统一调节久期联动偏离 ${row.durationDeviationPct.toFixed(1)}%，超过 ±10%（被动超限需一周内调整完成）`);
        }
      }
    }
    return warnings;
  });

  return {
    FICC_POSITION_TIERS,
    FICC_DURATION_TIERS,
    FICC_EQUITY_TIERS,
    FICC_DIM_TIERS,
    ficcTierForScore,
    ficcDecisionHint,
    selfVoteSuggestion,
    ficcGuidanceTable,
    ficcAllocationDetailRows,
    ficcDeviationWarnings,
    fmtPct,
  };
}

