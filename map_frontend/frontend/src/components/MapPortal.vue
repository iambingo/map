<template>
  <div class="h-full grid grid-cols-1 md:grid-cols-12 gap-4">

    <!-- ═══════════════════════════════════════════════════════════
         NAV PANEL
    ═══════════════════════════════════════════════════════════ -->
    <div :class="cn(
      'flex flex-col h-full bg-[#161922] border border-[#2E3348] rounded-xl overflow-hidden transition-all relative',
      fullScreenPanel === 'nav' ? 'col-span-12' : (fullScreenPanel ? 'hidden' : 'col-span-3')
    )">
      <div class="flex justify-between items-center p-3 border-b border-[#2E3348] bg-gradient-to-r from-[#252A3A] to-[#161922] shrink-0">
        <h2 class="am-title-l2"><div class="am-title-bar"></div>常用场景</h2>
        <div class="flex items-center space-x-1.5">
          <button @click="isEditingNav = true" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1.5 rounded hover:bg-[#2A2D3A] transition-colors" title="编辑常用场景">
            <Edit class="w-[13px] h-[13px]" />
          </button>
          <button @click="toggleFullScreen('nav')" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1.5 rounded hover:bg-[#2A2D3A] transition-colors">
            <ScaleToOriginal v-if="fullScreenPanel === 'nav'" class="w-[13px] h-[13px]" />
            <FullScreen v-else class="w-[13px] h-[13px]" />
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto p-3 space-y-3 no-scrollbar">
        <!-- Nav Grid -->
        <div>
          <div :class="cn('grid gap-2', fullScreenPanel === 'nav' ? 'grid-cols-6' : 'grid-cols-3')">
            <button
              v-for="item in currentNavItems"
              :key="item.id"
              @click="handleNavClick(item.id, item.sceneName || item.label)"
              class="flex flex-col items-center justify-center py-2.5 px-1 bg-[#1A1E2B] border border-[#2E3348] rounded-lg hover:border-[#3E4660] hover:bg-gradient-to-b hover:from-[#1F2333] hover:to-[#202431] transition-all group"
            >
              <div class="mb-1 group-hover:scale-110 transition-transform duration-200">
                <component :is="item.icon" :class="['w-[15px] h-[15px]', item.color]" />
              </div>
              <span class="text-[10px] font-medium text-[#94A3B8] group-hover:text-[#E5E5E5] text-center leading-tight transition-colors">{{ item.sceneName || item.label }}</span>
            </button>
          </div>
          <!-- Pagination Dots -->
          <div v-if="totalNavPages > 1" class="flex justify-center items-center space-x-1.5 mt-3 shrink-0">
            <button
              v-for="(_, idx) in totalNavPages"
              :key="idx"
              @click="navPage = idx"
              :class="cn('h-1.5 rounded-full transition-all duration-300', safeNavPage === idx ? 'bg-[#4D9DE0] w-4' : 'w-1.5 bg-[#333] hover:bg-[#555]')"
            />
          </div>
        </div>

        <!-- ═══ TODAY'S RADAR ═══ -->
        <div class="bg-[#1A1E2B] border border-[#2E3348] rounded-lg overflow-hidden">
          <!-- Header -->
          <div class="flex items-center justify-between px-2.5 py-1.5 border-b border-[#252A3A] bg-[#202431]">
            <div class="flex items-center space-x-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-[#FF5630] animate-pulse shrink-0"></span>
              <span class="text-[11px] font-bold text-[#E8ECF4] tracking-wide uppercase font-mono">今日关注</span>
            </div>
            <span class="text-[10px] font-mono text-[#94A3B8] tracking-widest">TODAY'S RADAR</span>
          </div>

          <div class="divide-y divide-[#252A3A]">

            <!-- Row 1: Product Alert -->
            <div class="flex items-start px-2.5 py-2 hover:bg-[#202431]/50 transition-colors">
              <div class="w-4 shrink-0 mt-px">
                <span class="text-[11px] leading-tight">🚨</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <span class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider">产品预警</span>
                  <span class="text-[10px] font-mono text-[#FF5630] bg-[#FF5630]/10 border border-[#FF5630]/25 px-1.5 py-px rounded font-bold">3只触线</span>
                </div>
                <p class="text-[11px] text-[#D0D4DD] mt-0.5 leading-snug">净值距预警阈值
                  <span class="text-[#FF5630] font-bold font-mono">&lt; 5bp</span>，需立即关注
                </p>
              </div>
            </div>

            <!-- Row 2: Macro rates -->
            <div class="flex items-start px-2.5 py-2 hover:bg-[#202431]/50 transition-colors">
              <div class="w-4 shrink-0 mt-px">
                <span class="text-[11px] leading-tight">📊</span>
              </div>
              <div class="flex-1 min-w-0">
                <span class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider">宏观利率</span>
                <div class="flex items-center flex-wrap gap-x-2.5 gap-y-0.5 mt-0.5">
                  <span class="text-[11px] font-mono text-[#E8ECF4]">10Y国债
                    <span class="font-bold">2.28%</span>
                    <span class="text-[#00C9A7] ml-0.5">▼3bp</span>
                  </span>
                  <span class="text-[#252A3A] select-none">|</span>
                  <span class="text-[11px] font-mono text-[#E8ECF4]">DR007
                    <span class="font-bold">1.82%</span>
                    <span class="text-[#FF5630] ml-0.5">▲2bp</span>
                  </span>
                </div>
              </div>
            </div>

            <!-- Row 3: Credit spread -->
            <div class="flex items-start px-2.5 py-2 hover:bg-[#202431]/50 transition-colors">
              <div class="w-4 shrink-0 mt-px">
                <span class="text-[11px] leading-tight">📈</span>
              </div>
              <div class="flex-1 min-w-0">
                <span class="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider">信用利差</span>
                <div class="flex items-center space-x-1 mt-0.5">
                  <span class="text-[11px] font-mono text-[#E8ECF4]">AA+
                    <span class="font-bold">62bp</span>
                    <span class="text-[#FF5630] ml-0.5">▲1bp</span>
                  </span>
                  <span class="text-[10px] font-mono text-[#94A3B8] bg-[#202431] px-1 py-px rounded border border-[#2E3348]">vs CGB</span>
                </div>
              </div>
            </div>

          </div>

          <!-- Footer timestamp -->
          <div class="px-2.5 py-1.5 border-t border-[#252A3A] bg-[#161922] flex items-center justify-between">
            <span class="text-[10px] font-mono text-[#64748B] uppercase tracking-widest">数据截止 09:25</span>
            <span class="text-[10px] font-mono text-[#64748B]">自动刷新</span>
          </div>
        </div>
      </div>

      <!-- Edit Nav Overlay -->
      <div v-if="isEditingNav" class="absolute inset-0 z-10 bg-[#161922] flex flex-col">
        <div class="flex justify-between items-center p-3 border-b border-[#2E3348] bg-gradient-to-r from-[#252A3A] to-[#161922] shrink-0">
          <h2 class="text-[15px] font-bold text-[#E5E5E5]">配置常用场景</h2>
          <button @click="isEditingNav = false" class="text-[#94A3B8] hover:text-[#E5E5E5] bg-[#222] hover:bg-[#2A2D3A] p-1 rounded transition-colors">
                  <Close class="w-3.5 h-3.5" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-3 space-y-4 no-scrollbar">
          <div>
            <div class="text-[10px] text-[#94A3B8] uppercase tracking-widest mb-2 font-mono">已选场景 (排序)</div>
            <div class="space-y-1.5">
              <div
                v-for="(id, index) in customNavIds"
                :key="id"
                class="flex items-center justify-between p-2 bg-[#1A1E2B] border border-[#2E3348] rounded group hover:border-[#3E4660] transition-colors"
              >
                <div class="flex items-center">
                  <Rank class="w-3 h-3 mr-2 text-[#7B8BA3]" />
                  <component :is="navItemById(id)?.icon" :class="cn('w-[13px] h-[13px] mr-2', navItemById(id)?.color)" />
                  <span class="text-[13px] text-[#D0D0D0]">{{ navItemById(id)?.label }}</span>
                </div>
                <div class="flex items-center space-x-1">
                  <button @click="moveNavItem(index, -1)" :disabled="index === 0" class="p-1 text-[#3A3A3A] hover:text-[#E5E5E5] disabled:opacity-20 rounded hover:bg-[#2A2D3A] transition-colors"><ArrowUp class="w-[11px] h-[11px]" /></button>
                  <button @click="moveNavItem(index, 1)" :disabled="index === customNavIds.length - 1" class="p-1 text-[#3A3A3A] hover:text-[#E5E5E5] disabled:opacity-20 rounded hover:bg-[#2A2D3A] transition-colors"><ArrowDown class="w-[11px] h-[11px]" /></button>
                  <div class="w-px h-3 bg-[#222] mx-1"></div>
                  <button @click="toggleNavId(id)" class="p-1 text-[#FF3B30]/70 hover:text-[#FF3B30] rounded hover:bg-[#FF3B30]/10 transition-colors"><Close class="w-[11px] h-[11px]" /></button>
                </div>
              </div>
            </div>
          </div>
          <div>
            <div class="text-[10px] text-[#94A3B8] uppercase tracking-widest mb-2 font-mono">可选场景</div>
            <div class="space-y-1.5">
              <div
                v-for="item in availableNavItems"
                :key="item.id"
                class="flex items-center justify-between p-2 bg-[#1A1E2B] border border-[#2E3348] rounded hover:border-[#3E4660] transition-colors"
              >
                <div class="flex items-center">
                  <component :is="item.icon" :class="cn('w-[13px] h-[13px] mr-2', item.color)" />
                  <span class="text-[13px] text-[#94A3B8]">{{ item.label }}</span>
                </div>
                <button @click="toggleNavId(item.id)" class="p-1 text-[#34C759]/70 hover:text-[#34C759] rounded hover:bg-[#34C759]/10 transition-colors">
                  <Plus class="w-[13px] h-[13px]" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════
         DASHBOARD PANEL
    ═══════════════════════════════════════════════════════════ -->
    <div :class="cn(
      'flex flex-col h-full bg-[#161922] border border-[#2E3348] rounded-xl overflow-hidden transition-all',
      fullScreenPanel === 'dashboard' ? 'col-span-12' : (fullScreenPanel ? 'hidden' : 'col-span-6')
    )">
      <div class="flex justify-between items-center p-3 border-b border-[#2E3348] bg-gradient-to-r from-[#252A3A] via-[#1C2030] to-[#161922] shrink-0">
        <h2 class="am-title-l2"><div class="am-title-bar"></div>投资工作台</h2>
        <button @click="toggleFullScreen('dashboard')" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1 rounded hover:bg-[#2A2D3A] transition-colors">
          <ScaleToOriginal v-if="fullScreenPanel === 'dashboard'" class="w-[13px] h-[13px]" />
          <FullScreen v-else class="w-[13px] h-[13px]" />
        </button>
      </div>

      <div class="flex-1 overflow-y-auto no-scrollbar flex flex-col min-h-0">

        <!-- ── Investment Process & Role Section ── -->
        <div class="px-3 py-2 border-b border-[#2E3348] shrink-0">

          <!-- Section Header -->
          <div class="flex items-center mb-2">
            <h3 class="text-[11px] font-bold text-[#94A3B8] flex items-center uppercase tracking-wider">
              <span class="w-[3px] h-3 rounded-full bg-[#4D9DE0] mr-2 shrink-0 shadow-[0_0_6px_rgba(77,157,224,0.6)]"></span>
              <Connection class="w-3 h-3 mr-1.5" /> 投资流程及重要事项提醒
            </h3>
          </div>

          <!-- ═══ DYNAMIC STEPPER FLOWCHART (compact) ═══ -->
          <div class="flex items-start w-full mb-2">
            <template v-for="(step, idx) in INVESTMENT_PROCESS" :key="step.id">

              <!-- ── Node ── -->
              <div
                class="flex flex-col items-center cursor-pointer group relative shrink-0"
                @click="selectedProcessStep = step.id"
              >
                <div :class="cn(
                  'w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 transition-all duration-200 select-none',
                  selectedProcessStep === step.id
                    ? 'bg-[#4D9DE0] border-[#4D9DE0] text-white scale-110 shadow-[0_0_0_2px_rgba(77,157,224,0.18),0_0_12px_rgba(77,157,224,0.55)]'
                    : 'bg-[#202431] border-[#2E3348] text-[#94A3B8] group-hover:border-[#4D9DE0]/60 group-hover:text-[#CBD5E1] group-hover:scale-110 group-hover:shadow-[0_0_0_2px_rgba(77,157,224,0.08),0_0_8px_rgba(77,157,224,0.2)]'
                )">
                  {{ step.id }}
                </div>
                <span :class="cn(
                  'mt-0.5 text-[10px] whitespace-nowrap transition-all duration-200',
                  selectedProcessStep === step.id
                    ? 'text-[#4D9DE0] font-bold'
                    : 'text-[#94A3B8] group-hover:text-[#CBD5E1]'
                )">{{ step.label }}</span>
                <div v-if="nodeTodoCounts[step.id]" class="absolute -top-1.5 -right-1.5 z-10 pointer-events-none">
                  <div class="min-w-[14px] h-3.5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center px-0.5 shadow-[0_0_6px_rgba(239,68,68,0.65)] border border-[#161922] leading-tight">
                    {{ nodeTodoCounts[step.id] }}
                  </div>
                </div>
              </div>

              <!-- ── Connector segment ── -->
              <div
                v-if="idx < INVESTMENT_PROCESS.length - 1"
                class="flex-1 self-start mt-[10px] mx-px"
              >
                <div class="h-[2px] bg-[#1E1E1E] relative overflow-hidden rounded-full">
                  <div :class="cn(
                    'absolute inset-y-0 left-0 rounded-full transition-all duration-500 ease-out',
                    selectedProcessStep !== null && step.id < selectedProcessStep
                      ? 'w-full bg-gradient-to-r from-[#4D9DE0] to-[#5BAEF0]'
                      : 'w-0'
                  )"></div>
                </div>
              </div>

            </template>
          </div>

          <!-- Task Detail Panel (compact single-line layout) -->
          <div class="bg-gradient-to-br from-[#202431] to-[#1A1E2B] border border-[#2E3348] rounded-lg px-2.5 py-2">
            <template v-if="selectedProcessStep">
              <template v-if="currentTasks.length > 0">
                <!-- Header row (compact) -->
                <div class="text-[11px] mb-1.5 border-b border-[#252A3A] pb-1.5 flex items-center justify-between">
                  <span class="flex items-center font-bold text-[#CBD5E1]">
                    <span class="text-[#4D9DE0] mr-1">{{ stepLabel }}</span>
                    <span class="text-[#7B8BA3] mx-1">—</span>
                    待办事项
                  </span>
                  <span :class="cn('text-[10px] font-mono px-2 py-1 rounded border', ROLE_BADGE_CLASSES[activeRole])">
                    {{ activeRole }}
                  </span>
                </div>
                <!-- Task list: single-line flat layout -->
                <div class="space-y-1">
                  <template v-for="(task, idx) in currentTasks" :key="idx">
                    <template v-if="task.todos?.length === 1">
                      <!-- Single todo → single-line layout -->
                      <div class="flex items-center gap-1.5 group/task py-1 px-1 rounded hover:bg-[#1A1E2B]/60 transition-colors cursor-pointer">
                        <div class="w-1.5 h-1.5 rounded-full bg-[#FF9500] shrink-0 shadow-[0_0_4px_rgba(255,149,0,0.4)]"></div>
                        <span class="text-[11px] text-[#D0D0D0] font-medium shrink-0 group-hover/task:text-[#4D9DE0] transition-colors">{{ task.title }}</span>
                        <span class="flex-1 min-w-0 text-[11px] text-[#B4BAC9] truncate">{{ task.todos[0].text }}</span>
                        <span class="text-[10px] text-[#94A3B8] shrink-0 font-mono">{{ task.todos[0].time }}</span>
                        <div class="flex items-center gap-1 shrink-0">
                          <button
                            v-for="(link, lIdx) in task.links"
                            :key="lIdx"
                            @click.stop="handleLinkNavigate(link)"
                            class="inline-flex items-center text-[10px] text-[#4D9DE0] hover:text-[#7EB6FF] bg-[#4D9DE0]/10 hover:bg-[#4D9DE0]/20 border border-[#4D9DE0]/25 px-1.5 py-px rounded transition-all"
                          >
                            {{ link }}
                            <ArrowUp class="w-[8px] h-[8px] ml-0.5" />
                          </button>
                        </div>
                      </div>
                    </template>
                    <template v-else>
                      <!-- Multiple todos → grouped compact layout -->
                      <div class="py-1 px-1">
                        <div class="flex items-center gap-1.5 mb-0.5">
                          <Select class="w-2.5 h-2.5 text-[#2A2A2A] group-hover/task:text-[#4D9DE0] transition-colors shrink-0" />
                          <span class="text-[11px] text-[#D0D0D0] font-medium group-hover/task:text-[#4D9DE0] transition-colors">{{ task.title }}</span>
                          <div class="flex items-center gap-1 shrink-0 ml-auto">
                            <button
                              v-for="(link, lIdx) in task.links"
                              :key="lIdx"
                              @click.stop="handleLinkNavigate(link)"
                              class="inline-flex items-center text-[10px] text-[#4D9DE0] hover:text-[#7EB6FF] bg-[#4D9DE0]/10 hover:bg-[#4D9DE0]/20 border border-[#4D9DE0]/25 px-1.5 py-px rounded transition-all"
                            >
                              {{ link }}
                              <ArrowUp class="w-[8px] h-[8px] ml-0.5" />
                            </button>
                          </div>
                        </div>
                        <div v-if="task.todos?.length" class="space-y-0.5 pl-2">
                          <div
                            v-for="(todo, tIdx) in task.todos"
                            :key="tIdx"
                            class="flex items-center gap-1.5 py-1 px-1 rounded hover:bg-[#1A1E2B]/60 transition-colors cursor-pointer"
                          >
                            <div class="w-1 h-1 rounded-full bg-[#FF9500] shrink-0"></div>
                            <span class="flex-1 min-w-0 text-[11px] text-[#B4BAC9] truncate">{{ todo.text }}</span>
                            <span class="text-[10px] text-[#94A3B8] shrink-0 font-mono">{{ todo.time }}</span>
                          </div>
                        </div>
                      </div>
                    </template>
                  </template>
                </div>
              </template>
              <!-- Fallback: current role has no tasks → show all-role reference tasks -->
              <template v-else>
                <div class="text-[11px] mb-1.5 border-b border-[#252A3A] pb-1.5 flex items-center justify-between">
                  <span class="flex items-center font-bold text-[#CBD5E1]">
                    <span class="text-[#4D9DE0] mr-1">{{ stepLabel }}</span>
                    <span class="text-[#7B8BA3] mx-1">—</span>
                    关联系统与场景
                  </span>
                  <span class="text-[10px] font-mono px-2 py-1 rounded border text-[#94A3B8] bg-[#555]/10 border-[#555]/30">全角色参考</span>
                </div>
                <div v-if="nodeAllTasks.length > 0" class="space-y-1">
                  <div v-for="(task, idx) in nodeAllTasks" :key="idx" class="flex items-center gap-1.5 py-1 px-1 rounded hover:bg-[#1A1E2B]/60 transition-colors group/task cursor-pointer">
                    <Select class="w-2.5 h-2.5 text-[#2A2A2A] group-hover/task:text-[#4D9DE0] transition-colors shrink-0" />
                    <span class="text-[11px] text-[#CBD5E1] font-medium group-hover/task:text-[#D0D0D0] transition-colors">{{ task.title }}</span>
                    <div class="flex items-center gap-1 shrink-0 ml-auto">
                      <button
                        v-for="(link, lIdx) in task.links"
                        :key="lIdx"
                        @click.stop="handleLinkNavigate(link)"
                        class="inline-flex items-center text-[10px] text-[#4D9DE0] hover:text-[#7EB6FF] bg-[#4D9DE0]/10 hover:bg-[#4D9DE0]/20 border border-[#4D9DE0]/25 px-1.5 py-px rounded transition-all"
                      >
                        {{ link }}
                        <ArrowUp class="w-[8px] h-[8px] ml-0.5" />
                      </button>
                    </div>
                  </div>
                </div>
                <div v-else class="flex items-center justify-center py-2 text-[11px] text-[#94A3B8] font-mono">
                  该节点暂无关联场景
                </div>
              </template>
            </template>
            <!-- No step selected -->
            <div v-else class="flex items-center justify-center py-2 text-[11px] text-[#94A3B8] font-mono tracking-wide">
              ↑ 请点击上方流程节点查看待办事项
            </div>
          </div>
        </div>

        <!-- ── Portfolio Analysis Cockpit Entry ── -->
        <div class="px-3 py-1.5 shrink-0 border-b border-[#2E3348]">
          <button
            @click="emit('navigate', 'executive')"
            class="w-full flex items-center justify-between bg-gradient-to-r from-[#0E1A2B] via-[#0C1420] to-[#1A1E2B] border border-[#4D9DE0]/20 hover:border-[#4D9DE0]/55 rounded-lg px-3 py-2 transition-all duration-200 group shadow-[0_0_18px_rgba(77,157,224,0.05)] hover:shadow-[0_0_22px_rgba(77,157,224,0.18)]"
          >
            <div class="flex items-center space-x-2.5">
              <div class="w-6 h-6 rounded-full bg-[#4D9DE0]/10 border border-[#4D9DE0]/20 flex items-center justify-center group-hover:shadow-[0_0_10px_rgba(77,157,224,0.3)] transition-all shrink-0">
                <Histogram class="w-3 h-3 text-[#4D9DE0]" />
              </div>
              <div class="text-left">
                <div class="text-[11px] font-bold text-[#D0D0D0] group-hover:text-white transition-colors tracking-wide">📊 进入组合分析驾驶舱</div>
                <div class="text-[10px] text-[#94A3B8] font-mono mt-0.5 tracking-wider">业绩归因 · 偏离监控 · 风险报告</div>
              </div>
            </div>
            <div class="flex items-center space-x-1 shrink-0">
              <span class="text-[10px] font-mono text-[#4D9DE0]/50 group-hover:text-[#4D9DE0] transition-colors">立即查看</span>
              <ArrowRight class="w-3 h-3 text-[#4D9DE0]/50 group-hover:text-[#4D9DE0] group-hover:translate-x-0.5 transition-all duration-200" />
            </div>
          </button>
        </div>

        <!-- ── Portfolio Info Section (flex-1 to consume remaining space) ── -->
        <div class="flex flex-col flex-1 min-h-0 px-3 py-2">
          <div class="flex justify-between items-center mb-2">
            <h3 class="text-[11px] font-bold text-[#94A3B8] flex items-center uppercase tracking-wider">
              <span class="w-[3px] h-3 rounded-full bg-[#FF9500] mr-2 shrink-0 shadow-[0_0_6px_rgba(255,149,0,0.5)]"></span>
              <Files class="w-3 h-3 mr-1.5" /> 组合信息展示
            </h3>
            <button
              @click="openPortfolioModal"
              class="flex items-center space-x-1.5 bg-[#202431] border border-[#2E3348] px-2.5 py-1 rounded text-[11px] text-[#CBD5E1] hover:border-[#4D9DE0]/40 hover:text-[#E5E5E5] hover:bg-[#4D9DE0]/5 transition-colors"
            >
              <Operation class="w-[10px] h-[10px] text-[#4D9DE0]" />
              <span>已选 {{ selectedPortfolios.length }} 个产品</span>
              <ArrowDown class="w-[10px] h-[10px] text-[#94A3B8]" />
            </button>
          </div>

          <template v-if="selectedPortfolios.length > 0">
            <!-- KPI Metrics (compact) -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-2 shrink-0">
              <div class="bg-gradient-to-br from-[#1A1E2B] to-[#1A1E2B] border border-[#2E3348] p-2 rounded-lg hover:border-[#3E4660] transition-colors">
                <div class="text-[10px] text-[#94A3B8] mb-0.5 uppercase tracking-wider">收益率 YTD</div>
                <div class="text-[15px] font-bold text-[#FF3B30] font-mono">+4.52%</div>
              </div>
              <div class="bg-gradient-to-br from-[#1A1E2B] to-[#1A1E2B] border border-[#2E3348] p-2 rounded-lg hover:border-[#3E4660] transition-colors">
                <div class="text-[10px] text-[#94A3B8] mb-0.5 uppercase tracking-wider">净资产</div>
                <div class="text-[15px] font-bold text-[#E5E5E5] font-mono">12.5 <span class="text-[10px] text-[#94A3B8]">亿</span></div>
              </div>
              <div class="bg-gradient-to-br from-[#1A1E2B] to-[#1A1E2B] border border-[#2E3348] p-2 rounded-lg hover:border-[#3E4660] transition-colors">
                <div class="text-[10px] text-[#94A3B8] mb-0.5 uppercase tracking-wider">负债规模</div>
                <div class="text-[15px] font-bold text-[#E5E5E5] font-mono">1.8 <span class="text-[10px] text-[#94A3B8]">亿</span></div>
              </div>
              <div class="bg-gradient-to-br from-[#1A1E2B] to-[#1A1E2B] border border-[#2E3348] p-2 rounded-lg hover:border-[#3E4660] transition-colors">
                <div class="text-[10px] text-[#94A3B8] mb-0.5 uppercase tracking-wider">杠杆指标</div>
                <div class="text-[15px] font-bold text-[#E5E5E5] font-mono">114.4%</div>
              </div>
            </div>

            <!-- Charts Row (flex-1 to eat remaining space) -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-2 flex-1 min-h-0">
              <div class="bg-gradient-to-br from-[#202431] to-[#1A1E2B] border border-[#2E3348] p-2 rounded-lg flex flex-col min-h-0">
                <div class="text-[11px] text-[#CBD5E1] mb-1.5 font-medium shrink-0">组合偏离差异 (权益敞口)</div>
                <div class="flex-1 min-h-0">
                  <VChart :option="deviationOption" autoresize style="height:100%;width:100%" />
                </div>
              </div>
              <div class="col-span-2 bg-gradient-to-br from-[#202431] to-[#1A1E2B] border border-[#2E3348] p-2 rounded-lg flex flex-col min-h-0">
                <div class="flex justify-between items-center mb-1.5 shrink-0">
                  <div class="text-[11px] text-[#CBD5E1] font-medium">近期历史表现</div>
                  <div class="flex space-x-0.5 bg-[#1A1E2B] p-0.5 rounded border border-[#2E3348]">
                    <button
                      v-for="t in ['1M','3M','6M','1Y','YTD']"
                      :key="t"
                      @click="timeframe = t"
                      :class="cn('px-2 py-1 text-[10px] rounded transition-all', timeframe === t ? 'bg-[#4D9DE0] text-white shadow-[0_0_6px_rgba(77,157,224,0.35)]' : 'text-[#94A3B8] hover:text-[#CBD5E1]')"
                    >{{ t }}</button>
                  </div>
                </div>
                <div class="flex-1 min-h-0">
                  <VChart :option="performanceOption" autoresize style="height:100%;width:100%" />
                </div>
              </div>
            </div>
          </template>
          <div v-else class="flex-1 flex items-center justify-center text-[#94A3B8] text-[11px] py-6 font-mono">
            请选择要查看的投资组合
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════
         CHAT PANEL
    ═══════════════════════════════════════════════════════════ -->
    <div :class="cn(
      'flex flex-col h-full bg-[#161922] border border-[#2E3348] rounded-xl overflow-hidden transition-all',
      fullScreenPanel === 'chat' ? 'col-span-12' : (fullScreenPanel ? 'hidden' : 'col-span-3')
    )">
      <!-- Header: subtle blue-tinted gradient -->
      <div class="flex justify-between items-center p-3 border-b border-[#2E3348] bg-gradient-to-r from-[#252A3A] via-[#15202B] to-[#161922] shrink-0">
        <h2 class="am-title-l2"><div class="am-title-bar"></div>AI 助手</h2>
        <div class="flex items-center space-x-1">
          <button class="text-[#94A3B8] hover:text-[#E5E5E5] p-1.5 bg-[#1F2333] hover:bg-[#252B3A] rounded transition-colors" title="历史记录">
            <Clock class="w-3 h-3" />
          </button>
          <button @click="chatMessages = []" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1.5 bg-[#1F2333] hover:bg-[#252B3A] rounded transition-colors" title="新对话">
            <Plus class="w-3 h-3" />
          </button>
          <button @click="toggleFullScreen('chat')" class="text-[#94A3B8] hover:text-[#E5E5E5] p-1 ml-0.5 rounded hover:bg-[#252B3A] transition-colors">
            <ScaleToOriginal v-if="fullScreenPanel === 'chat'" class="w-[13px] h-[13px]" />
            <FullScreen v-else class="w-[13px] h-[13px]" />
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto p-4 flex flex-col no-scrollbar" ref="chatContainerRef">
        <!-- Welcome State -->
        <template v-if="chatMessages.length === 0">
          <div class="flex-1 flex flex-col items-center justify-start space-y-5 pt-4">
            <div class="text-center">
              <div class="w-12 h-12 rounded-full bg-gradient-to-br from-[#4D9DE0] to-[#AF52DE] flex items-center justify-center shadow-[0_0_24px_rgba(77,157,224,0.35)] mx-auto mb-3">
                <StarFilled class="w-5 h-5 text-white" />
              </div>
              <h3 class="text-[15px] font-bold text-[#E5E5E5]">您好，我是您的全能 AI 助手</h3>
              <p class="text-[11px] text-[#94A3B8] mt-1.5 max-w-[200px] mx-auto leading-relaxed">
                您可以向我<span class="text-[#4D9DE0] font-bold mx-1">【问数】</span>或<span class="text-[#34C759] font-bold mx-1">【派活】</span>，我将为您自动路由至对应的系统或数字员工。
              </p>
            </div>
            <!-- ✨ Alpha Mind DIS Insight Card -->
            <div class="w-full relative overflow-hidden rounded-xl border border-purple-500/25 bg-gradient-to-br from-[#120B1E] via-[#0E0818] to-[#1A1E2B] shadow-[0_0_22px_rgba(168,85,247,0.18)] p-3">
              <!-- Corner glow -->
              <div class="absolute top-0 right-0 w-16 h-16 bg-purple-500/10 rounded-full blur-2xl pointer-events-none"></div>
              <!-- Header -->
              <div class="flex items-center justify-between mb-2">
                <span class="text-[11px] font-bold font-mono text-purple-300 flex items-center">
                  <span class="w-1.5 h-1.5 rounded-full bg-purple-400 mr-1.5 animate-pulse shrink-0"></span>
                  ✨ Alpha Mind 专属洞察
                </span>
                <span class="text-[7.5px] font-mono text-purple-400/50 bg-purple-900/20 border border-purple-500/15 px-1.5 py-1 rounded">置信度 72%</span>
              </div>
              <!-- Body -->
              <p class="text-[9.5px] font-mono text-purple-200/70 leading-relaxed mb-2.5">
                基于您过去 <span class="text-white font-bold">90天</span> 在系统内的 <span class="text-purple-300 font-bold">23 次</span>调仓操作，系统已成功为您反向拟合了<span class="text-purple-200 font-bold">【隐性配置偏好模型】</span>。<br/>
                在 <span class="text-yellow-400 font-bold">A股红利</span> 方向您的择时胜率达 <span class="text-green-400 font-bold">68%</span>，
                <span class="text-purple-400/80">高于部门均值 +14pp。</span>
              </p>
              <!-- Action buttons -->
              <div class="flex space-x-2">
                <button class="flex-1 flex items-center justify-center space-x-1 text-[10px] font-mono font-bold bg-purple-600/20 hover:bg-purple-600/35 border border-purple-500/30 hover:border-purple-400/50 text-purple-200 py-1.5 rounded-lg transition-all duration-200 shadow-[0_0_10px_rgba(168,85,247,0.15)] hover:shadow-[0_0_16px_rgba(168,85,247,0.3)]">
                  <TrendCharts class="w-3 h-3 shrink-0" />
                  <span>📊 查看组合分析档案</span>
                </button>
                <button class="flex-1 flex items-center justify-center space-x-1 text-[10px] font-mono font-bold bg-[#1A1E2B] hover:bg-[#1F2333] border border-purple-500/20 hover:border-purple-400/35 text-purple-400/80 hover:text-purple-300 py-1.5 rounded-lg transition-all duration-200">
                  <Files class="w-3 h-3 shrink-0" />
                  <span>💾 存入我的专属库</span>
                </button>
              </div>
            </div>

            <div class="w-full space-y-3">
              <div class="bg-gradient-to-br from-[#202431] to-[#1A1E2B] border border-[#2E3348] rounded-lg p-3 hover:border-[#4D9DE0]/25 transition-colors">
                <div class="flex items-center am-title-l3 mb-1"><div class="am-title-bar"></div>问数 - 理财有数</div>
                <div class="text-[10px] text-[#94A3B8] mb-2.5">通过自然语言直接生成各类数据报表。</div>
                <div class="space-y-1.5">
                  <button @click="handleSendMessage('拉取固收+部门Q1产品业绩归因表')" class="w-full text-left text-[11px] bg-[#1A1E2B] border border-[#252A3A] p-2 rounded hover:border-[#4D9DE0]/35 hover:bg-[#4D9DE0]/5 transition-all text-[#94A3B8] flex items-center">
                    <span class="w-1.5 h-1.5 rounded-full bg-[#4D9DE0] mr-2 shrink-0 shadow-[0_0_4px_rgba(77,157,224,0.5)]"></span>
                    <span class="truncate">拉取固收+部门Q1产品业绩归因表</span>
                  </button>
                  <button @click="handleSendMessage('对比启航1号与基准组合的行业偏离')" class="w-full text-left text-[11px] bg-[#1A1E2B] border border-[#252A3A] p-2 rounded hover:border-[#4D9DE0]/35 hover:bg-[#4D9DE0]/5 transition-all text-[#94A3B8] flex items-center">
                    <span class="w-1.5 h-1.5 rounded-full bg-[#4D9DE0] mr-2 shrink-0 shadow-[0_0_4px_rgba(77,157,224,0.5)]"></span>
                    <span class="truncate">对比启航1号与基准组合的行业偏离</span>
                  </button>
                </div>
              </div>
              <div class="bg-gradient-to-br from-[#202431] to-[#1A1E2B] border border-[#2E3348] rounded-lg p-3 hover:border-[#34C759]/25 transition-colors">
                <div class="flex items-center am-title-l3 mb-1"><div class="am-title-bar"></div>派活 - 数字员工</div>
                <div class="text-[10px] text-[#94A3B8] mb-2.5">唤起专属 Agent 帮您处理复杂任务。</div>
                <div class="grid grid-cols-3 gap-1.5">
                  <button
                    v-for="agent in AGENTS"
                    :key="agent"
                    @click="handleSendMessage(`唤起【${agent}】`)"
                    class="text-[10px] bg-[#1A1E2B] border border-[#252A3A] py-1.5 rounded text-center hover:border-[#34C759]/35 hover:bg-[#34C759]/5 hover:text-[#34C759] transition-all text-[#94A3B8]"
                  >{{ agent }}</button>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- Chat History -->
        <template v-else>
          <div class="flex-1 space-y-4">
            <div
              v-for="msg in chatMessages"
              :key="msg.id"
              :class="cn('flex flex-col', msg.role === 'user' ? 'items-end' : 'items-start')"
            >
              <div :class="cn(
                'max-w-[85%] rounded-lg p-2.5 text-[13px]',
                msg.role === 'user'
                  ? 'bg-[#4D9DE0] text-white rounded-tr-none shadow-[0_2px_12px_rgba(77,157,224,0.3)]'
                  : 'bg-gradient-to-br from-[#1F2333] to-[#1A1E2B] border border-[#2E3348] text-[#E5E5E5] rounded-tl-none'
              )">
                <template v-if="msg.role === 'user'">{{ msg.text }}</template>
                <template v-else>
                  <div v-if="msg.prefixLabel" class="mb-1.5">
                    <span :class="cn('font-mono text-[11px] px-1.5 py-1 rounded border inline-block', msg.prefixClass)">
                      {{ msg.prefixLabel }}
                    </span>
                  </div>
                  <div class="text-[#D0D0D0] text-[13px] leading-relaxed">{{ msg.text }}</div>
                  <div v-if="msg.actionType === 'data'" class="mt-3 h-14 border border-[#2E3348] rounded bg-[#1A1E2B] flex items-center justify-center text-[11px] text-[#94A3B8] hover:border-[#4D9DE0]/40 cursor-pointer transition-colors">
                    <Histogram class="w-[13px] h-[13px] mr-1.5 text-[#4D9DE0]" /> 点击查看数据面板
                  </div>
                  <div v-else-if="msg.actionType === 'bot'" class="mt-3 p-2 border border-[#2E3348] rounded bg-[#1A1E2B] flex items-center justify-between text-[11px] text-[#94A3B8]">
                    <div class="flex items-center"><Cpu class="w-[13px] h-[13px] mr-1.5 text-[#AF52DE]" /> 任务执行中...</div>
                    <div class="w-4 h-4 border-2 border-[#AF52DE]/30 border-t-[#AF52DE] rounded-full animate-spin"></div>
                  </div>
                  <div v-else-if="msg.actionType === 'model'" @click="emit('navigate', 'model-center')" class="mt-3 p-2 border border-[#2E3348] rounded bg-[#1A1E2B] flex items-center justify-center text-[11px] text-[#FF9500] hover:bg-[#FF9500]/10 cursor-pointer transition-colors">
                    <Odometer class="w-[13px] h-[13px] mr-1.5" /> 跳转至模型中心
                  </div>
                  <div v-else-if="msg.actionType === 'agent'" class="mt-3 p-2 border border-[#2E3348] rounded bg-[#1A1E2B] flex items-center justify-between text-[11px] text-[#94A3B8]">
                    <div class="flex items-center"><Lightning class="w-[13px] h-[13px] mr-1.5 text-[#34C759]" /> {{ msg.agentName }} 处理中...</div>
                    <div class="w-4 h-4 border-2 border-[#34C759]/30 border-t-[#34C759] rounded-full animate-spin"></div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Chat Input -->
      <div class="p-3 border-t border-[#252A3A] bg-gradient-to-r from-[#161922] to-[#161922] shrink-0">
        <div class="relative flex items-center bg-[#1A1E2B] border border-[#2E3348] rounded-lg focus-within:border-[#4D9DE0]/40 focus-within:shadow-[0_0_10px_rgba(77,157,224,0.08)] transition-all px-2 py-1.5">
          <button class="text-[#94A3B8] hover:text-[#4D9DE0] p-1 transition-colors shrink-0"><User class="w-[13px] h-[13px]" /></button>
          <input
            v-model="chatInput"
            @keydown.enter.exact.prevent="handleSendMessage()"
            type="text"
            placeholder="输入您的问题或指令..."
            class="flex-1 bg-transparent border-none outline-none text-[13px] text-[#E5E5E5] px-2 placeholder-[#333]"
          />
          <button
            @click="handleSendMessage()"
            :class="cn('p-1.5 rounded-md transition-all shrink-0', chatInput.length > 0 ? 'bg-[#4D9DE0] text-white shadow-[0_0_10px_rgba(77,157,224,0.35)] hover:bg-[#5AADF0]' : 'bg-[#161922] text-[#7B8BA3]')"
          >
            <Promotion class="w-[13px] h-[13px]" />
          </button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════
         PORTFOLIO SELECTION MODAL
    ═══════════════════════════════════════════════════════════ -->
    <div v-if="isPortfolioModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div class="bg-[#161922] border border-[#2E3348] rounded-xl w-[500px] max-h-[80vh] flex flex-col shadow-2xl">
        <div class="flex justify-between items-center p-4 border-b border-[#2E3348] bg-gradient-to-r from-[#1F2333] to-[#161922] rounded-t-xl">
          <h2 class="text-[15px] font-bold text-[#E5E5E5]">选择产品组合</h2>
          <button @click="isPortfolioModalOpen = false" class="text-[#94A3B8] hover:text-[#E5E5E5] transition-colors p-1 rounded hover:bg-[#2A2D3A]">
            <Close class="w-[15px] h-[15px]" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
          <div v-for="(category, idx) in PRODUCT_TREE" :key="idx" class="space-y-2">
            <div
              @click="toggleCategorySelection(category)"
              class="flex items-center text-[13px] font-bold text-[#CBD5E1] bg-[#202431] px-2 py-1.5 rounded cursor-pointer hover:bg-[#1F2333] transition-colors border border-[#2E3348]"
            >
              <div :class="cn('w-3.5 h-3.5 rounded flex items-center justify-center mr-2 border transition-colors', isCategoryFullySelected(category) || isCategoryPartiallySelected(category) ? 'bg-[#4D9DE0] border-[#4D9DE0]' : 'border-[#2E3348]')">
                <Select v-if="isCategoryFullySelected(category)" class="w-2.5 h-2.5 text-white" />
                <div v-else-if="isCategoryPartiallySelected(category)" class="w-1.5 h-0.5 bg-white rounded-sm"></div>
              </div>
              {{ category.category }}
            </div>
            <div class="grid grid-cols-2 gap-2 pl-6">
              <div
                v-for="item in category.items"
                :key="item.id"
                @click="toggleTempPortfolio(item.id)"
                :class="cn(
                  'flex items-center p-2 rounded border cursor-pointer transition-all',
                  tempSelectedPortfolios.includes(item.id)
                    ? 'bg-[#4D9DE0]/10 border-[#4D9DE0]/50 text-[#4D9DE0] shadow-[0_0_8px_rgba(77,157,224,0.1)]'
                    : 'bg-[#1A1E2B] border-[#2E3348] text-[#E5E5E5] hover:border-[#3E4660]'
                )"
              >
                <div :class="cn('w-3 h-3 rounded flex items-center justify-center mr-2 border shrink-0', tempSelectedPortfolios.includes(item.id) ? 'bg-[#4D9DE0] border-[#4D9DE0]' : 'border-[#2E3348]')">
                  <Select v-if="tempSelectedPortfolios.includes(item.id)" class="w-2.5 h-2.5 text-white" />
                </div>
                <div class="flex flex-col">
                  <span class="text-[13px]">{{ item.name }}</span>
                  <span class="text-[10px] text-[#94A3B8] font-mono">{{ item.code }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="p-4 border-t border-[#2E3348] flex justify-end space-x-3 bg-[#202431] rounded-b-xl">
          <button @click="isPortfolioModalOpen = false" class="px-4 py-1.5 rounded text-[13px] text-[#94A3B8] hover:text-[#E5E5E5] transition-colors">取消</button>
          <button @click="confirmPortfolioSelection" class="px-4 py-1.5 rounded text-[13px] bg-[#4D9DE0] text-white hover:bg-[#5AADF0] transition-colors shadow-[0_0_10px_rgba(77,157,224,0.3)]">确认选择</button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════
         EXTERNAL LINK MODAL
    ═══════════════════════════════════════════════════════════ -->
    <div v-if="externalLinkModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div class="bg-[#161922] border border-[#2E3348] rounded-xl w-[400px] flex flex-col shadow-2xl">
        <div class="flex justify-between items-center p-4 border-b border-[#2E3348] bg-gradient-to-r from-[#1F2333] to-[#161922] rounded-t-xl">
          <h2 class="am-title-l2"><div class="am-title-bar"></div>系统跳转提示</h2>
          <button @click="externalLinkModal = null" class="text-[#94A3B8] hover:text-[#E5E5E5] transition-colors p-1 rounded hover:bg-[#2A2D3A]"><Close class="w-[15px] h-[15px]" /></button>
        </div>
        <div class="p-6 text-center">
          <div class="w-12 h-12 rounded-full bg-[#4D9DE0]/10 border border-[#4D9DE0]/20 flex items-center justify-center mx-auto mb-4 shadow-[0_0_20px_rgba(77,157,224,0.12)]">
            <ArrowUp class="w-[22px] h-[22px] text-[#4D9DE0]" />
          </div>
          <h3 class="text-[#E5E5E5] font-medium mb-2">即将跳转至外部系统</h3>
          <p class="text-[#94A3B8] text-[13px]">即将前往<span class="text-[#4D9DE0] font-bold mx-1">【{{ externalLinkModal }}】</span>系统。</p>
        </div>
        <div class="p-4 border-t border-[#2E3348] flex justify-end space-x-3 bg-[#202431] rounded-b-xl">
          <button @click="externalLinkModal = null" class="px-4 py-1.5 rounded text-[13px] text-[#94A3B8] hover:text-[#E5E5E5] transition-colors">取消</button>
          <button @click="externalLinkModal = null" class="px-4 py-1.5 rounded text-[13px] bg-[#4D9DE0] text-white hover:bg-[#5AADF0] transition-colors shadow-[0_0_10px_rgba(77,157,224,0.3)]">确认跳转</button>
        </div>
      </div>
    </div>

  </div>

  <!-- ── Navigation Toast ── -->
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-3 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-3 scale-95"
    >
      <div
        v-if="showToast"
        class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[9999] px-5 py-2.5 rounded-xl border border-[#FF9500]/30 bg-[#1A1E2B]/90 backdrop-blur-md text-[#FF9500] text-[13px] font-mono shadow-[0_0_24px_rgba(255,149,0,0.15)] flex items-center space-x-2 select-none pointer-events-none"
      >
        <span>{{ toastMsg }}</span>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue';
import {
  FullScreen, ScaleToOriginal, Plus, Clock, Promotion, User,
  Operation, ArrowUp, TrendCharts, DataBoard, ArrowRight,
  Select, Connection, Odometer, Histogram, Setting,
  Monitor, UserFilled, OfficeBuilding, EditPen, DataAnalysis, Edit, Close, Rank,
  ArrowDown, DataLine, Files, Cpu, StarFilled, ChatDotRound, Lightning,
} from '@element-plus/icons-vue';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart } from 'echarts/charts';
import {
  GridComponent, TooltipComponent, LegendComponent,
} from 'echarts/components';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { activeRole, ROLES, fetchMeetingResolution, type Role } from '../store/demoStore';

// Register ECharts components
use([CanvasRenderer, BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent]);

/** 默认首页是门户 Tab，CommitteeView 不会挂载；在此拉取 BFF 快照，避免「从未发请求」 */
onMounted(() => {
  void fetchMeetingResolution();
});

// ── cn utility ──────────────────────────────────────────────────────────────
function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

// ── Emits ───────────────────────────────────────────────────────────────────
const emit = defineEmits<{ navigate: [tabId: string] }>();

// ── Types ───────────────────────────────────────────────────────────────────
type NodeId = 1 | 2 | 3 | 4 | 5 | 6 | 7;
type PanelId = 'nav' | 'dashboard' | 'chat';

interface TodoItem { text: string; time: string }
interface Task { title: string; links: string[]; todos?: TodoItem[] }
type RoleKey = Role | 'ALL';
type ProcessMatrix = Record<NodeId, Partial<Record<RoleKey, Task[]>>>;

interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  text: string;
  prefixLabel?: string;
  prefixClass?: string;
  actionType?: 'data' | 'bot' | 'model' | 'agent';
  agentName?: string;
}

// ── Static Data ──────────────────────────────────────────────────────────────

const ROLE_COLORS: Record<Role, string> = {
  '班子':    'bg-[#FF3B30]',
  '部门长':  'bg-[#FF9500]',
  '投资经理':'bg-[#4D9DE0]',
  '投资助理':'bg-[#34C759]',
  '投管':    'bg-[#AF52DE]',
};

const ROLE_BADGE_CLASSES: Record<Role, string> = {
  '班子':    'text-[#FF3B30] bg-[#FF3B30]/10 border-[#FF3B30]/30',
  '部门长':  'text-[#FF9500] bg-[#FF9500]/10 border-[#FF9500]/30',
  '投资经理':'text-[#4D9DE0] bg-[#4D9DE0]/10 border-[#4D9DE0]/30',
  '投资助理':'text-[#34C759] bg-[#34C759]/10 border-[#34C759]/30',
  '投管':    'text-[#AF52DE] bg-[#AF52DE]/10 border-[#AF52DE]/30',
};

const AGENTS = ['竞品分析', '选券助手', '研究助手', '观点跟踪', '预警提醒', '复盘检视'];

// ── Role-Process Matrix ───────────────────────────────────────────────────────
const roleProcessMatrix: ProcessMatrix = {
  1: {
    '班子':    [{ title: '完整的产品图谱', links: ['数据中心'],
                  todos: [{ text: '查看2024年Q1全公司产品线规模变动报告', time: '今天 10:00' }] }],
    '投管':    [{ title: '完整的产品图谱', links: ['数据中心'],
                  todos: [{ text: '全市场产品规模监控周报', time: '周一 09:00' }] }],
    '部门长':  [{ title: '部门负责的产品图谱', links: ['数据中心'],
                  todos: [{ text: '固收+部门新发产品目标设定审核', time: '明天 14:00' }] }],
    '投资经理':[{ title: '所负责产品系列的产品图谱', links: ['数据中心'],
                  todos: [{ text: '启航系列产品2024年收益目标确认', time: '今天 16:30' }] }],
    '投资助理':[{ title: '所负责产品系列的产品图谱', links: ['数据中心'],
                  todos: [{ text: '整理启航系列同业竞品分析数据', time: '今天 15:00' }] }],
  },
  2: {
    ALL: [
      { title: '市场跟踪', links: ['市场跟踪'],
        todos: [{ text: '阅读《3月宏观经济数据点评》', time: '今天 09:00' }] },
      { title: '投研小龙虾', links: ['ResearchBot'],
        todos: [{ text: '小龙虾已完成研究任务，请查看结果', time: '刚刚' }] },
    ],
    '投资经理':[{ title: '增加沙盘模拟', links: ['模型中心'],
                  todos: [{ text: '基于降准预期的长端利率沙盘模拟', time: '今天 11:00' }] }],
    '投资助理':[{ title: '增加沙盘模拟', links: ['模型中心'],
                  todos: [{ text: '准备降准情景下的模拟参数', time: '今天 10:30' }] }],
  },
  3: {
    '班子': [
      { title: '委员会投票', links: ['投委会决策'],
        todos: [
          { text: '[投委会填报] 请在 18:00 前完成 2026 Q2 资产配置问卷及定性观点提交', time: '今天 09:00' },
          { text: '混合投资委员会Q2会议投票', time: '今天 14:00' },
        ] },
      { title: '公司资配指引', links: ['投委会决策'],
        todos: [{ text: '签发2026年度公司大类资产配置指引', time: '周五 17:00' }] },
    ],
    '部门长': [
      { title: '委员会投票', links: ['投委会决策'],
        todos: [
          { text: '[投委会填报] 请在 18:00 前完成 2026 Q2 资产配置问卷及定性观点提交', time: '今天 09:00' },
          { text: '混合投资委员会Q2会议投票', time: '今天 14:00' },
        ] },
      { title: '部门资配指引', links: ['部门决策', '模型中心'],
        todos: [{ text: '固收部门Q2资产配置策略审批', time: '明天 10:00' }] },
    ],
    '投资经理': [
      { title: '委员会投票', links: ['投委会决策'],
        todos: [
          { text: '[会前准备] 请在 18:00 前完成投委会观点填报', time: '今天 09:00' },
        ] },
      { title: '形成产品层面目标组合', links: ['资配工作台'],
        todos: [{ text: '启航1号Q2目标组合权重设定', time: '今天 15:00' }] },
      { title: '模型应用', links: ['模型中心'],
        todos: [{ text: '运行BL模型优化目标组合', time: '今天 14:30' }] },
    ],
    '投管': [
      { title: '委员会配置', links: ['投委会决策'],
        todos: [{ text: '复核投委会Q1配置决议参数', time: '今天 16:00' }] },
      { title: '系统模型与约束', links: ['资配工作台', '模型中心'],
        todos: [{ text: '配置系统约束参数年度更新', time: '本周三 12:00' }] },
    ],
  },
  4: {
    '投资经理':[{ title: '资配工作台跳转试算模块', links: ['试算模块'],
                  todos: [{ text: '启航1号调仓方案A/B试算对比', time: '今天 16:00' }] }],
    '投资助理':[{ title: '资配工作台跳转试算模块', links: ['试算模块'],
                  todos: [{ text: '导出启航1号试算结果报告', time: '今天 16:30' }] }],
  },
  5: {
    '投资经理':[
      { title: '头寸、风控监控调整', links: ['指令系统', '交易系统', '风控系统'],
        todos: [{ text: '启航1号减持信用债头寸调整', time: '今天 14:30' }] },
      { title: '头寸与流动性救火', links: ['资配工作台'],
        todos: [
          { text: '⏰ 尾盘头寸告警：距闭市仅30分钟！3只产品正回购到期，现金透支，存在交收违约风险', time: '14:30 🔴' },
          { text: '⏳ 资金站岗应急：同业存单明日集中到期，预计释放闲置资金 3.2 亿', time: '今天' },
        ] },
    ],
    '投资助理':[
      { title: '指令系统下单', links: ['指令系统', '交易系统'],
        todos: [{ text: '录入启航1号调仓指令', time: '今天 13:00' }] },
      { title: '头寸风控监控调整', links: ['风控系统'],
        todos: [{ text: '检查稳健3号久期风控指标', time: '今天 15:00' }] },
    ],
  },
  6: {
    ALL: [{ title: '偏离分析', links: ['偏离监控模块'],
           todos: [{ text: '启航1号权益仓位偏离度告警处理', time: '今天 10:30' }] }],
    '投资经理': [
      { title: '合规红线纠偏', links: ['风控系统', '资配工作台'],
        todos: [{ text: '违规持仓：某地产债评级下调至 AA-，触发强平红线 (涉及 8 只产品)', time: '紧急' }] },
    ],
  },
  7: {
    ALL: [{ title: '绩效归因', links: ['组合分析系统'],
           todos: [{ text: '启航系列Q1绩效归因报告审阅', time: '下周一 10:00' }] }],
  },
};

const INVESTMENT_PROCESS = [
  { id: 1 as NodeId, label: '投资目标' },
  { id: 2 as NodeId, label: '研究分析' },
  { id: 3 as NodeId, label: '资产配置' },
  { id: 4 as NodeId, label: '组合试算' },
  { id: 5 as NodeId, label: '投资管理' },
  { id: 6 as NodeId, label: '定期再平衡' },
  { id: 7 as NodeId, label: '长期跟踪' },
];

const ALL_NAV_ITEMS = [
  { id: 'executive',         label: '高管驾驶舱', sceneName: '看全局',   icon: TrendCharts,    color: 'text-[#FF3B30]' },
  { id: 'terminal',          label: '资配工作台', sceneName: '我的资配',   icon: Monitor,        color: 'text-[#4D9DE0]' },
  { id: 'batch-simulator',   label: '调仓沙盘',   sceneName: '批量调仓',   icon: Operation,      color: 'text-[#FF9500]' },
  { id: 'committee',         label: '投委会决策', sceneName: '投委会投票',   icon: UserFilled,     color: 'text-[#FF9500]' },
  { id: 'dept-head',         label: '部门决策',   sceneName: '部门资配', icon: OfficeBuilding, color: 'text-[#34C759]' },
  { id: 'market',            label: '市场洞察',   sceneName: '看市场', icon: DataLine,       color: 'text-[#AF52DE]' },
  { id: 'model-center',      label: '模型中心',   sceneName: '用模型',   icon: EditPen,        color: 'text-[#FF3B30]' },
  { id: 'viewpoint',         label: '观点车间',   sceneName: '写观点',     icon: Files,          color: 'text-purple-400' },
  { id: 'factor',            label: '因子车间',   sceneName: '查因子',     icon: Histogram,      color: 'text-[#4D9DE0]' },
  { id: 'data-center',       label: '数据中心',   sceneName: '查数据',     icon: DataAnalysis,   color: 'text-[#CBD5E1]' },
  { id: 'portfolio-analysis',label: '组合分析',   sceneName: '看归因', icon: Histogram,      color: 'text-[#4D9DE0]' },
  { id: 'simulation',        label: '组合试算',   sceneName: '做试算',   icon: Odometer,       color: 'text-[#FF9500]' },
  { id: 'order-placement',   label: '指令下单',   sceneName: '下指令',   icon: Promotion,      color: 'text-[#34C759]' },
];

const EXTERNAL_NAV_IDS = new Set(['portfolio-analysis', 'simulation', 'order-placement']);

const PRODUCT_TREE = [
  { category: '固收中低波', items: [
    { id: 'p1', name: '启航9个月持有期1号', code: 'QH001' },
    { id: 'p2', name: '启航1年封闭A', code: 'QH002' },
    { id: 'p5', name: '启航6个月滚动', code: 'QH003' },
  ]},
  { category: '纯债', items: [
    { id: 'p3', name: '稳健增利3号', code: 'WJ003' },
  ]},
  { category: '偏债混合', items: [
    { id: 'p4', name: '远航混合精选', code: 'YH001' },
  ]},
];

const PORTFOLIO_META: Record<string, { name: string; color: string }> = {
  p1: { name: '启航1号',   color: '#FF3B30' },
  p2: { name: '启航封闭A', color: '#FF9500' },
  p3: { name: '稳健3号',   color: '#34C759' },
  p4: { name: '远航精选',  color: '#4D9DE0' },
  p5: { name: '启航滚动',  color: '#AF52DE' },
};

// ── Chart Mock Data ───────────────────────────────────────────────────────────
const MARKET_TREND_DATA = [
  { time: '09:30', val: 3500 }, { time: '10:00', val: 3512 }, { time: '10:30', val: 3508 },
  { time: '11:00', val: 3520 }, { time: '11:30', val: 3525 }, { time: '13:00', val: 3518 },
  { time: '14:00', val: 3530 }, { time: '15:00', val: 3542 },
];

const DEVIATION_DATA = [
  { name: '基准组合', value: 20, fill: '#A0A0A0' },
  { name: '目标组合', value: 22, fill: '#4D9DE0' },
  { name: '意向组合', value: 25, fill: '#FF9500' },
  { name: '实际组合', value: 24, fill: '#FF3B30' },
];

const PERFORMANCE_DATA = [
  { date: '2023-01', p1: 1.000, p2: 1.000, p3: 1.000, p4: 1.000, p5: 1.000 },
  { date: '2023-03', p1: 1.012, p2: 1.025, p3: 1.008, p4: 0.990, p5: 1.010 },
  { date: '2023-06', p1: 1.028, p2: 1.045, p3: 1.025, p4: 1.030, p5: 1.022 },
  { date: '2023-09', p1: 1.040, p2: 1.070, p3: 1.040, p4: 1.025, p5: 1.030 },
  { date: '2023-12', p1: 1.052, p2: 1.095, p3: 1.055, p4: 1.060, p5: 1.042 },
  { date: '2024-01', p1: 1.048, p2: 1.085, p3: 1.060, p4: 1.010, p5: 1.038 },
  { date: '2024-03', p1: 1.062, p2: 1.120, p3: 1.070, p4: 1.085, p5: 1.052 },
];

// ── State ─────────────────────────────────────────────────────────────────────
const fullScreenPanel   = ref<PanelId | null>(null);
const selectedProcessStep = ref<NodeId | null>(3);
const selectedPortfolios  = ref<string[]>(['p1']);
const tempSelectedPortfolios = ref<string[]>([]);
const isPortfolioModalOpen   = ref(false);
const externalLinkModal      = ref<string | null>(null);
const timeframe              = ref('3M');
const chatInput              = ref('');
const chatMessages           = ref<ChatMessage[]>([]);
const isEditingNav           = ref(false);
const navPage                = ref(0);
const customNavIds           = ref<string[]>([
  'executive','terminal','batch-simulator','committee','dept-head',
  'market','model-center','data-center','settings',
  'portfolio-analysis','simulation','order-placement',
]);
const chatContainerRef = ref<HTMLElement | null>(null);

// ── Toast state ───────────────────────────────────────────────────────────────
const showToast = ref(false);
const toastMsg  = ref('');
let   _toastTimer: ReturnType<typeof setTimeout> | null = null;

function _fireToast(msg: string) {
  toastMsg.value = msg;
  showToast.value = true;
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { showToast.value = false; }, 2800);
}

// ── Computed ──────────────────────────────────────────────────────────────────
const currentTasks = computed<Task[]>(() => {
  if (!selectedProcessStep.value) return [];
  const nodeData = roleProcessMatrix[selectedProcessStep.value];
  if (!nodeData) return [];
  const tasks: Task[] = [];
  if (nodeData.ALL) tasks.push(...nodeData.ALL);
  if (nodeData[activeRole.value]) tasks.push(...nodeData[activeRole.value]!);
  return tasks;
});

const stepLabel = computed(() =>
  INVESTMENT_PROCESS.find(s => s.id === selectedProcessStep.value)?.label ?? ''
);

// All tasks across ALL roles for the selected node (used as fallback when current role has no tasks)
const nodeAllTasks = computed<Task[]>(() => {
  if (!selectedProcessStep.value) return [];
  const nodeData = roleProcessMatrix[selectedProcessStep.value];
  if (!nodeData) return [];
  const seen = new Set<string>();
  const tasks: Task[] = [];
  for (const roleTasks of Object.values(nodeData)) {
    for (const t of (roleTasks as Task[])) {
      if (!seen.has(t.title)) { seen.add(t.title); tasks.push(t); }
    }
  }
  return tasks;
});

// iPhone-style badge counts per node (role-aware, updates reactively)
const nodeTodoCounts = computed(() => {
  const result: Partial<Record<NodeId, number>> = {};
  for (const step of INVESTMENT_PROCESS) {
    const nodeData = roleProcessMatrix[step.id];
    if (!nodeData) continue;
    const cnt =
      (nodeData.ALL?.length ?? 0) +
      ((nodeData[activeRole.value] as Task[] | undefined)?.length ?? 0);
    if (cnt > 0) result[step.id] = cnt;
  }
  return result;
});

const totalNavPages = computed(() => Math.max(1, Math.ceil(customNavIds.value.length / 9)));
const safeNavPage   = computed(() => Math.min(navPage.value, totalNavPages.value - 1));

const currentNavItems = computed(() => {
  const displayItems = customNavIds.value
    .map(id => ALL_NAV_ITEMS.find(item => item.id === id))
    .filter(Boolean) as typeof ALL_NAV_ITEMS;
  return displayItems.slice(safeNavPage.value * 9, (safeNavPage.value + 1) * 9);
});

const availableNavItems = computed(() =>
  ALL_NAV_ITEMS.filter(i => !customNavIds.value.includes(i.id))
);

// ── Chart Options ──────────────────────────────────────────────────────────────
const COMMON_TOOLTIP = {
  backgroundColor: '#1A1E2B',
  borderColor: '#2E3348',
  textStyle: { fontSize: 10, color: '#E5E5E5' },
};

const marketTrendOption = computed(() => ({
  backgroundColor: 'transparent',
  grid: { top: 4, right: 0, left: 0, bottom: 0 },
  xAxis: { type: 'category', data: MARKET_TREND_DATA.map(d => d.time), show: false },
  yAxis: { type: 'value', show: false, scale: true },
  series: [{
    type: 'line', smooth: true, symbol: 'none',
    data: MARKET_TREND_DATA.map(d => d.val),
    lineStyle: { color: '#FF3B30', width: 1.5 },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
      { offset: 0, color: 'rgba(255,59,48,0.3)' }, { offset: 1, color: 'rgba(255,59,48,0)' }
    ]}},
  }],
  tooltip: { trigger: 'axis', ...COMMON_TOOLTIP },
}));

const deviationOption = computed(() => ({
  backgroundColor: 'transparent',
  grid: { top: 10, right: 10, left: 0, bottom: 0, containLabel: true },
  xAxis: {
    type: 'category',
    data: DEVIATION_DATA.map(d => d.name),
    axisLine: { show: false }, axisTick: { show: false },
    axisLabel: { color: '#777', fontSize: 10 },
  },
  yAxis: {
    type: 'value',
    axisLine: { show: false }, axisTick: { show: false },
    axisLabel: { color: '#777', fontSize: 10, formatter: '{value}%' },
    splitLine: { lineStyle: { color: '#2E3348', type: 'dashed' } },
  },
  series: [{
    type: 'bar',
    data: DEVIATION_DATA.map(d => ({ value: d.value, itemStyle: { color: d.fill, borderRadius: [2, 2, 0, 0] } })),
  }],
  tooltip: { trigger: 'axis', ...COMMON_TOOLTIP, formatter: (p: any) => `${p[0].name}: ${p[0].value}%` },
}));

const performanceOption = computed(() => {
  const activePids = selectedPortfolios.value;
  const series = activePids.map(pid => ({
    name: PORTFOLIO_META[pid]?.name ?? pid,
    type: 'line',
    data: PERFORMANCE_DATA.map(d => (d as unknown as Record<string, number>)[pid]),
    symbol: 'none',
    lineStyle: { color: PORTFOLIO_META[pid]?.color ?? '#E5E5E5', width: 2 },
    smooth: false,
  }));
  return {
    backgroundColor: 'transparent',
    grid: { top: 5, right: 10, left: 0, bottom: 0, containLabel: true },
    xAxis: {
      type: 'category',
      data: PERFORMANCE_DATA.map(d => d.date),
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#777', fontSize: 10 },
    },
    yAxis: {
      type: 'value', scale: true,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#777', fontSize: 10, formatter: (v: number) => v.toFixed(3) },
      splitLine: { lineStyle: { color: '#2E3348', type: 'dashed' } },
    },
    legend: { textStyle: { color: '#777', fontSize: 10 }, icon: 'circle', itemWidth: 6 },
    series,
    tooltip: { trigger: 'axis', ...COMMON_TOOLTIP },
  };
});

// ── Methods ───────────────────────────────────────────────────────────────────
function toggleFullScreen(panel: PanelId) {
  fullScreenPanel.value = fullScreenPanel.value === panel ? null : panel;
}

function hasTasksForNode(nodeId: number): boolean {
  const nodeData = roleProcessMatrix[nodeId as NodeId];
  if (!nodeData) return false;
  return !!(nodeData.ALL?.length || (nodeData[activeRole.value] as Task[] | undefined)?.length);
}

function navItemById(id: string) {
  return ALL_NAV_ITEMS.find(i => i.id === id);
}

function handleNavClick(id: string, label: string) {
  if (EXTERNAL_NAV_IDS.has(id)) {
    externalLinkModal.value = label;
  } else {
    emit('navigate', id);
  }
}

// ── Link-label → tab-id routing for task-panel links ─────────────────────────
const LINK_ROUTES: Record<string, string | null> = {
  '数据中心':    'data-center',
  '市场跟踪':    'market',
  'ResearchBot': null,
  '模型中心':    'model-center',
  '投委会决策':  'committee',
  '部门决策':    'dept-head',
  '资配工作台':  'terminal',
  '试算模块':    'terminal',
  '指令系统':    null,
  '交易系统':    null,
  '风控系统':    null,
  '偏离监控模块': null,
  '组合分析系统': 'executive',
};

const KNOWN_TABS = new Set([
  'portal','executive','terminal','committee',
  'dept-head','market','model-center','data-center','settings',
  'batch-simulator',
]);

function handleLinkNavigate(linkLabel: string) {
  const target = LINK_ROUTES[linkLabel] ?? null;
  if (target && KNOWN_TABS.has(target)) {
    emit('navigate', target);
  } else {
    _fireToast('⚠️ 该模块建设中，敬请期待');
  }
}

function toggleNavId(id: string) {
  if (customNavIds.value.includes(id)) {
    customNavIds.value = customNavIds.value.filter(i => i !== id);
  } else {
    customNavIds.value = [...customNavIds.value, id];
  }
}

function moveNavItem(index: number, direction: number) {
  const newIds = [...customNavIds.value];
  const temp = newIds[index];
  newIds[index] = newIds[index + direction];
  newIds[index + direction] = temp;
  customNavIds.value = newIds;
}

function openPortfolioModal() {
  tempSelectedPortfolios.value = [...selectedPortfolios.value];
  isPortfolioModalOpen.value = true;
}

function confirmPortfolioSelection() {
  selectedPortfolios.value = [...tempSelectedPortfolios.value];
  isPortfolioModalOpen.value = false;
}

function toggleTempPortfolio(id: string) {
  tempSelectedPortfolios.value = tempSelectedPortfolios.value.includes(id)
    ? tempSelectedPortfolios.value.filter(p => p !== id)
    : [...tempSelectedPortfolios.value, id];
}

function isCategoryFullySelected(category: typeof PRODUCT_TREE[0]) {
  return category.items.every(i => tempSelectedPortfolios.value.includes(i.id));
}
function isCategoryPartiallySelected(category: typeof PRODUCT_TREE[0]) {
  return category.items.some(i => tempSelectedPortfolios.value.includes(i.id)) && !isCategoryFullySelected(category);
}
function toggleCategorySelection(category: typeof PRODUCT_TREE[0]) {
  const ids = category.items.map(i => i.id);
  if (isCategoryFullySelected(category)) {
    tempSelectedPortfolios.value = tempSelectedPortfolios.value.filter(id => !ids.includes(id));
  } else {
    const next = new Set([...tempSelectedPortfolios.value, ...ids]);
    tempSelectedPortfolios.value = Array.from(next);
  }
}

function handleSendMessage(text?: string) {
  const msg = (text ?? chatInput.value).trim();
  if (!msg) return;

  chatMessages.value.push({ id: Date.now().toString(), role: 'user', text: msg });
  chatInput.value = '';

  setTimeout(() => {
    let reply: ChatMessage = { id: String(Date.now() + 1), role: 'ai', text: '' };

    if (msg.includes('报表') || msg.includes('拉取') || msg.includes('数据') || msg.includes('对比')) {
      reply = { ...reply,
        prefixLabel: '[意图识别] 正在呼叫【理财有数】...',
        prefixClass: 'text-[#4D9DE0] bg-[#4D9DE0]/10 border-[#4D9DE0]/20',
        text: '已为您生成所需的数据视图，请点击下方链接查看详细数据面板。',
        actionType: 'data',
      };
    } else if (msg.includes('小龙虾') || msg.includes('研究')) {
      reply = { ...reply,
        prefixLabel: '[意图识别] 正在呼叫【投研小龙虾】...',
        prefixClass: 'text-[#AF52DE] bg-[#AF52DE]/10 border-[#AF52DE]/20',
        text: '已将研究任务派发给投研小龙虾 (ResearchBot)，完成后将通过待办事项提醒您。',
        actionType: 'bot',
      };
    } else if (msg.includes('沙盘') || msg.includes('模拟')) {
      reply = { ...reply,
        prefixLabel: '[意图识别] 正在呼叫【模型中心】...',
        prefixClass: 'text-[#FF9500] bg-[#FF9500]/10 border-[#FF9500]/20',
        text: '已为您准备好沙盘模拟环境，请前往模型中心配置参数。',
        actionType: 'model',
      };
    } else {
      const agentMatch = AGENTS.find(a => msg.includes(a));
      const agentName = agentMatch ?? '数字员工';
      reply = { ...reply,
        prefixLabel: `[意图识别] 已为您唤起【${agentName}】...`,
        prefixClass: 'text-[#34C759] bg-[#34C759]/10 border-[#34C759]/20',
        text: '正在为您执行复杂任务处理，预计需要 1-2 分钟，完成后将通过系统消息通知您。',
        actionType: 'agent',
        agentName,
      };
    }

    chatMessages.value.push(reply);
    nextTick(() => {
      if (chatContainerRef.value) {
        chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight;
      }
    });
  }, 800);
}

</script>
