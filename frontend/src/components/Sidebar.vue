<template>
  <aside 
    class="sidebar transition-all duration-300 flex flex-column" 
    :class="{ 'collapsed': isCollapsed }"
    @mouseenter="expandSidebar"
    @mouseleave="collapseSidebar"
  >
    <!-- Header: Logo & Identity -->
    <div class="logo flex align-items-center justify-content-between px-3 py-3 mb-2 border-bottom-1 border-gray-800">
      <div v-if="!isCollapsed" class="font-bold text-xl text-white white-space-nowrap overflow-hidden cursor-pointer fadein animation-duration-300" @click="goHome">
        {{ themeStore.currentTheme.logo.text }} 
        <span :style="{ color: themeStore.currentTheme.logo.dotColor || 'var(--color-brand-primary)' }">.</span>
      </div>
      <div v-else class="font-bold text-xl text-white mx-auto cursor-pointer fadein animation-duration-300" @click="goHome">
        {{ themeStore.currentTheme.logo.text.charAt(0) }}<span :style="{ color: themeStore.currentTheme.logo.dotColor || 'var(--color-brand-primary)' }">.</span>
      </div>
    </div>

    <!-- Navigation Groups -->
    <nav class="flex-1 overflow-y-auto custom-scrollbar flex flex-column gap-4 px-2 py-3">
      <div v-for="group in menuGroups" :key="group.title" class="nav-group">
        <!-- Group Title -->
        <div v-if="!isCollapsed" class="group-title text-xs font-bold text-gray-500 px-3 mb-2 uppercase tracking-wide fadein animation-duration-200">
          {{ group.title }}
        </div>
        <div v-if="isCollapsed" class="divider my-2 border-top-1 border-gray-800 opacity-20"></div>
        
        <!-- Group Items -->
        <div class="flex flex-column gap-1">
          <router-link 
            v-for="item in group.items" 
            :key="item.path" 
            :to="item.path"
            class="nav-item flex align-items-center p-2 text-gray-400 border-round hover:surface-hover transition-colors no-underline"
            active-class="active-route"
            v-tooltip.right="isCollapsed ? item.label : null"
          >
            <i :class="['pi text-lg', item.icon, isCollapsed ? 'mx-auto' : 'mr-3']"></i>
            <span v-if="!isCollapsed" class="white-space-nowrap font-medium fadein animation-duration-200">{{ item.label }}</span>
          </router-link>
        </div>
      </div>
    </nav>
    
    <!-- Model Selector -->
    <div class="model-selector-container px-2 mb-3">
        <div v-if="!isCollapsed" class="model-selector border-round flex flex-column gap-2 p-3 bg-gray-900 border-1 border-gray-800">
            <div class="text-xs font-bold text-gray-500 uppercase tracking-wide flex align-items-center justify-content-between">
                <span>Active Model</span>
                <i class="pi pi-bolt text-yellow-500"></i>
            </div>
            <Dropdown 
                v-model="selectedModel" 
                :options="availableModels" 
                optionLabel="name" 
                class="w-full model-dropdown"
                @change="onModelChange"
                :loading="loadingModels"
                placeholder="Select Model"
            />
        </div>
        <div v-else class="collapsed-model-indicator flex justify-content-center p-2" v-tooltip.right="selectedModel?.name || 'Select Model'">
            <div class="w-2rem h-2rem border-circle bg-gray-900 border-1 border-gray-800 flex align-items-center justify-content-center cursor-pointer hover:border-brand">
                <i class="pi pi-server text-brand text-xs"></i>
            </div>
        </div>
    </div>

    <!-- Bottom: All Apps Trigger -->
    <div class="px-2 pb-3">
        <div 
            class="nav-item flex align-items-center p-2 text-gray-400 border-round hover:surface-hover transition-colors cursor-pointer"
            @click="openAppLauncher"
            v-tooltip.right="isCollapsed ? 'All Apps' : null"
        >
            <i class="pi pi-th-large text-lg" :class="[isCollapsed ? 'mx-auto' : 'mr-3']"></i>
            <span v-if="!isCollapsed" class="white-space-nowrap font-medium fadein animation-duration-200">All Apps</span>
        </div>
    </div>
    
    <!-- App Launcher Drawer -->
    <Sidebar 
        v-model:visible="showAppLauncher" 
        position="left" 
        class="app-launcher-drawer"
        :style="{ width: '350px' }"
    >
        <div class="flex flex-column h-full">
            <h2 class="text-xl font-bold mb-4">All Applications</h2>
            <div class="p-input-icon-left w-full mb-4">
                <i class="pi pi-search" />
                <InputText v-model="appSearch" placeholder="Find an app..." class="w-full" />
            </div>
            
            <div class="apps-grid flex flex-column gap-2 overflow-y-auto">
                 <div 
                    v-for="app in filteredApps" 
                    :key="app.label"
                    class="app-item p-3 border-round surface-card hover:surface-100 cursor-pointer flex align-items-center gap-3 transition-colors border-1 border-transparent hover:border-300"
                    @click="navigateToApp(app.path)"
                 >
                    <div class="app-icon w-2rem h-2rem flex align-items-center justify-content-center bg-green-100 text-green-600 border-round">
                        <i :class="app.icon"></i>
                    </div>
                    <div>
                        <div class="font-medium text-900">{{ app.label }}</div>
                        <div class="text-xs text-500">Launch application</div>
                    </div>
                 </div>
            </div>
        </div>
    </Sidebar>

  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useThemeStore } from '../stores/theme';
import { getWorkflows } from '../api/workflows';
import { getModels, setActiveModel, type AIModel } from '../api/models';
import InputText from 'primevue/inputtext';
import Sidebar from 'primevue/sidebar';
import Dropdown from 'primevue/dropdown';
import { useToast } from 'primevue/usetoast';

const auth = useAuthStore();
const themeStore = useThemeStore();
const router = useRouter();

const toast = useToast();

const isCollapsed = ref(true); // Default collapsed on load (expanded on hover)
const showAppLauncher = ref(false);
const appSearch = ref('');
const customApps = ref<any[]>([]);

const availableModels = ref<AIModel[]>([]);
const selectedModel = ref<AIModel | null>(null);
const loadingModels = ref(false);

onMounted(async () => {
    if (auth.state.token) {
        // Fetch Apps
        try {
            const wfs = await getWorkflows();
            customApps.value = wfs.map(w => ({
                label: w.name,
                path: `/workflows?load=${w.id}`,
                icon: 'pi pi-box'
            }));
        } catch (e) {
            console.error("Failed to fetch custom apps", e);
        }

        // Fetch Models
        try {
            loadingModels.value = true;
            const models = await getModels();
            availableModels.value = models;
            const active = models.find(m => m.is_active);
            selectedModel.value = active ?? models[0] ?? null;
        } catch (e) {
            console.error("Failed to fetch models", e);
        } finally {
            loadingModels.value = false;
        }
    }
});

const onModelChange = async (event: any) => {
    const model = event.value;
    if (!model) return;

    try {
        await setActiveModel(model.id);
        toast.add({
            severity: 'success',
            summary: 'Model Switched',
            detail: `Active model is now ${model.name}`,
            life: 3000
        });
    } catch (e) {
        console.error("Failed to set active model", e);
        toast.add({
            severity: 'error',
            summary: 'Switch Failed',
            detail: 'Could not update active model',
            life: 5000
        });
    }
};

/* Hover Expand Logic */
const expandSidebar = () => {
    isCollapsed.value = false;
};

const collapseSidebar = () => {
    isCollapsed.value = true;
};

const goHome = () => {
    router.push('/dashboard');
};

const openAppLauncher = () => {
    showAppLauncher.value = true;
};

const navigateToApp = (path: string) => {
    router.push(path);
    showAppLauncher.value = false;
};

/* Menu Groups */
const menuGroups = computed(() => {
    const groups = [
      {
        title: 'Core',
        items: [
          { label: 'Dashboard', path: '/dashboard', icon: 'pi pi-home' },
          { label: 'Workflows', path: '/workflows', icon: 'pi pi-sitemap' },
          { label: 'Skills', path: '/skills', icon: 'pi pi-compass' },
        ]
      },
      {
        title: 'Enterprise Apps',
        items: [
          { label: 'Meeting AI', path: '/apps/meeting-ai', icon: 'pi pi-microphone' },
          { label: 'Policy Analysis', path: '/apps/policy-analysis', icon: 'pi pi-check-square' },
          { label: 'PPT Generator', path: '/apps/ppt-generator', icon: 'pi pi-desktop' },
          { label: 'Flowchart Generator', path: '/apps/flowchart-generator', icon: 'pi pi-share-alt' },
          { label: 'Contract Assistant', path: '/apps/contracts', icon: 'pi pi-file-pdf' },
          { label: 'Expense Helper', path: '/apps/expenses', icon: 'pi pi-wallet' },
          ...customApps.value 
        ]
      },
      {
        title: 'Operations',
        items: [
           { label: 'Settings', path: '/profile', icon: 'pi pi-cog' },
        ]
      }
    ];

    // Admin Group
    if (auth.state.isSuperuser) {
        groups.push({
            title: 'Admin',
            items: [
                { label: 'User Management', path: '/users', icon: 'pi pi-users' },
                { label: 'Feedback', path: '/feedback', icon: 'pi pi-comments' }
            ]
        });
    }

    return groups;
});

/* App Launcher Data */
const filteredApps = computed(() => {
    const all = [
        { label: 'Dashboard', path: '/dashboard', icon: 'pi pi-home' },
        { label: 'Contract Assistant', path: '/apps/contracts', icon: 'pi pi-file-pdf' },
        { label: 'Expense Helper', path: '/apps/expenses', icon: 'pi pi-wallet' },
        { label: 'Meeting AI', path: '/apps/meeting-ai', icon: 'pi pi-microphone' },
        { label: 'Policy Analysis', path: '/apps/policy-analysis', icon: 'pi pi-check-square' },
        { label: 'PPT Generator', path: '/apps/ppt-generator', icon: 'pi pi-desktop' },
        { label: 'Flowchart Generator', path: '/apps/flowchart-generator', icon: 'pi pi-share-alt' },
        { label: 'Workflows', path: '/workflows', icon: 'pi pi-sitemap' },
        { label: 'Skills', path: '/skills', icon: 'pi pi-compass' },
        { label: 'Components', path: '/components', icon: 'pi pi-box' },
        { label: 'Capability Map', path: '/capability-map', icon: 'pi pi-th-large' },
        { label: 'Monitoring', path: '/monitoring', icon: 'pi pi-chart-line' },
        { label: 'Models', path: '/models', icon: 'pi pi-server' },
        { label: 'News / Posts', path: '/news', icon: 'pi pi-megaphone' },
        ...customApps.value
    ];
    
    if (!appSearch.value) return all;
    return all.filter(a => a.label.toLowerCase().includes(appSearch.value.toLowerCase()));
});
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width-expanded, 260px);
  background-color: var(--color-black); /* Use theme vars via store if injected, or mapped var */
  height: 100vh;
  border-right: 1px solid #1f1f1f;
  z-index: 100;
}

.sidebar.collapsed {
  width: 70px;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1); 
  color: #FFF;
}

.nav-item.active-route {
  background-color: #1a1a1a;
  color: #FFF;
  border-left: 3px solid var(--color-brand-primary);
  padding-left: calc(0.5rem - 3px);
}

/* Model Selector Styling */
.model-selector {
    background-color: #0a0a0a !important;
}

.model-dropdown {
    background: transparent !important;
    border: none !important;
    font-size: 0.85rem !important;
    color: #fff !important;
}

:deep(.p-dropdown-label) {
    padding: 0.25rem 0.5rem !important;
    color: #e2e8f0;
}

:deep(.p-dropdown-trigger) {
    width: 2rem !important;
}

:deep(.p-dropdown-panel) {
    background-color: #0a0a0a !important;
    border: 1px solid #1f1f1f !important;
}

:deep(.p-dropdown-item) {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
}

:deep(.p-dropdown-item.p-highlight) {
    background-color: rgba(16, 185, 129, 0.1) !important;
    color: var(--color-brand-primary) !important;
}

.text-brand {
    color: var(--color-brand-primary);
}

.hover\:border-brand:hover {
    border-color: var(--color-brand-primary) !important;
}
</style>
