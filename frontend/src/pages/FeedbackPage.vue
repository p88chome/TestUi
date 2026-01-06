<template>
  <div class="card p-3">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-xl font-bold m-0 text-900">User Feedback</h2>
      <Button icon="pi pi-refresh" text rounded @click="loadFeedbacks" :loading="loading" />
    </div>

    <DataTable :value="feedbacks" :loading="loading" class="p-datatable-sm" sortField="created_at" :sortOrder="-1" paginator :rows="10">
        <Column field="id" header="ID" sortable style="width: 5rem"></Column>
        <Column header="User" sortable field="user.email">
            <template #body="slotProps">
                <div class="flex flex-column">
                    <span class="font-bold">{{ slotProps.data.user?.full_name || 'Unknown' }}</span>
                    <span class="text-sm text-500">{{ slotProps.data.user?.email || slotProps.data.user_id }}</span>
                </div>
            </template>
        </Column>
        <Column field="content" header="Feedback" style="min-width: 20rem">
            <template #body="slotProps">
                <span style="white-space: pre-wrap;">{{ slotProps.data.content }}</span>
            </template>
        </Column>
        <Column field="created_at" header="Date" sortable style="width: 12rem">
             <template #body="slotProps">
                 {{ new Date(slotProps.data.created_at).toLocaleString() }}
             </template>
        </Column>
        <Column header="Actions" style="width: 5rem">
            <template #body="slotProps">
                <Button icon="pi pi-trash" text rounded severity="danger" @click="confirmDelete(slotProps.data)" />
            </template>
        </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getFeedbacks, deleteFeedback, type Feedback } from '../api/feedback';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const feedbacks = ref<Feedback[]>([]);
const loading = ref(false);

const loadFeedbacks = async () => {
    loading.value = true;
    try {
        feedbacks.value = await getFeedbacks();
    } catch (e) {
        console.error("Failed to load feedback", e);
    } finally {
        loading.value = false;
    }
};

const confirmDelete = async (feedback: Feedback) => {
    if (!confirm('Are you sure you want to delete this feedback?')) return;
    
    try {
        await deleteFeedback(feedback.id);
        toast.add({ severity: 'success', summary: 'Deleted', detail: 'Feedback deleted', life: 3000 });
        // Remove from list locally
        feedbacks.value = feedbacks.value.filter(f => f.id !== feedback.id);
    } catch (e) {
        console.error("Failed to delete", e);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete feedback', life: 3000 });
    }
};

onMounted(() => {
    loadFeedbacks();
});
</script>
