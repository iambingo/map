<template>
  <div class="flex flex-col bg-[#161922] text-[#E8ECF4] h-full">
    <!-- Header -->
    <div class="bg-[#202431] border border-[#2E3348] rounded-xl px-4 py-2 shrink-0 flex justify-between items-center shadow-lg">
      <div>
        <h1 class="am-title-l1 tracking-wider"><div class="am-title-bar"></div>市场追踪 (Market Tracking)</h1>
        <p class="text-[13px] text-[#94A3B8] mt-0.5 font-mono">追踪各策略对标基准的收益率情况 · 点击走势图查看明细</p>
      </div>
      <div class="flex items-center space-x-2">
        <div class="flex items-center space-x-1.5 bg-[#1A1E2B] border border-[#2E3348] px-2.5 py-1.5 rounded">
          <Calendar class="w-3.5 h-3.5 text-[#94A3B8]" />
          <span class="text-xs text-[#6B7280] font-mono">基准日期</span>
          <input
            type="date"
            v-model="asOfDate"
            class="bg-transparent border-none text-[13px] font-mono text-[#B4BAC9] outline-none w-[110px]"
          />
        </div>
        <button
          class="flex items-center space-x-2 bg-[#1A1E2B] border border-[#2E3348] px-3 py-1.5 rounded text-[13px] font-mono text-[#94A3B8] hover:text-[#B4BAC9] hover:border-[#3E4660] transition-colors"
          title="将收益率数据导出为 2D 扁平横表 (Excel)"
        >
          <DataLine class="w-3.5 h-3.5" />
          <span>导出明细 (Excel)</span>
        </button>
        <button class="flex items-center space-x-2 bg-[#2A2D3A] border border-[#2E3348] px-3 py-1.5 rounded text-[13px] font-medium text-[#E8ECF4] hover:bg-[#2E3348] transition-colors shadow-sm">
          <Setting class="w-3.5 h-3.5" />
          <span>基准配置</span>
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-[#202431] border border-[#2E3348] rounded-xl shadow-lg overflow-hidden flex-1 flex flex-col min-h-0 mt-2">
      <div class="overflow-auto flex-1">
        <table class="min-w-full divide-y divide-[#252A3A] table-fixed">
          <thead class="bg-[#2A2D3A] sticky top-0 z-10">
            <tr>
              <th class="px-2 py-2 text-center text-[13px] font-bold text-[#94A3B8] uppercase tracking-wider w-12">大类</th>
              <th class="px-3 py-2 text-left text-[13px] font-bold text-[#94A3B8] uppercase tracking-wider w-28">策略</th>
              <th class="px-3 py-2 text-left text-[13px] font-bold text-[#94A3B8] uppercase tracking-wider">对标基准</th>
              <th class="px-3 py-2 text-right text-[13px] font-bold text-[#94A3B8] uppercase tracking-wider w-24" title="计算区间: 2026-04-14 至 2026-04-15">近1天</th>
              <th class="px-3 py-2 text-right text-[13px] font-bold text-[#94A3B8] uppercase tracking-wider w-24" title="计算区间: 2026-04-08 至 2026-04-15">近7天</th>
              <th class="px-3 py-2 text-right text-[13px] font-bold text-[#94A3B8] uppercase tracking-wider w-24" title="计算区间: 2026-03-15 至 2026-04-15">近1月</th>
              <th class="px-3 py-2 text-right text-[13px] font-bold text-[#94A3B8] uppercase tracking-wider w-24" title="计算区间: 2025-12-31 至 2026-04-15">YTD</th>
              <th class="px-3 py-2 text-center text-[13px] font-bold text-[#94A3B8] uppercase tracking-wider w-28">走势</th>
            </tr>
          </thead>
          <tbody class="bg-[#202431] divide-y divide-[#252A3A]">
            <template v-for="(category, ci) in MARKET_DATA" :key="category.category">
              <tr
                v-for="(strategy, si) in category.strategies"
                :key="strategy.id"
                class="hover:bg-[#2A2D3A]/60 transition-colors group"
              >
                <td
                  v-if="si === 0"
                  :rowspan="category.strategies.length"
                  class="px-2 text-[13px] font-bold border-r border-[#2E3348] bg-[#1A1E2B] align-middle text-center w-12"
                  :style="{ writingMode: 'vertical-rl', textOrientation: 'mixed', letterSpacing: '0.15em' }"
                  :class="CATEGORY_STYLES[ci]"
                >{{ category.category }}</td>
                <td class="px-3 py-1.5 whitespace-nowrap text-[13px] font-medium text-[#E8ECF4]">
                  {{ strategy.name }}
                </td>
                <td class="px-3 py-1.5 whitespace-nowrap">
                  <div class="relative">
                    <select
                      v-model="selectedBenchmarks[strategy.id]"
                      class="block w-full pl-2 pr-6 py-1 text-[13px] font-mono border border-[#3E4660] focus:outline-none focus:border-[#00C9A7] rounded bg-[#161922] text-[#B4BAC9] group-hover:text-[#E8ECF4] transition-colors appearance-none"
                    >
                      <option v-for="bm in strategy.benchmarks" :key="bm" :value="bm">{{ bm }}</option>
                    </select>
                    <ArrowDown class="w-3 h-3 absolute right-2 top-1/2 -translate-y-1/2 text-[#94A3B8] pointer-events-none" />
                  </div>
                </td>
                <td class="px-3 py-1.5 whitespace-nowrap text-right font-mono tabular-nums">
                  <ReturnCell :value="getReturns(selectedBenchmarks[strategy.id]).d1" />
                </td>
                <td class="px-3 py-1.5 whitespace-nowrap text-right font-mono tabular-nums">
                  <ReturnCell :value="getReturns(selectedBenchmarks[strategy.id]).d7" />
                </td>
                <td class="px-3 py-1.5 whitespace-nowrap text-right font-mono tabular-nums">
                  <ReturnCell :value="getReturns(selectedBenchmarks[strategy.id]).m1" />
                </td>
                <td class="px-3 py-1.5 whitespace-nowrap text-right font-mono tabular-nums">
                  <ReturnCell :value="getReturns(selectedBenchmarks[strategy.id]).ytd" />
                </td>
                <td class="px-3 py-1.5 whitespace-nowrap">
                  <button
                    class="h-5 w-18 ml-auto cursor-pointer hover:ring-1 hover:ring-[#3B9EFF]/50 rounded transition-all block"
                    @click="openDetail(strategy.name, selectedBenchmarks[strategy.id])"
                  >
                    <Sparkline
                      :data="getReturns(selectedBenchmarks[strategy.id]).trend"
                      :positive="getReturns(selectedBenchmarks[strategy.id]).ytd >= 0"
                    />
                  </button>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Detail Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showDetail"
          class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm"
          @click.self="showDetail = false"
        >
          <div class="bg-[#202431] border border-[#2E3348] rounded-xl shadow-2xl w-[720px] max-w-[90vw] overflow-hidden">
            <div class="flex items-center justify-between px-5 py-3 border-b border-[#2E3348] bg-gradient-to-r from-[#252A3A] to-[#202431]">
              <h3 class="am-title-l2"><div class="am-title-bar"></div>
                {{ detailStrategyName }}
                <span class="text-[#94A3B8] font-normal mx-2">/</span>
                <span class="text-[#B4BAC9] font-mono text-[13px]">{{ detailBenchmarkName }}</span>
              </h3>
              <button @click="showDetail = false" class="text-[#94A3B8] hover:text-white p-1 rounded hover:bg-[#2E3348] transition-colors">
                <Close class="w-4 h-4" />
              </button>
            </div>
            <div class="p-5">
              <div class="grid grid-cols-4 gap-3 mb-5">
                <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-3 text-center">
                  <div class="text-[13px] text-[#94A3B8] uppercase tracking-wider mb-1">近1天</div>
                  <ReturnCell :value="detailReturns.d1" size="lg" />
                </div>
                <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-3 text-center">
                  <div class="text-[13px] text-[#94A3B8] uppercase tracking-wider mb-1">近7天</div>
                  <ReturnCell :value="detailReturns.d7" size="lg" />
                </div>
                <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-3 text-center">
                  <div class="text-[13px] text-[#94A3B8] uppercase tracking-wider mb-1">近1月</div>
                  <ReturnCell :value="detailReturns.m1" size="lg" />
                </div>
                <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-3 text-center">
                  <div class="text-[13px] text-[#94A3B8] uppercase tracking-wider mb-1">YTD(年化)</div>
                  <ReturnCell :value="detailReturns.ytd" size="lg" />
                </div>
              </div>
              <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-4">
                <div class="flex items-center justify-between mb-3">
                  <span class="text-[13px] text-[#B4BAC9] font-mono">收益率走势</span>
                  <div class="flex items-center space-x-1">
                    <button
                      v-for="tf in ['7D', '1M', '3M']"
                      :key="tf"
                      @click="detailTimeframe = tf"
                      :class="cn(
                        'px-2.5 py-1 text-[13px] rounded transition-all',
                        detailTimeframe === tf
                          ? 'bg-[#3B9EFF] text-white'
                          : 'text-[#94A3B8] hover:text-[#B4BAC9] hover:bg-[#2E3348]'
                      )"
                    >{{ tf }}</button>
                  </div>
                </div>
                <div class="h-[240px]">
                  <VChart :option="detailChartOption" autoresize class="w-full h-full" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, defineComponent, h, computed } from 'vue';
import { Setting, ArrowDown, Close, DataLine, Calendar } from '@element-plus/icons-vue';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent]);

function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

const CATEGORY_STYLES = ['text-[#3B9EFF]', 'text-[#F04864]', 'text-[#FFAB00]'];

const asOfDate = ref('2026-04-15');

const showDetail = ref(false);
const detailStrategyName = ref('');
const detailBenchmarkName = ref('');
const detailReturns = ref({ d1: 0, d7: 0, m1: 0, ytd: 0, trend: [100] as number[] });
const detailTimeframe = ref<'7D' | '1M' | '3M'>('7D');

function openDetail(strategyName: string, benchmark: string) {
  const ret = getReturns(benchmark);
  detailStrategyName.value = strategyName;
  detailBenchmarkName.value = benchmark;
  detailReturns.value = ret;
  detailTimeframe.value = '7D';
  showDetail.value = true;
}

function generateDetailTrend(baseTrend: number[], days: number, seed: number): number[] {
  const result: number[] = [];
  let val = 100;
  for (let i = 0; i < days; i++) {
    const noise = (Math.sin(i * 0.3 + seed) * 0.15) + (Math.cos(i * 0.7 + seed * 2) * 0.1);
    const trendSlope = (baseTrend[baseTrend.length - 1] - baseTrend[0]) / baseTrend.length;
    val += trendSlope + noise;
    result.push(parseFloat(val.toFixed(4)));
  }
  return result;
}

function getDaysForTimeframe(tf: string): number {
  return tf === '7D' ? 7 : tf === '1M' ? 22 : 66;
}

function getDatesForTimeframe(tf: string): string[] {
  const days = getDaysForTimeframe(tf);
  const dates: string[] = [];
  const now = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    dates.push(`${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')}`);
  }
  return dates;
}

const detailChartOption = computed(() => {
  const trend = detailReturns.value.trend;
  const seed = detailBenchmarkName.value.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
  const days = getDaysForTimeframe(detailTimeframe.value);
  const data = generateDetailTrend(trend, days, seed);
  const dates = getDatesForTimeframe(detailTimeframe.value);
  const isPositive = detailReturns.value.ytd >= 0;
  const lineColor = isPositive ? '#F04864' : '#00C9A7';
  const areaColor = isPositive ? 'rgba(240,72,100,0.08)' : 'rgba(0,201,167,0.08)';

  return {
    backgroundColor: 'transparent',
    grid: { top: 10, right: 10, bottom: 25, left: 50 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1A1E2B',
      borderColor: '#3E4660',
      textStyle: { color: '#E8ECF4', fontSize: 11, fontFamily: 'monospace' },
      formatter: (params: any[]) => {
        const p = params[0];
        const val = p.value;
        const pct = ((val - 100) / 100).toFixed(4);
        const sign = val >= 100 ? '+' : '';
        return `<span style="color:#8B93A8">${p.axisValue}</span><br/><span style="color:${lineColor};font-weight:bold">${sign}${pct}%</span> <span style="color:#555E75">(${val.toFixed(2)})</span>`;
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#2E3348' } },
      axisTick: { show: false },
      axisLabel: { color: '#555E75', fontSize: 11, fontFamily: 'monospace', interval: Math.max(Math.floor(days / 6) - 1, 0) },
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#252A3A' } },
      axisLabel: {
        color: '#555E75',
        fontSize: 11,
        fontFamily: 'monospace',
        formatter: (v: number) => ((v - 100) / 100 >= 0 ? '+' : '') + ((v - 100) / 100).toFixed(2) + '%',
      },
    },
    series: [{
      type: 'line',
      data,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: lineColor, width: 1.5 },
      areaStyle: { color: areaColor },
    }],
  };
});

// ── Sparkline (inline SVG) ──────────────────────────────────────────────────
const Sparkline = defineComponent({
  props: { data: { type: Array as () => number[], required: true }, positive: Boolean },
  setup(props) {
    return () => {
      const d = props.data as number[];
      if (!d || d.length < 2) return h('div');
      const min = Math.min(...d), max = Math.max(...d);
      const range = max - min || 1;
      const W = 64, H = 16;
      const pts = d.map((v, i) => {
        const x = (i / (d.length - 1)) * W;
        const y = H - ((v - min) / range) * (H - 4) - 2;
        return `${x},${y}`;
      }).join(' ');
      const stroke = props.positive ? '#F04864' : '#00C9A7';
      return h('svg', { viewBox: `0 0 ${W} ${H}`, class: 'w-full h-full' }, [
        h('polyline', { points: pts, fill: 'none', stroke, 'stroke-width': '1.5', 'stroke-linejoin': 'round', 'stroke-linecap': 'round' })
      ]);
    };
  }
});

// ── ReturnCell ──────────────────────────────────────────────────────────────
const ReturnCell = defineComponent({
  props: {
    value: { type: Number, required: true },
    size: { type: String, default: 'sm' },
  },
  setup(props) {
    return () => {
      const v = props.value;
      const colorClass = v > 0 ? 'text-[#F04864]' : v < 0 ? 'text-[#00C9A7]' : 'text-[#B4BAC9]';
      const sign = v > 0 ? '+' : '';
      const sizeClass = props.size === 'lg' ? 'text-base' : 'text-[13px]';
      return h('span', { class: `font-mono font-bold ${colorClass} ${sizeClass}` }, `${sign}${v.toFixed(2)}%`);
    };
  }
});

// ── Market Data ─────────────────────────────────────────────────────────────
const MARKET_DATA = [
  {
    category: '固收',
    strategies: [
      { id: 'domestic-fi', name: '境内固收', benchmarks: ['高等级1Y以下', '高等级1-3Y', '高等级3-5Y'], defaultBenchmark: '高等级1-3Y' },
      { id: 'overseas-fi', name: '境外固收', benchmarks: ['美元债LOF', '全球高收益债指数', '新兴市场主权债指数'], defaultBenchmark: '美元债LOF' }
    ]
  },
  {
    category: '权益',
    strategies: [
      { id: 'dividend', name: '红利', benchmarks: ['中证红利', '上证红利', '深证红利'], defaultBenchmark: '中证红利' },
      { id: 'equity-mixed', name: '偏股混', benchmarks: ['偏股混指数', '沪深300', '中证500'], defaultBenchmark: '偏股混指数' },
      { id: 'equity-long', name: '权益多头', benchmarks: ['沪深300', '中证500', '中证1000'], defaultBenchmark: '沪深300' },
      { id: 'hk-equity', name: '港股', benchmarks: ['恒生科技指数ETF', '恒生指数', '国企指数'], defaultBenchmark: '恒生科技指数ETF' },
      { id: 'secondary-bond', name: '二级债基', benchmarks: ['二级债基指数', '混合债券型二级基金指数'], defaultBenchmark: '二级债基指数' },
      { id: 'flexible-allocation', name: '灵活配置', benchmarks: ['0.5*沪深300+0.5*高等级', '0.3*沪深300+0.7*高等级'], defaultBenchmark: '0.5*沪深300+0.5*高等级' },
      { id: 'convertible-bond', name: '转债', benchmarks: ['中证转债', '上证转债'], defaultBenchmark: '中证转债' },
      { id: 'overseas-equity', name: '海外权益', benchmarks: ['标普500ETF', '纳斯达克100ETF', '日经225ETF'], defaultBenchmark: '标普500ETF' }
    ]
  },
  {
    category: '另类',
    strategies: [
      { id: 'reits', name: 'REITS', benchmarks: ['中证REITS', '公募REITs指数'], defaultBenchmark: '中证REITS' },
      { id: 'gold', name: '黄金', benchmarks: ['黄金ETF', '上海金', 'COMEX黄金'], defaultBenchmark: '黄金ETF' },
      { id: 'cta', name: 'CTA', benchmarks: ['招商私募CTA指数', '南华商品指数'], defaultBenchmark: '招商私募CTA指数' },
      { id: 'quant-neutral', name: '量化中性', benchmarks: ['招商私募中性指数', '中证500对冲指数'], defaultBenchmark: '招商私募中性指数' },
      { id: 'absolute-return', name: '绝对收益类', benchmarks: ['债券+点3%', '债券+点5%'], defaultBenchmark: '债券+点3%' },
      { id: 'options', name: '期权', benchmarks: ['3%', '5%', '无风险利率+2%'], defaultBenchmark: '3%' },
      { id: 'liquidity', name: '流动性', benchmarks: ['国债财富1Y以下', '货币基金指数', '银行活期存款利率'], defaultBenchmark: '国债财富1Y以下' }
    ]
  }
];

const MOCK_RETURNS: Record<string, { d1: number; d7: number; m1: number; ytd: number; trend: number[] }> = {
  '高等级1Y以下': { d1: 0.01, d7: 0.05, m1: 0.21, ytd: 2.5, trend: [100, 100.01, 100.02, 100.05, 100.04, 100.08, 100.1] },
  '高等级1-3Y': { d1: 0.02, d7: 0.12, m1: 0.45, ytd: 3.2, trend: [100, 100.02, 100.05, 100.08, 100.12, 100.15, 100.2] },
  '高等级3-5Y': { d1: 0.05, d7: 0.25, m1: 0.85, ytd: 4.1, trend: [100, 100.05, 100.1, 100.15, 100.2, 100.3, 100.4] },
  '美元债LOF': { d1: -0.15, d7: 0.45, m1: 1.2, ytd: 5.5, trend: [100, 99.8, 100.2, 100.5, 100.3, 100.8, 101.2] },
  '中证红利': { d1: 0.45, d7: 1.2, m1: 3.5, ytd: 12.4, trend: [100, 100.5, 101.2, 100.8, 101.5, 102.5, 103.5] },
  '偏股混指数': { d1: -0.8, d7: -1.5, m1: 2.1, ytd: -5.2, trend: [100, 99.2, 98.5, 99.0, 98.2, 99.5, 102.1] },
  '沪深300': { d1: 0.2, d7: 0.8, m1: 1.5, ytd: 3.8, trend: [100, 100.2, 100.5, 101.0, 100.8, 101.2, 101.5] },
  '恒生科技指数ETF': { d1: 1.5, d7: 3.2, m1: -2.5, ytd: -15.4, trend: [100, 101.5, 103.2, 102.5, 100.5, 98.5, 97.5] },
  '二级债基指数': { d1: 0.1, d7: 0.3, m1: 0.8, ytd: 4.5, trend: [100, 100.1, 100.2, 100.4, 100.5, 100.7, 100.8] },
  '0.5*沪深300+0.5*高等级': { d1: 0.15, d7: 0.5, m1: 1.2, ytd: 3.5, trend: [100, 100.1, 100.3, 100.5, 100.6, 100.9, 101.2] },
  '中证转债': { d1: 0.3, d7: 0.9, m1: 2.5, ytd: 6.2, trend: [100, 100.3, 100.8, 101.2, 101.5, 102.0, 102.5] },
  '标普500ETF': { d1: 0.5, d7: 1.5, m1: 4.2, ytd: 18.5, trend: [100, 100.5, 101.2, 102.0, 102.5, 103.5, 104.2] },
  '中证REITS': { d1: -0.2, d7: -0.5, m1: 1.1, ytd: 2.4, trend: [100, 99.8, 99.5, 100.2, 100.5, 100.8, 101.1] },
  '黄金ETF': { d1: 0.8, d7: 2.1, m1: 5.5, ytd: 15.2, trend: [100, 100.8, 101.5, 102.5, 103.5, 104.5, 105.5] },
  '招商私募CTA指数': { d1: 0.1, d7: 0.8, m1: 2.2, ytd: 8.5, trend: [100, 100.1, 100.5, 101.0, 101.5, 102.0, 102.2] },
  '招商私募中性指数': { d1: 0.05, d7: 0.2, m1: 0.8, ytd: 4.2, trend: [100, 100.05, 100.1, 100.2, 100.4, 100.6, 100.8] },
  '债券+点3%': { d1: 0.02, d7: 0.15, m1: 0.6, ytd: 6.5, trend: [100, 100.02, 100.1, 100.2, 100.3, 100.5, 100.6] },
  '3%': { d1: 0.01, d7: 0.06, m1: 0.25, ytd: 3.0, trend: [100, 100.01, 100.03, 100.06, 100.1, 100.15, 100.25] },
  '国债财富1Y以下': { d1: 0.01, d7: 0.04, m1: 0.18, ytd: 2.1, trend: [100, 100.01, 100.02, 100.03, 100.04, 100.1, 100.18] },
};

function getReturns(benchmark: string) {
  if (MOCK_RETURNS[benchmark]) return MOCK_RETURNS[benchmark];
  let hash = 0;
  for (let i = 0; i < benchmark.length; i++) {
    hash = benchmark.charCodeAt(i) + ((hash << 5) - hash);
  }
  const base = (Math.abs(hash) % 50) / 10;
  const s1 = hash % 2 === 0 ? 1 : -1;
  const s2 = hash % 3 === 0 ? 1 : -1;
  const s3 = hash % 5 === 0 ? 1 : -1;
  return {
    d1: base * 0.1 * s1, d7: base * 0.5 * s2, m1: base * 1.5 * s3, ytd: base * 5 * s1,
    trend: Array.from({ length: 7 }).map((_, i) => 100 + i * base * 0.2 * s1)
  };
}

const selectedBenchmarks = reactive<Record<string, string>>({});
MARKET_DATA.forEach(cat => {
  cat.strategies.forEach(strat => {
    selectedBenchmarks[strat.id] = strat.defaultBenchmark;
  });
});
</script>
