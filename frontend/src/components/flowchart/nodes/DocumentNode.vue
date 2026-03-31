<template>
  <div class="custom-node document-node">
    <svg class="node-bg" viewBox="0 0 100 100" preserveAspectRatio="none">
      <!-- Standard document shape with wave bottom -->
      <path d="M 2,2 L 98,2 L 98,85 Q 75,100 50,85 T 2,85 Z" fill="#ffffff" stroke="#ea580c" stroke-width="4"/>
    </svg>
    <Handle type="target" :position="Position.Top" />
    <Handle type="source" :position="Position.Bottom" />
    
    <div class="node-content">
      <div class="label-text">{{ data.label }}</div>
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
  position: relative;
  width: 150px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.node-bg {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  z-index: -1;
  filter: drop-shadow(0px 4px 6px rgba(234, 88, 12, 0.2));
}
.node-content {
  text-align: center;
  z-index: 1;
  padding: 0 15px;
  margin-bottom: 5px; /* offset for the wave */
}
.label-text {
  color: #1e293b;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.2;
}
.custom-node:hover .node-bg path {
  fill: #fff7ed;
}
</style>
