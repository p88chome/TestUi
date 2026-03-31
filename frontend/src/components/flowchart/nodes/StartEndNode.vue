<template>
  <div class="custom-node start-end-node">
    <Handle v-if="data.isEnd || (!data.isStart && !data.isEnd)" type="target" :position="Position.Top" />
    
    <div class="node-content">
      <div class="label-text">{{ data.label }}</div>
    </div>
    
    <Handle v-if="data.isStart || (!data.isStart && !data.isEnd)" type="source" :position="Position.Bottom" />
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core';

defineProps<{
  data: { label: string; lane?: string; isStart?: boolean; isEnd?: boolean };
}>();
</script>

<style scoped>
.custom-node {
  padding: 10px 24px;
  background: #ffffff;
  border: 2px solid #334155;
  border-radius: 9999px; /* Capsule shape */
  color: #1e293b;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  min-width: 120px;
  text-align: center;
}
.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
</style>
