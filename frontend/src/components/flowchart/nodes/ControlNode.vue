<template>
  <div class="control-wrapper" :class="{ 'has-doc': hasDocs }">
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
    <div v-if="hasDocs" class="doc-sticker">
      <div v-for="(d, i) in data.docs" :key="i" class="doc-line">{{ d }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Handle, Position } from '@vue-flow/core';

const props = defineProps<{
  data: { label: string; lane?: string; docs?: string[] };
}>();

const hasDocs = computed(() => !!props.data.docs && props.data.docs.length > 0);
</script>

<style scoped>
.control-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}
.custom-node.control-node {
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
.custom-node.control-node:hover .node-bg polygon {
  stroke: #2563eb;
  stroke-width: 3;
}
.doc-sticker {
  position: relative;
  max-width: 180px;
  padding: 8px 14px 12px 14px;
  background: #ffffff;
  border: 2px solid #ea580c;
  color: #1e293b;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.3;
  box-shadow: 0 2px 4px rgba(234, 88, 12, 0.2);
  clip-path: polygon(0 0, 100% 0, 100% 88%, 85% 100%, 70% 88%, 55% 100%, 40% 88%, 25% 100%, 10% 88%, 0 100%);
  text-align: center;
}
.doc-line + .doc-line {
  margin-top: 2px;
  padding-top: 2px;
  border-top: 1px dashed #fed7aa;
}
</style>
