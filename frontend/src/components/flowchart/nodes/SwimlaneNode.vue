<template>
  <div class="swimlane-node">
    <div class="lane-header">{{ data.label }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  data: { label: string };
}>();
</script>

<style scoped>
.swimlane-node {
  width: 100%;
  height: 100%;
  background-color: rgba(241, 245, 249, 0.4); /* Slate 100, slightly transparent */
  border: 2px dashed #94a3b8; /* Slate 400 */
  border-radius: 12px;
  position: relative;
  z-index: -10; /* Keep it behind other nodes */
}
.lane-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background: #f1f5f9;
  border-bottom: 2px solid #94a3b8;
  color: #334155;
  font-weight: bold;
  font-size: 16px;
  padding: 12px;
  text-align: center;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}
</style>
