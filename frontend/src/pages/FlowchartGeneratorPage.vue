<template>
  <div class="flowchart-page p-4">
    <!-- Header -->
    <div class="flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="text-heading-xl m-0 mb-1 deloitte-green-dot">
          <i class="pi pi-share-alt mr-2 text-green-500"></i>
          互動流程圖產生器
        </h1>
        <p class="text-body-lg m-0 text-500">上傳文件，AI 分析後產出 Vue Flow 互動畫布，可即時拖曳與編輯</p>
      </div>
      <Tag value="Vue Flow + AI Powered" severity="success" class="font-bold" />
    </div>

    <div class="grid" style="height: calc(100vh - 130px);">
      <!-- ───────────────────── Left Panel ───────────────────── -->
      <div class="col-12 lg:col-4 flex flex-column h-full">
        <div class="deloitte-card p-4 flex flex-column h-full" style="overflow: hidden;">

          <!-- Step badges -->
          <div class="flex gap-2 mb-4">
            <Tag :value="step === 0 ? '步驟 1' : '完成'" :severity="step >= 1 ? 'success' : 'info'" />
            <Tag :value="step >= 1 ? '步驟 2 (對話中)' : '步驟 2'" :severity="step === 1 ? 'info' : 'secondary'" />
          </div>

          <!-- ── Upload area (Step 0) ── -->
          <div v-if="step === 0" class="flex-1 overflow-auto pr-2">
            <h2 class="text-heading-md m-0 mb-3 deloitte-green-dot">
              <i class="pi pi-upload mr-2 text-green-500"></i>上傳對應文件
            </h2>
            <div class="field mb-3">
              <label class="font-semibold mb-2 block">選擇文件 <span class="text-red-500">*</span></label>
              <FileUpload
                mode="basic"
                name="doc"
                :auto="false"
                accept=".docx,.pdf,.txt,.md"
                :maxFileSize="15000000"
                @select="onFileSelect"
                chooseLabel="選擇文件"
                class="w-full"
              />
              <small class="text-500 block mt-1">支援：DOCX、PDF、TXT（大於 15MB 將遭拒絕）</small>
            </div>

            <div v-if="selectedFile" class="surface-100 border-round p-3 mb-3">
              <div class="flex align-items-center justify-content-between">
                <div class="flex align-items-center gap-2">
                  <i class="pi pi-file text-2xl text-primary"></i>
                  <div>
                    <div class="font-semibold text-sm">{{ selectedFile.name }}</div>
                    <div class="text-xs text-500">{{ formatFileSize(selectedFile.size) }}</div>
                  </div>
                </div>
                <Button icon="pi pi-times" text rounded severity="danger" @click="selectedFile = null" />
              </div>
            </div>

            <div class="field mb-4">
              <label class="font-semibold mb-1 block">補充說明（可選）</label>
              <Textarea
                v-model="additionalContext"
                rows="3"
                class="w-full"
                placeholder="例如：這是一份內控制度 CA-100 的不動產循環，請注意泳道與表單..."
              />
            </div>

            <Button
              label="開始分析"
              icon="pi pi-sparkles"
              :loading="isLoading"
              :disabled="!selectedFile"
              @click="analyzeDocument"
              class="w-full"
            />
          </div>

          <!-- ── Chat area (Step 1+) ── -->
          <template v-else>
            <div class="flex align-items-center justify-content-between mb-3">
              <h2 class="text-heading-md m-0 deloitte-green-dot">
                <i class="pi pi-comments mr-2 text-green-500"></i>對話修改
              </h2>
              <Button
                label="重新開始"
                icon="pi pi-refresh"
                text
                severity="secondary"
                size="small"
                @click="restart"
              />
            </div>

            <div class="mb-2">
               <Message severity="info" :closable="false" class="m-0 py-2">
                 💡 提示：雙擊右側節點可直接修改文字，AI 修改後會自動重新排版。
               </Message>
            </div>

            <!-- Chat messages -->
            <div class="chat-messages flex-1 overflow-y-auto mb-3" ref="chatContainer">
              <div
                v-for="(msg, idx) in displayMessages"
                :key="idx"
                class="mb-3"
                :class="msg.role === 'user' ? 'flex justify-content-end' : 'flex justify-content-start'"
              >
                <div
                  class="chat-bubble p-3 border-round"
                  :class="msg.role === 'user' ? 'chat-user' : 'chat-ai'"
                  style="max-width: 85%;"
                >
                  <div class="text-xs font-semibold mb-1 opacity-70">
                    {{ msg.role === 'user' ? '你' : '🤖 AI 分析師' }}
                  </div>
                  <div class="text-sm" style="white-space: pre-wrap;">{{ msg.content }}</div>
                </div>
              </div>

              <div v-if="isLoading" class="flex justify-content-start mb-3">
                <div class="chat-bubble chat-ai p-3 border-round">
                  <div class="text-xs font-semibold mb-1 opacity-70">🤖 AI 分析師</div>
                  <div class="flex align-items-center gap-2 text-sm text-500">
                    <ProgressSpinner style="width:18px;height:18px;" strokeWidth="6" />
                    正在更新流程圖結構...
                  </div>
                </div>
              </div>
            </div>

            <!-- Input box -->
            <div class="chat-input-row flex gap-2">
              <InputText
                v-model="userInput"
                class="flex-1"
                placeholder="例如：請將審核拆成初核與覆核..."
                @keyup.enter="sendMessage"
                :disabled="isLoading"
              />
              <Button
                icon="pi pi-send"
                :loading="isLoading"
                :disabled="!userInput.trim()"
                @click="sendMessage"
              />
            </div>
          </template>
        </div>
      </div>

      <!-- ───────────────────── Right Panel ───────────────────── -->
      <div class="col-12 lg:col-8 flex flex-column h-full">
        <div class="deloitte-card p-4 flex flex-column h-full" style="overflow: hidden; background: #0f172a;">

          <!-- Toolbar -->
          <div class="flex align-items-center justify-content-between mb-3 z-5">
            <h2 class="text-heading-md m-0 text-white">
              <i class="pi pi-sitemap mr-2 text-green-400"></i>互動流程畫布
            </h2>
            <div v-if="chartNodes.length" class="flex gap-2 flex-wrap">
              <Button
                label="重新排版 (Auto Layout)"
                icon="pi pi-align-center"
                size="small"
                outlined
                severity="success"
                @click="applyAutoLayout"
              />
              <Button
                label="下載 PPTX（可編輯）"
                icon="pi pi-desktop"
                size="small"
                :loading="isExportingPptx"
                @click="downloadPptx"
              />
            </div>
          </div>

          <!-- Flow Area -->
          <div class="chart-area flex-1 relative border-round overflow-hidden bg-white" style="background: #0f172a;">
            
            <!-- Loading -->
            <div v-if="isLoading && !chartNodes.length" class="absolute inset-0 z-5 flex flex-column align-items-center justify-content-center bg-black-alpha-40 text-white">
              <ProgressSpinner style="width:50px;height:50px;" />
              <p class="text-300 mt-3 font-medium">✨ AI 正在解析內控制度文件，建構知識圖譜...</p>
            </div>

            <!-- Empty state -->
            <div v-else-if="!chartNodes.length" class="absolute inset-0 flex flex-column align-items-center justify-content-center text-500">
              <i class="pi pi-share-alt text-6xl mb-4 opacity-20 text-white"></i>
              <p class="m-0 text-lg font-medium text-400">請在左側上傳文件，開始 AI 視覺化流程</p>
            </div>

            <!-- Vue Flow Canvas -->
            <VueFlow
              v-else
              v-model:nodes="chartNodes"
              v-model:edges="chartEdges"
              :node-types="nodeTypes"
              :default-edge-options="{ type: 'smoothstep', animated: true }"
              fit-view-on-init
              class="vue-flow-theme"
              @nodeDoubleClick="onNodeDoubleClick"
            >
              <Background variant="dots" :gap="20" :size="1" color="#334155" />
              <Controls />
              <MiniMap node-color="#1e293b" mask-color="rgba(0,0,0,0.5)" class="border-round border-1 border-gray-700" />
            </VueFlow>
            
            <!-- Editing Dialog (Invisible input via PrimeVue Dialog overlay) -->
            <Dialog v-model:visible="isEditingNode" header="編輯節點文字" :style="{ width: '300px' }" modal>
              <div class="flex flex-column gap-3 mt-3">
                <InputText v-model="editNodeLabel" autofocus @keyup.enter="saveNodeEdit" />
                <Button label="儲存" icon="pi pi-check" @click="saveNodeEdit" size="small" />
              </div>
            </Dialog>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, markRaw } from 'vue';
import { useToast } from 'primevue/usetoast';
import apiClient from '../api/client';
import dagre from 'dagre';

// PrimeVue
import Button from 'primevue/button';
import FileUpload from 'primevue/fileupload';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Tag from 'primevue/tag';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Dialog from 'primevue/dialog';

// Vue Flow
import { VueFlow, useVueFlow } from '@vue-flow/core';
import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css';
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';
import { MiniMap } from '@vue-flow/minimap';

// Custom Nodes
import StartEndNode from '../components/flowchart/nodes/StartEndNode.vue';
import ProcessNode from '../components/flowchart/nodes/ProcessNode.vue';
import ControlNode from '../components/flowchart/nodes/ControlNode.vue';
import DocumentNode from '../components/flowchart/nodes/DocumentNode.vue';

const nodeTypes: any = {
  start: markRaw(StartEndNode),
  end: markRaw(StartEndNode),
  process: markRaw(ProcessNode),
  control: markRaw(ControlNode),
  document: markRaw(DocumentNode),
};

const toast = useToast();
const { fitView } = useVueFlow();

// ─── State ──────────────────────────────────────────────────────────────────
const step = ref(0);
const isLoading = ref(false);
const isExportingPptx = ref(false);
const errorMsg = ref('');

const selectedFile = ref<File | null>(null);
const additionalContext = ref('');

const messages = ref<{ role: string; content: string }[]>([]);
const displayMessages = ref<{ role: string; content: string }[]>([]);

const userInput = ref('');
const explanation = ref('');

// Vue Flow Data
const chartNodes = ref<any[]>([]);
const chartEdges = ref<any[]>([]);

// Node Editing
const isEditingNode = ref(false);
const editNodeId = ref('');
const editNodeLabel = ref('');

const chatContainer = ref<HTMLElement | null>(null);

// ─── Dagre Layout Engine ────────────────────────────────────────────────────
const applyAutoLayout = () => {
  if (!chartNodes.value.length) return;
  
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: 'TB', nodesep: 100, ranksep: 120, edgesep: 40 });
  g.setDefaultEdgeLabel(() => ({}));

  const nodeDimensions = {
    start: { w: 120, h: 48 },
    end: { w: 120, h: 48 },
    process: { w: 160, h: 60 },
    control: { w: 160, h: 80 },
    document: { w: 120, h: 60 }
  };

  chartNodes.value.forEach((n) => {
    const dim = nodeDimensions[n.type as keyof typeof nodeDimensions] || { w: 150, h: 50 };
    g.setNode(n.id, { width: dim.w, height: dim.h });
  });

  chartEdges.value.forEach((e) => {
    g.setEdge(e.source, e.target);
  });

  dagre.layout(g);

  // Apply layout to ref
  chartNodes.value = chartNodes.value.map((n) => {
    const nodeWithPosition = g.node(n.id);
    return {
      ...n,
      position: {
        x: nodeWithPosition.x - (nodeDimensions[n.type as keyof typeof nodeDimensions]?.w || 150) / 2,
        y: nodeWithPosition.y - (nodeDimensions[n.type as keyof typeof nodeDimensions]?.h || 50) / 2,
      },
      targetPosition: 'top',
      sourcePosition: 'bottom',
    };
  });

  // Re-fit view after tick
  setTimeout(() => {
    fitView({ duration: 800, padding: 0.2 });
  }, 50);
};

// ─── Data Mapping ───────────────────────────────────────────────────────────
const parseApiPayloadToVueFlow = (apiNodes: any[], apiEdges: any[]) => {
  const vNodes = apiNodes.map((n: any) => ({
    id: n.id,
    type: n.type,
    data: { label: n.label, lane: n.lane, isStart: n.type === 'start', isEnd: n.type === 'end' },
    position: { x: 0, y: 0 } // temporary
  }));

  const vEdges = apiEdges.map((e: any, idx: number) => ({
    id: `e-${e.from}-${e.to}-${idx}`,
    source: e.from,
    target: e.to,
    label: e.label || '',
    type: 'smoothstep',
    animated: true,
    style: { stroke: '#94a3b8', strokeWidth: 2 },
    labelBgPadding: [6, 4],
    labelBgBorderRadius: 4,
    labelBgStyle: { fill: '#1e293b', fillOpacity: 0.9 },
    labelStyle: { fill: '#cbd5e1', fontWeight: 600, fontSize: 12 }
  }));

  chartNodes.value = vNodes;
  chartEdges.value = vEdges;

  // Run layout
  applyAutoLayout();
};


// ─── Helpers ─────────────────────────────────────────────────────────────────
const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

const scrollChat = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const onFileSelect = (event: any) => {
  selectedFile.value = event.files[0] ?? null;
};

const onNodeDoubleClick = (event: any) => {
  editNodeId.value = event.node.id;
  editNodeLabel.value = event.node.data.label;
  isEditingNode.value = true;
};

const saveNodeEdit = () => {
  const idx = chartNodes.value.findIndex(n => n.id === editNodeId.value);
  if (idx !== -1) {
    chartNodes.value[idx].data.label = editNodeLabel.value;
  }
  isEditingNode.value = false;
};

// ─── API calls ────────────────────────────────────────────────────────────────
const analyzeDocument = async () => {
  if (!selectedFile.value) return;
  isLoading.value = true;
  errorMsg.value = '';

  try {
    const formData = new FormData();
    formData.append('file', selectedFile.value);
    if (additionalContext.value.trim()) {
      formData.append('additional_context', additionalContext.value);
    }

    const res: any = await apiClient.post('/flowchart/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000,
    });

    if (res.status === 'success') {
      messages.value = res.messages;
      explanation.value = res.explanation;
      
      // Parse to Vue Flow Format
      parseApiPayloadToVueFlow(res.nodes || [], res.edges || []);

      const firstAiMsg = messages.value.find(m => m.role === 'assistant');
      displayMessages.value = [];
      if (firstAiMsg) {
        displayMessages.value.push({
          role: 'assistant',
          content: `✅ 我已分析完文件「${selectedFile.value?.name}」並產生互動式畫布！\n\n${res.explanation}\n\n你可以直接在右側拖拉節點與連線，雙擊可以修改文字。如果需要大幅結構修改，也可以繼續跟我說！`,
        });
      }

      step.value = 1;
      await scrollChat();
      toast.add({ severity: 'success', summary: '分析完成', detail: '已產出 Vue Flow 畫布', life: 3000 });
    }
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || err.message || '分析失敗，請重試';
    toast.add({ severity: 'error', summary: '發生錯誤', detail: errorMsg.value, life: 5000 });
  } finally {
    isLoading.value = false;
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;

  const userText = userInput.value.trim();
  userInput.value = '';

  displayMessages.value.push({ role: 'user', content: userText });
  await scrollChat();

  isLoading.value = true;
  errorMsg.value = '';

  try {
    const res: any = await apiClient.post('/flowchart/chat', {
      messages: messages.value,
      user_message: userText,
    }, { timeout: 120000 });

    if (res.status === 'success') {
      messages.value = res.messages;
      explanation.value = res.explanation;
      
      parseApiPayloadToVueFlow(res.nodes || [], res.edges || []);

      displayMessages.value.push({
        role: 'assistant',
        content: `✅ 畫布結構已更新並重新排版！\n\n${res.explanation}`,
      });
      await scrollChat();
    }
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || err.message || '傳送失敗，請重試';
    displayMessages.value.push({
      role: 'assistant',
      content: '❌ 發生錯誤，請重試。',
    });
  } finally {
    isLoading.value = false;
  }
};

// ─── Download ─────────────────────────────────────────────────────────────────
const downloadPptx = async () => {
  if (!chartNodes.value.length) return;
  isExportingPptx.value = true;
  
  // Transform Vue Flow nodes back to API format, preserving the layout positions!
  const apiNodes = chartNodes.value.map(n => ({
    id: n.id,
    type: n.type,
    label: n.data.label,
    lane: n.data.lane,
    position: n.position // Send the latest coordinates back to server!
  }));

  const apiEdges = chartEdges.value.map(e => ({
    from: e.source,
    to: e.target,
    label: e.label || ''
  }));

  try {
    const response = await apiClient.post(
      '/flowchart/export-pptx',
      {
        nodes: apiNodes,
        edges: apiEdges,
        title: selectedFile.value?.name?.replace(/\.[^.]+$/, '') ?? '內控流程圖',
      },
      { responseType: 'blob', timeout: 60000 }
    );
    const blob = new Blob([response as any], {
      type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vueflow_${new Date().toISOString().slice(0, 10)}.pptx`;
    a.click();
    URL.revokeObjectURL(url);
    toast.add({ severity: 'success', summary: '下載成功', detail: 'PPTX 可編輯檔案已儲存', life: 3000 });
  } catch (err: any) {
    toast.add({ severity: 'error', summary: '匯出失敗', detail: err.message || '請重試', life: 3000 });
  } finally {
    isExportingPptx.value = false;
  }
};

const restart = () => {
  step.value = 0;
  messages.value = [];
  displayMessages.value = [];
  chartNodes.value = [];
  chartEdges.value = [];
  explanation.value = '';
  selectedFile.value = null;
  additionalContext.value = '';
  userInput.value = '';
};
</script>

<style scoped>
.flowchart-page {
  min-height: 100vh;
  background: var(--surface-ground);
}

.chat-messages {
  flex: 1;
  min-height: 0;
}

.chat-bubble {
  word-break: break-word;
  line-height: 1.5;
}

.chat-user {
  background: var(--primary-color);
  color: white;
}

.chat-ai {
  background: var(--surface-100);
  border: 1px solid var(--surface-border);
}

.vue-flow-theme {
  /* Vue Flow Custom Theme Configuration */
  --vf-node-bg: #1e293b;
  --vf-node-text: #fff;
  --vf-connection-path: #94a3b8;
  --vf-handle: #475569;
}

/* Ensure controls have visible icons in dark theme */
:deep(.vue-flow__controls) {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid #334155;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
  border-radius: 8px;
  overflow: hidden;
}

:deep(.vue-flow__controls-button) {
  background: transparent;
  border-bottom: 1px solid #334155;
  color: #cbd5e1;
}
:deep(.vue-flow__controls-button:hover) {
  background: rgba(255, 255, 255, 0.1);
}
:deep(.vue-flow__controls-button svg) {
  fill: currentColor;
}
</style>
