<template>
  <div class="flex h-full bg-[#161922] text-[#E8ECF4] overflow-hidden font-sans">
    <!-- Left Navigation -->
    <div class="w-56 bg-[#161922] border-r border-[#2E3348] flex flex-col shrink-0 z-20 shadow-[4px_0_24px_rgba(0,0,0,0.5)]">
      <div class="p-4 border-b border-[#2E3348] flex items-center space-x-3 bg-[#1A1E2B]">
        <div class="w-8 h-8 rounded bg-blue-900/30 border border-blue-500/50 flex items-center justify-center">
          <SettingsIcon class="w-4 h-4 text-blue-500" />
        </div>
        <div>
          <h2 class="am-title-l1"><div class="am-title-bar"></div>系统配置</h2>
          <p class="text-[11px] text-blue-500/70 font-mono uppercase">Admin Center</p>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto py-4 space-y-1">
        <button
          v-for="item in leftNavItems" :key="item.id"
          @click="activeNav = item.id"
          :class="cn(
            'w-full text-left px-4 py-3 text-[13px] font-medium transition-all flex items-center border-l-2',
            activeNav === item.id ? 'bg-[#2A2D3A] text-white border-blue-500' : 'text-[#B4BAC9] hover:bg-[#1A1E2B] hover:text-[#B4BAC9] border-transparent'
          )"
        >
          <component :is="item.icon" :class="cn('w-4 h-4 mr-3', activeNav === item.id ? 'text-blue-500' : '')" />
          {{ item.label }}
        </button>
      </div>
    </div>

    <!-- Right Workspace -->
    <div class="flex-1 relative overflow-hidden bg-[#161922]">
      <!-- IAM -->
      <div v-if="activeNav === 'iam'" class="flex flex-1 h-full overflow-hidden">
        <!-- Column 1: User Groups -->
        <div class="w-1/3 border-r border-[#2E3348] flex flex-col bg-[#161922]">
          <div class="p-3 border-b border-[#2E3348] bg-[#1A1E2B] flex justify-between items-center shrink-0">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>用户组 (Group)</h3>
            <button class="text-[#B4BAC9] hover:text-blue-400 transition-colors"><Plus class="w-4 h-4" /></button>
          </div>
          <div class="p-2">
            <div class="relative mb-2">
              <Search class="w-3.5 h-3.5 absolute left-2.5 top-2 text-[#94A3B8]" />
              <input type="text" placeholder="搜索用户组..." class="w-full operable-zone rounded pl-8 pr-2 py-1.5 text-[13px] text-[#E8ECF4] focus:outline-none" />
            </div>
          </div>
          <div class="flex-1 overflow-y-auto p-2 space-y-1">
            <button
              v-for="group in userGroups" :key="group.id"
              @click="activeGroup = group.id"
              :class="cn(
                'w-full text-left px-3 py-2.5 rounded text-[13px] flex items-center justify-between group transition-colors',
                activeGroup === group.id ? 'bg-blue-900/20 text-blue-400 border border-blue-900/50' : 'text-[#B4BAC9] hover:bg-[#2A2D3A] border border-transparent'
              )"
            >
              <div class="flex items-center">
                <span :class="cn('w-1.5 h-1.5 rounded-full mr-2', group.type === 'builtin' ? 'bg-blue-500' : 'bg-green-500')" />
                {{ group.name }}
              </div>
              <ArrowRight :class="cn('w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity', activeGroup === group.id && 'opacity-100')" />
            </button>
          </div>
        </div>

        <!-- Column 2: Roles -->
        <div class="w-1/3 border-r border-[#2E3348] flex flex-col bg-[#161922]">
          <div class="p-3 border-b border-[#2E3348] bg-[#1A1E2B] flex justify-between items-center shrink-0">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>角色权限 (Role)</h3>
            <span class="text-[11px] text-[#B4BAC9] bg-[#2E3348] px-2 py-1 rounded">功能级</span>
          </div>
          <div class="flex-1 overflow-y-auto p-4">
            <div class="space-y-4">
              <div v-for="module in roleTree" :key="module.id" class="space-y-2">
                <div class="flex items-center text-[13px] text-[#E8ECF4] font-medium">
                  <Select v-if="module.checked" class="w-3.5 h-3.5 mr-2 text-green-500" />
                  <SemiSelect v-else class="w-3.5 h-3.5 mr-2 text-[#94A3B8]" />
                  {{ module.name }}
                </div>
                <div class="pl-6 space-y-2 border-l border-[#3E4660] ml-1.5">
                  <div v-for="child in module.children" :key="child.id" class="flex items-center text-[13px] text-[#B4BAC9]">
                    <Select v-if="child.checked" class="w-3.5 h-3.5 mr-2 text-green-500" />
                    <SemiSelect v-else class="w-3.5 h-3.5 mr-2 text-[#94A3B8]" />
                    {{ child.name }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Column 3: Security Class -->
        <div class="w-1/3 flex flex-col bg-[#161922]">
          <div class="p-3 border-b border-[#2E3348] bg-[#1A1E2B] flex justify-between items-center shrink-0">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>安全类 (Security Class)</h3>
            <span class="text-[11px] text-red-400 bg-red-900/30 border border-red-900/50 px-2 py-1 rounded">数据级核心</span>
          </div>
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div
              v-for="sec in securityClasses" :key="sec.id"
              :class="cn('p-3 rounded-lg border cursor-pointer transition-colors', sec.selected ? 'bg-red-900/10 border-red-500/50' : 'bg-[#1A1E2B] border-[#3E4660] hover:border-[#555E75]')"
            >
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center text-[13px] font-medium text-[#E8ECF4]">
                  <div :class="cn('w-3 h-3 rounded-full border mr-2 flex items-center justify-center', sec.selected ? 'border-red-500' : 'border-[#555E75]')">
                    <div v-if="sec.selected" class="w-1.5 h-1.5 rounded-full bg-red-500" />
                  </div>
                  {{ sec.name }}
                </div>
              </div>
              <p class="text-[11px] text-[#B4BAC9] pl-5 leading-relaxed">{{ sec.desc }}</p>
            </div>
          </div>
          <div class="p-4 border-t border-[#2E3348] bg-[#1A1E2B] shrink-0">
            <button class="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-[13px] font-bold rounded flex items-center justify-center transition-colors shadow-[0_0_10px_rgba(37,99,235,0.2)]">
              <DocumentAdd class="w-3.5 h-3.5 mr-2" /> 保存权限配置
            </button>
          </div>
        </div>
      </div>

      <!-- MDM -->
      <div v-if="activeNav === 'mdm'" class="flex flex-col h-full overflow-hidden bg-[#161922]">
        <div class="flex border-b border-[#2E3348] bg-[#1A1E2B] shrink-0 px-2 pt-2">
          <button
            v-for="tab in mdmTabs" :key="tab.id"
            @click="activeMdmTab = tab.id"
            :class="cn(
              'px-4 py-2.5 text-[13px] font-medium flex items-center border-b-2 transition-colors',
              activeMdmTab === tab.id ? 'border-blue-500 text-blue-400 bg-[#2A2D3A]' : 'border-transparent text-[#B4BAC9] hover:text-[#B4BAC9] hover:bg-[#2A2D3A]'
            )"
          >
                <component :is="tab.icon" class="w-3.5 h-3.5 mr-2" />
            {{ tab.name }}
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="activeMdmTab === 'upstream'" class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="am-title-l2"><div class="am-title-bar"></div>外部系统接入看板 (Read-only)</h3>
              <button class="flex items-center text-[13px] text-[#B4BAC9] hover:text-white bg-[#1A1E2B] border border-[#3E4660] px-3 py-1.5 rounded transition-colors">
                <RefreshRight class="w-3 h-3 mr-1.5" /> 手动全量同步
              </button>
            </div>
            <div class="border border-[#2E3348] rounded-lg overflow-hidden">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-[#1A1E2B] border-b border-[#3E4660] text-[11px] text-[#B4BAC9] uppercase tracking-wider">
                    <th class="p-3 font-medium">产品类型</th>
                    <th class="p-3 font-medium">产品系列</th>
                    <th class="p-3 font-medium">产品名称/代码</th>
                    <th class="p-3 font-medium">数据源</th>
                    <th class="p-3 font-medium">同步状态</th>
                    <th class="p-3 font-medium text-right">最后同步时间</th>
                  </tr>
                </thead>
                <tbody class="text-[13px]">
                  <tr v-for="row in upstreamData" :key="row.id" class="border-b border-[#252A3A] hover:bg-[#2A2D3A] transition-colors">
                    <td class="p-3 text-[#B4BAC9]">{{ row.type }}</td>
                    <td class="p-3 text-[#B4BAC9]">{{ row.series }}</td>
                    <td class="p-3 text-[#E8ECF4] font-medium">{{ row.name }}</td>
                    <td class="p-3 text-[#B4BAC9]"><span class="bg-[#2E3348] px-2 py-1 rounded">{{ row.source }}</span></td>
                    <td class="p-3">
                      <span v-if="row.status === 'success'" class="text-green-500 flex items-center">
                        <CircleCheckFilled class="w-3 h-3 mr-1" /> 成功
                      </span>
                      <span v-else class="text-red-500 flex items-center">
                        <CircleCloseFilled class="w-3 h-3 mr-1" /> 失败
                      </span>
                    </td>
                    <td class="p-3 text-[#B4BAC9] text-right font-mono">{{ row.lastSync }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center h-full text-[#94A3B8]">
            <Connection class="w-12 h-12 mb-4 opacity-20" />
            <p class="text-[13px] font-mono mb-2">关系拓扑图 / 树状图渲染区</p>
            <p class="text-[13px] text-[#4A5568]">请选择左侧或上方具体映射类型进行配置</p>
          </div>
        </div>
      </div>

      <!-- Workflow -->
      <div v-if="activeNav === 'workflow'" class="flex flex-col h-full overflow-hidden bg-[#161922]">
        <div class="flex border-b border-[#2E3348] bg-[#1A1E2B] shrink-0 px-4 pt-3 space-x-6">
          <button
            @click="activeWorkflowTab = 'rules'"
            :class="cn('pb-3 text-[13px] font-bold transition-colors border-b-2', activeWorkflowTab === 'rules' ? 'border-blue-500 text-blue-400' : 'border-transparent text-[#B4BAC9] hover:text-[#B4BAC9]')"
          >自动化规则引擎 (Rule Engine)</button>
          <button
            @click="activeWorkflowTab = 'manual'"
            :class="cn('pb-3 text-[13px] font-bold transition-colors border-b-2', activeWorkflowTab === 'manual' ? 'border-blue-500 text-blue-400' : 'border-transparent text-[#B4BAC9] hover:text-[#B4BAC9]')"
          >手动代办派发</button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="activeWorkflowTab === 'rules'" class="space-y-6 max-w-4xl mx-auto">
            <div class="flex justify-between items-center">
              <div>
                <h3 class="am-title-l2"><div class="am-title-bar"></div>IFTTT 触发器配置</h3>
                <p class="text-[13px] text-[#B4BAC9] mt-1">配置自动化规则以驱动 MAP 门户的 7 个投资流程图节点流转。</p>
              </div>
              <button class="flex items-center bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded text-[13px] font-medium transition-colors">
                <Plus class="w-3.5 h-3.5 mr-1" /> 新建规则
              </button>
            </div>
            <div class="space-y-4">
              <div v-for="rule in rules" :key="rule.id" class="bg-[#1A1E2B] border border-[#3E4660] rounded-lg p-4 hover:border-[#555E75] transition-colors">
                <div class="flex justify-between items-start mb-4">
                  <div class="flex items-center">
                    <Lightning :class="cn('w-4 h-4 mr-2', rule.active ? 'text-yellow-500' : 'text-[#94A3B8]')" />
                    <span class="text-[13px] font-bold text-[#E8ECF4]">{{ rule.name }}</span>
                  </div>
                  <div :class="cn('w-10 h-5 rounded-full flex items-center p-0.5 cursor-pointer transition-colors', rule.active ? 'bg-blue-600' : 'bg-[#3E4660]')">
                    <div :class="cn('w-4 h-4 rounded-full bg-white transition-transform', rule.active ? 'translate-x-5' : 'translate-x-0')" />
                  </div>
                </div>
                <div class="flex flex-col space-y-2 bg-[#161922] p-3 rounded border border-[#2E3348]">
                  <div class="flex items-start">
                    <span class="text-[13px] font-bold text-blue-400 w-10 shrink-0 mt-0.5">IF</span>
                    <div class="text-[13px] text-[#B4BAC9] font-mono bg-[#2A2D3A] px-2 py-1 rounded border border-[#3E4660] flex-1">{{ rule.condition }}</div>
                  </div>
                  <div class="flex items-start">
                    <span class="text-[13px] font-bold text-green-400 w-10 shrink-0 mt-0.5">THEN</span>
                    <div class="text-[13px] text-[#B4BAC9] font-mono bg-[#2A2D3A] px-2 py-1 rounded border border-[#3E4660] flex-1">{{ rule.action }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="max-w-2xl mx-auto bg-[#1A1E2B] border border-[#2E3348] rounded-lg p-6">
            <h3 class="am-title-l2"><div class="am-title-bar"></div>派发新代办任务</h3>
            <div class="space-y-5">
              <div>
                <label class="block text-[13px] text-[#B4BAC9] mb-1.5">目标流程节点</label>
                <select class="w-full operable-zone text-[#E8ECF4] text-[13px] rounded px-3 py-2 focus:outline-none">
                  <option>1. 投资目标</option>
                  <option>2. 研究分析</option>
                  <option>3. 资产配置</option>
                  <option>4. 组合试算</option>
                  <option>5. 投资管理</option>
                  <option>6. 定期再平衡</option>
                  <option>7. 长期跟踪</option>
                </select>
              </div>
              <div>
                <label class="block text-[13px] text-[#B4BAC9] mb-1.5">指派给 (投资经理/研究员)</label>
                <input type="text" placeholder="输入姓名或工号搜索..." class="w-full operable-zone text-[#E8ECF4] text-[13px] rounded px-3 py-2 focus:outline-none" />
              </div>
              <div>
                <label class="block text-[13px] text-[#B4BAC9] mb-1.5">任务描述</label>
                <textarea rows="3" placeholder="描述需要执行的具体操作..." class="w-full operable-zone text-[#E8ECF4] text-[13px] rounded px-3 py-2 focus:outline-none resize-none" />
              </div>
              <div class="pt-4 border-t border-[#2E3348] flex justify-end">
                <button class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white text-[13px] font-bold rounded transition-colors shadow-[0_0_10px_rgba(37,99,235,0.2)]">立即派发</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  Management, DataAnalysis, Bell, UserFilled, Key, Lock,
  Connection, Share, Avatar, TrendCharts, WarningFilled,
  Plus, DocumentAdd, Search, ArrowRight, Select, SemiSelect,
  Setting as SettingsIcon, Lightning, VideoPlay, RefreshRight, CircleCheckFilled, CircleCloseFilled
} from '@element-plus/icons-vue';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }

const activeNav = ref('iam');
const activeGroup = ref('g2');
const activeMdmTab = ref('org');
const activeWorkflowTab = ref('rules');

const leftNavItems = [
  { id: 'iam', label: '权限安全管理', icon: Management },
  { id: 'mdm', label: '系统主数据', icon: DataAnalysis },
  { id: 'workflow', label: '消息与流程引擎', icon: Bell },
];

const userGroups = [
  { id: 'g1', name: '班子领导', type: 'builtin' },
  { id: 'g2', name: '投资经理', type: 'builtin' },
  { id: 'g3', name: '投资助理', type: 'builtin' },
  { id: 'g4', name: '投资管理岗', type: 'builtin' },
  { id: 'g5', name: '系统管理员', type: 'builtin' },
  { id: 'g6', name: '固收交易员', type: 'custom' },
];

const roleTree = [
  { id: 'r_dash', name: '工作台 (Dashboard)', checked: true, children: [
    { id: 'r_dash_view', name: '查看工作台', checked: true },
    { id: 'r_dash_edit', name: '编辑卡片布局', checked: false },
  ]},
  { id: 'r_port', name: '投资组合 (Portfolio)', checked: true, children: [
    { id: 'r_port_view', name: '查看组合列表', checked: true },
    { id: 'r_port_trade', name: '生成交易指令', checked: false },
    { id: 'r_port_rebal', name: '执行定期再平衡', checked: false },
  ]},
  { id: 'r_model', name: '模型中心 (Model Center)', checked: false, children: [
    { id: 'r_model_view', name: '查看模型', checked: false },
    { id: 'r_model_run', name: '运行模型', checked: false },
    { id: 'r_model_upload', name: '上传自定义模型', checked: false },
  ]}
];

const securityClasses = [
  { id: 'sec1', name: '仅看本人负责产品', desc: '限制查看当前用户作为主PM的产品数据', selected: false },
  { id: 'sec2', name: '可看本部门所有产品', desc: '允许查看当前用户所在部门（如固收部）的所有产品', selected: true },
  { id: 'sec3', name: '可看全公司产品', desc: '最高数据权限，可跨部门查看所有产品', selected: false },
];

const mdmTabs = [
  { id: 'org', name: '组织与产品映射', icon: Connection },
  { id: 'arch', name: '投资架构映射', icon: Share },
  { id: 'committee', name: '投委会配置', icon: Avatar },
  { id: 'upstream', name: '上游数据接入', icon: TrendCharts },
  { id: 'risk', name: '风控基准主数据', icon: WarningFilled },
];

const upstreamData = [
  { id: '1', type: '公募基金', series: '稳健收益系列', name: '稳健回报A (000001)', source: 'O32系统', status: 'success', lastSync: '10 mins ago' },
  { id: '2', type: '专户理财', series: '定制策略系列', name: '量化对冲1号 (Z0001)', source: '估值系统', status: 'success', lastSync: '12 mins ago' },
  { id: '3', type: '企业年金', series: '养老金系列', name: '企业年金计划B (N0002)', source: 'O32系统', status: 'error', lastSync: '2 hours ago' },
];

const rules = [
  { id: 'rule1', name: 'TAA偏离度预警', condition: 'If [实际组合与TAA偏离度] > [2%]', action: 'Then 在节点 [定期再平衡] 生成预警代办发送给 [对应PM]', active: true },
  { id: 'rule2', name: '最大回撤触警', condition: 'If [产品近1月最大回撤] >= [风控阈值]', action: 'Then 在节点 [长期跟踪] 生成高危提醒发送给 [投资管理岗]', active: true },
  { id: 'rule3', name: '研究报告更新', condition: 'If [核心股票池标的] 评级下调', action: 'Then 在节点 [研究分析] 生成复核代办发送给 [对应研究员]', active: false },
];
</script>
