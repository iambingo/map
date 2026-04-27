<template>
  <div :class="cn('relative', hasMaximized ? 'fixed inset-0 z-40 bg-[#161922]' : 'flex flex-col space-y-2 h-full')">

    <!-- Top Controls: hidden when fullscreen -->
    <template v-if="!hasMaximized">
    <!-- Model-Applied Banner -->
    <Transition
      enter-active-class="transition-all duration-500 ease-out"
      enter-from-class="opacity-0 -translate-y-3"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-3"
    >
      <div v-if="showModelAppliedBanner" class="shrink-0">
        <div class="bg-[#0F2240] border border-[#3B9EFF]/20 rounded px-4 py-2.5 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-7 h-7 rounded bg-[#3B9EFF]/15 border border-[#3B9EFF]/25 flex items-center justify-center shrink-0">
              <CircleCheckFilled class="w-3.5 h-3.5 text-[#3B9EFF]" />
            </div>
            <div>
              <p class="text-[13px] font-semibold text-[#3B9EFF]">模型权重已成功应用至意向组合</p>
              <p class="text-[11px] font-mono text-[#3B9EFF]/50 mt-0.5">
                [&nbsp;<span class="text-[#3B9EFF]/80">{{ appliedModelName }}</span>&nbsp;] 的优化权重已写入下方表格，请核查权重合计后再执行试算
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-2 shrink-0 ml-4">
            <span class="text-[11px] font-mono text-[#3B9EFF]/40 bg-[#3B9EFF]/5 border border-[#3B9EFF]/15 px-2 py-1 rounded">
              AUTO · APPLIED
            </span>
            <button @click="showModelAppliedBanner = false" class="text-[#3B9EFF]/30 hover:text-[#3B9EFF] transition-colors p-1 rounded hover:bg-[#3B9EFF]/10">
              <Close class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Read-Only Management Banner -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="isReadOnly" class="shrink-0 bg-[#1C1600] border border-[#D89614]/25 rounded px-3 py-2 flex items-center space-x-3">
        <WarningFilled class="w-3.5 h-3.5 text-[#D89614]/70 shrink-0" />
        <span class="text-[13px] text-[#D89614]/80 font-mono flex-1">当前为管理层查阅模式，仅可查看投资经理资配情况，无法编辑操作</span>
        <span class="text-[10px] font-mono text-[#D89614]/40 bg-[#D89614]/5 border border-[#D89614]/15 px-2 py-1 rounded">{{ currentRole }} · READ-ONLY</span>
      </div>
    </Transition>

    <!-- Global Group Pack Selector -->
    <div class="bg-[#202431] border border-[#2E3348] rounded p-2 shrink-0 flex items-center justify-between">
      <div class="flex items-center gap-3 min-w-0">
        <h3 class="am-title-l3 shrink-0"><div class="am-title-bar"></div>全局操作域</h3>
        <div class="relative">
          <select
            v-model="selectedGroupPack"
            class="appearance-none bg-[#0F2240] border border-[#3B9EFF]/25 hover:border-[#3B9EFF]/50 rounded px-3 py-1 text-xs font-mono text-[#E8ECF4] outline-none cursor-pointer transition-colors pr-7"
          >
            <optgroup label="系统标准系列" class="bg-[#161922] text-[#94A3B8]">
              <option value="qihang" class="bg-[#161922]">启航系列 (15只)</option>
              <option value="wenjian" class="bg-[#161922]">稳健系列 (42只)</option>
            </optgroup>
            <optgroup label="我的自定义包" class="bg-[#161922] text-[#94A3B8]">
              <option value="core_defense" class="bg-[#161922]">核心防守组合 (5只)</option>
              <option value="high弹性" class="bg-[#161922]">高弹性尝试 (3只)</option>
            </optgroup>
          </select>
          <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none">
            <ArrowDown class="w-3 h-3 text-[#3B9EFF]/60" />
          </div>
        </div>
        <span class="text-[10px] font-mono bg-[#3B9EFF]/10 text-[#3B9EFF] border border-[#3B9EFF]/20 px-2 py-1 rounded shrink-0">
          共 {{ GROUP_PACKS[selectedGroupPack]?.count || 0 }} 只产品
        </span>
        <span class="text-[10px] font-mono text-[#64748B]">|</span>
        <span class="text-[10px] font-mono text-[#94A3B8]">{{ GROUP_PACKS[selectedGroupPack]?.label }}</span>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <button
          @click="showTaskBasket = !showTaskBasket"
          :class="cn('text-[13px] px-2 py-1 rounded transition-colors flex items-center gap-1.5',
            showTaskBasket ? 'bg-[#FFAB00]/15 text-[#FFAB00] border border-[#FFAB00]/25' : 'bg-[#2A2E3D] text-[#B4BAC9] hover:bg-[#2E3348] border border-[#2E3348]')"
        >
          <CopyDocument class="w-3 h-3" /> 任务篮
          <span v-if="taskBasket.length > 0" class="text-[10px] font-mono font-bold bg-[#FFAB00] text-[#161922] px-1.5 py-px rounded-full leading-tight">{{ taskBasket.length }}</span>
        </button>
        <button
          @click="handleSaveAsCustomPack"
          class="text-[10px] font-mono text-[#94A3B8]/60 hover:text-[#3B9EFF] border border-[#2E3348] hover:border-[#3B9EFF]/30 bg-transparent hover:bg-[#3B9EFF]/5 px-2 py-1 rounded transition-colors whitespace-nowrap"
        >
          另存为自定义包
        </button>
        <button
          @click="showComparison = !showComparison"
          :class="cn('text-[13px] px-2 py-1 rounded transition-colors flex items-center', showComparison ? 'bg-[#3B9EFF]/15 text-[#3B9EFF] border border-[#3B9EFF]/25' : 'bg-[#2A2E3D] text-[#B4BAC9] hover:bg-[#2E3348] border border-[#2E3348]')"
        >
          <Histogram class="w-3 h-3 mr-1" /> 对比
        </button>
        <div class="w-px h-4 bg-[#2E3348] mx-0.5"></div>
        <button
          @click="navigateToBatchSimulator"
          class="text-[13px] font-bold bg-gradient-to-r from-[#D89614] to-[#FFAB00] hover:from-[#E5A020] hover:to-[#FFB830] text-[#161410] px-3 py-1.5 rounded flex items-center gap-1.5 transition-all shadow-[0_0_12px_rgba(216,150,20,0.25)]"
        >
          <Setting class="w-3.5 h-3.5" /> 进入调仓沙盘
        </button>
      </div>
    </div>

    <!-- 4-Stage Pipeline -->
    <div class="grid grid-cols-4 gap-2 shrink-0">
      <div
        v-for="(stage, idx) in pipelineStages" :key="stage.id"
        @click="activeTab = (stage.id as any)"
        :class="cn('bg-[#202431] border rounded p-2.5 relative overflow-hidden transition-all duration-150 cursor-pointer select-none',
          activeTab === stage.id
            ? [TAB_COLORS[stage.id].border]
            : 'border-[#2E3348] hover:border-[#3E4660]')"
      >
        <div class="flex justify-between items-start mb-2">
          <div>
            <div class="flex items-center space-x-1.5">
              <component :is="stage.icon" :class="['w-3 h-3 transition-colors duration-150', activeTab === stage.id ? TAB_COLORS[stage.id].text : 'text-[#B4BAC9]']" />
              <span :class="cn('text-[13px] font-semibold transition-colors duration-150', activeTab === stage.id ? TAB_COLORS[stage.id].text : 'text-[#B4BAC9]')">{{ stage.name }}</span>
            </div>
            <div class="text-[11px] text-[#94A3B8] mt-0.5">{{ stage.desc }}</div>
          </div>
          <div class="flex items-center space-x-1.5">
            <button @click.stop="expandedStage = expandedStage === stage.id ? null : stage.id" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors">
              <ArrowDown :class="cn('w-3 h-3 transition-transform', expandedStage === stage.id && 'rotate-180')" />
            </button>
            <div class="text-[11px] font-mono text-[#64748B]">0{{ idx + 1 }}</div>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-1.5">
          <div class="bg-[#161922] p-1.5 rounded border border-[#2E3348]">
            <div class="text-[10px] text-[#94A3B8]">权益</div>
            <div :class="cn('text-[13px] font-mono font-bold transition-colors duration-150', activeTab === stage.id ? TAB_COLORS[stage.id].text : 'text-[#E8ECF4]')">{{ stage.eq }}</div>
          </div>
          <div class="bg-[#161922] p-1.5 rounded border border-[#2E3348]">
            <div class="text-[10px] text-[#94A3B8]">固收</div>
            <div :class="cn('text-[13px] font-mono font-bold transition-colors duration-150', activeTab === stage.id ? TAB_COLORS[stage.id].text : 'text-[#E8ECF4]')">{{ stage.fi }}</div>
          </div>
          <div class="bg-[#161922] p-1.5 rounded border border-[#2E3348]">
            <div class="text-[10px] text-[#94A3B8]">另类</div>
            <div :class="cn('text-[13px] font-mono font-bold transition-colors duration-150', activeTab === stage.id ? TAB_COLORS[stage.id].text : 'text-[#E8ECF4]')">{{ stage.alt }}</div>
          </div>
        </div>

        <div v-if="expandedStage === stage.id" class="mt-2 pt-2 border-t border-[#2E3348] space-y-1.5">
          <div v-for="[macro, strats] in Object.entries(STRATEGIES)" :key="macro" class="space-y-1">
            <div class="text-[11px] text-[#B4BAC9] font-semibold">{{ macro }}</div>
            <div class="grid grid-cols-2 gap-1">
              <div v-for="strat in strats" :key="strat" class="flex justify-between items-center bg-[#161922] px-2 py-1 rounded border border-[#2E3348]">
                <span class="text-[11px] text-[#94A3B8]">{{ strat }}</span>
                <span class="text-[11px] font-mono text-[#E8ECF4]">{{ (macroWeights[stage.id as keyof typeof macroWeights] as any)[strat]?.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
          <div v-if="stage.id === 'intent' || stage.id === 'actual'" class="pt-1">
            <span class="text-[11px] text-[#3B9EFF] flex items-center">
              <InfoFilled class="w-2.5 h-2.5 mr-1" /> 支持展开至底层 SPV / 个券明细
            </span>
          </div>
        </div>

        <ArrowRight v-if="idx < 3" class="w-3 h-3 absolute -right-1.5 top-1/2 -translate-y-1/2 text-[#64748B] opacity-60" />
      </div>
    </div>

    <!-- ═══ 时空控制条: T+N 四维推演 & 通道穿透 ═══ -->
    <div class="shrink-0 bg-[#202431] border border-[#2E3348] rounded p-2.5 flex items-center justify-between gap-4">
      <!-- LEFT: T+N Timeline ButtonGroup -->
      <div class="flex items-center gap-3">
        <h3 class="am-title-l3 shrink-0"><div class="am-title-bar"></div>四维推演</h3>
        <div class="flex border border-[#2E3348] rounded overflow-hidden text-[11px] font-mono font-bold">
          <button
            v-for="t in TIMELINE_OPTIONS" :key="t.value"
            @click="timelineState = t.value"
            :class="cn('px-3 py-1.5 transition-all duration-150 border-r border-[#2E3348] last:border-0 whitespace-nowrap',
              timelineState === t.value
                ? 'bg-[#3B9EFF] text-white'
                : 'bg-[#161922] text-[#64748B] hover:bg-[#1A1E2B] hover:text-[#94A3B8]')"
          >{{ t.label }}</button>
        </div>
        <div class="flex items-center gap-1.5 text-[10px] font-mono">
          <div class="w-1.5 h-1.5 rounded-full shrink-0"
            :class="timelineState === 0 ? 'bg-[#00C9A7]' : timelineState === 1 ? 'bg-[#3B9EFF] animate-pulse' : 'bg-[#FFAB00] animate-pulse'"></div>
          <span class="text-[#94A3B8]">{{ TIMELINE_OPTIONS.find(t => t.value === timelineState)?.desc }}</span>
        </div>
      </div>
      <!-- CENTER: Basket Simulation Toggle -->
      <div class="flex items-center gap-1.5 border border-[#2E3348] rounded px-2 py-1 bg-[#161922]">
        <span class="text-xs font-mono text-[#94A3B8] whitespace-nowrap">应用任务篮试算</span>
        <button
          @click="applyBasketSimulation = !applyBasketSimulation"
          :class="cn('relative w-7 h-3.5 rounded-full transition-colors duration-200 border shrink-0 focus:outline-none',
            applyBasketSimulation ? 'bg-[#3B9EFF] border-[#3B9EFF]' : 'bg-[#252A3A] border-[#2E3348]')"
        >
          <div :class="cn('absolute top-0.5 w-2.5 h-2.5 rounded-full bg-white shadow-sm transition-all duration-200',
            applyBasketSimulation ? 'left-3.5' : 'left-0.5')"></div>
        </button>
      </div>
      <!-- RIGHT: Penetration Mode Toggle -->
      <div class="flex items-center gap-2.5 shrink-0">
        <span class="text-[11px] font-mono text-[#B4BAC9]">合并通道型子组合敞口</span>
        <span class="text-[10px] font-mono bg-[#3B9EFF]/10 text-[#3B9EFF] border border-[#3B9EFF]/20 px-1.5 py-px rounded tracking-wider">穿透</span>
        <button
          @click="isPenetrationMode = !isPenetrationMode"
          :class="cn('relative w-10 h-5 rounded-full transition-colors duration-200 border focus:outline-none',
            isPenetrationMode ? 'bg-[#3B9EFF] border-[#3B9EFF]' : 'bg-[#252A3A] border-[#2E3348]')"
          :title="isPenetrationMode ? '关闭穿透模式 → 结构视角' : '开启穿透模式 → 经济敞口视角'"
        >
          <div :class="cn('absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-all duration-200',
            isPenetrationMode ? 'left-5' : 'left-0.5')"></div>
        </button>
        <span :class="cn('text-[11px] font-mono font-bold w-6 transition-colors', isPenetrationMode ? 'text-[#3B9EFF]' : 'text-[#4A5568]')">
          {{ isPenetrationMode ? 'ON' : 'OFF' }}
        </span>
      </div>
    </div>

    </template>

    <!-- ═══ MAIN CONTENT (TAB + OPTIONAL COMPARISON) ═══ -->
    <div :class="cn('flex flex-1 min-h-0 gap-2 overflow-hidden', hasMaximized && 'p-2')">
      <!-- Fullscreen Exit Bar -->
      <div v-if="hasMaximized" class="fixed top-0 left-0 right-0 z-50 bg-[#202431]/90 backdrop-blur border-b border-[#2E3348] px-4 py-2 flex items-center justify-between">
        <span class="text-[13px] font-mono text-[#94A3B8]">
          {{ maximizedComponent === 'asset-distribution' ? '资产分布图' : maximizedComponent === 'holdings-list' ? '持仓列表' : '偏离度图' }} · 全屏模式
        </span>
        <button @click="exitFullscreen" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1.5 rounded hover:bg-[#2A2D3A] transition-colors flex items-center gap-1.5">
          <ScaleToOriginal class="w-4 h-4" />
          <span class="text-[13px]">退出全屏</span>
        </button>
      </div>

      <!-- Tab Content Panel -->
      <div class="flex-1 min-w-0 flex flex-col overflow-hidden bg-[#202431] border border-[#2E3348] rounded">

        <!-- ── SAA Benchmark View ── -->
        <template v-if="activeTab === 'saa'">
          <div class="px-4 py-2.5 border-b border-[#252A3A] bg-[#202431] shrink-0 flex items-center justify-between">
            <h3 class="am-title-l3">
              <div class="am-title-bar"></div> 基准组合 (SAA) 明细
            </h3>
            <div class="flex items-center gap-2">
              <span class="text-[11px] font-mono text-[#94A3B8] bg-[#161922] border border-[#252A3A] px-2 py-1 rounded">
                第十二期投委会 · 2026-03-20
              </span>
              <button @click="toggleFullscreen('asset-distribution')" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1.5 rounded hover:bg-[#2A2D3A] transition-colors" title="全屏查看">
                <ScaleToOriginal v-if="isFullscreen('asset-distribution')" class="w-[13px] h-[13px]" />
                <FullScreen v-else class="w-[13px] h-[13px]" />
              </button>
            </div>
          </div>

          <!-- ══ SAA 60/40 War Room Layout ══ -->
          <div class="flex flex-1 min-h-0 overflow-hidden">

            <!-- ────── LEFT PANE 60%: SAA Table ────── -->
            <div class="flex flex-col w-[60%] min-w-0 overflow-hidden bg-[#1A1D27] border-r border-[#2E3348]">
              <div class="flex-1 overflow-auto no-scrollbar p-3 space-y-3">
                <div class="readonly-zone border border-[#252A3A] rounded overflow-hidden">
                  <table class="w-full text-left border-collapse table-fixed">
                    <thead class="sticky top-0 bg-[#1A1E2B] z-10">
                      <tr class="text-[11px] text-[#94A3B8] uppercase tracking-widest border-b border-[#252A3A]">
                        <th class="px-3 py-2 font-medium">资产类别</th>
                        <th class="px-3 py-2 font-medium text-right">长期目标</th>
                        <th class="px-3 py-2 font-medium text-right">漂移区间</th>
                        <th class="px-3 py-2 font-medium text-right">当前偏差</th>
                        <th class="px-3 py-2 font-medium">说明</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-[#252A3A]">
                      <tr v-for="row in SAA_BENCHMARK" :key="row.asset" class="hover:bg-[#1E2333] transition-colors text-[13px]">
                        <td class="px-3 py-2 text-[#E8ECF4] font-medium">{{ row.asset }}</td>
                        <td class="px-3 py-2 text-right font-mono font-bold text-[#E8ECF4]">{{ row.target }}</td>
                        <td class="px-3 py-2 text-right font-mono text-[#B4BAC9]">{{ row.range }}</td>
                        <td class="px-3 py-2 text-right font-mono font-bold" :class="row.deviationPos ? 'text-[#F04864]' : 'text-[#00C9A7]'">{{ row.deviation }}</td>
                        <td class="px-3 py-2 text-[#94A3B8] text-[11px]">{{ row.note }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="grid grid-cols-4 gap-2">
                  <div v-for="m in SAA_METRICS" :key="m.label" class="readonly-zone border border-[#252A3A] rounded p-2">
                    <div class="text-[10px] text-[#94A3B8] uppercase tracking-widest mb-1.5">{{ m.label }}</div>
                    <div class="text-base font-bold font-mono" :class="m.color">{{ m.value }}</div>
                    <div class="text-[10px] text-[#64748B] mt-0.5 font-mono">{{ m.sub }}</div>
                  </div>
                </div>
              </div>
            </div><!-- end SAA LEFT PANE -->

            <!-- ────── RIGHT PANE 40%: SAA Context Rail ────── -->
            <div class="flex flex-col w-[40%] min-w-0 overflow-y-auto no-scrollbar bg-[#0B0E14]">

              <!-- Rail Header -->
              <div class="px-3 py-2 border-b border-[#2A2D3A] bg-[#0E1118] shrink-0 flex items-center justify-between">
                <h3 class="am-title-l3"><div class="am-title-bar"></div>决策输入</h3>
                <span class="text-[10px] font-mono text-[#64748B] uppercase tracking-widest">REFERENCE</span>
              </div>

              <!-- ── SAA MODULE A: 投委会年度指引 ── -->
              <div class="px-3 pt-3 pb-3 border-b border-[#2A2D3A]">
                <div class="flex items-center justify-between mb-2.5">
                  <h3 class="am-title-l3">
                    <div class="am-title-bar"></div>投委会年度指引
                  </h3>
                  <button
                    class="flex items-center space-x-0.5 text-[10px] font-mono text-[#94A3B8] border border-[#2A2D3A] hover:bg-[#3B9EFF]/5 hover:border-[#3B9EFF]/40 hover:text-[#3B9EFF] px-1.5 py-px rounded transition-colors group"
                    title="查看年度白皮书全文"
                  >
                    <span>查看研报</span>
                    <span class="leading-tight group-hover:translate-x-px group-hover:-translate-y-px inline-block transition-transform duration-150">↗</span>
                  </button>
                </div>
                <div class="space-y-2.5">
                  <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2.5 py-2 space-y-1.5">
                    <div class="flex items-center space-x-1.5 mb-1">
                      <span class="text-[10px] font-mono font-bold text-[#3B9EFF] bg-[#3B9EFF]/10 border border-[#3B9EFF]/20 px-1.5 py-1 rounded uppercase tracking-wider">2026 白皮书</span>
                      <span class="text-[10px] font-mono text-[#64748B]">第十二期投委会审议通过</span>
                    </div>
                    <div class="text-[11px] text-[#B4BAC9] leading-relaxed space-y-1">
                      <p>核心定调：<span class="text-[#E8ECF4] font-medium">"维持固收资产底仓，严控权益波动"</span></p>
                      <p>权益上限维持 <span class="text-[#FFAB00] font-mono font-bold">20%</span>，固收底仓不低于 <span class="text-[#00C9A7] font-mono font-bold">50%</span></p>
                      <p>另类资产用作分散化工具，上限 <span class="text-[#B4BAC9] font-mono font-bold">10%</span>，含黄金/REITS/CTA</p>
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-1.5">
                    <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2 py-1.5">
                      <div class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-widest mb-1">审议周期</div>
                      <div class="text-xs font-mono font-bold text-[#E8ECF4]">季度调整</div>
                      <div class="text-[10px] font-mono text-[#64748B] mt-0.5">下次: 2026-Q2</div>
                    </div>
                    <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2 py-1.5">
                      <div class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-widest mb-1">漂移容忍</div>
                      <div class="text-xs font-mono font-bold text-[#FFAB00]">±5pp</div>
                      <div class="text-[10px] font-mono text-[#64748B] mt-0.5">触发再平衡阈值</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ── SAA MODULE B: 长期风险预算 ── -->
              <div class="px-3 pt-3 pb-3 border-b border-[#2A2D3A]">
                <div class="flex items-center justify-between mb-2.5">
                  <h3 class="am-title-l3">
                    <div class="am-title-bar"></div>长期风险预算
                  </h3>
                  <button
                    class="flex items-center space-x-0.5 text-[10px] font-mono text-[#94A3B8] border border-[#2A2D3A] hover:bg-[#3B9EFF]/5 hover:border-[#3B9EFF]/40 hover:text-[#3B9EFF] px-1.5 py-px rounded transition-colors group"
                    title="查看风险预算明细"
                  >
                    <span>风险报告</span>
                    <span class="leading-tight group-hover:translate-x-px group-hover:-translate-y-px inline-block transition-transform duration-150">↗</span>
                  </button>
                </div>
                <div class="space-y-2.5">
                  <!-- Drawdown Limit -->
                  <div>
                    <div class="flex justify-between text-[10px] mb-1">
                      <span class="text-[#94A3B8] font-mono">长期回撤限额</span>
                      <span class="font-mono"><span class="text-[#F04864] font-bold">≤ 2.0%</span><span class="text-[#64748B]"> (投委会备案)</span></span>
                    </div>
                    <div class="h-1.5 bg-[#1A1D27] rounded-full overflow-hidden">
                      <div class="h-full bg-[#F04864] rounded-full" style="width:65%"></div>
                    </div>
                    <div class="text-[10px] font-mono text-[#F04864]/60 mt-0.5 text-right">当前 -1.3% · 余量 0.7%</div>
                  </div>
                  <!-- Vol Target -->
                  <div>
                    <div class="flex justify-between text-[10px] mb-1">
                      <span class="text-[#94A3B8] font-mono">年化波动率中枢</span>
                      <span class="font-mono"><span class="text-[#3B9EFF] font-bold">3.2%</span><span class="text-[#64748B]"> 目标</span></span>
                    </div>
                    <div class="h-1.5 bg-[#1A1D27] rounded-full overflow-hidden">
                      <div class="h-full bg-[#3B9EFF] rounded-full" style="width:55%"></div>
                    </div>
                    <div class="text-[10px] font-mono text-[#3B9EFF]/60 mt-0.5 text-right">当前 2.8% · 低于中枢</div>
                  </div>
                  <!-- VaR -->
                  <div>
                    <div class="flex justify-between text-[10px] mb-1">
                      <span class="text-[#94A3B8] font-mono">99% VaR (周度)</span>
                      <span class="font-mono"><span class="text-[#FFAB00] font-bold">-0.8%</span><span class="text-[#64748B]"> / 限额 -1.5%</span></span>
                    </div>
                    <div class="h-1.5 bg-[#1A1D27] rounded-full overflow-hidden">
                      <div class="h-full bg-[#FFAB00] rounded-full" style="width:53%"></div>
                    </div>
                  </div>
                  <!-- Risk card -->
                  <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2.5 py-1.5 space-y-1 mt-1">
                    <div class="flex justify-between text-[10px]">
                      <span class="text-[#94A3B8] font-mono">跟踪误差预算</span>
                      <span class="font-mono text-[#E8ECF4]">≤ 1.0% (vs SAA)</span>
                    </div>
                    <div class="flex justify-between text-[10px]">
                      <span class="text-[#94A3B8] font-mono">Beta 约束</span>
                      <span class="font-mono text-[#B4BAC9]">0.85 ~ 1.15</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ── SAA MODULE C: 历史审议记录 ── -->
              <div class="px-3 pt-3 pb-4">
                <div class="flex items-center mb-2.5">
                  <h3 class="am-title-l3">
                    <div class="am-title-bar"></div>历史审议记录
                  </h3>
                </div>
                <div class="space-y-1.5 mb-3">
                  <div class="flex justify-between text-[11px] bg-[#1A1D27] border border-[#2A2D3A] rounded px-2.5 py-1.5">
                    <span class="text-[#94A3B8] font-mono">第十二期 · 2026-03</span>
                    <span class="font-mono text-[#00C9A7]">通过 ✓</span>
                  </div>
                  <div class="flex justify-between text-[11px] bg-[#1A1D27] border border-[#2A2D3A] rounded px-2.5 py-1.5">
                    <span class="text-[#94A3B8] font-mono">第十一期 · 2025-12</span>
                    <span class="font-mono text-[#00C9A7]">通过 ✓</span>
                  </div>
                  <div class="flex justify-between text-[11px] bg-[#1A1D27] border border-[#2A2D3A] rounded px-2.5 py-1.5">
                    <span class="text-[#94A3B8] font-mono">第十期 · 2025-09</span>
                    <span class="font-mono text-[#FFAB00]">修订权益上限</span>
                  </div>
                </div>
                <button
                  class="w-full flex items-center justify-center space-x-1.5 py-1.5 px-2 bg-[#1A1D27] hover:bg-[#1E2230] border border-[#2A2D3A] hover:border-[#3B9EFF]/30 text-[#B4BAC9] hover:text-[#3B9EFF] text-[11px] font-mono rounded transition-colors group"
                  title="查看投委会历史决议"
                >
                  <Document class="w-3 h-3 shrink-0" />
                  <span>查看投委会历史决议</span>
                  <span class="ml-auto leading-tight group-hover:translate-x-px group-hover:-translate-y-px inline-block transition-transform duration-150">↗</span>
                </button>
              </div>

            </div><!-- end SAA RIGHT PANE -->

          </div><!-- end SAA 60/40 War Room -->
        </template>

        <!-- ── TAA Target Portfolio View ── -->
        <template v-else-if="activeTab === 'taa'">
          <div class="px-4 py-2.5 border-b border-[#252A3A] bg-[#202431] shrink-0 flex items-center justify-between">
            <h3 class="am-title-l3">
              <div class="am-title-bar"></div> 产品目标组合 (TAA)
            </h3>
            <div class="flex items-center space-x-2">
              <span class="text-[11px] font-mono text-[#94A3B8] bg-[#161922] border border-[#252A3A] px-2 py-1 rounded">
                投委会决议 · 2026-03-20 · 第十二期
              </span>
              <button @click="toggleFullscreen('deviation-chart')" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1.5 rounded hover:bg-[#2A2D3A] transition-colors" title="全屏查看">
                <ScaleToOriginal v-if="isFullscreen('deviation-chart')" class="w-[13px] h-[13px]" />
                <FullScreen v-else class="w-[13px] h-[13px]" />
              </button>
            </div>
          </div>
          <div class="text-[11px] text-[#94A3B8] px-4 py-1.5 border-b border-[#252A3A] shrink-0">基于部门 TAA，按策略配置微调</div>

          <!-- ══ TAA 60/40 War Room Layout ══ -->
          <div class="flex flex-1 min-h-0 overflow-hidden">

            <!-- ────── LEFT PANE 60%: TAA Sliders ────── -->
            <div class="flex flex-col w-[60%] min-w-0 overflow-hidden bg-[#1A1D27] border-r border-[#2E3348]">
              <div class="flex-1 overflow-y-auto no-scrollbar p-3 space-y-3">
                <div v-for="[macro, strats] in Object.entries(STRATEGIES)" :key="macro" class="space-y-1.5">
                  <div class="text-[13px] font-semibold text-[#B4BAC9] bg-[#2A2E3D] px-2 py-1 rounded border border-[#2E3348]">{{ macro }}</div>
                  <div v-for="strat in strats" :key="strat" class="operable-zone p-2.5 rounded border border-[#2E3348] ml-2">
                    <div class="flex justify-between items-center mb-1">
                      <span class="text-[13px] font-semibold text-[#E8ECF4]">{{ strat }}</span>
                      <span class="text-[13px] font-mono text-[#B4BAC9]">{{ productTaa[strat].val.toFixed(1) }}%</span>
                    </div>
                    <div class="flex justify-between items-center mb-1.5 text-[11px] text-[#94A3B8]">
                      <span>投委: {{ productTaa[strat].comm.toFixed(1) }}%</span>
                      <span>部门: {{ productTaa[strat].dept.toFixed(1) }}%</span>
                    </div>
                    <!-- Edit mode: range slider + number input (step 0.1%) -->
                    <div v-if="!isReadOnly" class="flex items-center gap-1.5 mt-1 bg-[#1E2330] p-1.5 rounded border border-[#3A4259] hover:border-[#3B9EFF] transition-colors">
                      <button
                        @click.prevent="handleTaaSet(strat, Math.max(0, Math.round((productTaa[strat].val - 0.1) * 10) / 10))"
                        class="w-5 h-5 flex items-center justify-center text-[#94A3B8] hover:text-[#E8ECF4] hover:bg-[#2A2D3A] rounded transition-colors shrink-0"
                      >
                        <Minus class="w-3 h-3" />
                      </button>
                      <div class="flex-1 relative flex items-center min-w-0">
                        <div class="absolute inset-0 pointer-events-none flex items-center z-10 px-[5px]">
                          <div class="relative w-full">
                            <div
                              class="absolute top-1/2 -translate-y-1/2 w-0.5 h-3.5 bg-[#3B9EFF]/75 rounded-full -translate-x-1/2"
                              :style="{ left: `${productTaa[strat].comm}%` }"
                              :title="`投委目标: ${productTaa[strat].comm.toFixed(1)}%`"
                            ></div>
                            <div
                              class="absolute top-1/2 -translate-y-1/2 w-0.5 h-3.5 bg-[#22D3EE]/65 rounded-full -translate-x-1/2"
                              :style="{ left: `${productTaa[strat].dept}%` }"
                              :title="`部门目标: ${productTaa[strat].dept.toFixed(1)}%`"
                            ></div>
                          </div>
                        </div>
                        <input
                          type="range" min="0" max="100" step="0.1"
                          class="am-slider w-full"
                          :value="productTaa[strat].val"
                          @input="(e: Event) => handleTaaSet(strat, Number((e.target as HTMLInputElement).value))"
                          :style="{ background: `linear-gradient(to right, #3B9EFF 0%, #3B9EFF ${productTaa[strat].val}%, #2A2D3A ${productTaa[strat].val}%, #2A2D3A 100%)` }"
                        />
                      </div>
                      <button
                        @click.prevent="handleTaaSet(strat, Math.min(100, Math.round((productTaa[strat].val + 0.1) * 10) / 10))"
                        class="w-5 h-5 flex items-center justify-center text-[#94A3B8] hover:text-[#E8ECF4] hover:bg-[#2A2D3A] rounded transition-colors shrink-0"
                      >
                        <Plus class="w-3 h-3" />
                      </button>
                      <div class="relative flex items-center w-14 border-l border-[#3A4259] pl-1.5 ml-0.5 shrink-0">
                        <input
                          type="number" min="0" max="100" step="0.1"
                          class="w-full bg-transparent text-[#E8ECF4] text-[11px] font-mono text-right outline-none pr-3 [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                          :value="productTaa[strat].val"
                          @change="(e: Event) => { const v = parseFloat((e.target as HTMLInputElement).value); if (!isNaN(v)) handleTaaSet(strat, v); }"
                        />
                        <span class="absolute right-0 text-[#94A3B8] text-[11px]">%</span>
                      </div>
                    </div>
                    <!-- Read-only: static reference bar -->
                    <div v-else class="flex items-center gap-2 mt-1">
                      <div class="flex-1 h-1.5 bg-[#2A2D3A] rounded-full relative overflow-hidden">
                        <div class="absolute top-0 bottom-0 w-0.5 bg-[#3B9EFF]/60 z-10" :style="{ left: `${productTaa[strat].comm}%` }"></div>
                        <div class="h-full bg-[#3E4660] rounded-full" :style="{ width: `${productTaa[strat].val}%` }"></div>
                      </div>
                      <span class="text-[11px] text-[#94A3B8] font-mono shrink-0">{{ productTaa[strat].val.toFixed(1) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div><!-- end TAA LEFT PANE -->

            <!-- ────── RIGHT PANE 40%: TAA Context Rail ────── -->
            <div class="flex flex-col w-[40%] min-w-0 overflow-y-auto no-scrollbar bg-[#0B0E14]">

              <!-- Rail Header -->
              <div class="px-3 py-2 border-b border-[#2A2D3A] bg-[#0E1118] shrink-0 flex items-center justify-between">
                <h3 class="am-title-l3"><div class="am-title-bar"></div>决策输入</h3>
                <span class="text-[10px] font-mono text-[#64748B] uppercase tracking-widest">REFERENCE</span>
              </div>

              <!-- ── TAA MODULE 0: 投委会当期 TAA 决议 (最高优先级) ── -->
              <div class="px-3 pt-3 pb-3 border-b border-[#2A2D3A]">
                <div class="flex items-center justify-between mb-2.5">
                  <h3 class="am-title-l3">
                    <div class="am-title-bar"></div>投委会当期 TAA 决议
                  </h3>
                  <span class="text-[10px] font-mono bg-[#FF9500]/10 text-[#FF9500] border border-[#FF9500]/20 px-1.5 py-1 rounded">决议有效期至: 2026-06-30</span>
                </div>
                <div class="bg-[#1A1D27] border border-[#FF9500]/15 rounded px-2.5 py-2.5 space-y-2">
                  <div class="flex items-center space-x-1.5 mb-1">
                    <span class="text-[10px] font-mono font-bold text-[#FF9500] bg-[#FF9500]/10 border border-[#FF9500]/20 px-1.5 py-1 rounded uppercase tracking-wider">Q2 决议</span>
                    <span class="text-[10px] font-mono text-[#64748B]">投资委员会 · 第 12 次会议</span>
                  </div>
                  <div class="text-[11px] text-[#B4BAC9] leading-relaxed space-y-1.5">
                    <p><span class="text-[#E8ECF4] font-medium">权益资产中性偏乐观</span>（建议敞口 15%-20%）；固收维持<span class="text-[#E8ECF4] font-medium">中等久期</span>，严禁尾部信用下沉。</p>
                    <p>另类资产方面：黄金维持<span class="text-[#FFAB00] font-medium">战术增配</span>，REITs 维持标配；港股敞口暂不加码，等待汇率企稳信号。</p>
                  </div>
                  <div class="pt-1.5 border-t border-[#2A2D3A] flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                      <span class="text-[10px] font-mono text-[#94A3B8]">参与委员</span>
                      <span class="text-[11px] font-mono font-bold text-[#E8ECF4]">7 / 9</span>
                      <span class="text-[10px] font-mono text-[#64748B]">全票通过</span>
                    </div>
                    <div class="flex items-center space-x-1">
                      <span class="text-[10px] font-mono bg-[#3B9EFF]/10 text-[#3B9EFF] border border-[#3B9EFF]/20 px-1.5 py-1 rounded">权益 +5pp</span>
                      <span class="text-[10px] font-mono bg-[#00C9A7]/10 text-[#00C9A7] border border-[#00C9A7]/20 px-1.5 py-1 rounded">久期中性</span>
                      <span class="text-[10px] font-mono bg-[#FF9500]/10 text-[#FF9500] border border-[#FF9500]/20 px-1.5 py-1 rounded">黄金+2pp</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ── TAA MODULE A: 部门月度观点 ── -->
              <div class="px-3 pt-3 pb-3 border-b border-[#2A2D3A]">
                <div class="flex items-center justify-between mb-2.5">
                  <h3 class="am-title-l3">
                    <div class="am-title-bar"></div>部门月度观点
                  </h3>
                  <button
                    class="flex items-center space-x-0.5 text-[10px] font-mono text-[#94A3B8] border border-[#2A2D3A] hover:bg-[#3B9EFF]/5 hover:border-[#3B9EFF]/40 hover:text-[#3B9EFF] px-1.5 py-px rounded transition-colors group"
                    title="查看月度观点全文"
                  >
                    <span>查看研报</span>
                    <span class="leading-tight group-hover:translate-x-px group-hover:-translate-y-px inline-block transition-transform duration-150">↗</span>
                  </button>
                </div>
                <div class="space-y-2.5">
                  <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2.5 py-2 space-y-1.5">
                    <div class="flex items-center space-x-1.5 mb-1">
                      <span class="text-[10px] font-mono font-bold text-[#D89614] bg-[#D89614]/10 border border-[#D89614]/20 px-1.5 py-1 rounded uppercase tracking-wider">2026-04 月会</span>
                      <span class="text-[10px] font-mono text-[#64748B]">投资经理办公会最新结论</span>
                    </div>
                    <div class="text-[11px] text-[#B4BAC9] leading-relaxed space-y-1">
                      <p>固收：<span class="text-[#E8ECF4] font-medium">建议超配短久期信用债，规避长端利率波动</span></p>
                      <p>权益：<span class="text-[#FFAB00] font-medium">红利策略维持标配，港股暂不追高</span></p>
                      <p>另类：<span class="text-[#B4BAC9]">黄金适度增配对冲地缘风险</span></p>
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-1.5">
                    <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2 py-1.5">
                      <div class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-widest mb-1">观点有效期</div>
                      <div class="text-xs font-mono font-bold text-[#E8ECF4]">2026.04</div>
                      <div class="text-[10px] font-mono text-[#64748B] mt-0.5">下月 05 号更新</div>
                    </div>
                    <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2 py-1.5">
                      <div class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-widest mb-1">参与人数</div>
                      <div class="text-xs font-mono font-bold text-[#D89614]">8 / 12</div>
                      <div class="text-[10px] font-mono text-[#64748B] mt-0.5">已提交观点</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ── TAA MODULE B: 战术对冲建议 ── -->
              <div class="px-3 pt-3 pb-3 border-b border-[#2A2D3A]">
                <div class="flex items-center justify-between mb-2.5">
                  <h3 class="am-title-l3">
                    <div class="am-title-bar"></div>战术对冲建议
                  </h3>
                  <button
                    class="flex items-center space-x-0.5 text-[10px] font-mono text-[#94A3B8] border border-[#2A2D3A] hover:bg-[#3B9EFF]/5 hover:border-[#3B9EFF]/40 hover:text-[#3B9EFF] px-1.5 py-px rounded transition-colors group"
                    title="查看对冲策略详情"
                  >
                    <span>对冲明细</span>
                    <span class="leading-tight group-hover:translate-x-px group-hover:-translate-y-px inline-block transition-transform duration-150">↗</span>
                  </button>
                </div>
                <div class="space-y-2.5">
                  <!-- Hedge recommendation -->
                  <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2.5 py-2 space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-[10px] font-mono text-[#94A3B8]">股指期货套保</span>
                      <span class="text-[10px] font-mono font-bold text-[#3B9EFF]">建议维持 5%</span>
                    </div>
                    <div class="h-1.5 bg-[#0B0E14] rounded-full overflow-hidden">
                      <div class="h-full bg-[#3B9EFF] rounded-full" style="width:50%"></div>
                    </div>
                    <div class="text-[10px] font-mono text-[#B4BAC9] leading-relaxed">
                      当前基差水平 (IF2504: <span class="text-[#FFAB00]">-12.3pt</span>) 建议维持套保头寸，展期至远月合约
                    </div>
                  </div>
                  <!-- Rate hedge -->
                  <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2.5 py-2 space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-[10px] font-mono text-[#94A3B8]">利率对冲</span>
                      <span class="text-[10px] font-mono font-bold text-[#00C9A7]">暂不需要</span>
                    </div>
                    <div class="h-1.5 bg-[#0B0E14] rounded-full overflow-hidden">
                      <div class="h-full bg-[#00C9A7] rounded-full" style="width:15%"></div>
                    </div>
                    <div class="text-[10px] font-mono text-[#B4BAC9] leading-relaxed">
                      久期缺口 <span class="text-[#00C9A7]">+0.2yr</span>，在容忍范围内，暂无需国债期货对冲
                    </div>
                  </div>
                  <!-- FX hedge -->
                  <div class="bg-[#1A1D27] border border-[#2A2D3A] rounded px-2.5 py-2 space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-[10px] font-mono text-[#94A3B8]">汇率对冲 (港股)</span>
                      <span class="text-[10px] font-mono font-bold text-[#FFAB00]">建议 50%</span>
                    </div>
                    <div class="h-1.5 bg-[#0B0E14] rounded-full overflow-hidden">
                      <div class="h-full bg-[#FFAB00] rounded-full" style="width:50%"></div>
                    </div>
                    <div class="text-[10px] font-mono text-[#B4BAC9] leading-relaxed">
                      USD/CNH 波动率抬升，港股敞口建议维持 <span class="text-[#FFAB00]">50%</span> 汇率对冲比率
                    </div>
                  </div>
                </div>
              </div>

              <!-- ── TAA MODULE C: 择时信号与触发条件 ── -->
              <div class="px-3 pt-3 pb-4">
                <div class="flex items-center mb-2.5">
                  <h3 class="am-title-l3">
                    <div class="am-title-bar"></div>择时信号与触发条件
                  </h3>
                </div>
                <div class="space-y-2 mb-3">
                  <div class="flex justify-between text-[11px]">
                    <span class="text-[#94A3B8] font-mono">SAA → TAA 偏离度</span>
                    <span class="font-mono text-[#FFAB00]">+4.2pp (需关注)</span>
                  </div>
                  <div class="flex justify-between text-[11px]">
                    <span class="text-[#94A3B8] font-mono">再平衡触发条件</span>
                    <span class="font-mono text-[#B4BAC9]">偏离 ≥ ±5pp</span>
                  </div>
                  <div class="flex justify-between text-[11px]">
                    <span class="text-[#94A3B8] font-mono">上次 TAA 调整</span>
                    <span class="font-mono text-[#E8ECF4]">2026-03-20</span>
                  </div>
                  <div class="pt-1.5 border-t border-[#2A2D3A]">
                    <div class="text-[10px] font-mono text-[#64748B] uppercase tracking-widest mb-1.5">内部研判信号</div>
                    <div class="flex flex-wrap gap-1">
                      <span class="text-[10px] font-mono bg-[#3B9EFF]/10 text-[#3B9EFF] border border-[#3B9EFF]/20 px-1.5 py-1 rounded">短久期优先</span>
                      <span class="text-[10px] font-mono bg-[#FFAB00]/10 text-[#FFAB00] border border-[#FFAB00]/20 px-1.5 py-1 rounded">信用利差收窄</span>
                      <span class="text-[10px] font-mono bg-[#00C9A7]/10 text-[#00C9A7] border border-[#00C9A7]/20 px-1.5 py-1 rounded">黄金多头</span>
                      <span class="text-[10px] font-mono bg-[#FF5630]/10 text-[#FF5630] border border-[#FF5630]/20 px-1.5 py-1 rounded">利率上行风险</span>
                    </div>
                  </div>
                </div>
                <button
                  class="w-full flex items-center justify-center space-x-1.5 py-1.5 px-2 bg-[#1A1D27] hover:bg-[#1E2230] border border-[#2A2D3A] hover:border-[#D89614]/30 text-[#B4BAC9] hover:text-[#D89614] text-[11px] font-mono rounded transition-colors group"
                  title="跳转观点车间查看研报"
                >
                  <span>跳转观点车间查看研报</span>
                  <span class="ml-auto leading-tight group-hover:translate-x-px group-hover:-translate-y-px inline-block transition-transform duration-150">↗</span>
                </button>
              </div>

            </div><!-- end TAA RIGHT PANE -->

          </div><!-- end TAA 60/40 War Room -->
        </template>

        <!-- ── Intent Builder View ── -->
        <template v-else-if="activeTab === 'intent'">
          <div class="px-4 py-2 border-b border-[#252A3A] bg-[#202431] shrink-0 flex items-center justify-between">
            <h3 class="am-title-l3">
              <div class="am-title-bar"></div> 模拟持仓 / 意向预览 (Intent Preview)
            </h3>
            <div class="flex items-center space-x-2">
              <span class="text-xs font-mono text-[#94A3B8] bg-[#161922] border border-[#252A3A] px-2 py-1 rounded">
                只读模式 · 权重合计 {{ totalIntentWeight.toFixed(1) }}%
              </span>
              <button @click="toggleFullscreen('holdings-list')" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1.5 rounded hover:bg-[#2A2D3A] transition-colors" title="全屏查看">
                <ScaleToOriginal v-if="isFullscreen('holdings-list')" class="w-[13px] h-[13px]" />
                <FullScreen v-else class="w-[13px] h-[13px]" />
              </button>
            </div>
          </div>

          <!-- ══ 60/40 War Room Layout ══ -->
          <!-- Read-only Intent Preview -->
          <div class="flex flex-1 min-h-0 overflow-hidden">

            <!-- LEFT: Read-only Intent Position Table (60%) -->
            <div class="flex flex-col w-[60%] min-w-0 overflow-hidden bg-[#1A1D27] border-r border-[#2E3348]">
              <div class="readonly-zone m-3 border border-[#252A3A] rounded overflow-hidden flex-1 flex flex-col">
                <div class="px-3 py-2 border-b border-[#252A3A] bg-[#1A1E2B] flex items-center justify-between shrink-0">
                  <span class="text-[13px] font-semibold text-[#B4BAC9]">意向持仓明细</span>
                  <span class="text-xs font-mono text-[#94A3B8]">{{ intentAssets.length }} 只标的 · 权重合计 {{ totalIntentWeight.toFixed(1) }}%</span>
                </div>
                <div class="flex-1 overflow-auto no-scrollbar">
                  <table class="w-full text-left border-collapse table-fixed">
                    <thead class="sticky top-0 bg-[#1A1E2B] z-10 border-b border-[#2E3348]">
                      <tr class="text-xs text-[#94A3B8] uppercase tracking-widest font-mono">
                        <th class="px-3 py-2 font-medium" style="width:220px">名称</th>
                        <th class="px-3 py-2 font-medium" style="width:120px">代码</th>
                        <th class="px-3 py-2 font-medium" style="width:110px">类型</th>
                        <th class="px-3 py-2 font-medium text-right" style="width:90px">权重</th>
                        <th class="px-3 py-2 font-medium text-right" style="width:125px">市值估算</th>
                        <th class="px-3 py-2 font-medium text-right" style="width:90px">偏离TAA</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-[#252A3A]">
                      <tr v-for="asset in intentAssets" :key="asset.id" class="hover:bg-[#1E2333] transition-colors text-[13px]">
                        <td class="px-3 py-2 text-[#E8ECF4] font-medium">{{ asset.name }}</td>
                        <td class="px-3 py-2 text-[#94A3B8] font-mono text-xs tabular-nums">{{ asset.code }}</td>
                        <td class="px-3 py-2">
                          <span :class="cn('text-xs font-mono px-1.5 py-px rounded border',
                            asset.type === '红利' || asset.type === '港股' ? 'bg-[#F04864]/10 text-[#F04864] border-[#F04864]/20' :
                            asset.type === 'REITS' || asset.type === '黄金' ? 'bg-[#FFAB00]/10 text-[#FFAB00] border-[#FFAB00]/20' :
                            'bg-[#3B9EFF]/10 text-[#3B9EFF] border-[#3B9EFF]/20')">{{ asset.type }}</span>
                        </td>
                        <td class="px-3 py-2 text-right font-mono font-bold text-[#E8ECF4] tabular-nums">{{ asset.weight.toFixed(1) }}%</td>
                        <td class="px-3 py-2 text-right font-mono text-[#B4BAC9] tabular-nums">{{ ((asset.weight / 100) * 26000).toFixed(0) }}万</td>
                        <td class="px-3 py-2 text-right">
                          <span :class="cn('font-mono font-bold tabular-nums',
                            diffFor(asset.type) > 0 ? 'text-[#F04864]' : diffFor(asset.type) < 0 ? 'text-[#00C9A7]' : 'text-[#94A3B8]')">
                            {{ diffFor(asset.type) > 0 ? '+' : '' }}{{ diffFor(asset.type).toFixed(1) }}pp
                          </span>
                        </td>
                      </tr>
                    </tbody>
                    <tfoot class="border-t border-[#2E3348] bg-[#161922]">
                      <tr class="text-[13px] font-mono">
                        <td class="px-3 py-2 text-[#B4BAC9] font-semibold" colspan="3">合计</td>
                        <td class="px-3 py-2 text-right font-bold tabular-nums" :class="Math.abs(totalIntentWeight - 100) > 0.1 ? 'text-[#FFAB00]' : 'text-[#00C9A7]'">{{ totalIntentWeight.toFixed(1) }}%</td>
                        <td class="px-3 py-2 text-right text-[#B4BAC9] tabular-nums">26,000万</td>
                        <td class="px-3 py-2"></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
            </div>

            <!-- RIGHT: Context Rail (40%) -->
            <div class="flex flex-col w-[40%] min-w-0 overflow-y-auto no-scrollbar bg-[#0B0E14]">

              <!-- Rail Header -->
              <div class="px-3 py-2 border-b border-[#2A2D3A] bg-[#0E1118] shrink-0 flex items-center justify-between">
                <h3 class="am-title-l3"><div class="am-title-bar"></div>策略配置概览</h3>
                <span class="text-xs font-mono text-[#64748B] uppercase tracking-widest">SUMMARY</span>
              </div>

              <!-- Strategy Allocation Bars -->
              <div class="px-3 pt-3 pb-3 border-b border-[#2A2D3A]">
                <div class="flex items-center justify-between mb-2.5">
                  <h3 class="am-title-l3"><div class="am-title-bar"></div>意向 vs TAA 偏离</h3>
                </div>
                <div class="space-y-2.5">
                  <div v-for="strat in ALL_STRATEGIES" :key="strat">
                    <div class="flex justify-between items-baseline mb-1">
                      <span class="text-[13px] text-[#B4BAC9]">{{ strat }}</span>
                      <span class="text-[13px] font-mono tabular-nums">
                        <span class="text-[#E8ECF4]">{{ (intentMacroSum[strat] || 0).toFixed(1) }}%</span>
                        <span class="text-[#64748B] mx-1">/</span>
                        <span class="text-[#94A3B8]">{{ productTaa[strat].val.toFixed(1) }}%</span>
                      </span>
                    </div>
                    <div class="h-1.5 bg-[#1A1D27] rounded-full overflow-hidden relative">
                      <div class="h-full bg-[#3B9EFF]/60 rounded-full transition-all" :style="{ width: `${Math.min(intentMacroSum[strat] || 0, 100)}%` }"></div>
                      <div class="absolute top-0 bottom-0 w-0.5 bg-[#FFAB00]/70 z-10" :style="{ left: `${productTaa[strat].val}%` }"></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Trade Diff Summary -->
              <div class="px-3 pt-3 pb-3 border-b border-[#2A2D3A]">
                <div class="flex items-center justify-between mb-2.5">
                  <h3 class="am-title-l3"><div class="am-title-bar"></div>调仓差异摘要</h3>
                </div>
                <div class="grid grid-cols-2 gap-2">
                  <div class="bg-[#1A1D27] border border-[#00C9A7]/15 rounded p-2">
                    <div class="text-xs text-[#94A3B8] mb-1">买入 / 增持</div>
                    <div class="text-[15px] font-bold font-mono tabular-nums text-[#00C9A7]">{{ tradeDiffs.buys.length }} 笔</div>
                  </div>
                  <div class="bg-[#1A1D27] border border-[#F04864]/15 rounded p-2">
                    <div class="text-xs text-[#94A3B8] mb-1">卖出 / 减持</div>
                    <div class="text-[15px] font-bold font-mono tabular-nums text-[#F04864]">{{ tradeDiffs.sells.length }} 笔</div>
                  </div>
                </div>
                <div v-if="tradeDiffs.buys.length > 0 || tradeDiffs.sells.length > 0" class="mt-2 space-y-1">
                  <div v-for="item in [...tradeDiffs.buys, ...tradeDiffs.sells]" :key="item.code"
                    class="flex justify-between items-center text-[13px] bg-[#1A1D27] border border-[#252A3A] rounded px-2.5 py-1.5">
                    <div class="flex items-center gap-2 min-w-0">
                      <span :class="cn('w-1.5 h-1.5 rounded-full shrink-0', item.diff > 0 ? 'bg-[#00C9A7]' : 'bg-[#F04864]')"></span>
                      <span class="text-[#B4BAC9] truncate">{{ item.name }}</span>
                    </div>
                    <span :class="cn('font-mono font-bold tabular-nums shrink-0', item.diff > 0 ? 'text-[#00C9A7]' : 'text-[#F04864]')">
                      {{ item.diff > 0 ? '+' : '' }}{{ item.diff.toFixed(1) }}%
                    </span>
                  </div>
                </div>
              </div>

              <!-- Risk Control Summary -->
              <div class="px-3 pt-3 pb-4">
                <div class="flex items-center mb-2.5">
                  <h3 class="am-title-l3">
                    <div class="w-0.5 h-3.5 bg-[#FF5630] rounded-sm mr-2 shrink-0"></div>风控约束检查
                  </h3>
                </div>
                <div class="space-y-2">
                  <div class="flex justify-between text-[13px]">
                    <span class="text-[#94A3B8]">权益仓位</span>
                    <span class="font-mono"><span class="text-[#FFAB00] font-bold tabular-nums">{{ (intentMacroSum['红利'] || 0 + (intentMacroSum['港股'] || 0)).toFixed(1) }}%</span><span class="text-[#64748B]"> / 20.0% 上限</span></span>
                  </div>
                  <div class="flex justify-between text-[13px]">
                    <span class="text-[#94A3B8]">权重合计</span>
                    <span :class="cn('font-mono font-bold tabular-nums', Math.abs(totalIntentWeight - 100) > 0.1 ? 'text-[#FFAB00]' : 'text-[#00C9A7]')">{{ totalIntentWeight.toFixed(1) }}%</span>
                  </div>
                  <div class="flex justify-between text-[13px]">
                    <span class="text-[#94A3B8]">集中度检查</span>
                    <span class="font-mono text-[#00C9A7] tabular-nums">通过</span>
                  </div>
                </div>
              </div>

            </div>

          </div>
        </template>

        <!-- ── Actual Holdings View ── -->
        <template v-else-if="activeTab === 'actual'">
          <!-- Header -->
          <div class="px-4 py-2.5 border-b border-[#252A3A] bg-[#202431] shrink-0 flex items-center justify-between">
            <h3 class="am-title-l3 flex items-center gap-2">
              <div class="am-title-bar"></div> 实际组合 (Actual Holdings)
              <span v-if="isPenetrationMode" class="text-[10px] font-mono bg-[#3B9EFF]/12 text-[#3B9EFF] border border-[#3B9EFF]/25 px-1.5 py-px rounded">经济敞口穿透</span>
              <span v-else class="text-[10px] font-mono bg-[#252A3A] text-[#64748B] border border-[#2E3348] px-1.5 py-px rounded">结构视角</span>
            </h3>
            <div class="flex items-center space-x-3">
              <span class="text-[11px] font-mono text-[#00C9A7]/60 bg-[#00C9A7]/8 border border-[#00C9A7]/15 px-2 py-1 rounded">● 数据截止: 2026-03-19 收盘</span>
              <span class="text-[11px] font-mono text-[#94A3B8]">总规模: <span class="text-[#E8ECF4] font-semibold">¥2.60亿</span></span>
              <button @click="toggleFullscreen('holdings-list')" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1.5 rounded hover:bg-[#2A2D3A] transition-colors" title="全屏查看">
                <ScaleToOriginal v-if="isFullscreen('holdings-list')" class="w-[13px] h-[13px]" />
                <FullScreen v-else class="w-[13px] h-[13px]" />
              </button>
            </div>
          </div>

          <!-- KPI Cards: 4 列动态指标 -->
          <div class="grid grid-cols-4 gap-2 px-3 py-2.5 border-b border-[#252A3A] shrink-0 bg-[#1A1D27]">

            <!-- KPI 1: 可用头寸 -->
            <div class="bg-[#161922] border border-[#252A3A] rounded-lg p-3 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider">可用头寸</span>
                <span class="text-[10px] font-mono px-1.5 py-px rounded border"
                  :class="timelineState === 0 ? 'text-[#00C9A7] border-[#00C9A7]/25 bg-[#00C9A7]/8' : 'text-[#3B9EFF] border-[#3B9EFF]/25 bg-[#3B9EFF]/8'">
                  T+{{ timelineState }}
                </span>
              </div>
              <div class="text-[15px] font-bold font-mono tabular-nums text-[#00C9A7]">
                ¥{{ kpiAvailableFunds.toLocaleString() }}<span class="text-[13px] text-[#64748B] ml-0.5">万</span>
              </div>
              <div class="text-[10px] font-mono text-[#64748B]">
                {{ timelineState === 0 ? '仅含当日可用现金' : `含 T+${timelineState} 前到账资金` }}
              </div>
            </div>

            <!-- KPI 2: 在途资金 CIT -->
            <div class="bg-[#161922] border rounded-lg p-3 space-y-1.5 transition-colors"
              :class="kpiCIT > 0 ? 'border-[#FFAB00]/30' : 'border-[#252A3A]'">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider">在途资金 (CIT)</span>
                <span v-if="kpiCIT > 0" class="text-[10px] font-mono text-[#FFAB00]/70 animate-pulse">● 结算中</span>
                <span v-else class="text-[10px] font-mono text-[#00C9A7]/60">● 全部到账</span>
              </div>
              <div class="text-[15px] font-bold font-mono tabular-nums transition-colors"
                :class="kpiCIT > 0 ? 'text-[#FFAB00]' : 'text-[#64748B]'">
                ¥{{ kpiCIT.toLocaleString() }}<span class="text-[13px] text-[#64748B] ml-0.5">万</span>
              </div>
              <div class="text-[10px] font-mono text-[#64748B]">已赎回 · 尚未到账</div>
            </div>

            <!-- KPI 3: 穿透后权益/债券占比 -->
            <div class="bg-[#161922] border border-[#252A3A] rounded-lg p-3 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider">权益 / 债券</span>
                <span v-if="isPenetrationMode" class="text-[10px] font-mono text-[#3B9EFF] bg-[#3B9EFF]/8 border border-[#3B9EFF]/20 px-1 py-px rounded">穿透后</span>
                <span v-else class="text-[10px] font-mono text-[#64748B] border border-[#2E3348] px-1 py-px rounded">表层</span>
              </div>
              <div class="text-[15px] font-bold font-mono tabular-nums">
                <span class="text-[#F04864]">{{ kpiEqPct }}%</span>
                <span class="text-[#4A5568] mx-0.5">/</span>
                <span class="text-[#3B9EFF]">{{ kpiBondPct }}%</span>
              </div>
              <div class="h-1.5 bg-[#252A3A] rounded-full overflow-hidden flex">
                <div class="h-full bg-[#F04864] transition-all duration-500" :style="{ width: kpiEqPct + '%' }"></div>
                <div class="h-full bg-[#3B9EFF] transition-all duration-500" :style="{ width: kpiBondPct + '%' }"></div>
                <div class="h-full bg-[#6B7280] transition-all duration-500" :style="{ width: (100 - kpiEqPct - kpiBondPct) + '%' }"></div>
              </div>
            </div>

            <!-- KPI 4: T+N 预测净资产 -->
            <div class="bg-[#161922] border border-[#252A3A] rounded-lg p-3 space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider">T+{{ timelineState }} 预测净资产</span>
                <span class="text-[10px] font-mono text-[#64748B]">预估</span>
              </div>
              <div class="text-[15px] font-bold font-mono tabular-nums text-[#E8ECF4]">
                ¥{{ kpiForecastNAV }}<span class="text-[13px] text-[#64748B] ml-0.5">亿</span>
              </div>
              <div class="text-[10px] font-mono"
                :class="kpiForecastNavChange > 0 ? 'text-[#F04864]' : kpiForecastNavChange < 0 ? 'text-[#00C9A7]' : 'text-[#64748B]'">
                {{ kpiForecastNavChange > 0 ? '+' : '' }}{{ kpiForecastNavChange > 0 ? kpiForecastNavChange + '万 vs T+0' : '与 T+0 持平' }}
              </div>
            </div>

          </div><!-- end KPI cards -->

          <!-- Penetration-aware Position Table -->
          <div class="flex-1 overflow-auto no-scrollbar">
            <table class="w-full text-left border-collapse table-fixed">
              <thead class="sticky top-0 bg-[#1A1E2B] z-10 border-b border-[#2E3348]">
                <tr class="text-[11px] text-[#94A3B8] uppercase tracking-widest font-mono">
                  <th class="px-3 py-2 font-medium" style="width:240px">资产名称</th>
                  <th class="px-3 py-2 font-medium" style="width:120px">代码</th>
                  <th class="px-3 py-2 font-medium" style="width:110px">类型</th>
                  <th class="px-3 py-2 font-medium text-right" style="width:82px">交收日</th>
                  <th class="px-3 py-2 font-medium text-right" style="width:82px">权重</th>
                  <th class="px-3 py-2 font-medium text-right" style="width:125px">持仓市值</th>
                  <th class="px-3 py-2 font-medium text-right" style="width:100px">参考盈亏</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#252A3A]">
                <tr
                  v-for="row in displayedPositions"
                  :key="row.code + (row.is_penetrated ? '_p' : '')"
                  :class="cn('text-[13px] transition-colors',
                    row.is_penetrated
                      ? 'bg-[#0A1929]/50 hover:bg-[#0F2240]/60'
                      : 'hover:bg-[#1E2333]',
                    row.settlement_days > 0 && timelineState < row.settlement_days
                      ? 'opacity-55'
                      : '')"
                >
                  <td class="px-3 py-2">
                    <div class="flex items-center gap-1.5">
                      <!-- Penetrated row indentation connector -->
                      <div v-if="row.is_penetrated" class="w-3 h-3 border-l-2 border-b-2 border-[#3B9EFF]/25 ml-1 mr-0.5 shrink-0 rounded-bl-sm"></div>
                      <span :class="row.is_penetrated ? 'text-[#B4BAC9]' : 'text-[#E8ECF4] font-medium'">{{ row.name }}</span>
                      <!-- Badges -->
                      <span v-if="row.is_penetrated"
                        class="text-[10px] font-mono px-1 py-px rounded bg-[#3B9EFF]/12 text-[#3B9EFF] border border-[#3B9EFF]/25 shrink-0 whitespace-nowrap">
                        通道穿透
                      </span>
                      <span v-else-if="row.asset_type === 'Passive_Channel'"
                        class="text-[10px] font-mono px-1 py-px rounded bg-[#3B9EFF]/8 text-[#3B9EFF]/65 border border-[#3B9EFF]/18 shrink-0">
                        通道
                      </span>
                      <span v-else-if="row.asset_type === 'Active_Outsourced'"
                        class="text-[10px] font-mono px-1 py-px rounded bg-[#FFAB00]/10 text-[#FFAB00]/80 border border-[#FFAB00]/20 shrink-0">
                        委外盲盒
                      </span>
                    </div>
                  </td>
                  <td class="px-3 py-2 text-[#94A3B8] font-mono text-[11px] tabular-nums">{{ row.code }}</td>
                  <td class="px-3 py-2 text-[#B4BAC9] text-[11px]">{{ row.display_type }}</td>
                  <td class="px-3 py-2 text-right font-mono text-[11px]">
                    <span class="px-1.5 py-px rounded"
                      :class="row.settlement_days === 0
                        ? 'text-[#00C9A7] bg-[#00C9A7]/10'
                        : timelineState >= row.settlement_days
                          ? 'text-[#00C9A7]/60'
                          : 'text-[#FFAB00] bg-[#FFAB00]/10'">
                      T+{{ row.settlement_days }}
                    </span>
                  </td>
                  <td class="px-3 py-2 text-right font-mono font-bold text-[#E8ECF4] tabular-nums">{{ row.weight_pct.toFixed(1) }}%</td>
                  <td class="px-3 py-2 text-right font-mono text-[#B4BAC9] tabular-nums">¥{{ row.mktValue_wan.toLocaleString() }}万</td>
                  <td class="px-3 py-2 text-right font-mono font-bold tabular-nums"
                    :class="row.pnlPos ? 'text-[#F04864]' : 'text-[#00C9A7]'">
                    {{ row.pnl }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

      </div><!-- end Tab Content -->

      <!-- ── Comparison Panel (togglable) ── -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-x-4"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-x-0"
        leave-to-class="opacity-0 translate-x-4"
      >
        <div v-if="showComparison" :class="cn('flex flex-col overflow-hidden bg-[#202431] border border-[#2E3348] rounded', hasMaximized ? 'w-full' : 'w-[360px] shrink-0')">
          <div class="flex justify-between items-center px-3 py-2.5 border-b border-[#252A3A] shrink-0">
            <h3 class="am-title-l3">
              <div class="am-title-bar"></div> 多维对比分析
            </h3>
            <div class="flex items-center space-x-2">
              <select v-model="chartType" class="appearance-none operable-zone border border-[#2E3348] text-[#B4BAC9] text-[13px] rounded px-2 py-1 outline-none focus:border-[#3B9EFF]/40">
                <option value="area">面积图</option>
                <option value="line">折线图</option>
                <option value="bar">柱状图</option>
              </select>
              <a href="#" @click.prevent class="text-[13px] text-[#3B9EFF] hover:text-[#5CB3FF] flex items-center transition-colors">
                <Link class="w-3 h-3 mr-1" /> 归因
              </a>
              <button @click="showComparison = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-0.5">
                <Close class="w-3 h-3" />
              </button>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-1.5 mx-3 my-2 shrink-0 operable-zone p-2 rounded border border-[#2E3348]">
            <template v-for="(opt, oi) in COMPARE_OPTIONS" :key="opt.id">
              <button
                @click="toggleCompareItem(opt.id)"
                :disabled="!selectedCompareList.includes(opt.id) && selectedCompareList.length >= 4"
                :class="cn('text-[11px] font-mono px-2 py-1 rounded border transition-all duration-150',
                  selectedCompareList.includes(opt.id)
                    ? `text-white border-transparent`
                    : selectedCompareList.length >= 4
                      ? 'bg-[#1A1D27] text-[#3E4660] border-[#2A2D3A] cursor-not-allowed opacity-40'
                      : 'bg-[#1A1D27] text-[#94A3B8] border-[#2A2D3A] hover:border-[#3E4660] hover:text-[#B4BAC9]')"
                :style="selectedCompareList.includes(opt.id) ? { backgroundColor: COMPARE_PALETTE[selectedCompareList.indexOf(opt.id) % 4], borderColor: COMPARE_PALETTE[selectedCompareList.indexOf(opt.id) % 4] } : {}"
              >{{ opt.label }}</button>
            </template>
            <span class="text-[10px] font-mono text-[#64748B] ml-auto">{{ selectedCompareList.length }}/4</span>
          </div>
          <div class="flex-1 overflow-hidden flex flex-col px-4 pb-4 space-y-4 min-h-0">
            <div class="flex-1 min-h-0">
              <div class="text-[13px] text-[#B4BAC9] mb-2">策略配置偏离度 ({{ selectedCompareList.map(id => compareLabels[id]).join(' vs ') }})</div>
              <VChart :option="deviationChartOption" autoresize class="w-full h-full" />
            </div>
            <div class="flex-1 min-h-0">
              <div class="text-[13px] text-[#B4BAC9] mb-2">模拟净值走势对比</div>
              <VChart :option="performanceChartOption" autoresize class="w-full h-full" />
            </div>
          </div>
        </div>
      </Transition>

      <!-- ── Task Basket Panel (全局任务篮 · 多渠道统一汇聚) ── -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-x-4"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-x-0"
        leave-to-class="opacity-0 translate-x-4"
      >
        <div v-if="showTaskBasket" class="w-[300px] shrink-0 flex flex-col overflow-hidden bg-[#202431] border border-[#2E3348] rounded">

          <!-- Basket Header -->
          <div class="flex justify-between items-center px-3 py-2.5 border-b border-[#252A3A] shrink-0">
            <h3 class="am-title-l3 flex items-center gap-2">
              <div class="am-title-bar"></div> 全局任务篮
              <span v-if="taskBasket.length > 0" class="text-[10px] font-mono font-bold bg-[#FFAB00] text-[#161922] px-1.5 py-px rounded-full leading-tight">{{ taskBasket.length }}</span>
            </h3>
            <button @click="showTaskBasket = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-0.5">
              <Close class="w-3 h-3" />
            </button>
          </div>

          <!-- Basket Items List -->
          <div class="flex-1 overflow-y-auto no-scrollbar">
            <div v-if="taskBasket.length === 0" class="py-10 text-center">
              <div class="text-[#3E4660] font-mono text-2xl mb-2">—</div>
              <p class="text-[13px] text-[#64748B] font-mono">任务篮为空</p>
              <p class="text-[11px] text-[#3E4660] font-mono mt-1">调仓或三板斧操作会自动入篮</p>
            </div>
            <template v-else>
              <div
                v-for="item in resolvedBasket" :key="item.id"
                :class="cn('px-3 py-2.5 border-b border-[#252A3A] transition-colors hover:bg-[#1A1E2B]',
                  item.overridden ? 'opacity-40 line-through' : '',
                  item.conflict ? 'bg-[#FFAB00]/5 border-l-2 border-l-[#FFAB00]/40' : '')"
              >
                <div class="flex items-start justify-between gap-2">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-1.5 mb-1 flex-wrap">
                      <!-- Source badge -->
                      <span :class="cn('text-[10px] font-mono font-bold px-1.5 py-px rounded border',
                        item.source === 'manual' ? 'bg-[#3B9EFF]/15 text-[#3B9EFF] border-[#3B9EFF]/25' :
                        item.source === 'model'  ? 'bg-[#AF52DE]/15 text-[#AF52DE] border-[#AF52DE]/25' :
                        'bg-[#8B93A8]/15 text-[#94A3B8] border-[#8B93A8]/25')">
                        {{ item.source === 'manual' ? '手动' : item.source === 'model' ? '模型' : '批量' }}
                      </span>
                      <span v-if="item.overridden" class="text-[10px] font-mono text-[#FFAB00] bg-[#FFAB00]/10 border border-[#FFAB00]/20 px-1 py-px rounded">已被覆盖</span>
                      <span class="text-[11px] font-mono text-[#64748B] truncate">{{ item.portfolioName }}</span>
                    </div>
                    <div class="text-[13px] font-medium text-[#E8ECF4] truncate">{{ item.securityName }}</div>
                    <div class="text-[11px] font-mono text-[#64748B] tabular-nums">{{ item.securityCode }} · T+{{ item.settlement_days }}</div>
                  </div>
                  <div class="text-right shrink-0 space-y-0.5">
                    <div class="text-[13px] font-bold font-mono tabular-nums"
                      :class="item.direction === 'buy' ? 'text-[#00C9A7]' : 'text-[#F04864]'">
                      {{ item.direction === 'buy' ? '买入 +' : '卖出 -' }}{{ item.amount_wan }}万
                    </div>
                    <div class="text-[10px] font-mono text-[#64748B]">{{ item.weight_delta > 0 ? '+' : '' }}{{ item.weight_delta.toFixed(1) }}pp</div>
                  </div>
                  <button @click="removeFromBasket(item.id)" class="text-[#3E4660] hover:text-[#F04864] transition-colors shrink-0 mt-0.5">
                    <Close class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </template>
          </div>

          <!-- Basket Footer: Capital Required + Compliance Status -->
          <div class="shrink-0 border-t border-[#252A3A] bg-[#1A1D27] px-3 py-3 space-y-2">
            <div class="flex justify-between items-baseline">
              <span class="text-[13px] font-mono text-[#94A3B8]">T+{{ timelineState }} 需动用资金</span>
              <span class="text-[15px] font-bold font-mono tabular-nums"
                :class="basketCapitalRequired > kpiAvailableFunds ? 'text-[#F04864]' : 'text-[#00C9A7]'">
                ¥{{ basketCapitalRequired.toLocaleString() }} <span class="text-[11px] text-[#64748B]">万</span>
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[13px] font-mono text-[#94A3B8]">合规预检状态</span>
              <span :class="cn('text-[10px] font-mono font-bold px-2 py-1 rounded border',
                basketComplianceStatus === 'pass' ? 'text-[#00C9A7] bg-[#00C9A7]/10 border-[#00C9A7]/25' :
                basketComplianceStatus === 'warn' ? 'text-[#FFAB00] bg-[#FFAB00]/10 border-[#FFAB00]/25' :
                'text-[#F04864] bg-[#F04864]/10 border-[#F04864]/25')">
                {{ basketComplianceStatus === 'pass' ? '通过' : basketComplianceStatus === 'warn' ? '需关注' : '阻断' }}
              </span>
            </div>
            <div class="flex gap-2 pt-1">
              <button
                @click="clearBasket"
                class="flex-1 text-[13px] font-mono text-[#94A3B8] border border-[#2E3348] hover:border-[#3E4660] hover:text-[#E8ECF4] py-1.5 rounded transition-colors"
              >
                清空
              </button>
              <button
                :disabled="taskBasket.length === 0 || basketComplianceStatus === 'fail'"
                @click="submitBasket"
                :class="cn('flex-1 text-[13px] font-mono font-bold py-1.5 rounded transition-all disabled:opacity-40 disabled:cursor-not-allowed',
                  basketComplianceStatus === 'fail'
                    ? 'bg-[#F04864]/15 text-[#F04864] border border-[#F04864]/25'
                    : 'bg-gradient-to-r from-[#3B9EFF] to-[#22D3EE] text-white hover:from-[#4DA8FF]')"
              >
                提交执行
              </button>
            </div>
          </div>

        </div>
      </Transition>

    </div><!-- end Main Content -->

    <!-- ═══ DECISION REFERENCE & RISK CONTROL PANEL ═══ -->
    <div v-if="!hasMaximized" class="shrink-0 bg-[#1A1E2B] border border-[#2E3348] rounded overflow-hidden">
      <div class="px-4 py-2.5 border-b border-[#252A3A] bg-[#202431] flex items-center justify-between">
        <h3 class="am-title-l3">
          <div class="am-title-bar"></div> 决策参考与风控预警
        </h3>
        <span class="text-xs font-mono text-[#94A3B8]">
          {{ globalBasketSimulation ? '试算模式 · 数据已更新' : '实时数据' }}
        </span>
      </div>
      <div class="grid grid-cols-4 gap-px bg-[#2E3348]">
        <!-- 当前资配偏离 -->
        <div class="bg-[#1A1E2B] p-3">
          <div class="text-xs text-[#94A3B8] mb-1.5">当前资配偏离</div>
          <div class="text-base font-bold font-mono tabular-nums" :class="parseFloat(decisionMetrics.deviation) > 2 ? 'text-[#FFAB00]' : 'text-[#00C9A7]'">
            {{ decisionMetrics.deviation }}<span class="text-xs text-[#94A3B8] ml-0.5">%</span>
          </div>
          <div class="text-xs text-[#64748B] mt-1">vs TAA 基准</div>
        </div>
        <!-- T+2 流动性头寸缺口 -->
        <div class="bg-[#1A1E2B] p-3">
          <div class="text-xs text-[#94A3B8] mb-1.5">T+2 流动性头寸缺口</div>
          <div class="text-base font-bold font-mono tabular-nums" :class="decisionMetrics.liquidityGap < 0 ? 'text-[#F04864]' : 'text-[#E8ECF4]'">
            {{ decisionMetrics.liquidityGap > 0 ? '+' : '' }}{{ decisionMetrics.liquidityGap.toLocaleString() }}<span class="text-xs text-[#94A3B8] ml-0.5">万</span>
          </div>
          <div class="text-xs text-[#64748B] mt-1">到期资金 vs 在途结算</div>
        </div>
        <!-- 组合久期与 VaR -->
        <div class="bg-[#1A1E2B] p-3">
          <div class="text-xs text-[#94A3B8] mb-1.5">组合久期 / VaR(95%)</div>
          <div class="flex items-baseline gap-2">
            <span class="text-base font-bold font-mono tabular-nums text-[#E8ECF4]">3.2<span class="text-xs text-[#94A3B8]">y</span></span>
            <span class="text-xs text-[#64748B]">/</span>
            <span :class="cn('text-base font-bold font-mono tabular-nums', parseFloat(decisionMetrics.varValue) > 1 ? 'text-[#FFAB00]' : 'text-[#00C9A7]')">
              {{ decisionMetrics.varValue }}<span class="text-xs text-[#94A3B8]">%</span>
            </span>
          </div>
          <div class="text-xs text-[#64748B] mt-1">{{ parseFloat(decisionMetrics.varValue) > 1 ? '接近风控阈值' : '风控正常' }}</div>
        </div>
        <!-- 择时择券信号 -->
        <div class="bg-[#1A1E2B] p-3">
          <div class="text-xs text-[#94A3B8] mb-1.5">择时择券信号</div>
          <div class="text-base font-bold font-mono tabular-nums text-[#3B9EFF]">
            {{ decisionMetrics.timingSignal }}
          </div>
          <div class="text-xs text-[#64748B] mt-1">基于宏观因子模型</div>
        </div>
      </div>
    </div>

    <!-- ═══ GLOBAL FLOATING TASK BASKET ═══ -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-x-4"
      enter-to-class="opacity-100 translate-x-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-x-0"
      leave-to-class="opacity-0 translate-x-4"
    >
      <div v-if="showGlobalBasket && !hasMaximized" class="fixed top-[72px] right-4 bottom-4 w-[320px] z-40 flex flex-col bg-[#1A1E2B] border border-[#2E3348] rounded shadow-2xl">
        <!-- Header -->
        <div class="px-3 py-2.5 border-b border-[#2E3348] bg-[#202431] flex items-center justify-between shrink-0">
          <div class="flex items-center gap-2">
            <div class="am-title-bar"></div>
            <span class="text-[13px] font-bold text-[#E8ECF4]">全局任务篮</span>
            <span v-if="basketSummary.totalCount > 0" class="text-xs font-mono text-[#FFAB00] bg-[#FFAB00]/10 border border-[#FFAB00]/20 px-1.5 py-px rounded">
              {{ basketSummary.totalCount }}
            </span>
          </div>
          <button @click="showGlobalBasket = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-0.5">
            <Close class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Simulation Toggle -->
        <div class="px-3 py-2 border-b border-[#2E3348] bg-[#161922] flex items-center justify-between shrink-0">
          <span class="text-xs text-[#94A3B8]">应用任务篮试算</span>
          <button
            @click="globalBasketSimulation = !globalBasketSimulation"
            :class="cn('relative w-7 h-3.5 rounded-full transition-colors duration-200 border shrink-0',
              globalBasketSimulation ? 'bg-[#3B9EFF] border-[#3B9EFF]' : 'bg-[#252A3A] border-[#2E3348]')"
          >
            <div :class="cn('absolute top-0.5 w-2.5 h-2.5 rounded-full bg-white shadow-sm transition-all duration-200',
              globalBasketSimulation ? 'left-3.5' : 'left-0.5')"></div>
          </button>
        </div>

        <!-- Basket Summary -->
        <div class="px-3 py-2 border-b border-[#252A3A] shrink-0 grid grid-cols-3 gap-2 text-center">
          <div>
            <div class="text-xs text-[#94A3B8]">买入</div>
            <div class="text-[13px] font-bold font-mono tabular-nums text-[#00C9A7]">{{ basketSummary.totalBuy.toLocaleString() }}<span class="text-xs text-[#64748B]">万</span></div>
          </div>
          <div>
            <div class="text-xs text-[#94A3B8]">卖出</div>
            <div class="text-[13px] font-bold font-mono tabular-nums text-[#F04864]">{{ basketSummary.totalSell.toLocaleString() }}<span class="text-xs text-[#64748B]">万</span></div>
          </div>
          <div>
            <div class="text-xs text-[#94A3B8]">净变动</div>
            <div class="text-[13px] font-bold font-mono tabular-nums" :class="basketSummary.netDelta >= 0 ? 'text-[#00C9A7]' : 'text-[#F04864]'">
              {{ basketSummary.netDelta >= 0 ? '+' : '' }}{{ basketSummary.netDelta.toLocaleString() }}<span class="text-xs text-[#64748B]">万</span>
            </div>
          </div>
        </div>

        <!-- Basket List -->
        <div class="flex-1 overflow-y-auto no-scrollbar">
          <div v-if="globalTaskBasket.length === 0" class="flex flex-col items-center justify-center h-full text-[#64748B]">
            <CopyDocument class="w-6 h-6 mb-2 opacity-40" />
            <span class="text-xs">任务篮为空</span>
            <span class="text-xs">通过调仓沙盘或模型中心添加指令</span>
          </div>
          <div v-for="item in globalTaskBasket" :key="item.id"
            class="px-3 py-2 border-b border-[#252A3A] hover:bg-[#202431] transition-colors group"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5 min-w-0">
                <span :class="cn('w-1.5 h-1.5 rounded-full shrink-0', item.type === 'buy' ? 'bg-[#00C9A7]' : 'bg-[#F04864]')"></span>
                <span class="text-[13px] text-[#E8ECF4] truncate">{{ item.assetName }}</span>
              </div>
              <button @click="globalRemoveFromBasket(item.id)" class="text-[#64748B] hover:text-[#F04864] transition-colors opacity-0 group-hover:opacity-100 p-0.5 shrink-0">
                <Close class="w-3 h-3" />
              </button>
            </div>
            <div class="flex items-center justify-between mt-1 text-xs">
              <span class="font-mono text-[#94A3B8] tabular-nums">{{ item.assetCode }}</span>
              <div class="flex items-center gap-2">
                <span :class="cn('font-mono font-bold tabular-nums', item.type === 'buy' ? 'text-[#00C9A7]' : 'text-[#F04864]')">
                  {{ item.type === 'buy' ? '+' : '-' }}{{ item.amount.toLocaleString() }}万
                </span>
                <span :class="cn('px-1 py-px rounded text-xs border',
                  item.source === '模型' ? 'bg-[#3B9EFF]/10 text-[#3B9EFF] border-[#3B9EFF]/20' :
                  item.source === '批量' ? 'bg-[#FFAB00]/10 text-[#FFAB00] border-[#FFAB00]/20' :
                  'bg-[#00C9A7]/10 text-[#00C9A7] border-[#00C9A7]/20')">{{ item.source }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="px-3 py-2.5 border-t border-[#2E3348] bg-[#161922] shrink-0 space-y-2">
          <button
            @click="handleSignOff"
            :disabled="globalTaskBasket.length === 0"
            class="w-full py-2 bg-[#00C9A7]/10 border border-[#00C9A7]/30 rounded text-[#00C9A7] hover:bg-[#00C9A7]/20 hover:border-[#00C9A7]/50 disabled:opacity-40 disabled:cursor-not-allowed text-[13px] font-semibold transition-colors flex items-center justify-center gap-1.5"
          >
            <CircleCheckFilled class="w-3.5 h-3.5" /> 签发至交易系统
          </button>
          <button
            v-if="globalTaskBasket.length > 0"
            @click="globalClearBasket"
            class="w-full py-1.5 bg-transparent border border-[#2E3348] rounded text-[#64748B] hover:text-[#94A3B8] hover:border-[#3E4660] text-xs transition-colors"
          >
            清空任务篮
          </button>
        </div>
      </div>
    </Transition>

    <!-- Global Basket Trigger (when basket has items) -->
    <button
      v-if="!showGlobalBasket && globalTaskBasket.length > 0 && !hasMaximized"
      @click="showGlobalBasket = true"
      class="fixed top-[72px] right-4 z-30 bg-[#FFAB00] text-[#161922] px-3 py-1.5 rounded shadow-lg flex items-center gap-1.5 text-[13px] font-bold hover:bg-[#FFB830] transition-colors"
    >
      <CopyDocument class="w-3 h-3" />
      任务篮 ({{ globalTaskBasket.length }})
    </button>

  <!-- Toast Notification -->
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 translate-y-3 scale-95"
    enter-to-class="opacity-100 translate-y-0 scale-100"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 translate-y-0 scale-100"
    leave-to-class="opacity-0 translate-y-3 scale-95"
  >
    <div
      v-if="toast.show"
      :class="cn('fixed bottom-6 right-6 z-[100] flex items-center space-x-2.5 px-4 py-2.5 rounded border text-[13px] font-medium max-w-[460px]',
        toast.type === 'success'
          ? 'bg-[#0E221A] border-[#00C9A7]/25 text-[#00C9A7]'
          : 'bg-[#220E14] border-[#F04864]/25 text-[#F04864]')"
    >
      <CircleCheckFilled v-if="toast.type === 'success'" class="w-3.5 h-3.5 shrink-0" />
      <span class="leading-relaxed">{{ toast.message }}</span>
    </div>
  </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, watch, onMounted, onUnmounted } from 'vue';
import {
  TrendCharts, Histogram, Operation, VideoPlay, ArrowRight,
  ArrowDown, ArrowUp, Aim, Lightning, DataBoard, Plus, Minus, Delete, Close, Monitor, Odometer,
  Link, InfoFilled, Document, Connection, CopyDocument, Cpu, Files, CircleCheckFilled,
  Grid, Search, Download, FolderAdd, Folder, WarningFilled,
  Coin, Lock, FullScreen, ScaleToOriginal, Setting
} from '@element-plus/icons-vue';
import { sharedIntentState, type PendingModelWeights, type BatchContext } from '../store/intentStore';
import { RULE_MODELS, getRuleModel, executeRuleModel, modelState } from '../store/modelStore';
import { timelineState, isPenetrationMode, maximizedComponent, modelBackPath, setMaximized, clearMaximized, taskBasket as globalTaskBasket, basketSummary, isApplyingBasket as isApplyingGlobalBasket, proFormaData, proFormaSummary, operationScene, addToBasket as globalAddToBasket, removeFromBasket as globalRemoveFromBasket, clearBasket as globalClearBasket } from '../store/demoStore';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

use([CanvasRenderer, BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent]);

function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

type FullscreenPanel = 'asset-distribution' | 'holdings-list' | 'deviation-chart';
function toggleFullscreen(panel: FullscreenPanel) {
  if (maximizedComponent.value === panel) clearMaximized();
  else setMaximized(panel);
}
function isFullscreen(panel: FullscreenPanel) {
  return maximizedComponent.value === panel;
}
function exitFullscreen() {
  clearMaximized();
}
const hasMaximized = computed(() => maximizedComponent.value !== null);

const showGlobalBasket = ref(false);
const globalBasketSimulation = ref(false);

watch(globalBasketSimulation, (v) => {
  isApplyingGlobalBasket.value = v;
});

function handleSignOff() {
  globalClearBasket();
  globalBasketSimulation.value = false;
  showToast(`已签发 ${basketSummary.value.totalCount} 条指令至交易系统，任务篮已清空`, 'success');
  showGlobalBasket.value = false;
}

const decisionMetrics = computed(() => {
  const pfs = proFormaSummary.value;
  const bs = basketSummary.value;
  const deviation = globalBasketSimulation.value ? 2.7 : 1.3;
  const liquidityGap = globalBasketSimulation.value ? -120 : 350;
  const varValue = globalBasketSimulation.value ? 0.82 : 1.15;
  const timingSignal = globalBasketSimulation.value ? '增配利率债' : '持有观望';
  return {
    deviation: deviation.toFixed(1),
    liquidityGap,
    varValue: varValue.toFixed(2),
    timingSignal,
    modifiedCount: pfs.modifiedCount,
    totalMktValue: pfs.totalMktValue,
    basketNetDelta: bs.netDelta,
    basketTotalCount: bs.totalCount,
  };
});

const emit = defineEmits<{ (e: 'navigate', target: string): void }>();

// ── Roles & View Tabs ────────────────────────────────────────────────────────
const ROLES = ['班子', '部门长', '投资经理', '投资助理', '投管'] as const;
type Role = typeof ROLES[number];

const TAB_COLORS: Record<string, { border: string; shadow: string; text: string }> = {
  saa:    { border: 'border-[#3B9EFF]/50',  shadow: '', text: 'text-[#3B9EFF]'  },
  taa:    { border: 'border-[#8B93A8]/40',  shadow: '', text: 'text-[#B4BAC9]'  },
  intent: { border: 'border-[#D89614]/50',  shadow: '', text: 'text-[#D89614]'  },
  actual: { border: 'border-[#00C9A7]/50',  shadow: '', text: 'text-[#00C9A7]'  },
};

const VIEW_TABS = [
  { id: 'saa',    label: '基准组合', badge: 'SAA',    badgeClass: 'text-[#3B9EFF]/70 bg-[#3B9EFF]/10 border-[#3B9EFF]/20', activeColor: 'text-[#3B9EFF]',  icon: Grid },
  { id: 'taa',    label: '目标组合', badge: 'TAA',    badgeClass: 'text-[#B4BAC9]/70 bg-[#8B93A8]/10 border-[#8B93A8]/20', activeColor: 'text-[#B4BAC9]',  icon: Aim },
  { id: 'intent', label: '意向组合', badge: 'INTENT', badgeClass: 'text-[#D89614]/70 bg-[#D89614]/10 border-[#D89614]/20', activeColor: 'text-[#D89614]',  icon: Lightning },
  { id: 'actual', label: '实际组合', badge: 'ACTUAL', badgeClass: 'text-[#00C9A7]/70 bg-[#00C9A7]/10 border-[#00C9A7]/20', activeColor: 'text-[#00C9A7]', icon: DataBoard },
] as const;

// ── SAA Benchmark Data ────────────────────────────────────────────────────────
const SAA_BENCHMARK = [
  { asset: '境内权益 (A股)',   target: '10.0%', range: '5.0% ~ 20.0%', deviation: '+0.5%', deviationPos: true,  note: '含红利/成长策略，长期价值中枢' },
  { asset: '境外权益 (港+美)', target: '5.0%',  range: '0.0% ~ 10.0%', deviation: '+0.2%', deviationPos: true,  note: '分散化配置，汇率对冲不超 50%' },
  { asset: '境内利率债',       target: '60.0%', range: '50.0% ~ 75.0%',deviation: '-3.0%', deviationPos: false, note: '含国债/政金债，压舱石资产' },
  { asset: '境内信用债',       target: '20.0%', range: '10.0% ~ 30.0%',deviation: '+0.8%', deviationPos: true,  note: '评级 AA+ 及以上，信用下沉受限' },
  { asset: '另类资产',         target: '5.0%',  range: '0.0% ~ 10.0%', deviation: '+2.5%', deviationPos: true,  note: 'REITS / 黄金 / CTA，分散风险' },
];
const SAA_METRICS = [
  { label: '长期预期收益率', value: '4.5%',   sub: '年化（含分红）',      color: 'text-[#4D9DE0]' },
  { label: '预期最大回撤',   value: '-1.5%',  sub: '3年历史分位 85%',     color: 'text-[#E5E5E5]' },
  { label: '夏普比率(预测)', value: '1.20',   sub: '基于 10 年历史数据',  color: 'text-[#E5E5E5]' },
  { label: '上次委员会审议', value: '2026-03',sub: '第十二期投委会',       color: 'text-[#4D9DE0]' },
];

// ── Actual Holdings (Enhanced: T+N & Penetration) ─────────────────────────────
interface UnderlyingAsset {
  code: string; name: string; display_type: string;
  asset_class: 'equity' | 'bond' | 'alternative';
  weight_in_spv: number; weight_pct: number;
  mktValue_wan: number; pnl: string; pnlPos: boolean;
}
interface PositionItem {
  code: string; name: string; display_type: string;
  asset_type: 'Direct' | 'Passive_Channel' | 'Active_Outsourced';
  asset_class: 'equity' | 'bond' | 'alternative' | 'cash';
  settlement_days: number;
  weight_pct: number; mktValue_wan: number; pnl: string; pnlPos: boolean;
  underlying?: UnderlyingAsset[];
}

// Keep legacy ACTUAL_HOLDINGS for backward compat (other sections that may ref it)
const ACTUAL_HOLDINGS = [
  { code: '512890.SH', name: '红利低波ETF',       type: '权益-红利',  weight: '10.5%', mktValue: '¥2,730万',  pnl: '+10.1%', pnlPos: true  },
  { code: '513180.SH', name: '恒生科技ETF',       type: '权益-港股',  weight: '5.0%',  mktValue: '¥1,300万',  pnl: '-10.3%', pnlPos: false },
  { code: '019686.SH', name: '22附息国债24',      type: '境内固收',   weight: '42.0%', mktValue: '¥10,920万', pnl: '+1.2%',  pnlPos: true  },
  { code: 'SPV001',    name: 'SPV-信用优选一号',  type: '境内固收',   weight: '34.0%', mktValue: '¥8,840万',  pnl: '+2.8%',  pnlPos: true  },
  { code: '511010.SH', name: '美债ETF',           type: '境外固收',   weight: '5.0%',  mktValue: '¥1,300万',  pnl: '-1.5%',  pnlPos: false },
  { code: '180105.SZ', name: '鹏华深圳能源REIT',  type: '另类-REITS', weight: '2.0%',  mktValue: '¥520万',    pnl: '+3.4%',  pnlPos: true  },
  { code: '518880.SH', name: '黄金ETF',           type: '另类-黄金',  weight: '1.5%',  mktValue: '¥390万',    pnl: '+8.7%',  pnlPos: true  },
];

// Rich position data with settlement rules and SPV underlying
const POSITIONS_DATA: PositionItem[] = [
  { code: '512890.SH', name: '红利低波ETF',      display_type: '权益-红利',  asset_type: 'Direct',          asset_class: 'equity',      settlement_days: 1, weight_pct: 10.5, mktValue_wan: 2730,  pnl: '+10.1%', pnlPos: true  },
  { code: '513180.SH', name: '恒生科技ETF',      display_type: '权益-港股',  asset_type: 'Direct',          asset_class: 'equity',      settlement_days: 1, weight_pct:  5.0, mktValue_wan: 1300,  pnl: '-10.3%', pnlPos: false },
  { code: '019686.SH', name: '22附息国债24',     display_type: '境内固收',   asset_type: 'Direct',          asset_class: 'bond',        settlement_days: 0, weight_pct: 42.0, mktValue_wan: 10920, pnl: '+1.2%',  pnlPos: true  },
  {
    code: 'SPV001', name: 'SPV-信用优选一号', display_type: '通道型 SPV',
    asset_type: 'Passive_Channel', asset_class: 'bond', settlement_days: 2,
    weight_pct: 34.0, mktValue_wan: 8840, pnl: '+2.8%', pnlPos: true,
    // ↓ 底层资产（穿透后可见）— 含少量权益敞口，穿透前被 SPV 壳体遮蔽
    underlying: [
      { code: 'SPV001-01', name: '国开行金融债',  display_type: '境内固收', asset_class: 'bond',      weight_in_spv: 45, weight_pct: 15.3, mktValue_wan: 3978, pnl: '+1.8%', pnlPos: true  },
      { code: 'SPV001-02', name: '信用债 AA+组合', display_type: '境内固收', asset_class: 'bond',      weight_in_spv: 30, weight_pct: 10.2, mktValue_wan: 2652, pnl: '+2.1%', pnlPos: true  },
      { code: 'SPV001-03', name: '可转债组合',    display_type: '转债',     asset_class: 'bond',      weight_in_spv: 15, weight_pct:  5.1, mktValue_wan: 1326, pnl: '+4.5%', pnlPos: true  },
      { code: 'SPV001-04', name: '中证500指增',   display_type: '权益-指数', asset_class: 'equity',   weight_in_spv: 10, weight_pct:  3.4, mktValue_wan:  884, pnl: '-3.2%', pnlPos: false },
    ],
  },
  { code: '511010.SH', name: '美债ETF',          display_type: '境外固收',   asset_type: 'Direct',          asset_class: 'bond',        settlement_days: 1, weight_pct:  5.0, mktValue_wan: 1300,  pnl: '-1.5%',  pnlPos: false },
  { code: '180105.SZ', name: '鹏华深圳能源REIT', display_type: '另类-REITS', asset_type: 'Direct',          asset_class: 'alternative', settlement_days: 1, weight_pct:  2.0, mktValue_wan:  520,  pnl: '+3.4%',  pnlPos: true  },
  { code: '518880.SH', name: '黄金ETF',          display_type: '另类-黄金',  asset_type: 'Direct',          asset_class: 'alternative', settlement_days: 1, weight_pct:  1.5, mktValue_wan:  390,  pnl: '+8.7%',  pnlPos: true  },
];

// ── Cash in Transit: 已发起赎回但尚未到账的资金 ────────────────────────────
const MOCK_CIT = [
  { name: 'SPV-信用优选一号 (部分赎回)',  settlement_days: 2, amount_wan: 800 },
  { name: '恒生科技ETF (调仓减持指令)',   settlement_days: 1, amount_wan: 200 },
];
const BASE_CASH_WAN = 500; // 当前账面现金底仓

// ── T+N 时间轴选项 ──────────────────────────────────────────────────────────
const TIMELINE_OPTIONS = [
  { value: 0 as const, label: 'T+0 今日', desc: '交易日账本 · 实时敞口，指令下达即扣除' },
  { value: 1 as const, label: 'T+1 在途', desc: '交收日账本 · 含 T+1 清算到账资金' },
  { value: 2 as const, label: 'T+2 到账', desc: '交收日账本 · 含 T+2 清算到账资金' },
  { value: 3 as const, label: 'T+3',      desc: '交收日账本 · 所有在途资金完成结算' },
] as const;

// ── KPI Computed: T+N & Penetration ─────────────────────────────────────────

// KPI 1: 可用头寸 — 基础现金 + 当前时间切片前已完成清算的在途资金
const kpiAvailableFunds = computed(() => {
  const settled = MOCK_CIT
    .filter(c => c.settlement_days <= timelineState.value)
    .reduce((s, c) => s + c.amount_wan, 0);
  return BASE_CASH_WAN + settled;
});

// KPI 2: 在途资金 (CIT) — 已发起赎回但尚未到账
const kpiCIT = computed(() => {
  return MOCK_CIT
    .filter(c => c.settlement_days > timelineState.value)
    .reduce((s, c) => s + c.amount_wan, 0);
});

const TOTAL_AUM_WAN = 26000;

// KPI 3: 权益占比 — 穿透后需溶解 SPV 壳体，重新计算底层真实敞口
const kpiEqPct = computed(() => {
  const eqWan = POSITIONS_DATA.reduce((sum, p) => {
    if (isPenetrationMode.value && p.asset_type === 'Passive_Channel' && p.underlying) {
      return sum + p.underlying
        .filter(u => u.asset_class === 'equity')
        .reduce((s, u) => s + u.mktValue_wan, 0);
    }
    return sum + (p.asset_class === 'equity' ? p.mktValue_wan : 0);
  }, 0);
  return +(eqWan / TOTAL_AUM_WAN * 100).toFixed(1);
});

// KPI 3: 债券占比
const kpiBondPct = computed(() => {
  const bondWan = POSITIONS_DATA.reduce((sum, p) => {
    if (isPenetrationMode.value && p.asset_type === 'Passive_Channel' && p.underlying) {
      return sum + p.underlying
        .filter(u => u.asset_class === 'bond')
        .reduce((s, u) => s + u.mktValue_wan, 0);
    }
    return sum + (p.asset_class === 'bond' ? p.mktValue_wan : 0);
  }, 0);
  return +(bondWan / TOTAL_AUM_WAN * 100).toFixed(1);
});

// KPI 4: T+N 预测净资产
const kpiForecastNAV = computed(() => {
  const baseNav = 2.60;
  const increments = [0, 0.01, 0.01, 0.02] as const;
  return (baseNav + increments[timelineState.value]).toFixed(2);
});
const kpiForecastNavChange = computed(() => {
  const increments = [0, 100, 100, 200] as const;
  return increments[timelineState.value];
});

// ── Penetration-aware Position Rows ─────────────────────────────────────────
interface DisplayRow {
  code: string; name: string; display_type: string;
  asset_type: 'Direct' | 'Passive_Channel' | 'Active_Outsourced';
  settlement_days: number;
  weight_pct: number; mktValue_wan: number; pnl: string; pnlPos: boolean;
  is_penetrated: boolean;
}
const displayedPositions = computed((): DisplayRow[] => {
  const rows: DisplayRow[] = [];
  for (const p of POSITIONS_DATA) {
    if (isPenetrationMode.value && p.asset_type === 'Passive_Channel' && p.underlying) {
      // Dissolve SPV shell — expose each underlying asset with [通道穿透] badge
      for (const u of p.underlying) {
        rows.push({
          code: u.code, name: u.name, display_type: u.display_type,
          asset_type: 'Direct', settlement_days: p.settlement_days,
          weight_pct: u.weight_pct, mktValue_wan: u.mktValue_wan,
          pnl: u.pnl, pnlPos: u.pnlPos, is_penetrated: true,
        });
      }
    } else {
      rows.push({
        code: p.code, name: p.name, display_type: p.display_type,
        asset_type: p.asset_type, settlement_days: p.settlement_days,
        weight_pct: p.weight_pct, mktValue_wan: p.mktValue_wan,
        pnl: p.pnl, pnlPos: p.pnlPos, is_penetrated: false,
      });
    }
  }
  return rows;
});
const STRATEGIES: Record<string, string[]> = {
  '权益': ['红利', '港股'],
  '固收': ['境内固收', '境外固收'],
  '另类': ['REITS', '黄金']
};
const ALL_STRATEGIES = Object.values(STRATEGIES).flat();

const timeSeriesData = {
  actual:  [{ t: '09:30', v: 2.1 }, { t: '10:00', v: 2.2 }, { t: '10:30', v: 2.15 }, { t: '11:00', v: 2.3 }, { t: '11:30', v: 2.4 }, { t: '13:00', v: 2.35 }, { t: '14:00', v: 2.5 }, { t: '15:00', v: 2.6 }],
  intent:  [{ t: '09:30', v: 2.05 }, { t: '10:00', v: 2.1 }, { t: '10:30', v: 2.1 }, { t: '11:00', v: 2.2 }, { t: '11:30', v: 2.25 }, { t: '13:00', v: 2.3 }, { t: '14:00', v: 2.4 }, { t: '15:00', v: 2.5 }],
  taa:     [{ t: '09:30', v: 2.0 }, { t: '10:00', v: 2.0 }, { t: '10:30', v: 2.0 }, { t: '11:00', v: 2.0 }, { t: '11:30', v: 2.0 }, { t: '13:00', v: 2.0 }, { t: '14:00', v: 2.0 }, { t: '15:00', v: 2.0 }],
  saa:     [{ t: '09:30', v: 1.8 }, { t: '10:00', v: 1.8 }, { t: '10:30', v: 1.8 }, { t: '11:00', v: 1.8 }, { t: '11:30', v: 1.8 }, { t: '13:00', v: 1.8 }, { t: '14:00', v: 1.8 }, { t: '15:00', v: 1.8 }],
};

const macroWeights = {
  actual: { '红利': 12.0, '港股': 5.2, '境内固收': 75.0, '境外固收': 4.8, 'REITS': 1.5, '黄金': 1.0 },
  intent: { '红利': 12.5, '港股': 5.0, '境内固收': 74.0, '境外固收': 6.0, 'REITS': 1.5, '黄金': 1.0 },
  taa:    { '红利': 15.0, '港股': 5.0, '境内固收': 70.0, '境外固收': 5.0, 'REITS': 2.0, '黄金': 3.0 },
  saa:    { '红利': 10.0, '港股': 5.0, '境内固收': 80.0, '境外固收': 0.0, 'REITS': 2.5, '黄金': 2.5 }
};

const pipelineStages = [
  { id: 'saa',    name: '基准组合 (SAA)',     desc: '长期战略中枢',      eq: '15.0%', fi: '80.0%', alt: '5.0%',  icon: Grid },
  { id: 'taa',    name: '目标组合 (TAA)',     desc: '部门决议 (产品层级)', eq: '20.0%', fi: '75.0%', alt: '5.0%',  icon: Aim },
  { id: 'intent', name: '意向组合 (Intent)',  desc: 'PM微调 (底层资产)',  eq: '17.5%', fi: '80.0%', alt: '2.5%',  icon: Lightning },
  { id: 'actual', name: '实际组合 (Actual)',  desc: '当前真实持仓',       eq: '17.2%', fi: '79.8%', alt: '2.5%',  icon: DataBoard },
];

const compareLabels: Record<string, string> = {
  actual: '实际组合', intent: '意向组合', taa: '目标组合(TAA)', saa: '基准组合(SAA)'
};

const publicModels = [
  { id: 'mf', name: '多因子模型', desc: '基于多因子打分的选股/选债模型' },
  { id: 'rp', name: '风险评价（Risk Parity）模型', desc: '基于风险贡献相等的资产配置' },
  { id: 'mc', name: '蒙特卡洛模拟算法', desc: '基于随机模拟的资产路径预测' },
];

// ── Security Search Database (Mock) ──────────────────────────────────────────
interface SecurityItem {
  id: string; code: string; name: string; category: string;
  meta: string; type: string; price: string;
}
const SECURITY_DB: SecurityItem[] = [
  { id: 'db1',  code: '019686.SH', name: '22附息国债24',     category: '境内固收', price: '100.32', meta: '久期 2.8Y · AAA',      type: '境内固收' },
  { id: 'db2',  code: '019524.SH', name: '23农发债07',       category: '境内固收', price: '100.85', meta: '久期 3.5Y · AAA',      type: '境内固收' },
  { id: 'db3',  code: '019521.SH', name: '23国债04',         category: '境内固收', price: '101.20', meta: '久期 5.1Y · AAA',      type: '境内固收' },
  { id: 'db4',  code: 'SPV002',    name: 'SPV-优质信用二号', category: '境内固收', price: '100.00', meta: '久期 1.8Y · AA+',      type: '境内固收' },
  { id: 'db5',  code: '512890.SH', name: '红利低波ETF',      category: '权益-红利', price: '6.882',  meta: 'PE 9.2x · 股息 4.1%', type: '红利'    },
  { id: 'db6',  code: '600519.SH', name: '贵州茅台',         category: '权益-红利', price: '1688.0', meta: 'PE 28.5x · 白酒龙头', type: '红利'    },
  { id: 'db7',  code: '513180.SH', name: '恒生科技ETF',      category: '权益-港股', price: '1.246',  meta: 'PB 1.8x · 港股科技',  type: '港股'    },
  { id: 'db8',  code: '511010.SH', name: '美债ETF',          category: '境外固收', price: '106.15', meta: '久期 7.2Y · 美国国债', type: '境外固收' },
  { id: 'db9',  code: '180105.SZ', name: '鹏华深圳能源REIT', category: '另类-REITS', price: '2.856', meta: '分红率 5.2%',          type: 'REITS'   },
  { id: 'db10', code: '159628.SZ', name: '华夏中证REITs',    category: '另类-REITS', price: '0.928', meta: '分红率 4.8%',          type: 'REITS'   },
  { id: 'db11', code: '518880.SH', name: '黄金ETF',          category: '另类-黄金', price: '7.432',  meta: '跟踪沪金 · 实物支撑', type: '黄金'    },
  { id: 'db12', code: '159980.SZ', name: '有色金属ETF',      category: '另类-黄金', price: '1.358',  meta: '含铜铝锌镍',           type: '黄金'    },
];
const ASSET_FILTER_TABS = ['全部', '固收', '权益', '港股', '另类'] as const;
type AssetFilterTab = typeof ASSET_FILTER_TABS[number];

// ── Reference Actual Holdings (for Trade Diff calculation) ───────────────────
const REFERENCE_ACTUAL_ASSETS = [
  { code: '512890.SH', name: '红利低波ETF',        weight: 10.5 },
  { code: '513180.SH', name: '恒生科技ETF',        weight: 5.0  },
  { code: '019686.SH', name: '22附息国债24',       weight: 42.5 },
  { code: 'SPV001',    name: 'SPV-信用优选一号',   weight: 34.0 },
  { code: '511010.SH', name: '美债ETF',            weight: 5.0  },
  { code: '180105.SZ', name: '鹏华深圳能源REIT',   weight: 2.0  },
  { code: '518880.SH', name: '黄金ETF',            weight: 1.0  },
];
const AUM_WAN = 26000; // 假设总规模 2.6亿元

// ── Snapshot Interface ────────────────────────────────────────────────────────
interface Snapshot {
  id: string;
  name: string;
  assets: Array<{ id: string; name: string; code: string; type: string; weight: number }>;
}

// ── State ────────────────────────────────────────────────────────────────────
// View / role
const activeTab = ref<'saa' | 'taa' | 'intent' | 'actual'>('intent');
const showComparison = ref(false);
const currentRole = ref<Role>('投资经理');
const isReadOnly = computed(() => (['班子', '部门长'] as Role[]).includes(currentRole.value));

const isGenerating = ref(false);
const isRunningModel = ref(false);
const isSimulating = ref(false);
const showSimulationModal = ref(false);
const showContextPanel = ref(true);
const chartType = ref<'area' | 'line' | 'bar'>('area');
const expandedStage = ref<string | null>(null);
const isModelModalOpen = ref(false);
const selectedModel = ref<string | null>(null);
const COMPARE_PALETTE = ['#4D9DE0', '#D89614', '#00C9A7', '#AF52DE'] as const;
const COMPARE_OPTIONS = [
  { id: 'actual', label: '实际组合' },
  { id: 'intent', label: '意向组合' },
  { id: 'taa',    label: '目标组合(TAA)' },
  { id: 'saa',    label: '基准组合(SAA)' },
] as const;
const selectedCompareList = ref<string[]>(['actual', 'intent']);

function toggleCompareItem(id: string) {
  const idx = selectedCompareList.value.indexOf(id);
  if (idx >= 0) {
    if (selectedCompareList.value.length > 1) selectedCompareList.value.splice(idx, 1);
  } else {
    if (selectedCompareList.value.length < 4) selectedCompareList.value.push(id);
  }
}

// Add Asset Modal state
const showAddAssetModal = ref(false);
const assetSearchQuery = ref('');
const assetFilterTab = ref<AssetFilterTab>('全部');
const searchInputRef = ref<HTMLInputElement | null>(null);

// Excel import state
const isImporting = ref(false);
const isTaaImporting = ref(false);

// Toast state
const toast = reactive({ show: false, message: '', type: 'success' as 'success' | 'error' });

// Snapshot state
const snapshots = ref<Snapshot[]>([]);
const activeSnapshotId = ref<string | null>(null);

// ── Smart Grouping (组合包管家) ──────────────────────────────────────────────
const selectedGroupPack = ref('qihang');
const GROUP_PACKS: Record<string, { label: string; count: number }> = {
  qihang: { label: '启航系列', count: 15 },
  wenjian: { label: '稳健系列', count: 42 },
  core_defense: { label: '核心防守组合', count: 5 },
  'high弹性': { label: '高弹性尝试', count: 3 },
};

function handleSaveAsCustomPack() {
  showToast(`已将当前选定产品保存为自定义包`, 'success');
}

// ── Task Inbox ───────────────────────────────────────────────────────────────
type InboxTab = 'pending' | 'resolved';
const inboxTab = ref<InboxTab>('pending');
const activeTaskId = ref<string | null>('task-2');

interface InboxTask {
  id: string;
  icon: string;
  tag: string;
  tagColor: string;
  title: string;
  time: string;
  priority: string;
  priorityClass: string;
  workspaceDesc: string;
  detail: string;
  gridData: GridRow[];
}

interface GridRowChild {
  name: string;
  code: string;
  current: string;
  target: string;
  diff: string;
  amount: string;
  status: string;
  statusClass: string;
}

interface GridRow {
  name: string;
  current: string;
  target: string;
  diff: string;
  amount: string;
  status: string;
  statusClass: string;
  isGroup: boolean;
  expanded: boolean;
  children?: GridRowChild[];
}

const PENDING_TASKS: InboxTask[] = [
  {
    id: 'task-1',
    icon: '',
    tag: '违规持仓',
    tagColor: 'text-[#FF3B30]',
    title: 'XX地产债降级至BBB-，触发持有上限',
    time: '10:42',
    priority: 'P0 紧急',
    priorityClass: 'text-[#FF3B30] bg-[#FF3B30]/10 border border-[#FF3B30]/20',
    workspaceDesc: '涉及 3 只产品，需减持 2.1 亿',
    detail: 'XX地产债于今日被联合资信从AA-下调至BBB-，已跌破内部持仓评级门槛 AA-，需在 T+1 内完成减持',
    gridData: [
      {
        name: '信用债持仓', current: '4.2%', target: '0.0%', diff: '-4.2%', amount: '2.1亿', status: '待减持', statusClass: 'text-[#FF3B30] bg-[#FF3B30]/10',
        isGroup: true, expanded: true,
        children: [
          { name: 'XX地产债01', code: '123456.SZ', current: '2.8%', target: '0.0%', diff: '-2.8%', amount: '1.4亿', status: '超限', statusClass: 'text-[#FF3B30] bg-[#FF3B30]/10' },
          { name: 'XX地产债02', code: '789012.SH', current: '1.4%', target: '0.0%', diff: '-1.4%', amount: '0.7亿', status: '超限', statusClass: 'text-[#FF3B30] bg-[#FF3B30]/10' },
        ],
      },
      {
        name: '替代方案', current: '—', target: '4.2%', diff: '+4.2%', amount: '2.1亿', status: '待配置', statusClass: 'text-[#FFAB00] bg-[#FFAB00]/10',
        isGroup: true, expanded: false,
        children: [
          { name: '国开2301', code: '230201.IB', current: '—', target: '2.5%', diff: '+2.5%', amount: '1.25亿', status: '建议', statusClass: 'text-[#3B9EFF] bg-[#3B9EFF]/10' },
          { name: '国债2405', code: '240005.IB', current: '—', target: '1.7%', diff: '+1.7%', amount: '0.85亿', status: '建议', statusClass: 'text-[#3B9EFF] bg-[#3B9EFF]/10' },
        ],
      },
    ],
  },
  {
    id: 'task-2',
    icon: '',
    tag: '资金站岗',
    tagColor: 'text-[#FFAB00]',
    title: '50亿存单明日到期，需配置再投资',
    time: '09:15',
    priority: 'P1 重要',
    priorityClass: 'text-[#FFAB00] bg-[#FFAB00]/10 border border-[#FFAB00]/20',
    workspaceDesc: '涉及 12 只产品，需配置 50 亿资金',
    detail: '12 只产品持有的同业存单 (NCD) 明日集中到期，总规模约 50 亿，需尽快安排再投资方案',
    gridData: [
      {
        name: '到期存单 (NCD)', current: '19.2%', target: '0.0%', diff: '-19.2%', amount: '50.0亿', status: '明日到期', statusClass: 'text-[#FFAB00] bg-[#FFAB00]/10',
        isGroup: true, expanded: true,
        children: [
          { name: '24浦发CD158', code: '112404158', current: '5.0%', target: '—', diff: '-5.0%', amount: '13.0亿', status: '到期', statusClass: 'text-[#FFAB00] bg-[#FFAB00]/10' },
          { name: '24兴业CD299', code: '112402299', current: '4.2%', target: '—', diff: '-4.2%', amount: '11.0亿', status: '到期', statusClass: 'text-[#FFAB00] bg-[#FFAB00]/10' },
          { name: '24交行CD088', code: '112408088', current: '3.5%', target: '—', diff: '-3.5%', amount: '9.1亿', status: '到期', statusClass: 'text-[#FFAB00] bg-[#FFAB00]/10' },
          { name: '其他9只存单', code: '—', current: '6.5%', target: '—', diff: '-6.5%', amount: '16.9亿', status: '到期', statusClass: 'text-[#FFAB00] bg-[#FFAB00]/10' },
        ],
      },
      {
        name: '再投资方案', current: '—', target: '19.2%', diff: '+19.2%', amount: '50.0亿', status: '待确认', statusClass: 'text-[#3B9EFF] bg-[#3B9EFF]/10',
        isGroup: true, expanded: false,
        children: [
          { name: '国开2401', code: '240201.IB', current: '—', target: '8.0%', diff: '+8.0%', amount: '20.8亿', status: '建议', statusClass: 'text-[#3B9EFF] bg-[#3B9EFF]/10' },
          { name: '国债2412', code: '240012.IB', current: '—', target: '6.0%', diff: '+6.0%', amount: '15.6亿', status: '建议', statusClass: 'text-[#3B9EFF] bg-[#3B9EFF]/10' },
          { name: '新发存单', code: '—', current: '—', target: '5.2%', diff: '+5.2%', amount: '13.6亿', status: '备选', statusClass: 'text-[#94A3B8] bg-[#94A3B8]/10' },
        ],
      },
    ],
  },
  {
    id: 'task-3',
    icon: '',
    tag: 'TAA偏离',
    tagColor: 'text-[#AF52DE]',
    title: '权益仓位落后目标3%，需增配',
    time: '昨天',
    priority: 'P2 关注',
    priorityClass: 'text-[#AF52DE] bg-[#AF52DE]/10 border border-[#AF52DE]/20',
    workspaceDesc: '涉及 8 只产品，需增配 7.8 亿权益',
    detail: '权益整体仓位 14.5%，TAA目标 17.5%，落后 3pp，建议增配红利低波 + 港股科技',
    gridData: [
      {
        name: '权益类', current: '14.5%', target: '17.5%', diff: '+3.0%', amount: '7.8亿', status: '低配', statusClass: 'text-[#AF52DE] bg-[#AF52DE]/10',
        isGroup: true, expanded: true,
        children: [
          { name: '红利低波ETF', code: '512890.SH', current: '3.2%', target: '5.0%', diff: '+1.8%', amount: '4.7亿', status: '增配', statusClass: 'text-[#AF52DE] bg-[#AF52DE]/10' },
          { name: '港股科技ETF', code: '513180.SH', current: '2.0%', target: '3.5%', diff: '+1.5%', amount: '3.9亿', status: '增配', statusClass: 'text-[#AF52DE] bg-[#AF52DE]/10' },
        ],
      },
      {
        name: '资金来源 (减持)', current: '—', target: '-3.0%', diff: '-3.0%', amount: '7.8亿', status: '待调出', statusClass: 'text-[#00C9A7] bg-[#00C9A7]/10',
        isGroup: true, expanded: false,
        children: [
          { name: '短融减持', code: '—', current: '5.0%', target: '3.5%', diff: '-1.5%', amount: '3.9亿', status: '可调', statusClass: 'text-[#00C9A7] bg-[#00C9A7]/10' },
          { name: '现金释放', code: '—', current: '9.0%', target: '7.5%', diff: '-1.5%', amount: '3.9亿', status: '可调', statusClass: 'text-[#00C9A7] bg-[#00C9A7]/10' },
        ],
      },
    ],
  },
];

const activeTask = computed<InboxTask | undefined>(() =>
  PENDING_TASKS.find(t => t.id === activeTaskId.value)
);

const activeTaskGridData = computed<GridRow[]>(() => {
  if (!activeTask.value) return [];
  return activeTask.value.gridData.map(row => ({ ...row }));
});

function toggleGridRowExpand(index: number) {
  const task = activeTask.value;
  if (!task) return;
  task.gridData[index].expanded = !task.gridData[index].expanded;
}

function handleResolveTask(taskId: string) {
  activeTaskId.value = null;
  showToast(`任务已标记为已解决`, 'success');
}

// ── Intent Model-Driven Adjustment ──────────────────────────────────────────
const intentModelId = ref<string | null>(null);
const intentModelParams = reactive<Record<string, string>>({});
const intentModelPreview = ref<{ name: string; value: string; change: string }[]>([]);
const isIntentModelRunning = ref(false);

const intentSelectedModel = computed(() => {
  if (!intentModelId.value) return null;
  return getRuleModel(intentModelId.value) ?? null;
});

watch(intentModelId, (newId) => {
  intentModelPreview.value = [];
  const model = newId ? getRuleModel(newId) : null;
  if (model) {
    model.params.forEach(p => {
      if (!(p.key in intentModelParams)) {
        intentModelParams[p.key] = String(p.defaultVal);
      }
    });
  }
});

function runIntentModelPreview() {
  if (!intentModelId.value || !intentSelectedModel.value) return;
  isIntentModelRunning.value = true;
  const pack = GROUP_PACKS[selectedGroupPack.value];
  setTimeout(() => {
    const result = executeRuleModel(
      intentModelId.value!,
      Object.fromEntries(
        intentSelectedModel.value!.params.map(p => [p.key, Number(intentModelParams[p.key]) || p.defaultVal])
      ),
      pack?.count ?? 0,
    );
    intentModelPreview.value = result.preview;
    isIntentModelRunning.value = false;
  }, 800);
}

function applyModelToIntent() {
  if (!intentSelectedModel.value || intentModelPreview.value.length === 0) return;
  appliedModelName.value = intentSelectedModel.value.name;
  showModelAppliedBanner.value = true;
  intentModelPreview.value = [];
  showToast(`已应用 [${intentSelectedModel.value.name}] 权重至当前意向组合`, 'success');
}

function navigateToBatchSimulator() {
  const pack = GROUP_PACKS[selectedGroupPack.value];
  const task = activeTask.value;
  sharedIntentState.batchContext = {
    sourcePack: selectedGroupPack.value,
    sourcePackLabel: pack?.label ?? '未知组合',
    productCount: pack?.count ?? 0,
    taskTag: task?.tag ?? '无活跃任务',
    taskIcon: task?.tag ?? '',
    timestamp: Date.now(),
  };
  emit('navigate', 'batch-simulator');
}

// Trade Preview Modal state
const showTradePreviewModal = ref(false);

// Model-applied banner state
const showModelAppliedBanner = ref(false);
const appliedModelName = ref('');

// Anonymous Consensus Feed ticker
const consensusIndex = ref(0);
let _consensusTicker: ReturnType<typeof setInterval> | null = null;
const CONSENSUS_FEED = [
  { id: 0, text: ['本周动向：固收+团队平均净增', '【港股科技】', '敞口', '+1.8%', ''], color: ['text-[#B4BAC9]', 'text-[#4D9DE0] font-bold', 'text-[#B4BAC9]', 'text-[#F04864] font-bold', ''] },
  { id: 1, text: ['您的', '【久期暴露】', '目前为', '2.8 yr', '，全公司同策略', '15% 分位', '（偏激进）'], color: ['text-[#B4BAC9]', 'text-[#F1C40F] font-bold', 'text-[#B4BAC9]', 'text-white font-bold', 'text-[#B4BAC9]', 'text-red-400 font-bold', 'text-[#94A3B8]'] },
  { id: 2, text: ['过去 24h，有', '3 位', '表现优异的投资经理上调了', '红利低波', '权重'], color: ['text-[#B4BAC9]', 'text-[#FF9500] font-bold', 'text-[#B4BAC9]', 'text-[#4D9DE0] font-bold', 'text-[#B4BAC9]'] },
];

// ── Model weight receiver ─────────────────────────────────────────────────────
function applyModelWeights(payload: PendingModelWeights) {
  intentAssets.forEach(asset => {
    if (payload.weights[asset.code] !== undefined) {
      asset.weight = payload.weights[asset.code];
    }
  });
  appliedModelName.value = payload.modelName;
  showModelAppliedBanner.value = true;
  setTimeout(() => { showModelAppliedBanner.value = false; }, 6500);
  sharedIntentState.pendingModelWeights = null;
}

// Pick up weights pushed from ModelCenter before navigation (runs after first render)
onMounted(() => {
  if (sharedIntentState.pendingModelWeights) {
    nextTick(() => applyModelWeights(sharedIntentState.pendingModelWeights!));
  }
  _consensusTicker = setInterval(() => {
    consensusIndex.value = (consensusIndex.value + 1) % CONSENSUS_FEED.length;
  }, 4500);
});

onUnmounted(() => {
  if (_consensusTicker) clearInterval(_consensusTicker);
});

// React to weights pushed while this component is already mounted (e.g. future live-push)
watch(
  () => sharedIntentState.pendingModelWeights,
  (payload) => { if (payload) applyModelWeights(payload); }
);

watch(showAddAssetModal, (val) => {
  if (val) nextTick(() => searchInputRef.value?.focus());
  else { assetSearchQuery.value = ''; assetFilterTab.value = '全部'; }
});

const selectedProducts = ref(['启航9个月持有期1号 (QH001)', '启航1年封闭A (QH002)']);

// ── Intent Strategy Engine ───────────────────────────────────────────────────
const STRATEGY_MODES: Record<string, string> = {
  average:       '总量平均分摊',
  nav:           '按净资产等比',
  concentration: '浓度策略',
  eod:           '尾盘平盘与头寸轧差',
  blacklist:     '黑名单一键置换',
};
const intentStrategyMode = ref<string>('eod');
const showSimResults      = ref(true);
const gridFocusRow        = ref<string | null>('QH001');

const productTaa = reactive<Record<string, { val: number; comm: number; dept: number }>>({
  '红利':   { val: 15.0, comm: 10.0, dept: 15.0 },
  '港股':   { val: 5.0,  comm: 5.0,  dept: 5.0 },
  '境内固收': { val: 70.0, comm: 80.0, dept: 70.0 },
  '境外固收': { val: 5.0,  comm: 0.0,  dept: 5.0 },
  'REITS':   { val: 2.0,  comm: 2.5,  dept: 2.0 },
  '黄金':   { val: 3.0,  comm: 2.5,  dept: 3.0 },
});

const intentAssets = reactive([
  { id: '1', name: '红利低波ETF',        code: '512890.SH', type: '红利',   weight: 12.5 },
  { id: '2', name: '恒生科技ETF',        code: '513180.SH', type: '港股',   weight: 5.0 },
  { id: '3', name: '22附息国债24',       code: '019686.SH', type: '境内固收', weight: 40.0 },
  { id: '4', name: 'SPV-信用优选一号',   code: 'SPV001',    type: '境内固收', weight: 34.0 },
  { id: '5', name: '美债ETF',            code: '511010.SH', type: '境外固收', weight: 6.0 },
  { id: '6', name: '鹏华深圳能源REIT',   code: '180105.SZ', type: 'REITS',  weight: 1.5 },
  { id: '7', name: '黄金ETF',            code: '518880.SH', type: '黄金',   weight: 1.0 },
]);

// ── Computed ─────────────────────────────────────────────────────────────────
const totalIntentWeight = computed(() => intentAssets.reduce((sum, a) => sum + a.weight, 0));

const intentMacroSum = computed(() => {
  const sum: Record<string, number> = {};
  intentAssets.forEach(a => { sum[a.type] = (sum[a.type] || 0) + a.weight; });
  return sum;
});

const filteredSecurities = computed(() => {
  let list = SECURITY_DB;
  if (assetFilterTab.value !== '全部') {
    const tab = assetFilterTab.value;
    list = list.filter(s => s.category.includes(tab) || s.type.includes(tab));
  }
  const q = assetSearchQuery.value.trim().toLowerCase();
  if (q) list = list.filter(s => s.code.toLowerCase().includes(q) || s.name.toLowerCase().includes(q));
  return list;
});

const existingCodes = computed(() => new Set(intentAssets.map(a => a.code)));

const tradeDiffs = computed(() => {
  const actualMap = new Map(REFERENCE_ACTUAL_ASSETS.map(a => [a.code, a]));
  const buys:  Array<{ name: string; code: string; diff: number; amount: string }> = [];
  const sells: Array<{ name: string; code: string; diff: number; amount: string }> = [];
  const allCodes = new Set([
    ...REFERENCE_ACTUAL_ASSETS.map(a => a.code),
    ...intentAssets.map(a => a.code),
  ]);
  allCodes.forEach(code => {
    const actual = actualMap.get(code);
    const intent = intentAssets.find(a => a.code === code);
    const actualW = actual?.weight ?? 0;
    const intentW = intent?.weight ?? 0;
    const diff = Number((intentW - actualW).toFixed(2));
    if (Math.abs(diff) < 0.05) return;
    const name = intent?.name ?? actual?.name ?? code;
    const amountWan = Math.abs((diff / 100) * AUM_WAN);
    const amount = `¥${amountWan >= 1 ? amountWan.toFixed(0) : (amountWan * 100).toFixed(0)}万`;
    if (diff > 0) buys.push({ name, code, diff, amount });
    else sells.push({ name, code, diff, amount });
  });
  return { buys, sells };
});

function diffFor(strat: string) {
  return (intentMacroSum.value[strat] || 0) - productTaa[strat].val;
}

const deviationChartOption = computed(() => {
  const keys = Object.keys(macroWeights.taa);
  const selected = selectedCompareList.value;
  if (selected.length < 2) {
    return {
      backgroundColor: 'transparent',
      title: { text: '请至少选择 2 个组合进行对比', left: 'center', top: 'middle', textStyle: { color: '#64748B', fontSize: 11 } }
    };
  }
  const base = selected[0];
  const series: any[] = [];
  selected.slice(1).forEach((cmp, i) => {
    const devData = keys.map(k => ({
      value: Number(((macroWeights[cmp as keyof typeof macroWeights] as any)[k] - (macroWeights[base as keyof typeof macroWeights] as any)[k]).toFixed(2)),
    }));
    series.push({
      name: compareLabels[cmp], type: 'bar',
      data: devData.map(d => ({ ...d, itemStyle: { color: d.value > 0 ? '#FF5630' : '#36B37E', borderRadius: [2, 2, 0, 0] } })),
      barGap: '10%',
      barMaxWidth: 16,
    });
  });
  return {
    backgroundColor: 'transparent',
    legend: { show: selected.length > 2, top: 0, textStyle: { color: '#94A3B8', fontSize: 9 } },
    grid: { top: selected.length > 2 ? 24 : 10, right: 10, bottom: 30, left: -10, containLabel: true },
    tooltip: { trigger: 'axis', backgroundColor: '#202431', borderColor: '#2E3348', textStyle: { color: '#E8ECF4', fontSize: 10 } },
    xAxis: {
      type: 'category', data: keys,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#555E75', fontSize: 10, rotate: -45 }
    },
    yAxis: {
      type: 'value', axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#555E75', fontSize: 10 },
      splitLine: { lineStyle: { color: '#2E3348', type: 'dashed' } }
    },
    series,
  };
});

const performanceChartOption = computed(() => {
  const selected = selectedCompareList.value;
  if (selected.length === 0) {
    return {
      backgroundColor: 'transparent',
      title: { text: '请选择至少 1 个组合', left: 'center', top: 'middle', textStyle: { color: '#64748B', fontSize: 11 } }
    };
  }
  const isArea = chartType.value === 'area';
  const isBar = chartType.value === 'bar';
  const seriesType = isBar ? 'bar' : 'line';
  const firstSer = timeSeriesData[selected[0] as keyof typeof timeSeriesData];
  const times = firstSer.map(d => d.t);

  const series = selected.map((key, i) => {
    const color = COMPARE_PALETTE[i % 4];
    const ser = timeSeriesData[key as keyof typeof timeSeriesData];
    return {
      name: compareLabels[key], type: seriesType,
      data: ser.map(d => d.v),
      smooth: !isBar, symbol: 'none',
      lineStyle: { color, width: 2 },
      itemStyle: { color },
      ...(isArea ? { areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: color.replace('#', 'rgba(') ? `${color}40` : `${color}40` }, { offset: 1, color: 'transparent' }] } } } : {})
    };
  });

  return {
    backgroundColor: 'transparent',
    legend: { show: selected.length > 1, top: 0, textStyle: { color: '#94A3B8', fontSize: 9 } },
    grid: { top: selected.length > 1 ? 24 : 10, right: 10, bottom: 20, left: -10, containLabel: true },
    tooltip: { trigger: 'axis', backgroundColor: '#202431', borderColor: '#2E3348', textStyle: { color: '#E8ECF4', fontSize: 10 } },
    xAxis: { type: 'category', data: times, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#555E75', fontSize: 10 } },
    yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#555E75', fontSize: 10 }, splitLine: { lineStyle: { color: '#2E3348', type: 'dashed' } } },
    series
  };
});

// ── Methods ──────────────────────────────────────────────────────────────────
function removeProduct(p: string) {
  const idx = selectedProducts.value.indexOf(p);
  if (idx >= 0) selectedProducts.value.splice(idx, 1);
}

function removeAsset(id: string) {
  const idx = intentAssets.findIndex(a => a.id === id);
  if (idx >= 0) intentAssets.splice(idx, 1);
}

function handleTaaAdjust(id: string, delta: number) {
  productTaa[id].val = Math.min(100, Math.max(0, Math.round((productTaa[id].val + delta) * 10) / 10));
}

function handleTaaSet(id: string, val: number) {
  productTaa[id].val = Math.min(100, Math.max(0, Math.round(val * 10) / 10));
}

function handleGenerate() {
  isGenerating.value = true;
  setTimeout(() => { isGenerating.value = false; }, 2000);
}

function handleGeneratePreview() {
  showTradePreviewModal.value = true;
}

function handleSimulate() {
  isSimulating.value = true;
  setTimeout(() => { isSimulating.value = false; showSimulationModal.value = true; }, 1500);
}

function handleConfirmGenerate() {
  showSimulationModal.value = false;
  isGenerating.value = true;
  setTimeout(() => { isGenerating.value = false; }, 2000);
}

function navigateToModelCenter() {
  isRunningModel.value = true;
  sharedIntentState.callerTab = (activeTab.value === 'taa' || activeTab.value === 'intent')
    ? activeTab.value
    : 'intent';
  modelBackPath.value = 'terminal';
  setTimeout(() => {
    sharedIntentState.navigationTarget = 'model-center';
    setTimeout(() => { isRunningModel.value = false; }, 100);
  }, 380);
}

function executeModel() {
  isModelModalOpen.value = false;
  isRunningModel.value = true;
  setTimeout(() => {
    isRunningModel.value = false;
    intentAssets.splice(0, intentAssets.length,
      { id: '1', name: '红利低波ETF',       code: '512890.SH', type: '红利',   weight: 15.0 },
      { id: '2', name: '恒生科技ETF',       code: '513180.SH', type: '港股',   weight: 5.0 },
      { id: '3', name: '22附息国债24',      code: '019686.SH', type: '境内固收', weight: 35.0 },
      { id: '4', name: 'SPV-信用优选一号',  code: 'SPV001',    type: '境内固收', weight: 35.0 },
      { id: '5', name: '美债ETF',           code: '511010.SH', type: '境外固收', weight: 5.0 },
      { id: '6', name: '鹏华深圳能源REIT',  code: '180105.SZ', type: 'REITS',  weight: 2.0 },
      { id: '7', name: '黄金ETF',           code: '518880.SH', type: '黄金',   weight: 3.0 },
    );
  }, 1500);
}

function clampWeight(asset: { weight: number }) {
  if (isNaN(asset.weight) || asset.weight < 0) asset.weight = 0;
  else if (asset.weight > 100) asset.weight = 100;
  asset.weight = Math.round(asset.weight * 10) / 10;
}

function addAssetFromSearch(sec: SecurityItem) {  const newId = String(Date.now());
  intentAssets.push({ id: newId, name: sec.name, code: sec.code, type: sec.type, weight: 0 });
  showAddAssetModal.value = false;
  showToast(`已添加 ${sec.name}（${sec.code}），权重默认 0，请手动调整`, 'success');
}

function handleExcelImport() {
  if (isImporting.value) return;
  isImporting.value = true;
  setTimeout(() => {
    isImporting.value = false;
    const maxId = intentAssets.reduce((max, a) => Math.max(max, Number(a.id) || 0), 0);
    intentAssets.push(
      { id: String(maxId + 1), name: '23农发债07',    code: '019524.SH', type: '境内固收', weight: 0 },
      { id: String(maxId + 2), name: '华夏中证REITs', code: '159628.SZ', type: 'REITS',  weight: 0 },
    );
    showToast('已从 组合持仓_0325.xlsx 导入 2 条资产，权重默认 0，请手动调整', 'success');
  }, 1200);
}

function handleTaaExcelImport() {
  if (isTaaImporting.value) return;
  isTaaImporting.value = true;
  setTimeout(() => {
    isTaaImporting.value = false;
    showToast('已从 TAA目标权重_0325.xlsx 导入目标配置，请核查', 'success');
  }, 1200);
}

function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.message = message;
  toast.type = type;
  toast.show = true;
  setTimeout(() => { toast.show = false; }, 3800);
}

function saveSnapshot() {
  const now = new Date();
  const timeStr = now.toTimeString().slice(0, 8);
  const snap: Snapshot = {
    id: String(Date.now()),
    name: `快照_${timeStr}`,
    assets: intentAssets.map(a => ({ ...a })),
  };
  snapshots.value.push(snap);
  activeSnapshotId.value = snap.id;
  showToast(`已保存「${snap.name}」(${snap.assets.length} 条标的)`, 'success');
}

function restoreSnapshot(id: string | null) {
  activeSnapshotId.value = id;
  if (id === null) return;
  const snap = snapshots.value.find(s => s.id === id);
  if (!snap) return;
  intentAssets.splice(0, intentAssets.length, ...snap.assets.map(a => ({ ...a })));
  showToast(`已恢复「${snap.name}」`, 'success');
}

// ═══════════════════════════════════════════════════════════════
// ── FEATURE: 单组合精细化调仓 + 全局任务篮 ────────────────────
// ═══════════════════════════════════════════════════════════════

// ── Portfolio Navigation Tree Data ──────────────────────────────
const PORTFOLIO_SERIES = [
  {
    name: '启航',
    products: [
      { id: 'QH001', name: '启航稳健1号', aum: '3.2亿', risk: '中低风险' },
      { id: 'QH002', name: '启航稳健2号', aum: '2.8亿', risk: '中低风险' },
      { id: 'QH003', name: '启航进取3号', aum: '1.4亿', risk: '中风险' },
    ],
  },
  {
    name: '稳健',
    products: [
      { id: 'WJ001', name: '稳健固收A', aum: '1.8亿', risk: '低风险' },
      { id: 'WJ002', name: '稳健增利B', aum: '2.1亿', risk: '中低风险' },
    ],
  },
  {
    name: '核心防守',
    products: [
      { id: 'CD001', name: '防守1号', aum: '1.5亿', risk: '低风险' },
    ],
  },
];
const ALL_PORTFOLIO_PRODUCTS = PORTFOLIO_SERIES.flatMap(s => s.products);

// ── Portfolio Navigation State ───────────────────────────────────
const selectedPortfolio = ref<string | null>(null);
const selectedPortfolioInfo = computed(() =>
  selectedPortfolio.value ? ALL_PORTFOLIO_PRODUCTS.find(p => p.id === selectedPortfolio.value) : null
);

// ── Task Basket State ────────────────────────────────────────────
interface BasketItem {
  id: string;
  portfolioId: string;
  portfolioName: string;
  securityCode: string;
  securityName: string;
  direction: 'buy' | 'sell';
  amount_wan: number;
  weight_delta: number;
  source: 'batch' | 'manual' | 'model';
  settlement_days: number;
  timestamp: string;
  overridden?: boolean;  // this item has been superseded by a higher-priority manual instruction
  conflict?: boolean;    // there exists a conflicting instruction for same portfolio+security
}
const taskBasket = ref<BasketItem[]>([]);
const showTaskBasket = ref(false);
const applyBasketSimulation = ref(false);

// ── Conflict resolution: 手动 > 批量 prioritization ─────────────
const resolvedBasket = computed((): BasketItem[] => {
  const result: BasketItem[] = [];
  for (const item of taskBasket.value) {
    const conflict = taskBasket.value.find(
      other => other.id !== item.id
        && other.portfolioId === item.portfolioId
        && other.securityCode === item.securityCode
        && other.source !== item.source
    );
    const isOverridden = conflict
      && item.source !== 'manual'
      && conflict.source === 'manual';
    result.push({ ...item, conflict: !!conflict, overridden: !!isOverridden });
  }
  return result;
});

// ── Basket KPIs ────────────────────────────────────────────────
const basketCapitalRequired = computed(() =>
  resolvedBasket.value
    .filter(i => !i.overridden && i.direction === 'buy')
    .reduce((s, i) => s + i.amount_wan, 0)
);
const basketComplianceStatus = computed((): 'pass' | 'warn' | 'fail' => {
  if (basketCapitalRequired.value === 0) return 'pass';
  if (basketCapitalRequired.value > kpiAvailableFunds.value) return 'fail';
  if (basketCapitalRequired.value > kpiAvailableFunds.value * 0.8) return 'warn';
  return 'pass';
});

const portfolioBasketCount = computed(() =>
  taskBasket.value.filter(i => i.portfolioId === selectedPortfolio.value).length
);

function addToBasket(item: Omit<BasketItem, 'id' | 'timestamp'>) {
  taskBasket.value.push({
    ...item,
    id: String(Date.now() + Math.random()),
    timestamp: new Date().toLocaleTimeString('zh-CN', { hour12: false }),
  });
  showTaskBasket.value = true;
}

function removeFromBasket(id: string) {
  const idx = taskBasket.value.findIndex(i => i.id === id);
  if (idx >= 0) taskBasket.value.splice(idx, 1);
}

function clearBasket() {
  taskBasket.value = [];
}

function submitBasket() {
  const count = resolvedBasket.value.filter(i => !i.overridden).length;
  clearBasket();
  showTaskBasket.value = false;
  showToast(`已提交 ${count} 条指令至执行层，待交易席位确认`, 'success');
}

// ── 三板斧: Model Tune Modal ─────────────────────────────────────
const showModelTuneModal = ref(false);
const activeTuneModel = ref<'bl' | 'rp'>('bl');

const MODEL_TYPES = [
  { id: 'bl' as const,  name: 'Black-Litterman' },
  { id: 'rp' as const,  name: '风险平价 (RP)' },
];

const MODEL_TUNE_PARAMS = {
  bl: [
    { key: 'tau',          label: 'Tau (观点置信度)',    min: 0.01, max: 1.0,  step: 0.01, unit: '',   def: 0.05, desc: '数值越大，观点对模型影响越大' },
    { key: 'eq_risk_aversion', label: '全局风险厌恶系数', min: 1,   max: 10,  step: 0.5,  unit: '',   def: 3.5,  desc: '影响均衡收益的风险溢价系数' },
    { key: 'bond_view',    label: '债券超额收益观点',    min: -2,  max: 5,   step: 0.1,  unit: '%',  def: 0.8,  desc: '基金经理对国内利率债的主观超额预期' },
    { key: 'eq_view',      label: '权益超额收益观点',    min: -5,  max: 15,  step: 0.5,  unit: '%',  def: 3.0,  desc: '基金经理对权益资产的主观超额预期' },
  ],
  rp: [
    { key: 'vol_lookback', label: '波动率回溯窗口',       min: 20,  max: 252, step: 5,    unit: 'D',  def: 60,   desc: '计算历史波动率所用交易日数' },
    { key: 'leverage',     label: '最大杠杆倍数',         min: 1.0, max: 2.0, step: 0.1,  unit: 'x',  def: 1.2,  desc: '组合整体杠杆上限约束' },
    { key: 'min_weight',   label: '单资产最低权重',       min: 0,   max: 10,  step: 0.5,  unit: '%',  def: 2,    desc: '每个资产类别的权重下限' },
  ],
};
const activeTuneModelParams = computed(() => MODEL_TUNE_PARAMS[activeTuneModel.value]);
const tuneParams = reactive<Record<string, number>>({
  tau: 0.05, eq_risk_aversion: 3.5, bond_view: 0.8, eq_view: 3.0,
  vol_lookback: 60, leverage: 1.2, min_weight: 2,
});

function applyModelTune() {
  const portfolio = selectedPortfolioInfo.value;
  if (!portfolio) return;
  // Generate mock model-driven instructions and add to basket
  const mockInstructions = [
    { securityCode: '019686.SH', securityName: '22附息国债24', direction: 'buy'  as const, amount_wan: 500, weight_delta: 1.5 },
    { securityCode: '512890.SH', securityName: '红利低波ETF',  direction: 'sell' as const, amount_wan: 300, weight_delta: -1.2 },
    { securityCode: '518880.SH', securityName: '黄金ETF',       direction: 'buy'  as const, amount_wan: 200, weight_delta: 0.8 },
  ];
  mockInstructions.forEach(inst =>
    addToBasket({ ...inst, portfolioId: portfolio.id, portfolioName: portfolio.name, source: 'model', settlement_days: 1 })
  );
  showModelTuneModal.value = false;
  showToast(`[${activeTuneModel.value === 'bl' ? 'BL模型' : '风险平价'}] 已生成 ${mockInstructions.length} 条意向指令并加入任务篮`, 'success');
}

// ── 三板斧: Security Pick Modal ──────────────────────────────────
const showSecurityPickModal = ref(false);
const pickSearchQuery = ref('');
const pickSelected = ref<SecurityItem | null>(null);
const pickDirection = ref<'buy' | 'sell'>('buy');
const pickAmount = ref<number | null>(null);

const filteredPickSecurities = computed(() => {
  const q = pickSearchQuery.value.toLowerCase().trim();
  if (!q) return SECURITY_DB;
  return SECURITY_DB.filter(s =>
    s.code.toLowerCase().includes(q) || s.name.toLowerCase().includes(q)
  );
});

function addPickToBasket() {
  const sec = pickSelected.value;
  const portfolio = selectedPortfolioInfo.value;
  if (!sec || !portfolio || !pickAmount.value || pickAmount.value <= 0) return;
  const wdelta = pickDirection.value === 'buy'
    ? +(pickAmount.value / 2600 * 100).toFixed(1)
    : -(pickAmount.value / 2600 * 100).toFixed(1);
  addToBasket({
    portfolioId: portfolio.id,
    portfolioName: portfolio.name,
    securityCode: sec.code,
    securityName: sec.name,
    direction: pickDirection.value,
    amount_wan: pickAmount.value,
    weight_delta: Number(wdelta),
    source: 'manual',
    settlement_days: 1,
  });
  showSecurityPickModal.value = false;
  pickSelected.value = null;
  pickAmount.value = null;
  pickSearchQuery.value = '';
  showToast(`已将「${sec.name}」${pickDirection.value === 'buy' ? '买入' : '卖出'} ¥${pickAmount.value}万 加入任务篮`, 'success');
}

// ── 三板斧: Upload Position (Excel Diff → Basket) ───────────────
const isPortfolioUploading = ref(false);

function handlePortfolioUpload() {
  if (isPortfolioUploading.value) return;
  const portfolio = selectedPortfolioInfo.value;
  if (!portfolio) return;
  isPortfolioUploading.value = true;
  setTimeout(() => {
    isPortfolioUploading.value = false;
    // Mock diff: compare uploaded target weights vs current holdings
    const diffInstructions = [
      { securityCode: '019524.SH', securityName: '23农发债07', direction: 'buy'  as const, amount_wan: 1200, weight_delta: 4.6 },
      { securityCode: '513180.SH', securityName: '恒生科技ETF', direction: 'sell' as const, amount_wan:  650, weight_delta: -2.5 },
      { securityCode: '159628.SZ', securityName: '华夏中证REITs', direction: 'buy' as const, amount_wan: 400, weight_delta: 1.5 },
    ];
    diffInstructions.forEach(inst =>
      addToBasket({ ...inst, portfolioId: portfolio.id, portfolioName: portfolio.name, source: 'batch', settlement_days: 1 })
    );
    showToast(`持仓_${portfolio.id}_0325.xlsx 解析完成，已 Diff 生成 ${diffInstructions.length} 条指令并加入任务篮`, 'success');
  }, 1400);
}

</script>
