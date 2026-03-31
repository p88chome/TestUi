<template>
  <div class="custom-node start-end-node">
    <Handle v-if="data.isEnd || (!data.isStart && !data.isEnd)" type="target" :position="Position.Top" />
    
    <div class="node-content">
      <div class="label-text">{{ data.label }}</div>
      <div v-if="data.lane" class="lane-tag">{{ data.lane }}</div>
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
  padding: 10px 16px;
  background: linear-gradient(135deg, #1e293b, #0f172a);
  border: 2px solid #334155;
  border-radius: 9999px; /* Capsule shape */
  color: #fff;
  font-size: 14px;
  font-weight: bold;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
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
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}
</style>
