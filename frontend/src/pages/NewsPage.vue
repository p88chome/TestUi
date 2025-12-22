<template>
  <div class="grid">
    <div class="col-12">
        <div class="surface-card shadow-2 border-round p-4 h-full">
            <div class="flex align-items-center justify-content-between mb-4">
                <span class="text-xl font-bold text-900">Platform News & Announcements</span>
                <Button v-if="isAdmin" label="Publish News" icon="pi pi-plus" class="p-button-primary" @click="showPublishDialog = true" />
            </div>

             <div class="flex flex-column gap-3">
                 <div v-for="news in newsItems" :key="news.id" class="border-bottom-1 surface-border pb-3">
                    <div class="flex justify-content-between">
                        <div class="font-bold text-blue-900 mb-1 text-lg">{{ news.title }}</div>
                        <Tag v-if="!news.is_published" severity="warning" value="Draft"></Tag>
                    </div>
                    <div class="text-700 block mb-2" style="white-space: pre-wrap; line-height: 1.6;">{{ news.content }}</div>
                    <div class="flex align-items-center gap-2 text-sm text-500">
                        <i class="pi pi-clock"></i>
                        <span>{{ formatDate(news.created_at) }}</span>
                    </div>
                 </div>
                 
                 <div v-if="newsItems.length === 0" class="text-center text-500 p-5">
                    <i class="pi pi-inbox text-4xl mb-3"></i>
                    <div>No active announcements.</div>
                 </div>
             </div>
        </div>
    </div>
    
    <!-- Admin Publish Dialog -->
    <Dialog v-model:visible="showPublishDialog" header="Publish News" :modal="true" class="p-fluid" style="width: 50vw">
        <div class="field">
            <label for="title" class="font-bold">Title</label>
            <InputText id="title" v-model="newsForm.title" autofocus />
        </div>
        <div class="field">
            <label for="content" class="font-bold">Content</label>
            <Textarea id="content" v-model="newsForm.content" rows="8" placeholder="Write your announcement here..." />
        </div>
        <div class="field-checkbox" v-if="isAdmin">
             <Checkbox inputId="binary" v-model="newsForm.is_published" :binary="true" />
             <label for="binary">Publish immediately</label>
        </div>
        <template #footer>
            <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="showPublishDialog = false" />
            <Button label="Publish" icon="pi pi-check" @click="publishNews" :loading="isPublishing" />
        </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import apiClient from '../api/client';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Checkbox from 'primevue/checkbox';
import Tag from 'primevue/tag';
import { useToast } from 'primevue/usetoast';

const auth = useAuthStore();
const toast = useToast();
const isAdmin = computed(() => auth.state.user?.is_superuser);

const showPublishDialog = ref(false);
const isPublishing = ref(false);
const newsItems = ref<any[]>([]);
const newsForm = ref({ title: '', content: '', is_published: true });

const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString() + ' ' + new Date(dateStr).toLocaleTimeString();
};

const loadNews = async () => {
    try {
        const res: any = await apiClient.get('/news');
        newsItems.value = res || [];
    } catch (e) {
        console.error("Failed to load news", e);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load news', life: 3000 });
    }
};

const publishNews = async () => {
    if (!newsForm.value.title || !newsForm.value.content) {
        toast.add({ severity: 'warn', summary: 'Missing Info', detail: 'Please fill in both title and content', life: 3000 });
        return;
    }

    isPublishing.value = true;
    try {
        await apiClient.post('/news', newsForm.value);
        toast.add({ severity: 'success', summary: 'Success', detail: 'News published successfully', life: 3000 });
        showPublishDialog.value = false;
        newsForm.value = { title: '', content: '', is_published: true };
        loadNews(); 
    } catch (e) {
        console.error("Failed to publish news", e);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to publish news. Check permissions.', life: 3000 });
    } finally {
        isPublishing.value = false;
    }
};

onMounted(() => {
    loadNews();
});
</script>
