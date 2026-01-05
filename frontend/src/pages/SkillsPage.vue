<template>
  <div class="skills-page p-4 fade-in">
    <!-- Header -->
    <div class="flex justify-content-between align-items-end mb-5 border-bottom-1 surface-border pb-3">
      <div>
        <h1 class="text-3xl font-bold text-900 mb-2 gradient-text">Skill Library</h1>
        <p class="text-600 m-0 text-sm" style="max-width: 600px; line-height: 1.6;">
          Manage and execute agent capabilities from the file system. 
          Folder-based skills in <code class="surface-ground px-2 py-1 border-round font-mono text-sm text-primary">app/skills/</code> are automatically discovered.
        </p>
      </div>
      
      <Button 
        @click="handleRefresh" 
        :loading="loading"
        severity="secondary"
        outlined
        class="flex align-items-center gap-2 border-round-xl shadow-1"
      >
        <i class="pi pi-refresh" :class="{ 'spin-icon': loading }"></i>
        <span>Reload Skills</span>
      </Button>
    </div>

    <!-- Error State -->
    <Message v-if="error" severity="error" :closable="false" class="mb-4 shadow-1 border-round-xl">
        {{ error }}
    </Message>

    <!-- Loading State -->
    <div v-if="loading && !skills.length" class="flex flex-column align-items-center justify-content-center py-8 text-500">
      <i class="pi pi-compass text-6xl mb-4 opacity-50 absolute-center-icon"></i>
      <p>Scanning skill directories...</p>
    </div>

    <!-- Skills Grid (PrimeFlex) -->
    <div v-else class="grid">
      <div v-for="skill in skills" :key="skill.id" class="col-12 md:col-6 lg:col-4 xl:col-3">
        <div class="card p-3 h-full flex flex-column surface-card border-1 surface-border border-round-2xl shadow-1 hover:shadow-4 transition-all transition-duration-300 relative overflow-hidden group">
            
            <!-- Active Indicator (Top Right) -->
            <div class="absolute top-0 right-0 p-3">
                <div class="w-2 h-2 border-circle" :class="skill.is_active ? 'bg-green-500 shadow-custom' : 'bg-gray-400'"></div>
            </div>

            <!-- Header -->
            <div class="flex align-items-center gap-3 mb-3">
                <div class="flex align-items-center justify-content-center w-3rem h-3rem border-round-xl bg-primary-50 text-primary text-xl shadow-1">
                    <span v-if="skill.category?.includes('ocr')">📄</span>
                    <span v-else-if="skill.category?.includes('extraction')">🧩</span>
                    <span v-else-if="skill.category?.includes('demo')">👋</span>
                    <span v-else>⚡</span>
                </div>
                <div class="overflow-hidden">
                    <h3 class="text-xl font-bold text-900 m-0 white-space-nowrap overflow-hidden text-overflow-ellipsis">{{ skill.name }}</h3>
                    <div class="flex align-items-center gap-2 mt-1">
                        <Tag :value="skill.category" severity="info" class="text-xs uppercase px-2 py-0 border-round-md opacity-80"></Tag>
                        <!-- Subtle Skill Type -->
                        <span class="text-xs text-400">{{ skill.skill_type.toLowerCase() }}</span>
                    </div>
                </div>
            </div>

            <!-- Description -->
            <div class="flex-1 mb-4">
                <p class="text-600 text-sm line-height-3 m-0 line-clamp-3">
                    {{ skill.description || 'No description provided.' }}
                </p>
            </div>

            <!-- Footer -->
            <div class="flex justify-content-between align-items-center mt-auto pt-3 border-top-1 surface-border">
                <div class="text-xs text-500 font-mono">v1.0.0</div>
                <div class="flex gap-2">
                    <Button 
                        icon="pi pi-pencil" 
                        size="small"
                        rounded 
                        outlined
                        severity="secondary"
                        @click="openEditor(skill)"
                        v-tooltip="'Edit SOP'"
                        class="h-2rem w-2rem opacity-60 hover:opacity-100"
                    />
                    <Button 
                        label="Run" 
                        icon="pi pi-play" 
                        size="small"
                        rounded 
                        text
                        @click="openExecute(skill)"
                        class="hover:surface-100 transition-colors transition-duration-200"
                    />
                </div>
            </div>
            
            <!-- Hover Effect Highlight -->
            <div class="absolute bottom-0 left-0 w-full h-1 bg-primary transform scale-x-0 group-hover:scale-x-100 transition-transform transition-duration-300"></div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="skills.length === 0 && !loading" class="col-12 py-8 text-center surface-card border-round-2xl border-1 surface-border border-dashed">
        <div class="text-900 font-bold text-xl mb-2">No Skills Found</div>
        <p class="text-600 mb-4">Add folders to <code class="font-mono text-primary">app/skills/</code></p>
        <Button label="Refresh" icon="pi pi-refresh" text @click="handleRefresh" />
      </div>
    </div>

    <!-- Editor Dialog (Skill Workspace) -->
    <Dialog 
        v-model:visible="showEditor" 
        :header="`Skill Workspace: ${editingSkill?.name}`" 
        modal 
        class="p-fluid"
        :style="{ width: '85vw', minWidth: '900px', height: '80vh' }"
        :maximizable="true"
        :contentStyle="{ height: '100%', padding: '0' }"
    >
         <div class="flex h-full surface-ground">
             <!-- Sidebar: File Tree -->
             <div class="w-16rem surface-card border-right-1 surface-border flex flex-column">
                 <div class="p-3 font-bold text-sm text-700 border-bottom-1 surface-border bg-gray-50">
                    <i class="pi pi-folder-open mr-2"></i> Files
                 </div>
                 <div class="flex-1 overflow-y-auto p-2">
                     <div 
                        v-for="file in skillFiles" 
                        :key="file"
                        @click="openFile(file)"
                        class="p-2 border-round cursor-pointer text-sm mb-1 flex align-items-center transition-colors transition-duration-150"
                        :class="currentFile === file ? 'bg-primary-50 text-primary font-bold' : 'text-700 hover:surface-100'"
                     >
                        <i class="pi mr-2 text-sm" :class="getFileIcon(file)"></i>
                        <span class="white-space-nowrap overflow-hidden text-overflow-ellipsis">{{ file }}</span>
                     </div>
                 </div>
                 <div class="p-2 border-top-1 surface-border text-xs text-500 text-center">
                    Auto-saved to disk
                 </div>
             </div>

             <!-- Main Content: Editor -->
             <div class="flex-1 flex flex-column h-full">
                 <div class="p-2 surface-100 border-bottom-1 surface-border flex justify-content-between align-items-center">
                     <span class="font-mono text-sm text-900 ml-2">{{ currentFile }}</span>
                     <div class="flex gap-2">
                        <Button 
                            label="Save" 
                            icon="pi pi-save" 
                            size="small" 
                            @click="saveSkillFile" 
                            :loading="saving"
                            class="py-1 px-3"
                        />
                     </div>
                 </div>
                 <div class="flex-1 relative">
                     <Textarea 
                        v-model="editorContent" 
                        class="w-full h-full font-mono text-sm leading-relaxed p-4 border-none border-noround focus:shadow-none" 
                        style="resize: none; background: #1e1e1e; color: #d4d4d4; outline: none;"
                        spellcheck="false"
                     />
                 </div>
             </div>
         </div>
    </Dialog>

    <!-- Execute Dialog -->
    <Dialog 
        v-model:visible="showDialog" 
        :header="`Execute: ${selectedSkill?.name}`" 
        modal 
        class="p-fluid"
        :style="{ width: '50vw', minWidth: '600px' }"
        :breakpoints="{ '960px': '75vw', '641px': '95vw' }"
        :maximizable="true"
    >
        <div class="flex flex-column h-full">
            <!-- Instructions Panel -->
             <div v-if="selectedSkill?.instructions" class="mb-4">
                <div class="surface-ground border-round-lg p-3 border-1 surface-border">
                    <div class="flex align-items-center gap-2 mb-2 text-primary font-bold text-sm uppercase">
                        <i class="pi pi-book"></i> Instructions
                    </div>
                    <div class="text-sm text-700 w-full overflow-auto" style="max-height: 150px; white-space: pre-wrap; line-height: 1.6;">{{ selectedSkill.instructions }}</div>
                </div>
             </div>

            <div class="field mb-4">
                <label class="block font-bold text-900 mb-2">Input Parameters (JSON)</label>
                 <Textarea 
                    v-model="executionInput" 
                    rows="8" 
                    class="font-mono text-sm line-height-3 w-full"
                    :class="{'p-invalid': jsonError}"
                    placeholder="{ ... }" 
                />
                <small v-if="jsonError" class="p-error">{{ jsonError }}</small>
            </div>

            <!-- Result Panel -->
            <div v-if="executionResult || executionError" class="mb-4 border-round-lg overflow-hidden border-1" :class="executionError ? 'surface-ground border-red-200' : 'surface-ground border-green-200'">
                 <div class="px-3 py-2 flex justify-content-between align-items-center" :class="executionError ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'">
                     <span class="font-bold text-sm">{{ executionError ? 'Execution Failed' : 'Success Output' }}</span>
                     <span class="text-xs opacity-70">{{ executionTime }}ms</span>
                 </div>
                 <pre class="p-3 m-0 text-sm font-mono overflow-auto" style="max-height: 300px;">{{ executionError || JSON.stringify(executionResult, null, 2) }}</pre>
            </div>
        </div>

        <template #footer>
            <Button label="Cancel" icon="pi pi-times" text @click="closeDialog" class="p-button-secondary" />
            <Button 
                label="Run Procedure" 
                icon="pi pi-bolt" 
                @click="handleExecute" 
                :loading="executing"
                class="p-button-primary bg-primary border-primary"
            />
        </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getSkills, refreshSkills, runSkill, getSkillFiles, getSkillFile, updateSkillFile, type Skill } from '../api/skills';

// PrimeVue Components
import Button from 'primevue/button';
import Message from 'primevue/message';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import Textarea from 'primevue/textarea';
// import Tooltip from 'primevue/tooltip'; // Directive

const skills = ref<Skill[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

// Editor State
const showEditor = ref(false);
const editingSkill = ref<Skill | null>(null);
const editorContent = ref('');
const saving = ref(false);
const skillFiles = ref<string[]>([]);
const currentFile = ref<string>('');

const openEditor = async (skill: Skill) => {
    try {
        editingSkill.value = skill;
        showEditor.value = true;
        editorContent.value = '';
        currentFile.value = '';
        
        // Load file list
        skillFiles.value = await getSkillFiles(skill.name);
        
        // Open skill.md by default if exists
        if (skillFiles.value.includes('skill.md')) {
            await openFile('skill.md');
        } else if (skillFiles.value.length > 0) {
            await openFile(skillFiles.value[0]!);
        }
    } catch (e) {
        alert("Failed to load skill workspace");
    }
};

const openFile = async (path: string) => {
    try {
        currentFile.value = path;
        editorContent.value = "Loading...";
        const content = await getSkillFile(editingSkill.value!.name, path);
        editorContent.value = content;
    } catch (e) {
        editorContent.value = "Error loading file content.";
    }
}

const getFileIcon = (fileName: string) => {
    if (fileName.endsWith('.md')) return 'pi-file-edit text-blue-500';
    if (fileName.endsWith('.py')) return 'pi-cog text-yellow-500';
    if (fileName.endsWith('.json')) return 'pi-code text-green-500';
    return 'pi-file text-500';
}



const saveSkillFile = async () => {
    if (!editingSkill.value || !currentFile.value) return;
    try {
        saving.value = true;
        await updateSkillFile(editingSkill.value.name, currentFile.value, editorContent.value);
        // Toast success? Using alert for MVP quick feedback
        // alert("Saved!"); 
    } catch (e) {
        alert("Failed to save file");
    } finally {
        saving.value = false;
    }
};

const showDialog = ref(false);
const selectedSkill = ref<Skill | null>(null);
const executionInput = ref('{}');
const executing = ref(false);
const executionResult = ref<any>(null);
const executionError = ref<string | null>(null);
const jsonError = ref<string | null>(null);
const executionTime = ref(0);

const fetchSkills = async () => {
  try {
    loading.value = true;
    error.value = null;
    const data = await getSkills();
    skills.value = (Array.isArray(data) ? data : []).map(s => ({
        ...s,
        instructions: s.configuration?.instructions || s.instructions || '' 
    }));
  } catch (err) {
    console.error(err);
    error.value = "Failed to load skills";
  } finally {
    loading.value = false;
  }
};

const handleRefresh = async () => {
  try {
    loading.value = true;
    await refreshSkills();
    await fetchSkills();
  } catch (err) {
    error.value = "Failed to refresh skills";
  } finally {
    loading.value = false;
  }
};

const openExecute = (skill: Skill) => {
  selectedSkill.value = skill;
  const defaultSchema = skill.input_schema || {};
  executionInput.value = JSON.stringify(defaultSchema, null, 2);
  executionResult.value = null;
  executionError.value = null;
  jsonError.value = null;
  showDialog.value = true;
};

const closeDialog = () => {
    showDialog.value = false;
    selectedSkill.value = null;
};

const handleExecute = async () => {
  if (!selectedSkill.value) return;
  jsonError.value = null;
  
  try {
    const input = JSON.parse(executionInput.value);
    
    executing.value = true;
    executionResult.value = null;
    executionError.value = null;
    
    const startTime = performance.now();
    const res = await runSkill(selectedSkill.value.name, input);
    executionResult.value = res.result || res; 
    const endTime = performance.now();
    executionTime.value = Math.round(endTime - startTime);
    
  } catch (err: any) {
    if (err instanceof SyntaxError) {
        jsonError.value = "Invalid JSON format";
    } else {
        executionError.value = err.message || "Unknown error";
    }
  } finally {
    executing.value = false;
  }
};

onMounted(() => {
  fetchSkills();
});
</script>

<style scoped>
/* Custom animations and utilities that PrimeFlex might miss */
.fade-in {
    animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.spin-icon {
    animation: spin 1s linear infinite;
}
@keyframes spin {
    100% { transform: rotate(360deg); }
}

.line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.gradient-text {
    background: linear-gradient(120deg, var(--primary-color), var(--primary-500));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.shadow-custom {
    box-shadow: 0 0 10px var(--green-500);
}

.group:hover .group-hover\:scale-x-100 {
    transform: scaleX(1);
}
</style>
