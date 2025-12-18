<template>
  <div class="run-detail-page">
    <div class="page-header">
      <h1>Run Details</h1>
      <button class="btn" @click="$router.back()">Back</button>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="run" class="run-container">
      <div class="run-meta">
        <div class="meta-item">
          <label>ID</label>
          <span>{{ run.id }}</span>
        </div>
        <div class="meta-item">
          <label>Status</label>
          <span :class="['status-badge', run.status]">{{ run.status }}</span>
        </div>
        <div class="meta-item">
          <label>Started</label>
          <span>{{ new Date(run.started_at).toLocaleString() }}</span>
        </div>
        <div class="meta-item">
          <label>Finished</label>
          <span>{{ run.finished_at ? new Date(run.finished_at).toLocaleString() : '-' }}</span>
        </div>
      </div>

      <div class="section">
        <h3>Input Payload</h3>
        <pre class="json-box">{{ JSON.stringify(run.input_payload, null, 2) }}</pre>
      </div>

      <div class="section">
        <h3>Execution Log (Step Results)</h3>
        <div class="logs">
          <div v-for="(stepLog, index) in run.log" :key="index" class="log-item">
            <div class="log-header" @click="toggleLog(index)">
              <strong>Step {{ stepLog.step_id }}</strong>
              <span>{{ stepLog.status || 'completed' }}</span>
            </div>
            <div class="log-body" v-show="expandedLogs[index]">
               <div class="sub-section">
                 <label>Input</label>
                 <pre>{{ JSON.stringify(stepLog.input, null, 2) }}</pre>
               </div>
               <div class="sub-section">
                 <label>Output</label>
                 <pre>{{ JSON.stringify(stepLog.output, null, 2) }}</pre>
               </div>
            </div>
          </div>
          <div v-if="run.log.length === 0" class="empty">No logs available yet.</div>
        </div>
      </div>

      <div class="section" v-if="run.output_payload">
        <h3>Final Output</h3>
        <pre class="json-box">{{ JSON.stringify(run.output_payload, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getRun } from '../api/runs';
import type { RunExecutionOut } from '../types';

const route = useRoute();
const run = ref<RunExecutionOut | null>(null);
const loading = ref(true);
const expandedLogs = ref<Record<number, boolean>>({});

const fetchRun = async () => {
  const id = route.params.id as string;
  try {
    run.value = await getRun(id);
    // Auto expand all
    if (run.value.log) {
        run.value.log.forEach((_, i) => expandedLogs.value[i] = true);
    }
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const toggleLog = (index: number) => {
  expandedLogs.value[index] = !expandedLogs.value[index];
};

onMounted(() => {
  fetchRun();
  // Poll every 2 seconds if running
  const interval = setInterval(async () => {
    if (run.value && run.value.status === 'running') {
        await fetchRun();
    } else {
        clearInterval(interval);
    }
  }, 2000);
});
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.run-container {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.run-meta {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.meta-item label {
  display: block;
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 4px;
}

.meta-item span {
  font-weight: 500;
  color: #111827;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  background: #f3f4f6;
}

.status-badge.running { background: #dbeafe; color: #1e40af; }
.status-badge.completed { background: #d1fae5; color: #065f46; }
.status-badge.failed { background: #fee2e2; color: #991b1b; }

.section {
  margin-bottom: 24px;
}

.section h3 {
  font-size: 1rem;
  margin-bottom: 12px;
  color: #374151;
}

.json-box {
  background: #f9fafb;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.9rem;
  font-family: monospace;
}

.log-item {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 8px;
}

.log-header {
  padding: 12px;
  background: #f9fafb;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.log-body {
  padding: 12px;
  border-top: 1px solid #e5e7eb;
}

.sub-section {
  margin-bottom: 8px;
}
.sub-section label {
  font-weight: 600;
  font-size: 0.8rem;
}

.btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
}
</style>
