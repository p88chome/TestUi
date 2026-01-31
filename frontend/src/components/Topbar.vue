<template>
  <header class="topbar">
    <!-- Left: Sidebar Toggle / Breadcrumb Placeholder -->
    <div class="topbar-left flex align-items-center">
        <!-- Optional: Add Sidebar Toggle here if needed, or leave empty for clean design -->
    </div>

    <!-- Center: Global Search -->
    <div class="topbar-center">
        <div class="global-search-container">
            <i class="pi pi-search global-search-icon" />
            <InputText 
                v-model="searchQuery" 
                placeholder="Search workflows, apps, models..." 
                class="global-search-input"
                @focus="showSearch"
                @input="handleSearch"
                autocomplete="off"
            />
            <!-- Search Results Overlay -->
            <OverlayPanel ref="searchOverlay" class="search-results-overlay" :style="{ width: '500px' }">
                <div v-if="filteredResults.length > 0">
                    <div v-for="(group, type) in groupedResults" :key="type" class="mb-3">
                        <div class="text-xs font-bold text-500 uppercase mb-2 px-2">{{ type }}</div>
                        <div 
                            v-for="item in group" 
                            :key="item.title"
                            class="p-2 border-round hover:surface-100 cursor-pointer flex align-items-center gap-3 transition-colors"
                            @click="selectResult(item)"
                        >
                            <i :class="getIconForType(type)" class="text-primary text-xl"></i>
                            <div>
                                <div class="font-medium text-900">{{ item.title }}</div>
                                <div class="text-xs text-500">{{ item.desc }}</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else class="p-3 text-center text-500">
                    <i class="pi pi-search text-2xl mb-2 block"></i>
                    No results found for "{{ searchQuery }}"
                </div>
            </OverlayPanel>
        </div>
    </div>

    <!-- Right: Tenant & User Controls -->
    <div class="topbar-right flex align-items-center gap-3">
        <!-- Tenant Switcher -->
        <div 
            class="tenant-switcher hidden md:flex align-items-center gap-2 px-3 py-1 border-round hover:surface-100 cursor-pointer transition-colors text-sm font-medium text-color-secondary"
            @click="toggleTenantMenu"
        >
            <i class="pi pi-building"></i>
            <span>{{ themeStore.currentTheme.name }}</span>
            <i class="pi pi-angle-down text-xs ml-1"></i>
        </div>
        <Menu ref="tenantMenuRef" :model="tenantMenuItems" :popup="true" />

        <!-- Notification -->
        <Button 
            icon="pi pi-bell" 
            text 
            rounded 
            class="text-color-secondary hover:text-color w-2rem h-2rem"
            v-tooltip.bottom="'Notifications'"
        />

        <!-- Settings / Theme -->
        <Button 
            icon="pi pi-cog" 
            text 
            rounded 
            class="text-color-secondary hover:text-color w-2rem h-2rem"
            v-tooltip.bottom="'Settings'"
        />

        <!-- User Profile Avatar -->
        <div class="user-profile relative ml-2">
            <Avatar 
                :image="auth.state.avatarUrl || undefined" 
                :label="userInitials" 
                class="flex-shrink-0 cursor-pointer" 
                shape="circle"
                :style="{ backgroundColor: 'var(--color-brand-primary)', color: '#FFF' }"
                @click="toggleUserMenu"
            />
             <Menu ref="userMenuRef" :model="userMenuItems" :popup="true" />
        </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useThemeStore } from '../stores/theme';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
import Menu from 'primevue/menu';
import OverlayPanel from 'primevue/overlaypanel';

const router = useRouter();
const auth = useAuthStore();
const themeStore = useThemeStore();

const searchQuery = ref('');
const userMenuRef = ref();
const tenantMenuRef = ref();
const searchOverlay = ref();

// Mock Search Data
const mockSearchData = [
    { type: 'Apps', title: 'Contract Assistant', desc: 'Enterprise App', link: '/apps/contracts' },
    { type: 'Apps', title: 'Expense Helper', desc: 'Enterprise App', link: '/apps/expenses' },
    { type: 'Apps', title: 'Meeting Minutes', desc: 'Productivity Tool', link: '/meeting-minutes' },
    { type: 'Workflows', title: 'Invoice Automation', desc: 'Finance Flow', link: '/workflows' },
    { type: 'Workflows', title: 'Onboarding V2', desc: 'HR Flow', link: '/workflows' },
    { type: 'Models', title: 'GPT-4-Turbo', desc: 'Azure OpenAI', link: '/models' },
    { type: 'Models', title: 'Claude 3 Opus', desc: 'Anthropic', link: '/models' },
];

const filteredResults = computed(() => {
    if (!searchQuery.value) return mockSearchData;
    const q = searchQuery.value.toLowerCase();
    return mockSearchData.filter(item => 
        item.title.toLowerCase().includes(q) || 
        item.desc.toLowerCase().includes(q)
    );
});

const groupedResults = computed(() => {
    const groups: any = {};
    filteredResults.value.forEach(item => {
        const typeKey = item.type;
        if (!groups[typeKey]) groups[typeKey] = [];
        groups[typeKey].push(item);
    });
    return groups;
});

const getIconForType = (type: string) => {
    switch(type) {
        case 'Apps': return 'pi pi-box';
        case 'Workflows': return 'pi pi-sitemap';
        case 'Models': return 'pi pi-server';
        default: return 'pi pi-file';
    }
};

const showSearch = (event: Event) => {
    searchOverlay.value.show(event, event.target);
};

const handleSearch = (event: Event) => {
    // If not visible, show it
    if (!searchOverlay.value.visible) {
        searchOverlay.value.show(event, event.target);
    }
};

const selectResult = (item: any) => {
    router.push(item.link);
//    searchQuery.value = ''; // Keep query or clear it? Keeping it feels like selection, clearing feels like navigation. Navigation usually clears context.
    searchQuery.value = '';
    searchOverlay.value.hide();
};

const userInitials = computed(() => {
    const name = auth.state.user?.full_name || 'User';
    return name.charAt(0).toUpperCase();
});

const toggleUserMenu = (event: Event) => {
    userMenuRef.value.toggle(event);
};

const toggleTenantMenu = (event: Event) => {
    tenantMenuRef.value.toggle(event);
};

// Tenant Menu Items (Dynamic from available themes)
const tenantMenuItems = computed(() => {
    return themeStore.availableThemes.map(theme => ({
        label: theme.name,
        icon: themeStore.currentTheme.name === theme.name ? 'pi pi-check text-green-500' : 'pi pi-building',
        command: () => themeStore.switchThemeByName(theme.name)
    }));
});

const userMenuItems = [
    {
        label: 'My Profile',
        icon: 'pi pi-user',
        command: () => router.push('/profile')
    },
    {
        label: 'Workspace Settings',
        icon: 'pi pi-cog',
        command: () => router.push('/settings')
    },
    { separator: true },
    {
        label: 'Sign Out',
        icon: 'pi pi-sign-out',
        command: () => {
            auth.logout();
            router.push('/login');
        }
    }
];
</script>

<style scoped>
.topbar {
  height: 64px;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  z-index: 1000;
}

.topbar-left {
    min-width: 260px; /* Aligns with Sidebar width */
    display: flex;
    align-items: center;
}

.topbar-center {
    flex: 1;
    display: flex;
    justify-content: center;
    max-width: 600px;
}

.global-search-container {
    width: 100%;
    position: relative;
    display: flex;
    align-items: center;
}

.global-search-icon {
    position: absolute;
    left: 1rem;
    z-index: 2;
    color: var(--color-gray);
    pointer-events: none;
    font-size: 1rem;
    top: 50%;
    transform: translateY(-50%);
}

:deep(.global-search-input) {
    width: 100%;
    background-color: var(--color-surface-muted);
    border: 1px solid transparent;
    border-radius: 6px;
    padding-left: 2.75rem !important;
    height: 40px;
    transition: all 0.2s;
}

:deep(.global-search-input:focus) {
    background-color: var(--color-surface);
    border-color: var(--color-brand-primary);
    box-shadow: 0 0 0 1px var(--color-brand-primary);
}

/* Overlay Styles */
:deep(.p-overlaypanel) {
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    border: 1px solid var(--color-border);
}
</style>
