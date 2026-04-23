<template>
  <div class="process-wrapper" :class="{ 'has-doc': hasDocs }">
    <div class="custom-node process-node">
      <Handle type="target" :position="Position.Top" />
      <div class="node-content">
        <div class="label-text">{{ data.label }}</div>
      </div>
      <Handle type="source" :position="Position.Bottom" />
      <Handle type="source" :position="Position.Right" id="right" />
      <Handle type="target" :position="Position.Left" id="left" />
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
.process-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}
.custom-node.process-node {
  padding: 12px 16px;
  background: #ffffff;
  border: 2px solid #334155;
  border-radius: 4px;
  color: #1e293b;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  min-width: 160px;
  text-align: center;
  transition: all 0.2s;
}
.custom-node.process-node:hover {
  border-color: #2563eb;
  box-shadow: 0 6px 12px -2px rgba(37, 99, 235, 0.2);
}
.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
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
  /* 紙張波浪底: 用 clip-path 做 */
  clip-path: polygon(0 0, 100% 0, 100% 88%, 85% 100%, 70% 88%, 55% 100%, 40% 88%, 25% 100%, 10% 88%, 0 100%);
  text-align: center;
}
.doc-line + .doc-line {
  margin-top: 2px;
  padding-top: 2px;
  border-top: 1px dashed #fed7aa;
}
</style>
