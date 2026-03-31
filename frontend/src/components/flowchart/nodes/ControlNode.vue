<template>
  <div class="custom-node control-node">
    <svg class="node-bg" viewBox="0 0 100 100" preserveAspectRatio="none">
      <polygon points="50,2 98,50 50,98 2,50" fill="#ffffff" stroke="#334155" stroke-width="2"/>
    </svg>
    <Handle type="target" :position="Position.Top" />
    
    <div class="node-content">
      <div class="label-text">{{ data.label }}</div>
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
  position: relative;
  width: 160px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.node-bg {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  z-index: -1;
  filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.1));
}
.node-content {
  text-align: center;
  z-index: 1;
  padding: 0 20px;
}
.label-text {
  color: #1e293b;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.2;
}
.custom-node:hover .node-bg polygon {
  stroke: #2563eb;
  stroke-width: 3;
}
</style>
