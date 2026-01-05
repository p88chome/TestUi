<template>
  <div class="models-page p-6">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-2xl font-bold m-0">AI Models Management</h1>
      <Button label="Add Model" icon="pi pi-plus" @click="openDialog()" />
    </div>

    <div class="card bg-white border-round shadow-1">
      <DataTable :value="models" tableStyle="min-width: 50rem">
         <Column field="name" header="Friendly Name"></Column>
         <Column field="deployment_name" header="Deployment Name"></Column>
         <Column field="api_version" header="API Version"></Column>
         <Column header="Status">
             <template #body="slotProps">
                 <Tag :severity="slotProps.data.is_active ? 'success' : 'secondary'" :value="slotProps.data.is_active ? 'Active' : 'Inactive'" />
             </template>
         </Column>
         <Column header="Actions">
             <template #body="slotProps">
                 <Button icon="pi pi-pencil" text rounded @click="openDialog(slotProps.data)" />
                 <Button icon="pi pi-trash" text rounded severity="danger" @click="confirmDelete(slotProps.data)" />
             </template>
         </Column>
      </DataTable>
    </div>

    <Dialog v-model:visible="dialogVisible" :header="isEdit ? 'Edit Model' : 'New Model'" modal class="p-fluid" :style="{ width: '400px' }">
        <div class="field">
            <label for="name">Friendly Name (e.g. GPT-4 Prod)</label>
            <InputText id="name" v-model="form.name" required autofocus />
        </div>
        <div class="field mt-3">
            <label for="deploy">Deployment Name (Azure)</label>
            <InputText id="deploy" v-model="form.deployment_name" required />
            <small class="text-secondary">Must match your Azure OpenAI Deployment Name</small>
        </div>
        <div class="field mt-3">
            <label for="version">API Version</label>
            <InputText id="version" v-model="form.api_version" placeholder="2023-05-15" />
        </div>
        <div class="field mt-3 flex align-items-center gap-2">
            <Checkbox v-model="form.is_active" :binary="true" inputId="active" />
            <label for="active">Set as Active (Default)</label>
        </div>
        
        <template #footer>
            <Button label="Cancel" icon="pi pi-times" text @click="dialogVisible = false" />
            <Button label="Save" icon="pi pi-check" @click="saveModel" autofocus />
        </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getModels, createModel, updateModel, deleteModel, type AIModel } from '../api/models';

// Components
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';

const models = ref<AIModel[]>([]);
const dialogVisible = ref(false);
const isEdit = ref(false);
const currentId = ref<string | null>(null);

const form = ref({
    name: '',
    deployment_name: '',
    api_version: '2023-05-15',
    is_active: false
});

const loadModels = async () => {
    try {
        models.value = await getModels();
    } catch (e) {
        console.error(e);
        alert("Failed to load models");
    }
};

onMounted(() => {
    loadModels();
});

const openDialog = (model?: AIModel) => {
    if (model) {
        isEdit.value = true;
        currentId.value = model.id;
        form.value = {
            name: model.name,
            deployment_name: model.deployment_name,
            api_version: model.api_version,
            is_active: model.is_active
        };
    } else {
        isEdit.value = false;
        currentId.value = null;
        form.value = {
            name: '',
            deployment_name: '',
            api_version: '2023-05-15',
            is_active: false
        };
    }
    dialogVisible.value = true;
};

const saveModel = async () => {
    try {
        if (isEdit.value && currentId.value) {
            await updateModel(currentId.value, form.value);
        } else {
            await createModel(form.value);
        }
        dialogVisible.value = false;
        await loadModels();
    } catch (e: any) {
        console.error(e);
        alert(`Error: ${e.response?.data?.detail || e.message}`);
    }
};

const confirmDelete = async (model: AIModel) => {
    if (confirm(`Delete model ${model.name}?`)) {
        try {
            await deleteModel(model.id);
            await loadModels();
        } catch (e) {
            console.error(e);
            alert("Failed to delete");
        }
    }
}
</script>

<style scoped>
</style>
