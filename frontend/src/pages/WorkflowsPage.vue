<template>
  <div class="workflows-page flex gap-4 h-full">
    <!-- Left Column: Component Library -->
    <div class="column left-col w-3 flex flex-column gap-3 p-3 bg-white border-round shadow-1">
      <h3 class="m-0 text-lg text-900 border-bottom-1 surface-border pb-3">Library</h3>
      <IconField iconPosition="left">
          <InputIcon class="pi pi-search" />
          <InputText v-model="filterText" placeholder="Search components..." class="w-full" />
      </IconField>
      
      <div class="component-list flex-1 overflow-y-auto flex flex-column gap-2">
        <div 
          v-for="comp in filteredComponents" 
          :key="comp.id" 
          class="component-item p-3 border-round cursor-pointer hover:surface-100 transition-colors border-1 surface-border"
          @click="addStep(comp)"
        >
          <div class="flex justify-content-between align-items-center mb-2">
            <span class="font-bold text-900">{{ comp.name }}</span>
            <Tag :value="comp.endpoint_type" severity="secondary" style="font-size: 0.7rem" />
          </div>
          <p class="m-0 text-sm text-600 line-height-3">{{ comp.description }}</p>
        </div>
      </div>
    </div>

    <!-- Center Column: Workflow Steps -->
    <div class="column center-col flex-1 flex flex-column gap-3 p-3 surface-ground border-round">
      <h3 class="m-0 text-lg text-900">Workflow Steps</h3>
      
      <div v-if="steps.length === 0" class="empty-placeholder flex align-items-center justify-content-center flex-1 text-600">
        <div class="text-center">
            <i class="pi pi-exclamation-circle text-4xl mb-3"></i>
            <p>Select components from the library to build your workflow.</p>
        </div>
      </div>

      <div class="steps-list flex-1 overflow-y-auto flex flex-column gap-3">
        <Card v-for="(step, index) in steps" :key="index" class="step-card shadow-1">
            <template #title>
                <div class="flex align-items-center justify-content-between text-base">
                    <div class="flex align-items-center gap-2">
                        <Avatar :label="String(index + 1)" shape="circle" size="normal" class="bg-primary text-white" />
                        <span class="font-bold">{{ getComponentName(step.component_id) }}</span>
                    </div>
                    <div class="flex gap-1">
                        <Button icon="pi pi-arrow-up" text rounded size="small" @click="moveStep(index, -1)" :disabled="index === 0" />
                        <Button icon="pi pi-arrow-down" text rounded size="small" @click="moveStep(index, 1)" :disabled="index === steps.length - 1" />
                        <Button icon="pi pi-times" text rounded severity="danger" size="small" @click="removeStep(index)" />
                    </div>
                </div>
            </template>
            <template #content>
                 <div class="flex flex-column gap-3 mt-0">
                    <div class="flex flex-column gap-2">
                        <label class="text-xs font-medium text-600">Configuration (JSON)</label>
                        <Textarea v-model="step.configStr" rows="2" class="w-full font-mono text-sm" autoResize placeholder="{}" />
                    </div>
                    <div class="flex flex-column gap-2">
                         <label class="text-xs font-medium text-600">Input Mapping (JSON)</label>
                        <Textarea v-model="step.inputMapStr" rows="2" class="w-full font-mono text-sm" autoResize placeholder='{"param": "source"}' />
                    </div>
                 </div>
            </template>
        </Card>
      </div>
    </div>

    <!-- Right Column: Properties & Test -->
    <div class="column right-col w-3 flex flex-column gap-3 p-3 bg-white border-round shadow-1 h-full overflow-y-auto">
      <h3 class="m-0 text-lg text-900 border-bottom-1 surface-border pb-3">Properties</h3>
      
      <div class="flex flex-column gap-2 border-bottom-1 surface-border pb-3 mb-3">
        <label for="wf-load" class="font-medium text-700">Load Existing</label>
        <Dropdown 
            id="wf-load" 
            v-model="selectedWorkflowId" 
            :options="existingWorkflows" 
            optionLabel="name" 
            optionValue="id" 
            placeholder="Select a workflow..." 
            class="w-full"
            @change="loadWorkflow"
        />
      </div>

      <div class="flex flex-column gap-2">
        <label for="wf-name" class="font-medium text-700">Name</label>
        <InputText id="wf-name" v-model="workflowMeta.name" />
      </div>

      <div class="flex flex-column gap-2">
        <label for="wf-desc" class="font-medium text-700">Description</label>
        <Textarea id="wf-desc" v-model="workflowMeta.description" rows="3" autoResize />
      </div>
      
      <Divider />
      
      <div class="flex gap-2">
         <Button :label="savedId ? 'Update' : 'Save New'" icon="pi pi-save" @click="saveWorkflow" class="flex-1" />
         <Button v-if="savedId" icon="pi pi-plus" label="New" severity="secondary" @click="resetForm" />
         <Button v-if="savedId" icon="pi pi-trash" label="Delete" severity="danger" text @click="deleteCurrentWorkflow" />
      </div>
      
      <div class="mt-4">
          <h4 class="text-900 mb-3">Test Run</h4>
          <div class="flex flex-column gap-2 mb-3">
            <label class="font-medium text-700">Input Payload (JSON)</label>
            <Textarea v-model="runPayloadStr" rows="5" class="w-full font-mono text-sm" />
          </div>
          <Button 
            label="Run Workflow"
            icon="pi pi-play"
            :severity="savedId ? 'success' : 'secondary'" 
            :disabled="!savedId" 
            @click="executeRun" 
            class="w-full" 
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { getComponents } from '../api/components';
import { createWorkflow, runWorkflow, getWorkflows, updateWorkflow, getWorkflow, deleteWorkflow } from '../api/workflows';
import type { ComponentOut, WorkflowStepConfig, WorkflowOut } from '../types';
import { useRouter } from 'vue-router';

// PrimeVue Components
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Tag from 'primevue/tag';
import Avatar from 'primevue/avatar';
import Divider from 'primevue/divider';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import Dropdown from 'primevue/dropdown';

const router = useRouter();
const components = ref<ComponentOut[]>([]);
const existingWorkflows = ref<WorkflowOut[]>([]);
const selectedWorkflowId = ref<string | null>(null);
const filterText = ref('');

// Workflow State
const workflowMeta = ref({ name: 'New Workflow', description: '' });
const savedId = ref<string | null>(null);

// Local Step representation with stringified JSON for editing
interface UIMappedStep {
  step_id: number;
  component_id: string;
  configStr: string;
  inputMapStr: string;
}

const steps = ref<UIMappedStep[]>([]);
const runPayloadStr = ref('{}');

const fetchWorkflows = async () => {
    try {
        existingWorkflows.value = await getWorkflows();
    } catch (e) {
        console.error("Failed to fetch workflows", e);
    }
};

onMounted(async () => {
  components.value = await getComponents();
  await fetchWorkflows(); // Load list on mount
});

const loadWorkflow = async () => {
    if (!selectedWorkflowId.value) return;
    try {
        const wf = await getWorkflow(selectedWorkflowId.value);
        savedId.value = wf.id;
        workflowMeta.value = { name: wf.name, description: wf.description };
        
        // Map steps
        steps.value = wf.steps.map(s => ({
            step_id: s.step_id,
            component_id: s.component_id,
            configStr: JSON.stringify(s.config, null, 2),
            inputMapStr: JSON.stringify(s.input_mapping, null, 2)
        }));
        
        // Load persist payload
        const savedPayload = localStorage.getItem(`wf_payload_${wf.id}`);
        if (savedPayload) {
            runPayloadStr.value = savedPayload;
        } else {
            runPayloadStr.value = '{}';
        }

    } catch (e) {
        console.error("Error loading workflow", e);
        alert("Failed to load workflow");
    }
};

const resetForm = () => {
    savedId.value = null;
    selectedWorkflowId.value = null;
    workflowMeta.value = { name: 'New Workflow', description: '' };
    steps.value = [];
    runPayloadStr.value = '{}';
};

const filteredComponents = computed(() => {
  const txt = filterText.value.toLowerCase();
  return components.value.filter(c => 
    c.name.toLowerCase().includes(txt) || 
    c.tags.some(t => t.includes(txt))
  );
});

const getComponentName = (id: string) => {
  return components.value.find(c => c.id === id)?.name || id;
};

const addStep = (comp: ComponentOut) => {
  steps.value.push({
    step_id: steps.value.length + 1,
    component_id: comp.id,
    configStr: '{}',
    inputMapStr: '{}',
  });
};

const removeStep = (index: number) => {
  steps.value.splice(index, 1);
  // Re-index
  steps.value.forEach((s, i) => s.step_id = i + 1);
};

const moveStep = (index: number, direction: number) => {
  const newIndex = index + direction;
  if (newIndex >= 0 && newIndex < steps.value.length) {
    const removed = steps.value.splice(index, 1)[0];
    if (!removed) return; 

    steps.value.splice(newIndex, 0, removed);
    steps.value.forEach((s, i) => {
      s.step_id = i + 1;
    });
  }
};


const saveWorkflow = async () => {
  try {
    const apiSteps: WorkflowStepConfig[] = steps.value.map(s => ({
      step_id: s.step_id,
      component_id: s.component_id,
      config: JSON.parse(s.configStr || '{}'),
      input_mapping: JSON.parse(s.inputMapStr || '{}'),
    }));

    const payload = {
      name: workflowMeta.value.name,
      description: workflowMeta.value.description,
      steps: apiSteps,
    };

    if (savedId.value) {
        await updateWorkflow(savedId.value, payload);
        alert('Workflow updated!');
    } else {
        const res = await createWorkflow(payload);
        savedId.value = res.id;
        alert('Workflow created!');
    }
    await fetchWorkflows(); // Refresh list
  } catch (e: any) {
    console.error(e);
    const msg = e.response?.data?.detail || e.message || 'Unknown error';
    alert(`Error saving workflow: ${JSON.stringify(msg)}`);
  }
};

const executeRun = async () => {
  if (!savedId.value) return;
  try {
    const payload = JSON.parse(runPayloadStr.value || '{}');
    const run = await runWorkflow(savedId.value, payload);
    
    // Save payload to localStorage for convenience
    if (savedId.value) {
        localStorage.setItem(`wf_payload_${savedId.value}`, runPayloadStr.value);
    }
    
    router.push(`/runs/${run.id}`);
  } catch (e: any) {
    console.error(e);
    const msg = e.response?.data?.detail || e.message || 'Unknown error';
    alert(`Error starting run: ${JSON.stringify(msg)}`);
  }
};

const deleteCurrentWorkflow = async () => {
    if (!savedId.value) return;
    if (!confirm("Are you sure you want to delete this workflow?")) return;
    
    try {
        await deleteWorkflow(savedId.value);
        alert("Workflow deleted");
        resetForm();
        await fetchWorkflows();
    } catch (e) {
        console.error(e);
        alert("Failed to delete workflow");
    }
};
</script>

<style scoped>
.workflows-page {
  /* Using PrimeFlex-like utility classes in template, minimal custom CSS needed */
  height: calc(100vh - 64px - 48px); /* Approximate height adjustment */
}
</style>
