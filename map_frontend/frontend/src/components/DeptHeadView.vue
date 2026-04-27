<template>
  <div class="flex flex-col space-y-6 h-full bg-[#161922] text-[#E8ECF4] p-4 overflow-y-auto">
    <!-- Header -->
    <div class="bg-[#202431] border border-[#2E3348] rounded-xl p-4 shrink-0 flex justify-between items-center shadow-lg sticky top-0 z-20">
      <div class="flex items-center space-x-6">
        <div class="flex items-center space-x-3">
          <div>
            <h2 class="am-title-l1">
              <div class="am-title-bar"></div> 部门长决策台 (Dept TAA)
            </h2>
            <p class="text-xs text-[#B4BAC9] ml-3 font-mono">基于投委决议，制定部门级策略目标组合</p>
          </div>
        </div>

        <div class="h-8 w-px bg-[#2E3348]"></div>

        <div class="flex space-x-4">
          <div class="flex flex-col">
            <span class="text-[11px] text-[#B4BAC9] mb-1">管理部门</span>
            <div class="relative">
              <select
                v-model="department"
                class="appearance-none bg-[#161922] border border-[#4A4A4A] text-[#E8ECF4] text-[13px] font-bold rounded pl-3 pr-8 py-1.5 outline-none focus:border-[#3B9EFF] transition-colors"
              >
                <option value="固收+投资部">固收+投资部</option>
                <option value="固收投资部">固收投资部</option>
                <option value="混合投资部">混合投资部</option>
              </select>
              <ArrowDown class="w-3.5 h-3.5 absolute right-2 top-1/2 -translate-y-1/2 text-[#B4BAC9] pointer-events-none" />
            </div>
          </div>
        </div>
      </div>

      <div class="flex items-center space-x-4">
        <div v-if="allPublished" class="flex items-center text-[13px] font-mono bg-[#3B9EFF]/10 border border-[#3B9EFF]/30 px-3 py-1.5 rounded text-[#3B9EFF]">
          <CircleCheckFilled class="w-3 h-3 mr-2" />
          所有产品已下发
        </div>
      </div>
    </div>

    <!-- Product Sections -->
    <div class="space-y-8 pb-8">
      <div
        v-for="product in PRODUCTS"
        :key="product.id"
        class="bg-[#202431] border border-[#2E3348] rounded-xl overflow-hidden shadow-lg flex flex-col"
      >
        <div class="bg-[#2A2D3A] border-b border-[#2E3348] p-4 flex justify-between items-center">
          <h3 class="am-title-l2">
            <div class="am-title-bar"></div>
            {{ product.name }}
          </h3>
          <div v-if="publishedProducts[product.id]" class="flex items-center text-[13px] font-mono bg-[#3B9EFF]/10 border border-[#3B9EFF]/30 px-3 py-1 rounded text-[#3B9EFF]">
                <CircleCheckFilled class="w-3 h-3 mr-1" /> 已下发
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-0">
          <!-- Left: Committee TAA -->
          <div class="lg:col-span-4 border-r border-[#2E3348] p-5 bg-[#1A1E2B] flex flex-col">
            <div class="flex justify-between items-center mb-4">
              <h4 class="am-title-l3">
                <div class="am-title-bar"></div>
                投委会决议 (类别 TAA)
              </h4>
            </div>
            <div class="text-[11px] font-mono bg-[#2A2D3A] text-[#3B9EFF] px-2 py-1.5 rounded border border-[#2E3348] mb-4 inline-block w-fit">
              固收久期指引: {{ product.duration }}
            </div>
            <div class="space-y-3 flex-1">
              <div v-for="asset in product.allocations" :key="asset.id" class="bg-[#161922] p-3 rounded-lg border border-[#2E3348]">
                <div class="flex justify-between items-center mb-1.5">
                  <div class="flex items-center space-x-2">
                    <div class="w-2 h-2 rounded-sm" :style="{ backgroundColor: asset.color }" />
                    <span class="text-[15px] font-bold text-[#E8ECF4]">{{ asset.asset }}</span>
                  </div>
                  <span class="text-base font-mono font-bold text-[#E8ECF4]">{{ asset.weight.toFixed(1) }}%</span>
                </div>
                <div class="flex justify-between items-center text-[11px] text-[#B4BAC9] font-mono">
                  <span>浮动指引: {{ asset.range }}</span>
                </div>
                <div v-if="asset.id === 'equity-total'" class="mt-2 pt-2 border-t border-[#2E3348] space-y-1.5">
                  <div class="text-[11px] text-[#B4BAC9] mb-1">权益内部固定分配:</div>
                  <div v-for="eq in product.eqBreakdown" :key="eq.id" class="flex justify-between items-center text-[13px]">
                    <span class="text-[#B4BAC9]">{{ eq.name }}</span>
                    <span class="font-mono text-[#B4BAC9]">{{ (asset.weight * eq.ratio).toFixed(2) }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Dept TAA Adjustment -->
          <div class="lg:col-span-8 p-5 relative flex flex-col">
            <!-- Published Overlay -->
            <div v-if="publishedProducts[product.id]" class="absolute inset-0 bg-[#161922]/60 backdrop-blur-[2px] z-10 flex items-center justify-center">
              <div class="bg-[#202431] border border-[#3B9EFF]/50 p-6 rounded-xl shadow-[0_0_40px_rgba(59,158,255,0.12)] text-center">
                <CircleCheckFilled class="w-12 h-12 text-[#3B9EFF] mx-auto mb-3" />
                <h3 class="text-lg font-bold text-white mb-2">部门 TAA 已锁定并下发</h3>
                <p class="text-[13px] text-[#B4BAC9] font-mono">投资经理现可基于此策略目标构建意向组合</p>
              </div>
            </div>

            <div class="flex justify-between items-center mb-5">
              <h4 class="am-title-l3">
                <div class="am-title-bar"></div>
                部门级策略目标组合微调
              </h4>
              <div class="flex items-center space-x-4">
                <div :class="cn(
                  'text-[13px] font-mono px-2 py-1 rounded border flex items-center',
                  isTotalValid(product.id) ? 'bg-[#3B9EFF]/10 text-[#3B9EFF] border-[#3B9EFF]/30' : 'bg-[#FF5630]/10 text-[#FF5630] border-[#FF5630]/30'
                )">
                  <WarningFilled v-if="!isTotalValid(product.id)" class="w-3 h-3 mr-1" />
                  总计: {{ getTotalWeight(product.id).toFixed(1) }}%
                </div>
                <button @click="handleReset(product.id)" class="text-[13px] text-[#B4BAC9] hover:text-white underline decoration-[#4A4A4A] underline-offset-2 transition-colors">
                  一键重置
                </button>
              </div>
            </div>

            <div class="space-y-5 flex-1">
              <!-- 固收类 -->
              <div class="space-y-2">
                <h5 class="text-[13px] font-bold text-[#B4BAC9] border-b border-[#2E3348] pb-1.5 flex justify-between">
                  <span>固收类策略 (目标: {{ product.allocations.find(a => a.id === 'fixed-income')?.weight.toFixed(1) }}%)</span>
                  <span class="text-[#3B9EFF] font-mono">{{ ((deptTaas[product.id]['境内固收'] || 0) + (deptTaas[product.id]['境外固收'] || 0)).toFixed(1) }}%</span>
                </h5>
                <StrategySlider
                  v-for="strat in ['境内固收', '境外固收']"
                  :key="strat"
                  :name="strat"
                  :val="deptTaas[product.id][strat] ?? 0"
                  color="#3B9EFF"
                  :disabled="publishedProducts[product.id]"
                  @update:val="v => setTaa(product.id, strat, v)"
                />
              </div>

              <!-- 权益类 -->
              <div class="space-y-2">
                <h5 class="text-[13px] font-bold text-[#B4BAC9] border-b border-[#2E3348] pb-1.5 flex justify-between">
                  <span>权益类策略 (目标: {{ product.allocations.find(a => a.id === 'equity-total')?.weight.toFixed(1) }}%)</span>
                  <span class="text-[#FF5630] font-mono">{{ (deptTaas[product.id]['权益总仓位'] || 0).toFixed(1) }}%</span>
                </h5>
                <StrategySlider
                  name="权益总仓位"
                  :val="deptTaas[product.id]['权益总仓位'] ?? 0"
                  color="#FF5630"
                  :disabled="publishedProducts[product.id]"
                  @update:val="v => setTaa(product.id, '权益总仓位', v)"
                />
                <div class="bg-[#202431] rounded p-2.5 border border-[#2E3348] ml-4">
                  <div class="text-[11px] text-[#B4BAC9] mb-1.5">自动拆解至底层策略 (固定比例):</div>
                  <div class="grid grid-cols-3 gap-4">
                    <div v-for="eq in product.eqBreakdown" :key="eq.id" class="flex flex-col">
                      <span class="text-[11px] text-[#B4BAC9]">{{ eq.name }}</span>
                      <span class="text-[13px] font-mono text-[#E8ECF4]">{{ ((deptTaas[product.id]['权益总仓位'] || 0) * eq.ratio).toFixed(2) }}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 另类 -->
              <div class="space-y-2">
                <h5 class="text-[13px] font-bold text-[#B4BAC9] border-b border-[#2E3348] pb-1.5 flex justify-between">
                  <span>另类策略 (黄金目标: {{ product.allocations.find(a => a.id === 'alt-gold')?.weight.toFixed(1) }}%)</span>
                  <span class="text-[#FFAB00] font-mono">{{ ((deptTaas[product.id]['黄金'] || 0) + (deptTaas[product.id]['REITS'] || 0)).toFixed(1) }}%</span>
                </h5>
                <StrategySlider
                  v-for="strat in ['黄金', 'REITS']"
                  :key="strat"
                  :name="strat"
                  :val="deptTaas[product.id][strat] ?? 0"
                  color="#FFAB00"
                  :disabled="publishedProducts[product.id]"
                  @update:val="v => setTaa(product.id, strat, v)"
                />
              </div>

              <!-- 流动性 -->
              <div class="space-y-2">
                <h5 class="text-[13px] font-bold text-[#B4BAC9] border-b border-[#2E3348] pb-1.5 flex justify-between">
                  <span>流动性资金 (固定: {{ product.allocations.find(a => a.id === 'liquidity')?.weight.toFixed(1) }}%)</span>
                  <span class="text-[#B4BAC9] font-mono">{{ (deptTaas[product.id]['流动性资金'] || 0).toFixed(1) }}%</span>
                </h5>
                <StrategySlider
                  name="流动性资金"
                  :val="deptTaas[product.id]['流动性资金'] ?? 0"
                  color="#8B93A8"
                  :disabled="publishedProducts[product.id]"
                  @update:val="v => setTaa(product.id, '流动性资金', v)"
                />
              </div>
            </div>

            <div class="mt-5 pt-4 border-t border-[#2E3348]">
              <button
                @click="isTotalValid(product.id) && handlePublish(product.id)"
                :disabled="!isTotalValid(product.id) || publishedProducts[product.id]"
                :class="cn(
                  'w-full py-2.5 rounded text-[15px] font-bold transition-all flex items-center justify-center',
                  isTotalValid(product.id) && !publishedProducts[product.id]
                    ? 'bg-[#3B9EFF] hover:bg-[#2E8EF0] text-white shadow-[0_0_15px_rgba(59,158,255,0.2)]'
                    : 'bg-[#2E3348] text-[#B4BAC9] cursor-not-allowed'
                )"
              >
                <Promotion class="w-4 h-4 mr-2" />
                {{ isTotalValid(product.id) ? `确认并下发 ${product.name} 策略` : '请调整权重使总计等于 100%' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import {
  CircleCheckFilled, Promotion, ArrowDown, WarningFilled
} from '@element-plus/icons-vue';
import StrategySlider from './StrategySlider.vue';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

const PRODUCTS = [
  {
    id: 'low-vol', name: '固收+中低波', duration: '3 - 5',
    allocations: [
      { id: 'fixed-income', asset: '固收', weight: 89.8, color: '#3B9EFF', range: '基准' },
      { id: 'equity-total', asset: '权益总仓位', weight: 3.5, color: '#FF5630', range: '±20%' },
      { id: 'alt-gold', asset: '另类-黄金', weight: 0.7, color: '#FFAB00', range: '0%-400%' },
      { id: 'liquidity', asset: '流动性资金', weight: 6.0, color: '#8B93A8', range: '固定' },
    ],
    eqBreakdown: [
      { id: 'eq-div', name: '红利 (50%)', ratio: 0.5 },
      { id: 'eq-hk', name: '港股 (30%)', ratio: 0.3 },
      { id: 'eq-other', name: '其他 (20%)', ratio: 0.2 }
    ],
    defaultDeptTaa: { '境内固收': 85.0, '境外固收': 4.8, '权益总仓位': 3.5, '黄金': 0.7, 'REITS': 0.0, '流动性资金': 6.0 }
  },
  {
    id: 'mid-vol', name: '固收+中波', duration: '2 - 4',
    allocations: [
      { id: 'fixed-income', asset: '固收', weight: 85.0, color: '#3B9EFF', range: '基准' },
      { id: 'equity-total', asset: '权益总仓位', weight: 7.5, color: '#FF5630', range: '±20%' },
      { id: 'alt-gold', asset: '另类-黄金', weight: 1.5, color: '#FFAB00', range: '0%-400%' },
      { id: 'liquidity', asset: '流动性资金', weight: 6.0, color: '#8B93A8', range: '固定' },
    ],
    eqBreakdown: [
      { id: 'eq-div', name: '红利 (50%)', ratio: 0.5 },
      { id: 'eq-hk', name: '港股 (30%)', ratio: 0.3 },
      { id: 'eq-other', name: '其他 (20%)', ratio: 0.2 }
    ],
    defaultDeptTaa: { '境内固收': 80.0, '境外固收': 5.0, '权益总仓位': 7.5, '黄金': 1.5, 'REITS': 0.0, '流动性资金': 6.0 }
  },
  {
    id: 'absolute-return', name: '混合绝对', duration: '1 - 3',
    allocations: [
      { id: 'fixed-income', asset: '固收', weight: 76.0, color: '#3B9EFF', range: '基准' },
      { id: 'equity-total', asset: '权益总仓位', weight: 15.0, color: '#FF5630', range: '±20%' },
      { id: 'alt-gold', asset: '另类-黄金', weight: 3.0, color: '#FFAB00', range: '0%-400%' },
      { id: 'liquidity', asset: '流动性资金', weight: 6.0, color: '#8B93A8', range: '固定' },
    ],
    eqBreakdown: [
      { id: 'eq-div', name: '红利 (50%)', ratio: 0.5 },
      { id: 'eq-hk', name: '港股 (30%)', ratio: 0.3 },
      { id: 'eq-other', name: '其他 (20%)', ratio: 0.2 }
    ],
    defaultDeptTaa: { '境内固收': 70.0, '境外固收': 6.0, '权益总仓位': 15.0, '黄金': 3.0, 'REITS': 0.0, '流动性资金': 6.0 }
  }
];

const department = ref('固收+投资部');

const deptTaas = reactive<Record<string, Record<string, number>>>({
  'low-vol': { ...PRODUCTS[0].defaultDeptTaa },
  'mid-vol': { ...PRODUCTS[1].defaultDeptTaa },
  'absolute-return': { ...PRODUCTS[2].defaultDeptTaa },
});

const publishedProducts = reactive<Record<string, boolean>>({});

const allPublished = computed(() => PRODUCTS.every(p => publishedProducts[p.id]));

function getTotalWeight(productId: string): number {
  return Object.values(deptTaas[productId]).reduce((a, b) => a + (b || 0), 0);
}

function isTotalValid(productId: string): boolean {
  return Math.abs(getTotalWeight(productId) - 100) < 0.1;
}

function setTaa(productId: string, stratId: string, val: number) {
  if (!publishedProducts[productId]) {
    deptTaas[productId][stratId] = val;
  }
}

function handleReset(productId: string) {
  const product = PRODUCTS.find(p => p.id === productId);
  if (product) {
    Object.assign(deptTaas[productId], { ...product.defaultDeptTaa });
  }
}

function handlePublish(productId: string) {
  publishedProducts[productId] = true;
}
</script>
