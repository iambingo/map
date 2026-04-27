<template>
  <div class="flex h-full bg-[#050505] text-[#E5E5E5] overflow-hidden font-sans">

    <!-- ═══ LEFT PANEL: Viewpoint & Constraints ═══ -->
    <div class="w-1/3 max-w-[480px] min-w-[360px] shrink-0 bg-[#0A0A0A] border-r border-[#1A1A1A] flex flex-col overflow-hidden shadow-[4px_0_24px_rgba(0,0,0,0.5)]">

      <!-- Header -->
      <div class="px-5 pt-3 pb-0 bg-gradient-to-b from-[#151515] to-[#0F0F0F]">
        <button
          @click="handleBack"
          class="flex items-center text-[#94A3B8] hover:text-[#CBD5E1] transition-all duration-150 text-xs font-mono group mb-2.5"
        >
          <ArrowLeft class="w-3 h-3 mr-1 group-hover:-translate-x-0.5 transition-transform duration-150" />
          {{ props.embedded ? '退出沙盘' : '门户枢纽' }}
        </button>
      </div>
      <div class="px-5 pb-4 border-b border-[#1A1A1A] flex items-center space-x-3 bg-gradient-to-b from-[#0F0F0F] to-[#0A0A0A]">
        <div class="w-8 h-8 rounded bg-red-900/30 border border-red-500/30 flex items-center justify-center shadow-[0_0_12px_rgba(239,68,68,0.15)]">
          <DataAnalysis class="w-[15px] h-[15px] text-red-400" />
        </div>
        <div>
          <h2 class="text-[15px] font-bold text-white tracking-wider">SAA 战略沙盘</h2>
          <p class="text-[10px] text-red-400/60 font-mono uppercase tracking-widest">Monte Carlo Simulator</p>
        </div>
      </div>

      <!-- Scrollable Controls -->
      <div class="flex-1 overflow-y-auto no-scrollbar px-5 py-5 space-y-4">

        <p class="text-[10px] font-mono text-[#7B8BA3] uppercase tracking-widest px-1">收益与风险目标</p>

        <!-- Target Return Slider -->
        <div class="glass-card p-4">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs text-[#94A3B8]">目标年化收益率</span>
            <span class="text-lg font-bold text-cyan-400 font-mono tabular-nums">
              {{ targetReturn.toFixed(1) }}<span class="text-[13px] text-cyan-400/60 ml-0.5">%</span>
            </span>
          </div>
          <input
            v-model.number="targetReturn"
            type="range" min="3.0" max="8.0" step="0.1"
            class="slider slider-cyan w-full"
            :style="{ '--fill': ((targetReturn - 3) / 5 * 100) + '%' }"
          />
          <div class="flex justify-between mt-1.5">
            <span class="text-[10px] text-[#7B8BA3] font-mono">3.0%</span>
            <span class="text-[10px] text-[#7B8BA3] font-mono">8.0%</span>
          </div>
        </div>

        <!-- Max Volatility Slider -->
        <div class="glass-card p-4">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs text-[#94A3B8]">最大波动率容忍度</span>
            <span class="text-lg font-bold text-amber-400 font-mono tabular-nums">
              {{ maxVolatility.toFixed(1) }}<span class="text-[13px] text-amber-400/60 ml-0.5">%</span>
            </span>
          </div>
          <input
            v-model.number="maxVolatility"
            type="range" min="1.0" max="15.0" step="0.1"
            class="slider slider-amber w-full"
            :style="{ '--fill': ((maxVolatility - 1) / 14 * 100) + '%' }"
          />
          <div class="flex justify-between mt-1.5">
            <span class="text-[10px] text-[#7B8BA3] font-mono">1.0%</span>
            <span class="text-[10px] text-[#7B8BA3] font-mono">15.0%</span>
          </div>
        </div>

        <p class="text-[10px] font-mono text-[#7B8BA3] uppercase tracking-widest px-1 pt-2">大类资产约束</p>

        <!-- Constraints Card -->
        <div class="glass-card p-4 space-y-3.5">
          <!-- Equity Cap -->
          <div class="flex items-center justify-between">
            <span class="text-xs text-[#94A3B8]">权益资产占比上限</span>
            <div class="flex items-center bg-[#111] border border-[#1E1E1E] rounded-lg overflow-hidden focus-within:border-cyan-500/30 transition-colors">
              <input
                v-model.number="equityCap"
                type="number" min="0" max="100" step="5"
                class="w-12 bg-transparent text-right text-[13px] text-white font-mono px-2 py-1.5 outline-none"
              />
              <span class="text-[11px] text-[#94A3B8] font-mono pr-2">%</span>
            </div>
          </div>

          <!-- Credit Floor -->
          <div class="flex items-center justify-between">
            <span class="text-xs text-[#94A3B8]">信用评级底线</span>
            <select
              v-model="creditFloor"
              class="bg-[#111] border border-[#1E1E1E] rounded-lg text-[13px] text-white font-mono px-2.5 py-1.5 outline-none cursor-pointer focus:border-cyan-500/30 transition-colors"
            >
              <option v-for="r in ['AAA','AA+','AA','AA-','A+']" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>

          <!-- Duration Constraint -->
          <div class="flex items-center justify-between">
            <span class="text-xs text-[#94A3B8]">组合久期约束</span>
            <div class="flex items-center bg-[#111] border border-[#1E1E1E] rounded-lg overflow-hidden focus-within:border-cyan-500/30 transition-colors">
              <input
                v-model.number="durationConstraint"
                type="number" min="0.5" max="10" step="0.5"
                class="w-12 bg-transparent text-right text-[13px] text-white font-mono px-2 py-1.5 outline-none"
              />
              <span class="text-[11px] text-[#94A3B8] font-mono pr-2">年</span>
            </div>
          </div>

          <!-- Dividend Factor Toggle -->
          <div class="flex items-center justify-between">
            <span class="text-xs text-[#94A3B8]">必须包含红利因子</span>
            <button
              @click="includeDividend = !includeDividend"
              :class="[
                'relative w-10 h-[22px] rounded-full transition-colors duration-200 focus:outline-none',
                includeDividend ? 'bg-cyan-600' : 'bg-[#222]'
              ]"
            >
              <span
                :class="[
                  'absolute top-[3px] left-[3px] w-4 h-4 rounded-full bg-white shadow-sm transition-transform duration-200',
                  includeDividend ? 'translate-x-[18px]' : 'translate-x-0'
                ]"
              />
            </button>
          </div>
        </div>
      </div>

      <!-- Run Button -->
      <div class="px-5 pb-5 pt-3 border-t border-[#1A1A1A] bg-gradient-to-t from-[#0A0A0A] to-transparent">
        <button
          @click="runSimulation"
          :disabled="isSimulating"
          :class="[
            'w-full py-3.5 rounded-xl text-[15px] font-bold transition-all duration-300 flex items-center justify-center space-x-2',
            isSimulating
              ? 'bg-[#1A1A1A] text-[#94A3B8] cursor-not-allowed'
              : 'bg-gradient-to-r from-red-600 via-orange-500 to-amber-500 hover:from-red-500 hover:via-orange-400 hover:to-amber-400 text-white shadow-[0_0_30px_rgba(239,68,68,0.3)] hover:shadow-[0_0_50px_rgba(239,68,68,0.5)] active:scale-[0.98]'
          ]"
        >
          <span v-if="isSimulating" class="flex items-center space-x-2">
            <span class="w-4 h-4 border-2 border-[#555] border-t-[#888] rounded-full animate-spin" />
            <span>模拟运行中...</span>
          </span>
          <span v-else>{{ hasSimulated ? '🔄 重新模拟 (10,000次)' : '🚀 运行蒙特卡洛模拟 (10,000次)' }}</span>
        </button>
        <button
          v-if="hasSimulated && !isSimulating"
          @click="resetSimulation"
          class="w-full text-center text-[11px] text-[#94A3B8] hover:text-[#888] font-mono mt-2 transition-colors"
        >重置模拟</button>
      </div>
    </div>

    <!-- ═══ RIGHT PANEL: Visualization ═══ -->
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">

      <!-- Toolbar -->
      <div class="bg-[#080808] border-b border-[#1A1A1A] px-6 py-3 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-3 min-w-0">
          <h3 class="text-[15px] font-bold text-[#E5E5E5] shrink-0">蒙特卡洛有效边界</h3>
          <span
            v-if="hasSimulated"
            class="text-[11px] font-mono text-[#94A3B8] bg-[#111] border border-[#1A1A1A] px-2 py-1 rounded-full shrink-0"
          >
            10,000 次模拟 · {{ scatterNear.length + scatterFar.length }} 有效组合
          </span>
          <span
            v-if="isConstrained && hasSimulated"
            class="text-[11px] font-mono text-amber-400 bg-amber-400/10 border border-amber-400/20 px-2 py-1 rounded-full shrink-0"
          >⚠ 波动率约束生效 · 实际收益 {{ anchorPoint[1] }}%</span>
        </div>
        <div v-if="hasSimulated" class="flex items-center space-x-1.5 text-[11px] font-mono text-cyan-400/60 shrink-0">
          <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
          <span>实时联动</span>
        </div>
      </div>

      <!-- Chart Area -->
      <div class="flex-1 relative min-h-0">

        <!-- Loading Overlay -->
        <Transition
          enter-active-class="transition-opacity duration-300"
          enter-from-class="opacity-0"
          leave-active-class="transition-opacity duration-300"
          leave-to-class="opacity-0"
        >
          <div v-if="isSimulating" class="absolute inset-0 bg-[#050505]/90 backdrop-blur-sm flex items-center justify-center z-20">
            <div class="text-center space-y-4">
              <div class="w-16 h-16 mx-auto rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin" />
              <p class="text-[15px] text-[#888]">正在运行蒙特卡洛模拟...</p>
              <div class="w-52 h-1 bg-[#1A1A1A] rounded-full overflow-hidden mx-auto">
                <div class="h-full progress-shimmer rounded-full transition-all duration-150 ease-out" :style="{ width: simulationProgress + '%' }" />
              </div>
              <p class="text-[13px] font-mono text-cyan-400">
                {{ Math.floor(simulationProgress * 100).toLocaleString() }} / 10,000 次
              </p>
            </div>
          </div>
        </Transition>

        <!-- Placeholder -->
        <div v-if="!hasSimulated && !isSimulating" class="flex items-center justify-center h-full select-none">
          <div class="text-center space-y-5">
            <div class="w-20 h-20 mx-auto rounded-2xl bg-[#111] border border-[#1A1A1A] flex items-center justify-center shadow-[0_0_30px_rgba(0,0,0,0.3)]">
              <DataAnalysis class="w-9 h-9 text-[#1E1E1E]" />
            </div>
            <div>
              <p class="text-[15px] text-[#94A3B8]">调整左侧参数后</p>
              <p class="text-[15px] text-[#666] mt-1">点击 <span class="text-cyan-400 font-bold">运行模拟</span> 生成有效边界</p>
            </div>
            <div class="flex items-center justify-center space-x-6 text-[11px] font-mono text-[#7B8BA3]">
              <span>📊 10,000 次随机组合</span>
              <span>📈 有效边界提取</span>
              <span>🎯 最优锚点定位</span>
            </div>
          </div>
        </div>

        <!-- Frontier Chart -->
        <VChart v-if="hasSimulated" :option="frontierOption" autoresize class="w-full h-full" />
      </div>

      <!-- Bottom: Allocation + Metrics -->
      <template v-if="hasSimulated">
        <div class="h-[280px] shrink-0 border-t border-[#1A1A1A] flex gap-3 p-3">

          <!-- Donut Chart -->
          <div class="w-[280px] shrink-0 bg-[#0A0A0A] border border-[#1A1A1A] rounded-xl p-3 flex flex-col">
            <p class="text-[11px] font-mono text-[#94A3B8] uppercase tracking-wider shrink-0">SAA 配置建议</p>
            <VChart :option="pieOption" autoresize class="flex-1 min-h-0" />
          </div>

          <!-- Key Metrics -->
          <div class="flex-1 min-w-0 bg-[#0A0A0A] border border-[#1A1A1A] rounded-xl p-3 flex flex-col">
            <p class="text-[11px] font-mono text-[#94A3B8] uppercase tracking-wider mb-2 shrink-0">关键绩效指标</p>
            <div class="grid grid-cols-3 grid-rows-2 gap-2 flex-1 min-h-0">
              <div
                v-for="m in metricCards" :key="m.label"
                class="bg-[#0E0E0E] border border-[#151515] rounded-lg px-3 py-2 flex flex-col justify-center"
              >
                <span class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider leading-tight">{{ m.label }}</span>
                <span :class="['text-xl font-bold font-mono tabular-nums mt-0.5 leading-tight', m.color]">{{ m.value }}</span>
                <span class="text-[10px] text-[#7B8BA3] font-mono mt-0.5 leading-tight">{{ m.sub }}</span>
              </div>
            </div>
          </div>

          <!-- Radar Chart -->
          <div class="w-[250px] shrink-0 bg-[#0A0A0A] border border-[#1A1A1A] rounded-xl p-3 flex flex-col">
            <p class="text-[11px] font-mono text-[#94A3B8] uppercase tracking-wider shrink-0">组合画像</p>
            <VChart :option="radarOption" autoresize class="flex-1 min-h-0" />
          </div>
        </div>
      </template>

      <!-- Bottom Placeholder -->
      <div
        v-if="!hasSimulated && !isSimulating"
        class="h-[280px] shrink-0 border-t border-[#1A1A1A] flex items-center justify-center"
      >
        <span class="text-xs font-mono text-[#1E1E1E] select-none">运行模拟后此处将展示配置建议与绩效指标</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, shallowRef } from 'vue';
import { ArrowLeft, DataAnalysis } from '@element-plus/icons-vue';
import { sharedIntentState } from '../store/intentStore';

const props = defineProps<{ embedded?: boolean }>();
const emit = defineEmits<{ close: [] }>();

function handleBack() {
  if (props.embedded) emit('close');
  else sharedIntentState.navigationTarget = 'portal';
}

import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import {
  ScatterChart, LineChart, PieChart, EffectScatterChart, RadarChart,
} from 'echarts/charts';
import {
  GridComponent, TooltipComponent, LegendComponent,
  MarkLineComponent, RadarComponent,
} from 'echarts/components';

use([
  CanvasRenderer,
  ScatterChart, LineChart, PieChart, EffectScatterChart, RadarChart,
  GridComponent, TooltipComponent, LegendComponent,
  MarkLineComponent, RadarComponent,
]);

// ── Frontier Model Constants ────────────────────────────────────────────────────
const SIGMA_MIN = 2.5;
const SIGMA_MAX = 18;
const R_MIN = 2.2;
const R_MAX = 10.5;
const RISK_FREE = 1.5;

// ── Reactive State ──────────────────────────────────────────────────────────────
const targetReturn = ref(5.5);
const maxVolatility = ref(10.0);
const equityCap = ref(20);
const creditFloor = ref('AA+');
const durationConstraint = ref(3.5);
const includeDividend = ref(true);

const isSimulating = ref(false);
const hasSimulated = ref(false);
const simulationProgress = ref(0);

const scatterNear = shallowRef<number[][]>([]);
const scatterFar = shallowRef<number[][]>([]);
const frontierCurveData = shallowRef<number[][]>([]);

// ── Model: Efficient Frontier ───────────────────────────────────────────────────

function frontierReturn(sigma: number): number {
  if (sigma <= SIGMA_MIN) return R_MIN;
  if (sigma >= SIGMA_MAX) return R_MAX;
  const t = (sigma - SIGMA_MIN) / (SIGMA_MAX - SIGMA_MIN);
  return R_MIN + (R_MAX - R_MIN) * Math.sqrt(t);
}

function generateScatter() {
  const near: number[][] = [];
  const far: number[][] = [];

  for (let i = 0; i < 10000; i++) {
    const u = Math.random();
    const vol = SIGMA_MIN * 0.7 + u * (SIGMA_MAX + 3.5);
    const fr = frontierReturn(Math.min(vol, SIGMA_MAX));
    const depth = 0.15 + Math.random() * Math.random() * 7.5;
    const ret = fr - depth;

    if (ret > 0.3 && vol > 1.5 && vol < 22) {
      const pt: [number, number] = [+vol.toFixed(2), +ret.toFixed(2)];
      if (depth < 1.6) near.push(pt);
      else far.push(pt);
    }
  }

  scatterNear.value = near;
  scatterFar.value = far;
}

function generateFrontierCurve() {
  const pts: number[][] = [];
  for (let s = SIGMA_MIN; s <= SIGMA_MAX; s += 0.12) {
    pts.push([+s.toFixed(2), +frontierReturn(s).toFixed(2)]);
  }
  frontierCurveData.value = pts;
}

// ── Simulation Runner ───────────────────────────────────────────────────────────

function runSimulation() {
  if (isSimulating.value) return;
  isSimulating.value = true;
  simulationProgress.value = 0;
  hasSimulated.value = false;

  const tick = setInterval(() => {
    simulationProgress.value = Math.min(100, simulationProgress.value + Math.random() * 14 + 3);
    if (simulationProgress.value >= 100) {
      clearInterval(tick);
      generateScatter();
      generateFrontierCurve();
      setTimeout(() => {
        isSimulating.value = false;
        hasSimulated.value = true;
      }, 350);
    }
  }, 100);
}

function resetSimulation() {
  hasSimulated.value = false;
  scatterNear.value = [];
  scatterFar.value = [];
  frontierCurveData.value = [];
}

// ── Computed: Anchor Point ──────────────────────────────────────────────────────

const anchorPoint = computed<[number, number]>(() => {
  const clampedR = Math.max(R_MIN, Math.min(R_MAX, targetReturn.value));
  const t = Math.pow((clampedR - R_MIN) / (R_MAX - R_MIN), 2);
  let sigma = SIGMA_MIN + t * (SIGMA_MAX - SIGMA_MIN);
  if (sigma > maxVolatility.value) sigma = maxVolatility.value;
  const r = frontierReturn(sigma);
  return [+sigma.toFixed(2), +r.toFixed(2)];
});

const isConstrained = computed(() => {
  const clampedR = Math.max(R_MIN, Math.min(R_MAX, targetReturn.value));
  const t = Math.pow((clampedR - R_MIN) / (R_MAX - R_MIN), 2);
  return SIGMA_MIN + t * (SIGMA_MAX - SIGMA_MIN) > maxVolatility.value + 0.3;
});

// ── Computed: Asset Allocation ──────────────────────────────────────────────────

interface AssetSlice { name: string; value: number; color: string }

const allocation = computed<AssetSlice[]>(() => {
  const sigma = anchorPoint.value[0];
  const t = Math.max(0, Math.min(1, (sigma - SIGMA_MIN) / (SIGMA_MAX - SIGMA_MIN)));

  let equity = Math.round(5 + t * 45);
  let dividend = includeDividend.value ? Math.round(3 + t * 7) : 0;

  const totalEq = equity + dividend;
  if (totalEq > equityCap.value) {
    const ratio = Math.max(0, equityCap.value) / Math.max(1, totalEq);
    equity = Math.round(equity * ratio);
    dividend = Math.round(dividend * ratio);
  }

  const fixedIncome = Math.round(72 - t * 38);
  const alternative = Math.round(t * 10);
  const overseas = Math.round(t * 6);
  const cash = Math.max(0, 100 - equity - fixedIncome - alternative - overseas - dividend);

  return [
    { name: '固收资产', value: fixedIncome, color: '#06b6d4' },
    { name: '权益资产', value: equity, color: '#818cf8' },
    ...(dividend > 0 ? [{ name: '红利增强', value: dividend, color: '#f43f5e' }] : []),
    ...(alternative > 0 ? [{ name: '另类投资', value: alternative, color: '#f59e0b' }] : []),
    ...(overseas > 0 ? [{ name: '海外配置', value: overseas, color: '#10b981' }] : []),
    ...(cash > 0 ? [{ name: '现金管理', value: cash, color: '#64748b' }] : []),
  ];
});

// ── Computed: Performance Metrics ───────────────────────────────────────────────

const metrics = computed(() => {
  const [sigma, r] = anchorPoint.value;
  const sharpe = sigma > 0 ? (r - RISK_FREE) / sigma : 0;
  const maxDD = sigma * 1.45;
  const calmar = maxDD > 0 ? r / maxDD : 0;
  const sortino = sharpe * 1.35;
  return { annualReturn: r, annualVol: sigma, sharpe, calmar, maxDD, sortino };
});

const metricCards = computed(() => {
  const m = metrics.value;
  return [
    { label: '年化收益', value: m.annualReturn.toFixed(1) + '%', color: 'text-cyan-400', sub: 'Annual Return' },
    { label: '年化波动', value: m.annualVol.toFixed(1) + '%', color: 'text-amber-400', sub: 'Volatility' },
    { label: '夏普比率', value: m.sharpe.toFixed(2), color: m.sharpe >= 0.5 ? 'text-green-400' : 'text-red-400', sub: 'Sharpe Ratio' },
    { label: '卡玛比率', value: m.calmar.toFixed(2), color: m.calmar >= 0.5 ? 'text-green-400' : 'text-amber-400', sub: 'Calmar Ratio' },
    { label: '最大回撤', value: m.maxDD.toFixed(1) + '%', color: 'text-red-400', sub: 'Max Drawdown' },
    { label: 'Sortino', value: m.sortino.toFixed(2), color: m.sortino >= 0.7 ? 'text-green-400' : 'text-amber-400', sub: 'Sortino Ratio' },
  ];
});

// ── ECharts Option: Efficient Frontier ──────────────────────────────────────────

const frontierOption = computed(() => {
  const [ax, ay] = anchorPoint.value;

  return {
    backgroundColor: 'transparent',
    animation: true,
    animationDuration: 1200,
    animationEasing: 'cubicOut' as const,
    grid: { left: 65, right: 40, top: 50, bottom: 55 },
    tooltip: {
      trigger: 'item' as const,
      backgroundColor: 'rgba(10,10,10,0.92)',
      borderColor: '#222',
      textStyle: { color: '#ccc', fontSize: 11, fontFamily: 'monospace' },
    },
    xAxis: {
      name: '年化波动率 (%)',
      nameLocation: 'center' as const,
      nameGap: 35,
      nameTextStyle: { color: '#555', fontSize: 11, fontFamily: 'monospace' },
      type: 'value' as const,
      min: 0,
      max: 22,
      splitLine: { lineStyle: { color: '#111', type: 'dashed' as const } },
      axisLine: { lineStyle: { color: '#1A1A1A' } },
      axisTick: { lineStyle: { color: '#1A1A1A' } },
      axisLabel: { color: '#444', fontSize: 10, fontFamily: 'monospace' },
    },
    yAxis: {
      name: '年化收益率 (%)',
      nameLocation: 'center' as const,
      nameGap: 48,
      nameTextStyle: { color: '#555', fontSize: 11, fontFamily: 'monospace' },
      type: 'value' as const,
      min: 0,
      max: 13,
      splitLine: { lineStyle: { color: '#111', type: 'dashed' as const } },
      axisLine: { lineStyle: { color: '#1A1A1A' } },
      axisTick: { lineStyle: { color: '#1A1A1A' } },
      axisLabel: { color: '#444', fontSize: 10, fontFamily: 'monospace' },
    },
    series: [
      {
        type: 'scatter' as const,
        name: '次优组合',
        large: true,
        largeThreshold: 2000,
        data: scatterFar.value,
        symbolSize: 2,
        itemStyle: { color: 'rgba(80, 90, 130, 0.08)' },
        silent: true,
      },
      {
        type: 'scatter' as const,
        name: '近优组合',
        large: true,
        largeThreshold: 2000,
        data: scatterNear.value,
        symbolSize: 3,
        itemStyle: { color: 'rgba(120, 140, 210, 0.22)' },
        silent: true,
      },
      {
        type: 'line' as const,
        name: '有效边界',
        data: frontierCurveData.value,
        smooth: 0.35,
        showSymbol: false,
        lineStyle: {
          width: 3,
          color: {
            type: 'linear' as const,
            x: 0, y: 0, x2: 1, y2: 0,
            colorStops: [
              { offset: 0, color: '#06b6d4' },
              { offset: 0.5, color: '#818cf8' },
              { offset: 1, color: '#e879f9' },
            ],
          },
          shadowColor: 'rgba(99, 102, 241, 0.5)',
          shadowBlur: 16,
        },
        z: 10,
        markLine: {
          silent: true,
          symbol: 'none' as const,
          lineStyle: { color: '#282828', type: 'dashed' as const, width: 1 },
          label: {
            color: '#555',
            fontSize: 9,
            fontFamily: 'monospace',
          },
          data: [
            { yAxis: targetReturn.value, label: { formatter: `目标 ${targetReturn.value.toFixed(1)}%`, position: 'insideEndTop' as const } },
            { xAxis: maxVolatility.value, label: { formatter: `上限 ${maxVolatility.value.toFixed(1)}%`, position: 'insideEndTop' as const } },
          ],
        },
      },
      {
        type: 'effectScatter' as const,
        name: '最优推荐',
        data: [[ax, ay]],
        symbolSize: 20,
        animationDurationUpdate: 500,
        animationEasingUpdate: 'cubicOut' as const,
        rippleEffect: {
          brushType: 'stroke' as const,
          scale: 4,
          period: 3,
        },
        itemStyle: {
          color: '#ef4444',
          shadowColor: 'rgba(239, 68, 68, 0.6)',
          shadowBlur: 24,
        },
        label: {
          show: true,
          formatter: `最优推荐组合\n收益 ${ay}% · 波动 ${ax}%`,
          position: 'top' as const,
          distance: 18,
          color: '#fff',
          fontSize: 10,
          fontFamily: 'monospace',
          backgroundColor: 'rgba(239, 68, 68, 0.88)',
          borderRadius: 6,
          padding: [6, 10] as [number, number],
          lineHeight: 16,
        },
        tooltip: {
          formatter: () =>
            `<div style="font-family:monospace;line-height:1.6">`
            + `<b style="color:#ef4444">● 最优推荐组合</b><br/>`
            + `年化收益: <b>${ay}%</b><br/>`
            + `年化波动: <b>${ax}%</b><br/>`
            + `夏普比率: <b>${metrics.value.sharpe.toFixed(2)}</b>`
            + `</div>`,
        },
        z: 20,
      },
    ],
  };
});

// ── ECharts Option: Donut Pie ───────────────────────────────────────────────────

const pieOption = computed(() => ({
  tooltip: {
    trigger: 'item' as const,
    backgroundColor: 'rgba(10,10,10,0.92)',
    borderColor: '#222',
    textStyle: { color: '#ccc', fontSize: 11, fontFamily: 'monospace' },
    formatter: (p: any) => `${p.marker} ${p.name}: <b>${p.value}%</b>`,
  },
  series: [
    {
      type: 'pie' as const,
      radius: ['40%', '68%'],
      center: ['50%', '54%'],
      avoidLabelOverlap: true,
      itemStyle: { borderColor: '#0A0A0A', borderWidth: 2, borderRadius: 4 },
      label: {
        color: '#888',
        fontSize: 10,
        fontFamily: 'monospace',
        formatter: '{b}\n{c}%',
        lineHeight: 14,
      },
      labelLine: { lineStyle: { color: '#333' }, length: 6, length2: 10 },
      emphasis: {
        itemStyle: { shadowBlur: 20, shadowColor: 'rgba(0,0,0,0.5)' },
        label: { fontSize: 12, fontWeight: 'bold' as const, color: '#fff' },
      },
      data: allocation.value.map(a => ({
        name: a.name,
        value: a.value,
        itemStyle: { color: a.color },
      })),
      animationType: 'scale' as const,
      animationEasing: 'elasticOut' as const,
      animationDelay: (_idx: number) => _idx * 80,
    },
  ],
}));

// ── ECharts Option: Radar ───────────────────────────────────────────────────────

const radarOption = computed(() => {
  const m = metrics.value;
  const returnScore = Math.min(100, (m.annualReturn / 10) * 100);
  const riskScore = Math.min(100, Math.max(0, (1 - m.annualVol / 18) * 100));
  const sharpeScore = Math.min(100, Math.max(0, (m.sharpe / 1.2) * 100));
  const liquidityScore = Math.min(100, 45 + (1 - m.annualVol / 18) * 55);
  const diverseScore = Math.min(100, allocation.value.length * 18);

  return {
    radar: {
      indicator: [
        { name: '收益性', max: 100 },
        { name: '风险控制', max: 100 },
        { name: '夏普效率', max: 100 },
        { name: '流动性', max: 100 },
        { name: '分散度', max: 100 },
      ],
      radius: '58%',
      center: ['50%', '55%'],
      axisName: { color: '#555', fontSize: 9, fontFamily: 'monospace' },
      splitArea: {
        areaStyle: {
          color: ['rgba(6,182,212,0.01)', 'rgba(6,182,212,0.03)', 'rgba(6,182,212,0.01)', 'rgba(6,182,212,0.03)'],
        },
      },
      splitLine: { lineStyle: { color: '#1A1A1A' } },
      axisLine: { lineStyle: { color: '#1A1A1A' } },
    },
    series: [
      {
        type: 'radar' as const,
        data: [
          {
            value: [returnScore, riskScore, sharpeScore, liquidityScore, diverseScore],
            areaStyle: { color: 'rgba(6, 182, 212, 0.12)' },
            lineStyle: { color: '#06b6d4', width: 2, shadowColor: 'rgba(6,182,212,0.4)', shadowBlur: 8 },
            itemStyle: { color: '#06b6d4' },
            symbol: 'circle' as const,
            symbolSize: 5,
          },
        ],
        animationDuration: 800,
      },
    ],
  };
});
</script>

<style scoped>
/* ── Glassmorphism Card ─────────────────────────────────────────────────────── */
.glass-card {
  background: linear-gradient(135deg, rgba(14,14,14,0.92), rgba(8,8,8,0.92));
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.035);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}

/* ── Range Slider ───────────────────────────────────────────────────────────── */
.slider {
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.slider-cyan {
  background: linear-gradient(to right, #06b6d4 0%, #06b6d4 var(--fill), #1a1a1a var(--fill), #1a1a1a 100%);
}
.slider-amber {
  background: linear-gradient(to right, #f59e0b 0%, #f59e0b var(--fill), #1a1a1a var(--fill), #1a1a1a 100%);
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 3px solid #0a0a0a;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
}
.slider-cyan::-webkit-slider-thumb {
  background: #06b6d4;
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.4);
}
.slider-amber::-webkit-slider-thumb {
  background: #f59e0b;
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
}
.slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}
.slider-cyan::-webkit-slider-thumb:hover {
  box-shadow: 0 0 22px rgba(6, 182, 212, 0.6);
}
.slider-amber::-webkit-slider-thumb:hover {
  box-shadow: 0 0 22px rgba(245, 158, 11, 0.6);
}

/* Firefox */
.slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 3px solid #0a0a0a;
  cursor: pointer;
}
.slider-cyan::-moz-range-thumb { background: #06b6d4; }
.slider-amber::-moz-range-thumb { background: #f59e0b; }
.slider::-moz-range-track { height: 4px; border-radius: 2px; background: #1a1a1a; border: none; }
.slider-cyan::-moz-range-progress { background: #06b6d4; border-radius: 2px; height: 4px; }
.slider-amber::-moz-range-progress { background: #f59e0b; border-radius: 2px; height: 4px; }

/* ── Progress Shimmer ───────────────────────────────────────────────────────── */
.progress-shimmer {
  background: linear-gradient(90deg, #06b6d4, #818cf8, #e879f9, #06b6d4);
  background-size: 300% 100%;
  animation: shimmer 2s ease-in-out infinite;
}

@keyframes shimmer {
  0%   { background-position: 0% 0; }
  100% { background-position: 300% 0; }
}
</style>
