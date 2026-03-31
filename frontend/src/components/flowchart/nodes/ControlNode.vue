<template>
  <div class="custom-node control-node">
    <Handle type="target" :position="Position.Top" />
    
    <div class="node-content">
      <i class="pi pi-question-circle text-orange-400 mb-1" style="font-size: 1.2rem"></i>
      <div class="label-text">{{ data.label }}</div>
      <div v-if="data.lane" class="lane-tag">{{ data.lane }}</div>
    </div>
    
    <Handle type="source" :position="Position.Bottom" id="bottom" />
    <Handle type="source" :position="Position.Right" id="right" />
    <Handle type="source" :position="Position.Left" id="left" />
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core';

defineProps<{
  data: { label: string; lane?: string };
}>();
</script>

<style scoped>
.custom-node {
  padding: 12px 16px;
  background: #1e293b;
  border: 2px solid #ea580c; /* Orange border */
  border-radius: 4px;
  color: #f8fafc;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  min-width: 140px;
  max-width: 180px;
  text-align: center;
  transition: all 0.2s;
  /* Make it roughly diamond-ish or just distinguishable */
  border-radius: 16px 4px 16px 4px; 
}
.custom-node:hover {
  border-color: #f97316;
  box-shadow: 0 6px 12px -2px rgba(234, 88, 12, 0.3);
}
.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.lane-tag {
  font-size: 11px;
  color: #fdba74;
  background: rgba(234, 88, 12, 0.15);
  padding: 2px 8px;
  border-radius: 4px;
  margin-top: 2px;
}
</style>
