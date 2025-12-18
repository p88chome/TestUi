<template>
  <div class="chatbot-page flex justify-content-center bg-white h-full relative">
    <div class="chat-wrapper w-full max-w-50rem flex flex-column h-full">
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
                {{ msg.content }}
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
        <div class="input-box relative flex align-items-center border-1 border-300 border-round-2xl shadow-1 focus-within:border-400 transition-colors">
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
            :disabled="isLoading || !inputDetails.trim()" 
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

// PrimeVue Components
import Avatar from 'primevue/avatar';
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const messages = ref<Message[]>([]);
const inputDetails = ref('');
const isLoading = ref(false);
const messagesRef = ref<HTMLElement | null>(null);

const scrollToBottom = async () => {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!inputDetails.value.trim()) return;

  const userMsg = inputDetails.value;
  messages.value.push({ role: 'user', content: userMsg });
  inputDetails.value = '';
  // Reset height of textarea if necessary, PrimeVue autoResize usually handles it but might need force reset
  
  isLoading.value = true;
  await scrollToBottom();

  // Simulate response
  setTimeout(async () => {
    messages.value.push({ role: 'assistant', content: `Here is a simulated response to: "${userMsg}". In a real implementation, this would connect to your backend LLM.` });
    isLoading.value = false;
    await scrollToBottom();
  }, 1000);
};
</script>

<style scoped>
.chatbot-page {
  height: calc(100vh - 64px); 
}

/* Custom overrides for specific PrimeVue feels if needed, mainly relying on PrimeFlex utilities */
</style>
