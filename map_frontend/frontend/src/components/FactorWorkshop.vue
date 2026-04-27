<template>
  <div class="flex flex-col h-full bg-[#161922] text-[#E8ECF4] overflow-hidden font-sans">

    <!-- ═══ HEADER ═══ -->
    <div class="bg-gradient-to-r from-[#1A1E2B] to-[#161922] border-b border-[#252A3A] px-5 py-3 shrink-0 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <button
          @click="sharedIntentState.navigationTarget = 'portal'"
          class="flex items-center text-[#4A5568] hover:text-[#B4BAC9] transition-all duration-150 text-xs font-mono group"
        >
          <ArrowLeft class="w-3 h-3 mr-1 group-hover:-translate-x-0.5 transition-transform duration-150" /> 门户枢纽
        </button>
        <div class="w-px h-4 bg-[#2E3348]"></div>
        <div class="flex items-center space-x-2.5">
          <div class="w-8 h-8 rounded bg-[#3B9EFF]/10 border border-[#3B9EFF]/30 flex items-center justify-center shadow-[0_0_12px_rgba(77,157,224,0.12)]">
            <DataAnalysis class="w-[15px] h-[15px] text-[#3B9EFF]" />
          </div>
          <div>
            <h1 class="text-[15px] font-bold text-white tracking-wider">因子车间</h1>
            <p class="text-[10px] text-[#3B9EFF]/60 font-mono uppercase tracking-widest">Global Factor Library · Quantitative Asset Database</p>
          </div>
        </div>
      </div>

      <div class="flex items-center space-x-2">
        <!-- Search -->
        <div class="flex items-center bg-[#1A1E2B] border border-[#2A2F40] rounded-lg px-2.5 py-1.5 space-x-2 w-56 focus-within:border-[#3B9EFF]/40 transition-colors duration-200">
          <Search class="w-3 h-3 text-[#4A5568] shrink-0" />
          <input v-model="searchQuery" placeholder="搜索因子名称 / ID..." class="bg-transparent text-[#E8ECF4] text-[13px] outline-none placeholder-[#3E4660] w-full font-mono" />
        </div>
        <!-- Sort -->
        <div class="flex items-center bg-[#1A1E2B] border border-[#2A2F40] rounded-lg p-0.5">
          <button
            v-for="s in SORT_OPTIONS" :key="s.key"
            @click="sortKey = s.key; sortAsc = sortKey === s.key ? !sortAsc : false"
            :class="cn('px-2.5 py-1 rounded-md text-xs font-mono transition-all duration-150', sortKey === s.key ? 'bg-[#2A2F40] text-[#3B9EFF]' : 'text-[#94A3B8] hover:text-[#B4BAC9]')"
          >{{ s.label }}</button>
        </div>
        <span class="text-[11px] font-mono text-[#7B8BA3]">{{ filteredFactors.length }} / {{ FACTORS.length }} 个因子</span>
      </div>
    </div>

    <!-- ═══ CATEGORY CARDS ═══ -->
    <div class="px-5 py-3 border-b border-[#1A1E2B] shrink-0">
      <div class="flex items-center space-x-2">
        <button
          @click="activeCategory = null"
          :class="cn('flex items-center space-x-2 px-3 py-2 rounded-lg border text-[13px] font-medium transition-all duration-150 shrink-0',
            activeCategory === null ? 'bg-[#3B9EFF]/10 border-[#3B9EFF]/30 text-[#3B9EFF]' : 'bg-[#161922] border-[#252A3A] text-[#94A3B8] hover:border-[#2E3348] hover:text-[#B4BAC9]')"
        >
          <Operation class="w-3.5 h-3.5" />
          <span>全部 ({{ FACTORS.length }})</span>
        </button>
        <button
          v-for="cat in CATEGORIES" :key="cat.key"
          @click="activeCategory = activeCategory === cat.key ? null : cat.key"
          :class="cn('flex items-center space-x-2 px-3 py-2 rounded-lg border text-[13px] font-medium transition-all duration-150 shrink-0',
            activeCategory === cat.key
              ? `${cat.activeBg} ${cat.activeBorder} ${cat.activeText}`
              : 'bg-[#161922] border-[#252A3A] text-[#94A3B8] hover:border-[#2E3348] hover:text-[#B4BAC9]')"
        >
          <div :class="cn('w-2 h-2 rounded-full shrink-0', cat.dot)"></div>
          <span>{{ cat.label }}</span>
          <span :class="cn('text-[11px] font-mono', activeCategory === cat.key ? cat.activeText : 'text-[#7B8BA3]')">{{ factorCountByCategory[cat.key] }}</span>
        </button>
      </div>
    </div>

    <!-- ═══ MAIN AREA (table + sidebar) ═══ -->
    <div class="flex flex-1 overflow-hidden">

      <!-- Factor Table -->
      <div class="flex-1 overflow-y-auto no-scrollbar">
        <table class="w-full text-[13px] border-collapse">
          <thead class="sticky top-0 z-10 bg-[#161922] shadow-[0_1px_0_rgba(42,42,42,1)]">
            <tr>
              <th class="text-left px-4 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest w-10">#</th>
              <th class="text-left px-3 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest">因子名称</th>
              <th class="text-left px-3 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest">分类</th>
              <th class="text-left px-3 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest cursor-pointer hover:text-[#3B9EFF] transition-colors" @click="toggleSort('ic')">
                IC均值 <span class="ml-0.5">{{ sortKey === 'ic' ? (sortAsc ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th class="text-left px-3 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest cursor-pointer hover:text-[#3B9EFF] transition-colors" @click="toggleSort('icir')">
                ICIR <span class="ml-0.5">{{ sortKey === 'icir' ? (sortAsc ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th class="text-left px-3 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest cursor-pointer hover:text-[#3B9EFF] transition-colors" @click="toggleSort('sharpe')">
                夏普比率 <span class="ml-0.5">{{ sortKey === 'sharpe' ? (sortAsc ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th class="text-left px-3 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest cursor-pointer hover:text-[#3B9EFF] transition-colors" @click="toggleSort('turnover')">
                换手率 <span class="ml-0.5">{{ sortKey === 'turnover' ? (sortAsc ? '↑' : '↓') : '↕' }}</span>
              </th>
              <th class="text-left px-3 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest">覆盖率</th>
              <th class="text-left px-3 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest">引用模型</th>
              <th class="text-right px-4 py-2.5 text-[11px] font-mono text-[#4A5568] uppercase tracking-widest">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(factor, idx) in filteredFactors" :key="factor.id"
              @click="selectedFactor = factor"
              :class="cn(
                'border-b border-[#1A1E2B] cursor-pointer transition-all duration-100 group',
                selectedFactor?.id === factor.id ? 'bg-[#3B9EFF]/5 border-l-2 border-l-[#3B9EFF]' : 'hover:bg-[#1A1E2B]'
              )"
            >
              <!-- # -->
              <td class="px-4 py-2.5 text-[11px] font-mono text-[#7B8BA3]">{{ idx + 1 }}</td>

              <!-- Name + ID -->
              <td class="px-3 py-2.5">
                <div class="flex flex-col">
                  <span class="text-[13px] font-bold text-[#E8ECF4] group-hover:text-white transition-colors">{{ factor.name }}</span>
                  <span class="text-[11px] font-mono text-[#94A3B8] mt-0.5">{{ factor.factorId }}</span>
                </div>
              </td>

              <!-- Category badge -->
              <td class="px-3 py-2.5">
                <span :class="cn('text-[11px] font-mono px-2 py-1 rounded-md border', getCategoryStyle(factor.category))">
                  {{ factor.category }}
                </span>
              </td>

              <!-- IC -->
              <td class="px-3 py-2.5">
                <span :class="cn('font-mono font-bold text-[13px]', factor.ic > 0 ? 'text-green-400' : factor.ic < -0.01 ? 'text-red-400' : 'text-[#B4BAC9]')">
                  {{ factor.ic > 0 ? '+' : '' }}{{ factor.ic.toFixed(4) }}
                </span>
              </td>

              <!-- ICIR -->
              <td class="px-3 py-2.5">
                <div class="flex items-center space-x-2">
                  <span :class="cn('font-mono text-[13px]', factor.icir >= 1.5 ? 'text-green-400' : factor.icir >= 0.8 ? 'text-[#E8ECF4]' : 'text-red-400')">
                    {{ factor.icir.toFixed(2) }}
                  </span>
                  <div class="w-12 h-1 bg-[#2A2D3A] rounded-full overflow-hidden">
                    <div
                      :class="cn('h-full rounded-full', factor.icir >= 1.5 ? 'bg-green-500' : factor.icir >= 0.8 ? 'bg-[#3B9EFF]' : 'bg-red-500')"
                      :style="{ width: Math.min(factor.icir / 3 * 100, 100) + '%' }"
                    ></div>
                  </div>
                </div>
              </td>

              <!-- Sharpe -->
              <td class="px-3 py-2.5">
                <div class="flex items-center space-x-2">
                  <span :class="cn('font-mono text-[13px]', factor.sharpe >= 1.5 ? 'text-green-400' : factor.sharpe >= 0.8 ? 'text-[#E8ECF4]' : 'text-[#B4BAC9]')">
                    {{ factor.sharpe.toFixed(2) }}
                  </span>
                  <div class="w-12 h-1 bg-[#2A2D3A] rounded-full overflow-hidden">
                    <div class="h-full bg-[#3B9EFF] rounded-full" :style="{ width: Math.min(factor.sharpe / 3 * 100, 100) + '%' }"></div>
                  </div>
                </div>
              </td>

              <!-- Turnover -->
              <td class="px-3 py-2.5">
                <span :class="cn('font-mono text-[13px]', factor.turnover < 0.2 ? 'text-green-400' : factor.turnover < 0.5 ? 'text-[#E8ECF4]' : 'text-[#FFAB00]')">
                  {{ (factor.turnover * 100).toFixed(1) }}%
                </span>
              </td>

              <!-- Coverage -->
              <td class="px-3 py-2.5">
                <div class="flex items-center space-x-1.5">
                  <span class="font-mono text-xs text-[#B4BAC9]">{{ (factor.coverage * 100).toFixed(0) }}%</span>
                  <div class="w-10 h-1 bg-[#2A2D3A] rounded-full overflow-hidden">
                    <div class="h-full bg-[#9747FF] rounded-full" :style="{ width: factor.coverage * 100 + '%' }"></div>
                  </div>
                </div>
              </td>

              <!-- Referenced models count -->
              <td class="px-3 py-2.5">
                <span v-if="factor.models.length > 0" class="flex items-center space-x-1 text-[#3B9EFF] text-[11px] font-mono">
                  <Connection class="w-3 h-3" />
                  <span>{{ factor.models.length }} 个</span>
                </span>
                <span v-else class="text-[#7B8BA3] text-[11px] font-mono">—</span>
              </td>

              <!-- Actions -->
              <td class="px-4 py-2.5 text-right">
                <button
                  @click.stop="copyFactorRef(factor)"
                  class="flex items-center space-x-1 px-2 py-1 rounded bg-[#1A1E2B] border border-[#2A2F40] text-[#94A3B8] hover:text-[#3B9EFF] hover:border-[#3B9EFF]/30 hover:bg-[#3B9EFF]/5 transition-all duration-150 text-[11px] font-mono ml-auto"
                  title="复制引用变量名"
                >
                  <CopyDocument class="w-3 h-3" />
                  <span>引用</span>
                </button>
              </td>
            </tr>

            <!-- Empty -->
            <tr v-if="filteredFactors.length === 0">
              <td colspan="10" class="px-4 py-16 text-center">
                <p class="text-[15px] text-[#7B8BA3] font-mono">未找到匹配的因子</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ═══ DETAIL SIDEBAR ═══ -->
      <Transition
        enter-active-class="transition-all duration-250 ease-out"
        enter-from-class="opacity-0 translate-x-4"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-x-0"
        leave-to-class="opacity-0 translate-x-4"
      >
        <div v-if="selectedFactor" class="w-80 bg-[#161922] border-l border-[#252A3A] flex flex-col shrink-0 overflow-hidden">
          <!-- Sidebar header -->
          <div class="px-4 py-3.5 border-b border-[#252A3A] flex items-center justify-between bg-gradient-to-r from-[#1A1E2B] to-[#161922]">
            <div class="flex items-center space-x-2 min-w-0">
              <div :class="cn('w-2.5 h-2.5 rounded-full shrink-0', getCategoryDot(selectedFactor.category))"></div>
              <div class="min-w-0">
                <p class="text-[13px] font-bold text-white truncate">{{ selectedFactor.name }}</p>
                <p class="text-[11px] font-mono text-[#3B9EFF]/60 mt-0.5">{{ selectedFactor.factorId }}</p>
              </div>
            </div>
            <button @click="selectedFactor = null" class="text-[#7B8BA3] hover:text-[#B4BAC9] transition-colors p-1 rounded hover:bg-[#2A2D3A] shrink-0">
              <Close class="w-3.5 h-3.5" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto no-scrollbar p-4 space-y-4">

            <!-- Key metrics -->
            <div class="grid grid-cols-2 gap-2">
              <div
                v-for="metric in getMetrics(selectedFactor)" :key="metric.label"
                class="bg-[#1A1E2B] border border-[#252A3A] rounded-lg p-3"
              >
                <p class="text-[10px] font-mono text-[#4A5568] uppercase tracking-widest mb-1">{{ metric.label }}</p>
                <p :class="cn('text-[15px] font-bold font-mono', metric.color)">{{ metric.value }}</p>
                <p class="text-[10px] text-[#7B8BA3] mt-0.5 font-mono">{{ metric.sub }}</p>
              </div>
            </div>

            <!-- Description -->
            <div class="bg-[#1A1E2B] border border-[#252A3A] rounded-lg p-3">
              <p class="text-[10px] font-mono text-[#4A5568] uppercase tracking-widest mb-2">因子说明</p>
              <p class="text-[13px] text-[#B4BAC9] leading-relaxed">{{ selectedFactor.description }}</p>
            </div>

            <!-- Copy reference -->
            <div class="bg-[#3B9EFF]/5 border border-[#3B9EFF]/20 rounded-lg p-3">
              <p class="text-[10px] font-mono text-[#3B9EFF]/60 uppercase tracking-widest mb-2">引用变量名</p>
              <div class="flex items-center justify-between bg-[#161922] border border-[#252A3A] rounded px-2.5 py-1.5">
                <code class="text-xs font-mono text-[#3B9EFF]">{{ selectedFactor.refVar }}</code>
                <button
                  @click="copyFactorRef(selectedFactor)"
                  class="text-[#3B9EFF]/40 hover:text-[#3B9EFF] transition-colors ml-2 shrink-0"
                >
                  <CopyDocument class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <!-- Referenced models -->
            <div>
              <div class="flex items-center space-x-2 mb-2.5">
                <Connection class="w-3.5 h-3.5 text-[#94A3B8]" />
                <p class="text-[11px] font-mono text-[#94A3B8] uppercase tracking-widest">被引用模型</p>
                <span class="text-[10px] font-mono text-[#7B8BA3] bg-[#1A1E2B] border border-[#252A3A] px-1.5 py-1 rounded-full">{{ selectedFactor.models.length }}</span>
              </div>

              <div v-if="selectedFactor.models.length > 0" class="space-y-1.5">
                <div
                  v-for="model in selectedFactor.models" :key="model.id"
                  class="flex items-center space-x-2.5 bg-[#1A1E2B] border border-[#252A3A] rounded-lg px-3 py-2 hover:border-[#2E3348] transition-colors group/m cursor-pointer"
                >
                  <div class="w-6 h-6 rounded bg-red-900/20 border border-red-500/20 flex items-center justify-center shrink-0">
                    <Cpu class="w-3 h-3 text-red-400/60" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-medium text-[#B8BFCC] group-hover/m:text-white transition-colors truncate">{{ model.name }}</p>
                    <p class="text-[10px] font-mono text-[#4A5568] mt-0.5">{{ model.version }} · {{ model.usedAt }}</p>
                  </div>
                  <ArrowRight class="w-3 h-3 text-[#7B8BA3] group-hover/m:text-[#3B9EFF] transition-colors shrink-0" />
                </div>
              </div>
              <div v-else class="py-4 text-center">
                <p class="text-xs text-[#7B8BA3] font-mono">暂无模型引用此因子</p>
              </div>
            </div>

            <!-- IC Trend sparkline (mock bars) -->
            <div class="bg-[#1A1E2B] border border-[#252A3A] rounded-lg p-3">
              <div class="flex items-center justify-between mb-2.5">
                <p class="text-[10px] font-mono text-[#4A5568] uppercase tracking-widest">近12月 IC 走势</p>
                <span class="text-[10px] font-mono text-[#7B8BA3]">月度</span>
              </div>
              <div class="flex items-end space-x-1 h-10">
                <div
                  v-for="(v, i) in selectedFactor.icHistory" :key="i"
                  :class="cn('flex-1 rounded-sm min-h-[2px] transition-all duration-200', v > 0 ? 'bg-green-500/60 hover:bg-green-400' : 'bg-red-500/60 hover:bg-red-400')"
                  :style="{ height: Math.abs(v) / 0.06 * 40 + 'px' }"
                  :title="`${v > 0 ? '+' : ''}${v.toFixed(4)}`"
                ></div>
              </div>
              <div class="flex justify-between mt-1">
                <span class="text-[10px] font-mono text-[#7B8BA3]">12m ago</span>
                <span class="text-[10px] font-mono text-[#7B8BA3]">Now</span>
              </div>
            </div>

          </div>

          <!-- Push to model center -->
          <div class="p-4 border-t border-[#252A3A] space-y-2 shrink-0 bg-[#161922]">
            <button
              @click="pushToModelCenter(selectedFactor)"
              :disabled="pushedIds.has(selectedFactor.id)"
              :class="cn('w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg text-[13px] font-bold transition-all duration-200',
                pushedIds.has(selectedFactor.id)
                  ? 'bg-green-900/20 border border-green-500/20 text-green-400 cursor-default'
                  : 'bg-red-600 hover:bg-red-500 hover:shadow-[0_0_20px_rgba(220,38,38,0.3)] text-white border border-transparent')"
            >
              <CircleCheckFilled v-if="pushedIds.has(selectedFactor.id)" class="w-3.5 h-3.5" />
              <Promotion v-else class="w-3.5 h-3.5" />
              <span>{{ pushedIds.has(selectedFactor.id) ? '已加入待选池' : '推送至模型中心' }}</span>
            </button>
            <p class="text-[10px] font-mono text-[#7B8BA3] text-center">
              {{ pushedIds.has(selectedFactor.id) ? '因子已在模型中心「待选因子池」中' : '将此因子加入模型中心的「待选因子池」' }}
            </p>
          </div>
        </div>
      </Transition>
    </div>

    <!-- ═══ TOAST ═══ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0 translate-y-4"
      >
        <div v-if="showToast" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[9999] bg-[#1A1E2B] border border-[#3B9EFF]/30 shadow-[0_0_40px_rgba(77,157,224,0.15)] rounded-xl px-5 py-3 flex items-center space-x-3 pointer-events-none whitespace-nowrap">
          <CircleCheckFilled class="w-4 h-4 text-[#3B9EFF] shrink-0" />
          <span class="text-[13px] font-mono text-[#E8ECF4]">{{ toastMsg }}</span>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  ArrowLeft, ArrowRight, DataAnalysis, Search, Operation, Connection,
  CopyDocument, Promotion, CircleCheckFilled, Close, Cpu,
} from '@element-plus/icons-vue';
import { sharedIntentState } from '../store/intentStore';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

// ── Types ──────────────────────────────────────────────────────────────────────
type CategoryKey = '红利' | '低波' | '质量' | '价值' | '动量' | '宏观' | '量价';

interface ModelRef {
  id: string;
  name: string;
  version: string;
  usedAt: string;
}

interface Factor {
  id: string;
  name: string;
  factorId: string;
  refVar: string;
  category: CategoryKey;
  ic: number;
  icir: number;
  sharpe: number;
  turnover: number;
  coverage: number;
  description: string;
  models: ModelRef[];
  icHistory: number[];
}

// ── Category config ────────────────────────────────────────────────────────────
const CATEGORIES: {
  key: CategoryKey; label: string; dot: string;
  activeBg: string; activeBorder: string; activeText: string;
}[] = [
  { key: '红利', label: '红利',  dot: 'bg-red-400',     activeBg: 'bg-red-400/10',     activeBorder: 'border-red-400/30',     activeText: 'text-red-400'    },
  { key: '低波', label: '低波',  dot: 'bg-blue-400',    activeBg: 'bg-blue-400/10',    activeBorder: 'border-blue-400/30',    activeText: 'text-blue-400'   },
  { key: '质量', label: '质量',  dot: 'bg-emerald-400', activeBg: 'bg-emerald-400/10', activeBorder: 'border-emerald-400/30', activeText: 'text-emerald-400'},
  { key: '价值', label: '价值',  dot: 'bg-orange-400',  activeBg: 'bg-orange-400/10',  activeBorder: 'border-orange-400/30',  activeText: 'text-orange-400' },
  { key: '动量', label: '动量',  dot: 'bg-yellow-400',  activeBg: 'bg-yellow-400/10',  activeBorder: 'border-yellow-400/30',  activeText: 'text-yellow-400' },
  { key: '宏观', label: '宏观',  dot: 'bg-purple-400',  activeBg: 'bg-purple-400/10',  activeBorder: 'border-purple-400/30',  activeText: 'text-purple-400' },
  { key: '量价', label: '量价',  dot: 'bg-cyan-400',    activeBg: 'bg-cyan-400/10',    activeBorder: 'border-cyan-400/30',    activeText: 'text-cyan-400'   },
];

function getCategoryStyle(cat: CategoryKey) {
  const c = CATEGORIES.find(c => c.key === cat);
  return c ? `${c.activeBg} ${c.activeBorder} ${c.activeText}` : 'bg-[#1A1E2B] border-[#252A3A] text-[#94A3B8]';
}
function getCategoryDot(cat: CategoryKey) {
  return CATEGORIES.find(c => c.key === cat)?.dot ?? 'bg-[#555E75]';
}

// ── Sort ───────────────────────────────────────────────────────────────────────
const SORT_OPTIONS = [
  { key: 'ic',       label: 'IC' },
  { key: 'icir',     label: 'ICIR' },
  { key: 'sharpe',   label: '夏普' },
  { key: 'turnover', label: '换手' },
] as const;
type SortKey = typeof SORT_OPTIONS[number]['key'];

const sortKey = ref<SortKey>('icir');
const sortAsc = ref(false);

function toggleSort(key: SortKey) {
  if (sortKey.value === key) { sortAsc.value = !sortAsc.value; }
  else { sortKey.value = key; sortAsc.value = false; }
}

// ── State ──────────────────────────────────────────────────────────────────────
const searchQuery    = ref('');
const activeCategory = ref<CategoryKey | null>(null);
const selectedFactor = ref<Factor | null>(null);
const pushedIds      = ref<Set<string>>(new Set());

// ── Toast ──────────────────────────────────────────────────────────────────────
const showToast = ref(false);
const toastMsg  = ref('');
let _toastTimer: ReturnType<typeof setTimeout> | null = null;
function fireToast(msg: string) {
  toastMsg.value = msg;
  showToast.value = true;
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { showToast.value = false; }, 3200);
}

// ── Actions ────────────────────────────────────────────────────────────────────
function copyFactorRef(factor: Factor) {
  navigator.clipboard.writeText(factor.refVar).catch(() => {});
  fireToast(`已复制因子引用变量名：${factor.refVar}`);
}

function pushToModelCenter(factor: Factor) {
  const s = new Set(pushedIds.value);
  s.add(factor.id);
  pushedIds.value = s;
  fireToast(`✅ [${factor.name}] 已加入模型中心「待选因子池」`);
}

// ── Metrics helper ─────────────────────────────────────────────────────────────
function getMetrics(f: Factor) {
  return [
    { label: 'IC 均值', value: (f.ic > 0 ? '+' : '') + f.ic.toFixed(4), sub: '5年滚动均值', color: f.ic > 0 ? 'text-green-400' : 'text-red-400' },
    { label: 'ICIR',   value: f.icir.toFixed(2), sub: 'IC / std(IC)', color: f.icir >= 1.5 ? 'text-green-400' : f.icir >= 0.8 ? 'text-[#E8ECF4]' : 'text-red-400' },
    { label: '夏普比率', value: f.sharpe.toFixed(2), sub: 'L/S 多空组合', color: f.sharpe >= 1.5 ? 'text-green-400' : 'text-[#E8ECF4]' },
    { label: '月均换手', value: (f.turnover * 100).toFixed(1) + '%', sub: '较低更稳定', color: f.turnover < 0.2 ? 'text-green-400' : f.turnover < 0.5 ? 'text-[#E8ECF4]' : 'text-orange-400' },
  ];
}

// ── Mock factor data ───────────────────────────────────────────────────────────
function rndIC(): number[] {
  return Array.from({ length: 12 }, () => parseFloat((Math.random() * 0.1 - 0.03).toFixed(4)));
}

const FACTORS: Factor[] = [
  {
    id: 'F001', name: '股息率因子', factorId: 'factor.equity.div_yield',
    refVar: '$factor.equity.div_yield', category: '红利',
    ic: 0.0421, icir: 2.18, sharpe: 1.92, turnover: 0.08, coverage: 0.96,
    description: '基于过去12个月现金分红与当前市值之比，剔除ST及亏损股后计算。高股息公司在利率下行周期表现显著优于市场。',
    models: [
      { id: 'm1', name: '中短债红利增强策略', version: 'V3.2', usedAt: '2026-03' },
      { id: 'm2', name: '固收+多资产轮动模型', version: 'V1.8', usedAt: '2026-01' },
      { id: 'm3', name: '红利低波因子组合', version: 'V2.1', usedAt: '2025-12' },
    ],
    icHistory: rndIC(),
  },
  {
    id: 'F002', name: '股息持续性因子', factorId: 'factor.equity.div_consistency',
    refVar: '$factor.equity.div_consistency', category: '红利',
    ic: 0.0318, icir: 1.74, sharpe: 1.55, turnover: 0.05, coverage: 0.91,
    description: '连续3年以上分红且分红金额逐年递增的因子。筛选高质量红利股，降低红利陷阱风险。',
    models: [{ id: 'm3', name: '红利低波因子组合', version: 'V2.1', usedAt: '2025-12' }],
    icHistory: rndIC(),
  },
  {
    id: 'F003', name: '历史波动率因子', factorId: 'factor.risk.hist_vol_60d',
    refVar: '$factor.risk.hist_vol_60d', category: '低波',
    ic: 0.0289, icir: 1.61, sharpe: 1.44, turnover: 0.15, coverage: 0.99,
    description: '过去60个交易日收益率的标准差（年化）。低波因子在高波动市场环境下具有显著的防御属性。',
    models: [
      { id: 'm4', name: '低波防御组合模型', version: 'V2.0', usedAt: '2026-02' },
      { id: 'm2', name: '固收+多资产轮动模型', version: 'V1.8', usedAt: '2026-01' },
    ],
    icHistory: rndIC(),
  },
  {
    id: 'F004', name: 'Beta中性化波动', factorId: 'factor.risk.idiosync_vol',
    refVar: '$factor.risk.idiosync_vol', category: '低波',
    ic: 0.0195, icir: 1.22, sharpe: 1.08, turnover: 0.12, coverage: 0.97,
    description: '对市场Beta进行回归后的残差波动率。相比原始波动率更纯粹地捕捉个股特质风险。',
    models: [],
    icHistory: rndIC(),
  },
  {
    id: 'F005', name: 'ROE因子', factorId: 'factor.quality.roe_ttm',
    refVar: '$factor.quality.roe_ttm', category: '质量',
    ic: 0.0512, icir: 2.65, sharpe: 2.14, turnover: 0.06, coverage: 0.94,
    description: '滚动12个月净资产收益率（TTM）。是衡量企业盈利质量的核心指标，与长期超额收益相关性最强。',
    models: [
      { id: 'm5', name: '质量动量增强策略', version: 'V4.1', usedAt: '2026-03' },
      { id: 'm6', name: '中短债避险模型 V2', version: 'V2.3', usedAt: '2026-02' },
      { id: 'm7', name: 'A股质量因子组合', version: 'V1.5', usedAt: '2025-11' },
    ],
    icHistory: rndIC(),
  },
  {
    id: 'F006', name: '资产负债率因子', factorId: 'factor.quality.debt_ratio',
    refVar: '$factor.quality.debt_ratio', category: '质量',
    ic: -0.0234, icir: -1.38, sharpe: 1.22, turnover: 0.04, coverage: 0.93,
    description: '总负债/总资产。低负债率公司在信用收紧环境下具有更强的抗风险能力，该因子取反向使用。',
    models: [{ id: 'm6', name: '中短债避险模型 V2', version: 'V2.3', usedAt: '2026-02' }],
    icHistory: rndIC(),
  },
  {
    id: 'F007', name: '市盈率因子 (EP)', factorId: 'factor.value.ep_ttm',
    refVar: '$factor.value.ep_ttm', category: '价值',
    ic: 0.0348, icir: 1.85, sharpe: 1.62, turnover: 0.09, coverage: 0.95,
    description: '每股收益TTM / 股价（EP为PE倒数）。低估值因子在经济周期底部具有较强的均值回归特性。',
    models: [
      { id: 'm8', name: '深度价值轮动策略', version: 'V2.7', usedAt: '2026-01' },
      { id: 'm5', name: '质量动量增强策略', version: 'V4.1', usedAt: '2026-03' },
    ],
    icHistory: rndIC(),
  },
  {
    id: 'F008', name: '市净率因子 (BP)', factorId: 'factor.value.bp',
    refVar: '$factor.value.bp', category: '价值',
    ic: 0.0267, icir: 1.41, sharpe: 1.28, turnover: 0.07, coverage: 0.98,
    description: '账面价值 / 市值。对于金融、地产等重资产行业，BP因子的定价能力优于PE。',
    models: [{ id: 'm8', name: '深度价值轮动策略', version: 'V2.7', usedAt: '2026-01' }],
    icHistory: rndIC(),
  },
  {
    id: 'F009', name: '1个月价格动量', factorId: 'factor.momentum.mom_1m',
    refVar: '$factor.momentum.mom_1m', category: '动量',
    ic: 0.0183, icir: 1.05, sharpe: 0.94, turnover: 0.62, coverage: 0.99,
    description: '过去1个月收益率（跳过最近5日）。短期反转与动量并存，需配合T+1调仓成本控制使用。',
    models: [{ id: 'm5', name: '质量动量增强策略', version: 'V4.1', usedAt: '2026-03' }],
    icHistory: rndIC(),
  },
  {
    id: 'F010', name: '12-1月价格动量', factorId: 'factor.momentum.mom_12_1m',
    refVar: '$factor.momentum.mom_12_1m', category: '动量',
    ic: 0.0412, icir: 2.04, sharpe: 1.78, turnover: 0.18, coverage: 0.97,
    description: '过去12个月至1个月的累计收益率（排除最近1月反转效应）。中长期趋势追踪效果优于短期动量。',
    models: [
      { id: 'm5', name: '质量动量增强策略', version: 'V4.1', usedAt: '2026-03' },
      { id: 'm9', name: '跨资产趋势跟踪模型', version: 'V1.2', usedAt: '2025-10' },
    ],
    icHistory: rndIC(),
  },
  {
    id: 'F011', name: '利率期限结构斜率', factorId: 'factor.macro.yield_curve_slope',
    refVar: '$factor.macro.yield_curve_slope', category: '宏观',
    ic: 0.0356, icir: 1.93, sharpe: 1.71, turnover: 0.03, coverage: 1.0,
    description: '10年期与1年期国债收益率之差。期限利差扩大预示经济复苏预期增强，通常利好权益资产。',
    models: [
      { id: 'm6', name: '中短债避险模型 V2', version: 'V2.3', usedAt: '2026-02' },
      { id: 'm2', name: '固收+多资产轮动模型', version: 'V1.8', usedAt: '2026-01' },
      { id: 'm9', name: '跨资产趋势跟踪模型', version: 'V1.2', usedAt: '2025-10' },
    ],
    icHistory: rndIC(),
  },
  {
    id: 'F012', name: '信用利差因子', factorId: 'factor.macro.credit_spread',
    refVar: '$factor.macro.credit_spread', category: '宏观',
    ic: -0.0298, icir: -1.67, sharpe: 1.45, turnover: 0.02, coverage: 1.0,
    description: 'AA级企业债与同期限国债的利差（取反，利差收窄为正信号）。信用利差扩张往往预示信用风险上升。',
    models: [{ id: 'm6', name: '中短债避险模型 V2', version: 'V2.3', usedAt: '2026-02' }],
    icHistory: rndIC(),
  },
  {
    id: 'F013', name: '成交量变化率', factorId: 'factor.technical.vol_change_20d',
    refVar: '$factor.technical.vol_change_20d', category: '量价',
    ic: 0.0144, icir: 0.87, sharpe: 0.76, turnover: 0.44, coverage: 0.98,
    description: '过去20日平均成交量相对于过去60日的变化率。成交量放大通常预示趋势转折或加速。',
    models: [],
    icHistory: rndIC(),
  },
  {
    id: 'F014', name: 'VWAP偏离度', factorId: 'factor.technical.vwap_dev_10d',
    refVar: '$factor.technical.vwap_dev_10d', category: '量价',
    ic: 0.0211, icir: 1.18, sharpe: 1.02, turnover: 0.38, coverage: 0.99,
    description: '当前价格相对于过去10日成交量加权均价的偏离程度。可识别短期超买超卖机会。',
    models: [{ id: 'm9', name: '跨资产趋势跟踪模型', version: 'V1.2', usedAt: '2025-10' }],
    icHistory: rndIC(),
  },
  {
    id: 'F015', name: '分析师盈利预测修正', factorId: 'factor.analyst.eps_revision_3m',
    refVar: '$factor.analyst.eps_revision_3m', category: '质量',
    ic: 0.0467, icir: 2.41, sharpe: 2.02, turnover: 0.22, coverage: 0.72,
    description: '近3个月分析师对EPS预测的上调/下调幅度。预测上调意味着基本面改善预期，具有较强的Alpha捕获能力。',
    models: [
      { id: 'm5', name: '质量动量增强策略', version: 'V4.1', usedAt: '2026-03' },
      { id: 'm7', name: 'A股质量因子组合', version: 'V1.5', usedAt: '2025-11' },
    ],
    icHistory: rndIC(),
  },
];

// ── Category counts ────────────────────────────────────────────────────────────
const factorCountByCategory = computed(() => {
  const counts: Partial<Record<CategoryKey, number>> = {};
  for (const f of FACTORS) counts[f.category] = (counts[f.category] ?? 0) + 1;
  return counts;
});

// ── Filtered + sorted ─────────────────────────────────────────────────────────
const filteredFactors = computed<Factor[]>(() => {
  let result = FACTORS.filter(f => {
    const matchCat = !activeCategory.value || f.category === activeCategory.value;
    const q = searchQuery.value.trim().toLowerCase();
    const matchQ = !q || f.name.toLowerCase().includes(q) || f.factorId.toLowerCase().includes(q) || f.refVar.toLowerCase().includes(q);
    return matchCat && matchQ;
  });

  const k = sortKey.value;
  result = [...result].sort((a, b) => {
    const diff = (a[k] as number) - (b[k] as number);
    return sortAsc.value ? diff : -diff;
  });

  return result;
});
</script>
