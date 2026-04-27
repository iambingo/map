import { ref, computed } from 'vue';
import axios from 'axios';
import { http } from '@/api/request';

/**
 * 方案 A：为 true 时不请求 portal-snapshot / committee/page-context，仅用前端 Mock，避免后端 500 等打断联调。
 * 在 frontend/.env 设置：VITE_COMMITTEE_OFFLINE_MOCK=true（改后需重启 Vite）。
 */
export function isCommitteeOfflineMock(): boolean {
  const v = import.meta.env.VITE_COMMITTEE_OFFLINE_MOCK;
  return v === 'true' || v === '1';
}

// ═══════════════════════════════════════════════════════════════════════════
// 1. 用户与角色
// ═══════════════════════════════════════════════════════════════════════════

export type Role =
  | '班子'
  | '部门长'
  | '投资经理'
  | '投资助理'
  | '投管'
  | '混合投资委员会秘书'
  | '混合投资委员会委员'
  | '混合投资委员会主任委员'
  | 'FICC投资委员会秘书'
  | 'FICC投资委员会委员'
  | 'FICC投资委员会主任委员';

export const activeRole = ref<Role>('投资经理');

export const ROLES: Role[] = [
  '班子',
  '部门长',
  '投资经理',
  '投资助理',
  '投管',
  '混合投资委员会秘书',
  '混合投资委员会委员',
  '混合投资委员会主任委员',
  'FICC投资委员会秘书',
  'FICC投资委员会委员',
  'FICC投资委员会主任委员',
];

// ═══════════════════════════════════════════════════════════════════════════
// 2. T+N 时间轴推演引擎
// ═══════════════════════════════════════════════════════════════════════════

export type TimelineState = 0 | 1 | 2 | 3;
export const timelineState = ref<TimelineState>(0);

// ═══════════════════════════════════════════════════════════════════════════
// 3. 通道型 SPV 嵌套穿透模式
// ═══════════════════════════════════════════════════════════════════════════

export const isPenetrationMode = ref(false);

// ═══════════════════════════════════════════════════════════════════════════
// 4. FICC 投委会决议广播
// ═══════════════════════════════════════════════════════════════════════════
export interface FiccDecisionPayload {
  meetingCode: string;
  confirmedAt: string;
  products: { name: string; position: string; durationRange: string; equityCap: string }[];
}
export const ficcLatestDecision = ref<FiccDecisionPayload | null>(null);

// ═══════════════════════════════════════════════════════════════════════════
// 4. 场景状态：建仓 / 调仓
// ═══════════════════════════════════════════════════════════════════════════

export type OperationScene = '建仓' | '调仓';
export const operationScene = ref<OperationScene>('调仓');

// ═══════════════════════════════════════════════════════════════════════════
// 5. 模型跳转缓存
// ═══════════════════════════════════════════════════════════════════════════

export const modelBackPath = ref('');

// ═══════════════════════════════════════════════════════════════════════════
// 6. 组件全屏放大状态
// ═══════════════════════════════════════════════════════════════════════════

export const maximizedComponent = ref<string | null>(null);

export function setMaximized(id: string) {
  maximizedComponent.value = id;
}

export function clearMaximized() {
  maximizedComponent.value = null;
}

// ═══════════════════════════════════════════════════════════════════════════
// 7. 再平衡跳转目标（沙盘携带任务）
// ═══════════════════════════════════════════════════════════════════════════

export interface RebalanceTarget {
  productId: string;
  gapAmount: number;
}
export const rebalanceTarget = ref<RebalanceTarget | null>(null);

// ═══════════════════════════════════════════════════════════════════════════
// 8. 持仓数据模型
// ═══════════════════════════════════════════════════════════════════════════

export interface PositionRow {
  code: string;
  name: string;
  assetClass: string;
  weightPct: number;
  mktValueWan: number;
  pnl: number;
  duration?: number;
  [key: string]: unknown;
}

export interface ProFormaRow extends PositionRow {
  _isModified: boolean;
  _amountDelta: number;
  _weightDelta: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// 9. 全局任务篮
// ═══════════════════════════════════════════════════════════════════════════

export interface TaskBasketItem {
  id: string;
  type: 'buy' | 'sell';
  assetName: string;
  assetCode: string;
  amount: number;
  source: '模型' | '手动' | '批量';
  status: 'pending' | 'confirmed' | 'executed';
  weightDelta: number;
  productId: string;
  [key: string]: unknown;
}

export type BasketInstruction = TaskBasketItem;

export const taskBasket = ref<TaskBasketItem[]>([]);

let _basketIdSeq = 0;

export function addToBasket(item: Omit<TaskBasketItem, 'id'>): string {
  const id = `bask_${++_basketIdSeq}_${Date.now()}`;
  const entry: TaskBasketItem = { ...item, id } as TaskBasketItem;
  taskBasket.value = [...taskBasket.value, entry];
  return id;
}

export function removeFromBasket(id: string) {
  taskBasket.value = taskBasket.value.filter(item => item.id !== id);
}

export function clearBasket() {
  taskBasket.value = [];
}

export const basketSummary = computed(() => {
  const items = taskBasket.value;
  const totalBuy = items.filter(i => i.type === 'buy').reduce((s, i) => s + i.amount, 0);
  const totalSell = items.filter(i => i.type === 'sell').reduce((s, i) => s + i.amount, 0);
  const netDelta = totalBuy - totalSell;
  const pendingCount = items.filter(i => i.status === 'pending').length;
  const confirmedCount = items.filter(i => i.status === 'confirmed').length;
  return { totalBuy, totalSell, netDelta, pendingCount, confirmedCount, totalCount: items.length };
});

// ═══════════════════════════════════════════════════════════════════════════
// 10. ProForma 持仓叠加引擎 (动态推演)
// ═══════════════════════════════════════════════════════════════════════════

export const isApplyingBasket = ref(false);

export const actualPositions = ref<PositionRow[]>([]);

export const proFormaData = computed<ProFormaRow[]>(() => {
  const isBuilding = operationScene.value === '建仓';

  const base: PositionRow[] = isBuilding
    ? []
    : actualPositions.value;

  if (!isApplyingBasket.value && !isBuilding) return base as ProFormaRow[];

  const instructions = taskBasket.value;
  if (instructions.length === 0 && !isBuilding) return base as ProFormaRow[];

  const codeMap = new Map<string, ProFormaRow>();

  for (const pos of base) {
    codeMap.set(pos.code, {
      ...pos,
      _isModified: false,
      _amountDelta: 0,
      _weightDelta: 0,
    });
  }

  const totalMktValue = base.reduce((s, p) => s + p.mktValueWan, 0);

  for (const inst of instructions) {
    const code = inst.assetCode;
    const deltaAmt = inst.type === 'buy' ? inst.amount : -inst.amount;

    if (codeMap.has(code)) {
      const existing = codeMap.get(code)!;
      existing._amountDelta += deltaAmt;
      existing._weightDelta += inst.weightDelta;
      existing.mktValueWan += deltaAmt;
      existing._isModified = true;
    } else {
      const row: ProFormaRow = {
        code,
        name: inst.assetName,
        assetClass: '待分类',
        weightPct: 0,
        mktValueWan: deltaAmt,
        pnl: 0,
        duration: 0,
        _isModified: true,
        _amountDelta: deltaAmt,
        _weightDelta: inst.weightDelta,
      };
      codeMap.set(code, row);
    }
  }

  const newTotalMktValue = totalMktValue
    + instructions.reduce((s, i) => s + (i.type === 'buy' ? i.amount : -i.amount), 0);

  const denominator = isBuilding
    ? Math.max(newTotalMktValue, 1)
    : Math.max(totalMktValue, 1);

  for (const row of codeMap.values()) {
    if (row.mktValueWan > 0 && denominator > 0) {
      row.weightPct = (row.mktValueWan / denominator) * 100;
    }
  }

  return Array.from(codeMap.values());
});

export const proFormaSummary = computed(() => {
  const data = proFormaData.value;
  if (data.length === 0) return { totalMktValue: 0, modifiedCount: 0, weightedDuration: 0 };

  const totalMktValue = data.reduce((s, r) => s + r.mktValueWan, 0);
  const modifiedCount = data.filter(r => r._isModified).length;
  const weightedDuration = data.reduce((s, r) => {
    const w = totalMktValue > 0 ? r.mktValueWan / totalMktValue : 0;
    return s + (r.duration ?? 0) * w;
  }, 0);

  return { totalMktValue, modifiedCount, weightedDuration };
});

// ═══════════════════════════════════════════════════════════════════════════
// 11. 投委会决议（门户 BFF 快照，替代 Committee 内硬编码 decisionTable）
// ═══════════════════════════════════════════════════════════════════════════

/** 与 CommitteeView 中决议表结构对齐，供组件直接绑定 */
export interface CommitteeDecisionChild {
  asset: string;
  sub: string;
  color: string;
  level: string;
  bubbles: string[];
  logic: string;
}

export interface CommitteeDecisionGroup {
  asset: string;
  sub: string;
  color: string;
  level: string;
  logic: string;
  children: CommitteeDecisionChild[];
}

/** 原 CommitteeView.vue 中硬编码的默认决议表（作为回退） */
const DEFAULT_COMMITTEE_DECISION_TABLE: CommitteeDecisionGroup[] = [
  {
    asset: '债券',
    sub: '固定收益',
    color: '#22D3EE',
    level: '中性偏乐观',
    logic: '利率下行趋势确立，久期可适度拉长',
    children: [
      {
        asset: '利率债',
        sub: '国债/政金债',
        color: '#22D3EE',
        level: '中性偏乐观',
        bubbles: ['利率下行趋势', '期限利差收窄'],
        logic: '长端利率仍有下行空间，增配10Y以上品种',
      },
    ],
  },
  {
    asset: '权益',
    sub: '股票/混合',
    color: '#3B9EFF',
    level: '乐观',
    logic: '估值低位，政策托底明确，结构性机会突出',
    children: [
      {
        asset: '红利',
        sub: '高股息策略',
        color: '#3B9EFF',
        level: '乐观',
        bubbles: ['防御属性', '股息率优势'],
        logic: '高股息策略在震荡市中具备确定性优势',
      },
      {
        asset: '偏股混',
        sub: '主动权益',
        color: '#3B9EFF',
        level: '中性偏乐观',
        bubbles: ['选股Alpha', '结构分化'],
        logic: '关注景气度反转行业，控制仓位',
      },
      {
        asset: '恒生科技',
        sub: '港股科技',
        color: '#3B9EFF',
        level: '中性',
        bubbles: ['估值修复', '政策风险'],
        logic: '估值处于历史低位但需关注政策不确定性',
      },
    ],
  },
  {
    asset: '另类',
    sub: '黄金/商品',
    color: '#F1C40F',
    level: '中性',
    logic: '地缘风险支撑金价，但需关注美联储政策转向',
    children: [
      {
        asset: '黄金',
        sub: '贵金属',
        color: '#F1C40F',
        level: '中性偏乐观',
        bubbles: ['避险需求', '去美元化'],
        logic: '全球央行持续增持，避险需求支撑',
      },
    ],
  },
  {
    asset: '现金',
    sub: '货币类',
    color: '#94A3B8',
    level: '中性',
    logic: '维持基础流动性，关注赎回节奏',
    children: [
      {
        asset: '现金',
        sub: '货币市场',
        color: '#94A3B8',
        level: '中性',
        bubbles: ['流动性管理', '赎回备付'],
        logic: '保持适度现金比例应对潜在赎回',
      },
    ],
  },
];

export const committeeDecisionTable = ref<CommitteeDecisionGroup[]>(
  JSON.parse(JSON.stringify(DEFAULT_COMMITTEE_DECISION_TABLE)) as CommitteeDecisionGroup[],
);

// ═══════════════════════════════════════════════════════════════════════════
// 12. 部门资配决策（投委会 Step 3 正式提交后写入，可供其他页面读取）
// ═══════════════════════════════════════════════════════════════════════════

export interface DeptAllocationDecisionProduct {
  id: string;
  name: string;
  bond: number;
  equity: number;
  alt: number;
  liquidity: number;
}

export interface DeptAllocationDecision {
  period: string;
  decidedAt: string;
  decidedBy: string;
  bondGrade: string;
  bondDuration: string;
  equityGrade: number;
  equityGradeLabel: string;
  equityMix: { 红利: number; 成长: number; 价值: number };
  altNotes: string;
  products: DeptAllocationDecisionProduct[];
}

/** 投委会正式提交的部门资产配置决策结果，供 MAP 其他页面读取 */
export const deptAllocationDecision = ref<DeptAllocationDecision | null>(null);

export interface PortalSnapshotChoiceResult {
  winner: string;
  vote_counts: Record<string, number>;
}

export interface PortalSnapshot {
  snapshot_at: string;
  is_stale: boolean;
  stale_reason: string | null;
  taa_guidance: {
    source_resolution: { resolution_id?: number; meeting_id?: number; published_at?: string | null } | null;
    choice_results: Record<string, PortalSnapshotChoiceResult>;
    numeric_results: Record<string, Record<string, unknown>>;
    published_at: string | null;
  };
  positions: Record<string, unknown> | null;
  deviation_analysis: Record<string, unknown>;
  rebalance_urgency: { level: string; reason: string };
  navigation_tiles: Array<Record<string, unknown>>;
}

const ROLE_QUERY: Record<Role, string> = {
  班子: 'ADMIN',
  部门长: 'COMMITTEE_MEMBER',
  投资经理: 'PM',
  投资助理: 'ANALYST',
  投管: 'PM',
  混合投资委员会秘书: 'COMMITTEE_SECRETARY',
  混合投资委员会委员: 'COMMITTEE_MEMBER',
  混合投资委员会主任委员: 'COMMITTEE_CHAIR',
  FICC投资委员会秘书: 'FICC_SECRETARY',
  FICC投资委员会委员: 'FICC_MEMBER',
  FICC投资委员会主任委员: 'FICC_CHAIR',
};

const TAA_KEY_META: Record<
  string,
  { asset: string; sub: string; color: string; childAsset: string; childSub: string }
> = {
  equity_view: {
    asset: '权益',
    sub: '股票/混合',
    color: '#3B9EFF',
    childAsset: '股票',
    childSub: '投委指引',
  },
  bond_view: {
    asset: '债券',
    sub: '固定收益',
    color: '#22D3EE',
    childAsset: '债券',
    childSub: '投委指引',
  },
  commodity_view: {
    asset: '另类',
    sub: '黄金/商品',
    color: '#F1C40F',
    childAsset: '商品',
    childSub: '投委指引',
  },
  cash_view: {
    asset: '现金',
    sub: '货币类',
    color: '#94A3B8',
    childAsset: '现金',
    childSub: '投委指引',
  },
};

function winnerToCN(w: string): string {
  const m: Record<string, string> = {
    overweight: '乐观',
    neutral: '中性',
    underweight: '谨慎',
  };
  return m[w] ?? w;
}

/** 由 choice_results（门户快照或 ic_resolutions.aggregated_taa）生成决议表行 */
function mapChoiceResultsToDecisionTable(
  cr: Record<string, PortalSnapshotChoiceResult>,
): CommitteeDecisionGroup[] {
  const keys = Object.keys(cr);
  if (keys.length === 0) return [];

  const groups: CommitteeDecisionGroup[] = [];
  for (const key of keys) {
    const meta = TAA_KEY_META[key];
    if (!meta) continue;
    const row = cr[key];
    if (!row?.winner) continue;
    const level = winnerToCN(row.winner);
    const counts = row.vote_counts ?? {};
    const bubbles = Object.entries(counts).map(([k, v]) => `${k}:${v}票`);
    const logic = `投委众数：${row.winner}（${Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => `${k} ${v}`)
      .join('，')}）`;
    groups.push({
      asset: meta.asset,
      sub: meta.sub,
      color: meta.color,
      level,
      logic,
      children: [
        {
          asset: meta.childAsset,
          sub: meta.childSub,
          color: meta.color,
          level,
          bubbles: bubbles.length ? bubbles : ['（无分项票数）'],
          logic,
        },
      ],
    });
  }
  return groups;
}

function mapPortalToDecisionTable(snapshot: PortalSnapshot): CommitteeDecisionGroup[] {
  return mapChoiceResultsToDecisionTable(snapshot.taa_guidance?.choice_results ?? {});
}

/** page-context 返回的 aggregated_taa 与门户结构一致时，提取 choice_results */
function choiceResultsFromAggregatedTaa(
  aggregated: Record<string, unknown> | undefined,
): Record<string, PortalSnapshotChoiceResult> | null {
  if (!aggregated || typeof aggregated !== 'object') return null;
  const raw = aggregated.choice_results;
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  return raw as Record<string, PortalSnapshotChoiceResult>;
}

export const portalSnapshot = ref<PortalSnapshot | null>(null);
export const portalSnapshotLoading = ref(false);
export const portalSnapshotError = ref<string | null>(null);

/** GET /v1/committee/page-context — 会议元数据 + 投票摘要（与门户快照并行拉取） */
export interface CommitteeVoteRowDTO {
  user_id: number;
  submitted_at: string | null;
}

export interface CommitteeMeetingSummaryDTO {
  id: number;
  meeting_code: string;
  title: string;
  type: string;
  status: string;
  scheduled_at: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface CommitteeResolutionSummaryDTO {
  id: number;
  meeting_id: number;
  aggregated_taa: Record<string, unknown>;
  ai_minutes: string | null;
  published_at: string | null;
  published_by: number | null;
  created_at: string;
}

export interface CommitteePageContextDTO {
  meeting: CommitteeMeetingSummaryDTO | null;
  resolution: CommitteeResolutionSummaryDTO | null;
  votes: CommitteeVoteRowDTO[];
}

export const committeePageContext = ref<CommitteePageContextDTO | null>(null);
export const committeeContextLoading = ref(false);
export const committeeContextError = ref<string | null>(null);

function formatAxiosError(e: unknown): string {
  if (axios.isAxiosError(e)) {
    const d = e.response?.data;
    if (typeof d === 'object' && d && 'detail' in d) {
      return String((d as { detail: unknown }).detail);
    }
    return e.message;
  }
  if (e instanceof Error) return e.message;
  return String(e);
}

/**
 * 拉取门户 BFF 快照，用后端 `taa_guidance.choice_results` 覆盖投委会决议表（有数据时）。
 * GET /api/v1/workspace/portal-snapshot（axios baseURL=/api → 路径 /v1/workspace/portal-snapshot）
 * （MAP 门户默认 Tab 使用；投委会 Tab 请用 fetchCommitteePageData）
 */
export async function fetchMeetingResolution() {
  if (isCommitteeOfflineMock()) {
    portalSnapshotLoading.value = false;
    portalSnapshotError.value = null;
    portalSnapshot.value = null;
    return;
  }
  portalSnapshotLoading.value = true;
  portalSnapshotError.value = null;
  const path = '/v1/workspace/portal-snapshot';
  const role = ROLE_QUERY[activeRole.value] ?? 'PM';
  try {
    const { data } = await http.get<PortalSnapshot>(path, {
      params: { role },
    });
    portalSnapshot.value = data;
    const mapped = mapPortalToDecisionTable(data);
    if (mapped.length > 0) {
      committeeDecisionTable.value = mapped;
    }
  } catch (e: unknown) {
    portalSnapshotError.value = formatAxiosError(e);
  } finally {
    portalSnapshotLoading.value = false;
  }
}

/**
 * 投委会视图专用：并行请求门户快照 + 投委会只读上下文，互不拖死（allSettled）。
 * - 决议表仍来自 portal-snapshot 的 choice_results（有则覆盖，无则保留默认 Mock 表）
 * - 会议编号 / 投票条数等来自 committee/page-context
 */
export async function fetchCommitteePageData() {
  if (isCommitteeOfflineMock()) {
    portalSnapshotLoading.value = false;
    committeeContextLoading.value = false;
    portalSnapshotError.value = null;
    committeeContextError.value = null;
    portalSnapshot.value = null;
    committeePageContext.value = null;
    // eslint-disable-next-line no-console
    console.log(
      '%c📴 [CommitteeView API]',
      'color:#94A3B8;font-weight:bold',
      'VITE_COMMITTEE_OFFLINE_MOCK 已开启：跳过 portal-snapshot 与 committee/page-context',
    );
    return;
  }
  // eslint-disable-next-line no-console
  console.log(
    '%c🚀 [CommitteeView API]',
    'color:#22D3EE;font-weight:bold',
    '开始拉取投委会页数据（portal-snapshot ∥ committee/page-context）',
  );
  portalSnapshotLoading.value = true;
  committeeContextLoading.value = true;
  portalSnapshotError.value = null;
  committeeContextError.value = null;

  const pathSnap = '/v1/workspace/portal-snapshot';
  const pathCtx = '/v1/committee/page-context';
  const role = ROLE_QUERY[activeRole.value] ?? 'PM';
  const base = http.defaults.baseURL ?? '';
  // eslint-disable-next-line no-console
  console.log(
    '%c🚀 [CommitteeView API]',
    'color:#22D3EE;font-weight:bold',
    '即将发出请求',
    { pathSnap, pathCtx, role, axiosBaseURL: base },
  );

  try {
    const [snapRes, ctxRes] = await Promise.allSettled([
      http.get<PortalSnapshot>(pathSnap, { params: { role } }),
      http.get<CommitteePageContextDTO>(pathCtx),
    ]);

    let portalMappedRows = 0;

    if (snapRes.status === 'fulfilled') {
      const data = snapRes.value.data;
      portalSnapshot.value = data;
      const mapped = mapPortalToDecisionTable(data);
      portalMappedRows = mapped.length;
      if (mapped.length > 0) {
        committeeDecisionTable.value = mapped;
      }
      // eslint-disable-next-line no-console
      console.log(
        '%c✅ [CommitteeView API]',
        'color:#34C759;font-weight:bold',
        'portal-snapshot 成功',
        {
          is_stale: data.is_stale,
          stale_reason: data.stale_reason,
          choiceKeys: Object.keys(data.taa_guidance?.choice_results ?? {}),
          mappedRows: mapped.length,
        },
      );
    } else {
      portalSnapshotError.value = formatAxiosError(snapRes.reason);
      // eslint-disable-next-line no-console
      console.error('%c❌ [CommitteeView API]', 'color:#F97316;font-weight:bold', 'portal-snapshot 失败', snapRes.reason);
    }

    if (ctxRes.status === 'fulfilled') {
      const ctx = ctxRes.value.data;
      committeePageContext.value = {
        meeting: ctx.meeting ?? null,
        resolution: ctx.resolution ?? null,
        votes: Array.isArray(ctx.votes) ? ctx.votes : [],
      };
      /** 门户快照无 choice_results 时，用 resolutions 表第一条的 aggregated_taa 填决议表 */
      if (portalMappedRows === 0 && ctx.resolution?.aggregated_taa) {
        const cr = choiceResultsFromAggregatedTaa(
          ctx.resolution.aggregated_taa as Record<string, unknown>,
        );
        if (cr) {
          const fromDb = mapChoiceResultsToDecisionTable(cr);
          if (fromDb.length > 0) {
            committeeDecisionTable.value = fromDb;
          }
        }
      }
      // eslint-disable-next-line no-console
      console.log(
        '%c✅ [CommitteeView API]',
        'color:#34C759;font-weight:bold',
        'committee/page-context 成功',
        {
          meetingCode: ctx.meeting?.meeting_code ?? null,
          voteRows: committeePageContext.value.votes.length,
          hasResolution: !!ctx.resolution,
        },
      );
    } else {
      committeeContextError.value = formatAxiosError(ctxRes.reason);
      committeePageContext.value = { meeting: null, resolution: null, votes: [] };
      // eslint-disable-next-line no-console
      console.error('%c❌ [CommitteeView API]', 'color:#F97316;font-weight:bold', 'committee/page-context 失败', ctxRes.reason);
    }
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('%c❌ [CommitteeView API]', 'color:#F97316;font-weight:bold', '未预期的同步错误', e);
  } finally {
    portalSnapshotLoading.value = false;
    committeeContextLoading.value = false;
    // eslint-disable-next-line no-console
    console.log('%c🏁 [CommitteeView API]', 'color:#94A3B8;font-weight:bold', '拉取流程结束');
  }
}
