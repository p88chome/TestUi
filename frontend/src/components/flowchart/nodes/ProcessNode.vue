<template>
  <div class="custom-node process-node">
    <Handle type="target" :position="Position.Top" />
    
    <div class="node-content">
      <div class="label-text">{{ data.label }}</div>
      <div v-if="data.lane" class="lane-tag">{{ data.lane }}</div>
    </div>
    
    <Handle type="source" :position="Position.Bottom" />
    <Handle type="source" :position="Position.Right" id="right" />
    <Handle type="target" :position="Position.Left" id="left" />
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
  border: 2px solid #3b82f6; /* Blue border */
  border-radius: 8px;
  color: #f8fafc;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  min-width: 160px;
  text-align: center;
  transition: all 0.2s;
}
.custom-node:hover {
  border-color: #60a5fa;
  box-shadow: 0 6px 12px -2px rgba(59, 130, 246, 0.3);
}
.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.lane-tag {
  font-size: 11px;
  color: #93c5fd;
  background: rgba(59, 130, 246, 0.15);
  padding: 2px 8px;
  border-radius: 4px;
}
</style>
