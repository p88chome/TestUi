<template>
  <div class="chatbot-page flex justify-content-center bg-white h-full relative">
    <div class="chat-wrapper w-full max-w-50rem flex flex-column h-full">
      <!-- Header / Mode Selector -->
      <div class="p-3 border-bottom-1 border-200 flex align-items-center justify-content-between bg-white z-1 shadow-1">
          <div class="flex align-items-center gap-2">
              <span class="font-bold text-lg">Chat Mode:</span>
              <Dropdown 
                v-model="selectedAssistant" 
                :options="assistants" 
                optionLabel="name" 
                placeholder="Select Assistant" 
                class="w-14rem"
                @change="onAssistantChange"
              />
          </div>
          <div>
            <!-- Future buttons like Clear Chat -->
             <Button icon="pi pi-refresh" text rounded @click="resetSession" v-tooltip="'New Chat'" />
          </div>
      </div>

      <!-- Messages Area -->
      <div class="messages flex-1 overflow-y-auto p-4 flex flex-column gap-4" ref="messagesRef">
        
        <!-- Empty State -->
        <div v-if="messages.length === 0" class="empty-state flex flex-column align-items-center justify-content-center flex-1 text-600">
           <i class="pi pi-sparkles text-6xl mb-3 text-primary"></i>
           <h3 class="m-0 font-medium">How can I help you today?</h3>
        </div>
        
        <!-- Message Rows -->
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          class="message-row flex gap-3 fadein animation-duration-300"
          :class="{'flex-row-reverse': msg.role === 'user'}"
        >
          <!-- Avatar -->
          <Avatar 
            :icon="msg.role === 'assistant' ? 'pi pi-android' : 'pi pi-user'" 
            :style="{ backgroundColor: msg.role === 'assistant' ? 'var(--brand-gray-light)' : 'var(--brand-black)', color: msg.role === 'assistant' ? 'var(--brand-black)' : 'white' }"
            shape="circle" 
            class="flex-shrink-0"
          />
          
          <!-- Content -->
          <div class="message-content flex flex-column gap-1" style="max-width: 80%;">
            <div class="role-name text-xs font-bold text-700" :class="{'text-right': msg.role === 'user', 'hidden': true}">
                {{ msg.role === 'assistant' ? 'AI Assistant' : 'You' }}
            </div>
            
            <div 
                class="bubble p-3 text-900 border-round-xl line-height-3"
                :class="{
                    'bg-surface-100': msg.role === 'user',
                    'bg-transparent pl-0': msg.role === 'assistant'
                }"
            >
                <div 
                    v-if="msg.role === 'assistant'"
                    v-html="renderMarkdown(msg.content)"
                    class="markdown-body"
                ></div>
                <div v-else>
                    {{ msg.content }}
                </div>
                
                <!-- Tool Usage Indicator -->
                <div v-if="msg.tool_used" class="mt-2 text-xs text-500 font-italic">
                    <i class="pi pi-cog mr-1"></i>Used skill: {{ msg.tool_used }}
                </div>
            </div>
          </div>
        </div>
        
        <!-- Loading State -->
        <div v-if="isLoading" class="message-row assistant flex gap-3 fadein">
           <Avatar icon="pi pi-android" class="bg-blue-50 text-blue-500 flex-shrink-0" shape="circle" />
           <div class="message-content">
             <div class="bubble pl-0 text-500 font-italic">Thinking...</div>
           </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-container p-4 bg-white">
        <!-- File Indicator -->
        <div v-if="selectedFile" class="flex align-items-center gap-2 mb-2 p-2 surface-100 border-round w-max">
            <i class="pi pi-file text-primary"></i>
            <span class="text-sm font-medium">{{ selectedFile.name }}</span>
            <i class="pi pi-times text-600 cursor-pointer hover:text-900" @click="clearFile"></i>
        </div>

        <div class="input-box relative flex align-items-center border-1 border-300 border-round-2xl shadow-1 focus-within:border-400 transition-colors pl-2">
            
          <!-- File Upload Button -->
          <input type="file" ref="fileInputRef" style="display: none" @change="onFileSelected" accept="image/*,.pdf" />
          <Button 
            icon="pi pi-paperclip" 
            rounded 
            text 
            severity="secondary"
            class="mr-1"
            @click="triggerFileUpload"
            v-tooltip="'Attach File (PDF/Image)'"
          />

          <Textarea 
            v-model="inputDetails" 
            @keyup.enter="sendMessage"
            placeholder="Ask anything..."
            autoResize
            rows="1"
            class="w-full border-none shadow-none text-base p-3 border-round-2xl"
            style="resize: none; max-height: 150px; background: transparent;"
            :disabled="isLoading"
          />
          <Button 
            icon="pi pi-arrow-up" 
            rounded 
            text
            aria-label="Send"
            @click="sendMessage" 
            :disabled="isLoading || (!inputDetails.trim() && !selectedFile)" 
            class="m-2 flex-shrink-0 bg-black-alpha-90 text-white hover:bg-black-alpha-70 w-2rem h-2rem p-0"
            style="background-color: var(--brand-black) !important;"
          />
        </div>
        <div class="text-center text-xs text-500 mt-2">
          AI can make mistakes. Please verify important information.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { runAgent } from '../api/agent';
import apiClient from '../api/client';
import { marked } from 'marked';

// PrimeVue Components
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  tool_used?: string;
}

const messages = ref<Message[]>([]);
const inputDetails = ref('');
const isLoading = ref(false);
const messagesRef = ref<HTMLElement | null>(null);

// Assistant State
const assistants = ref([
    { name: 'General Assistant', id: null }, // Default
    { name: 'Legal Bot (Contracts)', id: 'legal_bot' },
    { name: 'Finance Bot (Excel)', id: 'finance_bot' }
]);
const selectedAssistant = ref(assistants.value[0]);
const currentSessionId = ref<string | undefined>(undefined);

const onAssistantChange = () => {
    // changing assistant implies starting fresh context usually
    resetSession();
};

const resetSession = () => {
    messages.value = [];
    currentSessionId.value = undefined;
};

// File State
const selectedFile = ref<File | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);

const scrollToBottom = async () => {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
};

const renderMarkdown = (text: string) => {
    return marked.parse(text);
};

const triggerFileUpload = () => {
    fileInputRef.value?.click();
};

const onFileSelected = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
        selectedFile.value = target.files[0] || null;
    }
};

const clearFile = () => {
    selectedFile.value = null;
    if (fileInputRef.value) {
        fileInputRef.value.value = '';
    }
};

const sendMessage = async () => {
  if (!inputDetails.value.trim() && !selectedFile.value) return;

  const userMsg = inputDetails.value;
  messages.value.push({ role: 'user', content: userMsg || (selectedFile.value ? `[Sent File: ${selectedFile.value.name}]` : '') });
  
  // Clear inputs immediately
  inputDetails.value = '';
  const currentFile = selectedFile.value;
  clearFile();
  
  isLoading.value = true;
  await scrollToBottom();

  try {
      if (currentFile) {
          // Fallback to old Chat endpoint if file is present (Agent API MVP doesn't support file upload yet)
          // Ideally Agent API should handle FormData too.
          // For now, let's keep the file logic separate or simple.
          const formData = new FormData();
          formData.append('message', userMsg || "Please analyze this file.");
          formData.append('file', currentFile);

          const res = await apiClient.post('/chat/message', formData, {
               headers: {'Content-Type': 'multipart/form-data'}
          }) as any;
          messages.value.push({ role: 'assistant', content: res.content });

      } else {
          // USE NEW AGENT API
          const res = await runAgent(userMsg, currentSessionId.value, selectedAssistant.value?.id || undefined);
          
          if (res.session_id) {
              currentSessionId.value = res.session_id;
          }
          
          messages.value.push({ 
              role: 'assistant', 
              content: res.response,
              tool_used: res.tool_used 
          });
      }

  } catch (e: any) {
      console.error(e);
      messages.value.push({ role: 'assistant', content: "Sorry, I encountered an error. Agent might be taking a break." });
  } finally {
      isLoading.value = false;
      await scrollToBottom();
  }
};
</script>

<style>
/* Global Markdown Styles for Agent responses */
.markdown-body {
    font-size: 0.95rem;
    line-height: 1.6;
}
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
}
.markdown-body ul, .markdown-body ol {
    padding-left: 1.5rem;
    margin: 0.5rem 0;
}
.markdown-body p {
    margin-bottom: 0.5rem;
}
.markdown-body strong {
    font-weight: 700;
    color: var(--primary-color);
}
.markdown-body table {
    border-collapse: collapse;
    width: 100%;
    margin: 1rem 0;
    font-size: 0.9rem;
}
.markdown-body th, .markdown-body td {
    border: 1px solid #e0e0e0;
    padding: 0.75rem;
    text-align: left;
}
.markdown-body th {
    background-color: #f8f9fa;
    font-weight: 600;
}
.markdown-body blockquote {
    border-left: 4px solid var(--primary-color);
    margin: 0.5rem 0;
    padding-left: 1rem;
    color: #666;
    background-color: #f9f9f9;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
}
</style>

<style scoped>
.chatbot-page {
  height: calc(100vh - 64px); 
}
</style>
