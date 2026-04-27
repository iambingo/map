import { reactive } from 'vue';

export interface PendingModelWeights {
  modelId: string;
  modelName: string;
  /** code → suggested weight (%) */
  weights: Record<string, number>;
}

export interface BatchContext {
  sourcePack: string;
  sourcePackLabel: string;
  productCount: number;
  taskTag: string;
  taskIcon: string;
  timestamp: number;
}

export const sharedIntentState = reactive<{
  pendingModelWeights: PendingModelWeights | null;
  applyTimestamp: number;
  navigationTarget: string | null;
  callerTab: 'taa' | 'intent' | null;
  batchContext: BatchContext | null;
}>({
  pendingModelWeights: null,
  applyTimestamp: 0,
  navigationTarget: null,
  callerTab: null,
  batchContext: null,
});
