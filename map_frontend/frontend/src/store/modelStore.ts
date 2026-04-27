import { reactive } from 'vue';

export interface RuleModelParam {
  key: string;
  label: string;
  type: 'number' | 'percent' | 'text';
  defaultVal: number | string;
  unit?: string;
  min?: number;
  max?: number;
}

export interface RuleModel {
  id: string;
  name: string;
  shortName: string;
  desc: string;
  icon: string;
  color: string;
  params: RuleModelParam[];
  outputDesc: string;
}

export const RULE_MODELS: RuleModel[] = [
  {
    id: 'avg-total',
    name: '总量平均分配模型',
    shortName: '总量平均',
    desc: '将调仓总金额等额分配至所有目标产品，不考虑各产品现有规模差异',
    icon: '⚖️',
    color: '#3B9EFF',
    params: [
      { key: 'totalAmount', label: '调仓总金额', type: 'number', defaultVal: 50000, unit: '万', min: 0 },
    ],
    outputDesc: '每只产品分配金额 = 总金额 / 产品数量',
  },
  {
    id: 'nav-proportional',
    name: '净资产等比分摊模型',
    shortName: '净资产等比',
    desc: '按各产品净资产规模的比例分摊调仓金额，规模越大分配越多',
    icon: '📊',
    color: '#00C9A7',
    params: [
      { key: 'totalAmount', label: '调仓总金额', type: 'number', defaultVal: 50000, unit: '万', min: 0 },
      { key: 'navField', label: '净资产字段', type: 'text', defaultVal: 'latest_nav' },
    ],
    outputDesc: '分配金额 = 总金额 × (产品NAV / 全部产品NAV合计)',
  },
  {
    id: 'concentration',
    name: '资产浓度控制模型',
    shortName: '浓度策略',
    desc: '控制单一资产类别的集中度上限，超限部分自动削减并重新分配',
    icon: '🎯',
    color: '#FFAB00',
    params: [
      { key: 'targetPercent', label: '目标百分比', type: 'percent', defaultVal: 15, unit: '%', min: 0, max: 100 },
      { key: 'targetAsset', label: '目标资产', type: 'text', defaultVal: '权益' },
      { key: 'maxSingle', label: '单产品上限', type: 'percent', defaultVal: 5, unit: '%', min: 0, max: 100 },
    ],
    outputDesc: '超出上限的持仓将被削减至目标水平，释放额度按比例再分配',
  },
];

export interface ModelExecutionResult {
  modelId: string;
  modelName: string;
  timestamp: number;
  params: Record<string, number | string>;
  preview: { name: string; value: string; change: string }[];
}

export const modelState = reactive({
  selectedRuleModelId: null as string | null,
  executionResults: [] as ModelExecutionResult[],
  isExecuting: false,
});

export function getRuleModel(id: string): RuleModel | undefined {
  return RULE_MODELS.find(m => m.id === id);
}

export function executeRuleModel(
  modelId: string,
  params: Record<string, number | string>,
  productCount: number,
  productData?: { name: string; nav?: number }[]
): ModelExecutionResult {
  const model = getRuleModel(modelId);
  if (!model) throw new Error(`Model ${modelId} not found`);

  const preview: ModelExecutionResult['preview'] = [];

  if (modelId === 'avg-total') {
    const total = Number(params.totalAmount || 0);
    const perProduct = productCount > 0 ? total / productCount : 0;
    preview.push(
      { name: '调仓总额', value: `${total.toLocaleString()} 万`, change: '' },
      { name: '产品数量', value: `${productCount} 只`, change: '' },
      { name: '每只分配', value: `${perProduct.toFixed(1)} 万`, change: `均额` },
    );
  } else if (modelId === 'nav-proportional') {
    const total = Number(params.totalAmount || 0);
    const totalNav = productData?.reduce((s, p) => s + (p.nav || 0), 0) || productCount * 10000;
    const avgRatio = totalNav > 0 ? (total / totalNav * 100).toFixed(2) : '0.00';
    preview.push(
      { name: '调仓总额', value: `${total.toLocaleString()} 万`, change: '' },
      { name: '净资产合计', value: `${totalNav.toLocaleString()} 万`, change: '' },
      { name: '平均调仓比例', value: `${avgRatio}%`, change: `按NAV比` },
    );
    if (productData && productData.length > 0) {
      productData.slice(0, 3).forEach(p => {
        const ratio = totalNav > 0 ? (p.nav || 0) / totalNav : 1 / productCount;
        preview.push({ name: p.name, value: `${(total * ratio).toFixed(1)} 万`, change: `${(ratio * 100).toFixed(1)}%` });
      });
      if (productData.length > 3) {
        preview.push({ name: `...其余 ${productData.length - 3} 只`, value: '—', change: '按比例' });
      }
    }
  } else if (modelId === 'concentration') {
    const targetPct = Number(params.targetPercent || 15);
    const targetAsset = String(params.targetAsset || '权益');
    const maxSingle = Number(params.maxSingle || 5);
    preview.push(
      { name: '目标资产', value: targetAsset, change: '' },
      { name: '目标占比', value: `${targetPct}%`, change: `控制上限` },
      { name: '单产品上限', value: `${maxSingle}%`, change: `集中度` },
      { name: '预估需调整', value: `${Math.max(0, 17.5 - targetPct).toFixed(1)}pp`, change: `削减超限` },
    );
  }

  const result: ModelExecutionResult = {
    modelId,
    modelName: model.name,
    timestamp: Date.now(),
    params,
    preview,
  };

  modelState.executionResults.push(result);
  return result;
}
