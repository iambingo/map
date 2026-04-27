<template>
  <div class="flex flex-col h-full bg-[#161922] text-[#E8ECF4] overflow-hidden p-4 space-y-3">

    <!-- ═══ PORTAL: 会议选择中心 ═══ -->
    <div v-if="currentMeetingId == null" class="flex-1 flex flex-col items-center justify-center space-y-6">
      <div class="text-center space-y-2">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#3B9EFF] to-[#22D3EE] flex items-center justify-center mx-auto shadow-[0_0_40px_rgba(59,158,255,0.3)]">
          <UserFilled class="w-8 h-8 text-white" />
        </div>
        <h1 class="text-xl font-bold text-white tracking-wider mt-3">投委会会议中心</h1>
        <p class="text-[13px] font-mono text-[#64748B]">Investment Committee Meeting Portal</p>
      </div>

      <div class="w-full max-w-2xl space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider">全部会议 ({{ meetingList.length }})</span>
          <button v-if="isSecretary" @click="quickCreateMeeting"
            class="text-[13px] px-3 py-1.5 rounded-lg border border-[#3B9EFF]/25 bg-[#3B9EFF]/10 text-[#3B9EFF] hover:bg-[#3B9EFF]/18 transition-colors flex items-center gap-1.5">
            <Plus class="w-3.5 h-3.5" /> 一键新增
          </button>
        </div>
        <div class="space-y-2 max-h-[50vh] overflow-y-auto no-scrollbar">
          <div v-for="m in meetingList" :key="m.id"
            @click="enterMeeting(m.id)"
            class="bg-[#202431] border rounded-xl p-4 cursor-pointer hover:border-[#3B9EFF]/40 transition-all duration-200 group"
            :class="m.status === '进行中' ? 'border-[#3B9EFF]/30' : m.status === '已归档' ? 'border-[#252A3A]' : 'border-[#252A3A]'">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-2 h-2 rounded-full shrink-0"
                  :class="m.status === '进行中' ? 'bg-[#3B9EFF] animate-pulse' : m.status === '已归档' ? 'bg-[#6B7280]' : 'bg-[#FFAB00]'"></div>
                <div>
                  <div class="text-[15px] font-semibold text-[#E8ECF4] group-hover:text-white transition-colors">{{ m.name }}</div>
                  <div class="text-[13px] font-mono text-[#64748B] mt-0.5">{{ m.date }} · {{ m.time }} · {{ m.location }}</div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span :class="cn('text-[11px] font-mono px-2 py-1 rounded border',
                  m.status === '进行中' ? 'bg-[#3B9EFF]/15 border-[#3B9EFF]/30 text-[#3B9EFF]' :
                  m.status === '已归档' ? 'bg-[#6B7280]/10 border-[#2E3348] text-[#64748B]' :
                  m.status === '已结束' ? 'bg-[#00C9A7]/10 border-[#00C9A7]/25 text-[#00C9A7]' :
                  'bg-[#FFAB00]/10 border-[#FFAB00]/25 text-[#FFAB00]')">
                  {{ m.status }}
                </span>
                <ArrowRight class="w-4 h-4 text-[#4A5568] group-hover:text-[#3B9EFF] transition-colors" />
              </div>
            </div>
            <div v-if="m.decision" class="mt-2 text-[13px] font-mono text-[#94A3B8] truncate">{{ m.decision }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ MEETING DETAIL (原有内容) ═══ -->
    <template v-else>

    <!-- ═══ BFF 同步状态 / 离线 Mock ═══ -->
    <div
      v-if="committeeOfflineMock"
      class="shrink-0 text-xs font-mono px-3 py-2 rounded-lg border border-[#22D3EE]/25 bg-[#1A1E2B] text-[#22D3EE]"
    >
      离线 Mock（VITE_COMMITTEE_OFFLINE_MOCK）：未请求 portal-snapshot / page-context，决议表为前端默认数据。
    </div>
    <div
      v-else-if="portalSnapshotLoading || committeeContextLoading || portalSnapshotError || committeeContextError"
      class="shrink-0 text-xs font-mono px-3 py-2 rounded-lg border border-[#2E3348] bg-[#1A1E2B]"
      :class="(portalSnapshotError || committeeContextError) ? 'text-[#F97316] border-[#F97316]/25' : 'text-[#3B9EFF] border-[#3B9EFF]/20'"
    >
      <span v-if="portalSnapshotLoading || committeeContextLoading">正在从后端同步投委会数据（门户快照 + 会议上下文）…</span>
      <span v-else>
        <template v-if="portalSnapshotError">门户快照：{{ portalSnapshotError }}</template>
        <template v-if="portalSnapshotError && committeeContextError"> · </template>
        <template v-if="committeeContextError">投委会上下文：{{ committeeContextError }}</template>
      </span>
    </div>

    <!-- ═══ HEADER ═══ -->
    <div class="bg-gradient-to-r from-[#202431] to-[#1A1E2B] border border-[#2E3348] rounded-xl px-5 py-3.5 shrink-0 flex justify-between items-center shadow-[0_4px_24px_rgba(0,0,0,0.5)]">
      <div class="flex items-center space-x-4">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#3B9EFF] to-[#22D3EE] flex items-center justify-center shadow-[0_0_18px_rgba(59,158,255,0.3)]">
          <UserFilled class="w-[19px] h-[19px] text-white" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-base font-bold text-white tracking-wider">混合投资委员会</h2>
            <button @click="backToList" class="text-[11px] font-mono px-2 py-0.5 rounded border border-[#3B9EFF]/25 bg-[#3B9EFF]/8 text-[#3B9EFF] hover:bg-[#3B9EFF]/15 transition-colors flex items-center gap-1">
              <ArrowLeft class="w-3 h-3" /> 切换会议
            </button>
            <button v-if="isSecretary" @click="handleQuickCreateAndEnter" class="text-[11px] font-mono px-2.5 py-0.5 rounded-lg border border-[#3B9EFF]/35 bg-[#3B9EFF]/12 text-[#3B9EFF] hover:bg-[#3B9EFF]/22 hover:border-[#3B9EFF]/55 transition-all flex items-center gap-1.5 shadow-[0_0_12px_rgba(59,158,255,0.15)]">
              <Plus class="w-3 h-3" /> 一键新增会议
            </button>
            <span v-if="isViewingArchived" class="text-[11px] font-mono px-2 py-0.5 rounded border border-[#64748B]/25 bg-[#64748B]/10 text-[#64748B]">只读 · 历史归档</span>
          </div>
          <p class="text-xs text-[#94A3B8] mt-0.5 font-mono uppercase tracking-widest">{{ currentMeeting?.name ?? '2026 Q2 · 投资策略与TAA目标决议 · 全生命周期系统' }}</p>
        </div>
      </div>
      <div class="text-right space-y-2">
        <div class="flex items-center justify-end gap-2">
          <!-- 当前角色标签 (由右上角个人中心统一切换) -->
          <div class="flex items-center gap-1.5 border border-[#2E3348] rounded-lg px-2.5 py-1 bg-[#161922]">
            <span class="text-xs font-mono text-[#4A5568]">当前视角</span>
            <span :class="cn('text-xs font-mono font-bold px-1.5 py-1 rounded border',
              isSecretary ? 'bg-[#3B9EFF]/15 border-[#3B9EFF]/30 text-[#3B9EFF]' :
              isChairman  ? 'bg-[#FFAB00]/15 border-[#FFAB00]/30 text-[#FFAB00]' :
                            'bg-[#8B5CF6]/15 border-[#8B5CF6]/30 text-[#8B5CF6]')">
              {{ isSecretary ? '秘书' : isChairman ? '主任委员' : '委员' }}
            </span>
          </div>
          <!-- Recording Control (State Machine: idle / recording / paused / finished) -->
          <div class="flex items-center gap-1.5 border border-[#2E3348] rounded-lg px-2 py-1 bg-[#161922]">
            <!-- Timer -->
            <span class="text-[13px] font-mono tabular-nums min-w-[52px] text-center"
              :class="recState === 'recording' ? 'text-[#FF3B30] animate-pulse' : recState === 'paused' ? 'text-[#FFAB00]' : recState === 'finished' ? 'text-[#22D3EE]' : 'text-[#4A5568]'"
            >{{ recTimeDisplay }}</span>
            <div class="w-px h-4 bg-[#2E3348]"></div>
            <!-- Start / Resume -->
            <button @click="recStart"
              :disabled="recState === 'recording' || recState === 'finished'"
              :class="cn('w-7 h-7 flex items-center justify-center rounded transition-colors',
                recState === 'recording' ? 'opacity-40 cursor-not-allowed' : 'hover:bg-[#FF3B30]/15 cursor-pointer')"
            >
              <span class="w-2.5 h-2.5 rounded-full" :class="recState === 'idle' || recState === 'paused' ? 'bg-[#FF3B30]' : 'bg-[#FF3B30]/40'"></span>
            </button>
            <!-- Pause -->
            <button @click="recPause"
              :disabled="recState !== 'recording'"
              :class="cn('w-7 h-7 flex items-center justify-center rounded transition-colors',
                recState === 'recording' ? 'hover:bg-[#FFAB00]/15 cursor-pointer' : 'opacity-40 cursor-not-allowed')"
            >
              <div class="flex items-center gap-[3px]">
                <div class="w-[3px] h-3 rounded-sm" :class="recState === 'recording' ? 'bg-[#FFAB00]' : 'bg-[#FFAB00]/40'"></div>
                <div class="w-[3px] h-3 rounded-sm" :class="recState === 'recording' ? 'bg-[#FFAB00]' : 'bg-[#FFAB00]/40'"></div>
              </div>
            </button>
            <!-- Stop -->
            <button @click="recStop"
              :disabled="recState !== 'recording' && recState !== 'paused'"
              :class="cn('w-7 h-7 flex items-center justify-center rounded transition-colors',
                recState === 'recording' || recState === 'paused' ? 'hover:bg-[#3B9EFF]/15 cursor-pointer' : 'opacity-40 cursor-not-allowed')"
            >
              <div class="w-2.5 h-2.5 rounded-[2px]" :class="recState === 'recording' || recState === 'paused' ? 'bg-[#3B9EFF]' : 'bg-[#3B9EFF]/40'"></div>
            </button>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2">
          <div class="text-xs font-mono text-[#94A3B8] bg-[#1A1E2B] border border-[#252A3A] px-3 py-1.5 rounded-lg">
            会议编号 <span class="text-[#3B9EFF]">{{ meetingHeaderCode }}</span> · {{ meetingHeaderDate }}
          </div>
          <button
            v-if="isSecretary"
            @click="showMeetingDrawer = true"
            class="flex items-center gap-1.5 text-[13px] px-2.5 py-1.5 rounded-lg border border-[#3B9EFF]/25 bg-[#3B9EFF]/10 text-[#3B9EFF] hover:bg-[#3B9EFF]/18 transition-colors"
          >
            <Document class="w-3.5 h-3.5" /> 会议管理
          </button>
        </div>
        <div class="flex items-center justify-end space-x-3 mt-1">
          <span class="text-[11px] font-mono text-[#94A3B8]">问卷回收 {{ submittedCount }} / {{ voteProgressTotal }}</span>
          <div class="w-20 h-1 bg-[#1A1E2B] rounded-full overflow-hidden">
            <div class="h-full bg-[#3B9EFF] rounded-full transition-all duration-500" :style="{ width: `${voteProgressPct}%` }"></div>
          </div>
          <span class="text-[11px] font-mono" :class="voteProgressComplete ? 'text-[#22D3EE]' : 'text-[#94A3B8]'">{{ voteProgressComplete ? '全员完成' : '收集中' }}</span>
        </div>
      </div>
    </div>

    <!-- ═══ 5-STEP STEPPER (会前/会中/会后) ═══ -->
    <div class="shrink-0 bg-[#1A1E2B] border border-[#252A3A] rounded-xl px-5 py-3">
      <div class="flex items-center">
        <template v-for="(s, i) in STEPS" :key="i">
          <button @click="step = i" class="flex items-center space-x-2.5 group shrink-0">
            <div :class="cn(
              'w-8 h-8 rounded-full flex items-center justify-center text-[14px] font-bold font-mono border-2 transition-all duration-200',
              stepStatuses[i] === 'done'
                ? 'bg-[#34C759]/15 border-[#34C759]/50 text-[#34C759]'
                : step === i
                  ? 'bg-[#3B9EFF] border-[#3B9EFF] text-white shadow-[0_0_14px_rgba(59,158,255,0.45)]'
                  : 'bg-[#161922] border-[#2E3348] text-[#6B7280] group-hover:border-[#3B9EFF]/30 group-hover:text-[#94A3B8]'
            )">
              <Check v-if="stepStatuses[i] === 'done'" class="w-4 h-4" />
              <template v-else>{{ STEP_LABELS[i] }}</template>
            </div>
            <div class="text-left">
              <div :class="cn('text-[11px] font-mono uppercase tracking-wider',
                stepStatuses[i] === 'done' ? 'text-[#34C759]/70' : step === i ? STEP_PHASE_COLORS[i] : 'text-[#4A5568]'
              )">{{ STEP_PHASES[i] }}</div>
              <div :class="cn('text-[13px] font-medium whitespace-nowrap',
                stepStatuses[i] === 'done' ? 'text-[#34C759]' : step === i ? 'text-white' : 'text-[#4A5568] group-hover:text-[#6B7280]')">
                {{ s.label }}
              </div>
            </div>
          </button>
          <div v-if="i < 4" class="flex-1 mx-3 flex items-center min-w-[14px]">
            <div :class="cn('h-px w-full', stepStatuses[i] === 'done' ? 'bg-gradient-to-r from-[#34C759]/40 to-[#34C759]/15' : 'bg-[#252A3A]')" />
            <ArrowRight class="w-3 h-3 shrink-0 -ml-1" :class="stepStatuses[i] === 'done' ? 'text-[#34C759]/35' : 'text-[#252A3A]'" />
          </div>
        </template>
      </div>
    </div>

    <!-- ═══ MAIN SCROLL AREA ═══ -->
    <div class="flex-1 overflow-y-auto no-scrollbar min-h-0">

      <!-- ════════════════════════════════════════════════════════════
           STEP 0: 会前筹备与填报 (角色感知)
      ════════════════════════════════════════════════════════════ -->

      <!-- ── 秘书视角 (投管): 管理与配置中心 ── -->
      <div v-if="step === 0 && isSecretary" class="grid grid-cols-12 gap-4 pb-4">

        <!-- ══ 投票截止时间控制面板 ══ -->
        <div class="col-span-12 bg-[#202431] border border-[#252A3A] rounded-xl px-5 py-3 flex items-center gap-4 flex-wrap">
          <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider shrink-0">投票窗口</div>
          <span :class="cn('text-[11px] font-mono px-2 py-1 rounded border shrink-0 transition-colors',
            isVoteOpen
              ? 'bg-[#00C9A7]/10 border-[#00C9A7]/25 text-[#00C9A7]'
              : 'bg-[#F04864]/10 border-[#F04864]/25 text-[#F04864]')">
            {{ isVoteOpen ? '● 收集中' : '■ 已截止' }}
          </span>
          <div class="flex items-center gap-2.5 flex-1">
            <label class="text-xs font-mono text-[#64748B] shrink-0">截止时间</label>
            <input
              type="datetime-local"
              v-model="voteDeadlineInput"
              :disabled="voteForcedClosed"
              class="bg-[#161922] border border-[#2E3348] rounded px-2.5 py-1 text-[13px] font-mono text-[#E8ECF4] focus:border-[#FFAB00] focus:outline-none transition-colors"
              :class="voteForcedClosed ? 'opacity-40 cursor-not-allowed' : 'hover:border-[#FFAB00]/40'"
              style="color-scheme: dark;"
            />
            <span v-if="voteDeadlineInput && !voteForcedClosed" :class="cn('text-xs font-mono shrink-0', isVoteOpen ? 'text-[#FFAB00]' : 'text-[#F04864]')">
              {{ isVoteOpen ? `剩余 ${voteCountdownDisplay}` : '已过期' }}
            </span>
            <span v-if="voteForcedClosed" class="text-xs font-mono text-[#F04864] shrink-0">强制截止中</span>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button
              v-if="isVoteOpen"
              @click="forceCloseVote"
              class="flex items-center gap-1.5 text-[13px] px-3 py-1.5 rounded-lg border border-[#F04864]/30 bg-[#F04864]/8 text-[#F04864] hover:bg-[#F04864]/15 transition-colors font-medium"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-[#F04864] shrink-0"></span>
              手动截止投票
            </button>
            <button
              v-else
              @click="reopenVote"
              class="flex items-center gap-1.5 text-[13px] px-3 py-1.5 rounded-lg border border-[#00C9A7]/30 bg-[#00C9A7]/8 text-[#00C9A7] hover:bg-[#00C9A7]/15 transition-colors font-medium"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-[#00C9A7] shrink-0"></span>
              重新开放
            </button>
          </div>
        </div>

        <!-- LEFT: 问卷题目管理 (动态投票资产) -->
        <div class="col-span-5 space-y-3">
          <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden">
            <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3 flex items-center justify-between">
              <h3 class="am-title-l2"><div class="am-title-bar"></div>问卷题目管理</h3>
              <span class="text-[11px] font-mono text-[#64748B]">{{ questionAssetList.length }} 项投票资产</span>
            </div>
            <div class="divide-y divide-[#252A3A]">
              <div
                v-for="(qa, idx) in questionAssetList"
                :key="qa.id"
                class="px-5 py-3 flex items-center justify-between hover:bg-[#1A1E2B]/50 transition-colors"
              >
                <div class="flex items-center gap-3 flex-1 min-w-0">
                  <span class="text-xs font-mono font-bold text-[#3B9EFF] w-5 shrink-0">{{ idx + 1 }}</span>
                  <div class="flex-1 min-w-0">
                    <div class="text-[14px] font-semibold text-[#E8ECF4] truncate">{{ qa.name }}</div>
                    <div class="flex items-center gap-2 mt-0.5">
                      <span class="text-[11px] font-mono text-[#64748B]">{{ qa.type }}</span>
                      <span :class="cn('text-[11px] font-mono px-1.5 py-1 rounded border',
                        qa.enabled ? 'bg-[#00C9A7]/10 border-[#00C9A7]/25 text-[#00C9A7]' : 'bg-[#252A3A] border-[#2E3348] text-[#4A5568]')">{{ qa.enabled ? '启用' : '停用' }}</span>
                    </div>
                  </div>
                </div>
                <div class="flex items-center gap-1 shrink-0">
                  <button @click="editQuestionAsset(qa.id)" class="text-xs px-2 py-1 rounded border border-[#252A3A] text-[#94A3B8] hover:border-[#3B9EFF]/30 hover:text-[#3B9EFF] transition-colors flex items-center gap-1">
                    <Edit class="w-3 h-3" /> 编辑
                  </button>
                  <button @click="deleteQuestionAsset(qa.id)" class="text-xs px-2 py-1 rounded border border-[#252A3A] text-[#94A3B8] hover:border-[#F04864]/30 hover:text-[#F04864] transition-colors flex items-center gap-1">
                    <Close class="w-3 h-3" /> 删除
                  </button>
                </div>
              </div>
            </div>
            <div class="p-3 border-t border-[#252A3A]">
              <button @click="addQuestionAsset" class="w-full text-[14px] py-2.5 rounded-lg border border-dashed border-[#3B9EFF]/30 bg-[#3B9EFF]/5 text-[#3B9EFF] hover:bg-[#3B9EFF]/10 hover:border-[#3B9EFF]/50 transition-all flex items-center justify-center gap-1.5">
                <span class="text-[15px] leading-relaxed">+</span> 新增投票资产
              </button>
            </div>
          </div>

          <!-- 已提交委员详情查看 -->
          <div v-if="activeMemberId && memberSubmissions[activeMemberId]" class="bg-[#202431] border border-[#22D3EE]/15 rounded-xl overflow-hidden">
            <div class="bg-gradient-to-r from-[#22D3EE]/8 to-[#202431] border-b border-[#22D3EE]/10 px-5 py-3 flex items-center justify-between">
              <h3 class="am-title-l2"><div class="am-title-bar" style="background:#22D3EE"></div>{{ activeMember?.name }} · 已提交</h3>
              <span class="text-[11px] font-mono text-[#22D3EE] bg-[#22D3EE]/10 border border-[#22D3EE]/20 px-1.5 py-1 rounded">{{ memberSubmissions[activeMemberId].submittedAt }}</span>
            </div>
            <div class="p-4 space-y-2 max-h-[280px] overflow-y-auto no-scrollbar">
              <div class="grid grid-cols-3 gap-1.5">
                <div v-for="(val, key) in memberSubmissions[activeMemberId].sectionA" :key="key" class="bg-[#1A1E2B] border border-[#252A3A] rounded px-2.5 py-1.5 flex items-center justify-between">
                  <span class="text-xs text-[#B4BAC9]">{{ key }}</span>
                  <span :class="cn('text-xs font-bold font-mono', SCORE_COLORS[val] || 'text-[#94A3B8]')">{{ val }} · {{ SCORE_LABELS[val] || '-' }}</span>
                </div>
              </div>
              <div class="flex flex-wrap gap-1.5 mt-1">
                <span
                  v-for="(val, key) in memberSubmissions[activeMemberId].sectionB" :key="key"
                  :class="cn('text-[11px] font-mono px-2 py-1 rounded border',
                    val ? 'bg-[#00C9A7]/10 border-[#00C9A7]/25 text-[#00C9A7]' : 'bg-[#1A1E2B] border-[#252A3A] text-[#4A5568]')"
                >{{ key }}: {{ val ? '创新高' : '-' }}</span>
              </div>
              <p class="text-xs text-[#94A3B8] leading-relaxed line-clamp-3 mt-1">{{ memberSubmissions[activeMemberId].coreView }}</p>
            </div>
          </div>
        </div>

        <!-- RIGHT: 提交进度看板 -->
        <div class="col-span-7">
          <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden h-full flex flex-col">
            <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3 flex items-center justify-between">
              <h3 class="am-title-l2"><div class="am-title-bar"></div>提交进度看板</h3>
              <div class="flex items-center space-x-3">
                <span class="text-xs font-mono text-[#94A3B8]">{{ submittedCount }} / {{ MEMBERS_DATA.length }} 已提交</span>
                <div class="w-20 h-1 bg-[#1A1E2B] rounded-full overflow-hidden">
                  <div class="h-full bg-[#3B9EFF] rounded-full transition-all duration-500" :style="{ width: `${submittedCount / MEMBERS_DATA.length * 100}%` }"></div>
                </div>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto no-scrollbar divide-y divide-[#1A1E2B]">
              <div
                v-for="m in MEMBERS_DATA" :key="m.id"
                @click="selectMember(m.id)"
                :class="cn(
                  'flex items-center px-5 py-3.5 cursor-pointer transition-all duration-150',
                  activeMemberId === m.id ? 'bg-[#3B9EFF]/08 border-l-2 border-[#3B9EFF]' : 'hover:bg-[#1A1E2B]/70 border-l-2 border-transparent'
                )"
              >
                <div :class="cn(
                  'w-2.5 h-2.5 rounded-full shrink-0 mr-4',
                  memberSubmissions[m.id] ? 'bg-[#34C759] shadow-[0_0_6px_rgba(52,199,89,0.4)]' : 'bg-[#4A5568]'
                )"></div>
                <div class="flex-1 min-w-0">
                  <div class="text-[14px] font-medium text-[#E8ECF4]">{{ m.name }}</div>
                  <div class="text-[11px] font-mono text-[#6B7280] mt-0.5">{{ m.role }}</div>
                </div>
                <div class="flex items-center space-x-2">
                  <span v-if="memberSubmissions[m.id]" class="text-[11px] font-mono text-[#22D3EE] bg-[#22D3EE]/10 border border-[#22D3EE]/20 px-2 py-1 rounded">
                    已提交 {{ memberSubmissions[m.id].submittedAt }}
                  </span>
                  <span v-else class="text-[11px] font-mono text-[#F97316] bg-[#F97316]/10 border border-[#F97316]/20 px-2 py-1 rounded">未提交</span>
                  <button
                    v-if="!memberSubmissions[m.id]"
                    @click.stop="sendReminder(m.id)"
                    :class="cn(
                      'text-[11px] font-mono px-2.5 py-1 rounded border transition-all duration-150',
                      sentReminders.has(m.id) ? 'text-[#94A3B8] border-[#252A3A] cursor-default' : 'text-[#3B9EFF] border-[#3B9EFF]/25 hover:bg-[#3B9EFF]/10'
                    )"
                  >{{ sentReminders.has(m.id) ? '已催' : '催办' }}</button>
                </div>
              </div>
            </div>
            <div class="p-3 border-t border-[#252A3A]">
              <button
                @click="sendAllReminders"
                class="w-full text-[14px] py-2.5 rounded-lg border border-[#3B9EFF]/25 bg-[#3B9EFF]/8 text-[#3B9EFF] hover:bg-[#3B9EFF]/15 hover:border-[#3B9EFF]/40 transition-all flex items-center justify-center space-x-2"
              >
                <Promotion class="w-3.5 h-3.5" />
                <span>一键邮件催办全部未提交委员</span>
              </button>
              <button
                v-if="stepStatuses[0] !== 'done'"
                @click="markStepDone(0)"
                class="w-full mt-2 text-[14px] py-2.5 rounded-lg border border-[#34C759]/25 bg-[#34C759]/8 text-[#34C759] hover:bg-[#34C759]/15 hover:border-[#34C759]/40 transition-all flex items-center justify-center space-x-2"
              >
                <Check class="w-3.5 h-3.5" />
                <span>完成会前收集</span>
              </button>
              <div v-else class="w-full mt-2 text-[14px] py-2.5 rounded-lg border border-[#34C759]/30 bg-[#34C759]/10 text-[#34C759] flex items-center justify-center space-x-2">
                <Check class="w-3.5 h-3.5" />
                <span>会前收集已完成</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── 委员视角 (班子/部门长/投资经理): 纯填报入口 ── -->
      <div v-else-if="step === 0 && !isSecretary" class="pb-4">

        <!-- 已提交：只读确认状态 -->
        <div v-if="memberSubmitted" class="bg-[#202431] border border-[#34C759]/20 rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#34C759]/10 to-[#202431] border-b border-[#34C759]/15 px-6 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 rounded-full bg-[#34C759]/15 border border-[#34C759]/30 flex items-center justify-center">
                <Check class="w-4 h-4 text-[#34C759]" />
              </div>
              <div>
                <h3 class="text-[15px] font-bold text-[#34C759]">已成功提交</h3>
                <p class="text-xs font-mono text-[#94A3B8] mt-0.5">提交于 {{ memberSubmitted.submittedAt }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span :class="cn('text-[11px] font-mono px-2 py-1 rounded border',
                isVoteOpen
                  ? 'bg-[#FFAB00]/10 border-[#FFAB00]/20 text-[#FFAB00]'
                  : 'bg-[#94A3B8]/10 border-[#94A3B8]/20 text-[#94A3B8]')">
                {{ isVoteOpen ? '可更新' : '已锁定' }}
              </span>
            </div>
          </div>
          <div class="p-6 space-y-5">
            <div>
              <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider mb-2">A. 资产评分</div>
              <div class="grid grid-cols-3 gap-3">
                <div v-for="(val, key) in memberSubmitted.sectionA" :key="key" class="bg-[#1A1E2B] border border-[#252A3A] rounded-lg px-4 py-3 flex items-center justify-between">
                  <span class="text-[14px] text-[#B4BAC9]">{{ key }}</span>
                  <span :class="cn('text-[14px] font-bold font-mono', SCORE_COLORS[val])">{{ val }} · {{ SCORE_LABELS[val] }}</span>
                </div>
              </div>
            </div>
            <div>
              <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider mb-2">B. 新高预判</div>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(val, key) in memberSubmitted.sectionB" :key="key"
                  :class="cn('text-xs font-mono px-2.5 py-1 rounded-lg border',
                    val ? 'bg-[#00C9A7]/10 border-[#00C9A7]/25 text-[#00C9A7]' : 'bg-[#1A1E2B] border-[#252A3A] text-[#4A5568]')"
                >{{ key }}: {{ val ? '能' : '不能' }}</span>
              </div>
            </div>
            <div>
              <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider mb-2">C. 重点资产</div>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(checked, key) in memberSubmitted.sectionC" :key="key"
                  :class="cn('text-xs font-mono px-2.5 py-1 rounded-lg border',
                    checked ? 'bg-[#3B9EFF]/10 border-[#3B9EFF]/25 text-[#3B9EFF]' : 'bg-[#1A1E2B] border-[#252A3A] text-[#4A5568]')"
                >{{ key }}</span>
              </div>
            </div>
            <div>
              <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider mb-2">D. 核心观点</div>
              <div class="bg-[#1A1E2B] border border-[#252A3A] rounded-lg px-5 py-4 text-[14px] text-[#B4BAC9] leading-relaxed">{{ memberSubmitted.coreView }}</div>
            </div>
            <div v-if="memberSubmitted.riskFlag" class="flex items-center space-x-2 bg-[#FF9500]/10 border border-[#FF9500]/20 rounded-lg px-4 py-3">
              <Warning class="w-4 h-4 text-[#FF9500] shrink-0" />
              <span class="text-[14px] text-[#FF9500]">已标记：存在需关注的尾部风险事项</span>
            </div>
          </div>
          <!-- 更新并重新提交入口（仅在投票窗口开放时显示） -->
          <div v-if="isVoteOpen" class="px-6 pb-5">
            <button
              @click="clearMemberSubmission"
              class="w-full py-2.5 rounded-xl font-medium text-[14px] border border-[#FFAB00]/30 bg-[#FFAB00]/8 text-[#FFAB00] hover:bg-[#FFAB00]/15 transition-all duration-200 flex items-center justify-center gap-2"
            >
              <Edit class="w-3.5 h-3.5" />
              更新并重新提交
            </button>
          </div>
        </div>

        <!-- 未提交：全宽填报表单 -->
        <div v-else class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-6 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#3B9EFF] to-[#22D3EE] flex items-center justify-center shadow-[0_0_14px_rgba(59,158,255,0.25)]">
                <Edit class="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 class="am-title-l2"><div class="am-title-bar"></div>资配观点填报</h3>
                <p class="text-[11px] font-mono text-[#6B7280] mt-0.5">2026 Q2 · 请在截止时间前完成提交</p>
              </div>
            </div>
            <button @click="showHistoryModal = true" class="text-[13px] text-[#3B9EFF] bg-[#3B9EFF]/10 border border-[#3B9EFF]/25 hover:bg-[#3B9EFF]/18 hover:border-[#3B9EFF]/40 px-2.5 py-1 rounded flex items-center gap-1.5 transition-colors shrink-0">
              <Connection class="w-3 h-3" /> 查看历史投票
            </button>
          </div>
          <div class="p-6 space-y-6">
            <!-- A+B Unified: 资产评分 + 新高预判 (每行一个资产) -->
            <div>
              <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider mb-3">资产评分 (1-5档) & 新高预判</div>
              <div class="space-y-2">
                <div v-for="item in ASSET_LIST" :key="item" class="bg-[#1A1E2B] border border-[#252A3A] rounded-lg px-5 py-3 flex items-center gap-3">
                  <span class="text-[15px] text-[#E8ECF4] font-medium w-24 shrink-0">{{ item }}</span>
                  <div class="flex space-x-1">
                    <button
                      v-for="n in 5" :key="n"
                      @click="FORM_SECTION_A[item] = n"
                      :class="cn(
                        'w-8 h-7 text-[13px] rounded border transition-all duration-150 font-bold font-mono',
                        FORM_SECTION_A[item] === n ? SCORE_COLORS[n] : SCORE_INACTIVE
                      )"
                    >{{ n }}</button>
                  </div>
                  <span class="text-[13px] font-mono w-20 text-right shrink-0" :class="FORM_SECTION_A[item] >= 4 ? 'text-[#F04864]' : FORM_SECTION_A[item] <= 2 ? 'text-[#00C9A7]' : 'text-[#94A3B8]'">{{ SCORE_LABELS[FORM_SECTION_A[item]] }}</span>
                  <div class="w-px h-5 bg-[#2E3348] shrink-0"></div>
                  <label class="flex items-center gap-1.5 cursor-pointer shrink-0 select-none">
                    <button
                      @click="FORM_SECTION_B[item] = !FORM_SECTION_B[item]"
                      :class="cn('relative w-7 h-3.5 rounded-full transition-colors duration-200 border shrink-0',
                        FORM_SECTION_B[item] ? 'bg-[#00C9A7] border-[#00C9A7]' : 'bg-[#252A3A] border-[#2E3348]')"
                    >
                      <div :class="cn('absolute top-0.5 w-2.5 h-2.5 rounded-full bg-white shadow-sm transition-all duration-200',
                        FORM_SECTION_B[item] ? 'left-3.5' : 'left-0.5')"></div>
                    </button>
                    <span class="text-[13px] text-[#94A3B8] whitespace-nowrap">创新高</span>
                  </label>
                </div>
              </div>
            </div>
            <!-- C: 重点资产多选 -->
            <div>
              <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider mb-3">C. 重点资产（多选）</div>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="item in QUESTIONNAIRE_CONFIG.sections[2].items" :key="item"
                  @click="FORM_SECTION_C[item] = !FORM_SECTION_C[item]"
                  :class="cn(
                    'px-3.5 py-1.5 text-[14px] rounded-lg border transition-all duration-150 font-medium',
                    FORM_SECTION_C[item]
                      ? 'bg-[#3B9EFF]/15 border-[#3B9EFF]/40 text-[#3B9EFF]'
                      : 'bg-[#1A1E2B] border-[#252A3A] text-[#6B7280] hover:border-[#2E3348] hover:text-[#94A3B8]'
                  )"
                >{{ item }}</button>
              </div>
            </div>
            <!-- D: 核心观点 Textarea -->
            <div>
              <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider mb-3">D. 核心观点与论据</div>
              <textarea
                v-model="formCoreView"
                rows="5"
                class="w-full bg-[#1A1E2B] border border-[#2E3348] rounded-xl px-5 py-4 text-[15px] text-[#B4BAC9] placeholder-[#3A4555] outline-none focus:border-[#3B9EFF]/45 focus:shadow-[0_0_20px_rgba(59,158,255,0.06)] transition-all resize-none leading-relaxed"
                placeholder="请输入您对本季度市场的核心判断与主要论据，将在会议屏幕上作为讨论依据展示..."
              ></textarea>
              <div class="flex items-center justify-between mt-1.5">
                <div
                  @click="formRiskFlag = !formRiskFlag"
                  :class="cn(
                    'flex items-center space-x-2 px-3 py-1.5 rounded-lg border cursor-pointer transition-all duration-150',
                    formRiskFlag ? 'bg-[#FF9500]/10 border-[#FF9500]/25' : 'bg-[#1A1E2B] border-[#252A3A] hover:border-[#2E3348]'
                  )"
                >
                  <div :class="cn('w-3.5 h-3.5 rounded border flex items-center justify-center shrink-0 transition-all', formRiskFlag ? 'bg-[#FF9500] border-[#FF9500]' : 'border-[#2E3348]')">
                    <Check v-if="formRiskFlag" class="w-2 h-2 text-white" />
                  </div>
                  <span class="text-xs" :class="formRiskFlag ? 'text-[#FF9500]' : 'text-[#94A3B8]'">标记尾部风险事项</span>
                </div>
                <span class="text-[11px] font-mono text-[#4A5568]">{{ formCoreView.length }} 字</span>
              </div>
            </div>
          </div>
          <div class="p-5 border-t border-[#252A3A] space-y-2">
            <!-- 投票窗口已关闭提示 -->
            <div v-if="!isVoteOpen" class="flex items-center gap-2 bg-[#F04864]/8 border border-[#F04864]/20 rounded-lg px-4 py-2.5">
              <Warning class="w-3.5 h-3.5 text-[#F04864] shrink-0" />
              <span class="text-[13px] text-[#F04864]">投票窗口已截止，无法提交</span>
            </div>
            <button
              @click="submitMemberFormSelf"
              :disabled="!formCoreView.trim() || !isVoteOpen"
              :class="cn(
                'w-full py-3.5 rounded-xl font-bold text-[15px] transition-all duration-200',
                formCoreView.trim() && isVoteOpen
                  ? 'bg-gradient-to-r from-[#3B9EFF] to-[#22D3EE] text-white shadow-[0_4px_24px_rgba(59,158,255,0.3)] hover:shadow-[0_4px_36px_rgba(59,158,255,0.45)] active:scale-[0.99]'
                  : 'bg-[#1A1E2B] border border-[#252A3A] text-[#4A5568] cursor-not-allowed'
              )"
            >{{ !isVoteOpen ? '投票已截止' : '确认提交本次观点' }}</button>
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════════════
           STEP 1: 会中 · 回顾复盘 · 归因 (大屏演示)
      ════════════════════════════════════════════════════════════ -->
      <div v-if="step === 1" class="space-y-4 pb-4">

        <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden shadow-lg">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5 flex items-center justify-between">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>指引表现 · 收益曲线回溯对比</h3>
            <span class="text-xs font-mono text-[#94A3B8] bg-[#1A1E2B] px-2.5 py-1 rounded border border-[#252A3A]">区间: 2025.10 — 2026.03</span>
          </div>
          <div class="p-5">
            <div class="relative h-[180px] w-full">
              <svg class="absolute inset-0 w-full h-full" viewBox="0 0 760 160" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="fillBlue2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#3B9EFF" stop-opacity="0.12" />
                    <stop offset="100%" stop-color="#3B9EFF" stop-opacity="0" />
                  </linearGradient>
                </defs>
                <line x1="0" y1="20" x2="760" y2="20" stroke="#252A3A" stroke-width="1" />
                <line x1="0" y1="60" x2="760" y2="60" stroke="#252A3A" stroke-width="1" />
                <line x1="0" y1="100" x2="760" y2="100" stroke="#252A3A" stroke-width="1" />
                <line x1="0" y1="140" x2="760" y2="140" stroke="#2E3348" stroke-width="1" />
                <line x1="127" y1="0" x2="127" y2="140" stroke="#252A3A" stroke-width="0.5" stroke-dasharray="3,4" />
                <line x1="254" y1="0" x2="254" y2="140" stroke="#252A3A" stroke-width="0.5" stroke-dasharray="3,4" />
                <line x1="381" y1="0" x2="381" y2="140" stroke="#252A3A" stroke-width="0.5" stroke-dasharray="3,4" />
                <line x1="508" y1="0" x2="508" y2="140" stroke="#252A3A" stroke-width="0.5" stroke-dasharray="3,4" />
                <line x1="635" y1="0" x2="635" y2="140" stroke="#252A3A" stroke-width="0.5" stroke-dasharray="3,4" />
                <path d="M0,120 L127,104 L254,82 L381,74 L508,58 L635,52 L760,44 L760,140 L0,140 Z" fill="url(#fillBlue2)" />
                <polyline points="0,120 127,104 254,82 381,74 508,58 635,52 760,44" fill="none" stroke="#3B9EFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
                <polyline points="0,120 127,110 254,92 381,85 508,76 635,68 760,62" fill="none" stroke="#22D3EE" stroke-width="2" stroke-dasharray="7,4" stroke-linecap="round" />
                <polyline points="0,120 127,106 254,86 381,95 508,64 635,50 760,40" fill="none" stroke="#F1C40F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
                <circle v-for="(pt, i) in [[127,106],[254,86],[381,95],[508,64],[635,50],[760,40]]" :key="i" :cx="pt[0]" :cy="pt[1]" r="3" fill="#F1C40F" />
              </svg>
              <div class="absolute left-0 top-0 bottom-5 flex flex-col justify-between text-[11px] font-mono text-[#6B7280] pointer-events-none">
                <span>+5.5%</span><span>+3.8%</span><span>+2.1%</span><span>+0.4%</span>
              </div>
              <div class="absolute bottom-0 left-6 right-0 flex justify-between text-[11px] font-mono text-[#6B7280]">
                <span>Oct '25</span><span>Nov '25</span><span>Dec '25</span><span>Jan '26</span><span>Feb '26</span><span>Mar '26</span>
              </div>
            </div>
            <div class="flex items-center space-x-6 mt-4 pl-6">
              <div class="flex items-center space-x-2"><div class="w-7 h-[2.5px] bg-[#3B9EFF] rounded-full"></div><span class="text-xs text-[#B4BAC9] font-mono">委员会指引</span></div>
              <div class="flex items-center space-x-2"><svg width="28" height="3"><line x1="0" y1="1.5" x2="28" y2="1.5" stroke="#22D3EE" stroke-width="2" stroke-dasharray="5,3" /></svg><span class="text-xs text-[#B4BAC9] font-mono">部门指引</span></div>
              <div class="flex items-center space-x-2"><div class="w-7 h-[2.5px] bg-[#F1C40F] rounded-full"></div><span class="text-xs text-[#B4BAC9] font-mono">实际收益</span></div>
            </div>

            <!-- ── 指引表现总结区 ───────────────────────────────────── -->
            <div class="mt-5 grid grid-cols-2 gap-4">
              <!-- 定量分析 (系统自动生成) -->
              <div class="bg-[#0D1520] border border-[#3B9EFF]/20 rounded-lg p-4">
                <div class="flex items-center space-x-2 mb-2.5">
                  <div class="w-1.5 h-1.5 rounded-full bg-[#3B9EFF] shrink-0 animate-pulse"></div>
                  <span class="text-xs font-mono text-[#3B9EFF] uppercase tracking-widest">【定量分析】 · 系统自动生成</span>
                </div>
                <p class="text-[13px] leading-[1.7] text-[#B4BAC9] font-mono">{{ guidanceQuantAnalysis }}</p>
              </div>
              <!-- 定性评价 (PM 可编辑) -->
              <div class="bg-[#0D1520] border border-[#FFAB00]/20 rounded-lg p-4 flex flex-col">
                <div class="flex items-center space-x-2 mb-2.5">
                  <div class="w-1.5 h-1.5 rounded-full bg-[#FFAB00] shrink-0"></div>
                  <span class="text-xs font-mono text-[#FFAB00] uppercase tracking-widest">【定性评价】 · PM 主观复盘</span>
                </div>
                <template v-if="isSecretary || isChairman">
                  <textarea
                    v-model="guidanceQualReview"
                    rows="4"
                    placeholder="请 PM 填写上期指引执行情况的主观复盘，包括策略偏离原因、市场判断依据、改进方向等…"
                    class="flex-1 bg-transparent border border-[#FFAB00]/15 rounded text-[13px] leading-[1.7] text-[#E8ECF4] font-mono placeholder-[#4A5568] p-2.5 resize-none focus:outline-none focus:border-[#FFAB00]/40 transition-colors"
                  ></textarea>
                </template>
                <template v-else>
                  <p class="flex-1 text-[13px] leading-[1.7] text-[#B4BAC9] font-mono min-h-[5rem]">
                    {{ guidanceQualReview || '—' }}
                  </p>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- ── 产品表现：三类别深度视图 ────────────────────────────── -->
        <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden shadow-lg">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5 flex items-center justify-between">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>产品类别表现 · 深度绩效归因</h3>
            <div class="flex items-center space-x-2">
              <div class="w-1.5 h-1.5 rounded-full bg-[#34C759] shrink-0"></div>
              <span class="text-[11px] font-mono text-[#94A3B8]">最后同步 09:47:32</span>
            </div>
          </div>
          <div class="p-5 space-y-6">
            <div v-for="cat in PRODUCT_CATEGORIES" :key="cat.label">
              <!-- 类别标题行 -->
              <div class="flex items-center space-x-3 mb-3">
                <div class="h-px flex-1 bg-gradient-to-r from-transparent" :style="{ backgroundImage: `linear-gradient(to right, transparent, ${cat.color}33)` }"></div>
                <span class="text-xs font-bold font-mono uppercase tracking-widest px-3 py-1 rounded border" :style="{ color: cat.color, borderColor: cat.color + '40', background: cat.color + '12' }">
                  【{{ cat.label }}】 · {{ cat.tag }}
                </span>
                <div class="h-px flex-1 bg-gradient-to-l from-transparent" :style="{ backgroundImage: `linear-gradient(to left, transparent, ${cat.color}33)` }"></div>
              </div>
              <!-- 产品卡片列表 -->
              <div class="space-y-3">
                <div v-for="item in cat.items" :key="item.name"
                     class="bg-[#1A1E2B] border rounded-xl px-4 py-3.5 transition-colors hover:border-white/10"
                     :style="{ borderColor: (item.ret >= 0 ? '#3B9EFF' : '#F04864') + '28' }">
                  <!-- 顶行: 名称 + 竞品排名 + 区间收益 -->
                  <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center space-x-3">
                      <span class="text-[14px] font-semibold text-[#E8ECF4]">{{ item.name }}</span>
                      <!-- 竞品排名徽章 -->
                      <span class="text-[11px] font-bold font-mono px-2 py-1 rounded-full border"
                            :class="item.rankTier === 1 ? 'bg-[#F04864]/10 border-[#F04864]/35 text-[#F04864]' : item.rankTier === 2 ? 'bg-[#FFAB00]/10 border-[#FFAB00]/35 text-[#FFAB00]' : 'bg-[#00C9A7]/10 border-[#00C9A7]/35 text-[#00C9A7]'">
                        {{ item.rank }}
                      </span>
                      <span class="text-[11px] font-mono text-[#6B7280]">竞品排名</span>
                    </div>
                    <div class="text-right">
                      <span class="text-[14px] font-bold font-mono" :class="item.ret >= 0 ? 'text-[#F04864]' : 'text-[#00C9A7]'">
                        {{ item.ret >= 0 ? '+' : '' }}{{ item.ret.toFixed(1) }}%
                      </span>
                      <span class="text-[11px] font-mono text-[#6B7280] ml-1.5">区间收益</span>
                    </div>
                  </div>
                  <!-- 收益来源分析 + 择时择券评价 双列 -->
                  <div class="grid grid-cols-2 gap-4">
                    <!-- 收益来源分析 -->
                    <div>
                      <div class="text-[11px] font-mono text-[#94A3B8] uppercase tracking-widest mb-2">收益来源分析</div>
                      <div class="space-y-1.5">
                        <div class="flex items-center justify-between">
                          <span class="text-[11px] font-mono text-[#6B7280] w-16">Beta 收益</span>
                          <div class="flex-1 mx-2 h-1.5 bg-[#252A3A] rounded-full overflow-hidden">
                            <div class="h-full rounded-full" :style="{ width: `${Math.abs(item.beta) / 5 * 100}%`, background: item.beta >= 0 ? '#3B9EFF' : '#F04864' }"></div>
                          </div>
                          <span class="text-[11px] font-mono w-10 text-right" :class="item.beta >= 0 ? 'text-[#3B9EFF]' : 'text-[#F04864]'">{{ item.beta >= 0 ? '+' : '' }}{{ item.beta.toFixed(1) }}%</span>
                        </div>
                        <div class="flex items-center justify-between">
                          <span class="text-[11px] font-mono text-[#6B7280] w-16">Alpha 收益</span>
                          <div class="flex-1 mx-2 h-1.5 bg-[#252A3A] rounded-full overflow-hidden">
                            <div class="h-full rounded-full" :style="{ width: `${Math.abs(item.alpha) / 5 * 100}%`, background: item.alpha >= 0 ? '#FFAB00' : '#F04864' }"></div>
                          </div>
                          <span class="text-[11px] font-mono w-10 text-right" :class="item.alpha >= 0 ? 'text-[#FFAB00]' : 'text-[#F04864]'">{{ item.alpha >= 0 ? '+' : '' }}{{ item.alpha.toFixed(1) }}%</span>
                        </div>
                        <div class="flex items-center justify-between">
                          <span class="text-[11px] font-mono text-[#6B7280] w-16">杠杆收益</span>
                          <div class="flex-1 mx-2 h-1.5 bg-[#252A3A] rounded-full overflow-hidden">
                            <div class="h-full rounded-full" :style="{ width: `${Math.abs(item.lev) / 2 * 100}%`, background: item.lev >= 0 ? '#22D3EE' : '#F04864' }"></div>
                          </div>
                          <span class="text-[11px] font-mono w-10 text-right" :class="item.lev >= 0 ? 'text-[#22D3EE]' : 'text-[#F04864]'">{{ item.lev >= 0 ? '+' : '' }}{{ item.lev.toFixed(1) }}%</span>
                        </div>
                      </div>
                    </div>
                    <!-- 择时择券评价 + 最大回撤 -->
                    <div>
                      <div class="text-[11px] font-mono text-[#94A3B8] uppercase tracking-widest mb-2">择时择券评价</div>
                      <div class="space-y-1.5">
                        <div class="flex items-center justify-between">
                          <span class="text-[11px] font-mono text-[#6B7280] w-20">调仓贡献度</span>
                          <div class="flex-1 mx-2 h-1.5 bg-[#252A3A] rounded-full overflow-hidden">
                            <div class="h-full rounded-full" :style="{ width: `${Math.min(100, Math.abs(item.timing) / 25 * 100)}%`, background: item.timing >= 0 ? '#3B9EFF' : '#F04864' }"></div>
                          </div>
                          <span class="text-[11px] font-mono w-14 text-right" :class="item.timing >= 0 ? 'text-[#3B9EFF]' : 'text-[#F04864]'">{{ item.timing >= 0 ? '+' : '' }}{{ item.timing }} bps</span>
                        </div>
                        <div class="flex items-center justify-between">
                          <span class="text-[11px] font-mono text-[#6B7280] w-20">择券胜率</span>
                          <div class="flex-1 mx-2 h-1.5 bg-[#252A3A] rounded-full overflow-hidden">
                            <div class="h-full rounded-full" :style="{ width: `${item.selRate}%`, background: item.selRate >= 60 ? '#F04864' : item.selRate >= 50 ? '#FFAB00' : '#00C9A7' }"></div>
                          </div>
                          <span class="text-[11px] font-mono w-14 text-right" :class="item.selRate >= 60 ? 'text-[#F04864]' : item.selRate >= 50 ? 'text-[#FFAB00]' : 'text-[#00C9A7]'">{{ item.selRate }}%</span>
                        </div>
                        <div class="flex items-center justify-between">
                          <span class="text-[11px] font-mono text-[#6B7280] w-20">最大回撤</span>
                          <div class="flex-1 mx-2"></div>
                          <span class="text-[11px] font-mono text-[#F04864] w-14 text-right">{{ item.maxdd }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden shadow-lg">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>策略池红黑榜 · 本季度末综合评估</h3>
          </div>
          <div class="p-5 grid grid-cols-2 gap-5">
            <div>
              <div class="flex items-center space-x-2 mb-3">
                <div class="w-1.5 h-1.5 rounded-full bg-[#22D3EE]"></div>
                <span class="text-xs font-mono text-[#22D3EE] uppercase tracking-wider">Top 5 优选子策略</span>
              </div>
              <div class="space-y-2">
                <div v-for="(s, i) in TOP_STRATEGIES" :key="i" class="bg-[#1A1E2B] border border-[#22D3EE]/10 rounded-lg px-4 py-3 flex items-center justify-between hover:border-[#22D3EE]/25 transition-colors">
                  <div class="flex items-center space-x-3">
                    <span class="text-xs font-bold font-mono text-[#22D3EE]/50 w-4 shrink-0">#{{ i + 1 }}</span>
                    <div>
                      <div class="text-[14px] font-medium text-[#E8ECF4]">{{ s.name }}</div>
                      <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">{{ s.type }}</div>
                    </div>
                  </div>
                  <div class="text-right shrink-0 ml-3">
                    <div class="text-[14px] font-bold font-mono text-[#22D3EE]">{{ s.return }}</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono">夏普 {{ s.sharpe }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div>
              <div class="flex items-center space-x-2 mb-3">
                <div class="w-1.5 h-1.5 rounded-full bg-[#FF3B30] animate-pulse"></div>
                <span class="text-xs font-mono text-[#FF3B30] uppercase tracking-wider">需检视劣后策略</span>
                <span class="text-[11px] font-mono text-[#FF3B30]/60 bg-[#FF3B30]/10 border border-[#FF3B30]/20 px-1.5 py-1 rounded">预警</span>
              </div>
              <div class="space-y-2">
                <div v-for="(s, i) in BOTTOM_STRATEGIES" :key="i" class="bg-[#1A1E2B] border border-[#FF3B30]/15 rounded-lg px-4 py-3 flex items-center justify-between hover:border-[#FF3B30]/30 transition-colors">
                  <div class="flex items-center space-x-3">
                    <div class="w-1 h-8 rounded-full bg-[#FF3B30]/50 shrink-0"></div>
                    <div>
                      <div class="text-[14px] font-medium text-[#E8ECF4]">{{ s.name }}</div>
                      <div class="text-[11px] text-[#FF3B30]/70 font-mono mt-0.5">{{ s.issue }}</div>
                    </div>
                  </div>
                  <div class="text-right shrink-0 ml-3">
                    <div class="text-[14px] font-bold font-mono text-[#FF3B30]">{{ s.return }}</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono">最大回撤 {{ s.maxdd }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════════════
           STEP 2: 会中 · 讨论与量化参考 (大屏演示)
      ════════════════════════════════════════════════════════════ -->
      <div v-if="step === 2" class="space-y-4 pb-4">

        <!-- ══ Voting Matrix (转置: 行=委员, 列=资产) ══ -->
        <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5 flex items-center justify-between">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>委员投票明细矩阵</h3>
            <div class="flex items-center gap-3">
              <span class="text-[13px] font-mono text-[#94A3B8]">{{ MEMBERS_DATA.length }} 名委员 · {{ ASSET_LIST.length }} 项资产</span>
              <button @click="showHistoryModal = true" class="text-[13px] text-[#3B9EFF] bg-[#3B9EFF]/10 border border-[#3B9EFF]/25 hover:bg-[#3B9EFF]/18 hover:border-[#3B9EFF]/40 px-2.5 py-1 rounded flex items-center gap-1.5 transition-colors">
                <Connection class="w-3 h-3" /> 查询历史期会审结果
              </button>
            </div>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full border-collapse table-fixed text-[14px]">
              <thead class="bg-[#1A1E2B] border-b border-[#2E3348]">
                <tr>
                  <th class="px-4 py-2.5 text-left text-[13px] text-[#94A3B8] font-semibold" style="width:135px">委员</th>
                  <th v-for="asset in ASSET_LIST" :key="asset" class="px-2 py-2.5 text-center text-[13px] text-[#B4BAC9] font-medium">
                    <div class="truncate">{{ asset }}</div>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#252A3A]">
                <tr v-for="member in MEMBERS_DATA" :key="member.id" class="hover:bg-[#1A1E2B]/50 transition-colors">
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-1.5">
                      <span class="text-[#E8ECF4] font-semibold">{{ member.name }}</span>
                      <span v-if="member.role === '主任委员'" class="text-[11px] font-mono px-1 py-1 rounded bg-[#FFAB00]/15 border border-[#FFAB00]/30 text-[#FFAB00]">主任委员</span>
                    </div>
                  </td>
                  <td v-for="asset in ASSET_LIST" :key="asset" class="px-2 py-3 text-center relative">
                    <template v-if="memberSubmissions[member.id]">
                      <span :class="cn('text-[15px] font-mono font-bold tabular-nums',
                        MATRIX_COL_EXTREMES[asset]?.max === memberSubmissions[member.id].sectionA[asset] && MATRIX_COL_EXTREMES[asset]?.max !== MATRIX_COL_EXTREMES[asset]?.min ? 'text-[#F04864]' :
                        MATRIX_COL_EXTREMES[asset]?.min === memberSubmissions[member.id].sectionA[asset] && MATRIX_COL_EXTREMES[asset]?.max !== MATRIX_COL_EXTREMES[asset]?.min ? 'text-[#00C9A7]' :
                        'text-[#E8ECF4]')">{{ memberSubmissions[member.id].sectionA[asset] }}</span>
                      <span v-if="memberSubmissions[member.id].sectionB[asset]" class="text-[11px] text-[#FFAB00] ml-0.5" title="预期创新高">&#9650;</span>
                    </template>
                    <span v-else class="text-[#4A5568]">-</span>
                  </td>
                </tr>
              </tbody>
              <tfoot class="bg-[#1A1E2B] border-t border-[#2E3348]">
                <tr>
                  <td class="px-4 py-2.5 text-[13px] text-[#FFAB00] font-bold">列均值</td>
                  <td v-for="asset in ASSET_LIST" :key="asset" class="px-2 py-2.5 text-center">
                    <span class="text-[15px] font-mono font-bold tabular-nums text-[#FFAB00]">{{ MATRIX_COL_AVG[asset]?.toFixed(1) ?? '-' }}</span>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
          <div class="px-5 py-2.5 border-t border-[#2E3348] bg-[#161922] flex items-center justify-between text-[13px] text-[#64748B]">
            <span class="font-mono">评分对照: 1-谨慎 · 2-中性偏谨慎 · 3-中性 · 4-中性偏乐观 · 5-乐观</span>
            <span class="flex items-center gap-3">
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[#F04864]"></span> 列最高分</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[#00C9A7]"></span> 列最低分</span>
              <span class="flex items-center gap-1"><span class="text-[#FFAB00]">&#9650;</span> 预期创新高</span>
            </span>
          </div>
        </div>

        <!-- ══ Consensus Summary ══ -->
        <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5 flex items-center justify-between">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>会议共识与边际变化</h3>
            <span class="text-[13px] font-mono text-[#94A3B8]">综合 {{ submittedCount }} 份问卷</span>
          </div>
          <div class="p-5 grid grid-cols-3 gap-3">
            <div v-for="ca in CONSENSUS_ANALYSIS" :key="ca.asset" class="bg-[#1A1E2B] border border-[#252A3A] rounded-lg p-3.5">
              <div class="flex items-center justify-between mb-2">
                <span class="text-[14px] font-bold text-[#E8ECF4]">{{ ca.asset }}</span>
                <span :class="cn('text-[13px] font-mono font-bold px-2 py-1 rounded border',
                  ca.label === '乐观' ? 'bg-[#F04864]/10 text-[#F04864] border-[#F04864]/25' :
                  ca.label === '中性偏乐观' ? 'bg-[#FFAB00]/10 text-[#FFAB00] border-[#FFAB00]/25' :
                  ca.label === '中性' ? 'bg-[#3B9EFF]/10 text-[#3B9EFF] border-[#3B9EFF]/25' :
                  'bg-[#00C9A7]/10 text-[#00C9A7] border-[#00C9A7]/25')">{{ ca.label }}</span>
              </div>
              <div class="flex items-baseline gap-2 mb-1.5">
                <span class="text-lg font-bold font-mono tabular-nums text-[#FFAB00]">{{ ca.avg.toFixed(1) }}</span>
                <span class="text-[13px] font-mono" :class="ca.delta > 0 ? 'text-[#F04864]' : ca.delta < 0 ? 'text-[#00C9A7]' : 'text-[#94A3B8]'">
                  {{ ca.delta > 0 ? '+' : '' }}{{ ca.delta.toFixed(1) }} vs 上期
                  <span v-if="ca.delta > 0">&#9650;</span>
                  <span v-else-if="ca.delta < 0">&#9660;</span>
                </span>
              </div>
              <div class="flex items-center justify-between text-[13px] text-[#94A3B8]">
                <span>{{ ca.newHighCount }} 人看创新高</span>
                <span :class="cn('font-mono', ca.consensus === '高度一致' ? 'text-[#22D3EE]' : ca.consensus === '方向趋同' ? 'text-[#3B9EFF]' : 'text-[#FFAB00]')">{{ ca.consensus }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>多模型量化锚点 · 建议权益权重对比</h3>
          </div>
          <div class="p-5 grid grid-cols-3 gap-4">
            <div
              v-for="m in MODEL_OUTPUTS" :key="m.name"
              :class="cn(
                'bg-[#1A1E2B] border rounded-xl p-4 flex flex-col space-y-3 transition-all duration-200',
                m.highlight ? 'border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.07)]' : 'border-[#252A3A] hover:border-[#2E3348]'
              )"
            >
              <div class="flex items-start justify-between">
                <div>
                  <span class="text-[11px] font-mono px-2 py-1 rounded-full border" :style="{ color: m.color, borderColor: m.color + '40', backgroundColor: m.color + '15' }">{{ m.badge }}</span>
                  <div class="text-[15px] font-bold text-white mt-1.5">{{ m.name }}</div>
                  <div class="text-xs text-[#94A3B8] mt-0.5 leading-relaxed">{{ m.desc }}</div>
                </div>
              </div>
              <div class="space-y-2">
                <div v-for="alloc in m.allocations" :key="alloc.label" class="space-y-1">
                  <div class="flex justify-between">
                    <span class="text-xs text-[#94A3B8] font-mono">{{ alloc.label }}</span>
                    <span class="text-xs font-bold font-mono text-white">{{ alloc.weight }}%</span>
                  </div>
                  <div class="h-1.5 bg-[#161922] rounded-full overflow-hidden">
                    <div :style="{ width: `${alloc.weight}%`, backgroundColor: alloc.color }" class="h-full rounded-full"></div>
                  </div>
                </div>
              </div>
              <div class="pt-1 border-t border-[#252A3A]">
                <div class="flex justify-between items-center">
                  <span class="text-[11px] font-mono text-[#6B7280]">预期夏普: <span class="text-[#F1C40F]">{{ m.sharpe }}</span></span>
                  <button
                    v-if="m.action"
                    @click="showSAASandbox = true"
                    class="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 transition-colors"
                  >
                    <span>进入沙盘</span>
                    <ArrowRight class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5 flex items-center justify-between">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>会前问卷汇总 · 委员定性观点</h3>
            <div class="flex items-center space-x-2">
              <div class="w-1.5 h-1.5 rounded-full bg-[#3B9EFF] animate-pulse"></div>
              <span class="text-xs font-mono text-[#94A3B8]">来自会前收集 · 会中讨论参考</span>
            </div>
          </div>
          <div class="p-5 grid grid-cols-2 gap-3" v-if="committeeQualitativeViews.length > 0">
            <div
              v-for="(view, i) in committeeQualitativeViews" :key="view.author + i"
              class="bg-[#1A1E2B] border border-[#252A3A] rounded-lg p-4 hover:border-[#2E3348] transition-all duration-200"
            >
              <div class="flex items-start justify-between mb-2.5">
                <div class="flex items-center space-x-2">
                  <div class="w-1 h-full min-h-[14px] rounded-full shrink-0" :style="{ backgroundColor: view.color, width: '3px' }"></div>
                  <span class="text-xs font-bold font-mono" :style="{ color: view.color }">{{ view.role }}</span>
                  <span class="text-xs text-[#94A3B8]">{{ view.author }}</span>
                </div>
                <span :class="cn('text-[11px] px-2 py-1 rounded-full border font-mono shrink-0 ml-2', view.sentiment === '偏多' ? 'bg-[#3B9EFF]/10 border-[#3B9EFF]/20 text-[#3B9EFF]' : view.sentiment === '偏空' ? 'bg-[#FF3B30]/10 border-[#FF3B30]/20 text-[#FF3B30]' : 'bg-[#F1C40F]/10 border-[#F1C40F]/20 text-[#F1C40F]')">{{ view.sentiment }}</span>
              </div>
              <p class="text-[14px] text-[#B4BAC9] leading-relaxed">{{ view.content }}</p>
              <div class="flex flex-wrap gap-1.5 mt-2.5">
                <span v-for="tag in view.tags" :key="tag" class="text-[11px] text-[#94A3B8] bg-[#202431] border border-[#252A3A] px-1.5 py-1 rounded font-mono">{{ tag }}</span>
              </div>
            </div>
          </div>
          <div v-else class="p-8 text-center text-[#64748B] text-[14px]">
            暂无委员提交问卷观点
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════════════
           STEP 3: 会后 · 配置指引 · 决策
      ════════════════════════════════════════════════════════════ -->
      <div v-if="step === 3" class="space-y-4 pb-4">

        <!-- ══ Card 1: 主任委员决策矩阵 ══ -->
        <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <h3 class="am-title-l2"><div class="am-title-bar"></div>配置决策矩阵 · 主任委员定调</h3>
              <span v-if="!isReadOnly" class="text-[11px] font-mono px-2 py-1 rounded bg-[#FFAB00]/15 border border-[#FFAB00]/30 text-[#FFAB00]">主任委员定调模式</span>
              <span v-else class="text-[11px] font-mono px-2 py-1 rounded bg-[#94A3B8]/10 border border-[#2E3348] text-[#64748B]">只读预览</span>
            </div>
            <span class="text-xs font-mono text-[#6B7280]">问卷均值 — 债券 {{ MATRIX_COL_AVG['债券']?.toFixed(1) ?? '-' }} · 权益 {{ MATRIX_COL_AVG['权益-红利']?.toFixed(1) ?? '-' }}</span>
          </div>
          <div class="p-5 space-y-5">

            <!-- ① 固收类久期（产品差异化） -->
            <div class="space-y-3">
              <div class="flex items-start gap-4" v-for="(pid, idx) in (['low','mid','hybrid'] as const)" :key="pid">
                <div class="w-28 shrink-0 pt-1">
                  <div class="text-[13px] font-semibold text-[#E8ECF4]">{{ ['低波产品久期','中波产品久期','混合产品久期'][idx] }}</div>
                  <div class="text-[13px] text-[#94A3B8] font-mono mt-0.5">{{ PRODUCT_BOND_LABELS[pid] }}</div>
                </div>
                <div class="flex gap-2 flex-wrap">
                  <template v-if="!isReadOnly">
                    <button v-for="g in (['高','中','低'] as const)" :key="g"
                      @click="chairDecision.perProductBondGrade[pid] = g"
                      :class="cn('px-4 py-2 rounded-lg border text-[13px] font-bold font-mono transition-all duration-150',
                        chairDecision.perProductBondGrade[pid] === g
                          ? g === '高' ? 'bg-[#F04864]/15 border-[#F04864]/50 text-[#F04864]'
                            : g === '低' ? 'bg-[#00C9A7]/15 border-[#00C9A7]/50 text-[#00C9A7]'
                            : 'bg-[#3B9EFF]/15 border-[#3B9EFF]/50 text-[#3B9EFF]'
                          : 'bg-[#1A1E2B] border-[#2E3348] text-[#6B7280] hover:text-[#94A3B8] hover:border-[#3B9EFF]/30')"
                    >
                      {{ g }}
                      <span class="ml-1.5 text-[11px] opacity-60 font-normal">{{ BOND_GRADE_DURATION[g] }}</span>
                    </button>
                  </template>
                  <template v-else>
                    <span :class="cn('px-4 py-2 rounded-lg border text-[13px] font-bold font-mono',
                      chairDecision.perProductBondGrade[pid] === '高' ? 'bg-[#F04864]/10 border-[#F04864]/30 text-[#F04864]'
                      : chairDecision.perProductBondGrade[pid] === '低' ? 'bg-[#00C9A7]/10 border-[#00C9A7]/30 text-[#00C9A7]'
                      : 'bg-[#3B9EFF]/10 border-[#3B9EFF]/30 text-[#3B9EFF]')">
                      {{ chairDecision.perProductBondGrade[pid] }}
                      <span class="ml-1.5 text-[11px] opacity-60 font-normal">{{ BOND_GRADE_DURATION[chairDecision.perProductBondGrade[pid]] }}</span>
                    </span>
                  </template>
                </div>
              </div>
            </div>

            <div class="h-px bg-[#252A3A]"></div>

            <!-- ② 权益总额评级 -->
            <div class="flex items-start gap-4">
              <div class="w-28 shrink-0 pt-1">
                <div class="text-[13px] font-semibold text-[#E8ECF4]">权益总额评级</div>
                <div class="text-[13px] text-[#94A3B8] font-mono mt-0.5">Equity Stance</div>
              </div>
              <div class="flex gap-2 flex-wrap">
                <template v-if="!isReadOnly">
                  <button v-for="n in [1,2,3,4,5]" :key="n"
                    @click="chairDecision.equityGrade = n"
                    :class="cn('px-3 py-2 rounded-lg border text-xs font-bold font-mono transition-all duration-150 min-w-[72px]',
                      chairDecision.equityGrade === n
                        ? GRADE_COLORS[n]
                        : 'bg-[#1A1E2B] border-[#2E3348] text-[#6B7280] hover:text-[#94A3B8] hover:border-[#3B9EFF]/30')"
                  >
                    <div>{{ n }}</div>
                    <div class="text-[11px] font-normal opacity-70 mt-0.5">{{ SCORE_LABELS[n] }}</div>
                  </button>
                </template>
                <template v-else>
                  <span :class="cn('px-3 py-2 rounded-lg border text-xs font-bold font-mono inline-flex flex-col items-center min-w-[72px]',
                    GRADE_COLORS[chairDecision.equityGrade] || 'bg-[#94A3B8]/10 text-[#94A3B8] border-[#94A3B8]/25')">
                    <span>{{ chairDecision.equityGrade }}</span>
                    <span class="text-[11px] font-normal opacity-70 mt-0.5">{{ SCORE_LABELS[chairDecision.equityGrade] }}</span>
                  </span>
                </template>
              </div>
            </div>

            <div class="h-px bg-[#252A3A]"></div>

            <!-- ③ 权益明细分配 -->
            <div class="flex items-start gap-4">
              <div class="w-28 shrink-0 pt-1">
                <div class="text-[13px] font-semibold text-[#E8ECF4]">权益明细</div>
                <div class="text-[13px] text-[#94A3B8] font-mono mt-0.5">Equity Mix (%)</div>
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-4 flex-wrap">
                  <template v-if="!isReadOnly">
                    <div v-for="k in (['红利','成长','价值'] as const)" :key="k" class="flex items-center gap-2">
                      <span class="text-xs text-[#94A3B8] font-mono w-8">{{ k }}</span>
                      <input type="number" min="0" max="100" step="5"
                        v-model.number="chairDecision.equityMix[k]"
                        class="w-16 bg-[#1A1E2B] border rounded text-[13px] font-mono text-center text-[#E8ECF4] px-2 py-1.5 focus:outline-none transition-colors"
                        :class="equityMixSum === 100 ? 'border-[#2E3348] focus:border-[#3B9EFF]' : 'border-[#F04864]/50 focus:border-[#F04864]'"
                      />
                      <span class="text-xs text-[#6B7280] font-mono">%</span>
                    </div>
                  </template>
                  <template v-else>
                    <div v-for="k in (['红利','成长','价值'] as const)" :key="k" class="flex items-center gap-2">
                      <span class="text-xs text-[#94A3B8] font-mono w-8">{{ k }}</span>
                      <span class="text-[13px] font-mono text-[#E8ECF4] w-10 text-right">{{ chairDecision.equityMix[k] }}</span>
                      <span class="text-xs text-[#6B7280] font-mono">%</span>
                    </div>
                  </template>
                  <span :class="cn('ml-auto text-xs font-bold font-mono px-3 py-1.5 rounded-lg border',
                    equityMixSum === 100
                      ? 'bg-[#00C9A7]/10 border-[#00C9A7]/30 text-[#00C9A7]'
                      : 'bg-[#F04864]/10 border-[#F04864]/40 text-[#F04864] animate-pulse')">
                    合计 {{ equityMixSum }}%
                    <span v-if="equityMixSum !== 100" class="ml-1 opacity-70">≠ 100%</span>
                  </span>
                </div>
              </div>
            </div>

            <div class="h-px bg-[#252A3A]"></div>

            <!-- ④ 另类资产定性 -->
            <div class="flex items-start gap-4">
              <div class="w-28 shrink-0 pt-1">
                <div class="text-[13px] font-semibold text-[#E8ECF4]">另类资产</div>
                <div class="text-[13px] text-[#94A3B8] font-mono mt-0.5">Alternatives (可选)</div>
              </div>
              <template v-if="!isReadOnly">
                <textarea v-model="chairDecision.altNotes" rows="2"
                  placeholder="黄金标配，关注地缘风险；原油谨慎，控制能源敞口…（可留空）"
                  class="flex-1 bg-[#1A1E2B] border border-[#2E3348] rounded-lg text-[13px] font-mono text-[#E8ECF4] placeholder-[#4A5568] px-3 py-2 resize-none focus:outline-none focus:border-[#3B9EFF]/50 transition-colors"
                ></textarea>
              </template>
              <template v-else>
                <p class="flex-1 text-[13px] font-mono text-[#B4BAC9] min-h-[2.5rem]">{{ chairDecision.altNotes || '—' }}</p>
              </template>
            </div>

          </div>
          <!-- 计算按钮 (主任委员专属) -->
          <div v-if="!isReadOnly" class="px-5 py-3.5 border-t border-[#252A3A] bg-[#161922] flex items-center justify-between">
            <span class="text-xs font-mono text-[#6B7280]">设置固收档位、权益评级和权益明细后，点击按钮自动填充三类产品指引仓位</span>
            <button @click="calcProductGuidances"
              :disabled="equityMixSum !== 100"
              :class="cn('px-5 py-2 rounded-lg border text-[13px] font-bold font-mono transition-all duration-200 flex items-center gap-2',
                equityMixSum === 100
                  ? 'bg-[#3B9EFF]/12 border-[#3B9EFF]/40 text-[#3B9EFF] hover:bg-[#3B9EFF]/20 hover:border-[#3B9EFF]/60'
                  : 'bg-[#1A1E2B] border-[#2E3348] text-[#4A5568] cursor-not-allowed')"
            >
              <Cpu class="w-3.5 h-3.5 shrink-0" />
              计算产品指引
            </button>
          </div>
        </div>

        <!-- ══ Card 2: 三类产品配置指引 (三层嵌套表头) ══ -->
        <div class="bg-[#202431] border rounded-xl overflow-hidden transition-all duration-300"
             :class="guidanceCalculated ? 'border-[#3B9EFF]/25' : 'border-[#252A3A]'">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <h3 class="am-title-l2"><div class="am-title-bar"></div>三类产品配置指引</h3>
              <span v-if="guidanceCalculated" class="text-[11px] font-mono px-2 py-1 rounded bg-[#3B9EFF]/10 border border-[#3B9EFF]/25 text-[#3B9EFF]">已计算</span>
              <span v-else class="text-[11px] font-mono px-2 py-1 rounded bg-[#94A3B8]/10 border border-[#2E3348] text-[#64748B]">待计算</span>
            </div>
            <span class="text-xs font-mono text-[#6B7280]">另类/流动性自动读取上期比例</span>
          </div>
          <div class="overflow-x-auto">
            <table class="table-fixed w-full border-collapse font-mono text-[13px]">
              <!-- ── 第一层表头 ── -->
              <thead class="bg-[#1A1E2B] border-b border-[#2E3348]">
                <tr>
                  <th rowspan="2" class="px-3 py-2.5 text-left text-[11px] text-[#94A3B8] font-semibold uppercase tracking-wider border-r border-[#2E3348]" style="width:90px">产品类型</th>
                  <th rowspan="2" class="px-2 py-1.5 text-center text-[11px] text-[#22D3EE] font-semibold uppercase tracking-wider border-r border-[#2E3348]" style="width:130px">固收<br/><span class="text-[10px] font-normal text-[#22D3EE]/50">久期指引</span></th>
                  <th colspan="5" class="px-2 py-1.5 text-center text-[11px] text-[#3B9EFF] font-semibold uppercase tracking-wider border-r border-[#2E3348]">权益</th>
                  <th rowspan="2" class="px-2 py-1.5 text-center text-[11px] text-[#FFAB00] font-semibold uppercase tracking-wider border-r border-[#2E3348]" style="width:110px">另类</th>
                  <th rowspan="2" class="px-2 py-1.5 text-center text-[11px] text-[#94A3B8] font-semibold uppercase tracking-wider" style="width:55px">流动性</th>
                </tr>
                <tr class="border-b border-[#2E3348]">
                  <th class="px-1.5 py-1.5 text-center text-[11px] text-[#3B9EFF]/50 font-normal" style="width:80px">总仓位</th>
                  <th class="px-1.5 py-1.5 text-center text-[11px] text-[#3B9EFF]/50 font-normal">红利</th>
                  <th class="px-1.5 py-1.5 text-center text-[11px] text-[#3B9EFF]/50 font-normal">港股</th>
                  <th class="px-1.5 py-1.5 text-center text-[11px] text-[#3B9EFF]/50 font-normal">其他</th>
                  <th class="px-1.5 py-1.5 text-center text-[11px] text-[#3B9EFF]/50 font-normal border-r border-[#2E3348]">REITS</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#252A3A]">
                <!-- ── 委员会决策行 ── -->
                <tr class="bg-[#252A3A]/40 hover:bg-[#252A3A]/60 transition-colors">
                  <td class="px-3 py-2.5 border-r border-[#2E3348]">
                    <div class="flex items-center gap-1.5">
                      <div class="w-1.5 h-5 rounded-full bg-[#FFAB00] shrink-0"></div>
                      <div>
                        <div class="text-[13px] font-bold text-[#FFAB00]">委员会决策</div>
                        <div class="text-[11px] text-[#FFAB00]/50">DECISION</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-2 py-2.5 text-center border-r border-[#2E3348]">
                    <span class="text-[11px] font-bold text-[#FFAB00]">差异化定调</span>
                    <div class="text-[10px] text-[#FFAB00]/40 font-mono mt-0.5">见 Card 1</div>
                  </td>
                  <td class="px-2 py-2.5 text-center border-r border-[#2E3348]">
                    <span class="text-[13px] font-bold text-[#3B9EFF]">{{ chairDecision.equityGrade }}档</span>
                    <div class="text-[11px] text-[#3B9EFF]/50 mt-0.5">{{ SCORE_LABELS[chairDecision.equityGrade] }}</div>
                  </td>
                  <td class="px-1.5 py-2.5 text-center text-[11px] text-[#94A3B8]">{{ chairDecision.equityMix['红利'] }}%</td>
                  <td class="px-1.5 py-2.5 text-center text-[11px] text-[#94A3B8]">—</td>
                  <td class="px-1.5 py-2.5 text-center text-[11px] text-[#94A3B8]">{{ chairDecision.equityMix['价值'] }}%</td>
                  <td class="px-1.5 py-2.5 text-center text-[11px] text-[#94A3B8] border-r border-[#2E3348]">—</td>
                  <td class="px-2 py-2.5 text-center text-[11px] text-[#FFAB00]/70 border-r border-[#2E3348]">{{ chairDecision.altNotes || '—' }}</td>
                  <td class="px-1.5 py-2.5 text-center text-[11px] text-[#94A3B8]/50">—</td>
                </tr>
                <!-- ── 三类产品指引行 ── -->
                <tr v-for="row in productGuidances" :key="row.id" class="hover:bg-[#1A1E2B]/40 transition-colors">
                  <td class="px-3 py-2.5 border-r border-[#2E3348]">
                    <div class="flex items-center gap-1.5">
                      <div class="w-1.5 h-5 rounded-full shrink-0" :style="{ background: row.color }"></div>
                      <div class="text-[13px] font-semibold text-[#E8ECF4]">{{ row.name }}</div>
                    </div>
                  </td>
                  <!-- 固收: 久期指引文字 -->
                  <td class="px-2 py-2.5 text-center border-r border-[#2E3348]">
                    <span class="text-[11px] font-mono font-semibold text-[#22D3EE]">
                      {{ BOND_GRADE_LABEL[chairDecision.perProductBondGrade[row.id] as BondGrade] }}
                    </span>
                    <template v-if="showHistoryDiff">
                      <span v-if="diffBondGrade(chairDecision.perProductBondGrade[row.id], PREV_SNAPSHOT.perProductBondGrade[row.id])"
                            class="block text-[10px] font-mono font-bold text-[#FFAB00] mt-0.5">
                        {{ diffBondGrade(chairDecision.perProductBondGrade[row.id], PREV_SNAPSHOT.perProductBondGrade[row.id]) }}
                      </span>
                    </template>
                  </td>
                  <!-- 总权益仓位 -->
                  <td class="px-2 py-2.5 text-center border-r border-[#2E3348]">
                    <span class="font-mono text-[13px]"
                          :class="guidanceCalculated ? 'text-[#3B9EFF] font-bold' : 'text-[#2E3348]'">
                      {{ guidanceCalculated ? row.equity + '%' : '—' }}
                    </span>
                    <template v-if="guidanceCalculated && showHistoryDiff">
                      <span v-if="diffBadge(row.equity, PREV_SNAPSHOT.products.find(p => p.id === row.id)!.equity)"
                            class="block text-[10px] font-mono font-bold mt-0.5"
                            :class="(row.equity - PREV_SNAPSHOT.products.find(p => p.id === row.id)!.equity) > 0 ? 'text-[#F04864]' : 'text-[#00C9A7]'">
                        {{ diffBadge(row.equity, PREV_SNAPSHOT.products.find(p => p.id === row.id)!.equity) }}
                      </span>
                    </template>
                  </td>
                  <!-- 权益细分: 红利/港股/其他/REITS -->
                  <td v-for="k in (['红利','港股','其他权益','REITS'] as const)" :key="k"
                      class="px-1.5 py-2.5 text-center text-[13px] text-[#94A3B8]">
                    {{ guidanceCalculated ? row.equitySub[k] + '%' : '—' }}
                    <template v-if="guidanceCalculated && showHistoryDiff">
                      <span v-if="diffBadge(row.equitySub[k], PREV_SNAPSHOT.products.find(p => p.id === row.id)!.equitySub[k])"
                            class="block text-[10px] font-mono font-bold"
                            :class="(row.equitySub[k] - PREV_SNAPSHOT.products.find(p => p.id === row.id)!.equitySub[k]) > 0 ? 'text-[#F04864]' : 'text-[#00C9A7]'">
                        {{ diffBadge(row.equitySub[k], PREV_SNAPSHOT.products.find(p => p.id === row.id)!.equitySub[k]) }}
                      </span>
                    </template>
                  </td>
                  <!-- 另类 -->
                  <td class="px-2 py-2.5 text-center border-r border-[#2E3348]">
                    <template v-if="!isReadOnly && guidanceCalculated">
                      <input type="number" min="0" max="100" v-model.number="row.alt"
                        class="w-14 bg-[#1A1E2B] border border-[#FFAB00]/20 rounded text-[13px] font-mono text-center text-[#FFAB00] px-1 py-1 focus:outline-none focus:border-[#FFAB00]/50 transition-colors"/>
                    </template>
                    <template v-else>
                      <span class="font-mono text-[13px]"
                            :class="guidanceCalculated ? 'text-[#FFAB00]' : 'text-[#2E3348]'">
                        {{ guidanceCalculated ? row.alt + '%' : '—' }}
                      </span>
                    </template>
                    <template v-if="guidanceCalculated && showHistoryDiff">
                      <span v-if="diffBadge(row.alt, PREV_SNAPSHOT.products.find(p => p.id === row.id)!.alt)"
                            class="block text-[10px] font-mono font-bold mt-0.5"
                            :class="(row.alt - PREV_SNAPSHOT.products.find(p => p.id === row.id)!.alt) > 0 ? 'text-[#F04864]' : 'text-[#00C9A7]'">
                        {{ diffBadge(row.alt, PREV_SNAPSHOT.products.find(p => p.id === row.id)!.alt) }}
                      </span>
                    </template>
                  </td>
                  <!-- 流动性 -->
                  <td class="px-1.5 py-2.5 text-center">
                    <span class="font-mono text-[13px]"
                          :class="guidanceCalculated ? 'text-[#94A3B8]' : 'text-[#2E3348]'">
                      {{ guidanceCalculated ? row.liquidity + '%' : '—' }}
                    </span>
                    <template v-if="guidanceCalculated && showHistoryDiff">
                      <span v-if="diffBadge(row.liquidity, PREV_SNAPSHOT.products.find(p => p.id === row.id)!.liquidity)"
                            class="block text-[10px] font-mono font-bold mt-0.5"
                            :class="(row.liquidity - PREV_SNAPSHOT.products.find(p => p.id === row.id)!.liquidity) > 0 ? 'text-[#F04864]' : 'text-[#00C9A7]'">
                        {{ diffBadge(row.liquidity, PREV_SNAPSHOT.products.find(p => p.id === row.id)!.liquidity) }}
                      </span>
                    </template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="px-5 py-2 border-t border-[#252A3A] bg-[#161922] text-[11px] font-mono text-[#4A5568]">
            合计允许范围 95–105%（四舍五入容差）· 权益细分按产品系数自动计算 · 另类/流动性初值取自上期比例
          </div>
          <!-- ══ 折叠触发器：历史对比 ══ -->
          <button @click="showHistoryDiff = !showHistoryDiff" class="w-full px-5 py-2.5 border-t border-[#2E3348] bg-[#1A1E2B] text-[13px] font-mono text-[#94A3B8] hover:text-[#3B9EFF] hover:bg-[#1A1E2B]/80 transition-colors flex items-center justify-center gap-2">
            <ArrowRight class="w-3 h-3 transition-transform duration-200" :class="showHistoryDiff ? 'rotate-90' : ''" />
            <span>{{ showHistoryDiff ? '收起' : '点击展开' }}与上期 (2025 Q4) 配置指引对比</span>
          </button>
          <!-- ══ 历史对比报表 ══ -->
          <div v-if="showHistoryDiff" class="border-t border-[#2E3348]">
            <div class="px-5 py-2 bg-[#161922] border-b border-[#2E3348]">
              <div class="flex items-center gap-2">
                <div class="w-1.5 h-4 rounded-full bg-[#64748B]"></div>
                <span class="text-[13px] font-bold text-[#64748B]">上期快照 · 2025 Q4</span>
                <span class="text-[11px] font-mono text-[#4A5568]">固收{{ PREV_SNAPSHOT.bondGrade }}（{{ PREV_SNAPSHOT.bondDuration }}）· 权益{{ PREV_SNAPSHOT.equityLabel }}</span>
              </div>
            </div>
            <div class="overflow-x-auto">
              <table class="table-fixed w-full border-collapse font-mono text-[13px] opacity-70">
                <thead class="bg-[#161922] border-b border-[#2E3348]">
                  <tr>
                    <th class="px-3 py-2 text-left text-[11px] text-[#64748B] border-r border-[#2E3348]" style="width:90px">产品类型</th>
                    <th class="px-2 py-2 text-center text-[11px] text-[#22D3EE]/40 border-r border-[#2E3348]" style="width:130px">久期指引</th>
                    <th class="px-2 py-2 text-center text-[11px] text-[#3B9EFF]/40 border-r border-[#2E3348]" style="width:80px">总权益</th>
                    <th class="px-1.5 py-2 text-center text-[11px] text-[#3B9EFF]/40">红利</th>
                    <th class="px-1.5 py-2 text-center text-[11px] text-[#3B9EFF]/40">港股</th>
                    <th class="px-1.5 py-2 text-center text-[11px] text-[#3B9EFF]/40">其他</th>
                    <th class="px-1.5 py-2 text-center text-[11px] text-[#3B9EFF]/40 border-r border-[#2E3348]">REITS</th>
                    <th class="px-2 py-2 text-center text-[11px] text-[#FFAB00]/40 border-r border-[#2E3348]" style="width:110px">另类</th>
                    <th class="px-1.5 py-2 text-center text-[11px] text-[#94A3B8]/40" style="width:55px">流动性</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#252A3A]/50">
                  <tr v-for="p in PREV_SNAPSHOT.products" :key="p.id" class="hover:bg-[#161922]/60">
                    <td class="px-3 py-2 border-r border-[#2E3348]">
                      <span class="text-[13px] text-[#64748B]">{{ p.name }}</span>
                    </td>
                    <td class="px-2 py-2 text-center text-[11px] text-[#22D3EE]/50 border-r border-[#2E3348]">
                      {{ BOND_GRADE_LABEL[PREV_SNAPSHOT.perProductBondGrade[p.id]] }}
                    </td>
                    <td class="px-2 py-2 text-center text-[#3B9EFF]/50 border-r border-[#2E3348]">{{ p.equity }}%</td>
                    <td class="px-1.5 py-2 text-center text-[#94A3B8]/40">{{ p.equitySub['红利'] }}%</td>
                    <td class="px-1.5 py-2 text-center text-[#94A3B8]/40">{{ p.equitySub['港股'] }}%</td>
                    <td class="px-1.5 py-2 text-center text-[#94A3B8]/40">{{ p.equitySub['其他权益'] }}%</td>
                    <td class="px-1.5 py-2 text-center text-[#94A3B8]/40 border-r border-[#2E3348]">{{ p.equitySub['REITS'] }}%</td>
                    <td class="px-2 py-2 text-center text-[#FFAB00]/40 border-r border-[#2E3348]">{{ p.altText }}</td>
                    <td class="px-1.5 py-2 text-center text-[#94A3B8]/40">{{ p.liquidity }}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ══ 校验 Toast ══ -->
        <Transition enter-active-class="transition-all duration-300" enter-from-class="opacity-0 -translate-y-2" leave-active-class="transition-all duration-200" leave-to-class="opacity-0 -translate-y-2">
          <div v-if="showValidationToast && validationErrors.length > 0"
            class="bg-[#1A0A0E] border border-[#F04864]/40 rounded-xl px-5 py-4 space-y-2">
            <div class="flex items-center gap-2 mb-1">
              <Warning class="w-4 h-4 text-[#F04864] shrink-0" />
              <span class="text-[13px] font-bold text-[#F04864] uppercase tracking-widest">校验失败 · 无法提交</span>
            </div>
            <div v-for="(err, i) in validationErrors" :key="i" class="flex items-start gap-2">
              <span class="text-[#F04864] font-mono text-[11px] mt-0.5 shrink-0">›</span>
              <span class="text-[13px] font-mono text-[#F04864]/80">{{ err }}</span>
            </div>
          </div>
        </Transition>

        <!-- ══ 提交区 ══ -->
        <div v-if="!decisionSubmitted" class="bg-[#202431] border border-[#252A3A] rounded-xl p-5 space-y-4">
          <div class="flex items-start gap-3">
            <div class="mt-0.5 shrink-0">
              <div v-if="validationErrors.length === 0 && guidanceCalculated" class="w-2 h-2 rounded-full bg-[#00C9A7] mt-1"></div>
              <div v-else class="w-2 h-2 rounded-full bg-[#F04864] mt-1"></div>
            </div>
            <div class="flex-1 space-y-1 text-xs font-mono text-[#64748B]">
              <div :class="equityMixSum === 100 ? 'text-[#00C9A7]' : 'text-[#F04864]'">
                {{ equityMixSum === 100 ? '✓' : '✗' }} 权益明细之和 {{ equityMixSum }}% {{ equityMixSum === 100 ? '（通过）' : '（须为 100%）' }}
              </div>
              <div :class="guidanceCalculated ? 'text-[#00C9A7]' : 'text-[#6B7280]'">
                {{ guidanceCalculated ? '✓' : '○' }} 产品指引已计算 {{ guidanceCalculated ? '（通过）' : '（待点击「计算产品指引」）' }}
              </div>
              <div v-for="row in productGuidances" :key="row.id"
                   :class="guidanceCalculated ? (Math.abs(row.bond + row.equity + row.alt + row.liquidity - 100) <= 5 ? 'text-[#00C9A7]' : 'text-[#F04864]') : 'text-[#6B7280]'">
                <template v-if="guidanceCalculated">
                  {{ Math.abs(row.bond + row.equity + row.alt + row.liquidity - 100) <= 5 ? '✓' : '✗' }}
                  【{{ row.name }}】合计 {{ row.bond + row.equity + row.alt + row.liquidity }}%
                  {{ Math.abs(row.bond + row.equity + row.alt + row.liquidity - 100) <= 5 ? '（通过）' : '（超出容差）' }}
                </template>
                <template v-else>○ 【{{ row.name }}】待计算</template>
              </div>
            </div>
          </div>
          <button @click="handleSubmitDecision"
            :disabled="!canSubmitDecision"
            :class="cn('w-full py-3.5 rounded-xl font-bold text-[15px] tracking-widest transition-all duration-300 flex items-center justify-center gap-2 border',
              canSubmitDecision
                ? 'bg-[#FFAB00]/12 border-[#FFAB00]/35 text-[#FFAB00] hover:bg-[#FFAB00]/20 hover:border-[#FFAB00]/55'
                : 'bg-[#1A1E2B] border-[#2E3348] text-[#4A5568] cursor-not-allowed')"
          >
            <DocumentChecked class="w-4 h-4 shrink-0" />
            正式提交 · 生成决议并同步部门资配指引
          </button>
        </div>

        <!-- ══ 提交成功状态 ══ -->
        <div v-else class="bg-[#0A1A10] border border-[#00C9A7]/30 rounded-xl p-5 space-y-3">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-full bg-[#00C9A7]/15 border border-[#00C9A7]/30 flex items-center justify-center shrink-0">
              <Check class="w-4 h-4 text-[#00C9A7]" />
            </div>
            <div>
              <div class="text-[15px] font-bold text-[#00C9A7]">决议已正式提交</div>
              <div class="text-xs font-mono text-[#94A3B8] mt-0.5">会议状态 → 已结束 · 部门资配决策已同步至 demoStore</div>
            </div>
          </div>
          <pre class="text-xs font-mono text-[#B4BAC9] bg-[#1A1E2B] border border-[#252A3A] rounded-lg p-3.5 whitespace-pre-wrap leading-relaxed overflow-x-auto">{{ JSON.stringify(deptAllocationDecision, null, 2) }}</pre>
        </div>

        <!-- ══ Monte Carlo 入口 ══ -->
        <div
          @click="showSAASandbox = true"
          class="relative group cursor-pointer overflow-hidden rounded-xl border border-cyan-500/25 bg-gradient-to-r from-[#06101A] via-[#1A1E2B] to-[#080C14] px-6 py-4 hover:border-cyan-400/50 transition-all duration-300 shadow-[0_0_30px_rgba(6,182,212,0.06)] hover:shadow-[0_0_50px_rgba(6,182,212,0.15)]"
        >
          <div class="absolute inset-0 bg-gradient-to-r from-cyan-500/[0.04] via-transparent to-purple-500/[0.04] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          <div class="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-400/60 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out" />
          <div class="relative flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-cyan-500/15 to-purple-500/15 border border-cyan-500/25 flex items-center justify-center shadow-[0_0_16px_rgba(6,182,212,0.15)] group-hover:shadow-[0_0_32px_rgba(6,182,212,0.3)] transition-shadow duration-300">
                <DataAnalysis class="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <div class="flex items-center space-x-3">
                  <span class="text-[15px] font-bold text-white tracking-wide">前瞻性蒙特卡洛压力测试</span>
                  <span class="text-[11px] font-mono text-cyan-400/70 bg-cyan-400/10 px-2 py-1 rounded-full border border-cyan-400/15 uppercase tracking-wider">Monte Carlo</span>
                </div>
                <p class="text-[13px] text-[#94A3B8] mt-0.5 font-mono">基于当前指引决议进行前瞻性压力测试与收益预测</p>
              </div>
            </div>
            <div class="flex items-center space-x-2 text-cyan-400 group-hover:translate-x-1 transition-transform duration-200 shrink-0 ml-6">
              <span class="text-[14px] font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200">进入沙盘</span>
              <ArrowRight class="w-4 h-4" />
            </div>
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════════════
           STEP 4: 会后 · AI纪要与签发
      ════════════════════════════════════════════════════════════ -->
      <div v-if="step === 4" class="space-y-4 pb-4">

        <!-- ══ S3 完成守卫 ══ -->
        <div v-if="!decisionSubmitted" class="bg-[#1A0E08] border border-[#FFAB00]/30 rounded-xl p-5">
          <div class="flex items-center gap-3">
            <Warning class="w-5 h-5 text-[#FFAB00] shrink-0" />
            <div>
              <div class="text-[15px] font-bold text-[#FFAB00]">S3 决议尚未提交</div>
              <div class="text-[13px] font-mono text-[#94A3B8] mt-1">请先返回 Step 3，由主任委员完成决策并正式提交后，方可签发会议纪要。</div>
            </div>
          </div>
        </div>

        <!-- ══ 录音状态守卫 ══ -->
        <div class="bg-[#202431] border border-[#252A3A] rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#252A3A] to-[#202431] border-b border-[#252A3A] px-5 py-3.5 flex items-center justify-between">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>全局录音状态</h3>
            <div class="flex items-center gap-2">
              <div v-if="recState === 'recording'" class="flex items-center gap-1.5">
                <div class="w-2 h-2 rounded-full bg-[#FF3B30] animate-pulse"></div>
                <span class="text-[13px] font-mono text-[#FF3B30]">录音中 {{ recTimeDisplay }}</span>
              </div>
              <div v-else-if="recState === 'paused'" class="flex items-center gap-1.5">
                <div class="flex items-center gap-[2px]"><div class="w-[3px] h-3 rounded-sm bg-[#FFAB00]"></div><div class="w-[3px] h-3 rounded-sm bg-[#FFAB00]"></div></div>
                <span class="text-[13px] font-mono text-[#FFAB00]">已暂停 · {{ recTimeDisplay }}</span>
              </div>
              <div v-else-if="recState === 'finished'" class="flex items-center gap-1.5">
                <div class="w-2 h-2 rounded-full bg-[#22D3EE]"></div>
                <span class="text-[13px] font-mono text-[#22D3EE]">录音已结束 · {{ recTimeDisplay }}</span>
              </div>
              <div v-else class="flex items-center gap-1.5">
                <div class="w-2 h-2 rounded-full bg-[#4A5568]"></div>
                <span class="text-[13px] font-mono text-[#6B7280]">未开始</span>
              </div>
            </div>
          </div>
          <div v-if="recState !== 'finished'" class="p-5 flex items-center gap-3">
            <Warning class="w-4 h-4 text-[#FFAB00] shrink-0" />
            <span class="text-[13px] text-[#FFAB00]">请先在顶部全局控制栏结束录音，再生成 AI 纪要</span>
          </div>
          <div v-else class="p-5 flex items-center gap-3">
            <Check class="w-4 h-4 text-[#00C9A7] shrink-0" />
            <span class="text-[13px] text-[#00C9A7]">录音已完成，可生成 AI 纪要</span>
          </div>
        </div>

        <!-- ══ AI Minutes Generation (录音守卫) ══ -->
        <div v-if="recState === 'finished'" class="bg-[#202431] border border-[#3B9EFF]/20 rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#3B9EFF]/10 to-[#202431] border-b border-[#3B9EFF]/15 px-5 py-3.5 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <h3 class="am-title-l2"><div class="am-title-bar"></div>AI 会议纪要</h3>
              <div v-if="aiMinutesLoading" class="flex items-center gap-1.5">
                <div class="w-1.5 h-1.5 rounded-full bg-[#3B9EFF] animate-pulse"></div>
                <span class="text-[13px] font-mono text-[#3B9EFF]">AI 正在处理...</span>
              </div>
            </div>
            <button v-if="!aiMinutesReady && !aiMinutesLoading" @click="generateAIMinutes" class="text-[13px] text-[#3B9EFF] bg-[#3B9EFF]/10 border border-[#3B9EFF]/25 hover:bg-[#3B9EFF]/18 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5">
              <Cpu class="w-3 h-3" /> 生成 AI 纪要
            </button>
          </div>
          <div v-if="aiMinutesLoading" class="p-6 space-y-4">
            <div class="flex items-center gap-3">
              <Loading class="w-5 h-5 text-[#3B9EFF] animate-spin" />
              <span class="text-[15px] text-[#94A3B8]">AI 正在分析投票数据、识别争论焦点、生成结构化纪要...</span>
            </div>
            <div class="space-y-3">
              <div class="h-4 bg-[#1A1E2B] rounded animate-pulse w-3/4"></div>
              <div class="h-4 bg-[#1A1E2B] rounded animate-pulse w-1/2"></div>
              <div class="h-4 bg-[#1A1E2B] rounded animate-pulse w-2/3"></div>
              <div class="h-px bg-[#252A3A] my-2"></div>
              <div class="h-4 bg-[#1A1E2B] rounded animate-pulse w-5/6"></div>
              <div class="h-4 bg-[#1A1E2B] rounded animate-pulse w-3/5"></div>
              <div class="h-4 bg-[#1A1E2B] rounded animate-pulse w-4/5"></div>
            </div>
          </div>
          <div v-if="aiMinutesReady" class="p-6">
            <pre class="whitespace-pre-wrap text-[14px] font-mono text-[#B4BAC9] leading-relaxed bg-[#1A1E2B] border border-[#252A3A] rounded-lg p-5">{{ aiMinutesContent }}</pre>
          </div>
          <div v-if="!aiMinutesReady && !aiMinutesLoading" class="p-6 text-center">
            <p class="text-[13px] text-[#64748B]">点击上方按钮，AI 将基于投票矩阵和配置指引自动生成结构化会议纪要</p>
          </div>
        </div>

        <!-- ══ 签发人选择 + 正式签发 ══ -->
        <div v-if="recState === 'finished' && aiMinutesReady" class="bg-[#202431] border border-[#00C9A7]/20 rounded-xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#00C9A7]/10 to-[#202431] border-b border-[#00C9A7]/15 px-5 py-3.5">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-[#00C9A7]/15 border border-[#00C9A7]/30 flex items-center justify-center">
                <DocumentChecked class="w-4 h-4 text-[#00C9A7]" />
              </div>
              <div>
                <h3 class="text-[15px] font-bold text-[#00C9A7]">正式签发</h3>
                <p class="text-[13px] font-mono text-[#94A3B8] mt-0.5">选择签发人后确认签发</p>
              </div>
            </div>
          </div>
          <div class="p-5 space-y-4">
            <div class="flex items-center gap-4">
              <span class="text-[13px] text-[#94A3B8] shrink-0">签发人</span>
              <select v-model="signerId" :disabled="isIssued"
                class="bg-[#1A1E2B] border border-[#2E3348] text-[13px] font-mono rounded px-3 py-2 text-[#E8ECF4] focus:border-[#00C9A7] focus:outline-none transition-colors flex-1 max-w-[240px] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option v-for="m in MEMBERS_DATA" :key="m.id" :value="m.id">{{ m.name }}（{{ m.role }}）</option>
              </select>
              <span class="text-xs font-mono text-[#64748B]">{{ signerName }}</span>
            </div>
            <button
              @click="handleIssue"
              :disabled="isIssued || issuingLoading || !decisionSubmitted"
              :class="cn('w-full py-3.5 rounded-xl font-bold text-[15px] tracking-widest transition-all duration-300 flex items-center justify-center gap-2 border',
                isIssued ? 'bg-[#00C9A7]/10 border-[#00C9A7]/30 text-[#00C9A7] cursor-not-allowed' :
                issuingLoading ? 'bg-[#3B9EFF]/10 border-[#3B9EFF]/30 text-[#3B9EFF] cursor-wait' :
                'bg-[#00C9A7]/15 border-[#00C9A7]/30 text-[#00C9A7] hover:bg-[#00C9A7]/25')"
            >
              <DocumentChecked v-if="!issuingLoading" class="w-5 h-5 shrink-0" />
              <Loading v-else class="w-5 h-5 shrink-0 animate-spin" />
              <span>{{ isIssued ? `已签发 · ${signerName} · ${issuedTime}` : issuingLoading ? '正在签发...' : '正式签发并全系统下达' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ BOTTOM NAV ═══ -->
    <div class="shrink-0 flex justify-end items-center pt-1">
      <button v-if="step < 4" @click="goNextStep" class="px-6 py-2 rounded-lg bg-[#3B9EFF]/10 border border-[#3B9EFF]/25 text-[14px] text-[#3B9EFF] hover:bg-[#3B9EFF]/18 hover:border-[#3B9EFF]/45 transition-all duration-200 flex items-center space-x-2">
        <span>确认</span><Check class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- ═══ SAA SANDBOX ═══ -->
    <Teleport to="body">
      <Transition enter-active-class="transition-all duration-300 ease-out" enter-from-class="opacity-0 scale-[0.97]" enter-to-class="opacity-100 scale-100" leave-active-class="transition-all duration-200 ease-in" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-[0.97]">
        <div v-if="showSAASandbox" class="fixed inset-0 z-[9999] bg-[#161922]">
          <SAASimulator embedded @close="showSAASandbox = false" />
        </div>
      </Transition>
    </Teleport>

    <!-- ═══ MEETING MANAGEMENT DRAWER (秘书专属) ═══ -->
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition-transform duration-200 ease-in"
      leave-from-class="translate-x-0"
      leave-to-class="translate-x-full"
    >
      <div v-if="showMeetingDrawer" class="fixed inset-y-0 right-0 z-[9000] w-[520px] max-w-[90vw] bg-[#161922] border-l border-[#2E3348] shadow-[-8px_0_30px_rgba(0,0,0,0.5)] flex flex-col">
        <!-- Drawer Header -->
        <div class="shrink-0 px-5 py-4 border-b border-[#2E3348] flex items-center justify-between bg-gradient-to-r from-[#202431] to-[#161922]">
          <div class="flex items-center gap-2">
            <div class="am-title-bar"></div>
            <span class="text-[15px] font-bold text-[#E8ECF4]">会议管理</span>
            <span class="text-xs font-mono text-[#64748B] bg-[#1A1E2B] px-2 py-1 rounded border border-[#252A3A]">CRUD</span>
          </div>
          <button @click="showMeetingDrawer = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-1">
            <Close class="w-4 h-4" />
          </button>
        </div>

        <!-- Drawer Toolbar -->
        <div class="shrink-0 px-5 py-3 border-b border-[#252A3A] flex items-center justify-between bg-[#1A1E2B]">
          <span class="text-xs font-mono text-[#64748B]">共 {{ meetingList.length }} 条记录</span>
          <button @click="quickCreateMeeting" class="flex items-center gap-1.5 text-[13px] px-3 py-1.5 rounded-lg border border-[#3B9EFF]/25 bg-[#3B9EFF]/10 text-[#3B9EFF] hover:bg-[#3B9EFF]/18 transition-colors">
            <Document class="w-3 h-3" /> 新增会议
          </button>
        </div>

        <!-- Drawer Body -->
        <div class="flex-1 overflow-y-auto no-scrollbar">
          <div class="divide-y divide-[#252A3A]">
            <div
              v-for="m in meetingList"
              :key="m.id"
              class="px-5 py-4 hover:bg-[#1A1E2B]/50 transition-colors"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-[14px] font-semibold text-[#E8ECF4] truncate">{{ m.name }}</span>
                    <span :class="cn('text-[11px] font-mono px-1.5 py-1 rounded border',
                      m.status === '已结束' ? 'bg-[#94A3B8]/10 border-[#94A3B8]/25 text-[#94A3B8]' :
                      m.status === '进行中' ? 'bg-[#00C9A7]/10 border-[#00C9A7]/25 text-[#00C9A7]' :
                      'bg-[#3B9EFF]/10 border-[#3B9EFF]/25 text-[#3B9EFF]')">{{ m.status }}</span>
                  </div>
                  <div class="flex items-center gap-3 text-xs font-mono text-[#64748B]">
                    <span>{{ m.date }}</span>
                    <span>{{ m.time }}</span>
                    <span>{{ m.location }}</span>
                  </div>
                  <div v-if="m.decision" class="text-xs text-[#94A3B8] mt-1 truncate">{{ m.decision }}</div>
                </div>
                <div class="flex items-center gap-1 shrink-0 ml-3">
                  <button @click="openEditMeeting(m.id)" class="text-xs px-2 py-1 rounded border border-[#252A3A] text-[#94A3B8] hover:border-[#FFAB00]/30 hover:text-[#FFAB00] transition-colors flex items-center gap-1">
                    <Edit class="w-3 h-3" /> 编辑
                  </button>
                  <button @click="deleteMeeting(m.id)" class="text-xs px-2 py-1 rounded border border-[#252A3A] text-[#94A3B8] hover:border-[#F04864]/30 hover:text-[#F04864] transition-colors flex items-center gap-1">
                    <Close class="w-3 h-3" /> 删除
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="meetingList.length === 0" class="py-16 text-center">
            <p class="text-[13px] text-[#4A5568]">暂无会议记录</p>
          </div>
        </div>

        <!-- Drawer Footer -->
        <div class="shrink-0 px-5 py-3 border-t border-[#2E3348] bg-[#1A1E2B]">
          <div class="flex items-center justify-between text-[11px] font-mono text-[#4A5568]">
            <span>模拟数据 · 仅前端 CRUD 演示</span>
            <span>最后更新: {{ new Date().toLocaleDateString('zh-CN') }}</span>
          </div>
        </div>
      </div>
    </Transition>
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showMeetingDrawer" class="fixed inset-0 z-[8999] bg-black/40 backdrop-blur-sm" @click="showMeetingDrawer = false"></div>
    </Transition>

      <!-- ═══ EDIT MEETING DRAWER ═══ -->
      <Transition
        enter-active-class="transition-transform duration-300 ease-out"
        enter-from-class="translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transition-transform duration-200 ease-in"
        leave-from-class="translate-x-0"
        leave-to-class="translate-x-full"
      >
        <div v-if="showEditMeetingDrawer" class="fixed inset-y-0 right-0 z-[9150] w-[640px] max-w-[95vw] bg-[#161922] border-l border-[#2E3348] shadow-[-10px_0_40px_rgba(0,0,0,0.65)] flex flex-col">
          <!-- Drawer Header -->
          <div class="shrink-0 px-6 py-4 border-b border-[#2E3348] flex items-center justify-between bg-gradient-to-r from-[#202431] to-[#161922]">
            <div class="flex items-center gap-2.5 min-w-0">
              <div class="am-title-bar" style="background:#FFAB00; flex-shrink:0"></div>
              <span class="text-[15px] font-bold text-[#E8ECF4] shrink-0">编辑会议</span>
              <span class="text-xs font-mono text-[#FFAB00] bg-[#FFAB00]/10 border border-[#FFAB00]/20 px-1.5 py-1 rounded truncate">{{ editingMeetingTitle }}</span>
            </div>
            <button @click="showEditMeetingDrawer = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-1 shrink-0 ml-2">
              <Close class="w-4 h-4" />
            </button>
          </div>
          <!-- Drawer Body -->
          <div class="flex-1 overflow-y-auto no-scrollbar">
            <!-- ── 基础属性 ── -->
            <div class="px-6 py-5 border-b border-[#252A3A] space-y-4">
              <div class="text-xs font-mono text-[#3B9EFF] uppercase tracking-wider">基础属性</div>
              <!-- 会议属性 -->
              <div>
                <label class="text-xs font-mono text-[#94A3B8] block mb-2">会议属性</label>
                <div class="flex gap-2 flex-wrap">
                  <button v-for="t in MEETING_TYPES" :key="t"
                    @click="editingMeetingForm.meetingType = t; editingMeetingForm.meetingPeriod = PERIOD_OPTIONS[t][0]"
                    :class="cn('px-3.5 py-1 text-[14px] rounded-lg border transition-all',
                      editingMeetingForm.meetingType === t
                        ? 'bg-[#3B9EFF]/15 border-[#3B9EFF]/40 text-[#3B9EFF]'
                        : 'bg-[#1A1E2B] border-[#252A3A] text-[#6B7280] hover:text-[#94A3B8]')"
                  >{{ t }}</button>
                </div>
              </div>
              <!-- 期次 -->
              <div>
                <label class="text-xs font-mono text-[#94A3B8] block mb-2">期次</label>
                <div class="flex flex-wrap gap-2">
                  <button v-for="p in editingMeetingPeriodOptions" :key="p"
                    @click="editingMeetingForm.meetingPeriod = p"
                    :class="cn('px-3 py-1 text-[14px] rounded border font-mono transition-all',
                      editingMeetingForm.meetingPeriod === p
                        ? 'bg-[#FFAB00]/15 border-[#FFAB00]/40 text-[#FFAB00]'
                        : 'bg-[#1A1E2B] border-[#252A3A] text-[#6B7280] hover:text-[#94A3B8]')"
                  >{{ p }}</button>
                </div>
              </div>
              <!-- 年份 -->
              <div>
                <label class="text-xs font-mono text-[#94A3B8] block mb-2">年份</label>
                <div class="flex gap-2">
                  <button v-for="y in [2024,2025,2026,2027]" :key="y"
                    @click="editingMeetingForm.meetingYear = y"
                    :class="cn('px-3 py-1 text-[14px] rounded border font-mono transition-all',
                      editingMeetingForm.meetingYear === y
                        ? 'bg-[#3B9EFF]/15 border-[#3B9EFF]/40 text-[#3B9EFF]'
                        : 'bg-[#1A1E2B] border-[#252A3A] text-[#6B7280] hover:text-[#94A3B8]')"
                  >{{ y }}</button>
                </div>
              </div>
              <!-- 标题预览 -->
              <div class="bg-[#1A1E2B] border border-[#FFAB00]/15 rounded-lg px-4 py-2.5">
                <span class="text-[11px] font-mono text-[#FFAB00] mr-2">标题预览</span>
                <span class="text-[14px] font-bold text-[#E8ECF4]">{{ editingMeetingTitle }}</span>
              </div>
              <!-- 日期 时间 地点 -->
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="text-xs font-mono text-[#94A3B8] block mb-1.5">日期</label>
                  <input type="date" v-model="editingMeetingForm.date" style="color-scheme:dark"
                    class="w-full bg-[#1A1E2B] border border-[#2E3348] rounded-lg px-3 py-1.5 text-[14px] text-[#E8ECF4] font-mono focus:border-[#3B9EFF] focus:outline-none transition-colors"
                  />
                </div>
                <div>
                  <label class="text-xs font-mono text-[#94A3B8] block mb-1.5">时间</label>
                  <input type="text" v-model="editingMeetingForm.time"
                    class="w-full bg-[#1A1E2B] border border-[#2E3348] rounded-lg px-3 py-1.5 text-[14px] text-[#E8ECF4] font-mono focus:border-[#3B9EFF] focus:outline-none transition-colors"
                  />
                </div>
              </div>
              <div>
                <label class="text-xs font-mono text-[#94A3B8] block mb-1.5">地点</label>
                <input type="text" v-model="editingMeetingForm.location"
                  class="w-full bg-[#1A1E2B] border border-[#2E3348] rounded-lg px-3 py-1.5 text-[14px] text-[#E8ECF4] font-mono focus:border-[#3B9EFF] focus:outline-none transition-colors"
                />
              </div>
              <!-- 状态 -->
              <div>
                <label class="text-xs font-mono text-[#94A3B8] block mb-2">状态</label>
                <div class="flex gap-2">
                  <button v-for="s in MEETING_STATUS_LIST" :key="s"
                    @click="editingMeetingForm.status = s"
                    :class="cn('px-3 py-1 text-[14px] rounded border transition-all',
                      editingMeetingForm.status === s
                        ? s === '进行中' ? 'bg-[#00C9A7]/15 border-[#00C9A7]/40 text-[#00C9A7]'
                          : s === '已结束' ? 'bg-[#94A3B8]/15 border-[#94A3B8]/40 text-[#94A3B8]'
                          : s === '已取消' ? 'bg-[#F04864]/15 border-[#F04864]/40 text-[#F04864]'
                          : 'bg-[#3B9EFF]/15 border-[#3B9EFF]/40 text-[#3B9EFF]'
                        : 'bg-[#1A1E2B] border-[#252A3A] text-[#6B7280] hover:text-[#94A3B8]')"
                  >{{ s }}</button>
                </div>
              </div>
            </div>

            <!-- ── 投票截止控制 ── -->
            <div class="px-6 py-5 border-b border-[#252A3A] space-y-4">
              <div class="text-xs font-mono text-[#FFAB00] uppercase tracking-wider">投票截止控制</div>
              <div>
                <label class="text-xs font-mono text-[#94A3B8] block mb-1.5">截止时间</label>
                <input type="datetime-local" v-model="editingMeetingForm.voteDeadline" style="color-scheme:dark"
                  class="w-full bg-[#1A1E2B] border border-[#2E3348] rounded-lg px-3 py-1.5 text-[14px] text-[#E8ECF4] font-mono focus:border-[#FFAB00] focus:outline-none transition-colors"
                />
              </div>
              <label class="flex items-center gap-3 cursor-pointer group">
                <div
                  @click="editingMeetingForm.voteForcedClosed = !editingMeetingForm.voteForcedClosed"
                  :class="cn('w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-all',
                    editingMeetingForm.voteForcedClosed
                      ? 'bg-[#F04864] border-[#F04864]'
                      : 'border-[#2E3348] group-hover:border-[#F04864]/40')"
                >
                  <Check v-if="editingMeetingForm.voteForcedClosed" class="w-2.5 h-2.5 text-white" />
                </div>
                <span :class="cn('text-[14px]', editingMeetingForm.voteForcedClosed ? 'text-[#F04864]' : 'text-[#94A3B8]')">
                  强制截止（无论截止时间，立即锁定委员端）
                </span>
              </label>
            </div>

            <!-- ── 会前材料链接 ── -->
            <div class="px-6 py-5 border-b border-[#252A3A] space-y-3">
              <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider">会前材料链接</div>
              <textarea v-model="editingMeetingForm.preMaterials" rows="5"
                placeholder="每行粘贴一条文档/研报链接&#10;https://confluence.example.com/..."
                class="w-full bg-[#1A1E2B] border border-[#2E3348] rounded-xl px-4 py-3 text-[14px] text-[#B4BAC9] font-mono focus:border-[#3B9EFF] focus:outline-none resize-none placeholder-[#3A4555] leading-relaxed"
              ></textarea>
              <p class="text-[11px] font-mono text-[#4A5568]">材料链接将在会前通知邮件中自动附带</p>
            </div>

            <!-- ── 会议纪要模板 ── -->
            <div class="px-6 py-5 space-y-3">
              <div class="text-xs font-mono text-[#94A3B8] uppercase tracking-wider">会议初步纪要模板</div>
              <textarea v-model="editingMeetingForm.minutesTemplate" rows="12"
                placeholder="在此输入纪要结构模板..."
                class="w-full bg-[#1A1E2B] border border-[#2E3348] rounded-xl px-4 py-3 text-[14px] text-[#B4BAC9] font-mono focus:border-[#3B9EFF] focus:outline-none resize-none placeholder-[#3A4555] leading-relaxed"
              ></textarea>
              <p class="text-[11px] font-mono text-[#4A5568]">此模板将在 AI 纪要生成时作为结构参考</p>
            </div>
          </div>
          <!-- Drawer Footer -->
          <div class="shrink-0 px-6 py-4 border-t border-[#2E3348] bg-[#1A1E2B] flex items-center justify-between">
            <button @click="showEditMeetingDrawer = false"
              class="px-4 py-2 text-[14px] text-[#94A3B8] border border-[#2E3348] rounded-lg hover:border-[#3B9EFF]/30 hover:text-[#3B9EFF] transition-colors">
              取消
            </button>
            <button @click="saveEditMeeting"
              class="px-5 py-2 text-[14px] bg-[#FFAB00]/15 border border-[#FFAB00]/40 text-[#FFAB00] rounded-lg hover:bg-[#FFAB00]/25 transition-colors font-bold">
              保存修改
            </button>
          </div>
        </div>
      </Transition>
      <!-- Edit drawer backdrop -->
      <Transition enter-active-class="transition-opacity duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100" leave-active-class="transition-opacity duration-150" leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="showEditMeetingDrawer" class="fixed inset-0 z-[9050] bg-black/40 backdrop-blur-sm" @click="showEditMeetingDrawer = false"></div>
      </Transition>

      <div v-if="showHistoryModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="showHistoryModal = false">
        <div class="bg-[#202431] border border-[#2E3348] rounded-lg shadow-2xl w-[700px] max-h-[80vh] overflow-hidden flex flex-col">
          <div class="px-4 py-3 border-b border-[#2E3348] flex items-center justify-between shrink-0">
            <div class="flex items-center gap-2">
              <div class="am-title-bar"></div>
              <span class="text-[15px] font-semibold text-[#E8ECF4]">历史投票记录</span>
              <span class="text-[13px] font-mono text-[#94A3B8]">近 3 期</span>
            </div>
            <button @click="showHistoryModal = false" class="text-[#94A3B8] hover:text-[#E8ECF4] transition-colors p-0.5">
              <Close class="w-4 h-4" />
            </button>
          </div>
          <div class="flex-1 overflow-y-auto no-scrollbar p-4">
            <table class="w-full border-collapse table-fixed text-[14px]">
              <thead class="sticky top-0 bg-[#202431] z-10">
                <tr class="border-b border-[#2E3348] text-[#94A3B8]">
                  <th class="px-3 py-2 text-left font-medium" style="width:100px">期次</th>
                  <th v-for="asset in ASSET_LIST" :key="asset" class="px-2 py-2 text-center font-medium">{{ asset }}</th>
                  <th class="px-3 py-2 text-center font-medium" style="width:115px">新高预判</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#252A3A]">
                <tr v-for="row in historicalVotes" :key="row.period" class="hover:bg-[#1A1E2B] transition-colors">
                  <td class="px-3 py-2.5 text-[#E8ECF4] font-mono font-semibold">{{ row.period }}</td>
                  <td v-for="asset in ASSET_LIST" :key="asset" class="px-2 py-2.5 text-center">
                    <span :class="cn('text-[13px] font-mono font-bold px-1.5 py-1 rounded border', SCORE_COLORS[row.scores[asset]] || '')">
                      {{ row.scores[asset] }}
                    </span>
                  </td>
                  <td class="px-3 py-2.5 text-center">
                    <span class="text-[13px] font-mono text-[#00C9A7]">{{ row.newHighs.join(', ') }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="px-4 py-2.5 border-t border-[#2E3348] shrink-0 text-[13px] text-[#64748B] font-mono text-center">
            评分对照: 1-谨慎 · 2-中性偏谨慎 · 3-中性 · 4-中性偏乐观 · 5-乐观
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue';
import {
  UserFilled, ArrowRight, ArrowLeft, ArrowDown, DocumentChecked, DataAnalysis,
  Check, Warning, VideoPlay, VideoPause, Loading, Document, Promotion, Edit,
  Close, Connection, Cpu,
} from '@element-plus/icons-vue';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import SAASimulator from './SAASimulator.vue';
import { http } from '@/api/request';
import {
  activeRole,
  committeeContextError,
  committeeContextLoading,
  committeeDecisionTable,
  committeePageContext,
  deptAllocationDecision,
  fetchCommitteePageData,
  isCommitteeOfflineMock,
  portalSnapshotError,
  portalSnapshotLoading,
} from '@/store/demoStore';

function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

const committeeOfflineMock = computed(() => isCommitteeOfflineMock());

// #region agent log
fetch('http://127.0.0.1:7725/ingest/07ccf41f-a62c-4abe-baa4-4fee7bcfad84',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'68cfc4'},body:JSON.stringify({sessionId:'68cfc4',runId:'run1',hypothesisId:'H1',location:'CommitteeView.vue:1618',message:'CommitteeView script executed',data:{component:'CommitteeView'},timestamp:Date.now()})}).catch(()=>{});
// #endregion

const isCommitteeMember = computed(() =>
  ['班子', '部门长', '投资经理', '混合投资委员会委员'].includes(activeRole.value),
);

/** 右上角个人中心切换角色后驱动投委会页面权限 */
const isSecretary = computed(() => activeRole.value === '混合投资委员会秘书');
const isChairman = computed(() => activeRole.value === '混合投资委员会主任委员');

/**
 * 只读状态：当前角色无编辑权限 或 正在查看已归档会议时为 true。
 */
const currentMeetingId = ref<number | null>(null);
const currentMeeting = computed(() => currentMeetingId.value != null ? meetingList.find(m => m.id === currentMeetingId.value) : null);
const isViewingArchived = computed(() => currentMeeting.value?.status === '已归档' || currentMeeting.value?.status === '已结束');
const isReadOnly = computed(() => !isChairman.value || isViewingArchived.value);

function enterMeeting(id: number) {
  currentMeetingId.value = id;
  step.value = 0;
  stepStatuses.splice(0, 5, 'active', 'pending', 'pending', 'pending', 'pending');
  decisionSubmitted.value = false;
  isIssued.value = false;
  guidanceCalculated.value = false;
}
function backToList() {
  currentMeetingId.value = null;
}

const SCORE_LABELS: Record<number, string> = { 1: '谨慎', 2: '中性偏谨慎', 3: '中性', 4: '中性偏乐观', 5: '乐观' };
// 中国A股市场颜色惯例：红色=上涨/乐观（正面），绿色=下跌/谨慎（负面），蓝色=中性
const SCORE_COLORS: Record<number, string> = {
  1: 'bg-[#00C9A7]/15 border-[#00C9A7]/40 text-[#00C9A7]',   // 谨慎 — 绿（空头/悲观）
  2: 'bg-[#22D3EE]/15 border-[#22D3EE]/40 text-[#22D3EE]',   // 中性偏谨慎 — 青色
  3: 'bg-[#3B9EFF]/15 border-[#3B9EFF]/40 text-[#3B9EFF]',   // 中性 — 蓝
  4: 'bg-[#FFAB00]/15 border-[#FFAB00]/40 text-[#FFAB00]',   // 中性偏乐观 — 琥珀
  5: 'bg-[#F04864]/15 border-[#F04864]/40 text-[#F04864]',   // 乐观 — 红（多头/上涨）
};
const SCORE_INACTIVE = 'bg-[#202431] border-[#2E3348] text-[#6B7280] hover:text-[#94A3B8]';

const ROLE_BADGE_CLASSES: Record<string, string> = {
  '班子': 'bg-[#8B5CF6]/10 border-[#8B5CF6]/25 text-[#8B5CF6]',
  '部门长': 'bg-[#3B9EFF]/10 border-[#3B9EFF]/25 text-[#3B9EFF]',
  '投资经理': 'bg-[#22D3EE]/10 border-[#22D3EE]/25 text-[#22D3EE]',
};

// ── Core state ─────────────────────────────────────────────────
const step = ref(0);
const stepStatuses = reactive<Array<'pending' | 'active' | 'done'>>(['active', 'pending', 'pending', 'pending', 'pending']);

function markStepDone(i: number) {
  stepStatuses[i] = 'done';
  if (i + 1 < 5 && stepStatuses[i + 1] === 'pending') {
    stepStatuses[i + 1] = 'active';
  }
}

watch(step, (newStep) => {
  if (stepStatuses[newStep] === 'pending') {
    stepStatuses[newStep] = 'active';
  }
});

function goNextStep() {
  if (step.value < 4) {
    markStepDone(step.value);
    step.value++;
  }
}

function handleQuickCreateAndEnter() {
  quickCreateMeeting();
  if (meetingList.length > 0) {
    enterMeeting(meetingList[0].id);
  }
}

const STEPS = [
  { label: '筹备与填报' },
  { label: '回顾与复盘' },
  { label: '讨论与量化参考' },
  { label: '决议与配置指引' },
  { label: 'AI纪要与签发' },
];
const STEP_LABELS = ['S0', 'S1', 'S2', 'S3', 'S4'];
const STEP_PHASES = ['会前', '会中', '会中', '会后', '会后'];
const STEP_PHASE_COLORS = ['text-[#22D3EE]', 'text-[#3B9EFF]', 'text-[#3B9EFF]', 'text-[#F1C40F]', 'text-[#34C759]'];

// ── Step 0: Questionnaire config ───────────────────────────────
interface QSection { id: string; title: string; type: string; items: string[]; options: string[]; }
const ASSET_LIST = ['债券', '权益-红利', '权益-成长', '权益-价值', '黄金', '原油'] as const;
const QUESTIONNAIRE_CONFIG: { sections: QSection[] } = {
  sections: [
    { id: 'A', title: '资产评分 (1-5档)', type: 'score', items: [...ASSET_LIST], options: ['1', '2', '3', '4', '5'] },
    { id: 'B', title: '新高预判', type: 'boolean', items: [...ASSET_LIST], options: [] },
    { id: 'C', title: '重点资产', type: 'multi-select', items: ['利率债', '信用债', '可转债', '港股', 'A股大盘', '黄金', 'REITs'], options: [] },
    { id: 'D', title: '核心观点', type: 'textarea', items: ['论据'], options: [] },
  ],
};

interface QuestionAsset {
  id: number;
  name: string;
  type: string;
  enabled: boolean;
}
let qaIdCounter = 7;
const questionAssetList = reactive<QuestionAsset[]>([
  { id: 1, name: '债券', type: '1-5 评分 + 新高预判', enabled: true },
  { id: 2, name: '权益-红利', type: '1-5 评分 + 新高预判', enabled: true },
  { id: 3, name: '权益-成长', type: '1-5 评分 + 新高预判', enabled: true },
  { id: 4, name: '权益-价值', type: '1-5 评分 + 新高预判', enabled: true },
  { id: 5, name: '黄金', type: '1-5 评分 + 新高预判', enabled: true },
  { id: 6, name: '原油', type: '1-5 评分 + 新高预判', enabled: true },
]);

function addQuestionAsset() {
  questionAssetList.push({ id: qaIdCounter++, name: `新资产 #${qaIdCounter - 1}`, type: '1-5 评分', enabled: true });
}

function editQuestionAsset(id: number) {
  const item = questionAssetList.find(q => q.id === id);
  if (item) item.name = item.name + ' (已编辑)';
}

function deleteQuestionAsset(id: number) {
  const idx = questionAssetList.findIndex(q => q.id === id);
  if (idx !== -1) questionAssetList.splice(idx, 1);
}

const FORM_SECTION_A = reactive<Record<string, number>>({ '债券': 3, '权益-红利': 3, '权益-成长': 3, '权益-价值': 3, '黄金': 3, '原油': 3 });
const FORM_SECTION_B = reactive<Record<string, boolean>>({ '债券': false, '权益-红利': false, '权益-成长': false, '权益-价值': false, '黄金': false, '原油': false });
const FORM_SECTION_C = reactive<Record<string, boolean>>({ '利率债': false, '信用债': false, '可转债': false, '港股': false, 'A股大盘': false, '黄金': false, 'REITs': false });
const formCoreView = ref('');
const formRiskFlag = ref(false);

interface MemberSubmission { sectionA: Record<string, number>; sectionB: Record<string, boolean>; sectionC: Record<string, boolean>; coreView: string; riskFlag: boolean; submittedAt: string; }

const MEMBERS_DATA = [
  { id: 'm0', name: '曾XX', role: '主任委员' },
  { id: 'm1', name: '陈XX', role: '班子' },
  { id: 'm2', name: '张XX', role: '部门长' },
  { id: 'm3', name: '李XX', role: '投资经理' },
  { id: 'm4', name: '王XX', role: '部门长' },
  { id: 'm5', name: '赵XX', role: '投资经理' },
  { id: 'm6', name: '刘XX', role: '风控合规总监' },
];

const memberSubmissions = reactive<Record<string, MemberSubmission>>({});

/**
 * 从后端加载混合投委会问卷提交记录，填充成员提交状态（含评分明细）。
 * GET /v1/committee/mixed/sessions?session_code=2026Q2
 */
async function loadMixedSubmissions() {
  try {
    const { data } = await http.get('/v1/committee/mixed/sessions');
    // data: { session_code, total, submissions: [{ id, session_code, submitter_id, submitted_at, questionnaire_json }] }
    for (const sub of data.submissions ?? []) {
      const mid = `m${sub.submitter_id}`;
      const qj = sub.questionnaire_json ?? {};
      const sectionA = qj.section_a ?? {};
      const sectionB = qj.section_b ?? {};
      const sectionC: Record<string, boolean> = {};
      for (const key of (qj.section_c ?? [])) {
        sectionC[key] = true;
      }
      memberSubmissions[mid] = {
        sectionA: { ...sectionA },
        sectionB: { ...sectionB },
        sectionC,
        coreView: qj.core_view ?? '',
        riskFlag: qj.risk_flag ?? false,
        submittedAt: sub.submitted_at
          ? new Date(sub.submitted_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
          : '-',
      };
    }
  } catch {
    // 后端不可用时保持空状态，不影响页面其他功能
  }
}

const activeMemberId = ref<string | null>(null);
const activeMember = computed(() => MEMBERS_DATA.find(m => m.id === activeMemberId.value));

// ── ⚠️ TODO: 以下为演示用 Mock 数据，待后端 API 实现后替换 ──────────────
// PRODUCT_CATEGORIES   → 待产品业绩系统 API (外部系统)
// TOP_STRATEGIES       → 待策略排行 API (外部系统)
// BOTTOM_STRATEGIES    → 待策略排行 API (外部系统)
// MODEL_OUTPUTS        → 待模型输出 API (外部系统: 回测/风控)
// MEMBERS_DATA         → 待用户目录 API (或从 JWT/配置读取)
// ────────────────────────────────────────────────────────────────────────

const showHistoryModal = ref(false);

interface CommitteeViewCard {
  author: string;
  role: string;
  color: string;
  sentiment: string;
  content: string;
  tags: string[];
}

/** 委员角色 → 主题色映射 */
const ROLE_COLORS: Record<string, string> = {
  '主任委员': '#FFAB00',
  '班子': '#8B5CF6',
  '部门长': '#3B9EFF',
  '投资经理': '#22D3EE',
  '风控合规总监': '#FF9500',
};

/** 根据委员评分均值推断情绪倾向 */
function inferSentiment(avgScore: number): string {
  if (avgScore >= 3.8) return '偏多';
  if (avgScore >= 2.8) return '中性';
  return '偏空';
}

/** 从核心观点文本中提取标签（简易关键词匹配） */
function extractTags(coreView: string, riskFlag: boolean): string[] {
  const tags: string[] = [];
  if (riskFlag) tags.push('风险预警');
  const keywordMap: [RegExp, string][] = [
    [/权益|股票|A股|港股/g, '权益'],
    [/债券|利率|久期|信用/g, '固收'],
    [/黄金|避险/g, '黄金'],
    [/原油|能源/g, '原油'],
    [/红利|高股息/g, '红利'],
    [/成长|科技/g, '成长'],
    [/价值|估值/g, '价值'],
    [/量化|CTA|趋势/g, '量化'],
    [/流动性|安全垫|风控/g, '风控'],
    [/政策|宏观/g, '宏观'],
  ];
  for (const [re, label] of keywordMap) {
    if (re.test(coreView)) tags.push(label);
  }
  return tags.length > 0 ? [...new Set(tags)].slice(0, 4) : ['观点'];
}

/**
 * 会前问卷汇总 · 委员定性观点
 * 从 memberSubmissions（真实后端数据）中提取 coreView，生成观点卡片。
 * 无提交数据的委员不展示。
 */
const committeeQualitativeViews = computed<CommitteeViewCard[]>(() => {
  return MEMBERS_DATA
    .filter(m => memberSubmissions[m.id]?.coreView?.trim())
    .map(m => {
      const sub = memberSubmissions[m.id];
      const scores = Object.values(sub.sectionA).filter((v): v is number => typeof v === 'number');
      const avg = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 3;
      return {
        author: m.name,
        role: m.role,
        color: ROLE_COLORS[m.role] ?? '#94A3B8',
        sentiment: inferSentiment(avg),
        content: sub.coreView,
        tags: extractTags(sub.coreView, sub.riskFlag),
      };
    });
});

interface HistoricalVote {
  period: string;
  scores: Record<string, number>;
  newHighs: string[];
}

/** 历史投票数据，从后端加载 */
const historicalVotes = ref<HistoricalVote[]>([
  { period: '2026 Q1', scores: { '债券': 4, '权益-红利': 3, '权益-成长': 2, '权益-价值': 3, '黄金': 4, '原油': 2 }, newHighs: ['债券', '黄金'] },
]);

/** 从后端加载历史会期评分数据 */
async function loadHistoryVotes() {
  try {
    const { data } = await http.get('/v1/committee/mixed/sessions/history', { params: { limit: 10 } });
    // data: { sessions: [{ session_code, submitted_count, scores: { asset: { avg, max, min, count } } }] }
    historicalVotes.value = (data.sessions ?? []).map(s => {
      const period = s.session_code.replace(/Q/g, ' Q');
      const scores: Record<string, number> = {};
      const newHighs: string[] = [];
      for (const [asset, info] of Object.entries(s.scores ?? {})) {
        if (typeof info === 'object' && info !== null && 'avg' in info) {
          scores[asset] = (info as { avg: number }).avg;
        }
      }
      return { period, scores, newHighs };
    });
  } catch {
    // 后端不可用时保留 mock 数据作为降级
  }
}

function handleUrgentRemind(memberName: string) {
  window.alert(`已向 ${memberName} 发送催办通知。`);
}

async function handleUrgentRemindApi(memberName: string, memberId?: number) {
  try {
    await http.post('/v1/committee/mixed/remind', { member_name: memberName, member_id: memberId });
    window.alert(`已向 ${memberName} 发送催办通知。`);
  } catch {
    window.alert(`催办通知发送失败，请稍后重试。`);
  }
}

function formatMeetingDate(iso: string | null | undefined): string {
  if (!iso) return '2026.04.15';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '2026.04.15';
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
}

const meetingHeaderCode = computed(
  () => committeePageContext.value?.meeting?.meeting_code ?? 'IC-2026-Q2-04',
);
const meetingHeaderDate = computed(() => {
  const r = committeePageContext.value?.resolution?.published_at;
  const s = committeePageContext.value?.meeting?.scheduled_at;
  return formatMeetingDate((r ?? s) as string | undefined);
});

/** 有后端投票记录时以前端为准展示回收进度；否则沿用本地 mock 提交数 */
const voteProgressTotal = computed(() => {
  const vn = committeePageContext.value?.votes?.length ?? 0;
  return vn > 0 ? Math.max(MEMBERS_DATA.length, vn) : MEMBERS_DATA.length;
});

const submittedCount = computed(() => {
  const vn = committeePageContext.value?.votes?.length ?? 0;
  if (vn > 0) return vn;
  return Object.keys(memberSubmissions).length;
});

const voteProgressPct = computed(() => {
  const t = voteProgressTotal.value;
  if (t <= 0) return 0;
  return Math.min(100, (submittedCount.value / t) * 100);
});

const voteProgressComplete = computed(() => submittedCount.value >= voteProgressTotal.value && voteProgressTotal.value > 0);
const sentReminders = reactive(new Set<string>());

function selectMember(id: string) { activeMemberId.value = id; }
function sendReminder(id: string) { sentReminders.add(id); }
function sendAllReminders() { MEMBERS_DATA.forEach(m => { if (!memberSubmissions[m.id]) sentReminders.add(m.id); }); }

const SELF_MEMBER_ID = computed(() => {
  const roleMap: Record<string, string> = {
    '班子': 'm1',
    '部门长': 'm2',
    '投资经理': 'm3',
    '混合投资委员会秘书': 'm0',
    '混合投资委员会委员': 'm3',
    '混合投资委员会主任委员': 'm0',
  };
  return roleMap[activeRole.value] || 'm3';
});
const memberSubmitted = computed(() => memberSubmissions[SELF_MEMBER_ID.value] || null);

function scoreToVoteChoice(score: number): 'underweight' | 'neutral' | 'overweight' {
  if (score <= 2) return 'underweight';
  if (score >= 4) return 'overweight';
  return 'neutral';
}

function buildVotePayload() {
  const choice_items: Record<string, string> = {};
  const numeric_items: Record<string, number> = {};

  for (const [asset, score] of Object.entries(FORM_SECTION_A)) {
    choice_items[`${asset}_view`] = scoreToVoteChoice(score);
    numeric_items[`${asset}_score`] = score;
  }

  const selectedFocus = Object.keys(FORM_SECTION_C).filter(k => FORM_SECTION_C[k]);
  if (selectedFocus.length > 0) {
    choice_items.focus_asset = selectedFocus[0];
  }
  if (formRiskFlag.value) {
    choice_items.risk_flag = 'true';
  }
  if (formCoreView.value.trim()) {
    choice_items.core_view = formCoreView.value.trim();
  }

  return { vote: { choice_items, numeric_items } };
}

function resolveVotingMeetingId(): number | null {
  if (currentMeetingId.value != null) return currentMeetingId.value;
  const contextMeetingId = committeePageContext.value?.meeting?.id;
  if (typeof contextMeetingId === 'number') return contextMeetingId;
  return meetingList.length > 0 ? meetingList[0].id : null;
}

async function submitMemberForm() {
  if (!activeMemberId.value || !formCoreView.value.trim()) return;
  const meetingId = resolveVotingMeetingId();
  if (!meetingId) {
    alert('未找到可投票会议，请先创建并进入会议');
    return;
  }
  try {
    await http.post(`/v1/committee/meetings/${meetingId}/submit-vote`, buildVotePayload());
    memberSubmissions[activeMemberId.value] = {
      sectionA: { ...FORM_SECTION_A }, sectionB: { ...FORM_SECTION_B }, sectionC: { ...FORM_SECTION_C },
      coreView: formCoreView.value, riskFlag: formRiskFlag.value,
      submittedAt: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    };
    await fetchCommitteePageData();
  } catch (err) {
    console.error('[Committee] 提交失败:', err);
    alert('提交失败，请检查后端服务是否正常运行');
  }
}

async function submitMemberFormSelf() {
  if (!formCoreView.value.trim()) return;
  const meetingId = resolveVotingMeetingId();
  if (!meetingId) {
    alert('未找到可投票会议，请先创建并进入会议');
    return;
  }
  try {
    await http.post(`/v1/committee/meetings/${meetingId}/submit-vote`, buildVotePayload());
    memberSubmissions[SELF_MEMBER_ID.value] = {
      sectionA: { ...FORM_SECTION_A }, sectionB: { ...FORM_SECTION_B }, sectionC: { ...FORM_SECTION_C },
      coreView: formCoreView.value, riskFlag: formRiskFlag.value,
      submittedAt: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    };
    await fetchCommitteePageData();
  } catch (err) {
    console.error('[Committee] 提交失败:', err);
    alert('提交失败，请检查后端服务是否正常运行');
  }
}

// ── Step 1: Product Category Performance ─────────────────────
interface ProdItem {
  name: string;
  ret: number;       // 区间收益率 %
  alpha: number;     // Alpha 收益 %
  beta: number;      // Beta 收益 %
  lev: number;       // 杠杆收益 %
  rank: string;      // 竞品排名标签 e.g. 'TOP 8%'
  rankTier: 1 | 2 | 3;  // 1=前四分位 2=中段 3=后段
  timing: number;    // 调仓贡献度 bps
  selRate: number;   // 择券胜率 0-100
  maxdd: string;
}

interface ProdCategory {
  label: string;
  tag: string;
  color: string;
  items: ProdItem[];
}

const PRODUCT_CATEGORIES: ProdCategory[] = [
  {
    label: '固收+低波', tag: 'LOW-VOL', color: '#22D3EE',
    items: [
      { name: '稳健增利A', ret: 4.2,  alpha: 1.8,  beta: 2.1, lev: 0.3,  rank: 'TOP 8%',  rankTier: 1, timing: 12.5, selRate: 68, maxdd: '-1.2%' },
      { name: '启航1号',   ret: 3.8,  alpha: 1.2,  beta: 2.3, lev: 0.3,  rank: 'TOP 22%', rankTier: 1, timing: 8.1,  selRate: 62, maxdd: '-1.8%' },
    ],
  },
  {
    label: '固收+中波', tag: 'MID-VOL', color: '#3B9EFF',
    items: [
      { name: '全天候FOF', ret: 2.9,  alpha: 0.8,  beta: 1.9, lev: 0.2,  rank: 'TOP 35%', rankTier: 2, timing: 6.8,  selRate: 55, maxdd: '-2.5%' },
      { name: '高收益债',  ret: -2.1, alpha: -0.8, beta: -1.1, lev: -0.2, rank: 'BOT 12%', rankTier: 3, timing: -3.2, selRate: 38, maxdd: '-6.8%' },
    ],
  },
  {
    label: '混合', tag: 'HYBRID', color: '#FFAB00',
    items: [
      { name: '成长精选',   ret: 5.1,  alpha: 2.4,  beta: 2.5,  lev: 0.2,  rank: 'TOP 6%',  rankTier: 1, timing: 18.7, selRate: 72, maxdd: '-5.3%' },
      { name: '量化对冲',   ret: 1.8,  alpha: 1.5,  beta: 0.2,  lev: 0.1,  rank: 'TOP 28%', rankTier: 2, timing: -1.5, selRate: 58, maxdd: '-3.1%' },
      { name: '港股通精选', ret: -1.9, alpha: -1.2, beta: -0.5, lev: -0.2, rank: 'BOT 18%', rankTier: 3, timing: -2.1, selRate: 42, maxdd: '-9.2%' },
    ],
  },
];

/** PM 定性评价（可编辑） */
const guidanceQualReview = ref('');

/** 系统自动生成的定量分析摘要 */
const guidanceQuantAnalysis = computed(() => {
  const all = PRODUCT_CATEGORIES.flatMap(c => c.items);
  const total = all.length;
  const pos = all.filter(i => i.ret > 0).length;
  const winRate = Math.round(pos / total * 100);
  const topQ = all.filter(i => i.rankTier === 1).length;
  const posT = all.filter(i => i.timing > 0).length;
  const avgAlpha = (all.reduce((s, i) => s + i.alpha, 0) / total).toFixed(2);
  const avgSel = Math.round(all.reduce((s, i) => s + i.selRate, 0) / total);
  return `本期共 ${total} 只产品完成回溯，${pos} 只正收益（胜率 ${winRate}%）；前四分位产品 ${topQ} 只（占 ${Math.round(topQ / total * 100)}%）。` +
    `Alpha 均值 ${Number(avgAlpha) >= 0 ? '+' : ''}${avgAlpha}%，固收+低波类别 Beta 来源占比最高（>50%），指引跟踪偏离最小（≤20bps）。` +
    `择时贡献为正的产品 ${posT} 只（${Math.round(posT / total * 100)}%）；择券平均胜率 ${avgSel}%，混合类别 Alpha 离散度较大，需审视主动管理能力稳定性。`;
});

const TOP_STRATEGIES = [
  { name: '利率债骑乘', type: '固收', return: '+4.2%', sharpe: '2.31' },
  { name: '红利低波',   type: '权益', return: '+3.8%', sharpe: '1.87' },
  { name: '可转债双低', type: '转债', return: '+3.5%', sharpe: '1.72' },
  { name: 'CTA趋势',   type: '另类', return: '+3.1%', sharpe: '1.65' },
  { name: '信用挖掘',  type: '固收', return: '+2.9%', sharpe: '1.53' },
];
const BOTTOM_STRATEGIES = [
  { name: '中小盘成长', issue: '回撤超限 · 风格漂移', return: '-5.8%', maxdd: '-12.3%' },
  { name: '高收益债',   issue: '信用利差走阔',         return: '-2.1%', maxdd: '-6.8%' },
  { name: '港股通精选', issue: '流动性不足',            return: '-1.9%', maxdd: '-9.2%' },
];

// ── Step 2: Consensus & Models ────────────────────────────────
const MATRIX_COL_EXTREMES = computed(() => {
  const result: Record<string, { max: number; min: number }> = {};
  for (const asset of ASSET_LIST) {
    const scores = MEMBERS_DATA
      .filter(m => memberSubmissions[m.id])
      .map(m => memberSubmissions[m.id].sectionA[asset] ?? 3);
    result[asset] = {
      max: scores.length > 0 ? Math.max(...scores) : 3,
      min: scores.length > 0 ? Math.min(...scores) : 3,
    };
  }
  return result;
});

const MATRIX_COL_AVG = computed(() => {
  const result: Record<string, number> = {};
  for (const asset of ASSET_LIST) {
    const scores = MEMBERS_DATA
      .filter(m => memberSubmissions[m.id])
      .map(m => memberSubmissions[m.id].sectionA[asset] ?? 3);
    result[asset] = scores.length > 0 ? Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 10) / 10 : 3;
  }
  return result;
});
const CONSENSUS_ANALYSIS = computed(() => {
  const submittedMembers = MEMBERS_DATA.filter(m => memberSubmissions[m.id]);
  return ASSET_LIST.map(asset => {
    const scores = submittedMembers.map(m => memberSubmissions[m.id].sectionA[asset] ?? 3);
    const avg = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 3;
    const maxScore = scores.length > 0 ? Math.max(...scores) : 3;
    const minScore = scores.length > 0 ? Math.min(...scores) : 3;
    const newHighCount = submittedMembers.filter(m => memberSubmissions[m.id].sectionB[asset]).length;
    const prevAvg = historicalVotes.value.length > 0 ? (historicalVotes.value[0].scores[asset] ?? 3) : 3;
    const delta = avg - prevAvg;
    const label = avg >= 4.5 ? '乐观' : avg >= 3.5 ? '中性偏乐观' : avg >= 2.5 ? '中性' : avg >= 1.5 ? '中性偏谨慎' : '谨慎';
    const spread = maxScore - minScore;
    const consensus = spread <= 1 ? '高度一致' : spread <= 2 ? '方向趋同' : '分歧明显';
    return { asset, avg: Math.round(avg * 10) / 10, maxScore, minScore, newHighCount, prevAvg, delta, label, consensus, scores, memberIds: submittedMembers.map(m => m.id) };
  });
});

const VOTING_MATRIX = computed(() => {
  const submittedMembers = MEMBERS_DATA.filter(m => memberSubmissions[m.id]);
  return { members: submittedMembers, assets: [...ASSET_LIST] };
});

const GUIDANCE_MAP: Record<string, { high: string; mid: string; low: string }> = {
  '债券': { high: '拉长久期，适当下沉信用', mid: '维持中性久期，关注骑乘机会', low: '缩短久期，保持高流动性' },
  '权益-红利': { high: '增配高股息标的，把握分红行情', mid: '标配红利策略，注重防御', low: '减持红利暴露，转向防御性资产' },
  '权益-成长': { high: '积极布局成长赛道，把握估值修复', mid: '均衡配置成长板块', low: '规避高估值成长股，控制回撤' },
  '权益-价值': { high: '重配价值股，把握估值洼地', mid: '标配价值策略', low: '减持价值暴露，等待更好时机' },
  '黄金': { high: '增配黄金避险，对冲地缘风险', mid: '标配黄金，维持组合分散化', low: '减持黄金，释放资金效率' },
  '原油': { high: '把握能源涨价周期，适度参与', mid: '标配原油相关资产', low: '规避原油风险敞口' },
};

const GRADE_COLORS: Record<number, string> = {
  1: 'bg-[#00C9A7]/10 text-[#00C9A7] border-[#00C9A7]/25',   // 谨慎 — 绿
  2: 'bg-[#22D3EE]/10 text-[#22D3EE] border-[#22D3EE]/25',   // 中性偏谨慎 — 青
  3: 'bg-[#3B9EFF]/10 text-[#3B9EFF] border-[#3B9EFF]/25',   // 中性 — 蓝
  4: 'bg-[#FFAB00]/10 text-[#FFAB00] border-[#FFAB00]/25',   // 中性偏乐观 — 琥珀
  5: 'bg-[#F04864]/10 text-[#F04864] border-[#F04864]/25',   // 乐观 — 红
};

const chairmanGrades = reactive<Record<string, number>>({});
ASSET_LIST.forEach(a => { chairmanGrades[a] = MATRIX_COL_AVG[a] ? Math.round(MATRIX_COL_AVG[a]) : 3; });

const BOND_DURATION_MAP: Record<number, string> = { 1: '1-1.5年', 2: '1.5-2年', 3: '2-3年', 4: '3-4年', 5: '3-5年' };
const POSITION_MAP: Record<number, string> = { 1: '0-5%', 2: '5-10%', 3: '10-15%', 4: '15-20%', 5: '20-30%' };

const GUIDANCE_TEXT_MAP: Record<number, string> = {
  1: '谨慎规避，严格控制风险敞口',
  2: '中性偏谨慎，低配或观望',
  3: '中性标配，维持现有水平',
  4: '中性偏乐观，适度增配',
  5: '乐观积极，重点配置',
};

const DYNAMIC_GUIDANCE = computed(() => {
  const result: Record<string, string> = {};
  for (const asset of ASSET_LIST) {
    const grade = chairmanGrades[asset] ?? 3;
    if (asset === '债券') {
      result[asset] = `建议久期范围 ${BOND_DURATION_MAP[grade]}，${GUIDANCE_TEXT_MAP[grade]}`;
    } else if (asset.startsWith('权益')) {
      result[asset] = `建议仓位比例 ${POSITION_MAP[grade]}，${GUIDANCE_TEXT_MAP[grade]}`;
    } else {
      result[asset] = `建议配置比例 ${POSITION_MAP[grade]}，${GUIDANCE_TEXT_MAP[grade]}`;
    }
  }
  return result;
});

const DYNAMIC_METRIC = computed(() => {
  const result: Record<string, string> = {};
  for (const asset of ASSET_LIST) {
    const grade = chairmanGrades[asset] ?? 3;
    result[asset] = asset === '债券' ? `久期 ${BOND_DURATION_MAP[grade]}` : `仓位 ${POSITION_MAP[grade]}`;
  }
  return result;
});

const signerId = ref('m0');
const signerName = computed(() => MEMBERS_DATA.find(m => m.id === signerId.value)?.name ?? '-');

const GUIDANCE_RESULT = computed(() => {
  return CONSENSUS_ANALYSIS.value.map(ca => {
    const map = GUIDANCE_MAP[ca.asset];
    const guidance = ca.avg >= 4 ? map.high : ca.avg >= 2.5 ? map.mid : map.low;
    return { ...ca, guidance };
  });
});

const EQUITY_STYLE_GUIDANCE = computed(() => {
  const items = CONSENSUS_ANALYSIS.value.filter(ca => ca.asset.startsWith('权益'));
  if (items.length === 0) return { main: '数据不足', detail: '' };
  const sorted = [...items].sort((a, b) => b.avg - a.avg);
  const main = sorted[0];
  const worst = sorted[sorted.length - 1];
  const detail = main.avg === worst.avg
    ? `三种风格均值一致 (${main.avg.toFixed(1)})，建议均衡配置`
    : `当前建议主力风格: ${main.asset} (${main.avg.toFixed(1)}分)`;
  return { main: main.asset, avg: main.avg, detail, items: sorted };
});

const aiMinutesLoading = ref(false);
const aiMinutesReady = ref(false);
const aiMinutesContent = ref('');

function generateAIMinutes() {
  aiMinutesLoading.value = true;
  aiMinutesReady.value = false;
  const divergences = CONSENSUS_ANALYSIS.value
    .filter(ca => ca.consensus === '分歧明显')
    .map(ca => {
      const maxMember = ca.memberIds[ca.scores.indexOf(ca.maxScore)];
      const minMember = ca.memberIds[ca.scores.indexOf(ca.minScore)];
      const maxName = MEMBERS_DATA.find(m => m.id === maxMember)?.name ?? '某委员';
      const minName = MEMBERS_DATA.find(m => m.id === minMember)?.name ?? '某委员';
      return `${maxName}与${minName}在${ca.asset}资产的分歧较大（${ca.minScore}分 vs ${ca.maxScore}分）`;
    });

  const guidanceText = GUIDANCE_RESULT.value.map(g => `${g.asset}：均值 ${g.avg.toFixed(1)}（${g.label}）— ${g.guidance}`).join('\n');

  setTimeout(() => {
    aiMinutesContent.value = [
      `【会议纪要 · ${meetingHeaderCode.value}】`,
      `日期：${meetingHeaderDate.value}`,
      '',
      '一、投票汇总',
      `本次会议共收到 ${submittedCount.value} 份问卷，综合评分如下：`,
      ...CONSENSUS_ANALYSIS.value.map(ca => `  - ${ca.asset}: 均值 ${ca.avg.toFixed(1)}（${ca.label}），较上期 ${ca.delta >= 0 ? '+' : ''}${ca.delta.toFixed(1)}`),
      '',
      '二、配置指引',
      guidanceText,
      '',
      '三、权益风格建议',
      EQUITY_STYLE_GUIDANCE.value.detail,
      '',
      ...(divergences.length > 0 ? ['四、争论焦点', ...divergences.map(d => `  - ${d}`)] : []),
    ].join('\n');
    aiMinutesLoading.value = false;
    aiMinutesReady.value = true;
  }, 3000);
}

const MODEL_OUTPUTS = [
  { name: 'SAA 蒙特卡洛', badge: 'MC-SIM', color: '#3B9EFF', desc: '10万次随机模拟 · 均值-方差前沿', sharpe: '0.82', highlight: false, action: false, allocations: [{ label: '权益', weight: 35, color: '#3B9EFF' }, { label: '固收', weight: 50, color: '#22D3EE' }, { label: '另类', weight: 15, color: '#F1C40F' }] },
  { name: 'BL 模型', badge: 'BLACK-LIT', color: '#22D3EE', desc: '贝叶斯观点注入 · 委员预期融合', sharpe: '0.95', highlight: true, action: true, allocations: [{ label: '权益', weight: 42, color: '#3B9EFF' }, { label: '固收', weight: 43, color: '#22D3EE' }, { label: '另类', weight: 15, color: '#F1C40F' }] },
  { name: 'Risk Parity', badge: 'RP-ATAN', color: '#F1C40F', desc: '等风险贡献 · 波动率平价', sharpe: '0.78', highlight: false, action: false, allocations: [{ label: '权益', weight: 28, color: '#3B9EFF' }, { label: '固收', weight: 55, color: '#22D3EE' }, { label: '另类', weight: 17, color: '#F1C40F' }] },
];

// ── Step 3: Decision table ────────────────────────────────────
const expandedGroups = reactive(new Set<string>(['债券', '权益']));
function toggleGroup(asset: string) { expandedGroups.has(asset) ? expandedGroups.delete(asset) : expandedGroups.add(asset); }

/** 决议表数据由 demoStore.committeeDecisionTable 提供（fetchMeetingResolution 从门户快照覆盖） */
const decisionTable = committeeDecisionTable;

const showSAASandbox = ref(false);

// ── Step 3: Chairman Decision Matrix + Product Guidance ───────

type BondGrade = '高' | '中' | '低';

const BOND_GRADE_DURATION: Record<BondGrade, string> = {
  高: '3-5年',
  中: '1-3年',
  低: '0-1年',
};

const BOND_GRADE_LABEL: Record<BondGrade, string> = {
  高: '3-5Y (长久期策略)',
  中: '1-3Y (中枢久期策略)',
  低: '0-1Y (短久期/货币策略)',
};

const PRODUCT_BOND_LABELS: Record<string, string> = { low: '低波久期', mid: '中波久期', hybrid: '混合久期' };

/** 主任委员顶层配置决策 */
const chairDecision = reactive({
  bondGrade: '中' as BondGrade,
  perProductBondGrade: { low: '中' as BondGrade, mid: '中' as BondGrade, hybrid: '中' as BondGrade },
  equityGrade: 3,
  equityMix: { 红利: 40, 成长: 35, 价值: 25 } as Record<'红利' | '成长' | '价值', number>,
  altNotes: '',
});

type EquitySubKey = '红利' | '港股' | '其他权益' | 'REITS' | '黄金';

const EQUITY_SUB_KEYS: EquitySubKey[] = ['红利', '港股', '其他权益', 'REITS', '黄金'];

const PRODUCT_EQUITY_COEFF: Record<string, Record<EquitySubKey, number>> = {
  low:    { 红利: 0.50, 港股: 0.15, 其他权益: 0.10, REITS: 0.10, 黄金: 0.15 },
  mid:    { 红利: 0.45, 港股: 0.20, 其他权益: 0.15, REITS: 0.10, 黄金: 0.10 },
  hybrid: { 红利: 0.35, 港股: 0.20, 其他权益: 0.20, REITS: 0.15, 黄金: 0.10 },
};

/** 权益明细之和（用于校验） */
const equityMixSum = computed(() =>
  chairDecision.equityMix['红利'] + chairDecision.equityMix['成长'] + chairDecision.equityMix['价值'],
);

interface ProductGuidanceRow {
  id: string;
  name: string;
  tag: string;
  color: string;
  prevBond: number;
  prevEquity: number;
  prevAlt: number;
  prevLiquidity: number;
  bond: number;
  equity: number;
  equitySub: Record<EquitySubKey, number>;
  alt: number;
  altText: string;
  liquidity: number;
}

const productGuidances = reactive<ProductGuidanceRow[]>([
  { id: 'low',    name: '固收+中低波', tag: 'LOW-VOL', color: '#22D3EE', prevBond: 75, prevEquity: 10, prevAlt: 5, prevLiquidity: 10, bond: 0, equity: 0, equitySub: { 红利: 0, 港股: 0, 其他权益: 0, REITS: 0, 黄金: 0 }, alt: 0, altText: '维持一档风险预算', liquidity: 0 },
  { id: 'mid',    name: '固收+中波', tag: 'MID-VOL', color: '#3B9EFF', prevBond: 58, prevEquity: 25, prevAlt: 8, prevLiquidity:  9, bond: 0, equity: 0, equitySub: { 红利: 0, 港股: 0, 其他权益: 0, REITS: 0, 黄金: 0 }, alt: 0, altText: '标配REITS+黄金', liquidity: 0 },
  { id: 'hybrid', name: '混合绝对收益', tag: 'HYBRID',  color: '#FFAB00', prevBond: 38, prevEquity: 45, prevAlt: 8, prevLiquidity:  9, bond: 0, equity: 0, equitySub: { 红利: 0, 港股: 0, 其他权益: 0, REITS: 0, 黄金: 0 }, alt: 0, altText: '增配REITS+关注CTA', liquidity: 0 },
]);

/** 是否已点击"计算产品指引"完成自动填充 */
const guidanceCalculated = ref(false);

const showHistoryDiff = ref(false);

const PREV_SNAPSHOT = {
  bondGrade: '中' as BondGrade,
  bondDuration: '1-3年',
  equityGrade: 3,
  equityLabel: '中性',
  perProductBondGrade: { low: '低' as BondGrade, mid: '中' as BondGrade, hybrid: '中' as BondGrade },
  products: [
    { id: 'low', name: '固收+中低波', bond: 75, equity: 10, equitySub: { 红利: 5.0, 港股: 1.5, 其他权益: 1.0, REITS: 1.0, 黄金: 1.5 }, alt: 5, altText: '维持一档风险预算', liquidity: 10 },
    { id: 'mid', name: '固收+中波', bond: 58, equity: 25, equitySub: { 红利: 11.3, 港股: 5.0, 其他权益: 3.8, REITS: 2.5, 黄金: 2.5 }, alt: 8, altText: '标配REITS+黄金', liquidity: 9 },
    { id: 'hybrid', name: '混合绝对收益', bond: 38, equity: 45, equitySub: { 红利: 15.8, 港股: 9.0, 其他权益: 9.0, REITS: 6.8, 黄金: 4.5 }, alt: 8, altText: '增配REITS+关注CTA', liquidity: 9 },
  ],
};

function diffBadge(cur: number, prev: number, suffix = '%'): string | null {
  const d = cur - prev;
  if (Math.abs(d) < 0.01) return null;
  return (d > 0 ? '+' : '') + d.toFixed(1) + suffix;
}
function diffBondGrade(cur: BondGrade, prev: BondGrade): string | null {
  if (cur === prev) return null;
  return `由${prev}调${cur}`;
}

/** 债券档位 × 产品类型 → 基准固收仓位（索引: 高=0 中=1 低=2） */
const BASE_BOND: Record<string, [number, number, number]> = {
  low:    [78, 72, 65],
  mid:    [65, 58, 50],
  hybrid: [45, 38, 30],
};
/** 债券档位 × 产品类型 → 基准权益仓位 */
const BASE_EQUITY: Record<string, [number, number, number]> = {
  low:    [10, 12, 15],
  mid:    [20, 25, 30],
  hybrid: [38, 45, 55],
};

function calcProductGuidances() {
  const bgIdx: Record<BondGrade, number> = { 高: 0, 中: 1, 低: 2 };
  const eqAdj = (chairDecision.equityGrade - 3) * 5;
  for (const row of productGuidances) {
    const idx = bgIdx[chairDecision.perProductBondGrade[row.id] ?? chairDecision.bondGrade];
    const equity   = Math.max(0, Math.min(100, BASE_EQUITY[row.id][idx] + eqAdj));
    const bond     = Math.max(0, Math.min(100, BASE_BOND[row.id][idx]   - eqAdj));
    const alt      = row.prevAlt;
    const liquidity = Math.max(0, 100 - bond - equity - alt);
    row.bond      = bond;
    row.equity    = equity;
    row.alt       = alt;
    row.liquidity = liquidity;
    for (const k of EQUITY_SUB_KEYS) {
      row.equitySub[k] = +(equity * PRODUCT_EQUITY_COEFF[row.id][k]).toFixed(1);
    }
  }
  guidanceCalculated.value = true;
}

/** 规则校验：返回所有红线原因（空数组=通过） */
const validationErrors = computed((): string[] => {
  const errs: string[] = [];
  if (equityMixSum.value !== 100) {
    errs.push(`权益明细之和为 ${equityMixSum.value}%，必须等于 100%（当前差 ${100 - equityMixSum.value}%）`);
  }
  if (guidanceCalculated.value) {
    for (const row of productGuidances) {
      const total = row.bond + row.equity + row.alt + row.liquidity;
      if (total < 95 || total > 105) {
        errs.push(`【${row.name}】各资产合计 ${total}%，偏离 100% 超出 ±5% 容差`);
      }
    }
  }
  return errs;
});

const canSubmitDecision = computed(() =>
  guidanceCalculated.value && validationErrors.value.length === 0,
);

const showValidationToast = ref(false);
const decisionSubmitted = ref(false);

function handleSubmitDecision() {
  if (!canSubmitDecision.value) {
    showValidationToast.value = true;
    setTimeout(() => { showValidationToast.value = false; }, 6000);
    return;
  }
  const hybrid = productGuidances.find(p => p.id === 'hybrid');
  const payload = {
    period: meetingList[0]?.name ?? '2026 Q2',
    decidedAt: new Date().toISOString(),
    decidedBy: '混合投资委员会主任委员',
    bondGrade: chairDecision.bondGrade,
    bondDuration: BOND_GRADE_DURATION[chairDecision.bondGrade],
    equityGrade: chairDecision.equityGrade,
    equityGradeLabel: SCORE_LABELS[chairDecision.equityGrade],
    equityMix: { ...chairDecision.equityMix },
    altNotes: chairDecision.altNotes,
    products: productGuidances.map(p => ({
      id: p.id, name: p.name,
      bond: p.bond, equity: p.equity, equitySub: { ...p.equitySub }, alt: p.alt, altText: p.altText, liquidity: p.liquidity,
    })),
  };
  deptAllocationDecision.value = payload;
  const activeMeeting = meetingList.find(m => m.status === '进行中');
  if (activeMeeting) {
    activeMeeting.status = '已结束';
    activeMeeting.decision =
      `决议：权益${SCORE_LABELS[chairDecision.equityGrade]}，` +
      `固收${chairDecision.bondGrade}久期（${BOND_GRADE_DURATION[chairDecision.bondGrade]}），` +
      `混合产品权益比例 ${hybrid?.equity ?? '-'}%`;
  }
  decisionSubmitted.value = true;
  markStepDone(3);
}

// ── Meeting Management Drawer (秘书专属) ─────────────────────
const MEETING_TYPES = ['月度', '季度', '年度'] as const;
type MeetingType = (typeof MEETING_TYPES)[number];

const PERIOD_OPTIONS: Record<MeetingType, string[]> = {
  月度: ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'],
  季度: ['Q1','Q2','Q3','Q4'],
  年度: ['上半年度','下半年度','年度'],
};

const MEETING_STATUS_LIST = ['待召开', '进行中', '已结束', '已取消'] as const;

interface MeetingItem {
  id: number;
  name: string;
  date: string;
  time: string;
  location: string;
  status: string;
  decision: string;
  meetingType: MeetingType;
  meetingPeriod: string;
  meetingYear: number;
  voteDeadline: string | null;
  voteForcedClosed: boolean;
  preMaterials: string;
  minutesTemplate: string;
}

const showMeetingDrawer = ref(false);

/** 将后端 MeetingStatus 映射为前端中文标签 */
function mapMeetingStatus(status: string): string {
  switch (status) {
    case 'DRAFT': return '筹备中';
    case 'VOTING': return '进行中';
    case 'PUBLISHED': return '已结束';
    default: return status;
  }
}

/** 将后端 MeetingType 映射为前端会议类型标签 */
function mapMeetingType(type: string): MeetingType {
  return type === 'FICC' ? '固定收益' : '季度';
}

/** 从标题或会议编码中提取季度（Q1/Q2/Q3/Q4） */
function extractQuarter(text: string): string {
  const match = text.match(/Q([1-4])/);
  return match ? `Q${match[1]}` : 'Q4';
}

/** 从标题或会议编码中提取年份 */
function extractYear(text: string): number {
  const match = text.match(/(\d{4})/);
  return match ? parseInt(match[1], 10) : new Date().getFullYear();
}

/** 将后端 API 返回的会议转换为前端 MeetingItem 格式 */
function toMeetingItem(raw: {
  id: number; meeting_code: string; title: string;
  type: string; status: string; scheduled_at: string | null;
  created_by: number; created_at: string; updated_at: string;
}): MeetingItem {
  const scheduledAt = raw.scheduled_at ? new Date(raw.scheduled_at) : null;
  const dateStr = scheduledAt
    ? `${scheduledAt.getFullYear()}.${String(scheduledAt.getMonth() + 1).padStart(2, '0')}.${String(scheduledAt.getDate()).padStart(2, '0')}`
    : '—';
  const timeStr = scheduledAt
    ? `${String(scheduledAt.getHours()).padStart(2, '0')}:${String(scheduledAt.getMinutes()).padStart(2, '0')}`
    : '—';
  const quarter = extractQuarter(raw.title || raw.meeting_code);
  const year = extractYear(raw.title || raw.meeting_code);

  return {
    id: raw.id,
    name: raw.title,
    date: dateStr,
    time: timeStr,
    location: '总部3楼会议室',
    status: mapMeetingStatus(raw.status),
    decision: '',
    meetingType: mapMeetingType(raw.type),
    meetingPeriod: quarter,
    meetingYear: year,
    voteDeadline: null,
    voteForcedClosed: false,
    preMaterials: '',
    minutesTemplate: '',
  };
}

const meetingList = reactive<MeetingItem[]>([]);

/** 从后端加载会议列表 */
async function loadMeetings() {
  try {
    const res = await http.get('/v1/committee/meetings');
    const items: MeetingItem[] = Array.isArray(res.data)
      ? res.data.map((raw: any) => toMeetingItem(raw))
      : [];
    meetingList.length = 0;
    meetingList.push(...items);
  } catch (err) {
    console.error('[Committee] 加载会议列表失败:', err);
  }
}

function buildUniqueMeetingCode(now: Date): string {
  const y = now.getFullYear();
  const m = now.getMonth() + 1;
  const quarter = m <= 3 ? 'Q1' : m <= 6 ? 'Q2' : m <= 9 ? 'Q3' : 'Q4';
  const stamp = `${String(now.getDate()).padStart(2, '0')}${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`;
  const rand = Math.floor(Math.random() * 100).toString().padStart(2, '0');
  return `IC-${y}-${quarter}-${stamp}${rand}`;
}

// ── 新增会议（自动标题，无弹窗）─────────────────────────────────
async function quickCreateMeeting() {
  const now = new Date();
  const m = now.getMonth() + 1;
  const year = now.getFullYear();
  let title: string;
  if (m === 12 || m === 1 || m === 2) {
    title = `${m === 12 ? year : year - 1}年度配置决策会议`;
  } else if (m >= 3 && m <= 5) {
    title = `${year} Q1 配置决策会议`;
  } else if (m >= 6 && m <= 8) {
    title = `${year} Q2 配置决策会议`;
  } else {
    title = `${year} Q3 配置决策会议`;
  }
  const payload = {
    title: `混合投资委员会 ${title}`,
    type: 'MIXED',
  };
  try {
    // 发生唯一键冲突时自动重试，避免页面刷新后本地计数器重置导致撞码
    for (let i = 0; i < 3; i++) {
      try {
        await http.post('/v1/committee/meetings', {
          meeting_code: buildUniqueMeetingCode(new Date()),
          ...payload,
        });
        await loadMeetings();
        return;
      } catch (e: any) {
        const detail = e?.response?.data?.detail ?? '';
        const msg = String(detail);
        if (msg.includes('UNIQUE') || msg.includes('duplicate') || e?.response?.status === 409) {
          continue;
        }
        throw e;
      }
    }
    alert('创建会议失败：会议编码重复，请重试。');
  } catch (err: any) {
    const detail = err?.response?.data?.detail;
    console.error('[Committee] 创建会议失败:', err);
    alert(`创建会议失败：${detail ? String(detail) : '请检查后端服务'}`);
  }
}

// ── 编辑会议 Drawer ──────────────────────────────────────────
const showEditMeetingDrawer = ref(false);
const editingMeetingId = ref<number | null>(null);
const editingMeetingForm = reactive({
  meetingType: '季度' as MeetingType,
  meetingPeriod: 'Q3',
  meetingYear: 2026,
  date: '',
  time: '',
  location: '',
  status: '待召开' as string,
  decision: '',
  voteDeadline: '',
  voteForcedClosed: false,
  preMaterials: '',
  minutesTemplate: '',
});

const editingMeetingPeriodOptions = computed(() => PERIOD_OPTIONS[editingMeetingForm.meetingType]);
const editingMeetingTitle = computed(() =>
  `混合投资委员会 ${editingMeetingForm.meetingYear}年 ${editingMeetingForm.meetingPeriod} 配置决策会议`,
);

function openEditMeeting(id: number) {
  const item = meetingList.find(m => m.id === id);
  if (!item) return;
  editingMeetingId.value = id;
  Object.assign(editingMeetingForm, {
    meetingType: item.meetingType,
    meetingPeriod: item.meetingPeriod,
    meetingYear: item.meetingYear,
    date: item.date.replace(/\./g, '-'),
    time: item.time,
    location: item.location,
    status: item.status,
    decision: item.decision,
    voteDeadline: item.voteDeadline ?? '',
    voteForcedClosed: item.voteForcedClosed,
    preMaterials: item.preMaterials,
    minutesTemplate: item.minutesTemplate,
  });
  showEditMeetingDrawer.value = true;
}

function saveEditMeeting() {
  if (editingMeetingId.value === null) return;
  const item = meetingList.find(m => m.id === editingMeetingId.value);
  if (!item) return;
  Object.assign(item, {
    name: editingMeetingTitle.value,
    meetingType: editingMeetingForm.meetingType,
    meetingPeriod: editingMeetingForm.meetingPeriod,
    meetingYear: editingMeetingForm.meetingYear,
    date: editingMeetingForm.date ? editingMeetingForm.date.replace(/-/g, '.') : item.date,
    time: editingMeetingForm.time,
    location: editingMeetingForm.location,
    status: editingMeetingForm.status,
    decision: editingMeetingForm.decision,
    voteDeadline: editingMeetingForm.voteDeadline || null,
    voteForcedClosed: editingMeetingForm.voteForcedClosed,
    preMaterials: editingMeetingForm.preMaterials,
    minutesTemplate: editingMeetingForm.minutesTemplate,
  });
  showEditMeetingDrawer.value = false;
}

function deleteMeeting(id: number) {
  const idx = meetingList.findIndex(m => m.id === id);
  if (idx !== -1) meetingList.splice(idx, 1);
}

// ── 全局投票截止控制（当前进行中会议）───────────────────────
const voteForcedClosed = ref(false);
const voteDeadlineInput = ref('');
const nowTick = ref(new Date());
let nowTickInterval: ReturnType<typeof setInterval> | null = null;

const isVoteOpen = computed(() => {
  if (voteForcedClosed.value) return false;
  if (!voteDeadlineInput.value) return true;
  return new Date(voteDeadlineInput.value) > nowTick.value;
});

const voteCountdownDisplay = computed(() => {
  if (!voteDeadlineInput.value || voteForcedClosed.value) return '';
  const diff = new Date(voteDeadlineInput.value).getTime() - nowTick.value.getTime();
  if (diff <= 0) return '已过期';
  const totalMin = Math.floor(diff / 60000);
  if (totalMin < 60) return `${totalMin}分钟`;
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  return m > 0 ? `${h}小时${m}分钟` : `${h}小时`;
});

function forceCloseVote() { voteForcedClosed.value = true; }
function reopenVote() { voteForcedClosed.value = false; }

/** 允许委员在投票窗口开放期间重新编辑已提交的问卷 */
function clearMemberSubmission() {
  const id = SELF_MEMBER_ID.value;
  if (!id || !isVoteOpen.value) return;
  const sub = memberSubmissions[id];
  if (sub) {
    Object.assign(FORM_SECTION_A, sub.sectionA);
    Object.assign(FORM_SECTION_B, sub.sectionB);
    Object.assign(FORM_SECTION_C, sub.sectionC);
    formCoreView.value = sub.coreView;
    formRiskFlag.value = sub.riskFlag;
  }
  delete memberSubmissions[id];
}

// ── Step 4: Recording & Signing ───────────────────────────────
type MinuteState = 'draft' | 'pending' | 'ready';
const minuteState = ref<MinuteState>('draft');

const WAVE_COUNT = 30;
const waveformBars = ref<number[]>(Array.from({ length: WAVE_COUNT }, () => Math.random() * 32 + 6));

type RecState = 'idle' | 'recording' | 'paused' | 'finished';
const recState = ref<RecState>('idle');
const recSeconds = ref(0);
const recInterval = ref<ReturnType<typeof setInterval> | null>(null);

const recTimeDisplay = computed(() => {
  const h = Math.floor(recSeconds.value / 3600).toString().padStart(2, '0');
  const m = Math.floor((recSeconds.value % 3600) / 60).toString().padStart(2, '0');
  const s = (recSeconds.value % 60).toString().padStart(2, '0');
  return `${h}:${m}:${s}`;
});

const isRecording = computed(() => recState.value === 'recording');
const recordingStopped = computed(() => recState.value === 'finished');
const recordingTimeDisplay = recTimeDisplay;

function recTick() {
  recSeconds.value++;
  waveformBars.value = Array.from({ length: WAVE_COUNT }, () => Math.random() * 36 + 6);
}

function recStart() {
  if (recState.value === 'recording' || recState.value === 'finished') return;
  if (recState.value === 'idle') recSeconds.value = 0;
  recState.value = 'recording';
  aiPointsVisible.value = 0;
  if (recInterval.value) clearInterval(recInterval.value);
  recInterval.value = setInterval(recTick, 1000);
}

function recPause() {
  if (recState.value !== 'recording') return;
  recState.value = 'paused';
  if (recInterval.value) { clearInterval(recInterval.value); recInterval.value = null; }
}

function recStop() {
  if (recState.value !== 'recording' && recState.value !== 'paused') return;
  recState.value = 'finished';
  if (recInterval.value) { clearInterval(recInterval.value); recInterval.value = null; }
  waveformBars.value = Array.from({ length: WAVE_COUNT }, () => Math.random() * 20 + 8);
  let idx = 0;
  const iv = setInterval(() => {
    if (idx < AI_SUMMARY_POINTS.length) { aiPointsVisible.value = idx + 1; idx++; }
    else clearInterval(iv);
  }, 600);
}

function startRecording() { recStart(); }
function stopRecording() { recStop(); }

const aiPointsVisible = ref(0);
const AI_SUMMARY_POINTS = [
  '当前宏观环境支持适度提升权益配置比例，但需控制下行风险敞口',
  '利率下行趋势下，固收资产仍具配置价值，建议适度拉长久期',
  '黄金受地缘风险支撑，维持标配，关注美联储政策转向信号',
  '信用利差处于历史低位，需警惕信用事件风险，维持高等级配置',
  '建议加强组合流动性管理，预留充足安全垫应对潜在赎回压力',
  '委员会一致同意2026 Q3保持稳健偏积极的资产配置策略',
];

const chairmanInstruction = ref('');
const isIssued = ref(false);
const issuingLoading = ref(false);
const issuedTime = ref('');

function applyAIToInstruction() {
  const points = AI_SUMMARY_POINTS.slice(0, aiPointsVisible.value);
  if (points.length === 0) return;
  const suffix = points.map((p, i) => `${i + 1}. ${p}`).join('\n');
  chairmanInstruction.value = chairmanInstruction.value
    ? chairmanInstruction.value + '\n\n' + suffix
    : suffix;
}

function handleIssue() {
  if (isIssued.value || issuingLoading.value) return;
  if (!decisionSubmitted.value) return;
  issuingLoading.value = true;
  setTimeout(() => {
    issuingLoading.value = false;
    isIssued.value = true;
    markStepDone(4);
    issuedTime.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    const activeMeeting = meetingList.find(m => m.status === '已结束' || m.status === '进行中');
    if (activeMeeting) {
      activeMeeting.status = '已归档';
    }
  }, 2000);
}

onMounted(async () => {
  console.log(
    '%c🚀 [CommitteeView]',
    'color:#FF9500;font-weight:bold;font-size:12px',
    'onMounted → 加载会议列表 + 投委会数据',
  );
  await loadMeetings();
  void fetchCommitteePageData();
  void loadMixedSubmissions();
  void loadHistoryVotes();
  nowTickInterval = setInterval(() => { nowTick.value = new Date(); }, 30000);
  const activeMeeting = meetingList.find(m => m.status === '进行中');
  if (activeMeeting) {
    currentMeetingId.value = activeMeeting.id;
  }
});

watch(activeRole, () => {
  // eslint-disable-next-line no-console
  console.log('%c🚀 [CommitteeView]', 'color:#FF9500;font-weight:bold', 'activeRole 变化 → 重新拉取投委会数据');
  void fetchCommitteePageData();
});

onUnmounted(() => {
  if (recInterval.value) clearInterval(recInterval.value);
  if (nowTickInterval) clearInterval(nowTickInterval);
});
</script>

<style scoped>
.am-title-l2 {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.am-title-bar {
  width: 4px;
  height: 16px;
  border-radius: 9999px;
  background: #3B9EFF;
  flex-shrink: 0;
}
</style>