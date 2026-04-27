<template>
  <div
    class="operable-zone rounded-lg border border-[#2E3348] px-3 py-2.5 flex items-center gap-3"
    :class="disabled ? 'opacity-50 pointer-events-none' : ''"
  >
    <span class="text-[13px] font-medium text-[#E8ECF4] w-20 shrink-0 truncate" :title="name">{{ name }}</span>

    <div class="flex-1 flex items-center gap-1.5 min-w-0 bg-[#1E2330] p-1.5 rounded border border-[#3A4259] hover:border-[#3B9EFF] transition-colors">
      <button
        @click.prevent="emit('update:val', clamp(val - 0.1))"
        class="w-5 h-5 flex items-center justify-center text-[#94A3B8] hover:text-[#E8ECF4] hover:bg-[#2A2D3A] rounded transition-colors shrink-0"
        :disabled="disabled"
      >
        <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/></svg>
      </button>

      <input
        type="range"
        min="0"
        max="100"
        step="0.1"
        class="am-slider flex-1 min-w-0"
        :value="val"
        :disabled="disabled"
        @input="onSlider"
        :style="{
          background: `linear-gradient(to right, ${color} 0%, ${color} ${val}%, #252A3A ${val}%, #252A3A 100%)`,
          '--slider-thumb-color': color,
        }"
      />

      <button
        @click.prevent="emit('update:val', clamp(val + 0.1))"
        class="w-5 h-5 flex items-center justify-center text-[#94A3B8] hover:text-[#E8ECF4] hover:bg-[#2A2D3A] rounded transition-colors shrink-0"
        :disabled="disabled"
      >
        <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      </button>

      <div class="relative flex items-center w-14 border-l border-[#3A4259] pl-1.5 ml-0.5 shrink-0">
        <input
          type="number"
          min="0"
          max="100"
          step="0.1"
          :value="val"
          :disabled="disabled"
          @change="onInput"
          class="w-full bg-transparent text-[#E8ECF4] text-[13px] font-mono text-right outline-none pr-3 [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
        />
        <span class="absolute right-0 text-[#94A3B8] text-[11px]">%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  name: string;
  val: number;
  color: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:val', value: number): void;
}>();

function clamp(v: number): number {
  return Math.min(100, Math.max(0, Math.round(v * 10) / 10));
}

function onSlider(e: Event) {
  if (props.disabled) return;
  emit('update:val', clamp(Number((e.target as HTMLInputElement).value)));
}

function onInput(e: Event) {
  if (props.disabled) return;
  const raw = parseFloat((e.target as HTMLInputElement).value);
  if (!isNaN(raw)) emit('update:val', clamp(raw));
}
</script>
