<template>
  <div class="flex overflow-hidden bg-[#161922] font-mono text-[11px] text-[#E8ECF4]" style="height: calc(100vh - 64px)">

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- LEFT: Task Inbox & Drafts  (~25%)                     -->
    <!-- ══════════════════════════════════════════════════════ -->
    <div class="w-[252px] shrink-0 flex flex-col bg-[#1A1E2B] border-r border-[#2E3348]">

      <!-- Panel Header with Mode Switcher -->
      <div class="shrink-0 border-b border-[#2E3348]">
        <div class="flex items-center px-3 py-2 gap-2">
          <div class="am-title-bar"></div>
          <span class="text-xs font-bold tracking-wider text-[#E8ECF4]">任务篮 & 草稿</span>
          <span class="ml-auto shrink-0 text-[10px] text-[#555E75] bg-[#161922] border border-[#2E3348] px-1.5 py-1 rounded">INBOX</span>
        </div>
        <!-- Mode Switcher -->
        <div class="flex items-center px-3 pb-2 gap-1.5">
          <button
            @click="operationMode = 'single'"
            :class="cn('text-xs px-2 py-1 rounded border transition-colors',
              operationMode === 'single'
                ? 'bg-[#3B9EFF]/15 text-[#3B9EFF] border-[#3B9EFF]/30'
                : 'bg-[#161922] text-[#94A3B8] border-[#2E3348] hover:border-[#3B9EFF]/30')"
          >
            单组合: {{ singleProductLabel }}
          </button>
          <button
            @click="operationMode = 'batch'"
            :class="cn('text-xs px-2 py-1 rounded border transition-colors',
              operationMode === 'batch'
                ? 'bg-[#3B9EFF]/15 text-[#3B9EFF] border-[#3B9EFF]/30'
                : 'bg-[#161922] text-[#94A3B8] border-[#2E3348] hover:border-[#3B9EFF]/30')"
          >
            批量调仓
          </button>
          <select
            v-if="operationMode === 'single'"
            v-model="selectedSingleProduct"
            class="ml-auto h-6 bg-[#0E1118] border border-[#2E3348] hover:border-[#3B9EFF]/40 rounded text-xs text-[#E8ECF4] px-1.5 outline-none cursor-pointer transition-colors max-w-[100px]"
          >
            <option v-for="p in products" :key="p.id" :value="p.id" class="bg-[#161922]">{{ p.name }}</option>
          </select>
        </div>
      </div>

      <!-- Three-Axe Toolbar -->
      <div class="shrink-0 px-3 py-2 border-b border-[#2E3348] bg-[#0E1118] space-y-1.5">
        <div class="text-[10px] text-[#555E75] uppercase tracking-widest font-bold">操作工具</div>
        <div class="flex gap-1.5">
          <button
            @click="navigateToModelCenter"
            class="flex-1 text-xs bg-[#2A2E3D] hover:bg-[#2E3348] text-[#3B9EFF] border border-[#3B9EFF]/25 hover:border-[#3B9EFF]/50 px-2 py-1.5 rounded flex items-center justify-center gap-1.5 transition-colors"
          >
            <Cpu class="w-3 h-3" /> 调用模型
          </button>
          <button
            @click="handleExcelImport"
            class="flex-1 text-xs bg-[#0A2218] hover:bg-[#0D2216] border border-[#00C9A7]/25 hover:border-[#00C9A7]/50 text-[#00C9A7] px-2 py-1.5 rounded flex items-center justify-center gap-1.5 transition-colors"
          >
            <Download class="w-3 h-3" /> 导入持仓
          </button>
          <button
            @click="openAssetDialog"
            class="flex-1 text-xs bg-[#2A2E3D] hover:bg-[#2E3348] text-[#E8ECF4] border border-[#2E3348] hover:border-[#3E4660] px-2 py-1.5 rounded flex items-center justify-center gap-1.5 transition-colors"
          >
            <Plus class="w-3 h-3" /> 添加标的
          </button>
        </div>
      </div>

      <!-- Tab Switcher -->
      <div class="flex shrink-0 border-b border-[#2E3348]">
        <button
          v-for="tab in (['inbox', 'drafts'] as const)" :key="tab"
          @click="leftTab = tab"
          :class="[
            'flex-1 py-2 transition-colors text-[11px]',
            leftTab === tab
              ? 'text-[#3B9EFF] border-b-2 border-[#3B9EFF] bg-[#3B9EFF]/5'
              : 'text-[#555E75] hover:text-[#8B93A8]'
          ]"
        >
          {{ tab === 'inbox' ? '待办任务' : '我的草稿' }}
          <span v-if="tab === 'inbox'" class="ml-1 text-[10px] text-red-400 bg-red-400/10 px-1 rounded">{{ inboxTasks.length }}</span>
        </button>
      </div>

      <!-- Task Target Progress Bar -->
      <div class="shrink-0 px-3 py-2 border-b border-[#2E3348] bg-[#1A1E2B]">
        <div class="flex items-center justify-between mb-1.5">
          <span class="text-xs text-[#94A3B8]">任务目标进度</span>
          <span :class="cn('text-xs font-mono tabular-nums font-bold', isTargetMet ? 'text-[#00C9A7]' : 'text-[#FFAB00]')">
            {{ plannedAmount.toFixed(0) }}<span class="text-[#64748B]"> / {{ targetAmount.toFixed(0) }} 万</span>
          </span>
        </div>
        <div class="h-2 bg-[#161922] rounded-full overflow-hidden">
          <div
            :class="cn('h-full rounded-full transition-all duration-700',
              isTargetMet ? 'bg-[#00C9A7]' : 'bg-[#FFAB00]')"
            :style="{ width: progressPct + '%' }"
          ></div>
        </div>
        <div v-if="!isTargetMet && targetAmount > 0" class="mt-1.5 flex items-center gap-1">
          <WarningFilled class="w-3 h-3 text-[#FFAB00] shrink-0" />
          <span class="text-xs text-[#FFAB00]">尚未凑齐目标金额，差额 {{ (targetAmount - plannedAmount).toFixed(0) }} 万</span>
        </div>
        <div v-else-if="targetAmount > 0" class="mt-1.5 flex items-center gap-1">
          <CircleCheckFilled class="w-3 h-3 text-[#00C9A7] shrink-0" />
          <span class="text-xs text-[#00C9A7]">目标金额已凑齐</span>
        </div>
        <div v-else class="mt-1">
          <span class="text-xs text-[#64748B]">暂无再平衡目标</span>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-y-auto no-scrollbar p-2 space-y-1.5">

        <!-- INBOX -->
        <template v-if="leftTab === 'inbox'">
          <div
            v-for="task in inboxTasks" :key="task.id"
            @click="selectedTaskId = task.id"
            :class="[
              'p-2 rounded border cursor-pointer transition-all',
              selectedTaskId === task.id
                ? 'border-[#3B9EFF]/40 bg-[#3B9EFF]/8'
                : 'border-[#2E3348] hover:border-[#3E4660] bg-[#161922]'
            ]"
          >
            <div class="flex items-start gap-1.5">
              <div class="w-1.5 h-1.5 rounded-full shrink-0 mt-1.5" :class="task.urgent ? 'bg-red-500' : 'bg-[#FF9500]'"></div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-1">
                  <span :class="['font-semibold truncate', task.urgent ? 'text-red-300' : 'text-[#E8ECF4]']">
                    {{ task.title }}
                  </span>
                  <span :class="[
                    'shrink-0 text-[10px] px-1 py-px rounded border',
                    task.urgent
                      ? 'text-red-400 border-red-400/30 bg-red-400/8'
                      : 'text-[#FF9500] border-[#FF9500]/30 bg-[#FF9500]/8'
                  ]">{{ task.urgent ? '紧急' : '普通' }}</span>
                </div>
                <p class="text-[#8B93A8] mt-0.5 leading-relaxed line-clamp-2">{{ task.subtitle }}</p>
                <div class="flex items-center gap-1.5 mt-1.5">
                  <span class="text-[10px] text-[#555E75] bg-[#2E3348] px-1.5 py-1 rounded">涉{{ task.affected }}只产品</span>
                  <span class="text-[10px] text-[#555E75] font-mono">{{ task.time }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- DRAFTS -->
        <template v-else>
          <div
            v-for="draft in draftSchemes" :key="draft.id"
            @click="activeDraftId = draft.id"
            :class="[
              'p-2 rounded border cursor-pointer transition-all',
              activeDraftId === draft.id
                ? 'border-[#FF9500]/50 bg-[#FF9500]/6'
                : 'border-[#2E3348] hover:border-[#3E4660] bg-[#161922]'
            ]"
          >
            <div class="flex items-center justify-between gap-1">
              <span :class="['font-semibold truncate', activeDraftId === draft.id ? 'text-[#FF9500]' : 'text-[#E8ECF4]']">
                {{ draft.label }}
              </span>
              <span class="shrink-0 text-[10px] text-[#555E75] font-mono">{{ draft.timestamp }}</span>
            </div>
            <p class="text-[#8B93A8] mt-0.5 line-clamp-1">{{ draft.desc }}</p>
            <div class="flex items-center gap-2 mt-1.5">
              <span class="text-[10px] text-[#555E75] bg-[#2E3348] px-1.5 py-1 rounded">{{ draft.count }}只产品</span>
              <span :class="['text-[10px] font-mono font-semibold', draft.delta >= 0 ? 'text-green-400' : 'text-red-400']">
                预估{{ draft.delta >= 0 ? '+' : '' }}{{ draft.delta }}bp
              </span>
            </div>
          </div>

          <!-- New Draft -->
          <button
            @click="addDraft"
            class="w-full flex items-center justify-center gap-1.5 py-2 rounded border border-dashed border-[#2E3348] text-[#555E75] hover:border-[#3B9EFF]/50 hover:text-[#3B9EFF] transition-all"
          >
            <Plus class="w-3 h-3" />
            <span>新建草稿方案</span>
          </button>
        </template>

      </div>

      <!-- Left Footer -->
      <div class="shrink-0 border-t border-[#2E3348] px-3 py-2 bg-[#161922] space-y-1">
        <div class="flex items-center justify-between text-[#555E75]">
          <span>当前草稿</span>
          <span class="text-[#FF9500] font-semibold truncate max-w-[110px]">{{ activeDraft?.label ?? '—' }}</span>
        </div>
        <div class="flex items-center justify-between text-[#555E75]">
          <span>关联任务</span>
          <span :class="['truncate max-w-[110px]', selectedTask ? 'text-red-400' : 'text-[#555E75]']">
            {{ selectedTask?.title ?? '未选择' }}
          </span>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- MIDDLE: Workspace  (~50%)                             -->
    <!-- ══════════════════════════════════════════════════════ -->
    <div class="flex-1 flex flex-col min-w-0 border-r border-[#2E3348]">

      <!-- Middle Header -->
      <div class="h-10 flex items-center px-3 border-b border-[#2E3348] shrink-0 gap-2.5">
        <span class="text-xs font-bold tracking-wider text-[#E8ECF4]">调仓矩阵</span>
        <span class="text-[10px] text-[#555E75] font-mono bg-[#161922] border border-[#2E3348] px-1.5 py-1 rounded">
          {{ activeDraft?.label ?? '未命名草稿' }}
        </span>

        <!-- Scene Switcher -->
        <div class="flex items-center gap-1 ml-2 border border-[#2E3348] rounded overflow-hidden">
          <button
            @click="operationScene = '调仓'"
            :class="cn('text-xs px-2 py-1 transition-colors',
              operationScene === '调仓' ? 'bg-[#3B9EFF]/20 text-[#3B9EFF]' : 'bg-[#161922] text-[#94A3B8] hover:bg-[#1E2333]')"
          >组合调仓</button>
          <button
            @click="operationScene = '建仓'"
            :class="cn('text-xs px-2 py-1 transition-colors',
              operationScene === '建仓' ? 'bg-[#00C9A7]/20 text-[#00C9A7]' : 'bg-[#161922] text-[#94A3B8] hover:bg-[#1E2333]')"
          >新发建仓</button>
        </div>
        <span v-if="operationScene === '建仓'" class="text-xs text-[#00C9A7] bg-[#00C9A7]/10 border border-[#00C9A7]/20 px-1.5 py-px rounded">
          建仓模式 · 目标 {{ productTotalScale.toLocaleString() }} 万
        </span>

        <!-- Batch Context Banner (from TerminalDashboard) -->
        <div v-if="batchCtx" class="flex items-center gap-1.5 ml-2 text-[10px] font-mono">
          <span class="text-[#D89614]">{{ batchCtx.taskIcon }}</span>
          <span class="text-[#94A3B8]">来源:</span>
          <span class="text-[#D89614] font-bold">{{ batchCtx.sourcePackLabel }}</span>
          <span class="text-[#64748B]">·</span>
          <span class="text-[#94A3B8]">{{ batchCtx.productCount }} 只产品</span>
          <span class="text-[#64748B]">·</span>
          <span class="text-[#3B9EFF]">{{ batchCtx.taskTag }}</span>
        </div>

        <div class="ml-auto flex items-center gap-3 text-[#555E75]">
          <span>产品 <span class="text-[#E8ECF4] font-semibold">{{ products.length }}只</span></span>
          <div class="w-px h-3 bg-[#2E3348]"></div>
          <span>调仓净额
            <span :class="['font-semibold font-mono ml-1', totalDelta >= 0 ? 'text-green-400' : 'text-red-400']">
              {{ totalDelta >= 0 ? '+' : '' }}{{ totalDelta.toLocaleString('zh-CN', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) }}万
            </span>
          </span>
          <div class="w-px h-3 bg-[#2E3348]"></div>
          <span>拦截 <span :class="['font-semibold', flaggedCount > 0 ? 'text-red-400' : 'text-green-400']">{{ flaggedCount }}笔</span></span>
        </div>
      </div>

      <!-- Unified Strategy & Model Engine Bar -->
      <div class="shrink-0 border-b border-[#2E3348] bg-[#161922]">
        <div class="flex items-center gap-2 px-3 py-2">
          <div class="flex items-center gap-1.5 shrink-0">
            <div class="am-title-bar"></div>
            <span class="text-xs font-bold text-[#E8ECF4]">策略与模型引擎</span>
          </div>
          <div class="w-px h-4 bg-[#2E3348] shrink-0"></div>
          <select
            v-model="mergedEngineMode"
            class="h-6 bg-[#0E1118] border border-[#2E3348] hover:border-[#3B9EFF]/40 rounded text-[11px] text-[#E8ECF4] px-2 outline-none cursor-pointer transition-colors"
          >
            <optgroup label="基础分配规则" class="bg-[#161922]">
              <option value="proportional" class="bg-[#161922]">等比分摊</option>
              <option value="target" class="bg-[#161922]">目标对齐</option>
              <option value="concentration" class="bg-[#161922]">资产浓度控制</option>
            </optgroup>
            <optgroup label="复杂策略模型" class="bg-[#161922]">
              <option value="quant-override" class="bg-[#161922]">量化资配模型</option>
            </optgroup>
          </select>

          <template v-if="mergedEngineMode === 'proportional' || mergedEngineMode === 'target'">
            <div class="flex items-center gap-1 shrink-0">
              <span class="text-[10px] text-[#64748B]">调仓总金额</span>
              <input
                v-model.number="allocAmount"
                type="number"
                placeholder="万元"
                class="h-6 w-24 bg-[#0E1118] border border-[#2E3348] hover:border-[#3B9EFF]/40 focus:border-[#3B9EFF] rounded text-[11px] text-[#E8ECF4] px-2 outline-none transition-colors text-right font-mono"
              />
              <span class="text-[10px] text-[#64748B]">万</span>
            </div>
            <button
              @click="applyAllocation"
              class="h-6 px-3 bg-[#3B9EFF]/15 border border-[#3B9EFF]/35 rounded text-[#3B9EFF] hover:bg-[#3B9EFF]/25 hover:border-[#3B9EFF]/60 transition-colors shrink-0 font-semibold text-[11px]"
            >执行分配</button>
          </template>

          <template v-else-if="mergedEngineMode === 'concentration'">
            <div class="flex items-center gap-1 shrink-0">
              <span class="text-[10px] text-[#64748B]">目标标的</span>
              <select
                v-model="concentrationTarget"
                class="h-6 bg-[#0E1118] border border-[#2E3348] hover:border-[#3B9EFF]/40 rounded text-[11px] text-[#E8ECF4] px-1.5 outline-none cursor-pointer transition-colors"
              >
                <option v-for="p in products" :key="p.id" :value="p.id" class="bg-[#161922]">{{ p.name }}</option>
              </select>
            </div>
            <div class="flex items-center gap-1 shrink-0">
              <span class="text-[10px] text-[#64748B]">目标浓度</span>
              <input
                v-model.number="allocTarget"
                type="number"
                placeholder="%"
                class="h-6 w-16 bg-[#0E1118] border border-[#2E3348] hover:border-[#3B9EFF]/40 focus:border-[#3B9EFF] rounded text-[11px] text-[#E8ECF4] px-2 outline-none transition-colors text-right font-mono"
              />
              <span class="text-[10px] text-[#64748B]">%</span>
            </div>
            <button
              @click="applyAllocation"
              class="h-6 px-3 bg-[#3B9EFF]/15 border border-[#3B9EFF]/35 rounded text-[#3B9EFF] hover:bg-[#3B9EFF]/25 hover:border-[#3B9EFF]/60 transition-colors shrink-0 font-semibold text-[11px]"
            >执行分配</button>
          </template>

          <template v-else-if="mergedEngineMode === 'quant-override'">
            <button
              @click="executeQuantModel"
              class="h-6 px-3 bg-transparent border border-[#AF52DE]/30 rounded text-[#AF52DE]/70 hover:text-[#AF52DE] hover:border-[#AF52DE]/60 hover:bg-[#AF52DE]/5 transition-colors shrink-0 text-[11px] font-mono flex items-center gap-1"
            >
              跳转模型中心配置参数 <span class="group-hover:translate-x-px inline-block transition-transform">↗</span>
            </button>
            <span class="text-[10px] font-mono text-[#FFAB00]/60 bg-[#FFAB00]/5 border border-[#FFAB00]/10 px-2 py-1 rounded">将覆盖当前所有产品草稿数据</span>
          </template>

          <button
            @click="resetAllocation"
            title="重置调仓后金额"
            class="ml-auto h-6 w-6 flex items-center justify-center bg-[#0E1118] border border-[#2E3348] rounded text-[#555E75] hover:text-[#8B93A8] hover:border-[#3E4660] transition-colors shrink-0"
          >
            <Refresh class="w-3 h-3" />
          </button>
        </div>

        <!-- Model Result (shown after quant model execution) -->
        <div v-if="sandboxModelResult.length > 0" class="px-3 pb-2">
          <div class="bg-[#0E1118] border border-[#AF52DE]/20 rounded p-2 space-y-1">
            <div class="text-[10px] font-mono text-[#AF52DE]/70 uppercase tracking-widest mb-1">模型执行结果</div>
            <div v-for="(row, i) in sandboxModelResult" :key="i" class="flex justify-between items-center text-[10px] font-mono">
              <span class="text-[#94A3B8]">{{ row.name }}</span>
              <div class="flex items-center gap-2">
                <span class="text-[#E8ECF4] font-bold">{{ row.value }}</span>
                <span v-if="row.change" :class="row.change.startsWith('+') ? 'text-[#34C759]' : row.change.startsWith('-') ? 'text-[#F04864]' : 'text-[#94A3B8]'">{{ row.change }}</span>
              </div>
            </div>
            <button @click="sandboxModelResult = []" class="mt-1 text-[10px] font-mono text-[#64748B] hover:text-[#94A3B8] transition-colors">关闭结果</button>
          </div>
        </div>
      </div>

      <!-- TreeGrid -->
      <div class="flex-1 overflow-y-auto no-scrollbar">
        <table class="w-full border-collapse table-fixed">

          <!-- Table Head -->
          <thead class="sticky top-0 z-10">
            <tr class="bg-[#1A1E2B] border-b border-[#2E3348]">
              <th class="text-left px-2.5 py-1.5 text-[#555E75] font-medium w-[32%]">
                <span class="font-mono uppercase tracking-wider text-[10px]">产品名称</span>
              </th>
              <th class="text-right px-2 py-1.5 text-[#555E75] font-medium w-[14%]">
                <span class="font-mono uppercase tracking-wider text-[10px]">调仓前 (万)</span>
              </th>
              <th class="text-right px-2 py-1.5 text-[#555E75] font-medium w-[15%]">
                <span class="font-mono uppercase tracking-wider text-[10px]">调仓后 (万)</span>
              </th>
              <th class="text-right px-2 py-1.5 text-[#555E75] font-medium w-[13%]">
                <span class="font-mono uppercase tracking-wider text-[10px]">T+0 现金</span>
              </th>
              <th class="text-right px-2 py-1.5 text-[#555E75] font-medium w-[12%]">
                <span class="font-mono uppercase tracking-wider text-[10px]">偏离度</span>
              </th>
              <th class="text-center px-2 py-1.5 text-[#555E75] font-medium w-[14%]">
                <span class="font-mono uppercase tracking-wider text-[10px]">状态</span>
              </th>
            </tr>
          </thead>

          <tbody>
            <template v-for="p in products" :key="p.id">

              <!-- ── Product Row ── -->
              <tr
                :class="[
                  'border-b border-[#2E3348]/60 transition-colors group cursor-pointer',
                  p.flagged
                    ? 'bg-red-500/5 hover:bg-red-500/8'
                    : selectedProductId === p.id
                      ? 'bg-[#3B9EFF]/5 hover:bg-[#3B9EFF]/8'
                      : 'hover:bg-[#1A1E2B]/70'
                ]"
                @click="selectedProductId = p.id"
              >
                <!-- Name + expand -->
                <td class="px-2.5 py-1.5">
                  <div class="flex items-center gap-1.5">
                    <button
                      @click.stop="p.expanded = !p.expanded"
                      class="w-3.5 h-3.5 flex items-center justify-center text-[#555E75] hover:text-[#3B9EFF] transition-colors shrink-0"
                    >
                      <ArrowRight v-if="!p.expanded" class="w-2.5 h-2.5" />
                      <ArrowDown v-else class="w-2.5 h-2.5 text-[#3B9EFF]" />
                    </button>
                    <span :class="['font-semibold truncate', p.flagged ? 'text-red-300' : 'text-[#E8ECF4]']">
                      {{ p.name }}
                    </span>
                    <span class="text-[10px] text-[#555E75] font-mono shrink-0">{{ p.code }}</span>
                  </div>
                </td>

                <!-- Before -->
                <td class="px-2 py-1.5 text-right font-mono text-[#8B93A8]">
                  {{ p.beforeAmt.toLocaleString('zh-CN', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) }}
                </td>

                <!-- After (inline-editable) -->
                <td
                  class="px-2 py-1.5 text-right"
                  @click.stop="startEdit(p.id, 'afterAmt')"
                >
                  <div class="flex items-center justify-end gap-1">
                    <input
                      v-if="editingCell?.productId === p.id && editingCell.field === 'afterAmt'"
                      v-model.number="p.afterAmt"
                      type="number"
                      autofocus
                      @blur="stopEdit"
                      @keydown.enter="stopEdit"
                      @keydown.escape="stopEdit"
                      @click.stop
                      class="w-20 text-right bg-[#161922] border border-[#3B9EFF]/60 rounded px-1 text-[#3B9EFF] outline-none font-mono text-[11px]"
                    />
                    <template v-else>
                      <span :class="[
                        'font-mono cursor-text transition-colors',
                        p.afterAmt > p.beforeAmt ? 'text-green-400' : p.afterAmt < p.beforeAmt ? 'text-red-400' : 'text-[#E8ECF4]'
                      ]">
                        {{ p.afterAmt.toLocaleString('zh-CN', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) }}
                      </span>
                      <EditPen class="w-2.5 h-2.5 text-[#555E75] opacity-0 group-hover:opacity-60 transition-opacity shrink-0" />
                    </template>
                  </div>
                </td>

                <!-- Cash -->
                <td class="px-2 py-1.5 text-right font-mono text-[#8B93A8]">
                  {{ p.cash.toLocaleString('zh-CN', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) }}
                </td>

                <!-- Deviation -->
                <td class="px-2 py-1.5 text-right font-mono">
                  <span :class="[
                    Math.abs(p.deviation) > 3
                      ? 'text-red-400'
                      : Math.abs(p.deviation) > 1.5
                        ? 'text-[#FF9500]'
                        : 'text-green-400'
                  ]">
                    {{ p.deviation > 0 ? '+' : '' }}{{ p.deviation.toFixed(2) }}%
                  </span>
                </td>

                <!-- Status badge -->
                <td class="px-2 py-1.5 text-center">
                  <span
                    v-if="p.flagged"
                    class="inline-flex items-center gap-0.5 text-[10px] text-red-400 bg-red-400/10 border border-red-400/25 px-1.5 py-1 rounded"
                  >
                    <WarningFilled class="w-2 h-2" /> 拦截
                  </span>
                  <span
                    v-else
                    class="inline-flex items-center gap-0.5 text-[10px] text-green-400 bg-green-400/10 border border-green-400/25 px-1.5 py-1 rounded"
                  >
                    <CircleCheckFilled class="w-2 h-2" /> 正常
                  </span>
                </td>
              </tr>

              <!-- ── Bond Detail Rows ── -->
              <template v-if="p.expanded">
                <tr
                  v-for="(bond, bidx) in p.bonds"
                  :key="`${p.id}-b${bidx}`"
                  :class="['border-b border-[#252A3A]/50 text-[10px]', bond.flagged ? 'bg-red-900/10' : 'bg-[#161922]/60']"
                >
                  <td class="px-2.5 py-1">
                    <div class="flex items-center gap-1.5 pl-6">
                      <span class="text-[#3E4660] select-none">└</span>
                      <span :class="['truncate', bond.flagged ? 'text-red-300/70' : 'text-[#8B93A8]']">
                        {{ bond.name }}
                      </span>
                      <span class="text-[10px] text-[#555E75] font-mono shrink-0">{{ bond.code }}</span>
                    </div>
                  </td>
                  <td class="px-2 py-1 text-right font-mono text-[#555E75]">{{ bond.before.toLocaleString() }}</td>
                  <td class="px-2 py-1 text-right font-mono text-[#555E75]">{{ bond.after.toLocaleString() }}</td>
                  <td class="px-2 py-1 text-right font-mono text-[#555E75]">—</td>
                  <td class="px-2 py-1 text-right font-mono">
                    <span :class="bond.change > 0 ? 'text-green-400/70' : bond.change < 0 ? 'text-red-400/70' : 'text-[#555E75]'">
                      {{ bond.change > 0 ? '+' : '' }}{{ bond.change.toLocaleString() }}
                    </span>
                  </td>
                  <td class="px-2 py-1 text-center">
                    <span v-if="bond.flagged" class="text-[10px] text-red-400/70 border border-red-400/20 px-1 rounded">久期越限</span>
                  </td>
                </tr>
              </template>

            </template>
          </tbody>

          <!-- Totals Footer -->
          <tfoot>
            <tr class="bg-[#1A1E2B] border-t-2 border-[#2E3348]">
              <td class="px-2.5 py-2 text-[#8B93A8] font-semibold">
                合计 <span class="text-[#555E75]">({{ products.length }}只产品)</span>
              </td>
              <td class="px-2 py-2 text-right font-mono text-[#8B93A8]">
                {{ totalBefore.toLocaleString('zh-CN', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) }}
              </td>
              <td class="px-2 py-2 text-right font-mono">
                <span :class="totalAfter > totalBefore ? 'text-green-400 font-semibold' : totalAfter < totalBefore ? 'text-red-400 font-semibold' : 'text-[#E8ECF4]'">
                  {{ totalAfter.toLocaleString('zh-CN', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) }}
                </span>
              </td>
              <td class="px-2 py-2 text-right font-mono text-[#8B93A8]">
                {{ totalCash.toLocaleString('zh-CN', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) }}
              </td>
              <td class="px-2 py-2 text-right font-mono text-[#555E75]">—</td>
              <td class="px-2 py-2 text-center">
                <span v-if="flaggedCount > 0" class="text-[10px] text-red-400 font-semibold">{{ flaggedCount }}笔拦截</span>
                <span v-else class="text-[10px] text-green-400">全部正常</span>
              </td>
            </tr>
          </tfoot>

        </table>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════ -->
    <!-- RIGHT: Context & Service Hub  (~25%)                  -->
    <!-- ══════════════════════════════════════════════════════ -->
    <div class="w-[272px] shrink-0 flex flex-col bg-[#1A1E2B]">

      <!-- Right Header -->
      <div class="h-10 flex items-center px-3 border-b border-[#2E3348] shrink-0 gap-2">
        <div class="am-title-bar"></div>
        <span class="text-xs font-bold tracking-wider text-[#E8ECF4]">决策上下文</span>
        <span class="ml-auto shrink-0 text-[10px] text-[#555E75] bg-[#161922] border border-[#2E3348] px-1.5 py-1 rounded">CONTEXT</span>
      </div>

      <!-- TAA Targets -->
      <div class="shrink-0 p-3 border-b border-[#2E3348] space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-[10px] text-[#555E75] uppercase tracking-widest">TAA 目标要求</span>
          <span :class="[
            'text-[10px] border px-1 rounded font-mono',
            selectedTask ? 'text-[#AF52DE] border-[#AF52DE]/30 bg-[#AF52DE]/5' : 'text-[#555E75] border-[#2E3348]'
          ]">{{ selectedTask ? 'LINKED' : 'DEFAULT' }}</span>
        </div>

        <div class="bg-[#161922] rounded border border-[#2E3348] p-2 space-y-1.5">
          <div v-for="t in contextTAATargets" :key="t.label" class="flex items-center justify-between">
            <span class="text-[#8B93A8] truncate mr-2">{{ t.label }}</span>
            <div class="flex items-center gap-1 shrink-0">
              <span class="font-mono text-[#555E75] text-[10px]">{{ t.current }}</span>
              <span class="text-[#3E4660]">→</span>
              <span :class="[
                'font-mono font-semibold',
                t.status === 'ok' ? 'text-green-400' : t.status === 'warn' ? 'text-[#FF9500]' : 'text-red-400'
              ]">{{ t.target }}</span>
            </div>
          </div>
        </div>

        <!-- Position Water Levels -->
        <div class="space-y-1.5">
          <span class="text-[10px] text-[#555E75] uppercase tracking-widest">头寸水位</span>
          <div class="space-y-2">
            <div v-for="pos in positionLevels" :key="pos.label">
              <div class="flex justify-between mb-0.5">
                <span class="text-[#8B93A8]">{{ pos.label }}</span>
                <span :class="['font-mono text-[10px]', pos.level > pos.limit * 0.95 ? 'text-red-400' : pos.level > pos.limit * 0.85 ? 'text-[#FF9500]' : 'text-[#E8ECF4]']">
                  {{ pos.level }}<span class="text-[#555E75]">/{{ pos.limit }}</span>
                  <span class="text-[#555E75]">{{ pos.unit }}</span>
                </span>
              </div>
              <div class="h-1 bg-[#161922] rounded-full overflow-hidden">
                <div
                  :class="[
                    'h-full rounded-full transition-all duration-500',
                    pos.level > pos.limit * 0.95 ? 'bg-red-500' : pos.level > pos.limit * 0.85 ? 'bg-[#FF9500]' : 'bg-[#3B9EFF]'
                  ]"
                  :style="{ width: Math.min(100, (pos.level / pos.limit) * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Service Hub -->
      <div class="flex-1 overflow-y-auto no-scrollbar p-3 flex flex-col gap-2.5">

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <div class="am-title-bar"></div>
            <span class="text-[10px] text-[#E8ECF4] font-bold">提交与试算</span>
          </div>
          <span class="text-[10px] text-[#3B9EFF] border border-[#3B9EFF]/30 bg-[#3B9EFF]/5 px-1 rounded font-mono">LAST MILE</span>
        </div>

        <!-- Submission Summary -->
        <div class="bg-[#161922] rounded border border-[#2E3348] p-2 space-y-1">
          <div class="flex justify-between">
            <span class="text-[#555E75]">草稿方案</span>
            <span class="text-[#FF9500] font-semibold truncate max-w-[120px]">{{ activeDraft?.label ?? '—' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-[#555E75]">涉及产品</span>
            <span class="text-[#E8ECF4] font-mono">{{ products.length }}只</span>
          </div>
          <div class="flex justify-between">
            <span class="text-[#555E75]">指令总笔数</span>
            <span class="text-[#E8ECF4] font-mono">{{ totalOrders }}笔</span>
          </div>
          <div class="flex justify-between">
            <span class="text-[#555E75]">预检状态</span>
            <span :class="flaggedCount > 0 ? 'text-red-400 font-semibold' : 'text-green-400'">
              {{ flaggedCount > 0 ? `${flaggedCount}笔待确认` : '全部通过' }}
            </span>
          </div>
        </div>

        <!-- IDLE: Submit Button -->
        <button
          v-if="hubState === 'idle'"
          @click="submitToHub"
          class="w-full py-3 px-2 bg-[#3B9EFF]/10 border border-[#3B9EFF]/35 rounded text-[#3B9EFF] hover:bg-[#3B9EFF]/20 hover:border-[#3B9EFF]/65 active:scale-[0.98] transition-all flex items-center justify-center gap-2 font-semibold"
        >
          <span>执行系统合规试算</span>
        </button>

        <!-- LOADING: Progress -->
        <div
          v-else-if="hubState === 'loading'"
          class="w-full py-4 flex flex-col items-center gap-2.5 bg-[#161922] border border-[#2E3348] rounded"
        >
          <div class="flex items-center gap-2 text-[#3B9EFF]">
            <div class="w-3.5 h-3.5 border-2 border-[#3B9EFF]/30 border-t-[#3B9EFF] rounded-full animate-spin"></div>
            <span class="font-semibold">试算进行中...</span>
          </div>
          <div class="text-[#555E75] text-center space-y-0.5">
            <p>{{ loadProgress < 40 ? '连接估值引擎' : loadProgress < 75 ? '风控规则校验中' : '汇总试算结果' }}</p>
          </div>
          <div class="w-full px-4">
            <div class="h-1 bg-[#2E3348] rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-[#3B9EFF] to-[#22D3EE] rounded-full transition-all duration-300"
                :style="{ width: loadProgress + '%' }"
              ></div>
            </div>
            <div class="flex justify-between mt-1 text-[#555E75] text-[10px]">
              <span>估值引擎</span>
              <span class="font-mono">{{ Math.round(loadProgress) }}%</span>
            </div>
          </div>
        </div>

        <!-- DONE: Results -->
        <template v-else-if="hubState === 'done'">

          <!-- Positive result -->
          <Transition
            appear
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
          >
            <div class="bg-green-500/5 border border-green-500/20 rounded p-2.5 space-y-1">
              <div class="flex items-center gap-1.5">
                <CircleCheckFilled class="w-3.5 h-3.5 text-green-400 shrink-0" />
                <span class="font-semibold text-green-400">估值预测通过</span>
              </div>
              <p class="text-[#8B93A8] pl-5">整体年化收益预计提升</p>
              <p class="text-green-400 font-mono text-[15px] font-bold pl-5 tracking-tight">+12 <span class="text-xs">bp</span></p>
              <div class="pl-5 space-y-0.5 text-[#555E75]">
                <div class="flex justify-between">
                  <span>久期中性贡献</span><span class="text-green-400/60 font-mono">+8bp</span>
                </div>
                <div class="flex justify-between">
                  <span>信用利差收窄</span><span class="text-green-400/60 font-mono">+4bp</span>
                </div>
              </div>
            </div>
          </Transition>

          <!-- Risk block -->
          <Transition
            appear
            enter-active-class="transition-all duration-300 delay-100 ease-out"
            enter-from-class="opacity-0 translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
          >
            <div class="bg-red-500/5 border border-red-500/25 rounded p-2.5 space-y-1.5">
              <div class="flex items-center gap-1.5">
                <WarningFilled class="w-3.5 h-3.5 text-red-400 shrink-0" />
                <span class="font-semibold text-red-400">风控拦截</span>
                <span class="ml-auto text-[10px] text-red-400 border border-red-400/30 bg-red-400/8 px-1.5 py-1 rounded">2笔</span>
              </div>
              <div class="space-y-1.5 pl-1">
                <div class="flex items-start gap-1.5 bg-red-500/5 rounded p-1.5">
                  <span class="text-red-400 font-mono shrink-0">①</span>
                  <div>
                    <p class="text-red-300/80">启航6月滚动</p>
                    <p class="text-[#555E75]">久期敞口越限 (3.8y → 4.2y, 上限4.0y)</p>
                  </div>
                </div>
                <div class="flex items-start gap-1.5 bg-red-500/5 rounded p-1.5">
                  <span class="text-red-400 font-mono shrink-0">②</span>
                  <div>
                    <p class="text-red-300/80">鑫源纯债A</p>
                    <p class="text-[#555E75]">单券集中度超限 (地产债 XY02 占比27.9%)</p>
                  </div>
                </div>
              </div>
            </div>
          </Transition>

          <!-- Re-submit -->
          <button
            @click="hubState = 'idle'"
            class="w-full py-1.5 bg-[#161922] border border-[#2E3348] rounded text-[#555E75] hover:text-[#8B93A8] hover:border-[#3E4660] transition-colors flex items-center justify-center gap-1.5"
          >
            <Refresh class="w-3 h-3" />
            <span>重新试算</span>
          </button>

          <!-- Apply Simulation Toggle -->
          <div class="flex items-center justify-between bg-[#161922] border border-[#2E3348] rounded px-2.5 py-1.5">
            <span class="text-xs text-[#94A3B8]">应用任务篮试算</span>
            <button
              @click="localSimulation = !localSimulation"
              :class="cn('relative w-7 h-3.5 rounded-full transition-colors duration-200 border shrink-0',
                localSimulation ? 'bg-[#3B9EFF] border-[#3B9EFF]' : 'bg-[#252A3A] border-[#2E3348]')"
            >
              <div :class="cn('absolute top-0.5 w-2.5 h-2.5 rounded-full bg-white shadow-sm transition-all duration-200',
                localSimulation ? 'left-3.5' : 'left-0.5')"></div>
            </button>
          </div>

          <!-- Sign Off Button -->
          <button
            class="w-full py-2.5 bg-[#00C9A7]/10 border border-[#00C9A7]/30 rounded text-[#00C9A7] hover:bg-[#00C9A7]/20 hover:border-[#00C9A7]/50 disabled:opacity-40 disabled:cursor-not-allowed text-[13px] font-semibold transition-colors flex items-center justify-center gap-1.5"
            :disabled="taskBasket.length === 0"
            @click="handleSignOff"
          >
            <CircleCheckFilled class="w-3.5 h-3.5" /> 签发至交易系统
          </button>

        </template>

      </div>
    </div>

    <!-- ═══ Add Asset Inline Dialog ═══ -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="showAssetDialog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="showAssetDialog = false">
        <div class="bg-[#202431] border border-[#2E3348] rounded-lg shadow-2xl w-[380px] overflow-hidden">
          <div class="px-4 py-3 border-b border-[#2E3348] flex items-center justify-between">
            <span class="text-[15px] font-semibold text-[#E8ECF4]">添加标的</span>
            <button @click="showAssetDialog = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-0.5">
              <Close class="w-4 h-4" />
            </button>
          </div>
          <div class="p-4 space-y-3">
            <div>
              <label class="text-xs text-[#94A3B8] mb-1 block">标的代码</label>
              <input v-model="assetForm.code" placeholder="如 240001.IB"
                class="w-full bg-[#161922] border border-[#2E3348] hover:border-[#3B9EFF]/40 focus:border-[#3B9EFF] rounded px-3 py-1.5 text-[13px] text-[#E8ECF4] outline-none transition-colors placeholder:text-[#555E75]" />
            </div>
            <div>
              <label class="text-xs text-[#94A3B8] mb-1 block">标的名称</label>
              <input v-model="assetForm.name" placeholder="如 24国债01"
                class="w-full bg-[#161922] border border-[#2E3348] hover:border-[#3B9EFF]/40 focus:border-[#3B9EFF] rounded px-3 py-1.5 text-[13px] text-[#E8ECF4] outline-none transition-colors placeholder:text-[#555E75]" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs text-[#94A3B8] mb-1 block">金额 (万)</label>
                <input v-model.number="assetForm.amount" type="number" min="0" placeholder="0"
                  class="w-full bg-[#161922] border border-[#2E3348] hover:border-[#3B9EFF]/40 focus:border-[#3B9EFF] rounded px-3 py-1.5 text-[13px] text-[#E8ECF4] outline-none transition-colors font-mono tabular-nums placeholder:text-[#555E75]" />
              </div>
              <div>
                <label class="text-xs text-[#94A3B8] mb-1 block">方向</label>
                <div class="flex gap-1">
                  <button
                    @click="assetForm.direction = 'buy'"
                    :class="cn('flex-1 text-xs py-1.5 rounded border transition-colors',
                      assetForm.direction === 'buy' ? 'bg-[#00C9A7]/15 text-[#00C9A7] border-[#00C9A7]/30' : 'bg-[#161922] text-[#94A3B8] border-[#2E3348]')"
                  >买入</button>
                  <button
                    @click="assetForm.direction = 'sell'"
                    :class="cn('flex-1 text-xs py-1.5 rounded border transition-colors',
                      assetForm.direction === 'sell' ? 'bg-[#F04864]/15 text-[#F04864] border-[#F04864]/30' : 'bg-[#161922] text-[#94A3B8] border-[#2E3348]')"
                  >卖出</button>
                </div>
              </div>
            </div>
          </div>
          <div class="px-4 py-3 border-t border-[#2E3348] flex items-center justify-end gap-2">
            <button @click="showAssetDialog = false" class="text-[13px] text-[#94A3B8] hover:text-[#E8ECF4] px-3 py-1.5 transition-colors">取消</button>
            <button
              @click="confirmAddAsset"
              :disabled="!assetForm.code || assetForm.amount <= 0"
              class="text-[13px] bg-[#3B9EFF] hover:bg-[#5AAFFF] text-white px-4 py-1.5 rounded transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >确认添加</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue';
import {
  ArrowRight, ArrowDown, EditPen,
  CircleCheckFilled, WarningFilled, Refresh, Plus,
  Cpu, Download, TrendCharts, Close
} from '@element-plus/icons-vue';
import { sharedIntentState } from '../store/intentStore';
import { rebalanceTarget, taskBasket, addToBasket, modelBackPath, operationScene, basketSummary, isApplyingBasket, clearBasket, type TaskBasketItem } from '../store/demoStore';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

type ClassValue = Parameters<typeof clsx>[0];
function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

const emit = defineEmits<{ (e: 'navigate', target: string): void }>();

const batchCtx = computed(() => sharedIntentState.batchContext);

type OperationMode = 'single' | 'batch';
const operationMode = ref<OperationMode>('single');
const selectedSingleProduct = ref<string>('p1');
const singleProductLabel = computed(() => {
  const p = products.value.find(x => x.id === selectedSingleProduct.value);
  return p ? p.name : '未选择';
});

function navigateToModelCenter() {
  sharedIntentState.callerTab = 'intent';
  sharedIntentState.navigationTarget = 'model-center';
  modelBackPath.value = 'batch-simulator';
  emit('navigate', 'model-center');
}

function handleExcelImport() {
  window.alert('导入持仓功能对接中。\n将读取 Excel 并解析为持仓数据。');
}

const showAssetDialog = ref(false);
const assetForm = reactive({ code: '', name: '', amount: 0, direction: 'buy' as 'buy' | 'sell' });

function openAssetDialog() {
  assetForm.code = '';
  assetForm.name = '';
  assetForm.amount = 0;
  assetForm.direction = 'buy';
  showAssetDialog.value = true;
}

function confirmAddAsset() {
  if (!assetForm.code || assetForm.amount <= 0) return;
  const prodId = operationMode.value === 'single' ? selectedSingleProduct.value : 'all';
  addToBasket({
    type: assetForm.direction,
    assetName: assetForm.name || assetForm.code,
    assetCode: assetForm.code,
    amount: assetForm.amount,
    source: operationMode.value === 'batch' ? '批量' : '手动',
    status: 'pending',
    weightDelta: 0,
    productId: prodId,
  });
  showAssetDialog.value = false;
}

const localSimulation = ref(false);
watch(localSimulation, (v) => { isApplyingBasket.value = v; });

function handleSignOff() {
  clearBasket();
  localSimulation.value = false;
  window.alert(`已签发 ${basketSummary.value.totalCount} 条指令至交易系统，任务篮已清空。`);
}

const productTotalScale = computed(() => products.value.reduce((s, p) => s + p.beforeAmt, 0));

const plannedAmount = computed(() => {
  return taskBasket.value.reduce((s, inst) => s + inst.amount, 0);
});
const targetAmount = computed(() => {
  if (operationScene.value === '建仓') return productTotalScale.value;
  return rebalanceTarget.value?.gapAmount ?? 0;
});
const progressPct = computed(() => {
  if (targetAmount.value <= 0) return 100;
  return Math.min(100, (plannedAmount.value / targetAmount.value) * 100);
});
const isTargetMet = computed(() => {
  if (targetAmount.value <= 0) return true;
  return plannedAmount.value >= targetAmount.value;
});

// ── Unified Engine State ─────────────────────────────────────────────────
const mergedEngineMode = ref<string>('proportional');
const concentrationTarget = ref<string>('p1');
const allocAmount    = ref<number | null>(null);
const allocTarget    = ref<number | null>(null);
const sandboxModelResult = ref<{ name: string; value: string; change: string }[]>([]);
const isSandboxModelRunning = ref(false);

function executeQuantModel() {
  isSandboxModelRunning.value = true;
  setTimeout(() => {
    const navTotal = products.value.reduce((s, p) => s + p.beforeAmt, 0);
    products.value.forEach(p => {
      const ratio = navTotal > 0 ? p.beforeAmt / navTotal : 1 / products.value.length;
      p.afterAmt = Math.round(p.beforeAmt * (1 + (Math.random() - 0.4) * 0.05) * 100) / 100;
      p.deviation = Math.round((p.afterAmt - p.beforeAmt) / p.beforeAmt * 10000) / 100;
    });
    sandboxModelResult.value = [
      { name: '执行模型', value: '量化资配模型', change: '一键覆盖' },
      { name: '影响产品', value: `${products.value.length} 只`, change: '' },
      { name: '总调仓额', value: `${products.value.reduce((s, p) => s + Math.abs(p.afterAmt - p.beforeAmt), 0).toFixed(1)} 万`, change: '已写入' },
      { name: '执行状态', value: '完成', change: '草稿已更新' },
    ];
    isSandboxModelRunning.value = false;
  }, 1200);
}

// ── Types ──────────────────────────────────────────────────────────────────
interface Bond {
  name: string;
  code: string;
  before: number;
  after: number;
  change: number;
  flagged?: boolean;
}

interface Product {
  id: string;
  name: string;
  code: string;
  beforeAmt: number;
  afterAmt: number;
  cash: number;
  deviation: number;
  flagged: boolean;
  expanded: boolean;
  bonds: Bond[];
}

interface Task {
  id: string;
  icon: string;
  title: string;
  subtitle: string;
  urgent: boolean;
  affected: number;
  time: string;
}

interface Draft {
  id: string;
  label: string;
  desc: string;
  count: number;
  delta: number;
  timestamp: string;
}

// ── UI State ───────────────────────────────────────────────────────────────
const leftTab        = ref<'inbox' | 'drafts'>('inbox');
const selectedTaskId = ref<string | null>('t1');
const selectedProductId = ref<string | null>(null);
const activeDraftId  = ref('d1');
const editingCell    = ref<{ productId: string; field: string } | null>(null);

type HubState = 'idle' | 'loading' | 'done';
const hubState    = ref<HubState>('idle');
const loadProgress = ref(0);

// ── Mock: Tasks ────────────────────────────────────────────────────────────
const inboxTasks = ref<Task[]>([
  {
    id: 't1', icon: '', title: '违规持仓',
    subtitle: '某地产债评级下调至BB+，需压降敞口',
    urgent: true, affected: 8, time: '09:32'
  },
  {
    id: 't2', icon: '', title: '资金站岗',
    subtitle: '存单集中到期，12只产品现金水位过高',
    urgent: true, affected: 12, time: '10:15'
  },
  {
    id: 't3', icon: '', title: 'TAA偏离预警',
    subtitle: '权益仓位较基准偏离超±3%阈值',
    urgent: false, affected: 5, time: '11:00'
  },
  {
    id: 't4', icon: '', title: '季度再平衡',
    subtitle: '季末标准化资产配置重平衡任务',
    urgent: false, affected: 15, time: '13:00'
  },
]);

// ── Mock: Drafts ───────────────────────────────────────────────────────────
const draftSchemes = ref<Draft[]>([
  {
    id: 'd1', label: '方案A: 激进对齐',
    desc: '一次性对齐TAA目标，最大化预期收益',
    count: 8, delta: 14, timestamp: '今日 09:45'
  },
  {
    id: 'd2', label: '方案B: 平缓过渡',
    desc: '分两期执行，分散市场冲击成本',
    count: 6, delta: 8, timestamp: '今日 10:22'
  },
  {
    id: 'd3', label: '方案C: 保守底线',
    desc: '仅处理违规仓位，保持其余结构不变',
    count: 3, delta: 3, timestamp: '昨日 16:30'
  },
]);

// ── Mock: Products (12 items) ──────────────────────────────────────────────
const products = ref<Product[]>([
  {
    id: 'p1', name: '启航9月持有1号', code: 'QH001',
    beforeAmt: 12850.0, afterAmt: 13200.0, cash: 428.5, deviation: 2.72,
    flagged: false, expanded: false,
    bonds: [
      { name: '24国债01', code: '240001.IB', before: 4200, after: 4500, change: 300 },
      { name: '23地方债15', code: '230015.IB', before: 3100, after: 2800, change: -300 },
      { name: '中银转债', code: '113045.SZ', before: 2550, after: 2900, change: 350 },
    ]
  },
  {
    id: 'p2', name: '启航1年封闭A', code: 'QH002',
    beforeAmt: 8640.0, afterAmt: 8640.0, cash: 212.3, deviation: 0.00,
    flagged: false, expanded: false,
    bonds: [
      { name: '24国债03', code: '240003.IB', before: 2800, after: 2800, change: 0 },
      { name: '中债AAA复利', code: '220058.IB', before: 3200, after: 3200, change: 0 },
    ]
  },
  {
    id: 'p3', name: '启航6月滚动', code: 'QH003',
    beforeAmt: 5200.0, afterAmt: 5850.0, cash: 88.2, deviation: 4.87,
    flagged: true, expanded: false,
    bonds: [
      { name: '地产债XY01', code: 'XY2301.IB', before: 1500, after: 2100, change: 600, flagged: true },
      { name: '24农发债08', code: '240008.IB', before: 1800, after: 1800, change: 0 },
    ]
  },
  {
    id: 'p4', name: '稳健增利3号', code: 'WJ003',
    beforeAmt: 18750.0, afterAmt: 17900.0, cash: 562.1, deviation: -1.23,
    flagged: false, expanded: false,
    bonds: [
      { name: '24国开债02', code: '240002.IB', before: 6200, after: 6000, change: -200 },
      { name: '城投债HN01', code: 'HN2301.IB', before: 5500, after: 5000, change: -500 },
      { name: '中票AAA', code: '230088.IB', before: 4800, after: 4800, change: 0 },
    ]
  },
  {
    id: 'p5', name: '远航混合精选', code: 'YH001',
    beforeAmt: 22400.0, afterAmt: 23100.0, cash: 840.0, deviation: 1.55,
    flagged: false, expanded: false,
    bonds: [
      { name: '24国债05', code: '240005.IB', before: 8000, after: 8500, change: 500 },
      { name: '沪深300ETF', code: '510300.SH', before: 5200, after: 5200, change: 0 },
    ]
  },
  {
    id: 'p6', name: '远航混合精选2号', code: 'YH002',
    beforeAmt: 15600.0, afterAmt: 16200.0, cash: 320.5, deviation: 2.18,
    flagged: false, expanded: false,
    bonds: [
      { name: '转债精选A', code: '110062.SH', before: 5200, after: 5800, change: 600 },
      { name: '24农发债11', code: '240011.IB', before: 6500, after: 6500, change: 0 },
    ]
  },
  {
    id: 'p7', name: '均衡优选6月', code: 'JH001',
    beforeAmt: 7800.0, afterAmt: 7800.0, cash: 195.0, deviation: 0.00,
    flagged: false, expanded: false,
    bonds: [
      { name: '24国债07', code: '240007.IB', before: 3000, after: 3000, change: 0 },
      { name: '央行票据', code: 'CB2401.IB', before: 2800, after: 2800, change: 0 },
    ]
  },
  {
    id: 'p8', name: '均衡优选1年', code: 'JH002',
    beforeAmt: 9350.0, afterAmt: 9700.0, cash: 248.0, deviation: 1.87,
    flagged: false, expanded: false,
    bonds: [
      { name: '城投债YN02', code: 'YN2302.IB', before: 4200, after: 4500, change: 300 },
      { name: '24国债08', code: '240008.IB', before: 3800, after: 3800, change: 0 },
    ]
  },
  {
    id: 'p9', name: '鑫源纯债A', code: 'WJ004',
    beforeAmt: 31200.0, afterAmt: 30500.0, cash: 980.0, deviation: -0.89,
    flagged: true, expanded: false,
    bonds: [
      { name: '地产债XY02', code: 'XY2302.IB', before: 8500, after: 8500, change: 0, flagged: true },
      { name: '24国债09', code: '240009.IB', before: 12000, after: 11500, change: -500 },
      { name: '城投债JX01', code: 'JX2301.IB', before: 7200, after: 7200, change: 0 },
    ]
  },
  {
    id: 'p10', name: '精选信用债1号', code: 'XX001',
    beforeAmt: 14500.0, afterAmt: 15200.0, cash: 380.0, deviation: 2.95,
    flagged: false, expanded: false,
    bonds: [
      { name: '中票AA+', code: '230092.IB', before: 5200, after: 5800, change: 600 },
      { name: '城投债GD01', code: 'GD2301.IB', before: 6200, after: 6500, change: 300 },
    ]
  },
  {
    id: 'p11', name: '盈利增强3号', code: 'YL003',
    beforeAmt: 6800.0, afterAmt: 7200.0, cash: 156.0, deviation: 3.41,
    flagged: false, expanded: false,
    bonds: [
      { name: '24国开债05', code: '240005.IB', before: 2800, after: 3200, change: 400 },
      { name: '城投债BJ01', code: 'BJ2301.IB', before: 2500, after: 2500, change: 0 },
    ]
  },
  {
    id: 'p12', name: '积成增利半年', code: 'JS001',
    beforeAmt: 4200.0, afterAmt: 4200.0, cash: 105.0, deviation: 0.00,
    flagged: false, expanded: false,
    bonds: [
      { name: '货币市场基金', code: 'MMF001.OF', before: 2000, after: 2000, change: 0 },
      { name: '同业存单', code: 'NCD2401.IB', before: 1800, after: 1800, change: 0 },
    ]
  },
]);

// ── Computed ───────────────────────────────────────────────────────────────
const selectedTask  = computed(() => inboxTasks.value.find(t => t.id === selectedTaskId.value) ?? null);
const activeDraft   = computed(() => draftSchemes.value.find(d => d.id === activeDraftId.value) ?? null);
const totalBefore   = computed(() => products.value.reduce((s, p) => s + p.beforeAmt, 0));
const totalAfter    = computed(() => products.value.reduce((s, p) => s + p.afterAmt, 0));
const totalCash     = computed(() => products.value.reduce((s, p) => s + p.cash, 0));
const totalDelta    = computed(() => totalAfter.value - totalBefore.value);
const flaggedCount  = computed(() => products.value.filter(p => p.flagged).length);
const totalOrders   = computed(() => products.value.reduce((s, p) => s + p.bonds.length, 0));

const contextTAATargets = computed(() => {
  if (selectedTaskId.value === 't1') return [
    { label: '地产债敞口', current: '8.2%',  target: '≤3.0%', status: 'error' },
    { label: '信用久期',   current: '3.8y',  target: '3.5y',  status: 'warn'  },
    { label: 'AA+以上占比', current: '72%',  target: '≥80%',  status: 'warn'  },
  ];
  if (selectedTaskId.value === 't2') return [
    { label: '现金等价物', current: '15.2%', target: '≤8.0%', status: 'error' },
    { label: '到期再投资', current: '12.4亿', target: '再配置', status: 'warn' },
    { label: '短债配置',   current: '22%',   target: '30%',   status: 'warn'  },
  ];
  return [
    { label: '权益仓位',   current: '18.5%', target: '15-20%', status: 'ok' },
    { label: '固收仓位',   current: '74.2%', target: '70-80%', status: 'ok' },
    { label: '另类资产',   current: '7.3%',  target: '≤10%',  status: 'ok' },
  ];
});

const positionLevels = computed(() => [
  { label: '久期敞口',   level: 3.8,  limit: 4.0,  unit: 'y'  },
  { label: '信用集中度', level: 28,   limit: 30,   unit: '%'  },
  { label: '权益仓位',   level: 18,   limit: 25,   unit: '%'  },
  { label: '现金水位',   level: 15,   limit: 20,   unit: '%'  },
]);

// ── Methods ────────────────────────────────────────────────────────────────
function startEdit(productId: string, field: string) {
  editingCell.value = { productId, field };
}

function stopEdit() {
  editingCell.value = null;
}

function applyAllocation() {
  const n = products.value.length;
  if (!n) return;
  if ((mergedEngineMode.value === 'proportional' || mergedEngineMode.value === 'target') && allocAmount.value) {
    const total = allocAmount.value * 10000;
    if (mergedEngineMode.value === 'proportional') {
      const avg = total / n;
      products.value.forEach(p => { p.afterAmt = Math.round(avg) / 100; p.deviation = Math.round((p.afterAmt - p.beforeAmt) / p.beforeAmt * 10000) / 100; });
    } else {
      const navTotal = products.value.reduce((s, p) => s + p.beforeAmt, 0);
      products.value.forEach(p => {
        const ratio = navTotal > 0 ? p.beforeAmt / navTotal : 1 / n;
        p.afterAmt = Math.round(total * ratio * 100) / 100;
        p.deviation = Math.round((p.afterAmt - p.beforeAmt) / p.beforeAmt * 10000) / 100;
      });
    }
  } else if (mergedEngineMode.value === 'concentration' && allocTarget.value) {
    const target = concentrationTarget.value;
    const maxW = allocTarget.value / 100;
    const tgt = products.value.find(p => p.id === target);
    if (tgt) {
      tgt.afterAmt = Math.round(tgt.beforeAmt * (1 + maxW) * 100) / 100;
      tgt.deviation = Math.round((tgt.afterAmt - tgt.beforeAmt) / tgt.beforeAmt * 10000) / 100;
    }
  }
}

function resetAllocation() {
  products.value.forEach(p => { p.afterAmt = p.beforeAmt; });
  allocAmount.value = null;
  allocTarget.value = null;
}

function addDraft() {
  const letters = ['D', 'E', 'F', 'G', 'H', 'I'];
  const idx     = draftSchemes.value.length - 2;
  const newId   = `d${draftSchemes.value.length + 1}`;
  draftSchemes.value.push({
    id:        newId,
    label:     `方案${letters[idx] ?? 'X'}: 新建草稿`,
    desc:      '待编辑',
    count:     0,
    delta:     0,
    timestamp: '刚刚',
  });
  activeDraftId.value = newId;
  leftTab.value = 'drafts';
}

let _loadTimer: ReturnType<typeof setInterval> | null = null;

function submitToHub() {
  hubState.value    = 'loading';
  loadProgress.value = 0;
  _loadTimer = setInterval(() => {
    loadProgress.value = Math.min(93, loadProgress.value + Math.random() * 15 + 5);
    if (loadProgress.value >= 93) {
      clearInterval(_loadTimer!);
      setTimeout(() => {
        loadProgress.value = 100;
        setTimeout(() => {
          hubState.value = 'done';
          products.value.forEach(p => { p.flagged = ['p3', 'p9'].includes(p.id); });
        }, 300);
      }, 600);
    }
  }, 220);
}

function handleOMS() {
  window.alert('OMS 对接通道建设中，敬请期待。\n\n当前已生成 ' + totalOrders.value + ' 笔指令草稿。');
}
</script>
