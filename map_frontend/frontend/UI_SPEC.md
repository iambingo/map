# MAP UI/UX Design System (v1.0)

## 1. 设计哲学 (Design Philosophy)
* **极客与专业 (Geek & Professional)**：深蓝灰主色调，克制使用高饱和色彩，绝对禁止使用装饰性 Emoji。
* **数据严谨 (Data Integrity)**：数字对齐重于一切，消除视觉歧义。
* **读写分离 (Read/Write Separation)**：通过背景深度和阴影，明确区分“只读数据”与“可操作域”。

## 2. 字体与排版规范 (Typography & Legibility)
为保证高管及业务人员的阅读体验，提升全局基础字号，严禁过度压缩字号。
* **全局基准字号**：`text-xs` (12px) 作为数据表格、正文的最小常规阅读字号。
* **辅助说明字号**：`text-[11px]` (11px) 仅用于次要的、非核心数据的修饰语（如单位、图表图例）。
* **禁用字号**：**严禁在可读文本中使用 `8px`、`9px` 或 `10px`**（除非是极小的状态徽章 Badge）。
* **数字字体**：所有包含金额、比例、收益率的数据，必须强制使用等宽数字字体 `font-mono tabular-nums`，确保上下行数字的绝对对齐。

## 3. 表格与网格规范 (The "DongZong" Grid Rule)
针对所有包含对比性质的财务、收益率表格，严格执行以下红线：
* **固定列宽**：强制开启 `table-fixed`。
* **等宽数据列**：无论表头文字多长，所有数据对比列必须使用统一的绝对宽度（如 `w-24` 或 `w-[100px]`）。
* **绝对右对齐**：所有金额、百分比数值必须绝对右对齐 `text-right`。
* **表头释义**：对于“近1月”、“YTD”等时间区间表头，必须配有 `(i)` 悬浮图标，Tooltip 需明确标示计算的自然日区间（如 `2026-03-15 至 2026-04-15`）。

## 4. 色彩规范 (Color Tokens)
* **背景层级 (Backgrounds)**：
  * Base (页面底色): `#161922`
  * Panel (卡片色): `#1A1E2B`
  * Elevated (悬浮/弹窗色): `#202431`
* **文本层级 (Text)**：
  * Title / Highlight: `#FFFFFF`
  * Primary: `#E8ECF4`
  * Secondary: `#B4BAC9`
  * Muted: `#94A3B8`
* **金融语义色 (Financial Semantics - A股习惯)**：
  * 盈利/看多 (Gain/Bull): `#F04864` (Red)
  * 亏损/看空 (Loss/Bear): `#00C9A7` (Green)
  * 预警/偏离 (Warn): `#FFAB00` (Amber)

## 5. 交互与术语规范 (Interaction & Terminology)
* **SASA 命名法**：全局统一层级黑话：`委员会指引`、`部门指引`、`产品指引`、`实际持仓`。
* **扁平化导出**：所有树形折叠表格（TreeGrid）上方必须提供 `[⬇ 导出数据 (Excel)]` 按钮，并默认承诺导出格式为 2D 扁平横表，便于业务拉取透视表。
* **区域响应 (Zones)**：
  * `.readonly-zone`: 下沉阴影，无 hover 效果。
  * `.operable-zone`: 略浅的底色，hover 时边框亮起（`hover:border-[#3B9EFF]/50`）。

  ## 6. 字号梯队规范 (Typography Hierarchy)
建立严格的层级秩序，确保页面逻辑清晰：
- **一级标题 (Page Title)**: `text-lg` (18px) / `font-bold`。用于页面顶端主标题。
- **二级标题 (Section Title)**: `text-base` (16px) / `font-semibold`。用于主要卡片或栏目。
- **三级标题 (Sub-section Title)**: `text-sm` (14px) / `font-medium`。用于子栏目。
- **正文/内容 (Body/Content)**: `text-xs` (12px)。用于表格数据、表单标签、描述文本。
- **辅助/标注 (Helper)**: `text-[11px]`。仅用于极细微的补充说明。

## 7. 色彩强化约定 (Color Semantics)
- **上涨/看涨/利好**: 强制使用红色 `#F04864` (Tailwind类: `text-[#F04864]` 或 `bg-[#F04864]`)。
- **下跌/看跌/利空**: 强制使用绿色 `#00C9A7` (Tailwind类: `text-[#00C9A7]` 或 `bg-[#00C9A7]`)。
- **背景与秩序**: 页面必须保持蓝灰色系背景，确保红/绿数据在深色背景下具备极高的对比度和清晰度。

## 8. 视觉元素规范
- **Emoji 禁令**: 严禁出现任何 Emoji 图标。
- **标题装饰**: 所有级别标题左侧必须统一使用“粗竖线”修饰。
  - 一级标题: `w-1 h-5 bg-[#3B9EFF] mr-3`
  - 二级/三级标题: `w-0.5 h-4 bg-[#3B9EFF]/70 mr-2`