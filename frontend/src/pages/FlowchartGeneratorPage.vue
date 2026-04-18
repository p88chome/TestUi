<template>
  <div class="flowchart-page p-4">
    <!-- Header -->
    <div class="flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="text-heading-xl m-0 mb-1 deloitte-green-dot">
          <i class="pi pi-share-alt mr-2 text-green-500"></i>
          互動流程圖產生器
        </h1>
        <p class="text-body-lg m-0 text-500">上傳文件，AI 兩步拆解後產出互動畫布與 Mermaid 語法，可即時拖曳與切換檢視</p>
      </div>
      <Tag value="Vue Flow + Mermaid + AI Powered" severity="success" class="font-bold" />
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

          <!-- ── Upload / Paste area (Step 0) ── -->
          <div v-if="step === 0" class="flex-1 overflow-auto pr-2">
            <!-- Input mode toggle -->
            <div class="flex gap-2 mb-3">
              <Button
                :label="'📄 上傳檔案'"
                :severity="inputMode === 'file' ? 'success' : 'secondary'"
                :outlined="inputMode !== 'file'"
                size="small"
                @click="inputMode = 'file'"
                class="flex-1"
              />
              <Button
                :label="'✏️ 貼文字(單一子作業)'"
                :severity="inputMode === 'text' ? 'success' : 'secondary'"
                :outlined="inputMode !== 'text'"
                size="small"
                @click="inputMode = 'text'"
                class="flex-1"
              />
            </div>

            <!-- File mode -->
            <template v-if="inputMode === 'file'">
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
            </template>

            <!-- Text paste mode -->
            <template v-else>
              <h2 class="text-heading-md m-0 mb-3 deloitte-green-dot">
                <i class="pi pi-pencil mr-2 text-green-500"></i>貼上單一子作業說明
              </h2>
              <Message severity="info" :closable="false" class="mb-3">
                💡 一次貼一個子作業(例如 CS-101)的「作業程序」段落,產第一版流程圖後可拖拉/編輯節點。
              </Message>
              <div class="field mb-3">
                <label class="font-semibold mb-1 block">子作業文字 <span class="text-red-500">*</span></label>
                <Textarea
                  v-model="rawText"
                  rows="14"
                  class="w-full"
                  style="font-family: monospace; font-size: 13px;"
                  placeholder="CS-101 銷售預測及目標作業&#10;&#10;作業程序：&#10;1. ...&#10;2. ...&#10;&#10;使用表單：&#10;1. 年度銷售計畫"
                />
                <small class="text-500 block mt-1">純文字,建議 < 3000 字。AI 會產初版流程圖,你可在右側拖拉編輯。</small>
              </div>

              <Button
                label="產生流程圖初版"
                icon="pi pi-sparkles"
                :loading="isLoading"
                :disabled="!rawText.trim()"
                @click="extractFromText"
                class="w-full"
              />
            </template>
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
          <div class="flex align-items-center justify-content-between mb-3 z-5 flex-wrap gap-2">
            <h2 class="text-heading-md m-0 text-white">
              <i class="pi pi-sitemap mr-2 text-green-400"></i>互動流程畫布
            </h2>
            <div class="flex gap-2 flex-wrap align-items-center">
              <!-- View Mode Toggle -->
              <div v-if="chartNodes.length || mermaidCode" class="view-toggle flex border-round overflow-hidden">
                <button
                  :class="['toggle-btn px-3 py-1 text-sm font-semibold', viewMode === 'flow' ? 'toggle-active' : 'toggle-inactive']"
                  @click="viewMode = 'flow'"
                >
                  <i class="pi pi-share-alt mr-1"></i>Flow 圖
                </button>
                <button
                  :class="['toggle-btn px-3 py-1 text-sm font-semibold', viewMode === 'mermaid' ? 'toggle-active' : 'toggle-inactive']"
                  @click="switchToMermaid"
                >
                  <i class="pi pi-code mr-1"></i>Mermaid
                </button>
              </div>
              <template v-if="chartNodes.length && viewMode === 'flow'">
                <Button
                  label="重新排版"
                  icon="pi pi-align-center"
                  size="small"
                  outlined
                  severity="success"
                  @click="applyAutoLayout"
                />
                <Button
                  label="下載 PPTX"
                  icon="pi pi-desktop"
                  size="small"
                  :loading="isExportingPptx"
                  @click="downloadPptx"
                />
              </template>
            </div>
          </div>

          <!-- Flow Area -->
          <div class="chart-area flex-1 relative border-round overflow-hidden" style="background: #0f172a;">
            
            <!-- Loading -->
            <div v-if="isLoading && !chartNodes.length" class="absolute inset-0 z-5 flex flex-column align-items-center justify-content-center bg-black-alpha-40 text-white">
              <ProgressSpinner style="width:50px;height:50px;" />
              <p class="text-300 mt-3 font-medium">✨ AI 正在兩步拆解文件，建構知識圖譜...</p>
            </div>

            <!-- Empty state -->
            <div v-else-if="!chartNodes.length && !mermaidCode" class="absolute inset-0 flex flex-column align-items-center justify-content-center text-500">
              <i class="pi pi-share-alt text-6xl mb-4 opacity-20 text-white"></i>
              <p class="m-0 text-lg font-medium text-400">請在左側上傳文件，開始 AI 視覺化流程</p>
            </div>

            <!-- Vue Flow Canvas -->
            <VueFlow
              v-else-if="viewMode === 'flow'"
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

            <!-- Mermaid View -->
            <div v-else-if="viewMode === 'mermaid'" class="h-full flex flex-column overflow-hidden" style="background: #0f172a;">
              <!-- Mermaid rendered preview -->
              <div class="mermaid-preview flex-1 overflow-auto p-4 flex justify-content-center" style="background: #fff;">
                <div ref="mermaidContainer" class="w-full"></div>
              </div>
              <!-- Mermaid code editor -->
              <div class="mermaid-code-area border-top-1 border-gray-700" style="height: 200px; overflow: auto;">
                <div class="flex align-items-center justify-content-between px-3 py-2 bg-gray-900">
                  <span class="text-xs font-semibold text-gray-400">📝 Mermaid 語法（可直接編輯）</span>
                  <Button label="重新渲染" icon="pi pi-refresh" size="small" text severity="success" @click="renderMermaid" />
                </div>
                <Textarea
                  v-model="mermaidCode"
                  class="w-full border-none border-round-none"
                  style="min-height: 155px; background: #1e293b; color: #94a3b8; font-family: monospace; font-size: 12px; resize: none;"
                  @blur="renderMermaid"
                />
              </div>
            </div>
            
            <!-- Editing Dialog -->
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
import mermaid from 'mermaid';

mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'loose' });
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
import SwimlaneNode from '../components/flowchart/nodes/SwimlaneNode.vue';

const nodeTypes: any = {
  start: markRaw(StartEndNode),
  end: markRaw(StartEndNode),
  process: markRaw(ProcessNode),
  control: markRaw(ControlNode),
  document: markRaw(DocumentNode),
  swimlane: markRaw(SwimlaneNode),
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
const inputMode = ref<'file' | 'text'>('file');
const rawText = ref('');

const messages = ref<{ role: string; content: string }[]>([]);
const displayMessages = ref<{ role: string; content: string }[]>([]);

const userInput = ref('');
const explanation = ref('');

// Vue Flow Data
const chartNodes = ref<any[]>([]);
const chartEdges = ref<any[]>([]);

// Intermediate steps (from two-step LLM)
const currentSteps = ref<any>(null);

// Mermaid
const viewMode = ref<'flow' | 'mermaid'>('flow');
const mermaidCode = ref('');
const mermaidContainer = ref<HTMLElement | null>(null);

// Node Editing
const isEditingNode = ref(false);
const editNodeId = ref('');
const editNodeLabel = ref('');

const chatContainer = ref<HTMLElement | null>(null);

// Render Mermaid in the container
const renderMermaid = async () => {
  if (!mermaidContainer.value || !mermaidCode.value.trim()) return;
  try {
    mermaidContainer.value.innerHTML = '';
    const { svg } = await mermaid.render('mermaid-graph-' + Date.now(), mermaidCode.value);
    mermaidContainer.value.innerHTML = svg;
  } catch (e) {
    mermaidContainer.value.innerHTML = `<pre style="color:#ef4444;font-size:12px;">${e}</pre>`;
  }
};

const switchToMermaid = async () => {
  viewMode.value = 'mermaid';
  await nextTick();
  await renderMermaid();
};

const applyAutoLayout = () => {
  if (!chartNodes.value.length) return;
  
  const g = new dagre.graphlib.Graph({ compound: true });
  g.setGraph({ rankdir: 'TB', nodesep: 100, ranksep: 120, edgesep: 40 });
  g.setDefaultEdgeLabel(() => ({}));

  const nodeDimensions: Record<string, { w: number, h: number }> = {
    start: { w: 120, h: 48 },
    end: { w: 120, h: 48 },
    process: { w: 160, h: 60 },
    control: { w: 160, h: 100 },
    document: { w: 150, h: 80 }
  };

  // 1. Add Swimlanes as clusters
  const lanes = chartNodes.value.filter(n => n.type === 'swimlane');
  lanes.forEach(lane => {
    g.setNode(lane.id, { label: lane.data.label, clusterLabelPos: 'top' });
  });

  // 2. Add normal nodes and attach to parents
  const childNodes = chartNodes.value.filter(n => n.type !== 'swimlane');
  childNodes.forEach((n) => {
    const dim = nodeDimensions[n.type] || { w: 150, h: 50 };
    g.setNode(n.id, { width: dim.w, height: dim.h });
    if (n.parentNode) {
      g.setParent(n.id, n.parentNode);
    }
  });

  chartEdges.value.forEach((e) => {
    g.setEdge(e.source, e.target);
  });

  try {
    dagre.layout(g);
  } catch(e) {
    console.warn("Dagre layout issue", e); // fallback gracefully if bad structure
  }

  // Apply layout to ref
  chartNodes.value = chartNodes.value.map((n) => {
    const nodeData = g.node(n.id);
    if (!nodeData) return n;

    if (n.type === 'swimlane') {
      return {
        ...n,
        position: {
          x: nodeData.x - nodeData.width / 2,
          y: nodeData.y - nodeData.height / 2,
        },
        style: { width: `${nodeData.width + 40}px`, height: `${nodeData.height + 60}px` }
      };
    } else {
      let relativeX = nodeData.x - (nodeDimensions[n.type]?.w || 150) / 2;
      let relativeY = nodeData.y - (nodeDimensions[n.type]?.h || 50) / 2;

      if (n.parentNode) {
        const parentData = g.node(n.parentNode);
        if (parentData) {
          const parentAbsX = parentData.x - parentData.width / 2;
          const parentAbsY = parentData.y - parentData.height / 2;
          // shift back relative to parent bounding box + padding
          relativeX = relativeX - parentAbsX + 20;
          relativeY = relativeY - parentAbsY + 40;
        }
      }

      return {
        ...n,
        position: { x: relativeX, y: relativeY },
        targetPosition: 'top',
        sourcePosition: 'bottom',
      };
    }
  });

  // Re-fit view after tick
  setTimeout(() => {
    fitView({ duration: 800, padding: 0.2 });
  }, 50);
};

// ─── Data Mapping ───────────────────────────────────────────────────────────
const parseApiPayloadToVueFlow = (apiNodes: any[], apiEdges: any[]) => {
  const uniqueLanes = [...new Set(apiNodes.map((n: any) => n.lane || '預設部門'))];
  
  const laneNodes = uniqueLanes.map(lane => ({
    id: `lane-${lane}`,
    type: 'swimlane',
    data: { label: lane },
    position: { x: 0, y: 0 },
    style: { width: '400px', height: '800px' },
    zIndex: -1
  }));

  const vNodes = apiNodes.map((n: any) => ({
    id: n.id,
    type: n.type,
    data: { label: n.label, lane: n.lane, isStart: n.type === 'start', isEnd: n.type === 'end' },
    position: { x: 0, y: 0 },
    parentNode: `lane-${n.lane || '預設部門'}`,
    extent: 'parent'
  }));

  const vEdges = apiEdges.map((e: any, idx: number) => {
    const fromNode = apiNodes.find((n: any) => n.id === e.from);
    const toNode = apiNodes.find((n: any) => n.id === e.to);
    const isDoc = toNode?.type === 'document';
    const isFromDecision = fromNode?.type === 'control';
    const label = (e.label || '').toString().trim().toUpperCase();
    const isNo = label === 'N' || label === 'NO' || label === '否';
    const isYes = label === 'Y' || label === 'YES' || label === '是';

    // Handle routing:
    //   Y / 順流 / 無標籤 → 底進頂(預設)
    //   N / 退件回圈 → 從右側出,對方左側進(視覺上繞側邊,不壓主幹)
    let sourceHandle: string | undefined;
    let targetHandle: string | undefined;
    if (isFromDecision && isNo) {
      sourceHandle = 'right';
      targetHandle = 'left';
    }

    // 樣式:doc 虛線橘、N 紅、Y 綠、其他灰
    let stroke = '#475569';
    let strokeDasharray: string | undefined;
    if (isDoc) { stroke = '#ea580c'; strokeDasharray = '5 5'; }
    else if (isNo) { stroke = '#dc2626'; }
    else if (isYes) { stroke = '#16a34a'; }

    return {
      id: `e-${e.from}-${e.to}-${idx}`,
      source: e.from,
      target: e.to,
      sourceHandle,
      targetHandle,
      label: e.label || '',
      type: 'smoothstep',
      animated: !isDoc,
      style: { stroke, strokeWidth: 2, ...(strokeDasharray ? { strokeDasharray } : {}) },
      markerEnd: { type: 'arrowclosed', color: stroke, width: 18, height: 18 },
      labelBgPadding: [6, 4],
      labelBgBorderRadius: 4,
      labelBgStyle: { fill: '#1e293b', fillOpacity: 0.9 },
      labelStyle: { fill: '#cbd5e1', fontWeight: 700, fontSize: 13 },
    };
  });

  chartNodes.value = [...laneNodes, ...vNodes];
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
      currentSteps.value = res.steps ?? null;
      mermaidCode.value = res.mermaid ?? '';
      
      // Parse to Vue Flow Format
      parseApiPayloadToVueFlow(res.nodes || [], res.edges || []);

      displayMessages.value = [];
      displayMessages.value.push({
        role: 'assistant',
        content: `✅ 已完成兩步驟 AI 分析！\n\n${res.explanation}\n\n💡 右上角可切換「Flow 圖」或「Mermaid 語法」視圖。`,
      });

      step.value = 1;
      await scrollChat();
      toast.add({ severity: 'success', summary: '分析完成', detail: '已產出 Vue Flow 畫布 + Mermaid 語法', life: 3000 });
    }
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || err.message || '分析失敗，請重試';
    toast.add({ severity: 'error', summary: '發生錯誤', detail: errorMsg.value, life: 5000 });
  } finally {
    isLoading.value = false;
  }
};

const extractFromText = async () => {
  if (!rawText.value.trim()) return;
  isLoading.value = true;
  errorMsg.value = '';

  try {
    const res: any = await apiClient.post('/flowchart/extract-text', {
      text: rawText.value,
    }, { timeout: 120000 });

    if (res.status === 'success') {
      explanation.value = res.explanation;
      currentSteps.value = null;
      mermaidCode.value = res.mermaid ?? '';
      messages.value = [
        { role: 'system', content: '純文字抽取模式' },
        { role: 'user', content: rawText.value },
        { role: 'assistant', content: JSON.stringify({ nodes: res.nodes, edges: res.edges }) },
      ];

      parseApiPayloadToVueFlow(res.nodes || [], res.edges || []);

      displayMessages.value = [{
        role: 'assistant',
        content: `✅ 已產出初版。\n\n${res.explanation}\n\n💡 雙擊節點可改文字,拖拉可移動位置。右上可切換 Mermaid 視圖。`,
      }];

      step.value = 1;
      await scrollChat();
      toast.add({ severity: 'success', summary: '初版已生成', detail: '可開始編輯', life: 3000 });
    }
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || err.message || '產生失敗';
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
      steps: currentSteps.value ?? undefined,
    }, { timeout: 120000 });

    if (res.status === 'success') {
      messages.value = res.messages;
      explanation.value = res.explanation;
      if (res.steps) currentSteps.value = res.steps;
      if (res.mermaid) {
        mermaidCode.value = res.mermaid;
        // Re-render mermaid if we are currently in mermaid view
        if (viewMode.value === 'mermaid') await renderMermaid();
      }
      
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
  rawText.value = '';
  currentSteps.value = null;
  mermaidCode.value = '';
  viewMode.value = 'flow';
};
</script>

<style scoped>
.flowchart-page {
  min-height: 100vh;
  background: var(--surface-ground);
}

/* View Mode Toggle */
.view-toggle {
  background: #1e293b;
  border: 1px solid #334155;
}
.toggle-btn {
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}
.toggle-active {
  background: #16a34a;
  color: #fff;
}
.toggle-inactive {
  background: transparent;
  color: #94a3b8;
}
.toggle-inactive:hover {
  background: rgba(255,255,255,0.08);
  color: #e2e8f0;
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
