﻿﻿<template>
  <div class="flex flex-col h-full bg-[#161922] text-[#E8ECF4] overflow-hidden font-sans">

    <!-- Workbench Context Banner (auto-shows when navigated from TerminalDashboard) -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="isFromWorkbench" class="bg-[#0F2240] border-b border-[#3B9EFF]/20 py-1.5 px-4 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-2 text-[11px]">
          <div class="w-1.5 h-1.5 rounded-full bg-[#3B9EFF] animate-pulse shrink-0"></div>
          <span class="text-[#3B9EFF]/80 font-mono">
            已从【资配工作台】跳转进入
            <span class="text-[#3B9EFF] font-bold mx-1">·</span>
            来源视图：
            <span class="font-bold text-[#3B9EFF]">
              {{ sharedIntentState.callerTab === 'taa' ? '目标组合 (TAA)' : '意向组合 (Intent)' }}
            </span>
          </span>
        </div>
        <div class="text-[10px] font-mono text-[#94A3B8]">
          运行模型后，从结构化输出中勾选指标并推送返回工作台
        </div>
      </div>
    </Transition>

    <div class="flex flex-1 overflow-hidden">

      <!-- ═══ LEFT SIDEBAR ═══ -->
      <div class="w-60 bg-[#1A1E2B] border-r border-[#252A3A] flex flex-col shrink-0 z-20">

        <!-- Sidebar Header -->
        <div class="px-3 py-3 border-b border-[#252A3A] flex items-center space-x-2.5">
          <div class="w-7 h-7 rounded bg-[#3B9EFF]/15 border border-[#3B9EFF]/30 flex items-center justify-center">
            <Cpu class="w-3.5 h-3.5 text-[#3B9EFF]" />
          </div>
          <div>
            <h2 class="am-title-l2 tracking-wide">模型中心</h2>
            <p class="text-[10px] text-[#3B9EFF]/50 font-mono uppercase tracking-widest">Model Core v2.4</p>
          </div>
        </div>

        <!-- Leaderboard Button -->
        <div class="p-2.5 border-b border-[#252A3A]">
          <button
            @click="showLeaderboard = true; selectedModelId = null; isDrawerOpen = false"
            :class="cn('w-full flex items-center justify-center space-x-2 px-3 py-1.5 rounded text-[13px] font-semibold transition-colors', showLeaderboard ? 'bg-[#FFAB00]/12 text-[#FFAB00] border border-[#FFAB00]/30' : 'bg-[#202431] text-[#B4BAC9] hover:bg-[#2A2E3D] hover:text-[#E8ECF4] border border-[#2E3348]')"
          >
            <Trophy class="w-3.5 h-3.5" :class="showLeaderboard ? 'text-[#FFAB00]' : 'text-[#FFAB00]/60'" />
            <span>模型热度榜</span>
          </button>
        </div>

        <!-- ── Core Action Buttons ── -->
        <div class="px-2.5 pt-2 pb-2 border-b border-[#252A3A] grid grid-cols-2 gap-1.5">
          <button
            @click="showUploadModal = true"
            class="flex items-center justify-center space-x-1 py-1.5 px-2 rounded border border-[#2E3348] bg-[#202431] hover:bg-[#2A2E3D] hover:border-[#3E4660] transition-colors group"
            title="上传自定义模型文件"
          >
            <UploadFilled class="w-3 h-3 text-[#94A3B8] group-hover:text-[#E8ECF4] transition-colors shrink-0" />
            <span class="text-[11px] font-mono text-[#94A3B8] group-hover:text-[#B4BAC9] transition-colors whitespace-nowrap">上传模型</span>
          </button>
          <button
            @click="handleGenerateModel"
            class="flex items-center justify-center space-x-1 py-1.5 px-2 rounded border border-purple-500/20 bg-purple-900/8 hover:bg-purple-900/18 hover:border-purple-500/35 transition-colors group"
            title="用 Alpha Mind AI 生成模型代码"
          >
            <StarFilled class="w-3 h-3 text-purple-500/60 group-hover:text-purple-400 transition-colors shrink-0" />
            <span class="text-[11px] font-mono text-purple-600/70 group-hover:text-purple-400 transition-colors whitespace-nowrap">生成模型</span>
          </button>
        </div>

        <!-- Model Categories -->
        <div class="flex-1 overflow-y-auto p-2.5 space-y-4 no-scrollbar">
          <!-- tip bar -->
          <div class="flex items-center space-x-1.5 px-2 py-1 bg-[#202431] border border-[#252A3A] rounded text-[10px] font-mono text-[#94A3B8]">
            <Operation class="w-3 h-3 text-[#64748B] shrink-0" />
            <span>点击模型 → 进入运行 / 微调工作区</span>
          </div>
          <div v-for="(category, idx) in categories" :key="idx">
            <div class="flex justify-between items-center mb-1.5">
              <h3 class="am-title-l3 uppercase tracking-widest">
                <div class="am-title-bar"></div>
                <span>{{ category.title }}</span>
              </h3>
            </div>
            <div class="space-y-px">
              <button
                v-for="model in category.models"
                :key="model.id"
                @click="handleSelectModel(model); showLeaderboard = false"
                :class="cn('w-full text-left px-2.5 py-1.5 rounded text-[13px] transition-colors flex items-center justify-between group', selectedModel?.id === model.id && !showLeaderboard ? 'bg-[#3B9EFF]/12 text-[#3B9EFF] border border-[#3B9EFF]/22' : 'text-[#94A3B8] hover:bg-[#202431] hover:text-[#E8ECF4] border border-transparent hover:border-[#252A3A]')"
              >
                <div class="flex items-center overflow-hidden flex-1 mr-2">
                  <User v-if="model.source === 'self'" class="w-[10px] h-[10px] mr-1.5 shrink-0 text-[#3B9EFF]/70" />
                  <UserFilled v-else-if="model.source === 'shared'" class="w-[10px] h-[10px] mr-1.5 shrink-0 text-[#00C9A7]/70" />
                  <span class="truncate">{{ model.name }}</span>
                  <template v-if="model.visibility === 'private'">
                    <CircleCheckFilled class="w-[9px] h-[9px] ml-1.5 shrink-0 text-emerald-400/80" />
                    <span class="ml-1 text-[7.5px] font-mono font-bold leading-tight text-emerald-400/70 bg-emerald-900/15 border border-emerald-500/20 px-[3px] py-[1px] rounded">加密</span>
                  </template>
                </div>
                <div class="flex items-center shrink-0 space-x-1">
                  <div v-if="model.usageCount > 0 && (model.visibility === 'dept' || model.visibility === 'corp' || model.type === 'classic' || model.type === 'ai')" class="flex items-center text-[10px] text-[#FFAB00]/60">
                    <Lightning class="w-[9px] h-[9px] mr-0.5" />
                    <span class="font-mono">{{ formatUsageCount(model.usageCount) }}</span>
                  </div>
                  <ArrowRight :class="cn('w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity', selectedModel?.id === model.id && !showLeaderboard ? 'opacity-100 text-[#3B9EFF]' : '')" />
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ MAIN AREA ═══ -->
      <div class="flex-1 relative overflow-hidden bg-[#161922]">

        <!-- Empty State -->
        <div v-if="!isDrawerOpen && !showLeaderboard" class="absolute inset-0 flex flex-col items-center justify-center">
          <div class="w-14 h-14 rounded bg-[#202431] border border-[#2E3348] flex items-center justify-center mb-4">
            <Cpu class="w-6 h-6 text-[#3B9EFF]/20" />
          </div>
          <p class="text-[13px] font-mono text-[#94A3B8] tracking-widest uppercase">请在左侧选择模型以开启工作区</p>
          <p class="text-[10px] text-[#64748B] mt-1 font-mono">MODEL_CENTER_IDLE</p>
        </div>

        <!-- ═══ LEADERBOARD ═══ -->
        <div v-if="showLeaderboard" class="absolute inset-0 bg-[#161922] flex flex-col z-30 overflow-hidden">
          <div class="px-5 py-3.5 border-b border-[#252A3A] bg-[#1A1E2B] shrink-0">
            <h2 class="am-title-l1"><div class="am-title-bar"></div>模型调用热度榜
              <span class="ml-3 text-[13px] font-normal text-[#94A3B8] font-mono">Leaderboard</span>
            </h2>
            <p class="text-[11px] text-[#94A3B8] mt-1 font-mono">全公司模型调用频次排行，数据每月更新</p>
          </div>
          <div class="flex-1 overflow-y-auto p-4 no-scrollbar">
            <div class="max-w-6xl mx-auto bg-[#1A1E2B] border border-[#252A3A] rounded overflow-hidden">
              <table class="min-w-full divide-y divide-[#252A3A]">
                <thead class="bg-[#202431] sticky top-0 z-10">
                  <tr>
                    <th class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#94A3B8] uppercase tracking-widest w-24">排名</th>
                    <th class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#94A3B8] uppercase tracking-widest">模型名称</th>
                    <th class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#94A3B8] uppercase tracking-widest w-28">类型</th>
                    <th class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#94A3B8] uppercase tracking-widest w-28">作者</th>
                    <th class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#94A3B8] uppercase tracking-widest w-36">所属部门</th>
                    <th class="px-4 py-2.5 text-right text-[11px] font-semibold text-[#94A3B8] uppercase tracking-widest w-28">月度调用</th>
                    <th class="px-4 py-2.5 text-right text-[11px] font-semibold text-[#94A3B8] uppercase tracking-widest w-24">环比趋势</th>
                  </tr>
                </thead>
                <tbody class="bg-[#161922] divide-y divide-[#252A3A]">
                  <tr
                    v-for="(model, index) in leaderboardModels"
                    :key="model.id"
                    @click="handleSelectModel(model); showLeaderboard = false"
                    class="hover:bg-[#202431] transition-colors cursor-pointer group"
                  >
                    <td class="px-4 py-3 whitespace-nowrap">
                      <div :class="cn('w-7 h-7 rounded flex items-center justify-center text-[13px] font-bold font-mono', index === 0 ? 'bg-[#FFAB00]/12 text-[#FFAB00] border border-[#FFAB00]/30' : index === 1 ? 'bg-[#8B93A8]/10 text-[#B4BAC9] border border-[#8B93A8]/25' : index === 2 ? 'bg-[#FFAB00]/8 text-[#FFAB00]/70 border border-[#FFAB00]/20' : 'bg-[#202431] text-[#94A3B8] border border-[#2E3348]')">
                        {{ index + 1 }}
                      </div>
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap">
                      <div class="text-[13px] font-semibold text-[#E8ECF4] group-hover:text-[#3B9EFF] transition-colors">{{ model.name }}</div>
                      <div class="text-[11px] text-[#94A3B8] mt-0.5 truncate max-w-md">{{ model.desc }}</div>
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap">
                      <span :class="cn('px-1.5 py-px rounded text-[11px] font-mono border', model.type === 'ai' ? 'bg-purple-900/15 text-purple-400/80 border-purple-500/18' : model.type === 'classic' ? 'bg-[#3B9EFF]/10 text-[#3B9EFF]/80 border-[#3B9EFF]/18' : 'bg-[#2A2E3D] text-[#B4BAC9] border-[#2E3348]')">
                        {{ model.type === 'ai' ? 'AI 模型' : model.type === 'classic' ? '经典模型' : '自定义' }}
                      </span>
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap text-[13px] text-[#94A3B8]">
                      <div class="flex items-center"><User class="w-3 h-3 mr-1 text-[#64748B]" />{{ model.author }}</div>
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap text-[13px] text-[#94A3B8]">{{ model.department }}</td>
                    <td class="px-4 py-3 whitespace-nowrap text-right">
                      <span class="text-[13px] font-mono font-bold text-[#FFAB00]/75">{{ model.usageCount.toLocaleString() }}</span>
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap text-right">
                      <span :class="cn('text-[13px] font-mono font-bold', model.trend.startsWith('+') ? 'text-[#00C9A7]' : model.trend.startsWith('-') ? 'text-[#FF5630]' : 'text-[#94A3B8]')">{{ model.trend }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ═══ DRAWER ═══ -->
        <div :class="cn('absolute inset-0 flex transition-transform duration-300 ease-in-out', isDrawerOpen ? 'translate-x-0' : 'translate-x-full')">

          <!-- MIDDLE: Editor / Form / Chat -->
          <div class="flex-1 flex flex-col border-r border-[#252A3A] bg-[#1A1E2B] min-w-0">

            <!-- Model Header -->
            <div class="px-4 py-3 border-b border-[#252A3A] bg-[#202431] flex justify-between items-center shrink-0">
              <div class="flex-1 mr-4 min-w-0">
                <h2 class="am-title-l2"><div class="am-title-bar"></div><span class="truncate">{{ selectedModel?.name }}</span></h2>
                <div class="flex items-center mt-1 text-[10px] text-[#94A3B8] space-x-4 flex-wrap gap-y-1 font-mono">
                <span class="flex items-center"><User class="w-2.5 h-2.5 mr-1" /> {{ selectedModel?.author }}</span>
                <span class="flex items-center"><TrendCharts class="w-2.5 h-2.5 mr-1" /> {{ selectedModel?.updateTime }}</span>
                <span class="flex items-center text-[#FFAB00]/55"><Lightning class="w-2.5 h-2.5 mr-1" /> {{ selectedModel?.usageCount?.toLocaleString() }} 次调用</span>
              </div>
              <p class="text-[11px] text-[#B4BAC9] mt-1 truncate">{{ selectedModel?.desc }}</p>
              </div>
              <div class="flex items-center space-x-2 shrink-0">
                <button
                  v-if="selectedModel?.visibility === 'private' && selectedModel?.author === '当前用户'"
                  @click="showShareModal = true"
                  class="flex items-center space-x-1 px-2.5 py-1.5 bg-[#3B9EFF]/10 hover:bg-[#3B9EFF]/18 text-[#3B9EFF] border border-[#3B9EFF]/20 hover:border-[#3B9EFF]/35 text-[13px] font-semibold rounded transition-colors"
                >
                  <Share class="w-3.5 h-3.5" /><span>分享与发布</span>
                </button>
                <button
                  v-if="selectedModel?.type !== 'ai'"
                  @click="handleRunModel"
                  :disabled="isRunning"
                  :class="cn('flex items-center space-x-2 px-4 py-1.5 text-white text-[13px] font-semibold rounded transition-colors disabled:cursor-not-allowed', isRunning ? 'bg-[#3B9EFF]/70 disabled:opacity-80' : 'bg-[#3B9EFF] hover:bg-[#5CB3FF] disabled:bg-[#3B9EFF]/30')"
                >
                  <TrendCharts v-if="isRunning" class="w-3.5 h-3.5 animate-spin" />
                  <VideoPlay v-else class="w-3.5 h-3.5" />
                  <span>{{ isRunning ? '计算中...' : '运行模型' }}</span>
                </button>
              </div>
            </div>

            <div class="flex-1 overflow-hidden flex flex-col">

              <!-- Classic Form -->
              <div v-if="selectedModel?.type === 'classic'" class="flex-1 overflow-y-auto p-4 no-scrollbar">
                <div class="max-w-2xl mx-auto space-y-3">
                  <div class="bg-[#161922] border border-[#2E3348] rounded p-4">
                    <h3 class="am-title-l3 mb-3 border-b border-[#252A3A] pb-2 uppercase tracking-wider"><div class="am-title-bar"></div>数据源配置</h3>
                    <div class="space-y-3">
                      <div>
                        <label class="block text-[11px] text-[#94A3B8] mb-1 uppercase tracking-wider font-mono">行情与宏观数据源</label>
                        <select class="w-full operable-zone text-[#E8ECF4] text-[13px] rounded px-3 py-2 focus:outline-none">
                          <option>Wind API (万得)</option>
                          <option>Bloomberg Terminal</option>
                          <option>Choice 数据</option>
                          <option>内部数仓 (Data Warehouse)</option>
                        </select>
                      </div>
                      <div>
                        <label class="block text-[11px] text-[#94A3B8] mb-1 uppercase tracking-wider font-mono">历史数据回溯区间</label>
                        <div class="flex space-x-2">
                          <input type="date" value="2015-01-01" class="flex-1 operable-zone text-[#E8ECF4] text-[13px] rounded px-3 py-2 focus:outline-none" />
                          <span class="text-[#64748B] self-center font-mono">—</span>
                          <input type="date" value="2024-01-01" class="flex-1 operable-zone text-[#E8ECF4] text-[13px] rounded px-3 py-2 focus:outline-none" />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="bg-[#161922] border border-[#2E3348] rounded p-4">
                    <h3 class="am-title-l3 mb-3 border-b border-[#252A3A] pb-2 uppercase tracking-wider"><div class="am-title-bar"></div>模型参数设置</h3>
                    <div class="space-y-4">
                      <div>
                        <div class="flex justify-between mb-1.5">
                          <label class="text-[13px] text-[#B4BAC9]">风险厌恶系数 (Risk Aversion)</label>
                          <span class="text-[13px] text-[#3B9EFF] font-mono font-bold">2.5</span>
                        </div>
                        <input type="range" min="1" max="10" step="0.1" value="2.5" class="w-full accent-[#3B9EFF]" />
                        <div class="flex justify-between text-[10px] text-[#94A3B8] mt-0.5 font-mono">
                          <span>激进 (1.0)</span><span>保守 (10.0)</span>
                        </div>
                      </div>
                      <div>
                        <div class="flex justify-between mb-1.5">
                          <label class="text-[13px] text-[#B4BAC9]">预期收益率上限 (Max Target Return)</label>
                          <span class="text-[13px] text-[#3B9EFF] font-mono font-bold">15.0%</span>
                        </div>
                        <input type="range" min="5" max="30" step="0.5" value="15" class="w-full accent-[#3B9EFF]" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Custom Code Editor -->
              <div v-else-if="selectedModel?.type === 'custom'" :class="cn('flex flex-col bg-[#161922] p-3', isFullscreenCode ? 'fixed inset-0 z-50' : 'flex-1')">
                <div v-if="!isFullscreenCode" class="mb-2 grid grid-cols-2 gap-2 shrink-0">
                  <!-- Inputs Panel -->
                  <div class="bg-[#1A1E2B] border border-[#2E3348] rounded flex flex-col max-h-[200px]">
                    <div class="px-3 py-1.5 border-b border-[#252A3A] shrink-0 bg-[#202431]">
                      <h4 class="am-title-l3 uppercase tracking-wider"><div class="am-title-bar"></div>识别输入 (Inputs)</h4>
                    </div>
                    <div class="p-2 overflow-y-auto space-y-1.5 no-scrollbar">
                      <div v-for="item in MODEL_INPUTS" :key="item.key" class="bg-[#161922] p-2 rounded border border-[#252A3A] flex flex-col space-y-1 hover:border-[#2E3348] transition-colors">
                        <div class="flex items-center justify-between">
                          <span class="text-[#E8ECF4] text-xs font-mono">{{ item.key }}</span>
                          <span class="text-[#94A3B8] text-[10px] font-mono bg-[#202431] px-1.5 py-1 rounded border border-[#2E3348]">{{ item.type }}</span>
                        </div>
                        <button
                          @click="openApiModal(item.key)"
                          class="w-full bg-[#202431] border border-[#2E3348] hover:border-[#3B9EFF]/40 hover:bg-[#3B9EFF]/5 text-left text-[11px] rounded px-2 py-1 transition-colors flex items-center justify-between group"
                        >
                          <div class="flex flex-col overflow-hidden">
                            <span class="text-[#B4BAC9] truncate">{{ inputMappings[item.key]?.source || '请选择数据源' }}</span>
                            <span v-if="inputMappings[item.key]?.source !== '自定义输入 (Manual)' && inputMappings[item.key]?.table" class="text-[#94A3B8] text-[10px] truncate mt-0.5 font-mono">
                              {{ inputMappings[item.key].table }} {{ inputMappings[item.key].field?.length ? `> ${inputMappings[item.key].field.join(', ')}` : '' }}
                            </span>
                            <span v-else-if="inputMappings[item.key]?.source === '自定义输入 (Manual)' && inputMappings[item.key]?.value" class="text-[#94A3B8] text-[10px] truncate mt-0.5 font-mono">
                              值: {{ inputMappings[item.key].value }}
                            </span>
                          </div>
                          <SettingsIcon class="w-[11px] h-[11px] text-[#94A3B8] group-hover:text-[#3B9EFF] shrink-0 ml-2 transition-colors" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <!-- Outputs Panel -->
                  <div class="bg-[#1A1E2B] border border-[#2E3348] rounded flex flex-col max-h-[200px]">
                    <div class="px-3 py-1.5 border-b border-[#252A3A] shrink-0 bg-[#202431]">
                      <h4 class="am-title-l3 uppercase tracking-wider"><div class="am-title-bar"></div>识别输出 (Outputs)</h4>
                    </div>
                    <div class="p-2 overflow-y-auto space-y-1.5 no-scrollbar">
                      <div v-for="item in MODEL_OUTPUTS" :key="item.key" class="bg-[#161922] p-2 rounded border border-[#252A3A] flex flex-col space-y-1">
                        <div class="flex items-center justify-between">
                          <span class="text-[#E8ECF4] text-xs font-mono">{{ item.key }}</span>
                          <span class="text-[#94A3B8] text-[10px] font-mono bg-[#202431] px-1.5 py-1 rounded border border-[#2E3348]">{{ item.type }}</span>
                        </div>
                        <div class="text-[11px] text-[#B4BAC9]">{{ item.desc }}</div>
                      </div>
                    </div>
                  </div>
                </div>
                <!-- ═══ FACTOR INJECTION PANEL ═══ -->
                <div v-if="!isFullscreenCode" class="mb-2 shrink-0">
                  <!-- Toggle header -->
                  <button
                    @click="showFactorPanel = !showFactorPanel"
                    class="w-full flex items-center justify-between px-3 py-1.5 bg-[#1A1E2B] border border-[#2E3348] rounded hover:border-[#3B9EFF]/30 hover:bg-[#3B9EFF]/3 transition-colors group"
                  >
                    <div class="flex items-center space-x-2">
                      <Connection class="w-3.5 h-3.5 text-[#3B9EFF]/55 group-hover:text-[#3B9EFF] transition-colors" />
                      <span class="text-[11px] font-mono text-[#94A3B8] group-hover:text-[#B4BAC9] uppercase tracking-wider transition-colors">因子仓库引用 (Factor Injection)</span>
                      <span v-if="injectedFactorList.length > 0" class="text-[10px] font-mono px-1.5 py-1 rounded-full bg-[#3B9EFF]/12 text-[#3B9EFF] border border-[#3B9EFF]/22">
                        {{ injectedFactorList.length }} 已注入
                      </span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <div v-if="!showFactorPanel && injectedFactorList.length > 0" class="flex items-center space-x-1 overflow-hidden max-w-[180px]">
                        <span
                          v-for="f in injectedFactorList.slice(0, 3)" :key="f.id"
                          class="text-[10px] font-mono text-[#3B9EFF] bg-[#3B9EFF]/8 border border-[#3B9EFF]/25 px-1.5 py-1 rounded whitespace-nowrap"
                        >{{ f.shortVar }}</span>
                        <span v-if="injectedFactorList.length > 3" class="text-[10px] font-mono text-[#94A3B8]">+{{ injectedFactorList.length - 3 }}</span>
                      </div>
                      <ArrowDown :class="cn('w-3 h-3 text-[#94A3B8] transition-transform duration-200', showFactorPanel ? 'rotate-180' : '')" />
                    </div>
                  </button>

                  <!-- Expanded panel -->
                  <Transition
                    enter-active-class="transition-all duration-200 ease-out"
                    enter-from-class="opacity-0 -translate-y-1"
                    enter-to-class="opacity-100 translate-y-0"
                    leave-active-class="transition-all duration-150 ease-in"
                    leave-from-class="opacity-100"
                    leave-to-class="opacity-0 -translate-y-1"
                  >
                    <div v-if="showFactorPanel" class="mt-1 bg-[#1A1E2B] border border-[#2E3348] rounded overflow-hidden">
                      <!-- Search -->
                      <div class="px-3 py-2 border-b border-[#252A3A] flex items-center space-x-2 bg-[#202431]">
                        <Search class="w-3 h-3 text-[#94A3B8] shrink-0" />
                        <input
                          v-model="factorSearchQuery"
                          placeholder="搜索因子名称 / 变量名..."
                          class="bg-transparent text-[#E8ECF4] text-xs font-mono outline-none placeholder-[#2E3348] flex-1"
                        />
                        <span class="text-[10px] font-mono text-[#94A3B8]">{{ filteredInjectableFactors.length }} 个</span>
                      </div>

                      <!-- Factor list -->
                      <div class="max-h-[160px] overflow-y-auto no-scrollbar">
                        <div
                          v-for="f in filteredInjectableFactors" :key="f.id"
                          @click="toggleFactor(f)"
                          :class="cn('flex items-center space-x-3 px-3 py-1.5 cursor-pointer transition-colors border-b border-[#202431] last:border-0 group/fi',
                            injectedFactorIds.has(f.id) ? 'bg-[#3B9EFF]/5' : 'hover:bg-[#202431]')"
                        >
                          <!-- Checkbox -->
                          <div :class="cn('w-3.5 h-3.5 rounded border flex items-center justify-center shrink-0 transition-colors',
                            injectedFactorIds.has(f.id) ? 'bg-[#3B9EFF] border-[#3B9EFF]' : 'border-[#2E3348] group-hover/fi:border-[#3B9EFF]/40')"
                          >
                            <Select v-if="injectedFactorIds.has(f.id)" class="w-2.5 h-2.5 text-white" />
                          </div>

                          <!-- Factor info -->
                          <div class="flex-1 min-w-0">
                            <div class="flex items-center space-x-2">
                              <span :class="cn('text-[11px] font-medium transition-colors', injectedFactorIds.has(f.id) ? 'text-[#E8ECF4]' : 'text-[#B4BAC9]')">{{ f.name }}</span>
                              <span :class="cn('text-[10px] font-mono px-1 py-1 rounded border shrink-0', FACTOR_CAT_COLOR[f.category] || 'text-[#94A3B8] bg-[#202431] border-[#2E3348]')">{{ f.category }}</span>
                            </div>
                            <span class="text-[10px] font-mono text-[#94A3B8] mt-0.5 block">${{ f.refVar }}</span>
                          </div>

                          <!-- Status -->
                          <div class="flex flex-col items-end shrink-0 space-y-0.5">
                            <span :class="cn('text-[10px] font-mono font-bold', injectedFactorIds.has(f.id) ? 'text-[#3B9EFF]' : 'text-[#94A3B8]')">
                              {{ injectedFactorIds.has(f.id) ? '✓ 已注入' : '+ 注入' }}
                            </span>
                            <span class="text-[10px] font-mono text-[#64748B]">↑ {{ f.updateDate }}</span>
                          </div>
                        </div>
                      </div>

                      <!-- Active injections footer -->
                      <div v-if="injectedFactorList.length > 0" class="px-3 py-1.5 border-t border-[#252A3A] bg-[#161922]">
                        <p class="text-[10px] font-mono text-[#94A3B8] mb-1.5 uppercase tracking-wider">已注入变量 → 代码 inputs 段</p>
                        <div class="flex flex-wrap gap-1.5">
                          <span
                            v-for="f in injectedFactorList" :key="f.id"
                            class="flex items-center space-x-1 text-[11px] font-mono text-[#3B9EFF] bg-[#3B9EFF]/8 border border-[#3B9EFF]/25 px-2 py-1 rounded cursor-default"
                            :title="`已更新至 ${f.updateDate}`"
                          >
                            <span>{{ f.shortVar }}</span>
                            <span class="text-[#3B9EFF]/30 text-[10px]">{{ f.updateDate }}</span>
                            <button @click.stop="toggleFactor(f)" class="text-[#3B9EFF]/30 hover:text-[#3B9EFF] ml-0.5 transition-colors">
                              <Close class="w-2 h-2" />
                            </button>
                          </span>
                        </div>
                      </div>
                    </div>
                  </Transition>
                </div>

                <!-- Vault Security Banner -->
                <div
                  v-if="selectedModel?.visibility === 'private' && !isFullscreenCode"
                  class="mb-1.5 shrink-0 flex items-center space-x-2 bg-[#00C9A7]/8 border border-[#00C9A7]/15 rounded px-2.5 py-1"
                >
                  <CircleCheckFilled class="w-3 h-3 text-[#00C9A7]/70 shrink-0" />
                  <p class="text-[10px] font-mono text-[#00C9A7]/60 flex-1 truncate">
                    <span class="text-[#00C9A7]/90 font-bold">🛡️ TEE 防护中</span>
                    <span class="text-[#00C9A7]/40 mx-1">·</span>策略代码已加密隔离，管理员无权读取
                  </p>
                  <span class="shrink-0 text-[7.5px] font-mono text-[#00C9A7]/50 bg-[#00C9A7]/8 border border-[#00C9A7]/12 px-1.5 py-1 rounded whitespace-nowrap">AES-256 · TEE ✓</span>
                </div>

                <!-- Code Display -->
                <div :class="cn('border border-[#2E3348] flex flex-col overflow-hidden', isFullscreenCode ? 'flex-1 rounded-none border-0' : 'flex-1 rounded')">
                  <div class="flex items-center justify-between px-3 py-2 bg-[#202431] border-b border-[#252A3A]">
                    <div class="flex items-center space-x-2">
                      <div class="flex space-x-1.5">
                        <div class="w-2.5 h-2.5 rounded-full bg-[#FF5F57]/50"></div>
                        <div class="w-2.5 h-2.5 rounded-full bg-[#FFBD2E]/50"></div>
                        <div class="w-2.5 h-2.5 rounded-full bg-[#28C840]/50"></div>
                      </div>
                      <div class="w-px h-3 bg-[#2E3348]"></div>
                      <CopyDocument class="w-3 h-3 text-[#3B9EFF]/60" />
                      <span class="text-[11px] font-mono text-[#94A3B8]">{{ selectedModel?.name }}</span>
                    </div>
                    <button @click="isFullscreenCode = !isFullscreenCode" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-1">
                      <ScaleToOriginal v-if="isFullscreenCode" class="w-[13px] h-[13px]" /><FullScreen v-else class="w-[13px] h-[13px]" />
                    </button>
                  </div>
                  <div class="flex-1 overflow-auto p-4 bg-[#0E1118] no-scrollbar">
                    <pre class="text-[13px] font-mono leading-relaxed text-[#C5C8C6]"><code>{{ mockPythonCode }}</code></pre>
                  </div>
                </div>
              </div>

              <!-- AI Chat -->
              <div v-else-if="selectedModel?.type === 'ai'" class="flex-1 flex flex-col bg-[#161922]">
                <div class="flex-1 overflow-y-auto p-4 space-y-3 no-scrollbar" ref="chatContainerRef">
                  <div v-for="(msg, idx) in chatMessages" :key="idx" :class="cn('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')">
                    <div :class="cn('max-w-[88%] rounded p-3 flex items-start space-x-2.5', msg.role === 'user' ? 'bg-[#3B9EFF]/12 border border-[#3B9EFF]/22 text-[#E8ECF4]' : 'bg-[#202431] border border-[#2E3348] text-[#B4BAC9]')">
                      <StarFilled v-if="msg.role === 'ai'" class="w-3.5 h-3.5 text-purple-400/80 shrink-0 mt-0.5" />
                      <div class="text-[13px] leading-relaxed whitespace-pre-wrap">{{ msg.text }}</div>
                    </div>
                  </div>
                  <!-- Typing indicator -->
                  <div v-if="isRunning" class="flex justify-start">
                    <div class="bg-[#202431] border border-[#2E3348] rounded p-3 flex items-center space-x-2.5 text-[#94A3B8]">
                      <TrendCharts class="w-3.5 h-3.5 text-purple-400 animate-spin shrink-0" />
                      <span class="text-[13px] animate-pulse">Alpha Mind 正在生成策略代码...</span>
                    </div>
                  </div>
                </div>
                <div class="px-3 py-2.5 bg-[#1A1E2B] border-t border-[#252A3A]">
                  <div class="relative">
                    <textarea
                      v-model="chatInput"
                      @keydown.enter.exact.prevent="handleSendChat"
                      placeholder="例如：当沪深300指数20日均线上穿60日均线且RSI小于30时买入，等权分配..."
                      class="w-full bg-[#161922] border border-[#2E3348] rounded pl-3 pr-10 py-2 text-[13px] text-[#E8ECF4] focus:border-[#3B9EFF]/50 focus:outline-none resize-none h-20 transition-colors placeholder-[#2E3348]"
                    />
                    <button
                      @click="handleSendChat"
                      :disabled="!chatInput.trim() || isRunning"
                      class="absolute bottom-2.5 right-2.5 p-1.5 bg-purple-700 hover:bg-purple-600 disabled:bg-[#202431] disabled:text-[#94A3B8] text-white rounded transition-colors"
                    >
                      <Promotion class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ═══ RIGHT PANEL: Terminal & Output ═══ -->
          <div :class="cn('flex flex-col bg-[#161922] shrink-0 transition-all duration-300', (isFullscreenLog || isFullscreenOutput) ? 'absolute inset-0 z-50 w-full' : 'w-[420px]')">

            <!-- Log Panel -->
            <div :class="cn('flex flex-col border-b border-[#252A3A] transition-all duration-300', isFullscreenOutput ? 'hidden' : isFullscreenLog ? 'h-full' : 'h-1/3')">
              <div class="px-3 py-2 border-b border-[#252A3A] bg-[#1A1E2B] flex items-center justify-between shrink-0">
                <div class="flex items-center">
                  <span class="am-title-l3 uppercase tracking-widest">
                    <div class="am-title-bar"></div>{{ selectedModel?.type === 'ai' ? 'Alpha Mind 推理日志' : 'Console Log' }}
                  </span>
                  <div v-if="isRunning" class="ml-2 w-1.5 h-1.5 rounded-full bg-[#3B9EFF] animate-pulse"></div>
                </div>
                <button @click="isFullscreenLog = !isFullscreenLog" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-1">
                  <ScaleToOriginal v-if="isFullscreenLog" class="w-3 h-3" /><FullScreen v-else class="w-3 h-3" />
                </button>
              </div>
              <div class="flex-1 overflow-y-auto p-3 bg-[#0E1118] font-mono text-[11px] space-y-1 no-scrollbar">
                <div v-for="(log, i) in logs" :key="i" :class="logColor(log)">{{ log }}</div>
                <div v-if="isRunning" class="text-[#3B9EFF] animate-pulse">_</div>
              </div>
            </div>

            <!-- Output Panel -->
            <div :class="cn('flex flex-col relative transition-all duration-300', isFullscreenLog ? 'hidden' : isFullscreenOutput ? 'h-full' : 'h-2/3')">
              <div class="px-3 py-2 border-b border-[#252A3A] bg-[#1A1E2B] flex items-center justify-between shrink-0">
                <div class="flex items-center">
                  <span class="am-title-l3 uppercase tracking-widest"><div class="am-title-bar"></div>输出结果与映射区</span>
                </div>
              <div class="flex items-center space-x-2.5">
                  <span v-if="outputData.length > 0" class="text-[10px] bg-[#00C9A7]/10 text-[#00C9A7] px-2 py-1 rounded border border-[#00C9A7]/20 flex items-center font-mono">
                    <CircleCheckFilled class="w-[9px] h-[9px] mr-1" /> 计算完成
                  </span>
                  <!-- status badge only in header -->
                  <button @click="isFullscreenOutput = !isFullscreenOutput" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-1">
                    <ScaleToOriginal v-if="isFullscreenOutput" class="w-3 h-3" /><FullScreen v-else class="w-3 h-3" />
                  </button>
                </div>
              </div>

              <div class="flex-1 overflow-y-auto p-3 bg-[#161922] flex flex-col no-scrollbar">
                <!-- AI model: generated code viewer -->
                <template v-if="selectedModel?.type === 'ai'">
                  <div v-if="aiGeneratedCode" class="flex flex-col flex-1 overflow-hidden rounded border border-[#2E3348]">
                    <div class="flex items-center justify-between px-3 py-2 bg-[#202431] border-b border-[#252A3A] shrink-0">
                      <div class="flex items-center space-x-2">
                        <div class="flex space-x-1.5">
                          <div class="w-2.5 h-2.5 rounded-full bg-[#FF5F57]/50"></div>
                          <div class="w-2.5 h-2.5 rounded-full bg-[#FFBD2E]/50"></div>
                          <div class="w-2.5 h-2.5 rounded-full bg-[#28C840]/50"></div>
                        </div>
                        <span class="text-[10px] font-mono text-[#94A3B8] tracking-wider">python · alpha_mind_generated.py</span>
                      </div>
                      <span class="text-[10px] bg-purple-900/20 text-purple-400/70 border border-purple-500/18 px-1.5 py-1 rounded font-mono">AM-generated</span>
                    </div>
                    <div class="flex-1 overflow-auto p-4 bg-[#0E1118] no-scrollbar">
                      <pre class="text-xs font-mono leading-relaxed text-[#C5C8C6]"><code>{{ aiGeneratedCode }}</code></pre>
                    </div>
                  </div>
                  <div v-else class="flex-1 flex flex-col items-center justify-center space-y-2">
                    <StarFilled class="w-7 h-7 opacity-15 text-purple-500" />
                    <span class="text-[11px] font-mono text-[#94A3B8]">向 Alpha Mind 发送策略描述后，代码将在此生成</span>
                  </div>
                </template>
                <template v-else-if="outputData.length > 0">
                  <div class="mb-4">
                    <h4 class="am-title-l3 mb-2 uppercase tracking-wider"><div class="am-title-bar"></div>结构化权重数据</h4>
                    <div class="bg-[#1A1E2B] border border-[#2E3348] rounded overflow-hidden">
                      <table class="w-full text-left border-collapse">
                        <thead class="sticky top-0 z-10 bg-[#202431]">
                          <tr class="border-b border-[#2E3348]">
                            <th v-if="isFromWorkbench" class="px-3 py-1.5 text-[10px] font-semibold text-[#94A3B8] uppercase w-10 text-center">映射</th>
                            <th class="px-3 py-1.5 text-[10px] font-semibold text-[#94A3B8] uppercase tracking-wider">资产类别</th>
                            <th class="px-3 py-1.5 text-[10px] font-semibold text-[#94A3B8] uppercase tracking-wider">标的代码</th>
                            <th class="px-3 py-1.5 text-[10px] font-semibold text-[#94A3B8] uppercase tracking-wider text-right">建议权重</th>
                          </tr>
                        </thead>
                        <tbody class="text-[13px] font-mono divide-y divide-[#252A3A]">
                          <tr v-for="(row, i) in outputData" :key="i" class="hover:bg-[#202431] transition-colors">
                            <td v-if="isFromWorkbench" class="px-3 py-1.5 text-center">
                              <input type="checkbox" :checked="!!mappedParams[row.id]" @change="toggleMapping(row.id)" class="accent-[#3B9EFF]" />
                            </td>
                            <td class="px-3 py-1.5 text-[#B4BAC9]">{{ row.class }}</td>
                            <td class="px-3 py-1.5 text-[#E8ECF4]">{{ row.ticker }}</td>
                            <td class="px-3 py-1.5 text-[#3B9EFF] font-bold text-right">{{ row.weight }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div v-if="outputFiles.length > 0">
                    <h4 class="am-title-l3 mb-2 uppercase tracking-wider"><div class="am-title-bar"></div>非结构化输出 (文件/数据包)</h4>
                    <div class="space-y-1">
                      <div v-for="(file, idx) in outputFiles" :key="idx" class="flex items-center justify-between bg-[#1A1E2B] border border-[#2E3348] p-2 rounded hover:border-[#3E4660] transition-colors">
                        <div class="flex items-center">
                          <Document class="w-3 h-3 text-[#94A3B8] mr-2" />
                          <span class="text-[13px] text-[#B4BAC9]">{{ file.name }}</span>
                          <span class="text-[10px] text-[#94A3B8] ml-2 font-mono">({{ file.size }})</span>
                        </div>
                        <button class="text-[#3B9EFF]/60 hover:text-[#3B9EFF] transition-colors" title="下载">
                          <Download class="w-[13px] h-[13px]" />
                        </button>
                      </div>
                    </div>
                  </div>
                </template>
                <div v-else-if="selectedModel?.type !== 'ai'" class="flex-1 flex flex-col items-center justify-center text-[#64748B]">
                  <Histogram class="w-7 h-7 mb-2 opacity-40" />
                  <span class="text-[11px] font-mono text-[#94A3B8]">暂无输出数据</span>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="px-3 py-2.5 bg-[#1A1E2B] border-t border-[#252A3A] space-y-1.5 shrink-0">
                <!-- AI model buttons -->
                <template v-if="selectedModel?.type === 'ai'">
                  <button
                    :disabled="!aiGeneratedCode"
                    class="w-full py-1.5 bg-[#202431] hover:bg-[#2A2E3D] disabled:opacity-40 disabled:cursor-not-allowed text-[#B4BAC9] text-[13px] font-semibold rounded flex items-center justify-center transition-colors border border-[#2E3348]"
                  >
                    <Operation class="w-[13px] h-[13px] mr-2" /> 🐛 模型调试
                  </button>
                  <button
                    :disabled="!aiGeneratedCode"
                    @click="handleSaveToMyModels"
                    class="w-full py-1.5 bg-purple-700 hover:bg-purple-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-[13px] font-semibold rounded flex items-center justify-center space-x-2 transition-colors"
                  >
                    <DocumentAdd class="w-[13px] h-[13px]" /><span>💾 保存到我的模型</span>
                  </button>
                </template>
                <!-- Classic / Custom model buttons -->
                <template v-else>
                <button :disabled="outputData.length === 0" class="w-full py-1.5 bg-[#202431] hover:bg-[#2A2E3D] disabled:opacity-40 disabled:cursor-not-allowed text-[#B4BAC9] text-[13px] font-semibold rounded flex items-center justify-center transition-colors border border-[#2E3348]">
                  <DocumentAdd class="w-[13px] h-[13px] mr-2" /> 保存结果
                </button>
                <!-- Push button: single direct button when context is set, dropdown when both options available -->
                <!-- ── Single-option mode (from workbench) ── -->
                <template v-if="allowedPushTarget !== null">
                  <button
                    :disabled="outputData.length === 0"
                    @click="handlePushTo(allowedPushTarget!)"
                    :class="cn('w-full py-1.5 text-white text-[13px] font-semibold rounded flex items-center justify-center space-x-2 transition-colors disabled:opacity-40 disabled:cursor-not-allowed',
                      allowedPushTarget === 'allocation'
                        ? 'bg-[#3B9EFF] hover:bg-[#5CB3FF]'
                        : 'bg-purple-700 hover:bg-purple-600')"
                  >
                    <TrendCharts v-if="allowedPushTarget === 'allocation'" class="w-3.5 h-3.5" />
                    <DataAnalysis v-else class="w-3.5 h-3.5" />
                    <span>🚀 {{ allowedPushTarget === 'allocation' ? '推送至资配模型' : '推送至策略模型' }}</span>
                  </button>
                </template>

                <!-- ── Multi-option mode (direct entry, no workbench context) ── -->
                <div v-else class="relative">
                  <button
                    :disabled="outputData.length === 0"
                    @click="showPushDropdown = !showPushDropdown"
                    class="w-full py-1.5 bg-[#3B9EFF] hover:bg-[#5CB3FF] disabled:opacity-40 disabled:cursor-not-allowed text-white text-[13px] font-semibold rounded flex items-center justify-center space-x-2 transition-colors"
                  >
                    <Promotion class="w-3.5 h-3.5" />
                    <span>🚀 推送模型结果至...</span>
                    <ArrowDown :class="cn('w-3 h-3 transition-transform duration-200', showPushDropdown ? 'rotate-180' : '')" />
                  </button>
                  <Transition
                    enter-active-class="transition-all duration-200 ease-out"
                    enter-from-class="opacity-0 translate-y-1 scale-95"
                    enter-to-class="opacity-100 translate-y-0 scale-100"
                    leave-active-class="transition-all duration-150 ease-in"
                    leave-from-class="opacity-100"
                    leave-to-class="opacity-0 translate-y-1"
                  >
                    <div
                      v-if="showPushDropdown"
                      class="absolute bottom-full left-0 right-0 mb-1.5 bg-[#202431] border border-[#2E3348] rounded overflow-hidden z-20"
                    >
                      <button
                        @click="handlePushTo('allocation')"
                        class="w-full flex items-center px-3 py-2 text-[13px] text-[#E8ECF4] hover:bg-[#3B9EFF]/8 hover:text-[#3B9EFF] transition-colors border-b border-[#252A3A]"
                      >
                        <TrendCharts class="w-3.5 h-3.5 mr-2.5 text-[#3B9EFF]/55" />
                        <div class="text-left">
                          <div class="font-semibold">推送至资配模型</div>
                          <div class="text-[10px] text-[#94A3B8] font-mono mt-0.5">作为资产配置模型的输入参数</div>
                        </div>
                      </button>
                      <button
                        @click="handlePushTo('strategy')"
                        class="w-full flex items-center px-3 py-2 text-[13px] text-[#E8ECF4] hover:bg-purple-900/10 hover:text-purple-400 transition-colors"
                      >
                        <DataAnalysis class="w-3.5 h-3.5 mr-2.5 text-purple-500/50" />
                        <div class="text-left">
                          <div class="font-semibold">推送至策略模型</div>
                          <div class="text-[10px] text-[#94A3B8] font-mono mt-0.5">作为量化策略的权重初始解</div>
                        </div>
                      </button>
                    </div>
                  </Transition>
                </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ APPLY WEIGHTS CONFIRMATION MODAL ═══ -->
    <Transition
      enter-active-class="transition-all duration-250 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="showApplyModal" class="fixed inset-0 bg-black/80 z-[60] flex items-center justify-center">
        <div class="bg-[#202431] border border-[#2E3348] rounded w-[660px] max-w-[95vw] flex flex-col overflow-hidden">

          <!-- Header -->
          <div class="px-5 py-4 bg-[#1A1E2B] border-b border-[#2E3348] flex items-start justify-between">
            <div>
              <div class="flex items-center space-x-2 mb-1">
                <div class="w-6 h-6 rounded bg-[#3B9EFF]/12 border border-[#3B9EFF]/25 flex items-center justify-center">
                  <Lightning class="w-3.5 h-3.5 text-[#3B9EFF]" />
                </div>
                <h3 class="am-title-l3">应用模型权重至意向组合</h3>
              </div>
              <p class="text-[11px] font-mono text-[#94A3B8] ml-8">
                <span class="text-[#3B9EFF]/70">{{ selectedModel?.name }}</span>
                &nbsp;·&nbsp; 建议调仓 Diff &nbsp;·&nbsp; 覆盖后请在工作台核查权重合计
              </p>
            </div>
            <button @click="showApplyModal = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-1 rounded hover:bg-[#2E3348] mt-0.5 shrink-0">
              <Close class="w-4 h-4" />
            </button>
          </div>

          <!-- Diff Body -->
          <div class="px-5 py-4 space-y-3">

            <!-- Column header -->
            <div class="flex items-center text-[10px] font-mono text-[#94A3B8] uppercase tracking-widest px-3">
              <span class="flex-1">资产类别</span>
              <span class="w-20 text-center">当前权重</span>
              <span class="w-6"></span>
              <span class="w-20 text-center">模型建议</span>
              <span class="w-24 text-right">调整幅度</span>
            </div>

            <!-- Buy (增配) -->
            <div>
              <div class="text-[10px] font-semibold text-[#00C9A7]/60 uppercase tracking-widest mb-1.5 font-mono px-1">↑ 增配</div>
              <div class="space-y-1">
                <div
                  v-for="item in BL_APPLY_DIFFS.filter(d => d.pos)" :key="item.label"
                  class="flex items-center bg-[#00C9A7]/5 border border-[#00C9A7]/12 rounded px-3 py-2 hover:border-[#00C9A7]/20 transition-colors"
                >
                  <div class="w-4 h-4 rounded bg-[#00C9A7]/10 border border-[#00C9A7]/18 flex items-center justify-center mr-2.5 shrink-0">
                    <ArrowUp class="w-2 h-2 text-[#00C9A7]" />
                  </div>
                  <span class="text-[13px] text-[#B4BAC9] flex-1">{{ item.label }}</span>
                  <span class="w-20 text-center text-[13px] font-mono text-[#94A3B8]">{{ item.from }}</span>
                  <span class="w-6 text-center text-[#64748B] font-mono text-[13px]">→</span>
                  <span class="w-20 text-center text-[13px] font-mono text-[#E8ECF4]">{{ item.to }}</span>
                  <span class="w-24 text-right text-[13px] font-bold font-mono text-[#00C9A7]">{{ item.diff }}</span>
                </div>
              </div>
            </div>

            <!-- Sell (减配) -->
            <div>
              <div class="text-[10px] font-semibold text-[#FF5630]/50 uppercase tracking-widest mb-1.5 font-mono px-1">↓ 减配</div>
              <div class="space-y-1">
                <div
                  v-for="item in BL_APPLY_DIFFS.filter(d => !d.pos)" :key="item.label"
                  class="flex items-center bg-[#FF5630]/5 border border-[#FF5630]/12 rounded px-3 py-2 hover:border-[#FF5630]/20 transition-colors"
                >
                  <div class="w-4 h-4 rounded bg-[#FF5630]/10 border border-[#FF5630]/18 flex items-center justify-center mr-2.5 shrink-0">
                    <ArrowDown class="w-2 h-2 text-[#FF5630]" />
                  </div>
                  <span class="text-[13px] text-[#B4BAC9] flex-1">{{ item.label }}</span>
                  <span class="w-20 text-center text-[13px] font-mono text-[#94A3B8]">{{ item.from }}</span>
                  <span class="w-6 text-center text-[#64748B] font-mono text-[13px]">→</span>
                  <span class="w-20 text-center text-[13px] font-mono text-[#E8ECF4]">{{ item.to }}</span>
                  <span class="w-24 text-right text-[13px] font-bold font-mono text-[#FF5630]">{{ item.diff }}</span>
                </div>
              </div>
            </div>

            <!-- Total -->
            <div class="flex items-center justify-between bg-[#1A1E2B] border border-[#2E3348] rounded px-4 py-2 text-[11px] font-mono">
              <span class="text-[#94A3B8]">权重合计变化</span>
              <span class="text-[#00C9A7] font-bold">± 0.0%  ·  覆盖后仍维持 100.0%</span>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-5 py-3 border-t border-[#2E3348] bg-[#1A1E2B] flex items-center justify-between">
            <div class="flex items-center space-x-1.5 text-[11px] text-[#94A3B8] font-mono">
              <InfoFilled class="w-3 h-3 text-[#94A3B8]/60 shrink-0" />
              <span>覆盖仅影响「意向组合」，不直接触发交易指令</span>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="showApplyModal = false"
                class="px-3 py-1.5 rounded text-[13px] text-[#B4BAC9] hover:text-[#E8ECF4] transition-colors border border-[#2E3348] hover:border-[#3E4660]"
              >取消</button>
              <button
                @click="confirmApplyWeights"
                :disabled="isApplying"
                class="bg-[#3B9EFF] hover:bg-[#5CB3FF] disabled:opacity-60 disabled:cursor-wait text-white px-5 py-1.5 rounded text-[13px] font-semibold transition-colors flex items-center min-w-[160px] justify-center"
              >
                <template v-if="isApplying">
                  <span class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2 shrink-0"></span>
                  写入权重并跳转...
                </template>
                <template v-else>
                  <ArrowRight class="w-3.5 h-3.5 mr-2" /> 确认覆盖，跳转至资配工作台
                </template>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ═══ PUSH TO MODEL CONFIRMATION MODAL ═══ -->
    <Transition
      enter-active-class="transition-all duration-250 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="showPushModal" class="fixed inset-0 bg-black/80 z-[60] flex items-center justify-center">
        <div class="bg-[#202431] border border-[#2E3348] rounded w-[660px] max-w-[95vw] flex flex-col overflow-hidden">

          <!-- Header -->
          <div class="px-5 py-4 bg-[#1A1E2B] border-b border-[#2E3348] flex items-start justify-between">
            <div>
              <div class="flex items-center space-x-2 mb-1">
                <div :class="cn('w-6 h-6 rounded flex items-center justify-center', pushModalTarget === 'allocation' ? 'bg-[#3B9EFF]/12 border border-[#3B9EFF]/25' : 'bg-purple-500/12 border border-purple-500/22')">
                  <TrendCharts v-if="pushModalTarget === 'allocation'" class="w-3.5 h-3.5 text-[#3B9EFF]" />
                  <DataAnalysis v-else class="w-3.5 h-3.5 text-purple-400" />
                </div>
                <h3 class="am-title-l1">
                  {{ pushModalTarget === 'allocation' ? '推送至资配模型' : '推送至策略模型' }}
                </h3>
              </div>
              <p class="text-[11px] font-mono text-[#94A3B8] ml-8">
                <span :class="pushModalTarget === 'allocation' ? 'text-[#3B9EFF]/70' : 'text-purple-400/70'">{{ selectedModel?.name }}</span>
                &nbsp;·&nbsp; 建议调仓 Diff &nbsp;·&nbsp;
                {{ pushModalTarget === 'allocation' ? '作为资产配置模型的输入参数' : '作为量化策略的权重初始解' }}
              </p>
            </div>
            <button @click="showPushModal = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-1 rounded hover:bg-[#2E3348] mt-0.5 shrink-0">
              <Close class="w-4 h-4" />
            </button>
          </div>

          <!-- Diff Body -->
          <div class="px-5 py-4 space-y-3">
            <div class="flex items-center text-[10px] font-mono text-[#94A3B8] uppercase tracking-widest px-3">
              <span class="flex-1">资产类别</span>
              <span class="w-20 text-center">当前权重</span>
              <span class="w-6"></span>
              <span class="w-20 text-center">模型建议</span>
              <span class="w-24 text-right">调整幅度</span>
            </div>
            <!-- Buy rows -->
            <div>
              <div class="text-[10px] font-semibold text-[#00C9A7]/60 uppercase tracking-widest mb-1.5 font-mono px-1">↑ 增配</div>
              <div class="space-y-1">
                <div
                  v-for="item in BL_APPLY_DIFFS.filter(d => d.pos)" :key="item.label"
                  class="flex items-center bg-[#00C9A7]/5 border border-[#00C9A7]/12 rounded px-3 py-2 hover:border-[#00C9A7]/20 transition-colors"
                >
                  <div class="w-4 h-4 rounded bg-[#00C9A7]/10 border border-[#00C9A7]/18 flex items-center justify-center mr-2.5 shrink-0">
                    <ArrowUp class="w-2 h-2 text-[#00C9A7]" />
                  </div>
                  <span class="text-[13px] text-[#B4BAC9] flex-1">{{ item.label }}</span>
                  <span class="w-20 text-center text-[13px] font-mono text-[#94A3B8]">{{ item.from }}</span>
                  <span class="w-6 text-center text-[#64748B] font-mono text-[13px]">→</span>
                  <span class="w-20 text-center text-[13px] font-mono text-[#E8ECF4]">{{ item.to }}</span>
                  <span class="w-24 text-right text-[13px] font-bold font-mono text-[#00C9A7]">{{ item.diff }}</span>
                </div>
              </div>
            </div>
            <!-- Sell rows -->
            <div>
              <div class="text-[10px] font-semibold text-[#FF5630]/50 uppercase tracking-widest mb-1.5 font-mono px-1">↓ 减配</div>
              <div class="space-y-1">
                <div
                  v-for="item in BL_APPLY_DIFFS.filter(d => !d.pos)" :key="item.label"
                  class="flex items-center bg-[#FF5630]/5 border border-[#FF5630]/12 rounded px-3 py-2 hover:border-[#FF5630]/20 transition-colors"
                >
                  <div class="w-4 h-4 rounded bg-[#FF5630]/10 border border-[#FF5630]/18 flex items-center justify-center mr-2.5 shrink-0">
                    <ArrowDown class="w-2 h-2 text-[#FF5630]" />
                  </div>
                  <span class="text-[13px] text-[#B4BAC9] flex-1">{{ item.label }}</span>
                  <span class="w-20 text-center text-[13px] font-mono text-[#94A3B8]">{{ item.from }}</span>
                  <span class="w-6 text-center text-[#64748B] font-mono text-[13px]">→</span>
                  <span class="w-20 text-center text-[13px] font-mono text-[#E8ECF4]">{{ item.to }}</span>
                  <span class="w-24 text-right text-[13px] font-bold font-mono text-[#FF5630]">{{ item.diff }}</span>
                </div>
              </div>
            </div>
            <!-- Total -->
            <div class="flex items-center justify-between bg-[#1A1E2B] border border-[#2E3348] rounded px-4 py-2 text-[11px] font-mono">
              <span class="text-[#94A3B8]">权重合计变化</span>
              <span class="text-[#00C9A7] font-bold">± 0.0%  ·  覆盖后仍维持 100.0%</span>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-5 py-3 border-t border-[#2E3348] bg-[#1A1E2B] flex items-center justify-between">
            <div class="flex items-center space-x-1.5 text-[11px] text-[#94A3B8] font-mono">
              <InfoFilled class="w-3 h-3 text-[#94A3B8]/60 shrink-0" />
              <span>{{ pushModalTarget === 'allocation' ? '推送仅影响资配模型参数，不直接触发交易指令' : '推送仅作为策略模型的初始权重参考' }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click="showPushModal = false"
                class="px-3 py-1.5 rounded text-[13px] text-[#B4BAC9] hover:text-[#E8ECF4] transition-colors border border-[#2E3348] hover:border-[#3E4660]"
              >取消</button>
              <button
                @click="confirmPushAndReturn"
                :disabled="isPushingBack"
                :class="cn('text-white px-5 py-1.5 rounded text-[13px] font-semibold transition-colors flex items-center min-w-[160px] justify-center disabled:opacity-60 disabled:cursor-wait',
                  pushModalTarget === 'allocation'
                    ? 'bg-[#3B9EFF] hover:bg-[#5CB3FF]'
                    : 'bg-purple-700 hover:bg-purple-600')"
              >
                <template v-if="isPushingBack">
                  <span class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2 shrink-0"></span>
                  推送并跳转回工作台...
                </template>
                <template v-else>
                  <ArrowRight class="w-3.5 h-3.5 mr-2" />
                  {{ pushModalTarget === 'allocation' ? '确认推送至资配模型' : '确认推送至策略模型' }}
                </template>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ═══ API MAPPING MODAL ═══ -->
    <div v-if="showApiModal" class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center">
      <div class="bg-[#202431] border border-[#2E3348] rounded w-[580px] flex flex-col overflow-hidden max-h-[80vh]">
        <div class="px-4 py-3 border-b border-[#2E3348] flex justify-between items-center bg-[#1A1E2B] shrink-0">
          <h3 class="am-title-l2"><div class="am-title-bar"></div>配置数据源映射
            <span class="text-[#3B9EFF] ml-2 font-mono text-[13px] bg-[#3B9EFF]/10 px-2 py-1 rounded border border-[#3B9EFF]/20">{{ currentMappingKey }}</span>
          </h3>
          <button @click="showApiModal = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-1 rounded hover:bg-[#2E3348]"><Close class="w-[14px] h-[14px]" /></button>
        </div>

        <div class="p-4 flex-1 overflow-y-auto space-y-4 no-scrollbar">
          <!-- Source Selection -->
          <div>
            <label class="block text-[11px] font-semibold text-[#94A3B8] mb-1.5 uppercase tracking-widest">1. 选择数据源 (API)</label>
            <div class="grid grid-cols-2 gap-1.5">
              <button
                v-for="source in allApiSources" :key="source"
                @click="modalSource = source; modalTable = ''; modalField = []"
                :class="cn('px-3 py-2 text-[13px] rounded border transition-colors text-left', modalSource === source ? 'bg-[#3B9EFF]/12 border-[#3B9EFF]/30 text-[#3B9EFF]' : 'bg-[#161922] border-[#2E3348] text-[#B4BAC9] hover:border-[#3E4660] hover:text-[#E8ECF4]')"
              >{{ source }}</button>
            </div>
          </div>

          <template v-if="modalSource !== '自定义输入 (Manual)'">
            <!-- Table Selection -->
            <div>
              <label class="block text-[11px] font-semibold text-[#94A3B8] mb-1.5 uppercase tracking-widest">2. 选择数据表</label>
              <div class="space-y-1">
                <button
                  v-for="table in apiTablesForSource" :key="table.id"
                  @click="modalTable = table.name; modalField = []"
                  :class="cn('w-full px-3 py-2 text-[13px] rounded border transition-colors text-left', modalTable === table.name ? 'bg-[#3B9EFF]/12 border-[#3B9EFF]/30 text-[#3B9EFF]' : 'bg-[#161922] border-[#2E3348] text-[#B4BAC9] hover:border-[#3E4660] hover:text-[#E8ECF4]')"
                >
                  <span class="font-mono text-[11px] text-[#94A3B8]">{{ table.id }}</span>
                  <span class="ml-2">{{ table.name }}</span>
                </button>
              </div>
            </div>

            <!-- Field Selection -->
            <div v-if="modalTable">
              <label class="block text-[11px] font-semibold text-[#94A3B8] mb-1.5 uppercase tracking-widest">3. 选择字段 (可多选)</label>
              <div class="flex flex-wrap gap-1.5 p-3 bg-[#161922] border border-[#2E3348] rounded">
                <button
                  v-for="field in apiFieldsForTable" :key="field"
                  @click="toggleModalField(field)"
                  :class="cn('px-2 py-1 text-[11px] rounded border transition-colors font-mono', modalField.includes(field) ? 'bg-[#3B9EFF]/12 border-[#3B9EFF]/30 text-[#3B9EFF]' : 'bg-[#202431] border-[#2E3348] text-[#94A3B8] hover:border-[#3E4660] hover:text-[#B4BAC9]')"
                >
                  <Select v-if="modalField.includes(field)" class="w-[9px] h-[9px] inline mr-1" />{{ field }}
                </button>
              </div>
            </div>
          </template>

          <!-- Manual Input -->
          <div v-else>
            <label class="block text-[11px] font-semibold text-[#94A3B8] mb-1.5 uppercase tracking-widest">自定义输入值</label>
            <input v-model="modalManualValue" type="text" placeholder="输入静态值或 Python 表达式..." class="w-full operable-zone text-[#E8ECF4] text-[13px] rounded px-3 py-2 focus:outline-none" />
          </div>
        </div>

        <div class="px-4 py-3 border-t border-[#2E3348] bg-[#1A1E2B] flex justify-end space-x-2 shrink-0">
          <button @click="showApiModal = false" class="px-3 py-1.5 rounded text-[13px] text-[#B4BAC9] hover:text-[#E8ECF4] transition-colors border border-[#2E3348]">取消</button>
          <button @click="saveApiMapping" class="bg-[#3B9EFF] hover:bg-[#5CB3FF] text-white px-4 py-1.5 rounded text-[13px] font-semibold transition-colors">确认映射</button>
        </div>
      </div>
    </div>

    <!-- ═══ UPLOAD MODAL ═══ -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center">
      <div class="bg-[#202431] border border-[#2E3348] rounded w-[480px] overflow-hidden">
        <div class="px-4 py-3 border-b border-[#2E3348] flex justify-between items-center bg-[#1A1E2B]">
          <h3 class="am-title-l2"><div class="am-title-bar"></div>上传自定义模型</h3>
          <button @click="showUploadModal = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-1 rounded hover:bg-[#2E3348]"><Close class="w-[14px] h-[14px]" /></button>
        </div>
        <div class="p-4 space-y-3">
          <div class="border border-dashed border-[#2E3348] rounded p-7 text-center hover:border-[#3B9EFF]/35 hover:bg-[#3B9EFF]/3 transition-colors cursor-pointer group">
            <UploadFilled class="w-6 h-6 mx-auto mb-2.5 text-[#94A3B8] group-hover:text-[#3B9EFF]/55 transition-colors" />
            <p class="text-[13px] text-[#B4BAC9]">点击或拖拽 Python (.py) 文件至此处</p>
            <p class="text-[11px] text-[#94A3B8] mt-1">支持 .py 文件，最大 10MB</p>
          </div>
          <div>
            <label class="block text-[11px] text-[#94A3B8] mb-1 uppercase tracking-wider font-mono">模型名称</label>
            <input type="text" v-model="uploadName" placeholder="例如: My_Strategy_v1.py" class="w-full operable-zone text-[#E8ECF4] text-[13px] rounded px-3 py-2 focus:outline-none placeholder-[#2E3348]" />
          </div>
        </div>
        <div class="px-4 py-3 border-t border-[#2E3348] bg-[#1A1E2B] flex justify-end space-x-2">
          <button @click="showUploadModal = false" class="px-3 py-1.5 rounded text-[13px] text-[#B4BAC9] hover:text-[#E8ECF4] transition-colors border border-[#2E3348]">取消</button>
          <button class="bg-[#3B9EFF] hover:bg-[#5CB3FF] text-white px-4 py-1.5 rounded text-[13px] font-semibold transition-colors">上传</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, watch, onMounted } from 'vue';
import {
  Monitor, EditPen, Setting as SettingsIcon, DataAnalysis, VideoPlay, Cpu, Grid,
  ArrowRight, ArrowLeft, TrendCharts, CopyDocument, Files, StarFilled, CircleCheckFilled,
  Operation, Connection, Histogram, UploadFilled, User, UserFilled,
  FullScreen, ScaleToOriginal, Promotion, Document, Download, Search,
  DocumentAdd, Hide, View, Close, ArrowDown, ArrowUp, Select,
  Trophy, Lock, Lightning, Share, Link, OfficeBuilding, InfoFilled
} from '@element-plus/icons-vue';
import { sharedIntentState } from '../store/intentStore';
import { modelBackPath, addToBasket } from '../store/demoStore';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

// ── Static Data ──────────────────────────────────────────────────────────────
const MODEL_INPUTS = [
  { key: 'market_caps', type: 'pd.Series' },
  { key: 'cov_matrix', type: 'pd.DataFrame' },
  { key: 'views', type: 'dict' }
];
const MODEL_OUTPUTS = [
  { key: 'optimal_weights', type: 'dict', desc: '最优资产权重字典' },
  { key: 'metrics_report', type: 'pd.DataFrame', desc: '组合风险收益指标报告' }
];

// ── Factor Injection ──────────────────────────────────────────────────────────
interface InjectableFactor {
  id: string; name: string; refVar: string; shortVar: string;
  category: string; updateDate: string;
}

const INJECTABLE_FACTORS: InjectableFactor[] = [
  { id: 'F001', name: '股息率因子',        refVar: 'factor.equity.div_yield',       shortVar: 'div_yield',         category: '红利', updateDate: '2026-03-31' },
  { id: 'F002', name: '股息持续性因子',    refVar: 'factor.equity.div_consistency', shortVar: 'div_consistency',   category: '红利', updateDate: '2026-03-31' },
  { id: 'F003', name: '历史波动率因子',    refVar: 'factor.risk.hist_vol_60d',      shortVar: 'hist_vol_60d',      category: '低波', updateDate: '2026-03-30' },
  { id: 'F005', name: 'ROE因子',           refVar: 'factor.quality.roe_ttm',        shortVar: 'roe_ttm',           category: '质量', updateDate: '2026-03-31' },
  { id: 'F006', name: '资产负债率因子',    refVar: 'factor.quality.debt_ratio',     shortVar: 'debt_ratio',        category: '质量', updateDate: '2026-03-31' },
  { id: 'F007', name: '市盈率因子 (EP)',   refVar: 'factor.value.ep_ttm',           shortVar: 'ep_ttm',            category: '价值', updateDate: '2026-03-31' },
  { id: 'F010', name: '12-1月价格动量',    refVar: 'factor.momentum.mom_12_1m',     shortVar: 'mom_12_1m',         category: '动量', updateDate: '2026-03-28' },
  { id: 'F011', name: '利率期限结构斜率',  refVar: 'factor.macro.yield_curve_slope',shortVar: 'yield_curve_slope', category: '宏观', updateDate: '2026-03-31' },
  { id: 'F012', name: '信用利差因子',      refVar: 'factor.macro.credit_spread',    shortVar: 'credit_spread',     category: '宏观', updateDate: '2026-03-31' },
  { id: 'F015', name: '分析师盈利预测修正',refVar: 'factor.analyst.eps_revision_3m',shortVar: 'eps_revision_3m',   category: '质量', updateDate: '2026-03-29' },
];

const FACTOR_CAT_COLOR: Record<string, string> = {
  '红利': 'text-red-400 bg-red-400/10 border-red-400/25',
  '低波': 'text-blue-400 bg-blue-400/10 border-blue-400/25',
  '质量': 'text-emerald-400 bg-emerald-400/10 border-emerald-400/25',
  '价值': 'text-orange-400 bg-orange-400/10 border-orange-400/25',
  '动量': 'text-yellow-400 bg-yellow-400/10 border-yellow-400/25',
  '宏观': 'text-purple-400 bg-purple-400/10 border-purple-400/25',
  '量价': 'text-cyan-400 bg-cyan-400/10 border-cyan-400/25',
};

const injectedFactorIds  = ref<Set<string>>(new Set());
const showFactorPanel    = ref(false);
const factorSearchQuery  = ref('');

const filteredInjectableFactors = computed(() => {
  const q = factorSearchQuery.value.trim().toLowerCase();
  return q ? INJECTABLE_FACTORS.filter(f => f.name.toLowerCase().includes(q) || f.shortVar.includes(q) || f.category.includes(q)) : INJECTABLE_FACTORS;
});

const injectedFactorList = computed(() => INJECTABLE_FACTORS.filter(f => injectedFactorIds.value.has(f.id)));

function toggleFactor(f: InjectableFactor) {
  const s = new Set(injectedFactorIds.value);
  s.has(f.id) ? s.delete(f.id) : s.add(f.id);
  injectedFactorIds.value = s;
}

// ── Dynamic Python Code (reactive to injected factors) ────────────────────────
const mockPythonCode = computed(() => {
  const factorBlock = injectedFactorList.value.length
    ? `\n# ── 因子仓库引用 (Factor Library Injection) ─────────────────────────────────
from map_factor_lib import factor_client
factor_client.init(api_key="$ENV_FACTOR_API_KEY")

${injectedFactorList.value.map(f =>
  `${f.shortVar.padEnd(22)} = factor_client.get("${f.refVar}", date="${f.updateDate}")`
).join('\n')}\n`
    : '';
  return `import pandas as pd
import numpy as np
from windpy import w
from scipy.optimize import minimize

# 初始化Wind API
w.start()

def get_market_data(tickers, start_date, end_date):
    """通过万得接口获取宏观及行情数据"""
    data = w.wsd(tickers, "close", start_date, end_date, "")
    return pd.DataFrame(data.Data).T

def optimize_portfolio(market_caps, cov_matrix, views):
    """执行自定义优化逻辑"""
    optimal_weights = {
        'A股宽基': 0.185, '港股科技': 0.060,
        '美股标普': 0.050, '中债利率': 0.475, '中债信用': 0.230
    }
    return optimal_weights

if __name__ == "__main__":
    weights = optimize_portfolio(None, None, None)
    print(f"Optimization complete: {weights}")${factorBlock}`;
});

// Alpha Mind generated multi-factor strategy code (mock)
const mockAlphaMindCode = `# ============================================================
# Alpha Mind Generated Strategy  |  v1.0  |  2026-03-26
# Strategy: Trend × Momentum × Mean-Reversion (Multi-Factor)
# ============================================================
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class StrategyConfig:
    universe: List[str] = field(default_factory=lambda: [
        "000300.SH", "512890.SH", "CBA00301.CS"
    ])
    ma_short: int = 20
    ma_long:  int = 60
    rsi_period: int = 14
    rsi_oversold: float = 30.0
    max_single_weight: float = 0.40    # 单标的权重上限

class MultiFactorStrategy:
    """
    Alpha Mind 多因子策略
    信号逻辑：均线金叉 AND RSI超卖时做多，
              均线死叉时平仓，等权分配资金。
    """

    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg

    def _compute_rsi(self, px: pd.Series) -> pd.Series:
        delta = px.diff()
        gain  = delta.clip(lower=0).rolling(self.cfg.rsi_period).mean()
        loss  = (-delta.clip(upper=0)).rolling(self.cfg.rsi_period).mean()
        rs    = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    def generate_signals(self, price_df: pd.DataFrame) -> pd.DataFrame:
        sigs = pd.DataFrame(index=price_df.index)
        for t in self.cfg.universe:
            px     = price_df[t]
            ma_s   = px.rolling(self.cfg.ma_short).mean()
            ma_l   = px.rolling(self.cfg.ma_long).mean()
            rsi    = self._compute_rsi(px)
            entry  = (ma_s > ma_l) & (ma_s.shift(1) <= ma_l.shift(1)) & (rsi < self.cfg.rsi_oversold)
            exit_s = ma_s < ma_l
            sigs[t] = np.where(entry, 1, np.where(exit_s, -1, 0))
        return sigs

    def compute_weights(self, sigs: pd.DataFrame) -> Dict[str, float]:
        longs = sigs.iloc[-1][sigs.iloc[-1] > 0]
        if longs.empty:
            return {t: 0.0 for t in self.cfg.universe}
        raw_w = 1.0 / len(longs)
        w = min(raw_w, self.cfg.max_single_weight)
        return {t: (w if t in longs.index else 0.0) for t in self.cfg.universe}

    def run_backtest(self, price_df: pd.DataFrame) -> dict:
        sigs     = self.generate_signals(price_df)
        ret_df   = price_df.pct_change().fillna(0)
        port_ret = (ret_df * sigs.shift(1)).sum(axis=1)
        sharpe   = port_ret.mean() / port_ret.std() * np.sqrt(252) if port_ret.std() > 0 else 0
        cum_ret  = (1 + port_ret).prod() - 1
        max_dd   = (port_ret.cumsum() - port_ret.cumsum().cummax()).min()
        return {
            "weights":       self.compute_weights(sigs),
            "sharpe_ratio":  round(sharpe, 3),
            "total_return":  f"{cum_ret:.2%}",
            "max_drawdown":  f"{max_dd:.2%}",
        }

if __name__ == "__main__":
    cfg    = StrategyConfig()
    strat  = MultiFactorStrategy(cfg)
    # 实盘对接: 替换 price_df 为实时行情数据
    # result = strat.run_backtest(price_df)
    print("Alpha Mind Strategy initialized. Connect data feed to run.")`;

const mockApiData: Record<string, { tables: { id: string; name: string; fields: string[] }[] }> = {
  'Wind API (万得)': {
    tables: [
      { id: 'AshareEODPrices', name: '中国A股日行情', fields: ['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_OPEN', 'S_DQ_HIGH', 'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_VOLUME'] },
      { id: 'AShareValuation', name: '中国A股估值指标', fields: ['S_INFO_WINDCODE', 'TRADE_DT', 'PE_TTM', 'PB_LF', 'PS_TTM'] },
      { id: 'AShareFinancialIndicator', name: '中国A股财务指标', fields: ['S_INFO_WINDCODE', 'REPORT_PERIOD', 'ROE', 'ROA', 'GROSS_MARGIN'] }
    ]
  },
  '同花顺 iFinD': {
    tables: [
      { id: 'THS_HQ_Daily', name: '日线行情', fields: ['thscode', 'time', 'open', 'high', 'low', 'close', 'volume'] },
      { id: 'THS_Finance_Main', name: '主要财务指标', fields: ['thscode', 'report_date', 'basiceps', 'roe_diluted'] }
    ]
  },
  'Choice 数据': {
    tables: [
      { id: 'CSS_Stock_Quote', name: '股票行情', fields: ['SecurityCode', 'TradeDate', 'OpenPrice', 'ClosePrice', 'TurnoverVolume'] }
    ]
  },
  '内部数仓 (Data Warehouse)': {
    tables: [
      { id: 'dw_fact_stock_daily', name: '股票日频事实表', fields: ['stock_code', 'trade_date', 'close_adj', 'volume', 'vwap'] },
      { id: 'dw_dim_stock_info', name: '股票基础信息维表', fields: ['stock_code', 'stock_name', 'industry_sw_l1', 'list_date'] }
    ]
  }
};

const CATEGORY_ICONS: Record<string, any> = {
  '我的模型': EditPen,
  '经典资配模型': Files,
  '经典策略模型': Grid,
  'AI 模型 (Beta)': StarFilled,
};

// ── Apply-to-workbench: mock diff data (BL model output vs current intent) ───
const BL_APPLY_DIFFS = [
  { label: '红利 (宽基权益 / A股)', from: '12.5%', to: '15.0%', diff: '+2.5%', pos: true  },
  { label: '港股 (恒生科技 ETF)',   from: '5.0%',  to: '6.0%',  diff: '+1.0%', pos: true  },
  { label: '境内固收 (利率债)',     from: '40.0%', to: '38.5%', diff: '-1.5%', pos: false },
  { label: '境外固收 (美元债)',     from: '6.0%',  to: '5.0%',  diff: '-1.0%', pos: false },
  { label: '黄金 ETF',             from: '1.0%',  to: '0.0%',  diff: '-1.0%', pos: false },
];

const MOCK_BL_WEIGHTS: Record<string, number> = {
  '512890.SH': 15.0,
  '513180.SH': 6.0,
  '019686.SH': 38.5,
  'SPV001':    34.0,
  '511010.SH': 5.0,
  '180105.SZ': 1.5,
  '518880.SH': 0.0,
};

// ── State ────────────────────────────────────────────────────────────────────
interface ModelItem {
  id: string; name: string; type: string; source: string; author: string;
  department: string; updateTime: string; desc: string; visibility: string;
  usageCount: number; trend: string; sharedWith: string[];
}

const categories = reactive([
  {
    title: '我的模型', action: 'upload', icon: EditPen,
    models: [
      { id: 'custom-py', name: 'Custom_Strategy_v2.py', type: 'custom', source: 'self', author: '当前用户', department: '固收+投资部', updateTime: '2026-03-25', desc: '用户自定义Python策略', visibility: 'private', usageCount: 0, trend: '0%', sharedWith: [] },
      { id: 'shared-py', name: 'Tech_Momentum_Factor.py', type: 'custom', source: 'shared', author: '张经理', department: '权益投资部', updateTime: '2026-03-20', desc: '科技股动量因子挖掘', visibility: 'dept', usageCount: 342, trend: '+5%', sharedWith: [] },
      { id: 'alpha-mind', name: '✨ Alpha Mind (AI 生成)', type: 'ai', source: 'system', author: 'AI 实验室', department: '创新业务部', updateTime: '2026-03-24', desc: '用自然语言描述策略，AI 自动生成资配模型或策略模型', visibility: 'corp', usageCount: 28900, trend: '+45%', sharedWith: [] },
    ] as ModelItem[]
  },
  {
    title: '经典资配模型', action: undefined, icon: Files,
    models: [
      { id: 'bl', name: 'Black-Litterman (BL) 模型', type: 'classic', source: 'system', author: '系统内置', department: '投管部', updateTime: '2026-01-10', desc: '结合主观观点的资产配置', visibility: 'corp', usageCount: 12500, trend: '+15%', sharedWith: [] },
      { id: 'rp', name: '风险评价 (Risk Parity)', type: 'classic', source: 'system', author: '系统内置', department: '投管部', updateTime: '2026-01-15', desc: '基于风险贡献相等的资产配置', visibility: 'corp', usageCount: 8900, trend: '+8%', sharedWith: [] },
      { id: 'mc', name: '蒙特卡洛模拟算法', type: 'classic', source: 'system', author: '系统内置', department: '投管部', updateTime: '2026-02-01', desc: '基于随机模拟的资产路径预测', visibility: 'corp', usageCount: 5600, trend: '-2%', sharedWith: [] },
    ] as ModelItem[]
  },
  {
    title: '经典策略模型', action: undefined, icon: Grid,
    models: [
      { id: 'mf', name: '多因子模型', type: 'classic', source: 'system', author: '系统内置', department: '投管部', updateTime: '2026-02-20', desc: '基于多因子打分的选股/选债', visibility: 'corp', usageCount: 15200, trend: '+22%', sharedWith: [] },
      { id: 'barra', name: 'Barra 多因子模型', type: 'classic', source: 'system', author: '系统内置', department: '投管部', updateTime: '2026-03-01', desc: '基于Barra风险模型的组合优化', visibility: 'corp', usageCount: 11000, trend: '+12%', sharedWith: [] },
    ] as ModelItem[]
  },
]);

const selectedModelId = ref<string | null>(null);
const selectedModel = computed(() => categories.flatMap(c => c.models).find(m => m.id === selectedModelId.value) || null);
const isDrawerOpen = ref(false);
const showLeaderboard = ref(true);   // default landing = leaderboard
const showPushDropdown = ref(false); // unified push dropdown
const showSaveToMyModels = ref(false); // show save CTA after Alpha Mind generates code
const aiGeneratedCode = ref('');       // latest code from Alpha Mind, shown in right panel
const isRunning = ref(false);
const isFromWorkbench = ref(false);
const isFullscreenLog = ref(false);
const isFullscreenOutput = ref(false);
const isFullscreenCode = ref(false);
const showUploadModal = ref(false);
const showShareModal = ref(false);
const uploadName = ref('');

const logs = ref<string[]>(['[SYSTEM] Model Center Initialized.', '[SYSTEM] Awaiting model selection...']);
const outputData = ref<any[]>([]);
const outputFiles = ref<any[]>([]);
const mappedParams = reactive<Record<string, boolean>>({});

const chatMessages = ref<{ role: 'user' | 'ai'; text: string; codeBlock?: string }[]>([
  { role: 'ai', text: '您好！我是 Alpha Mind · 策略代码生成器。请用自然语言描述您的量化投资逻辑或策略约束，我将为您生成完整的 Python 模型代码，可直接验证并存入「我的模型」库。' }
]);
const chatInput = ref('');
const chatContainerRef = ref<HTMLElement | null>(null);

const inputMappings = reactive<Record<string, any>>({
  market_caps: { source: 'Wind API (万得)', table: 'AshareEODPrices', field: ['S_DQ_CLOSE'] },
  cov_matrix:  { source: 'Wind API (万得)', table: 'AshareEODPrices', field: ['S_DQ_CLOSE'] },
  views:       { source: '自定义输入 (Manual)', value: '' }
});

const showApiModal = ref(false);
const currentMappingKey = ref<string | null>(null);
const modalSource = ref('Wind API (万得)');
const modalTable = ref('');
const modalField = ref<string[]>([]);
const modalManualValue = ref('');

// Apply-to-workbench state
const showApplyModal = ref(false);
const isApplying    = ref(false);   // loading state for confirm-and-navigate transition
// Push-to-model modal state
const showPushModal    = ref(false);
const pushModalTarget  = ref<'allocation' | 'strategy'>('allocation');
const isPushingBack    = ref(false); // loading state for push-modal confirm

// ── Computed ─────────────────────────────────────────────────────────────────
const leaderboardModels = computed(() =>
  categories.flatMap(c => c.models)
    .filter(m => m.visibility !== 'private')
    .sort((a, b) => b.usageCount - a.usageCount)
);

const allApiSources = computed(() => Object.keys(mockApiData).concat('自定义输入 (Manual)'));

const apiTablesForSource = computed(() => {
  if (!mockApiData[modalSource.value]) return [];
  return mockApiData[modalSource.value].tables;
});

const apiFieldsForTable = computed(() => {
  const tables = apiTablesForSource.value;
  const t = tables.find(t => t.name === modalTable.value);
  return t ? t.fields : [];
});

/** Which push option is visible based on which workbench tab triggered the jump.
 *  'allocation' → only show "推送至资配模型"
 *  'strategy'   → only show "推送至策略模型"
 *  null         → show both (direct entry, not from workbench) */
const allowedPushTarget = computed<'allocation' | 'strategy' | null>(() => {
  if (sharedIntentState.callerTab === 'taa')    return 'allocation';
  if (sharedIntentState.callerTab === 'intent') return 'strategy';
  return null;
});

// ── Lifecycle ────────────────────────────────────────────────────────────────
onMounted(() => {
  // Auto-detect workbench entry and pre-set the "from workbench" mode
  if (sharedIntentState.callerTab) {
    isFromWorkbench.value = true;
  }
});

// ── Methods ──────────────────────────────────────────────────────────────────
function formatUsageCount(count: number) {
  return count >= 1000 ? (count / 1000).toFixed(1) + 'k' : count.toString();
}

function logColor(log: string): string {
  if (log.includes('[ERROR]')) return 'text-[#FF5630]';
  if (log.includes('[SUCCESS]')) return 'text-[#00C9A7]';
  if (log.includes('[WIND]')) return 'text-[#3B9EFF]';
  if (log.includes('[Alpha Mind]')) return 'text-purple-400';
  if (log.startsWith('>')) return 'text-[#FFAB00]';
  return 'text-[#94A3B8]';
}

function handleGenerateModel() {
  const alphaMind = categories.flatMap(c => c.models).find(m => m.id === 'alpha-mind');
  if (alphaMind) { handleSelectModel(alphaMind); showLeaderboard.value = false; }
}

function handlePushTo(target: 'workbench' | 'allocation' | 'strategy') {
  showPushDropdown.value = false;
  if (target === 'workbench') { showApplyModal.value = true; }
  else {
    pushModalTarget.value = target as 'allocation' | 'strategy';
    showPushModal.value = true;
  }
}

function handleSelectModel(model: ModelItem) {
  selectedModelId.value = model.id;
  isDrawerOpen.value = true;
  logs.value = [
    `[SYSTEM] Loaded model: ${model.name}`,
    `[SYSTEM] Type: ${model.type === 'classic' ? 'Classic Form' : model.type === 'ai' ? 'AI Chat' : 'Custom Code'}`,
    '[SYSTEM] Ready for execution.'
  ];
  outputData.value = [];
  outputFiles.value = [];
  aiGeneratedCode.value = '';
  showSaveToMyModels.value = false;
  Object.keys(mappedParams).forEach(k => delete mappedParams[k]);
}

function handleRunModel() {
  isRunning.value = true;
  const model = selectedModel.value;
  if (!model) return;

  // Update usage count
  const cat = categories.find(c => c.models.some(m => m.id === model.id));
  if (cat) {
    const m = cat.models.find(m => m.id === model.id);
    if (m) m.usageCount += 1;
  }

  if (model.type === 'ai') {
    logs.value.push('[Alpha Mind] 正在解析自然语言意图...');
    setTimeout(() => {
      logs.value.push('[Alpha Mind] 提取关键因子与策略约束...');
      logs.value.push('[Alpha Mind] 正在构建代码生成上下文...');
      logs.value.push('[Alpha Mind] 调用量化推理引擎生成 Python 代码...');
      logs.value.push('[Alpha Mind] 代码优化与语法校验通过。');
      logs.value.push('> Code generation finished in 2.15s.');
      isRunning.value = false;
    }, 2000);
  } else {
    logs.value.push(`> Executing ${model.name}...`);
    setTimeout(() => {
      logs.value.push('[WIND] Connecting to Data Server...');
      logs.value.push('[WIND] Data fetched successfully. Shape: (252, 5)');
      logs.value.push('[OPTIMIZER] Running optimization matrix...');
      logs.value.push('[SUCCESS] Optimal weights generated.');
      logs.value.push('> Execution finished in 1.24s.');
      populateOutput();
    }, 1500);
  }
}

function populateOutput() {
  outputData.value = [
    { id: 'row1', class: '权益', ticker: '000300.SH', name: '沪深300', weight: '18.5%' },
    { id: 'row2', class: '权益', ticker: 'HSTECH.HI', name: '恒生科技', weight: '6.0%' },
    { id: 'row3', class: '权益', ticker: 'SPX.GI', name: '标普500', weight: '5.0%' },
    { id: 'row4', class: '固收', ticker: 'CBA00301.CS', name: '中债国债总财富', weight: '47.5%' },
    { id: 'row5', class: '固收', ticker: 'CBA02501.CS', name: '中债信用债总财富', weight: '23.0%' },
  ];
  outputFiles.value = [
    { name: 'optimization_report.pdf', size: '1.2 MB', type: 'pdf' },
    { name: 'factor_exposure.csv', size: '45 KB', type: 'csv' },
    { name: 'weights_matrix.json', size: '12 KB', type: 'json' }
  ];
  isRunning.value = false;
}

function handleSendChat() {
  if (!chatInput.value.trim() || isRunning.value) return;
  const q = chatInput.value.trim();
  chatMessages.value.push({ role: 'user', text: q });
  chatInput.value = '';
  showSaveToMyModels.value = false;
  isRunning.value = true;

  // Update usage count
  const model = selectedModel.value;
  if (model) {
    const cat = categories.find(c => c.models.some(m => m.id === model.id));
    if (cat) { const m = cat.models.find(m => m.id === model.id); if (m) m.usageCount += 1; }
  }
  logs.value.push('[Alpha Mind] 正在解析自然语言意图...');
  logs.value.push('[Alpha Mind] 提取关键因子与策略约束...');

  setTimeout(() => {
    logs.value.push('[Alpha Mind] 正在构建代码生成上下文...');
    logs.value.push('[Alpha Mind] 调用量化推理引擎生成 Python 代码...');
    logs.value.push('[Alpha Mind] 代码优化与语法校验通过。');
    logs.value.push('> Code generation finished in 2.28s.');
    isRunning.value = false;
    showSaveToMyModels.value = true;
    aiGeneratedCode.value = mockAlphaMindCode;
    chatMessages.value.push({
      role: 'ai',
      text: `✅ 策略代码已生成（含回测接口），已同步至右侧「输出结果与映射区」，可直接调试或保存至「我的模型」库。`,
    });
    nextTick(() => {
      if (chatContainerRef.value) chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight;
    });
  }, 2300);
}

function handleSaveToMyModels() {
  showSaveToMyModels.value = false;
  chatMessages.value.push({ role: 'ai', text: '✅ 代码已通过语法校验并存入「我的模型」库。您可在左侧「自定义模型」列表中找到该模型，并直接运行或进一步微调。' });
  nextTick(() => {
    if (chatContainerRef.value) chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight;
  });
}

function toggleMapping(id: string) {
  mappedParams[id] = !mappedParams[id];
}

function openApiModal(key: string) {
  currentMappingKey.value = key;
  const cur = inputMappings[key] || { source: 'Wind API (万得)' };
  modalSource.value = cur.source || 'Wind API (万得)';
  modalTable.value = cur.table || '';
  modalField.value = Array.isArray(cur.field) ? [...cur.field] : (cur.field ? [cur.field] : []);
  modalManualValue.value = cur.value || '';
  showApiModal.value = true;
}

function saveApiMapping() {
  if (currentMappingKey.value) {
    inputMappings[currentMappingKey.value] = {
      source: modalSource.value,
      ...(modalSource.value !== '自定义输入 (Manual)'
        ? { table: modalTable.value, field: [...modalField.value] }
        : { value: modalManualValue.value })
    };
  }
  showApiModal.value = false;
}

function toggleModalField(field: string) {
  const idx = modalField.value.indexOf(field);
  if (idx >= 0) modalField.value.splice(idx, 1);
  else modalField.value.push(field);
}

function confirmApplyWeights() {
  if (isApplying.value) return;
  isApplying.value = true;
  setTimeout(() => {
    sharedIntentState.pendingModelWeights = {
      modelId:   selectedModel.value?.id   ?? 'bl',
      modelName: selectedModel.value?.name ?? 'Black-Litterman (BL) 模型',
      weights: { ...MOCK_BL_WEIGHTS },
    };
    sharedIntentState.applyTimestamp = Date.now();

    addToBasket({
      type: 'buy',
      assetName: '24国债01',
      assetCode: '240001.IB',
      amount: 5000,
      source: '模型',
      status: 'pending',
      weightDelta: 2.1,
      productId: 'all',
    });
    addToBasket({
      type: 'buy',
      assetName: '中票AAA',
      assetCode: '230088.IB',
      amount: 2000,
      source: '模型',
      status: 'pending',
      weightDelta: 0.8,
      productId: 'all',
    });
    addToBasket({
      type: 'sell',
      assetName: '城投债HN01',
      assetCode: 'HN2301.IB',
      amount: 3000,
      source: '模型',
      status: 'pending',
      weightDelta: -1.3,
      productId: 'all',
    });

    const backPath = modelBackPath.value || 'terminal';
    sharedIntentState.navigationTarget = backPath;
    modelBackPath.value = '';
    showApplyModal.value = false;
    isApplying.value = false;
  }, 600);
}

function confirmPushAndReturn() {
  if (isPushingBack.value) return;
  isPushingBack.value = true;
  setTimeout(() => {
    sharedIntentState.pendingModelWeights = {
      modelId:   selectedModel.value?.id   ?? 'bl',
      modelName: selectedModel.value?.name ?? 'Black-Litterman (BL) 模型',
      weights: { ...MOCK_BL_WEIGHTS },
    };
    sharedIntentState.applyTimestamp = Date.now();

    addToBasket({
      type: 'buy',
      assetName: '24国债01',
      assetCode: '240001.IB',
      amount: 5000,
      source: '模型',
      status: 'pending',
      weightDelta: 2.1,
      productId: 'all',
    });
    addToBasket({
      type: 'buy',
      assetName: '中票AAA',
      assetCode: '230088.IB',
      amount: 2000,
      source: '模型',
      status: 'pending',
      weightDelta: 0.8,
      productId: 'all',
    });
    addToBasket({
      type: 'sell',
      assetName: '城投债HN01',
      assetCode: 'HN2301.IB',
      amount: 3000,
      source: '模型',
      status: 'pending',
      weightDelta: -1.3,
      productId: 'all',
    });

    const backPath = modelBackPath.value || 'terminal';
    sharedIntentState.navigationTarget = backPath;
    modelBackPath.value = '';
    sharedIntentState.callerTab = null;
    isFromWorkbench.value = false;
    showPushModal.value = false;
    isPushingBack.value = false;
  }, 600);
}
</script>
