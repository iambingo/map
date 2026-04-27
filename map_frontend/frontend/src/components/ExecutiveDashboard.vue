<template>
  <div class="flex flex-col h-full bg-[#161922] text-[#E8ECF4] overflow-y-auto font-sans p-4 space-y-4">
    <!-- Header -->
    <div class="flex justify-between items-end pb-2 border-b border-[#2E3348] shrink-0">
      <div>
        <h1 class="am-title-l1 tracking-wider"><div class="am-title-bar"></div>总裁驾驶舱（调用组合分析） <span class="text-[#94A3B8] text-[13px] ml-3 font-mono font-normal">EXECUTIVE DASHBOARD</span></h1>
        <p class="text-[13px] text-[#B4BAC9] mt-1 font-mono">
          DATA AS OF: 2026-03-24 23:25:53 UTC-7 | SYSTEM STATUS: <span class="text-green-500">OPTIMAL</span>
        </p>
      </div>
      <div class="flex space-x-2">
        <button class="bg-[#1A1E2B] border border-[#3E4660] text-[#B4BAC9] hover:text-white px-3 py-1.5 rounded text-[13px] font-mono transition-colors">EXPORT PDF</button>
        <button class="bg-[#1A1E2B] border border-[#3E4660] text-[#B4BAC9] hover:text-white px-3 py-1.5 rounded text-[13px] font-mono transition-colors">REFRESH</button>
      </div>
    </div>

    <!-- KPI Ribbon -->
    <div class="grid grid-cols-4 gap-4 shrink-0">
      <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-4 relative overflow-hidden group hover:border-[#4A5568] transition-colors">
        <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-[#1A1E2B] to-transparent opacity-50" />
        <h3 class="text-[13px] font-bold text-[#B4BAC9] uppercase tracking-wider mb-1">总管理规模 (AUM)</h3>
        <div class="flex items-baseline space-x-2">
          <span class="text-3xl font-bold text-white font-mono">¥842.5</span>
          <span class="text-[15px] text-[#B4BAC9]">B</span>
        </div>
        <div class="mt-2 flex items-center text-[13px] font-mono text-red-500 bg-red-950/30 w-fit px-1.5 py-1 rounded border border-red-900/50">
          <ArrowUp class="w-3 h-3 mr-1" /><span>+12.4B MoM</span>
        </div>
      </div>
      <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-4 relative overflow-hidden group hover:border-[#4A5568] transition-colors">
        <h3 class="text-[13px] font-bold text-[#B4BAC9] uppercase tracking-wider mb-1">全公司加权收益率 (YTD)</h3>
        <div class="flex items-baseline space-x-2">
          <span class="text-3xl font-bold text-red-500 font-mono">+8.24</span>
          <span class="text-[15px] text-red-500">%</span>
        </div>
        <div class="mt-2 flex items-center text-[13px] font-mono text-red-500 bg-red-950/30 w-fit px-1.5 py-1 rounded border border-red-900/50">
          <ArrowUp class="w-3 h-3 mr-1" /><span>+3.74% vs 基准</span>
        </div>
      </div>
      <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-4 relative overflow-hidden group hover:border-[#4A5568] transition-colors">
        <h3 class="text-[13px] font-bold text-[#B4BAC9] uppercase tracking-wider mb-1">产品胜率 (跑赢同业)</h3>
        <div class="flex items-baseline space-x-2">
          <span class="text-3xl font-bold text-white font-mono">76.5</span>
          <span class="text-[15px] text-[#B4BAC9]">%</span>
        </div>
        <div class="mt-2 flex items-center text-[13px] font-mono text-[#B4BAC9] bg-[#1A1E2B] w-fit px-1.5 py-1 rounded border border-[#3E4660]">
          <Aim class="w-3 h-3 mr-1 text-blue-400" /><span>153 / 200 只产品</span>
        </div>
      </div>
      <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-4 relative overflow-hidden group hover:border-[#4A5568] transition-colors">
        <h3 class="text-[13px] font-bold text-[#B4BAC9] uppercase tracking-wider mb-1">全公司最大回撤水位</h3>
        <div class="flex items-baseline space-x-2">
          <span class="text-3xl font-bold text-green-500 font-mono">-2.15</span>
          <span class="text-[15px] text-green-500">%</span>
        </div>
        <div class="mt-2 flex items-center text-[13px] font-mono text-green-500 bg-green-950/30 w-fit px-1.5 py-1 rounded border border-green-900/50">
          <ArrowDown class="w-3 h-3 mr-1" /><span>安全垫充足 (阈值 -5%)</span>
        </div>
      </div>
    </div>

    <!-- Middle Row: Chart + Treemap -->
    <div class="grid grid-cols-3 gap-4 h-[320px] shrink-0">
      <!-- Performance Area Chart -->
      <div class="col-span-2 bg-[#161922] border border-[#2E3348] rounded-lg p-4 flex flex-col">
        <div class="flex justify-between items-center mb-4 shrink-0">
          <h3 class="am-title-l2 uppercase tracking-wider"><div class="am-title-bar"></div>综合收益率走势 vs 核心基准</h3>
          <div class="flex space-x-4 text-[13px] font-mono">
            <div class="flex items-center"><span class="w-3 h-3 bg-[#3B9EFF]/20 border border-[#3B9EFF] mr-1.5 rounded-sm" /> 本公司综合</div>
            <div class="flex items-center"><span class="w-3 h-3 bg-blue-500/20 border border-blue-500 mr-1.5 rounded-sm" /> 核心同业基准</div>
          </div>
        </div>
        <div class="flex-1 min-h-0">
          <VChart :option="performanceChartOption" autoresize class="w-full h-full" />
        </div>
      </div>

      <!-- Attribution Treemap -->
      <div class="col-span-1 bg-[#161922] border border-[#2E3348] rounded-lg p-4 flex flex-col">
        <div class="flex justify-between items-center mb-4 shrink-0">
          <h3 class="am-title-l2 uppercase tracking-wider"><div class="am-title-bar"></div>超额收益归因穿透</h3>
          <button
            v-if="drilledDept"
            @click="drilledDept = null"
            class="text-[13px] text-[#B4BAC9] hover:text-white bg-[#1A1E2B] border border-[#3E4660] px-2 py-1 rounded transition-colors"
          >返回顶层</button>
        </div>

        <div class="flex-1 relative overflow-hidden">
          <!-- Top Level -->
          <div v-if="!drilledDept" class="absolute inset-0 flex flex-wrap gap-1">
            <div
              @click="drilledDept = '权益投资部'"
              class="w-[58%] h-[60%] bg-red-900/40 border border-red-500/60 p-3 flex flex-col justify-between cursor-pointer hover:bg-red-900/60 transition-colors group"
            >
              <span class="text-[13px] font-bold text-red-100 group-hover:text-white transition-colors">权益投资部</span>
              <div class="flex flex-col">
                <span class="text-2xl font-mono text-red-400 font-bold">+0.82%</span>
                <span class="text-xs text-red-200/50 font-mono">Alpha Contrib.</span>
              </div>
            </div>
            <div
              @click="drilledDept = '固收+部'"
              class="w-[calc(42%-4px)] h-[60%] bg-red-900/20 border border-red-500/40 p-3 flex flex-col justify-between cursor-pointer hover:bg-red-900/40 transition-colors group"
            >
              <span class="text-[13px] font-bold text-red-100 group-hover:text-white transition-colors">固收+部</span>
              <div class="flex flex-col">
                <span class="text-xl font-mono text-red-400 font-bold">+0.51%</span>
              </div>
            </div>
            <div
              @click="drilledDept = '纯债部'"
              class="w-[45%] h-[calc(40%-4px)] bg-green-900/30 border border-green-500/50 p-3 flex flex-col justify-between cursor-pointer hover:bg-green-900/50 transition-colors group"
            >
              <span class="text-[13px] font-bold text-green-100 group-hover:text-white transition-colors">纯债部</span>
              <div class="flex flex-col">
                <span class="text-lg font-mono text-green-400 font-bold">-0.24%</span>
              </div>
            </div>
            <div
              @click="drilledDept = '量化投资部'"
              class="w-[calc(55%-4px)] h-[calc(40%-4px)] bg-red-900/10 border border-red-500/30 p-3 flex flex-col justify-between cursor-pointer hover:bg-red-900/30 transition-colors group"
            >
              <span class="text-[13px] font-bold text-red-100 group-hover:text-white transition-colors">量化投资部</span>
              <div class="flex flex-col">
                <span class="text-lg font-mono text-red-400 font-bold">+0.15%</span>
              </div>
            </div>
          </div>

          <!-- Drilled Down View -->
          <div v-else class="absolute inset-0 flex flex-col">
            <div class="text-[13px] text-[#B4BAC9] mb-2 font-mono border-b border-[#2E3348] pb-2">
              DRILL DOWN: <span class="text-white font-bold">{{ drilledDept }}</span>
            </div>
            <div class="flex-1 flex flex-wrap gap-1">
              <template v-if="drilledDept === '权益投资部'">
                <div class="w-[70%] h-[100%] bg-red-900/50 border border-red-500/70 p-3 flex flex-col justify-between">
                  <span class="text-[13px] font-bold text-red-100">红利低波资产 (超配)</span>
                  <span class="text-xl font-mono text-red-400 font-bold">+0.95%</span>
                </div>
                <div class="w-[calc(30%-4px)] h-[100%] bg-green-900/40 border border-green-500/60 p-3 flex flex-col justify-between">
                  <span class="text-[13px] font-bold text-green-100">TMT科技 (低配)</span>
                  <span class="text-lg font-mono text-green-400 font-bold">-0.13%</span>
                </div>
              </template>
              <div v-else class="w-full h-full flex items-center justify-center text-[#94A3B8] border border-[#2E3348] border-dashed">
                <span class="text-[13px] font-mono">No detailed attribution data for {{ drilledDept }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="grid grid-cols-2 gap-4 h-[280px] shrink-0">
      <!-- Allocation View -->
      <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-4 flex flex-col">
        <h3 class="am-title-l2 mb-4 uppercase tracking-wider shrink-0"><div class="am-title-bar"></div>全盘资产配置视图 (Actual vs SAA)</h3>
        <div class="flex-1 flex flex-col justify-center space-y-4">
          <div v-for="(item, idx) in allocationData" :key="idx" class="flex flex-col space-y-1">
            <div class="flex justify-between text-[13px] font-mono">
              <span class="text-[#B4BAC9]">{{ item.category }}</span>
              <div class="flex space-x-3">
                <span class="text-[#94A3B8]">SAA: {{ item.saa.toFixed(1) }}%</span>
                <span class="text-[#E8ECF4] font-bold">ACT: {{ item.actual.toFixed(1) }}%</span>
                <span :class="['w-12 text-right font-bold', item.diff > 0 ? 'text-red-500' : item.diff < 0 ? 'text-green-500' : 'text-[#B4BAC9]']">
                  {{ item.diff > 0 ? '+' : '' }}{{ item.diff.toFixed(1) }}%
                </span>
              </div>
            </div>
            <div class="relative h-3 bg-[#1A1E2B] rounded overflow-hidden border border-[#2E3348]">
              <div
                :class="['absolute top-0 left-0 h-full', item.diff > 0 ? 'bg-red-500/50' : item.diff < 0 ? 'bg-green-500/50' : 'bg-[#555E75]']"
                :style="{ width: `${item.actual}%` }"
              />
              <div class="absolute top-0 bottom-0 w-0.5 bg-white z-10 shadow-[0_0_4px_rgba(255,255,255,0.8)]" :style="{ left: `${item.saa}%` }" />
            </div>
          </div>
          <div class="flex justify-end space-x-4 mt-2 text-xs font-mono text-[#B4BAC9]">
            <div class="flex items-center"><span class="w-2 h-2 bg-white mr-1.5" /> SAA 战略基准线</div>
            <div class="flex items-center"><span class="w-2 h-2 bg-red-500/50 mr-1.5" /> 超配 (Overweight)</div>
            <div class="flex items-center"><span class="w-2 h-2 bg-green-500/50 mr-1.5" /> 低配 (Underweight)</div>
          </div>
        </div>
      </div>

      <!-- Action & Risk Radar -->
      <div class="bg-[#161922] border border-[#2E3348] rounded-lg p-4 flex flex-col">
        <h3 class="am-title-l2 mb-4 uppercase tracking-wider shrink-0"><div class="am-title-bar"></div>高管行动与风控雷达</h3>
        <div class="flex-1 flex flex-col space-y-4 min-h-0">
          <div class="bg-blue-900/20 border border-blue-500/50 rounded-lg p-3 shrink-0 cursor-pointer hover:bg-blue-900/30 transition-colors group">
            <div class="flex items-start justify-between">
              <div class="flex items-start">
                <div class="bg-blue-500/20 p-1.5 rounded mr-3 mt-0.5">
                  <Lightning class="w-4 h-4 text-blue-400" />
                </div>
                <div>
                  <h4 class="text-[13px] font-bold text-blue-100 mb-1 group-hover:text-white transition-colors">2026 Q2 战术配置投委会投票进行中</h4>
                  <p class="text-[13px] text-blue-300/70">需您在今日 18:00 前完成最终决议投票。</p>
                </div>
              </div>
              <ArrowRight class="w-4 h-4 text-blue-400 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          <div class="flex-1 bg-[#1A1E2B] border border-[#2E3348] rounded-lg p-3 overflow-hidden flex flex-col">
            <h4 class="am-title-l3 font-mono shrink-0"><div class="am-title-bar"></div>REAL-TIME RISK ALERTS</h4>
            <div class="flex-1 overflow-y-auto space-y-2 pr-1">
              <div
                v-for="alert in riskAlerts"
                :key="alert.id"
                class="flex items-start bg-[#161922] border border-[#3E4660] p-2 rounded"
              >
                <div class="shrink-0 mt-0.5 mr-2">
                  <WarningFilled class="w-3.5 h-3.5" :class="alert.level === 'high' ? 'text-red-500' : 'text-yellow-500'" />
                </div>
                <div class="flex-1 min-w-0">
                  <p :class="['text-[13px] leading-relaxed', alert.level === 'high' ? 'text-red-200' : 'text-yellow-200']">
                    {{ alert.message }}
                  </p>
                  <p class="text-xs text-[#94A3B8] font-mono mt-1 flex items-center">
                    <Clock class="w-2.5 h-2.5 mr-1" /> {{ alert.time }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  TrendCharts, DataLine, WarningFilled, Aim, Warning,
  ArrowRight, Histogram, PieChart, ArrowUp, ArrowDown,
  Lightning, Clock, CircleCheckFilled
} from '@element-plus/icons-vue';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent]);

const drilledDept = ref<string | null>(null);

const performanceData = [
  { month: '25/10', company: 2.1, benchmark: 1.5 },
  { month: '25/11', company: 3.5, benchmark: 2.2 },
  { month: '25/12', company: 3.2, benchmark: 2.8 },
  { month: '26/01', company: 5.4, benchmark: 3.5 },
  { month: '26/02', company: 6.8, benchmark: 4.1 },
  { month: '26/03', company: 8.2, benchmark: 4.5 },
];

const performanceChartOption = computed(() => ({
  backgroundColor: 'transparent',
  grid: { top: 10, right: 0, bottom: 20, left: -10, containLabel: true },
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#1A1E2B',
    borderColor: '#3E4660',
    textStyle: { color: '#E8ECF4', fontSize: 11, fontFamily: 'monospace' },
    formatter: (params: any[]) => {
      const label = params[0].axisValue;
      const rows = params.map((p: any) => `<span style="color:${p.color}">${p.seriesName}</span>: <b>${p.value.toFixed(2)}%</b>`).join('<br/>');
      const alpha = params.length >= 2 ? (params[0].value - params[1].value).toFixed(2) : '0.00';
      return `<span style="color:#8B93A8;font-family:monospace">${label}</span><br/>${rows}<br/><span style="color:#8B93A8">超额收益:</span> <b style="color:#22D3EE">+${alpha}%</b>`;
    }
  },
  legend: { show: false },
  xAxis: {
    type: 'category',
    data: performanceData.map(d => d.month),
    axisLine: { show: false }, axisTick: { show: false },
    axisLabel: { color: '#8B93A8', fontSize: 11, fontFamily: 'monospace' }
  },
  yAxis: {
    type: 'value',
    axisLine: { show: false }, axisTick: { show: false },
    axisLabel: { color: '#8B93A8', fontSize: 11, fontFamily: 'monospace', formatter: (v: number) => `${v}%` },
    splitLine: { lineStyle: { color: '#2E3348', type: 'dashed' } }
  },
  series: [
    {
      name: '本公司综合',
      type: 'line',
      data: performanceData.map(d => d.company),
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#3B9EFF', width: 2 },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(59,158,255,0.25)' }, { offset: 1, color: 'rgba(59,158,255,0)' }] } }
    },
    {
      name: '核心同业基准',
      type: 'line',
      data: performanceData.map(d => d.benchmark),
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#00B8D9', width: 2 },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,184,217,0.3)' }, { offset: 1, color: 'rgba(0,184,217,0)' }] } }
    }
  ]
}));

const allocationData = [
  { category: '权益类 (Equity)', actual: 38.5, saa: 30.0, diff: 8.5 },
  { category: '固收类 (Fixed Inc)', actual: 52.0, saa: 60.0, diff: -8.0 },
  { category: '现金类 (Cash)', actual: 6.5, saa: 5.0, diff: 1.5 },
  { category: '另类投资 (Alt)', actual: 3.0, saa: 5.0, diff: -2.0 },
];

const riskAlerts = [
  { id: 1, time: '10:42:15', level: 'high', message: '警告：稳健3号产品实际回撤已达 1.8%，逼近 2.0% 风控阈值' },
  { id: 2, time: '09:15:22', level: 'medium', message: '提示：量化对冲系列A组敞口偏离度超过 3%' },
  { id: 3, time: '昨日 16:30', level: 'high', message: '警告：全公司信用债违约风险敞口上升，涉及主体 [XXX集团]' },
];
</script>
