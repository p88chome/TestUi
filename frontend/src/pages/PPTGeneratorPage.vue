<template>
  <div class="ppt-generator-page p-6">
    <!-- Header -->
    <div class="flex align-items-center justify-content-between mb-5">
      <div>
        <h1 class="text-heading-xl m-0 mb-2 deloitte-green-dot">
          <i class="pi pi-desktop mr-2 text-green-500"></i>
          簡報生成器
        </h1>
        <p class="text-body-lg m-0">輸入主題，AI 自動搜尋資料並生成專業簡報</p>
      </div>
      <Tag :value="'Enterprise'" severity="success" class="font-bold" />
    </div>

    <!-- Mode Toggle -->
    <div class="flex gap-3 mb-4">
      <Button 
        :label="'AI 智能生成'" 
        :icon="'pi pi-sparkles'"
        :class="mode === 'ai' ? '' : 'p-button-outlined'"
        @click="mode = 'ai'"
      />
      <Button 
        :label="'手動輸入'" 
        :icon="'pi pi-pencil'"
        :class="mode === 'manual' ? '' : 'p-button-outlined'"
        @click="mode = 'manual'"
      />
    </div>

    <!-- Main Content Grid -->
    <div class="grid">
      <!-- Left Panel: Input -->
      <div class="col-12 lg:col-5">
        <div class="deloitte-card p-4 h-full">
          
          <!-- AI Mode -->
          <template v-if="mode === 'ai'">
            <h2 class="text-heading-lg m-0 mb-4 deloitte-green-dot">
              <i class="pi pi-sparkles mr-2 text-green-500"></i>
              AI 智能生成
            </h2>
            <p class="text-500 mb-4">只需輸入主題，AI 會自動搜尋網路資料並生成完整簡報</p>
            
            <!-- Topic -->
            <div class="field mb-4">
              <label class="font-semibold mb-2 block">
                簡報主題 <span class="text-red-500">*</span>
              </label>
              <InputText 
                v-model="aiTopic" 
                placeholder="例如：2024 年 AI 發展趨勢"
                class="w-full"
              />
            </div>
            
            <!-- Slide Count -->
            <div class="field mb-4">
              <label class="font-semibold mb-2 block">投影片數量</label>
              <div class="flex align-items-center gap-3">
                <Slider v-model="aiSlideCount" :min="3" :max="12" class="flex-1" />
                <span class="font-bold text-lg" style="width: 50px;">{{ aiSlideCount }} 張</span>
              </div>
            </div>
            
            <!-- Theme -->
            <div class="field mb-4">
              <label class="font-semibold mb-2 block">主題風格</label>
              <Dropdown
                v-model="selectedTheme"
                :options="themes"
                optionLabel="name"
                optionValue="id"
                placeholder="選擇主題"
                class="w-full"
              />
            </div>
            
            <!-- Generate Button -->
            <div class="flex justify-content-end gap-2 mt-4">
              <Button 
                label="AI 生成簡報" 
                icon="pi pi-sparkles"
                :loading="isGenerating"
                :disabled="!aiTopic"
                @click="aiGeneratePPT"
                class="w-full"
                size="large"
              />
            </div>
          </template>
          
          <!-- Manual Mode -->
          <template v-else>
            <h2 class="text-heading-lg m-0 mb-4 deloitte-green-dot">
              <i class="pi pi-pencil mr-2 text-green-500"></i>
              手動輸入
            </h2>
            
            <!-- Title -->
            <div class="field mb-4">
              <label class="font-semibold mb-2 block">
                簡報標題 <span class="text-red-500">*</span>
              </label>
              <InputText 
                v-model="title" 
                placeholder="輸入簡報標題"
                class="w-full"
              />
            </div>
            
            <!-- Subtitle -->
            <div class="field mb-4">
              <label class="font-semibold mb-2 block">副標題</label>
              <InputText 
                v-model="subtitle" 
                placeholder="輸入副標題（選填）"
                class="w-full"
              />
            </div>
            
            <!-- Theme -->
            <div class="field mb-4">
              <label class="font-semibold mb-2 block">主題風格</label>
              <Dropdown
                v-model="selectedTheme"
                :options="themes"
                optionLabel="name"
                optionValue="id"
                placeholder="選擇主題"
                class="w-full"
              />
            </div>
            
            <Divider />
            
            <!-- Slides -->
            <div class="field mb-4">
              <div class="flex align-items-center justify-content-between mb-3">
                <label class="font-semibold">投影片內容</label>
                <Button 
                  icon="pi pi-plus" 
                  label="新增"
                  class="p-button-sm p-button-outlined"
                  @click="addSlide"
                />
              </div>
              
              <div v-for="(slide, index) in slides" :key="index" class="surface-100 border-round p-3 mb-3">
                <div class="flex align-items-center justify-content-between mb-2">
                  <span class="font-semibold">投影片 {{ index + 1 }}</span>
                  <Button 
                    icon="pi pi-trash" 
                    class="p-button-text p-button-danger p-button-sm"
                    @click="removeSlide(index)"
                    v-if="slides.length > 1"
                  />
                </div>
                
                <div class="grid">
                  <div class="col-12 md:col-8">
                    <InputText 
                      v-model="slide.title" 
                      placeholder="投影片標題"
                      class="w-full mb-2"
                    />
                  </div>
                  <div class="col-12 md:col-4">
                    <Dropdown
                      v-model="slide.layout"
                      :options="layouts"
                      optionLabel="name"
                      optionValue="id"
                      placeholder="版型"
                      class="w-full"
                    />
                  </div>
                </div>
                
                <Textarea
                  v-model="slide.contentText"
                  placeholder="內容（每行一個項目）"
                  rows="3"
                  class="w-full"
                />
              </div>
            </div>
            
            <!-- Generate Button -->
            <div class="flex justify-content-end gap-2 mt-4">
              <Button 
                label="重設" 
                icon="pi pi-refresh" 
                class="p-button-outlined p-button-secondary"
                @click="resetForm"
              />
              <Button 
                label="生成簡報" 
                icon="pi pi-file-export"
                :loading="isGenerating"
                :disabled="!title || slides.length === 0"
                @click="generatePPT"
              />
            </div>
          </template>
        </div>
      </div>
      
      <!-- Right Panel: Preview -->
      <div class="col-12 lg:col-7">
        <div class="deloitte-card p-4 h-full flex flex-column">
          <div class="flex align-items-center justify-content-between mb-3">
            <h2 class="text-heading-lg m-0 deloitte-green-dot">
              <i class="pi pi-eye mr-2 text-green-500"></i>
              預覽 & 下載
            </h2>
          </div>
          
          <!-- Preview Area -->
          <div class="flex-1 overflow-auto surface-100 border-round p-4" style="min-height: 500px;">
            <div v-if="isGenerating" class="flex flex-column align-items-center justify-content-center h-full">
              <ProgressSpinner style="width: 50px; height: 50px" />
              <p class="text-500 mt-3">{{ mode === 'ai' ? 'AI 正在搜尋資料並生成簡報...' : '正在生成簡報...' }}</p>
              <p class="text-xs text-400" v-if="mode === 'ai'">這可能需要 10-30 秒</p>
            </div>
            
            <div v-else-if="generatedResult" class="text-center">
              <i class="pi pi-check-circle text-6xl text-green-500 mb-4"></i>
              <h3 class="m-0 mb-2">簡報生成成功！</h3>
              <p class="text-500 mb-4">共 {{ generatedResult.slide_count }} 張投影片</p>
              
              <Button 
                label="下載 PowerPoint" 
                icon="pi pi-download"
                class="p-button-lg"
                @click="downloadPPT"
              />
              
              <!-- Preview Outline -->
              <Divider />
              <h4 class="text-left mb-3">大綱預覽</h4>
              <div class="text-left">
                <div v-for="(slide, index) in previewSlides" :key="index" class="surface-200 border-round p-3 mb-2">
                  <div class="flex align-items-center gap-2">
                    <Tag :value="`#${index + 1}`" severity="info" />
                    <span class="font-semibold">{{ slide.title }}</span>
                    <Tag :value="getLayoutName(slide.layout)" class="ml-auto" />
                  </div>
                  <div class="text-500 text-sm mt-2" v-if="slide.content && slide.content.length > 0">
                    <div v-for="(item, i) in slide.content.slice(0, 3)" :key="i" class="mb-1">
                      • {{ item }}
                    </div>
                    <span v-if="slide.content.length > 3" class="text-xs">...還有 {{ slide.content.length - 3 }} 項</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="flex flex-column align-items-center justify-content-center h-full text-500">
              <i class="pi pi-file-powerpoint text-6xl mb-3 opacity-30" style="color: #D04423;"></i>
              <p class="m-0">簡報預覽將顯示在這裡</p>
              <p class="text-sm m-0 mt-2" v-if="mode === 'ai'">輸入主題後點擊「AI 生成簡報」</p>
              <p class="text-sm m-0 mt-2" v-else>填寫左側表單後點擊「生成簡報」</p>
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
import { useToast } from 'primevue/usetoast';
import apiClient from '../api/client';

// PrimeVue Components
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import Message from 'primevue/message';
import Tag from 'primevue/tag';
import Divider from 'primevue/divider';
import ProgressSpinner from 'primevue/progressspinner';
import Slider from 'primevue/slider';

const toast = useToast();

// Mode
const mode = ref<'ai' | 'manual'>('ai');

// Options
const themes = [
  { id: 'deloitte', name: 'Deloitte (企業綠)' },
  { id: 'professional', name: '專業商務 (深藍)' },
  { id: 'creative', name: '創意活潑 (紫橘)' },
  { id: 'minimal', name: '極簡風格 (黑白)' }
];

const layouts = [
  { id: 'bullet', name: '項目符號' },
  { id: 'content', name: '純文字' },
  { id: 'section', name: '章節分隔' },
  { id: 'two_column', name: '雙欄對比' }
];

// AI Mode State
const aiTopic = ref('');
const aiSlideCount = ref(6);

// Manual Mode State
const title = ref('');
const subtitle = ref('');
const selectedTheme = ref('deloitte');
const slides = ref([
  { title: '', layout: 'bullet', contentText: '' }
]);

// Common State
const isGenerating = ref(false);
const generatedResult = ref<any>(null);
const errorMsg = ref('');

// Preview slides (for both modes)
const previewSlides = computed(() => {
  if (generatedResult.value?.outline) {
    return generatedResult.value.outline;
  }
  return slides.value.map(s => ({
    title: s.title,
    content: s.contentText ? s.contentText.split('\n').filter((l: string) => l.trim()) : [],
    layout: s.layout
  }));
});

// Methods
const addSlide = () => {
  slides.value.push({ title: '', layout: 'bullet', contentText: '' });
};

const removeSlide = (index: number) => {
  slides.value.splice(index, 1);
};

const resetForm = () => {
  title.value = '';
  subtitle.value = '';
  selectedTheme.value = 'deloitte';
  slides.value = [{ title: '', layout: 'bullet', contentText: '' }];
  generatedResult.value = null;
  errorMsg.value = '';
};

const getLayoutName = (layoutId: string): string => {
  const layout = layouts.find(l => l.id === layoutId);
  return layout ? layout.name : layoutId;
};

// AI Generate
const aiGeneratePPT = async () => {
  if (!aiTopic.value) {
    toast.add({ severity: 'warn', summary: '請輸入主題', life: 3000 });
    return;
  }
  
  isGenerating.value = true;
  errorMsg.value = '';
  generatedResult.value = null;
  
  try {
    const response: any = await apiClient.post('/ppt/ai-generate', {
      topic: aiTopic.value,
      slide_count: aiSlideCount.value,
      theme: selectedTheme.value,
      language: 'zh-TW'
    });
    
    if (response.status === 'success') {
      generatedResult.value = response;
      toast.add({
        severity: 'success',
        summary: 'AI 生成成功',
        detail: `簡報已生成，共 ${response.slide_count} 張投影片`,
        life: 3000
      });
    } else {
      errorMsg.value = response.message || '生成失敗';
    }
  } catch (err: any) {
    console.error('AI Generate error:', err);
    errorMsg.value = err.response?.data?.detail || err.message || '生成時發生錯誤';
  } finally {
    isGenerating.value = false;
  }
};

// Manual Generate
const generatePPT = async () => {
  if (!title.value) {
    toast.add({ severity: 'warn', summary: '請輸入標題', life: 3000 });
    return;
  }
  
  isGenerating.value = true;
  errorMsg.value = '';
  generatedResult.value = null;
  
  try {
    const slidesData = slides.value.map(slide => ({
      title: slide.title,
      content: slide.contentText ? slide.contentText.split('\n').filter((l: string) => l.trim()) : [],
      layout: slide.layout
    }));
    
    const response: any = await apiClient.post('/ppt/generate', {
      title: title.value,
      subtitle: subtitle.value,
      slides: slidesData,
      theme: selectedTheme.value
    });
    
    if (response.status === 'success') {
      generatedResult.value = response;
      toast.add({
        severity: 'success',
        summary: '生成成功',
        detail: `簡報已生成，共 ${response.slide_count} 張投影片`,
        life: 3000
      });
    } else {
      errorMsg.value = response.message || '生成失敗';
    }
  } catch (err: any) {
    console.error('Generate error:', err);
    errorMsg.value = err.response?.data?.detail || err.message || '生成時發生錯誤';
  } finally {
    isGenerating.value = false;
  }
};

const downloadPPT = () => {
  if (generatedResult.value?.download_url) {
    // Use VITE_API_URL if set (production), otherwise use relative path (works via proxy)
    const baseUrl = import.meta.env.VITE_API_URL || '';
    window.open(`${baseUrl}${generatedResult.value.download_url}`, '_blank');
  }
};
</script>

<style scoped>
.ppt-generator-page {
  min-height: calc(100vh - 60px);
  background: var(--surface-ground);
}
</style>
