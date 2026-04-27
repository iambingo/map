<template>
  <div class="flex h-screen w-full bg-[#161922] overflow-hidden font-sans text-[#E8ECF4]">
    <!-- Sidebar (hidden on portal page) -->
    <aside
      v-if="activeTab !== 'portal'"
      :class="cn(
        'flex flex-col border-r border-[#2E3348] bg-[#1A1E2B] transition-all duration-300 ease-in-out z-20',
        isSidebarOpen ? 'w-56' : 'w-14'
      )"
    >
      <div class="flex h-10 items-center px-3 border-b border-[#2E3348]">
        <button
          @click="isSidebarOpen = !isSidebarOpen"
          class="p-1.5 rounded hover:bg-[#2A2E3D] text-[#8B93A8] transition-colors"
        >
          <Expand class="w-4 h-4" />
        </button>
        <span v-if="isSidebarOpen" class="ml-2.5 font-bold text-[#E8ECF4] tracking-widest text-[13px]">MAP.SYS</span>
      </div>

      <div class="flex-1 overflow-y-auto py-2 px-1.5 no-scrollbar">
        <!-- First group label -->
        <p v-if="isSidebarOpen" class="text-[9px] font-mono text-[#555E75] uppercase tracking-widest px-2 mb-1 mt-0.5">工作室</p>
        <template v-for="(item, idx) in navItems" :key="item.id">
          <!-- Group divider -->
          <div
            v-if="idx > 0 && item.group !== navItems[idx - 1].group"
            :class="cn('my-1.5 flex items-center', isSidebarOpen ? 'px-2' : 'justify-center')"
          >
            <div class="flex-1 h-px bg-[#252A3A]"></div>
            <span v-if="isSidebarOpen" class="mx-2 text-[9px] font-mono text-[#555E75] uppercase tracking-widest shrink-0">
              {{ item.group === 'ops' ? '业务流' : '系统' }}
            </span>
            <div class="flex-1 h-px bg-[#252A3A]"></div>
          </div>
          <!-- Nav button -->
          <button
            @click="activeTab = item.id"
            :class="cn(
              'flex items-center w-full px-2.5 py-2 rounded text-xs font-medium transition-colors mb-px',
              activeTab === item.id
                ? 'bg-[#3B9EFF]/12 text-[#3B9EFF] border border-[#3B9EFF]/25'
                : 'text-[#8B93A8] hover:bg-[#2A2E3D] hover:text-[#E8ECF4] border border-transparent',
              !isSidebarOpen && 'justify-center px-0'
            )"
            :title="!isSidebarOpen ? item.label : undefined"
          >
            <component :is="item.icon" :class="cn('w-4 h-4 shrink-0', activeTab === item.id ? 'text-[#3B9EFF]' : 'text-[#555E75]')" />
            <span v-if="isSidebarOpen" class="ml-2.5 truncate tracking-wide">{{ item.label }}</span>
          </button>
        </template>
      </div>

    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0 bg-[#161922]">
      <!-- Merged Header: Trapezoid Tabs (left) + Controls (right) -->
      <header class="h-10 flex items-stretch bg-[#1A1E2B] border-b border-[#2E3348] shrink-0 relative z-50">
        <!-- Left: Trapezoid Tabs -->
        <div class="flex items-stretch flex-1 overflow-x-auto overflow-y-hidden no-scrollbar">
          <div
            v-for="(tab, idx) in openTabs"
            :key="tab.id"
            :class="cn('tab-trap group', idx === 0 ? 'tab-trap-first' : '', activeTab === tab.id ? 'tab-trap-active' : '')"
            @click="activeTab = tab.id"
          >
            <!-- Nav icon → ✖ on tab hover -->
            <span class="relative w-3.5 h-3.5 shrink-0">
              <component :is="tab.icon" class="w-3.5 h-3.5 absolute inset-0 transition-opacity duration-150 group-hover:opacity-0" />
              <span
                class="absolute inset-0 flex items-center justify-center text-[10px] leading-none opacity-0 group-hover:opacity-100 transition-opacity duration-150 hover:text-[#F04864]"
                @click.stop="tab.id !== 'portal' && closeTab(tab.id)"
              >✖</span>
            </span>
            <span>{{ tab.label }}</span>
            <span v-if="activeTab === tab.id" class="ml-0.5 text-[9px] opacity-50" title="锁定标签">📌</span>
          </div>
        </div>

        <!-- Right: Controls -->
        <div class="flex items-center gap-1.5 px-3 shrink-0 border-l border-[#2E3348]">
          <!-- Search -->
          <div class="relative">
            <Search class="w-3 h-3 absolute left-2 top-1/2 -translate-y-1/2 text-[#555E75] pointer-events-none" />
            <input
              type="text"
              placeholder="Search (Ctrl+K)"
              class="h-6 w-36 pl-6 pr-2 text-[10px] bg-[#181C28] border border-[#2E3348] rounded text-[#E8ECF4] focus:outline-none focus:border-[#3B9EFF]/50 transition-all font-mono placeholder-[#555E75]"
            />
          </div>

          <!-- Notifications -->
          <button class="p-1 text-[#8B93A8] hover:text-[#E8ECF4] rounded hover:bg-[#2A2E3D] transition-colors relative" title="消息提醒">
            <Bell class="w-3.5 h-3.5" />
            <span class="absolute top-0.5 right-0.5 w-1.5 h-1.5 bg-[#F04864] rounded-full"></span>
          </button>

          <!-- Fullscreen -->
          <button
            @click="toggleFullscreen"
            class="p-1 text-[#8B93A8] hover:text-[#E8ECF4] rounded hover:bg-[#2A2E3D] transition-colors"
            title="全屏切换"
          >
            <FullScreen class="w-3.5 h-3.5" />
          </button>

          <!-- User Avatar — icon only, username in tooltip -->
          <div class="relative" @mouseenter="showUserMenu = true" @mouseleave="showUserMenu = false">
            <button
              class="w-6 h-6 rounded-full bg-gradient-to-br from-[#3B9EFF] to-[#22D3EE] flex items-center justify-center text-[10px] font-bold text-white hover:ring-2 hover:ring-[#3B9EFF]/50 transition-all"
              title="PM_01 | ID: 8942.A"
              ref="avatarBtnRef"
            >P</button>
          </div>
        </div>
      </header>

            <!-- Scrollable Content Area -->
      <div class="flex-1 overflow-y-auto p-3">
        <div class="max-w-[1680px] mx-auto min-h-full">
          <MapPortal v-if="activeTab === 'portal'" @navigate="activeTab = $event" />
          <ExecutiveDashboard v-else-if="activeTab === 'executive'" />
          <TerminalDashboard v-else-if="activeTab === 'terminal'" @navigate="activeTab = $event" />
          <CommitteeView v-else-if="activeTab === 'committee'" />
          <FiccCommitteeView v-else-if="activeTab === 'ficc-committee'" />
          <DeptHeadView v-else-if="activeTab === 'dept-head'" />
          <MarketView v-else-if="activeTab === 'market'" />
          <ModelCenterView v-else-if="activeTab === 'model-center'" />
          <SettingsView v-else-if="activeTab === 'settings'" />
          <ViewpointWorkshop v-else-if="activeTab === 'viewpoint'" />
          <FactorWorkshop v-else-if="activeTab === 'factor'" />
          <BatchSimulator v-else-if="activeTab === 'batch-simulator'" @navigate="activeTab = $event" />
          <div v-else class="flex h-full items-center justify-center text-[#555E75]">模块开发中...</div>
        </div>
      </div>
    </main>

    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-150 ease-out"
        enter-from-class="opacity-0 scale-95 -translate-y-1"
        enter-to-class="opacity-100 scale-100 translate-y-0"
        leave-active-class="transition-all duration-100 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95 -translate-y-1"
      >
        <div
          v-if="showUserMenu"
          ref="userMenuRef"
          class="fixed bg-[#202431] border border-[#2E3348] rounded-lg shadow-xl py-1"
          :style="userMenuStyle"
          @mouseenter="showUserMenu = true"
          @mouseleave="showUserMenu = false"
        >
          <div class="px-3 py-2 border-b border-[#2E3348]">
            <p class="text-xs font-semibold text-[#E8ECF4]">PM_01</p>
            <p class="text-[10px] text-[#555E75] font-mono">ID: 8942.A</p>
          </div>
          <div class="px-3 py-2 border-b border-[#2E3348] bg-[#161922]">
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-[10px] text-[#8B93A8]">演示视角切换</span>
              <span class="text-[8px] text-[#3B9EFF] border border-[#3B9EFF]/30 px-1 rounded">Demo</span>
            </div>
            <select v-model="activeRole" class="w-full bg-[#1A1E2B] text-[#E8ECF4] text-xs border border-[#2E3348] rounded px-1.5 py-1 outline-none cursor-pointer hover:border-[#3B9EFF]/50 transition-colors">
              <option v-for="role in ROLES" :key="role" :value="role">{{ role }}</option>
            </select>
          </div>
          <button class="w-full text-left px-3 py-1.5 text-xs text-[#8B93A8] hover:bg-[#2A2E3D] hover:text-[#E8ECF4] transition-colors">个人设置</button>
          <button class="w-full text-left px-3 py-1.5 text-xs text-[#8B93A8] hover:bg-[#2A2E3D] hover:text-[#E8ECF4] transition-colors">操作日志</button>
          <div class="border-t border-[#2E3348] mt-1 pt-1">
            <button class="w-full text-left px-3 py-1.5 text-xs text-[#F04864] hover:bg-[#2A2E3D] transition-colors">退出登录</button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import {
  DataBoard, DataLine, Setting, Search, Bell, User, Expand,
  Monitor, UserFilled, OfficeBuilding, Cpu, DataAnalysis, TrendCharts,
  ChatDotRound, Operation, Histogram, ArrowDown, FullScreen
} from '@element-plus/icons-vue';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { sharedIntentState } from './store/intentStore';
import { activeRole, ROLES } from './store/demoStore';

import MapPortal from './components/MapPortal.vue';
import ExecutiveDashboard from './components/ExecutiveDashboard.vue';
import TerminalDashboard from './components/TerminalDashboard.vue';
import CommitteeView from './components/CommitteeView.vue';
import FiccCommitteeView from './components/FiccCommitteeView.vue';
import DeptHeadView from './components/DeptHeadView.vue';
import MarketView from './components/MarketView.vue';
import ModelCenterView from './components/ModelCenterView.vue';
import SettingsView from './components/SettingsView.vue';
import ViewpointWorkshop from './components/ViewpointWorkshop.vue';
import FactorWorkshop from './components/FactorWorkshop.vue';
import BatchSimulator from './components/BatchSimulator.vue';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navItems = [
  { id: 'portal',       label: 'MAP门户',   icon: DataBoard,    group: 'labs'  },
  { id: 'viewpoint',    label: '观点车间',   icon: ChatDotRound, group: 'labs'  },
  { id: 'factor',       label: '因子车间',   icon: Histogram,    group: 'labs'  },
  { id: 'executive',    label: '总裁驾驶舱', icon: TrendCharts,  group: 'ops'   },
  { id: 'terminal',     label: '资配工作台', icon: Monitor,      group: 'ops'   },
  { id: 'committee',    label: '投委会决策', icon: UserFilled,   group: 'ops'   },
  { id: 'ficc-committee', label: 'FICC 委员会', icon: Histogram,  group: 'ops'   },
  { id: 'dept-head',    label: '部门决策',   icon: OfficeBuilding,group: 'ops'  },
  { id: 'batch-simulator', label: '调仓沙盘', icon: Operation,  group: 'ops'   },
  { id: 'market',       label: '市场洞察',   icon: DataLine,     group: 'ops'   },
  { id: 'model-center', label: '模型中心',   icon: Cpu,          group: 'ops'   },
  { id: 'data-center',  label: '数据中心',   icon: DataAnalysis, group: 'sys'   },
  { id: 'settings',     label: '系统设置',   icon: Setting,      group: 'sys'   },
];

const TAB_STORAGE_KEY = 'map_active_tab';

function readPersistedTab(): string {
  try {
    const raw = sessionStorage.getItem(TAB_STORAGE_KEY);
    if (raw && navItems.some((n) => n.id === raw)) return raw;
  } catch {
    /* 隐私模式等 */
  }
  return 'portal';
}

const initialActiveTab = readPersistedTab();
const activeTab = ref(initialActiveTab);
const isSidebarOpen = ref(false);
const showUserMenu = ref(false);

const avatarBtnRef = ref<HTMLElement | null>(null);
const userMenuRef = ref<HTMLElement | null>(null);
const userMenuStyle = computed(() => {
  const btn = avatarBtnRef.value;
  if (!btn) return {};
  const r = btn.getBoundingClientRect();
  return { top: `${r.bottom + 4}px`, right: `${window.innerWidth - r.right}px` };
});

const globalDate = (() => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
})();

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
}

watch(() => sharedIntentState.navigationTarget, (target) => {
  if (target) {
    activeTab.value = target;
    sharedIntentState.navigationTarget = null;
  }
});

const openTabIds = ref<string[]>(
  initialActiveTab === 'portal' ? ['portal'] : ['portal', initialActiveTab].filter((v, i, a) => a.indexOf(v) === i),
);

watch(activeTab, (newTab) => {
  try {
    sessionStorage.setItem(TAB_STORAGE_KEY, newTab);
  } catch {
    /* ignore */
  }
  if (!openTabIds.value.includes(newTab)) {
    openTabIds.value.push(newTab);
  }
}, { immediate: true });

const openTabs = computed(() => {
  return openTabIds.value
    .map(id => navItems.find(n => n.id === id))
    .filter(Boolean) as typeof navItems;
});

function closeTab(tabId: string) {
  const idx = openTabIds.value.indexOf(tabId);
  if (idx === -1) return;
  openTabIds.value.splice(idx, 1);
  if (activeTab.value === tabId) {
    const fallback = openTabIds.value[openTabIds.value.length - 1] || 'portal';
    activeTab.value = fallback;
  }
}
</script>
