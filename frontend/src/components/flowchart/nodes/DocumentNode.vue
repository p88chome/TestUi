<template>
  <div class="custom-node document-node">
    <Handle type="target" :position="Position.Top" />
    <Handle type="source" :position="Position.Bottom" />
    
    <div class="node-content">
      <i class="pi pi-file text-purple-400" style="font-size: 1.1rem"></i>
      <div class="label-text">{{ data.label }}</div>
      <div v-if="data.lane" class="lane-tag">{{ data.lane }}</div>
    </div>
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
  padding: 10px 14px;
  background: #312e81; /* Indigo */
  border: 1px solid #6366f1;
  border-radius: 0 12px 0 0; /* Folded corner look */
  color: #e0e7ff;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.3);
  min-width: 120px;
  text-align: center;
}
.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.lane-tag {
  font-size: 10px;
  color: #a5b4fc;
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
