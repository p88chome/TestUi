<template>
  <div class="meeting-minutes-page p-6">
    <!-- Header -->
    <div class="flex align-items-center justify-content-between mb-5">
      <div>
        <h1 class="text-heading-xl m-0 mb-2 deloitte-green-dot">
          <i class="pi pi-microphone mr-2 text-green-500"></i>
          會議紀錄助手
        </h1>
        <p class="text-body-lg m-0">將會議對話轉換為結構化會議紀錄</p>
      </div>
      <Tag :value="'MVP'" severity="info" class="font-bold" />
    </div>

    <!-- Main Content Grid -->
    <div class="grid">
      <!-- Left Panel: Input -->
      <div class="col-12 lg:col-6">
        <div class="deloitte-card p-4 h-full">
          <!-- Input Type Tabs -->
          <TabView v-model:activeIndex="activeTab" class="mb-4">
            <TabPanel value="0">
              <template #header>
                <i class="pi pi-pencil mr-2"></i>
                <span>文字輸入</span>
              </template>
              
              <!-- Text Input Form -->
              <div class="flex flex-column gap-4">
                <div class="field">
                  <label for="meetingTitle" class="font-semibold mb-2 block">會議標題 (選填)</label>
                  <InputText 
                    id="meetingTitle" 
                    v-model="form.title" 
                    placeholder="例：Q1 內控會議"
                    class="w-full"
                  />
                </div>
                
                <div class="field">
                  <label for="meetingDate" class="font-semibold mb-2 block">會議日期</label>
                  <Calendar 
                    id="meetingDate" 
                    v-model="form.date" 
                    dateFormat="yy-mm-dd"
                    class="w-full"
                  />
                </div>
                
                <div class="field">
                  <label for="participants" class="font-semibold mb-2 block">出席者 (選填)</label>
                  <InputText 
                    id="participants" 
                    v-model="form.participants" 
                    placeholder="例：Tony, Mary, John"
                    class="w-full"
                  />
                </div>
                
                <div class="field">
                  <div class="flex justify-content-between align-items-center mb-2">
                    <label for="content" class="font-semibold block">
                      會議內容 <span class="text-red-500">*</span>
                    </label>
                    <FileUpload
                      mode="basic"
                      name="textfile"
                      :auto="true"
                      accept=".txt,.md"
                      :maxFileSize="1000000"
                      @select="onTextFileSelect"
                      chooseLabel="匯入文字檔"
                      class="p-button-sm p-button-outlined p-button-secondary"
                    />
                  </div>
                  <Textarea 
                    id="content" 
                    v-model="form.content" 
                    rows="12"
                    placeholder="請貼上會議對話或逐字稿...

範例：
Tony: 今天主要討論 Q1 預算分配
Mary: 我建議研發部門增加 10%
John: 同意，但需要重新評估人力成本
Tony: 好，那我們決議...
"
                    class="w-full"
                    :class="{ 'p-invalid': !form.content && submitted }"
                  />
                  <small v-if="!form.content && submitted" class="p-error">
                    請輸入會議內容
                  </small>
                </div>
              </div>
            </TabPanel>
            
            <TabPanel value="1">
              <template #header>
                <i class="pi pi-upload mr-2"></i>
                <span>音訊上傳</span>
              </template>
              
              <!-- Audio/Video Upload -->
              <div class="flex flex-column gap-4">
                <div class="field">
                  <label class="font-semibold mb-2 block">上傳音訊或影片檔案</label>
                  <FileUpload
                    mode="basic"
                    name="audio"
                    :auto="false"
                    accept=".mp3,.wav,.m4a,.webm,.mp4,.mov,.avi,.mkv"
                    :maxFileSize="100000000"
                    @select="onAudioSelect"
                    chooseLabel="選擇檔案"
                    class="w-full"
                  />
                  <small class="text-500 block mt-2">
                    支援格式: MP3, WAV, M4A, WebM, MP4, MOV, AVI, MKV (最大 100MB)
                  </small>
                </div>
                
                <div v-if="audioFile" class="surface-100 border-round p-3">
                  <div class="flex align-items-center justify-content-between">
                    <div class="flex align-items-center gap-2">
                      <i class="pi pi-file text-2xl text-primary"></i>
                      <div>
                        <div class="font-semibold">{{ audioFile.name }}</div>
                        <div class="text-sm text-500">{{ formatFileSize(audioFile.size) }}</div>
                      </div>
                    </div>
                    <Button 
                      icon="pi pi-times" 
                      text 
                      rounded 
                      severity="danger"
                      @click="clearAudioFile"
                    />
                  </div>
                </div>

                <div v-if="isTranscribing" class="flex flex-column align-items-center py-4">
                  <ProgressSpinner style="width: 50px; height: 50px" />
                  <p class="text-500 mt-3">正在轉錄音訊，請稍候...</p>
                  <small class="text-500">首次使用時需下載模型，可能需要數分鐘</small>
                </div>
                
                <Button 
                  v-if="audioFile && !isTranscribing"
                  label="開始轉錄"
                  icon="pi pi-play"
                  :disabled="!audioFile"
                  @click="transcribeAudio"
                  class="w-full"
                />
                
                <Message v-if="form.content && activeTab === 1" severity="success" class="mt-2">
                  轉錄完成！文字已自動填入下方，您可以編輯後再生成會議紀錄。
                </Message>

                <div v-if="form.content && activeTab === 1" class="field">
                  <label for="transcribedContent" class="font-semibold mb-2 block">
                    轉錄文字 (可編輯)
                  </label>
                  <Textarea 
                    id="transcribedContent" 
                    v-model="form.content" 
                    rows="10"
                    class="w-full"
                  />
                </div>
              </div>
            </TabPanel>
          </TabView>
          
          <!-- Generate Button -->
          <div class="flex justify-content-end gap-2 mt-4">
            <Button 
              label="清除" 
              icon="pi pi-trash" 
              class="p-button-outlined p-button-secondary"
              @click="clearForm"
            />
            <Button 
              label="生成會議紀錄" 
              icon="pi pi-sparkles"
              :loading="isGenerating"
              :disabled="!form.content"
              @click="generateMinutes"
            />
          </div>
        </div>
      </div>
      
      <!-- Right Panel: Output -->
      <div class="col-12 lg:col-6">
        <div class="deloitte-card p-4 h-full flex flex-column">
          <div class="flex align-items-center justify-content-between mb-3">
            <h2 class="text-heading-lg m-0 deloitte-green-dot">
              <i class="pi pi-file-edit mr-2 text-green-500"></i>
              會議紀錄輸出
            </h2>
            
            <div class="flex gap-2" v-if="output">
              <Button 
                icon="pi pi-copy" 
                class="p-button-outlined p-button-sm"
                v-tooltip.top="'複製'"
                @click="copyToClipboard"
              />
              <SplitButton 
                label="匯出" 
                icon="pi pi-download"
                :model="exportOptions"
                class="p-button-sm"
                @click="exportMarkdown"
              />
            </div>
          </div>
          
          <!-- Output Area -->
          <div class="flex-1 overflow-auto surface-100 border-round p-3" style="min-height: 400px;">
            <div v-if="isGenerating" class="flex flex-column align-items-center justify-content-center h-full">
              <ProgressSpinner style="width: 50px; height: 50px" />
              <p class="text-500 mt-3">AI 正在生成會議紀錄...</p>
            </div>
            
            <div v-else-if="output" class="markdown-content" v-html="renderedOutput"></div>
            
            <div v-else class="flex flex-column align-items-center justify-content-center h-full text-500">
              <i class="pi pi-inbox text-5xl mb-3 opacity-30"></i>
              <p class="m-0">會議紀錄將顯示在這裡</p>
              <p class="text-sm m-0 mt-2">請在左側輸入會議內容後點擊「生成會議紀錄」</p>
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
import { ref, computed } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { useToast } from 'primevue/usetoast';
import apiClient from '../api/client';

// PrimeVue Components
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Calendar from 'primevue/calendar';
import Button from 'primevue/button';
import SplitButton from 'primevue/splitbutton';
import FileUpload from 'primevue/fileupload';
import Message from 'primevue/message';
import Tag from 'primevue/tag';
import ProgressSpinner from 'primevue/progressspinner';

const toast = useToast();

// State
const activeTab = ref(0);
const submitted = ref(false);
const isGenerating = ref(false);
const isTranscribing = ref(false);
const output = ref('');
const errorMsg = ref('');
const audioFile = ref<File | null>(null);

const form = ref({
  title: '',
  date: new Date(),
  participants: '',
  content: ''
});

// Computed
const renderedOutput = computed(() => {
  if (!output.value) return '';
  return DOMPurify.sanitize(marked(output.value) as string);
});

// Export options
const exportOptions = [
  {
    label: 'Markdown (.md)',
    icon: 'pi pi-file',
    command: () => exportMarkdown()
  },
  {
    label: 'Word (.docx)',
    icon: 'pi pi-file-word',
    command: () => exportDocx()
  }
];

// Methods
const formatDate = (date: Date | null | undefined): string => {
  const d = date || new Date();
  const isoString = d.toISOString();
  return isoString.split('T')[0] || isoString.substring(0, 10);
};

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

const onAudioSelect = (event: any) => {
  audioFile.value = event.files[0];
  form.value.content = ''; // Clear previous content
};

const clearAudioFile = () => {
  audioFile.value = null;
  form.value.content = '';
};

const onTextFileSelect = async (event: any) => {
  const file = event.files[0];
  if (!file) return;

  try {
    const text = await file.text();
    form.value.content = text;
    toast.add({
      severity: 'success',
      summary: '匯入成功',
      detail: `已讀取 ${file.name}`,
      life: 2000
    });
  } catch (err) {
    console.error('Read file error:', err);
    toast.add({
      severity: 'error',
      summary: '匯入失敗',
      detail: '無法讀取檔案內容',
      life: 3000
    });
  }
};

const transcribeAudio = async () => {
  if (!audioFile.value) return;
  
  isTranscribing.value = true;
  errorMsg.value = '';
  
  try {
    const formData = new FormData();
    formData.append('file', audioFile.value);
    formData.append('method', 'whisper');
    formData.append('model_size', 'base');
    formData.append('language', 'zh');
    
    
    const response : any = await apiClient.post('/meeting/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    if (response.status === 'success') {
      form.value.content = response.transcript;
      toast.add({
        severity: 'success',
        summary: '轉錄完成',
        detail: `已成功轉錄 ${audioFile.value.name}`,
        life: 3000
      });
    } else {
      errorMsg.value = '轉錄失敗';
      toast.add({
        severity: 'error',
        summary: '轉錄失敗',
        detail: response.error || '請檢查檔案格式',
        life: 5000
      });
    }
  } catch (err: any) {
    console.error('Transcribe error:', err);
    const detail = err.response?.data?.detail || err.message || '轉錄時發生錯誤';
    errorMsg.value = detail;
    toast.add({
      severity: 'error',
      summary: '轉錄失敗',
      detail: detail,
      life: 5000
    });
  } finally {
    isTranscribing.value = false;
  }
};

const clearForm = () => {
  form.value = {
    title: '',
    date: new Date(),
    participants: '',
    content: ''
  };
  output.value = '';
  errorMsg.value = '';
  submitted.value = false;
};

const generateMinutes = async () => {
  submitted.value = true;
  
  if (!form.value.content.trim()) {
    toast.add({
      severity: 'warn',
      summary: '請輸入內容',
      detail: '會議內容不可為空',
      life: 3000
    });
    return;
  }
  
  isGenerating.value = true;
  errorMsg.value = '';
  
  try {
    const response : any = await apiClient.post('/meeting/generate', {
      content: form.value.content,
      meeting_title: form.value.title || null,
      meeting_date: formatDate(form.value.date),
      participants: form.value.participants || null
    });
    
    if (response.status === 'success') {
      output.value = response.meeting_minutes;
      toast.add({
        severity: 'success',
        summary: '生成完成',
        detail: '會議紀錄已生成',
        life: 3000
      });
    } else {
      errorMsg.value = response.error || '生成失敗';
    }
  } catch (err: any) {
    console.error('Generate error:', err);
    errorMsg.value = err.response?.data?.detail || err.message || '生成會議紀錄時發生錯誤';
  } finally {
    isGenerating.value = false;
  }
};

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(output.value);
    toast.add({
      severity: 'success',
      summary: '已複製',
      detail: '會議紀錄已複製到剪貼簿',
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
  a.download = `${form.value.title || 'meeting_minutes'}_${formatDate(new Date())}.md`;
  a.click();
  URL.revokeObjectURL(url);
  
  toast.add({
    severity: 'success',
    summary: '匯出成功',
    detail: 'Markdown 檔案已下載',
    life: 2000
  });
};

const exportDocx = async () => {
  try {
    const formData = new FormData();
    formData.append('content', output.value);
    formData.append('format', 'docx');
    formData.append('title', form.value.title || 'meeting_minutes');
    
    const response = await apiClient.post('/meeting/export', formData, {
      responseType: 'blob'
    });
    
    const url = URL.createObjectURL(response.data);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${form.value.title || 'meeting_minutes'}_${formatDate(new Date())}.docx`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.add({
      severity: 'success',
      summary: '匯出成功',
      detail: 'Word 檔案已下載',
      life: 2000
    });
  } catch (err: any) {
    toast.add({
      severity: 'error',
      summary: '匯出失敗',
      detail: err.response?.data?.detail || '無法匯出 Word 檔案',
      life: 3000
    });
  }
};
</script>

<style scoped>
.meeting-minutes-page {
  min-height: calc(100vh - 60px);
  background: var(--surface-ground);
}

.markdown-content {
  font-size: 0.95rem;
  line-height: 1.6;
}

.markdown-content :deep(h2) {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin-top: 0;
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
</style>
