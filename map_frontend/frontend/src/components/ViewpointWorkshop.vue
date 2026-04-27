<template>
  <div class="flex h-full bg-[#161922] text-[#E8ECF4] overflow-hidden font-sans">

    <!-- ═══ LEFT SIDEBAR ═══ -->
    <div class="w-64 bg-[#161922] border-r border-[#252A3A] flex flex-col shrink-0 shadow-[4px_0_24px_rgba(0,0,0,0.5)]">

      <!-- Back + Title -->
      <div class="px-4 pt-3 pb-0 bg-gradient-to-b from-[#252A3A] to-[#1A1E2B]">
        <button
          @click="sharedIntentState.navigationTarget = 'portal'"
          class="flex items-center text-[#4A5568] hover:text-[#B4BAC9] transition-all duration-150 text-xs font-mono group mb-2.5"
        >
          <ArrowLeft class="w-3 h-3 mr-1 group-hover:-translate-x-0.5 transition-transform duration-150" />
          门户枢纽
        </button>
      </div>
      <div class="px-4 pb-4 border-b border-[#252A3A] flex items-center space-x-3 bg-gradient-to-b from-[#1A1E2B] to-[#161922]">
        <div class="w-8 h-8 rounded bg-purple-900/30 border border-purple-500/30 flex items-center justify-center shadow-[0_0_12px_rgba(168,85,247,0.15)]">
          <EditPen class="w-[15px] h-[15px] text-purple-400" />
        </div>
        <div>
          <h2 class="text-[15px] font-bold text-white tracking-wider">观点车间</h2>
          <p class="text-[10px] text-purple-400/60 font-mono uppercase tracking-widest">Viewpoint Workshop</p>
        </div>
      </div>

      <!-- Search -->
      <div class="p-3 border-b border-[#1A1E2B]">
        <div class="flex items-center bg-[#1A1E2B] border border-[#2A2F40] rounded-lg px-2.5 py-1.5 space-x-2 focus-within:border-purple-500/40 transition-colors duration-200">
          <Search class="w-3 h-3 text-[#4A5568] shrink-0" />
          <input
            v-model="searchQuery"
            placeholder="搜索观点..."
            class="bg-transparent text-[#E8ECF4] text-[13px] outline-none placeholder-[#3E4660] w-full font-mono"
          />
        </div>
      </div>

      <!-- View Navigation -->
      <div class="p-2 space-y-0.5">
        <p class="text-[10px] font-mono text-[#7B8BA3] uppercase tracking-widest px-2 py-1.5">视图导航</p>
        <button
          v-for="nav in navItems" :key="nav.id"
          @click="selectedNav = nav.id; viewMode = 'feed'"
          :class="cn(
            'w-full flex items-center space-x-2.5 px-2.5 py-2 rounded-lg text-[13px] font-medium transition-all duration-150 group',
            selectedNav === nav.id
              ? 'bg-purple-500/10 text-purple-300 border border-purple-500/20'
              : 'text-[#6B7280] hover:bg-[#1A1E2B] hover:text-[#B4BAC9] border border-transparent'
          )"
        >
          <component
            :is="nav.icon"
            :class="cn('w-3.5 h-3.5 shrink-0', selectedNav === nav.id ? 'text-purple-400' : 'text-[#4A5568] group-hover:text-[#6B7280]')"
          />
          <span class="flex-1 text-left">{{ nav.label }}</span>
          <span
            v-if="nav.count"
            :class="cn('text-[11px] font-mono px-1.5 py-1 rounded-full', selectedNav === nav.id ? 'bg-purple-500/20 text-purple-300' : 'bg-[#2A2D3A] text-[#94A3B8]')"
          >{{ nav.count }}</span>
        </button>
      </div>

      <!-- New Button -->
      <div class="px-3 py-2 border-t border-[#1A1E2B] mt-1">
        <button
          @click="openEditor"
          class="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 hover:shadow-[0_0_20px_rgba(168,85,247,0.3)] text-white text-[13px] font-bold transition-all duration-200"
        >
          <Plus class="w-3.5 h-3.5" />
          <span>新建观点</span>
        </button>
      </div>

      <!-- Hot Tags -->
      <div class="p-3 border-t border-[#1A1E2B] mt-auto">
        <p class="text-[10px] font-mono text-[#7B8BA3] uppercase tracking-widest px-1 mb-2">热门标签</p>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="tag in hotTags" :key="tag.label"
            @click="activeTag = activeTag === tag.label ? null : tag.label"
            :class="cn(
              'text-[11px] px-2 py-1 rounded-md font-mono transition-all duration-150',
              activeTag === tag.label
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                : 'bg-[#1A1E2B] text-[#94A3B8] border border-[#252A3A] hover:text-[#B4BAC9] hover:border-[#2E3348]'
            )"
          >#{{ tag.label }} <span class="opacity-40 ml-0.5">{{ tag.count }}</span></button>
        </div>
      </div>
    </div>

    <!-- ═══ RIGHT MAIN AREA ═══ -->
    <div class="flex-1 flex flex-col overflow-hidden">

      <!-- Toolbar -->
      <div class="bg-[#161922] border-b border-[#252A3A] px-6 py-3 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-3">
          <h3 class="text-[15px] font-bold text-[#E8ECF4]">
            {{ viewMode === 'editor' ? '✍️ 编辑新观点' : currentNavLabel }}
          </h3>
          <div v-if="viewMode === 'feed'" class="flex items-center space-x-1 bg-[#1A1E2B] border border-[#2A2F40] rounded-lg p-0.5">
            <button
              v-for="s in sortOptions" :key="s.id"
              @click="activeSortId = s.id"
              :class="cn('px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-150', activeSortId === s.id ? 'bg-[#2A2F40] text-white' : 'text-[#94A3B8] hover:text-[#B4BAC9]')"
            >{{ s.label }}</button>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <template v-if="viewMode === 'editor'">
            <button @click="viewMode = 'feed'" class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-[13px] text-[#94A3B8] hover:text-[#B4BAC9] hover:bg-[#1A1E2B] border border-transparent hover:border-[#2A2F40] transition-all duration-150">
              <Close class="w-3 h-3" /><span>取消</span>
            </button>
            <button @click="publishViewpoint" class="flex items-center space-x-1.5 px-4 py-1.5 rounded-lg text-[13px] font-bold bg-purple-600 hover:bg-purple-500 hover:shadow-[0_0_15px_rgba(168,85,247,0.3)] text-white transition-all duration-200">
              <Promotion class="w-3 h-3" /><span>发布观点</span>
            </button>
          </template>
          <span v-else class="text-[11px] font-mono text-[#7B8BA3]">{{ filteredViewpoints.length }} 篇观点</span>
        </div>
      </div>

      <!-- ── EDITOR ── -->
      <div v-if="viewMode === 'editor'" class="flex-1 overflow-y-auto no-scrollbar">
        <div class="max-w-3xl mx-auto px-8 py-10">

          <input
            v-model="editorTitle"
            placeholder="观点标题..."
            class="w-full bg-transparent text-[#E8ECF4] text-3xl font-bold outline-none placeholder-[#2E3348] mb-2 tracking-tight leading-tight"
          />

          <div class="flex items-center space-x-3 mb-8 pb-4 border-b border-[#1A1E2B]">
            <span class="text-[11px] font-mono text-[#7B8BA3]">{{ todayStr }}</span>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="t in selectedTags" :key="t"
                class="flex items-center text-[11px] font-mono text-purple-400 bg-purple-400/10 border border-purple-400/20 px-2 py-1 rounded-full"
              >
                #{{ t }}
                <button @click="removeTag(t)" class="ml-1 text-purple-400/50 hover:text-purple-300 transition-colors">
                  <Close class="w-2.5 h-2.5" />
                </button>
              </span>
              <button
                @click="showTagPicker = !showTagPicker"
                class="text-[11px] font-mono text-[#4A5568] border border-[#2A2F40] px-2 py-1 rounded-full hover:border-purple-500/30 hover:text-purple-400 transition-all duration-150"
              >+ 添加标签</button>
            </div>
          </div>

          <!-- Tag Picker -->
          <div v-if="showTagPicker" class="mb-4 bg-[#1A1E2B] border border-[#2A2F40] rounded-xl p-3 flex flex-wrap gap-1.5 shadow-[0_8px_30px_rgba(0,0,0,0.6)]">
            <button
              v-for="tag in hotTags" :key="tag.label"
              @click="toggleEditorTag(tag.label)"
              :class="cn('text-[11px] font-mono px-2 py-1 rounded-md transition-all duration-150', selectedTags.includes(tag.label) ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'bg-[#1A1E2B] text-[#94A3B8] border border-[#252A3A] hover:text-purple-400 hover:border-purple-500/20')"
            >#{{ tag.label }}</button>
          </div>

          <!-- Block Editor -->
          <div class="space-y-1 relative min-h-[200px]">
            <p v-if="allBlocksEmpty" class="absolute left-2 top-1 pointer-events-none text-[#2A2F40] text-[15px] font-mono select-none">
              敲击 "/" 呼出 AI 助手或插入投研组件 (图表 / 指标)
            </p>
            <div
              v-for="(block, idx) in editorBlocks" :key="block.id"
              class="relative flex items-start group"
              @mouseenter="hoveredBlockId = block.id"
              @mouseleave="hoveredBlockId = null"
            >
              <!-- Grip handle -->
              <div :class="cn('absolute -left-6 top-2 cursor-grab text-[#64748B] hover:text-[#94A3B8] transition-all duration-150', hoveredBlockId === block.id ? 'opacity-100' : 'opacity-0')">
                <svg viewBox="0 0 10 16" fill="currentColor" class="w-2.5 h-3.5">
                  <circle cx="2"  cy="2"  r="1.3"/><circle cx="8"  cy="2"  r="1.3"/>
                  <circle cx="2"  cy="8"  r="1.3"/><circle cx="8"  cy="8"  r="1.3"/>
                  <circle cx="2"  cy="14" r="1.3"/><circle cx="8"  cy="14" r="1.3"/>
                </svg>
              </div>
              <!-- Type badge -->
              <div
                v-if="block.type !== 'p'"
                :class="cn('shrink-0 text-[10px] font-mono px-1.5 py-1 rounded mr-2 mt-1.5 uppercase tracking-wider', block.type === 'h2' ? 'text-purple-400 bg-purple-400/10' : 'text-[#3B9EFF] bg-[#3B9EFF]/10')"
              >{{ block.type === 'h2' ? 'H2' : 'QUOTE' }}</div>
              <textarea
                v-model="block.content"
                :placeholder="block.placeholder"
                :class="cn('flex-1 bg-transparent outline-none resize-none leading-relaxed placeholder-[#2A2F40] border border-transparent rounded-lg px-2 py-1 transition-all duration-150 focus:bg-[#1A1E2B] focus:border-[#2A2F40]',
                  block.type === 'h2' ? 'text-lg font-bold text-white' : 'text-[15px] text-[#B8BFCC]',
                  hoveredBlockId === block.id ? 'bg-[#161922]' : ''
                )"
                rows="1"
                @input="autoResize($event)"
                @keydown.enter.prevent="addBlockAfter(idx)"
              />
              <span v-if="!block.content && hoveredBlockId === block.id" class="absolute right-3 top-2 text-[11px] font-mono text-[#2A2F40] pointer-events-none">/ 插入</span>
            </div>
          </div>

          <!-- AI hint footer -->
          <div class="mt-10 flex items-center space-x-3 text-[#252A3A] text-[13px] font-mono select-none">
            <Lightning class="w-3.5 h-3.5" />
            <span>AI 助手已就绪 · 输入 <kbd class="bg-[#1A1E2B] border border-[#2A2F40] px-1.5 py-1 rounded text-[#7B8BA3]">/</kbd> 呼出 · 支持：📊 插入图表 · 📈 引用指标 · 🔗 关联历史观点</span>
          </div>
        </div>
      </div>

      <!-- ── FEED ── -->
      <div v-else class="flex-1 overflow-y-auto no-scrollbar">
        <div class="max-w-3xl mx-auto px-6 py-6 space-y-4">

          <!-- Tag filter banner -->
          <div v-if="activeTag" class="flex items-center space-x-2 bg-purple-500/5 border border-purple-500/20 rounded-xl px-4 py-2.5">
            <PriceTag class="w-3.5 h-3.5 text-purple-400" />
            <span class="text-[13px] text-purple-300 font-mono">筛选中: #{{ activeTag }}</span>
            <button @click="activeTag = null" class="ml-auto text-purple-400/40 hover:text-purple-300 transition-colors">
              <Close class="w-3.5 h-3.5" />
            </button>
          </div>

          <!-- Viewpoint cards -->
          <div
            v-for="vp in filteredViewpoints" :key="vp.id"
            class="bg-[#1A1E2B] border border-[#252A3A] rounded-xl overflow-hidden hover:border-[#2E3348] hover:shadow-[0_8px_40px_rgba(0,0,0,0.5)] transition-all duration-200 group"
          >
            <!-- Card header -->
            <div class="px-5 pt-4 pb-3 border-b border-[#1A1E2B]">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center space-x-3">
                  <div :class="cn('w-8 h-8 rounded-full flex items-center justify-center text-[15px] font-bold shrink-0', vp.avatarColor)">
                    {{ vp.author.charAt(0) }}
                  </div>
                  <div>
                    <p class="text-[13px] font-bold text-[#E8ECF4]">{{ vp.author }}</p>
                    <p class="text-[11px] text-[#4A5568] font-mono mt-0.5">{{ vp.role }} · {{ vp.timestamp }}</p>
                  </div>
                </div>
                <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button class="text-[#7B8BA3] hover:text-[#B4BAC9] p-1 rounded hover:bg-[#2A2D3A] transition-colors">
                    <Share class="w-3.5 h-3.5" />
                  </button>
                  <button class="text-[#7B8BA3] hover:text-[#B4BAC9] p-1 rounded hover:bg-[#2A2D3A] transition-colors">
                    <MoreFilled class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
              <h3 class="text-[15px] font-bold text-white leading-snug mb-2 cursor-pointer group-hover:text-purple-100 transition-colors duration-200">
                {{ vp.title }}
              </h3>
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="tag in vp.tags" :key="tag"
                  @click.stop="activeTag = tag"
                  class="text-[11px] font-mono text-blue-400 bg-blue-400/10 border border-blue-400/15 px-2 py-1 rounded-md cursor-pointer hover:bg-blue-400/20 transition-all duration-150"
                >#{{ tag }}</span>
              </div>
            </div>

            <!-- Card body -->
            <div class="px-5 py-3">
              <p class="text-[13px] text-[#B4BAC9] leading-relaxed line-clamp-3">{{ vp.summary }}</p>
              <div v-if="vp.highlight" class="mt-3 flex items-start space-x-2.5 bg-[#161922] border-l-2 border-purple-500/50 rounded-r-lg px-3 py-2">
                <Lightning class="w-3 h-3 text-purple-400 shrink-0 mt-0.5" />
                <p class="text-xs text-[#B4BAC9] italic leading-relaxed">{{ vp.highlight }}</p>
              </div>
            </div>

            <!-- Card footer -->
            <div class="px-5 py-2.5 border-t border-[#1A1E2B] flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <button
                  @click="toggleLike(vp.id)"
                  :class="cn('flex items-center space-x-1.5 text-xs font-mono transition-all duration-150 group/lb', likedIds.has(vp.id) ? 'text-red-400' : 'text-[#4A5568] hover:text-red-400')"
                >
                  <StarFilled v-if="likedIds.has(vp.id)" class="w-3.5 h-3.5 group-hover/lb:scale-110 transition-transform" />
                  <Star v-else class="w-3.5 h-3.5 group-hover/lb:scale-110 transition-transform" />
                  <span>{{ likedIds.has(vp.id) ? vp.likes + 1 : vp.likes }}</span>
                </button>
                <button class="flex items-center space-x-1.5 text-xs font-mono text-[#4A5568] hover:text-[#3B9EFF] transition-colors duration-150">
                  <ChatDotRound class="w-3.5 h-3.5" />
                  <span>{{ vp.comments }}</span>
                </button>
                <span class="flex items-center space-x-1.5 text-xs font-mono text-[#7B8BA3]">
                  <View class="w-3.5 h-3.5" />
                  <span>{{ vp.views }}</span>
                </span>
              </div>
              <div :class="cn('flex items-center space-x-1.5 text-[11px] font-mono px-2.5 py-1 rounded-full border', vp.sentiment === 'bullish' ? 'text-green-400 bg-green-400/5 border-green-400/20' : vp.sentiment === 'bearish' ? 'text-red-400 bg-red-400/5 border-red-400/20' : 'text-[#B4BAC9] bg-[#1A1E2B] border-[#2A2F40]')">
                <span>{{ vp.sentiment === 'bullish' ? '▲ 看多' : vp.sentiment === 'bearish' ? '▼ 看空' : '— 中性' }}</span>
                <span class="opacity-50 ml-1">{{ vp.confidence }}%</span>
              </div>
            </div>
          </div>

          <!-- Empty state -->
          <div v-if="filteredViewpoints.length === 0" class="py-20 flex flex-col items-center space-y-4">
            <div class="w-16 h-16 rounded-2xl bg-[#1A1E2B] border border-[#252A3A] flex items-center justify-center">
              <EditPen class="w-7 h-7 text-[#7B8BA3]" />
            </div>
            <div class="text-center">
              <p class="text-[15px] text-[#94A3B8]">暂无匹配的观点</p>
              <p class="text-[13px] text-[#7B8BA3] mt-1 font-mono">
                <button @click="openEditor" class="text-purple-400 hover:text-purple-300 transition-colors">新建一篇观点</button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0 translate-y-4"
      >
        <div v-if="showToast" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[9999] bg-[#1A1E2B] border border-purple-500/30 shadow-[0_0_40px_rgba(168,85,247,0.2)] rounded-xl px-5 py-3 flex items-center space-x-3 pointer-events-none">
          <CircleCheckFilled class="w-4 h-4 text-purple-400 shrink-0" />
          <span class="text-[13px] font-medium text-[#E8ECF4]">{{ toastMsg }}</span>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  ArrowLeft, EditPen, Search, Plus, Close, Promotion, Share, Lightning,
  Star, StarFilled, View, CircleCheckFilled, ChatDotRound, MoreFilled,
  Document, UserFilled, PriceTag,
} from '@element-plus/icons-vue';
import { sharedIntentState } from '../store/intentStore';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

// ── Types ─────────────────────────────────────────────────────────────────────
type Sentiment = 'bullish' | 'bearish' | 'neutral';
type BlockType  = 'h2' | 'p' | 'quote';

interface Block {
  id: number;
  type: BlockType;
  content: string;
  placeholder: string;
}

interface Viewpoint {
  id: number;
  author: string;
  role: string;
  avatarColor: string;
  timestamp: string;
  title: string;
  tags: string[];
  summary: string;
  highlight: string | null;
  likes: number;
  comments: number;
  views: number;
  sentiment: Sentiment;
  confidence: number;
}

// ── Nav items ──────────────────────────────────────────────────────────────────
const navItems = [
  { id: 'all',   label: '全部观点', icon: Document,   count: 12 },
  { id: 'mine',  label: '我的观点', icon: UserFilled,  count: 4  },
  { id: 'draft', label: '我的草稿', icon: EditPen,     count: 1  },
  { id: 'hot',   label: '热门讨论', icon: ChatDotRound,count: 8  },
];
const selectedNav   = ref('all');
const activeSortId  = ref('latest');
const sortOptions   = [
  { id: 'latest',  label: '最新' },
  { id: 'popular', label: '热门' },
];
const currentNavLabel = computed(() => navItems.find(n => n.id === selectedNav.value)?.label ?? '全部观点');

// ── Tags ───────────────────────────────────────────────────────────────────────
const hotTags = [
  { label: '宏观研判',  count: 18 },
  { label: '固收+策略', count: 14 },
  { label: '降息预期',  count: 11 },
  { label: '港股科技',  count: 9  },
  { label: 'A股红利',   count: 7  },
  { label: '资产配置',  count: 6  },
  { label: '信用债',    count: 5  },
];
const activeTag     = ref<string | null>(null);
const selectedTags  = ref<string[]>([]);
const showTagPicker = ref(false);

function toggleEditorTag(tag: string) {
  const idx = selectedTags.value.indexOf(tag);
  idx === -1 ? selectedTags.value.push(tag) : selectedTags.value.splice(idx, 1);
}
function removeTag(tag: string) {
  selectedTags.value = selectedTags.value.filter(t => t !== tag);
}

// ── Editor ──────────────────────────────────────────────────────────────────────
const viewMode    = ref<'feed' | 'editor'>('feed');
const editorTitle = ref('');
const hoveredBlockId = ref<number | null>(null);
let _blockSeed = 100;
const todayStr = new Date().toLocaleDateString('zh-CN');

const editorBlocks = ref<Block[]>([
  { id: 1, type: 'h2',   content: '', placeholder: '一级小标题...' },
  { id: 2, type: 'p',    content: '', placeholder: '在这里写下你的核心论点...' },
  { id: 3, type: 'p',    content: '', placeholder: '继续展开...' },
  { id: 4, type: 'quote',content: '', placeholder: '引用关键数据或原文...' },
]);

const allBlocksEmpty = computed(() => editorBlocks.value.every(b => !b.content));

function openEditor() {
  viewMode.value = 'editor';
}

function addBlockAfter(idx: number) {
  editorBlocks.value.splice(idx + 1, 0, {
    id: ++_blockSeed, type: 'p', content: '', placeholder: '继续写...',
  });
}

function autoResize(e: Event) {
  const el = e.target as HTMLTextAreaElement;
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
}

// ── Toast ──────────────────────────────────────────────────────────────────────
const showToast = ref(false);
const toastMsg  = ref('');
let _toastTimer: ReturnType<typeof setTimeout> | null = null;
function fireToast(msg: string) {
  toastMsg.value = msg;
  showToast.value = true;
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { showToast.value = false; }, 3000);
}

// ── Publish ────────────────────────────────────────────────────────────────────
function publishViewpoint() {
  if (!editorTitle.value.trim()) { fireToast('请先填写观点标题'); return; }
  const bodyText = editorBlocks.value.map(b => b.content).filter(Boolean).join(' ').slice(0, 120);
  const newVp: Viewpoint = {
    id: Date.now(),
    author: '张伟（我）',
    role: '固收+投资经理',
    avatarColor: 'bg-purple-600/80 text-purple-200',
    timestamp: '刚刚',
    title: editorTitle.value,
    tags: [...selectedTags.value],
    summary: bodyText || '（暂无正文内容）',
    highlight: null,
    likes: 0, comments: 0, views: 1,
    sentiment: 'neutral',
    confidence: 50,
  };
  viewpoints.value.unshift(newVp);
  // reset
  editorTitle.value = '';
  selectedTags.value = [];
  showTagPicker.value = false;
  editorBlocks.value = [
    { id: ++_blockSeed, type: 'h2', content: '', placeholder: '一级小标题...' },
    { id: ++_blockSeed, type: 'p',  content: '', placeholder: '在这里写下你的核心论点...' },
  ];
  viewMode.value = 'feed';
  fireToast('✅ 观点已成功发布');
}

// ── Like ──────────────────────────────────────────────────────────────────────
const likedIds = ref<Set<number>>(new Set());
function toggleLike(id: number) {
  const s = new Set(likedIds.value);
  s.has(id) ? s.delete(id) : s.add(id);
  likedIds.value = s;
}

// ── Search / Filter ────────────────────────────────────────────────────────────
const searchQuery = ref('');

// ── Mock data ──────────────────────────────────────────────────────────────────
const viewpoints = ref<Viewpoint[]>([
  {
    id: 1,
    author: '李明',
    role: '固收+投资经理',
    avatarColor: 'bg-blue-700/80 text-blue-200',
    timestamp: '2 小时前',
    title: '当前时点固收+品种的仓位思路：拥抱哑铃两端',
    tags: ['固收+策略', '信用债', 'A股红利'],
    summary: '在利率快速下行的背景下，纯债端的利差保护已经非常薄弱。与其在中间追信用，不如走"哑铃"策略：短端用高流动性的国债/存单打底，权益端精选红利低波，以股息率对冲久期风险。当前 10 年期国债收益率已突破 2.0%，我认为进一步下行空间有限，应将久期控制在 3 年以内。',
    highlight: '核心结论：将组合久期从 4.2 年压缩至 2.8 年，同步将红利权益仓位从 8% 提升至 12%。',
    likes: 14, comments: 6, views: 238,
    sentiment: 'bullish', confidence: 72,
  },
  {
    id: 2,
    author: '王芳',
    role: '宏观策略研究员',
    avatarColor: 'bg-emerald-700/80 text-emerald-200',
    timestamp: '昨天 09:41',
    title: '美联储降息路径重估：2026 年或只剩 1 次',
    tags: ['宏观研判', '降息预期'],
    summary: '近两周公布的非农就业数据持续超预期，叠加 CPI 通胀粘性，市场已大幅修正联储降息预期。CME FedWatch 显示 2026 年全年降息次数中位数从年初的 3 次降至当前的 1 次。这对国内资产的影响主要体现在：人民币贬值压力缓和，但外资流入固收资产的动力也相应减弱。',
    highlight: '关键风险点：若 4 月 CPI 再度超预期，降息预期可能彻底归零，届时美债收益率将重新测试 4.8% 阻力位。',
    likes: 21, comments: 9, views: 412,
    sentiment: 'bearish', confidence: 68,
  },
  {
    id: 3,
    author: '赵晨',
    role: '权益研究员',
    avatarColor: 'bg-orange-700/80 text-orange-200',
    timestamp: '3 天前',
    title: '港股科技的困境反转：AI 算力链是唯一确定性主线',
    tags: ['港股科技', '宏观研判', '资产配置'],
    summary: '港股恒生科技年初至今已反弹 18%，但成交量并未跟上，表明市场情绪仍处于"半信半疑"阶段。我认为 AI 算力链是当前港股唯一具备基本面支撑的主线——以英伟达为核心的全球算力军备竞赛仍在加速，而港股中的算力相关标的估值相较 A股折价明显。短期关注 GPU 服务器出货数据。',
    highlight: null,
    likes: 8, comments: 12, views: 189,
    sentiment: 'bullish', confidence: 61,
  },
]);

const filteredViewpoints = computed<Viewpoint[]>(() => {
  let result = viewpoints.value;
  if (activeTag.value) {
    result = result.filter(vp => vp.tags.includes(activeTag.value!));
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(vp =>
      vp.title.toLowerCase().includes(q) ||
      vp.summary.toLowerCase().includes(q) ||
      vp.tags.some(t => t.toLowerCase().includes(q))
    );
  }
  if (activeSortId.value === 'popular') {
    result = [...result].sort((a, b) => (b.likes + b.comments) - (a.likes + a.comments));
  }
  return result;
});
</script>
