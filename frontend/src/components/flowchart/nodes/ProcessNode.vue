<template>
  <div class="custom-node process-node">
    <Handle type="target" :position="Position.Top" />
    
    <div class="node-content">
      <div class="label-text">{{ data.label }}</div>
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
  background: #ffffff;
  border: 2px solid #334155; /* Slate border */
  border-radius: 4px; /* Slight rounding or sharp */
  color: #1e293b;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  min-width: 160px;
  text-align: center;
  transition: all 0.2s;
}
.custom-node:hover {
  border-color: #2563eb;
  box-shadow: 0 6px 12px -2px rgba(37, 99, 235, 0.2);
}
.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
</style>
