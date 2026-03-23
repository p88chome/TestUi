<template>
  <div class="flowchart-page p-4">
    <!-- Header -->
    <div class="flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="text-heading-xl m-0 mb-1 deloitte-green-dot">
          <i class="pi pi-share-alt mr-2 text-green-500"></i>
          流程圖產生器
        </h1>
        <p class="text-body-lg m-0 text-500">上傳文件，AI 分析流程後產出互動式流程圖，可即時討論修改</p>
      </div>
      <Tag value="AI Powered" severity="success" class="font-bold" />
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
          <div v-if="step === 0">
            <h2 class="text-heading-md m-0 mb-3 deloitte-green-dot">
              <i class="pi pi-upload mr-2 text-green-500"></i>上傳文件
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
              <small class="text-500 block mt-1">支援：DOCX、PDF、TXT（最大 15MB）</small>
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
                placeholder="例如：此流程是採購申請流程，重點在審批步驟..."
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
                    正在更新流程圖...
                  </div>
                </div>
              </div>
            </div>

            <!-- Input box -->
            <div class="chat-input-row flex gap-2">
              <InputText
                v-model="userInput"
                class="flex-1"
                placeholder="例如：幫我把審核步驟拆成兩個..."
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
        <div class="deloitte-card p-4 flex flex-column h-full" style="overflow: hidden;">

          <!-- Toolbar -->
          <div class="flex align-items-center justify-content-between mb-3">
            <h2 class="text-heading-md m-0 deloitte-green-dot">
              <i class="pi pi-image mr-2 text-green-500"></i>流程圖預覽
            </h2>
            <div v-if="mermaidCode" class="flex gap-2 flex-wrap">
              <Button
                label="複製 Code"
                icon="pi pi-code"
                size="small"
                outlined
                @click="copyMermaidCode"
              />
              <Button
                label="下載 SVG"
                icon="pi pi-download"
                size="small"
                outlined
                severity="secondary"
                @click="downloadSvg"
              />
              <Button
                label="下載 PNG"
                icon="pi pi-image"
                size="small"
                outlined
                severity="secondary"
                @click="downloadPng"
              />
              <Button
                label="下載 PPTX（可編輯）"
                icon="pi pi-desktop"
                size="small"
                :loading="isExportingPptx"
                :disabled="!chartNodes.length"
                @click="downloadPptx"
              />
            </div>
          </div>

          <!-- Chart area -->
          <div class="chart-area flex-1 surface-100 border-round p-4 overflow-auto" ref="chartContainer">
            <!-- Loading -->
            <div v-if="isLoading && !mermaidCode" class="flex flex-column align-items-center justify-content-center h-full">
              <ProgressSpinner style="width:50px;height:50px;" />
              <p class="text-500 mt-3">AI 正在分析文件並產生流程圖...</p>
              <small class="text-500">這可能需要 10-30 秒</small>
            </div>

            <!-- Empty state -->
            <div v-else-if="!mermaidCode" class="flex flex-column align-items-center justify-content-center h-full text-500">
              <i class="pi pi-share-alt text-6xl mb-4 opacity-20"></i>
              <p class="m-0 text-lg font-medium">上傳文件後，流程圖將顯示在這裡</p>
              <p class="text-sm m-0 mt-2">AI 會自動識別流程步驟並視覺化呈現</p>
            </div>

            <!-- Mermaid chart -->
            <div v-else>
              <!-- Explanation -->
              <div v-if="explanation" class="mb-4 surface-0 border-round p-3 border-left-4 border-green-500">
                <div class="text-xs font-bold text-green-600 mb-2 uppercase tracking-wide">
                  <i class="pi pi-info-circle mr-1"></i>AI 分析說明
                </div>
                <div class="text-sm text-700" style="white-space: pre-wrap; line-height: 1.6;">{{ explanation }}</div>
              </div>

              <!-- Chart render target -->
              <div id="mermaid-render-area" ref="mermaidTarget" class="mermaid-wrapper"></div>
            </div>
          </div>

          <!-- Mermaid code editor (collapsible) -->
          <div v-if="mermaidCode" class="mt-3">
            <div
              class="flex align-items-center gap-2 cursor-pointer text-500 hover:text-700 transition-colors select-none"
              @click="showCodeEditor = !showCodeEditor"
            >
              <i :class="['pi text-xs', showCodeEditor ? 'pi-chevron-down' : 'pi-chevron-right']"></i>
              <span class="text-xs font-medium">檢視 / 編輯 Mermaid 原始碼</span>
            </div>
            <div v-if="showCodeEditor" class="mt-2">
              <Textarea
                v-model="mermaidCode"
                rows="6"
                class="w-full font-mono text-sm"
                @input="renderMermaid"
              />
            </div>
          </div>

          <!-- Error -->
          <Message v-if="errorMsg" severity="error" class="mt-3">{{ errorMsg }}</Message>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { useToast } from 'primevue/usetoast';
import mermaid from 'mermaid';
import apiClient from '../api/client';

import Button from 'primevue/button';
import FileUpload from 'primevue/fileupload';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Tag from 'primevue/tag';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';

mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' },
});

const toast = useToast();

// ─── State ──────────────────────────────────────────────────────────────────
const step = ref(0);               // 0 = upload, 1 = chat
const isLoading = ref(false);
const isExportingPptx = ref(false);
const errorMsg = ref('');

const selectedFile = ref<File | null>(null);
const additionalContext = ref('');

const messages = ref<{ role: string; content: string }[]>([]);   // Full LLM messages (system + history)
const displayMessages = ref<{ role: string; content: string }[]>([]);  // Only user / assistant

const userInput = ref('');
const mermaidCode = ref('');
const explanation = ref('');
const chartNodes = ref<any[]>([]);
const chartEdges = ref<any[]>([]);
const showCodeEditor = ref(false);

const chatContainer = ref<HTMLElement | null>(null);
const mermaidTarget = ref<HTMLElement | null>(null);

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

// ─── Mermaid ─────────────────────────────────────────────────────────────────
let renderCounter = 0;

const renderMermaid = async () => {
  if (!mermaidCode.value || !mermaidTarget.value) return;
  await nextTick();
  const id = `mermaid-chart-${++renderCounter}`;
  try {
    const code = sanitizeMermaidCode(mermaidCode.value.trim());
    const { svg } = await mermaid.render(id, code);
    mermaidTarget.value.innerHTML = svg;
  } catch (err) {
    console.warn('Mermaid render error:', err);
    if (mermaidTarget.value) {
      mermaidTarget.value.innerHTML = `
        <div style="border-left: 4px solid #ef4444; padding:1rem; background: #fef2f2; border-radius:6px;">
          <div style="color:#dc2626; font-weight:600; margin-bottom:0.5rem;">⚠️ 流程圖語法有誤</div>
          <pre style="font-size:12px; overflow:auto;">${mermaidCode.value}</pre>
        </div>`;
    }
  }
};

const sanitizeMermaidCode = (code: string): string => {
  const nodePattern = /([A-Za-z0-9_]+)(\[|\{|\()([^\]})\"']+?)(\]|\}|\))/g;
  return code.replace(nodePattern, (match, nodeId, open, label, close) => {
    const needsQuotes = /[、，,/\\()（）【】<>：:；;！!？?\-\s]/.test(label);
    if (needsQuotes && !label.startsWith('"') && !label.endsWith('"')) {
      return `${nodeId}${open}"${label}"${close}`;
    }
    return match;
  });
};

// Watch mermaidCode changes (from AI or manual edit)
watch(mermaidCode, async (val) => {
  if (val) await renderMermaid();
});

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
      mermaidCode.value = res.mermaid_code;
      explanation.value = res.explanation;
      chartNodes.value = res.nodes ?? [];
      chartEdges.value = res.edges ?? [];

      // Show first AI reply in display messages
      const firstAiMsg = messages.value.find(m => m.role === 'assistant');

      displayMessages.value = [];
      if (firstAiMsg) {
        displayMessages.value.push({
          role: 'assistant',
          content: `✅ 我已分析完文件「${selectedFile.value?.name}」並產生初始流程圖！\n\n${res.explanation}\n\n請問你想修改哪個部分？`,
        });
      }

      step.value = 1;
      await scrollChat();

      toast.add({ severity: 'success', summary: '分析完成', detail: '流程圖已生成', life: 3000 });
    }
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || err.message || '分析失敗，請重試';
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
      mermaidCode.value = res.mermaid_code;
      explanation.value = res.explanation;
      chartNodes.value = res.nodes ?? [];
      chartEdges.value = res.edges ?? [];

      displayMessages.value.push({
        role: 'assistant',
        content: `✅ 流程圖已更新！\n\n${res.explanation}`,
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
const getSvgElement = (): SVGElement | null => {
  return mermaidTarget.value?.querySelector('svg') ?? null;
};

const downloadSvg = () => {
  const svg = getSvgElement();
  if (!svg) return;
  const svgStr = new XMLSerializer().serializeToString(svg);
  const blob = new Blob([svgStr], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `flowchart_${new Date().toISOString().slice(0, 10)}.svg`;
  a.click();
  URL.revokeObjectURL(url);
  toast.add({ severity: 'success', summary: '下載成功', detail: 'SVG 已儲存', life: 2000 });
};

const downloadPng = async () => {
  const svg = getSvgElement();
  if (!svg) return;
  const svgStr = new XMLSerializer().serializeToString(svg);
  const canvas = document.createElement('canvas');
  const scale = 3; // High-DPI
  const w = svg.getBoundingClientRect().width || 800;
  const h = svg.getBoundingClientRect().height || 600;
  canvas.width = w * scale;
  canvas.height = h * scale;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  ctx.scale(scale, scale);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, w, h);

  const img = new Image();
  img.onload = () => {
    ctx.drawImage(img, 0, 0, w, h);
    const pngUrl = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = pngUrl;
    a.download = `flowchart_${new Date().toISOString().slice(0, 10)}.png`;
    a.click();
    toast.add({ severity: 'success', summary: '下載成功', detail: 'PNG 已儲存', life: 2000 });
  };
  img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgStr)));
};

const copyMermaidCode = async () => {
  try {
    await navigator.clipboard.writeText(mermaidCode.value);
    toast.add({ severity: 'success', summary: '已複製', detail: 'Mermaid Code 已複製', life: 2000 });
  } catch {
    toast.add({ severity: 'error', summary: '複製失敗', detail: '請手動選取', life: 2000 });
  }
};

const downloadPptx = async () => {
  if (!chartNodes.value.length) return;
  isExportingPptx.value = true;
  try {
    const response = await apiClient.post(
      '/flowchart/export-pptx',
      {
        nodes: chartNodes.value,
        edges: chartEdges.value,
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
    a.download = `flowchart_${new Date().toISOString().slice(0, 10)}.pptx`;
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
  mermaidCode.value = '';
  explanation.value = '';
  chartNodes.value = [];
  chartEdges.value = [];
  errorMsg.value = '';
  selectedFile.value = null;
  additionalContext.value = '';
  userInput.value = '';
  showCodeEditor.value = false;
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

.mermaid-wrapper {
  display: flex;
  justify-content: center;
  min-height: 200px;
}

.mermaid-wrapper :deep(svg) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.chart-area {
  min-height: 0;
}
</style>
