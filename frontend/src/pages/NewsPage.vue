<template>
  <div class="grid">
    <div class="col-12">
        <div class="surface-card shadow-2 border-round p-4 h-full">
            <div class="flex align-items-center justify-content-between mb-4">
                <span class="text-xl font-bold text-900">Platform News & Announcements</span>
                <Button v-if="isAdmin" label="Publish News" icon="pi pi-plus" class="p-button-primary" @click="openPublishDialog" />
            </div>

             <div class="flex flex-column gap-3">
                 <div v-for="news in newsItems" :key="news.id" class="border-bottom-1 surface-border pb-3">
                    <div class="flex justify-content-between align-items-start">
                        <div>
                            <div class="font-bold text-blue-900 mb-1 text-lg">{{ news.title }}</div>
                            <Tag v-if="!news.is_published" severity="warning" value="Draft" class="mr-2"></Tag>
                        </div>
                        <div v-if="isAdmin" class="flex gap-2">
                             <Button icon="pi pi-pencil" text rounded severity="secondary" @click="editNews(news)" />
                             <Button icon="pi pi-trash" text rounded severity="danger" @click="deleteNews(news)" />
                        </div>
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
    <Dialog v-model:visible="showPublishDialog" :header="isEditMode ? 'Edit News' : 'Publish News'" :modal="true" class="p-fluid" style="width: 50vw">
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
            <Button :label="isEditMode ? 'Save Changes' : 'Publish'" icon="pi pi-check" @click="saveNews" :loading="isPublishing" />
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
const isEditMode = ref(false);
const editingId = ref<number | null>(null);

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

const openPublishDialog = () => {
    isEditMode.value = false;
    editingId.value = null;
    newsForm.value = { title: '', content: '', is_published: true };
    showPublishDialog.value = true;
};

const editNews = (item: any) => {
    isEditMode.value = true;
    editingId.value = item.id;
    newsForm.value = { 
        title: item.title, 
        content: item.content, 
        is_published: item.is_published 
    };
    showPublishDialog.value = true;
};

const deleteNews = async (item: any) => {
    if (!confirm('Are you sure you want to delete this announcement?')) return;
    try {
        await apiClient.delete(`/news/${item.id}`);
        toast.add({ severity: 'success', summary: 'Deleted', detail: 'News deleted', life: 3000 });
        loadNews();
    } catch (e) {
        console.error("Failed to delete news", e);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete news', life: 3000 });
    }
};

const saveNews = async () => {
    if (!newsForm.value.title || !newsForm.value.content) {
        toast.add({ severity: 'warn', summary: 'Missing Info', detail: 'Please fill in both title and content', life: 3000 });
        return;
    }

    isPublishing.value = true;
    try {
        if (isEditMode.value && editingId.value) {
            await apiClient.put(`/news/${editingId.value}`, newsForm.value);
            toast.add({ severity: 'success', summary: 'Updated', detail: 'News updated successfully', life: 3000 });
        } else {
            await apiClient.post('/news', newsForm.value);
            toast.add({ severity: 'success', summary: 'Published', detail: 'News published successfully', life: 3000 });
        }
        showPublishDialog.value = false;
        loadNews(); 
    } catch (e) {
        console.error("Failed to save news", e);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save news. check permissions.', life: 3000 });
    } finally {
        isPublishing.value = false;
    }
};

onMounted(() => {
    loadNews();
});
</script>
