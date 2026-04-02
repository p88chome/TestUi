<template>
  <div class="models-page p-6">
    <!-- Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-2xl font-bold m-0">AI Models Management</h1>
      <Button label="Add Model" icon="pi pi-plus" @click="openDialog()" />
    </div>

    <!-- Models Table -->
    <div class="card bg-white border-round shadow-1">
      <DataTable :value="models" tableStyle="min-width: 50rem">
        <Column field="name" header="Friendly Name" />
        <Column header="Provider">
          <template #body="slotProps">
            <Tag
              :severity="providerSeverity(slotProps.data.provider)"
              :value="slotProps.data.provider.toUpperCase()"
            />
          </template>
        </Column>
        <Column header="Model / Deployment">
          <template #body="slotProps">
            <span class="font-mono text-sm">
              {{ slotProps.data.model_name || slotProps.data.deployment_name || '—' }}
            </span>
          </template>
        </Column>
        <Column field="api_version" header="API Version">
          <template #body="slotProps">
            {{ slotProps.data.api_version || '—' }}
          </template>
        </Column>
        <Column header="Status">
          <template #body="slotProps">
            <Tag
              :severity="slotProps.data.is_active ? 'success' : 'secondary'"
              :value="slotProps.data.is_active ? 'Active' : 'Inactive'"
            />
          </template>
        </Column>
        <Column header="Actions">
          <template #body="slotProps">
            <Button
              v-if="!slotProps.data.is_active"
              icon="pi pi-check-circle"
              text
              rounded
              severity="success"
              v-tooltip.top="'Set as Active'"
              @click="activateModel(slotProps.data)"
            />
            <Button icon="pi pi-pencil" text rounded @click="openDialog(slotProps.data)" />
            <Button
              icon="pi pi-trash"
              text
              rounded
              severity="danger"
              @click="confirmDelete(slotProps.data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Create / Edit Dialog -->
    <Dialog
      v-model:visible="dialogVisible"
      :header="isEdit ? 'Edit Model' : 'New Model'"
      modal
      class="p-fluid"
      :style="{ width: '500px' }"
    >
      <!-- Friendly Name -->
      <div class="field">
        <label for="name">Friendly Name</label>
        <InputText id="name" v-model="form.name" required autofocus placeholder="e.g. GPT-4 Production" />
      </div>

      <!-- Provider selector -->
      <div class="field mt-3">
        <label for="provider">Provider</label>
        <Dropdown
          id="provider"
          v-model="form.provider"
          :options="providerOptions"
          option-label="label"
          option-value="value"
          placeholder="Select Provider"
        />
      </div>

      <!-- Azure-specific fields -->
      <template v-if="form.provider === 'azure'">
        <div class="field mt-3">
          <label for="deploy">Deployment Name</label>
          <InputText id="deploy" v-model="form.deployment_name" placeholder="e.g. gpt-4-prod" />
          <small class="text-color-secondary">Must match your Azure OpenAI Deployment Name</small>
        </div>
        <div class="field mt-3">
          <label for="version">API Version</label>
          <InputText id="version" v-model="form.api_version" placeholder="2024-12-01-preview" />
        </div>
        <div class="field mt-3 flex align-items-center gap-2">
          <Checkbox v-model="form.is_reasoning_model" :binary="true" inputId="reasoning" />
          <label for="reasoning">
            Reasoning Model (o1/o3/o4-mini)
            <small class="ml-2 text-color-secondary">Uses <code>max_completion_tokens</code> instead of <code>max_tokens</code></small>
          </label>
        </div>
      </template>

      <!-- Google / OpenAI fields -->
      <template v-if="form.provider === 'google' || form.provider === 'openai'">
        <div class="field mt-3">
          <label for="model_name">Model Name</label>
          <InputText
            id="model_name"
            v-model="form.model_name"
            :placeholder="form.provider === 'google' ? 'e.g. gemini-1.5-flash' : 'e.g. gpt-4o'"
          />
          <small class="text-color-secondary">
            {{ form.provider === 'google' ? 'Google Gemini model identifier' : 'OpenAI model name' }}
          </small>
        </div>
      </template>

      <!-- Description -->
      <div class="field mt-3">
        <label for="desc">Description (optional)</label>
        <InputText id="desc" v-model="form.description" placeholder="Short note about this model" />
      </div>

      <!-- Active toggle -->
      <div class="field mt-3 flex align-items-center gap-2">
        <Checkbox v-model="form.is_active" :binary="true" inputId="active" />
        <label for="active">Set as Active (Default)</label>
      </div>

      <template #footer>
        <Button label="Cancel" icon="pi pi-times" text @click="dialogVisible = false" />
        <Button label="Save" icon="pi pi-check" @click="saveModel" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {
  getModels,
  createModel,
  updateModel,
  deleteModel,
  setActiveModel,
  type AIModel,
  type LLMProvider,
} from '../api/models';

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Checkbox from 'primevue/checkbox';
import Dropdown from 'primevue/dropdown';

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const models = ref<AIModel[]>([]);
const dialogVisible = ref(false);
const isEdit = ref(false);
const currentId = ref<string | null>(null);

const emptyForm = () => ({
  name: '',
  provider: 'azure' as LLMProvider,
  model_name: '',
  deployment_name: '',
  api_version: '2024-12-01-preview',
  description: '',
  is_active: false,
  is_reasoning_model: false,
});

const form = ref(emptyForm());

const providerOptions = [
  { label: '☁️  Azure OpenAI', value: 'azure' },
  { label: '🔵 Google Gemini', value: 'google' },
  { label: '🟢 OpenAI', value: 'openai' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const providerSeverity = (provider: LLMProvider) => {
  const map: Record<LLMProvider, string> = {
    azure: 'info',
    google: 'warning',
    openai: 'success',
  };
  return map[provider] ?? 'secondary';
};

// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------
const loadModels = async () => {
  try {
    models.value = await getModels();
  } catch (e) {
    console.error(e);
    alert('Failed to load models');
  }
};

onMounted(loadModels);

// ---------------------------------------------------------------------------
// Dialog
// ---------------------------------------------------------------------------
const openDialog = (model?: AIModel) => {
  if (model) {
    isEdit.value = true;
    currentId.value = model.id;
    form.value = {
      name: model.name,
      provider: model.provider,
      model_name: model.model_name ?? '',
      deployment_name: model.deployment_name ?? '',
      api_version: model.api_version ?? '',
      description: model.description ?? '',
      is_active: model.is_active,
      is_reasoning_model: model.is_reasoning_model,
    };
  } else {
    isEdit.value = false;
    currentId.value = null;
    form.value = emptyForm();
  }
  dialogVisible.value = true;
};

const saveModel = async () => {
  try {
    const payload = {
      ...form.value,
      // Send null instead of empty string for optional fields
      model_name: form.value.model_name || null,
      deployment_name: form.value.deployment_name || null,
      api_version: form.value.api_version || null,
      description: form.value.description || undefined,
    };

    if (isEdit.value && currentId.value) {
      await updateModel(currentId.value, payload);
    } else {
      await createModel(payload);
    }
    dialogVisible.value = false;
    await loadModels();
  } catch (e: any) {
    console.error(e);
    alert(`Error: ${e.response?.data?.detail || e.message}`);
  }
};

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------
const activateModel = async (model: AIModel) => {
  try {
    await setActiveModel(model.id);
    await loadModels();
  } catch (e: any) {
    alert(`Failed to activate: ${e.response?.data?.detail || e.message}`);
  }
};

const confirmDelete = async (model: AIModel) => {
  if (confirm(`Delete model "${model.name}"?`)) {
    try {
      await deleteModel(model.id);
      await loadModels();
    } catch (e) {
      console.error(e);
      alert('Failed to delete');
    }
  }
};
</script>

<style scoped>
.font-mono {
  font-family: 'Courier New', monospace;
}
</style>
