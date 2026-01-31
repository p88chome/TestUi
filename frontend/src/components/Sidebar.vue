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
    
    <!-- Bottom: All Apps Trigger -->
    <div class="mt-auto px-2 pb-3">
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
import InputText from 'primevue/inputtext';
import Sidebar from 'primevue/sidebar';

const auth = useAuthStore();
const themeStore = useThemeStore();
const router = useRouter();

const isCollapsed = ref(true); // Default collapsed on load (expanded on hover)
const showAppLauncher = ref(false);
const appSearch = ref('');
const customApps = ref<any[]>([]);

onMounted(async () => {
    if (auth.state.token) {
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
    }
});

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
          { label: 'Contract Assistant', path: '/apps/contracts', icon: 'pi pi-file-pdf' },
          { label: 'Expense Helper', path: '/apps/expenses', icon: 'pi pi-wallet' },
          ...customApps.value 
        ]
      },
      {
        title: 'Operations',
        items: [
           { label: 'Models', path: '/models', icon: 'pi pi-server' },
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
</style>
