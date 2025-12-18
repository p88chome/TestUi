<template>
  <div class="components-page">
    <div class="page-header">
      <h1>Components</h1>
      <Button label="Create Component" icon="pi pi-plus" @click="openCreateModal" />
    </div>

    <!-- Components List -->
    <div class="card">
        <DataTable :value="components" tableStyle="min-width: 50rem" showGridlines stripedRows>
            <Column field="name" header="Name">
                <template #body="slotProps">
                    <div style="font-weight: 500;">{{ slotProps.data.name }}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">{{ slotProps.data.description }}</div>
                </template>
            </Column>
            <Column field="endpoint_type" header="Type">
                <template #body="slotProps">
                    <Tag :value="slotProps.data.endpoint_type" severity="info" />
                </template>
            </Column>
            <Column field="tags" header="Tags">
                <template #body="slotProps">
                    <div class="flex gap-1 flex-wrap">
                        <Tag v-for="tag in slotProps.data.tags" :key="tag" :value="tag" severity="secondary" style="font-size: 0.75rem" />
                    </div>
                </template>
            </Column>
            <Column field="active" header="Active">
                <template #body="slotProps">
                    <i class="pi" :class="{'pi-check-circle text-green-500': slotProps.data.active, 'pi-times-circle text-red-500': !slotProps.data.active}" style="font-size: 1.2rem"></i>
                </template>
            </Column>
            <Column header="Actions">
                <template #body="slotProps">
                    <div class="flex gap-2">
                        <Button icon="pi pi-pencil" severity="secondary" text rounded aria-label="Edit" @click="editComponent(slotProps.data)" />
                        <Button icon="pi pi-trash" severity="danger" text rounded aria-label="Delete" @click="removeComponent(slotProps.data.id)" />
                    </div>
                </template>
            </Column>
            <template #empty> No components found. </template>
        </DataTable>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog 
      v-model:visible="showModal" 
      :header="isEditing ? 'Edit Component' : 'Create Component'" 
      :modal="true" 
      :style="{ width: '50vw' }"
    >
      <form @submit.prevent="saveComponent" class="flex flex-column gap-3 mt-3">
        <div class="flex flex-column gap-2">
          <label for="name">Name</label>
          <InputText id="name" v-model="form.name" required />
        </div>
        
        <div class="flex flex-column gap-2">
          <label for="description">Description</label>
          <Textarea id="description" v-model="form.description" rows="2" autoResize />
        </div>

        <div class="flex flex-column gap-2">
          <label for="type">Type</label>
          <Select id="type" v-model="form.endpoint_type" :options="['api', 'function', 'model']" placeholder="Select a Type" />
        </div>

        <div class="flex flex-column gap-2">
          <label for="tags">Tags (comma separated)</label>
          <InputText id="tags" v-model="tagsInput" placeholder="e.g. preprocessing, ml" />
        </div>

        <div class="flex flex-column gap-2">
          <label for="inputSchema">Input Schema (JSON)</label>
          <Textarea id="inputSchema" v-model="inputSchemaStr" rows="4" style="font-family: monospace;" />
        </div>

        <div class="flex flex-column gap-2">
          <label for="outputSchema">Output Schema (JSON)</label>
          <Textarea id="outputSchema" v-model="outputSchemaStr" rows="4" style="font-family: monospace;" />
        </div>
      </form>
      <template #footer>
        <Button label="Cancel" text @click="closeModal" severity="secondary" />
        <Button label="Save" @click="saveComponent" severity="primary" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getComponents, createComponent, updateComponent, deleteComponent } from '../api/components';
import type { ComponentOut, ComponentCreate } from '../types';

// PrimeVue Components
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Select from 'primevue/select';
import Tag from 'primevue/tag';

const components = ref<ComponentOut[]>([]);
const showModal = ref(false);
const isEditing = ref(false);
const currentId = ref<string>('');

const form = ref<ComponentCreate>({
  name: '',
  description: '',
  endpoint_type: 'function',
  tags: [],
  input_schema: {},
  output_schema: {},
  active: true,
});

const tagsInput = ref('');
const inputSchemaStr = ref('{}');
const outputSchemaStr = ref('{}');

const fetchComponents = async () => {
  try {
    components.value = await getComponents();
  } catch (error) {
    console.error('Failed to fetch components', error);
  }
};

const openCreateModal = () => {
  isEditing.value = false;
  currentId.value = '';
  form.value = {
    name: '',
    description: '',
    endpoint_type: 'function',
    tags: [],
    input_schema: {},
    output_schema: {},
    active: true,
  };
  tagsInput.value = '';
  inputSchemaStr.value = '{}';
  outputSchemaStr.value = '{}';
  showModal.value = true;
};

const editComponent = (comp: ComponentOut) => {
  isEditing.value = true;
  currentId.value = comp.id;
  form.value = { ...comp };
  tagsInput.value = comp.tags.join(', ');
  inputSchemaStr.value = JSON.stringify(comp.input_schema, null, 2);
  outputSchemaStr.value = JSON.stringify(comp.output_schema, null, 2);
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveComponent = async () => {
  try {
    // Parse tags and JSON
    const tags = tagsInput.value.split(',').map(t => t.trim()).filter(t => t);
    const input_schema = JSON.parse(inputSchemaStr.value);
    const output_schema = JSON.parse(outputSchemaStr.value);

    const payload = {
      ...form.value,
      tags,
      input_schema,
      output_schema,
    };

    if (isEditing.value) {
      await updateComponent(currentId.value, payload);
    } else {
      await createComponent(payload);
    }
    await fetchComponents();
    closeModal();
  } catch (error) {
    alert('Error saving component. Check JSON format.');
    console.error(error);
  }
};

const removeComponent = async (id: string) => {
  if (confirm('Are you sure?')) {
    await deleteComponent(id);
    await fetchComponents();
  }
};

onMounted(fetchComponents);
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

/* Helper utility classes since we don't have Tailwind fully configured but want flex */
.flex { display: flex; }
.flex-column { flex-direction: column; }
.gap-1 { gap: 0.25rem; }
.gap-2 { gap: 0.5rem; }
.gap-3 { gap: 1rem; }
.flex-wrap { flex-wrap: wrap; }
.mt-3 { margin-top: 1rem; }
.mr-2 { margin-right: 0.5rem; }

.text-green-500 { color: var(--brand-green); }
.text-red-500 { color: #ef4444; }
</style>
