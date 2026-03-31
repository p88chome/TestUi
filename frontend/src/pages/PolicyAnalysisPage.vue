<template>
  <div class="policy-analysis-page p-6">
    <!-- Header -->
    <div class="flex align-items-center justify-content-between mb-5">
      <div>
        <h1 class="text-heading-xl m-0 mb-2 deloitte-green-dot">
          <i class="pi pi-check-square mr-2 text-green-500"></i>
          制度差異分析
        </h1>
        <p class="text-body-lg m-0">比對管理辦法與訪談紀錄，產出精確的修改建議報告</p>
      </div>
      <Tag :value="'MVP'" severity="info" class="font-bold" />
    </div>

    <!-- Main Content Grid -->
    <div class="grid">
      <!-- Left Panel: Input -->
      <div class="col-12 lg:col-5">
        <div class="deloitte-card p-4 h-full">
          <h2 class="text-heading-lg m-0 mb-4 deloitte-green-dot">
            <i class="pi pi-upload mr-2 text-green-500"></i>
            上傳文件
          </h2>
          
          <!-- Policy File Upload -->
          <div class="field mb-4">
            <label class="font-semibold mb-2 block">
              管理辦法 <span class="text-red-500">*</span>
            </label>
            <FileUpload
              mode="basic"
              name="policy"
              :auto="false"
              accept=".docx,.pdf"
              :maxFileSize="10000000"
              @select="onPolicySelect"
              chooseLabel="選擇檔案"
              class="w-full"
            />
            <small class="text-500 block mt-2">
              支援格式: DOCX、PDF（最大 10MB）
            </small>
            
            <div v-if="policyFile" class="surface-100 border-round p-3 mt-2">
              <div class="flex align-items-center justify-content-between">
                <div class="flex align-items-center gap-2">
                  <i class="pi pi-file-word text-2xl text-primary"></i>
                  <div>
                    <div class="font-semibold">{{ policyFile.name }}</div>
                    <div class="text-sm text-500">{{ formatFileSize(policyFile.size) }}</div>
                  </div>
                </div>
                <Button 
                  icon="pi pi-times" 
                  text 
                  rounded 
                  severity="danger"
                  @click="clearPolicyFile"
                />
              </div>
            </div>
          </div>
          
          <Divider />
          
          <!-- Interview Files Upload -->
          <div class="field mb-4">
            <label class="font-semibold mb-2 block">
              訪談紀錄 <span class="text-red-500">*</span>
              <Tag :value="`已選 ${interviewFiles.length} 份`" severity="info" class="ml-2" />
            </label>
            <FileUpload
              mode="basic"
              name="interviews"
              :auto="false"
              accept=".docx,.pdf"
              :maxFileSize="10000000"
              :multiple="true"
              @select="onInterviewSelect"
              chooseLabel="選擇檔案 (可多選)"
              class="w-full"
            />
            <small class="text-500 block mt-2">
              可一次選擇多個 DOCX 或 PDF 檔案
            </small>
            
            <div v-for="(file, index) in interviewFiles" :key="index" class="surface-100 border-round p-3 mt-2">
              <div class="flex align-items-center justify-content-between">
                <div class="flex align-items-center gap-2">
                  <i class="pi pi-file-word text-2xl text-blue-500"></i>
                  <div>
                    <div class="font-semibold">{{ file.name }}</div>
                    <div class="text-sm text-500">{{ formatFileSize(file.size) }}</div>
                  </div>
                </div>
                <Button 
                  icon="pi pi-times" 
                  text 
                  rounded 
                  severity="danger"
                  @click="removeInterviewFile(index)"
                />
              </div>
            </div>
          </div>
          
          <!-- Analyze Button -->
          <div class="flex justify-content-end gap-2 mt-4">
            <Button 
              label="清除全部" 
              icon="pi pi-trash" 
              class="p-button-outlined p-button-secondary"
              @click="clearAll"
            />
            <Button 
              label="開始分析" 
              icon="pi pi-sparkles"
              :loading="isAnalyzing"
              :disabled="!policyFile || interviewFiles.length === 0"
              @click="analyzeGap"
            />
          </div>
        </div>
      </div>
      
      <!-- Right Panel: Output -->
      <div class="col-12 lg:col-7">
        <div class="deloitte-card p-4 h-full flex flex-column">
          <div class="flex align-items-center justify-content-between mb-3">
            <h2 class="text-heading-lg m-0 deloitte-green-dot">
              <i class="pi pi-file-edit mr-2 text-green-500"></i>
              差異分析報告
            </h2>
            
            <div class="flex gap-2" v-if="output">
              <Button 
                icon="pi pi-copy" 
                class="p-button-outlined p-button-sm"
                v-tooltip.top="'複製'"
                @click="copyToClipboard"
              />
              <Button 
                label="匯出 Word" 
                icon="pi pi-file-word"
                class="p-button-sm"
                severity="secondary"
                :loading="isExportingWord"
                @click="downloadWord"
              />
              <Button 
                label="匯出 Markdown" 
                icon="pi pi-download"
                class="p-button-sm"
                @click="exportMarkdown"
              />
            </div>
          </div>
          
          <!-- Output Area -->
          <div class="flex-1 overflow-auto surface-100 border-round p-3" style="min-height: 500px;">
            <div v-if="isAnalyzing" class="flex flex-column align-items-center justify-content-center h-full">
              <ProgressSpinner style="width: 50px; height: 50px" />
              <p class="text-500 mt-3">AI 正在分析差異，請稍候...</p>
              <small class="text-500">此過程可能需要 1-2 分鐘</small>
            </div>
            
            <div v-else-if="output" class="markdown-content" v-html="renderedOutput"></div>
            
            <div v-else class="flex flex-column align-items-center justify-content-center h-full text-500">
              <i class="pi pi-search text-5xl mb-3 opacity-30"></i>
              <p class="m-0">差異分析報告將顯示在這裡</p>
              <p class="text-sm m-0 mt-2">請上傳管理辦法和訪談紀錄後點擊「開始分析」</p>
            </div>
          </div>
          
          <!-- Error Message -->
          <Message v-if="errorMsg" severity="error" class="mt-3">
            {{ errorMsg }}
          </Message>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import { marked } from 'marked';
import mermaid from 'mermaid';
import { useToast } from 'primevue/usetoast';
import apiClient from '../api/client';

// PrimeVue Components
import Button from 'primevue/button';
import FileUpload from 'primevue/fileupload';
import Message from 'primevue/message';
import Tag from 'primevue/tag';
import Divider from 'primevue/divider';
import ProgressSpinner from 'primevue/progressspinner';

const toast = useToast();

// Initialize Mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis'
  }
});

// State
const isAnalyzing = ref(false);
const isExportingWord = ref(false);
const output = ref('');
const errorMsg = ref('');
const policyFile = ref<File | null>(null);
const interviewFiles = ref<File[]>([]);

// Computed
// Computed
const fixedOutput = computed(() => {
  if (!output.value) return '';
  let text = output.value;
  
  // Fix: Check if we have 'flowchart TD' but missing the opening ```mermaid
  const hasFlowchart = /flowchart\s+TD/.test(text);
  const hasCodeBlock = /```mermaid/.test(text);

  if (hasFlowchart && !hasCodeBlock) {
    console.log('Detected detailed mermaid chart without code block, attempting fix...');
    // Attempt to wrap the flowchart block
    // We look for 'flowchart TD' and capture until we hit a double newline followed by text, horizontal rule, header, or specific keywords
    text = text.replace(
      /(flowchart\s+TD[\s\S]+?)(\n\n[^\n]|\n---|#|\n流程圖說明|$)/, 
      '\n```mermaid\n$1\n```\n$2'
    );
  }
  return text;
});

const renderedOutput = computed(() => {
  if (!fixedOutput.value) return '';
  // Configure marked if needed, though default usually works
  return marked(fixedOutput.value);
});

// Watch for output changes and render Mermaid
watch(output, async () => {
  if (output.value) {
    await nextTick();
    renderMermaid();
  }
});

const renderMermaid = async () => {
  await nextTick();
  const mermaidElements = document.querySelectorAll('.markdown-content pre code.language-mermaid');
  
  for (let i = 0; i < mermaidElements.length; i++) {
    const element = mermaidElements[i];
    if (!element) continue;
    
    let code = element.textContent || '';
    const container = element.parentElement;
    
    // Sanitize: Auto-quote node labels with special characters
    code = sanitizeMermaidCode(code);
    
    if (container && code) {
      try {
        const id = `mermaid-${Date.now()}-${i}`;
        const { svg } = await mermaid.render(id, code);
        container.outerHTML = `<div class="mermaid-container">${svg}</div>`;
      } catch (err) {
        console.error('Mermaid render error:', err);
        // Show error with raw code for debugging
        const escapedCode = code.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        container.outerHTML = `
          <div class="mermaid-error surface-100 border-round p-3 my-3" style="border-left: 4px solid #ef4444;">
            <div class="text-red-500 font-semibold mb-2">
              <i class="pi pi-exclamation-triangle mr-2"></i>流程圖繪製失敗
            </div>
            <details class="text-sm">
              <summary class="cursor-pointer text-600 mb-2">查看原始代碼</summary>
              <pre class="bg-gray-900 text-gray-100 p-3 border-round overflow-auto mt-2" style="white-space: pre-wrap; font-size: 0.8rem;">${escapedCode}</pre>
            </details>
          </div>
        `;
      }
    }
  }
};

/**
 * Sanitize Mermaid code by quoting node labels that contain special characters
 */
const sanitizeMermaidCode = (code: string): string => {
  // Pattern to match node definitions like A[label], B{label}, C(label), D[/label/]
  // We need to quote labels that contain special chars but aren't already quoted
  
  // Match: NodeId + bracket type + label content + closing bracket
  // Examples: A[開始]  B{決策}  C(結束)  D[/文件/]
  const nodePattern = /([A-Za-z0-9_]+)(\[|\{|\()([^\]}\)"']+?)(\]|\}|\))/g;
  
  return code.replace(nodePattern, (match, nodeId, openBracket, label, closeBracket) => {
    // Check if label contains special characters that need quoting
    const needsQuotes = /[、，,/\\()（）【】<>：:；;！!？?\-\s]/.test(label);
    
    if (needsQuotes && !label.startsWith('"') && !label.endsWith('"')) {
      // Add quotes around the label
      return `${nodeId}${openBracket}"${label}"${closeBracket}`;
    }
    return match;
  });
};

// Methods
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

const formatDate = (): string => {
  const dateStr = new Date().toISOString().split('T')[0];
  return dateStr ?? new Date().toISOString().substring(0, 10);
};

const onPolicySelect = (event: any) => {
  policyFile.value = event.files[0];
};

const clearPolicyFile = () => {
  policyFile.value = null;
};

const onInterviewSelect = (event: any) => {
  // Append new files
  for (const file of event.files) {
    interviewFiles.value.push(file);
  }
};

const removeInterviewFile = (index: number) => {
  interviewFiles.value.splice(index, 1);
};

const clearAll = () => {
  policyFile.value = null;
  interviewFiles.value = [];
  output.value = '';
  errorMsg.value = '';
};

const analyzeGap = async () => {
  if (!policyFile.value || interviewFiles.value.length === 0) {
    toast.add({
      severity: 'warn',
      summary: '請上傳檔案',
      detail: '需要上傳管理辦法和至少一份訪談紀錄',
      life: 3000
    });
    return;
  }
  
  isAnalyzing.value = true;
  errorMsg.value = '';
  output.value = ''; // Reset output for streaming
  
  try {
    const formData = new FormData();
    formData.append('policy_file', policyFile.value);
    for (const file of interviewFiles.value) {
      formData.append('interview_files', file);
    }
    
    // Using native fetch for streaming
    const baseUrl = import.meta.env.VITE_API_URL 
      ? (import.meta.env.VITE_API_URL.endsWith('/') ? import.meta.env.VITE_API_URL + 'api/v1' : import.meta.env.VITE_API_URL + '/api/v1')
      : '/api/v1';
    
    const token = localStorage.getItem('token');
    const response = await fetch(`${baseUrl}/policy/analyze`, {
      method: 'POST',
      body: formData,
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('登入已過期，請重新登入');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'API 伺服器傳回錯誤' }));
      throw new Error(errorData.detail || '連線失敗');
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    if (!reader) throw new Error('無法建立讀取流');

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const data = JSON.parse(line);
          if (data.status === 'content') {
            output.value += data.content;
          } else if (data.status === 'error') {
            errorMsg.value = data.error;
            toast.add({ severity: 'error', summary: '分析錯誤', detail: data.error, life: 5000 });
          } else if (data.status === 'extracting' || data.status === 'processing') {
            // Optional: update a status message if you have one
            console.log('Status:', data.message);
          }
        } catch (e) {
          console.warn('NDJSON parse error:', e);
        }
      }
    }

    if (!errorMsg.value) {
      toast.add({
        severity: 'success',
        summary: '分析完成',
        detail: '差異分析報告已生成',
        life: 3000
      });
    }
  } catch (err: any) {
    console.error('Analyze error:', err);
    errorMsg.value = err.message || '分析時發生錯誤';
    toast.add({ severity: 'error', summary: '發生錯誤', detail: errorMsg.value, life: 5000 });
  } finally {
    isAnalyzing.value = false;
  }
};

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(output.value);
    toast.add({
      severity: 'success',
      summary: '已複製',
      detail: '報告內容已複製到剪貼簿',
      life: 2000
    });
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: '複製失敗',
      detail: '請手動選取複製',
      life: 3000
    });
  }
};

const exportMarkdown = () => {
  const blob = new Blob([output.value], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `制度差異分析報告_${formatDate()}.md`;
  a.click();
  URL.revokeObjectURL(url);
  
  toast.add({
    severity: 'success',
    summary: '匯出成功',
    detail: 'Markdown 檔案已下載',
    life: 2000
  });
};

const downloadWord = async () => {
  if (!output.value) return;
  isExportingWord.value = true;
  try {
    const response = await apiClient.post(
      '/policy/export-docx',
      {
        report: output.value,
        policy_name: policyFile.value?.name?.replace(/\.[^.]+$/, '') ?? '制度差異分析報告',
      },
      { responseType: 'blob', timeout: 60000 }
    );
    
    // Check if the response is actually a JSON error hidden in a blob
    const responseBlob = response as unknown as Blob;
    if (responseBlob.type === 'application/json') {
      const text = await responseBlob.text();
      const errorData = JSON.parse(text);
      throw new Error(errorData.detail || '匯出 Word 失敗');
    }

    const url = URL.createObjectURL(responseBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `制度差異分析報告_${formatDate()}.docx`;
    a.click();
    URL.revokeObjectURL(url);
    toast.add({ severity: 'success', summary: '匯出成功', detail: 'Word 檔案已下載', life: 2000 });
  } catch (err: any) {
    console.error('Export error:', err);
    toast.add({ severity: 'error', summary: '匯出失敗', detail: err.message || '請重試', life: 5000 });
  } finally {
    isExportingWord.value = false;
  }
};
</script>

<style scoped>
.policy-analysis-page {
  min-height: calc(100vh - 60px);
  background: var(--surface-ground);
}

.markdown-content {
  font-size: 0.95rem;
  line-height: 1.6;
}

.markdown-content :deep(h1) {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color);
  margin-top: 0;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 3px solid var(--primary-color);
}

.markdown-content :deep(h2) {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-color);
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--primary-color);
}

.markdown-content :deep(h3) {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.markdown-content :deep(h4) {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 1.5rem;
  margin: 0.5rem 0;
}

.markdown-content :deep(li) {
  margin: 0.3rem 0;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid var(--surface-border);
  padding: 0.5rem 0.75rem;
  text-align: left;
}

.markdown-content :deep(th) {
  background: var(--surface-200);
  font-weight: 600;
}

.markdown-content :deep(strong) {
  color: var(--text-color);
}

.markdown-content :deep(p) {
  margin: 0.5rem 0;
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--surface-border);
  margin: 1.5rem 0;
}

/* Mermaid Flowchart Styles */
.markdown-content :deep(.mermaid-container) {
  background: var(--surface-0);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 1.5rem 0;
  border: 1px solid var(--surface-border);
  overflow-x: auto;
}

.markdown-content :deep(.mermaid-container svg) {
  max-width: 100%;
  height: auto;
}
</style>
