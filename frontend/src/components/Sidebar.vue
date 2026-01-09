<template>
  <aside class="sidebar transition-all duration-300 flex flex-column" :class="{ 'collapsed': isCollapsed }">
    <!-- Header -->
    <div class="logo flex align-items-center justify-content-between px-3 py-3 mb-2">
      <div v-if="!isCollapsed" class="font-bold text-xl text-white white-space-nowrap overflow-hidden">
        Ɐ Platform <span class="text-green-500 text-2xl line-height-1">.</span>
      </div>
      <div v-else class="font-bold text-xl text-white mx-auto cursor-pointer" @click="toggleSidebar">
        Ɐ<span class="text-green-500">.</span>
      </div>
      <Button 
        v-if="!isCollapsed"
        icon="pi pi-angle-left" 
        text 
        rounded 
        class="text-gray-400 hover:text-white w-2rem h-2rem"
        @click="toggleSidebar"
      />
    </div>

    <!-- Navigation Groups -->
    <nav class="flex-1 overflow-y-auto custom-scrollbar flex flex-column gap-4 px-2">
      <div v-for="group in menuGroups" :key="group.title" class="nav-group">
        <div v-if="!isCollapsed" class="group-title text-xs font-bold text-500 px-3 mb-2 uppercase tracking-wide">
          {{ group.title }}
        </div>
        <div v-if="isCollapsed" class="divider my-2 border-top-1 surface-border opacity-20"></div>
        
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
            <span v-if="!isCollapsed" class="white-space-nowrap font-medium">{{ item.label }}</span>
          </router-link>
        </div>
      </div>
    </nav>
    
    <!-- Feedback Button -->
    <div 
        class="feedback-btn mx-3 mb-2 p-2 border-round hover:surface-700 cursor-pointer transition-colors flex align-items-center text-gray-400 hover:text-white"
        @click="showFeedbackDialog = true"
        v-tooltip.right="isCollapsed ? 'Send Feedback' : null"
    >
        <i class="pi pi-comments text-lg" :class="{ 'mx-auto': isCollapsed, 'mr-3': !isCollapsed }"></i>
        <span v-if="!isCollapsed" class="font-medium text-sm">Feedback</span>
    </div>

    <!-- User Profile (Bottom) -->
    <!-- Clickable Container for Menu -->
    <div 
        class="user-profile border-top-1 border-gray-800 p-3 flex align-items-center gap-3 mt-auto cursor-pointer hover:surface-800 transition-colors"
        @click="toggleUserMenu"
        aria-haspopup="true" 
        aria-controls="user_menu"
    >
      <Avatar :image="auth.state.avatarUrl || undefined" :label="!auth.state.avatarUrl ? userInitials : undefined" class="bg-green-500 text-white flex-shrink-0" shape="circle" style="background-color: transparent !important;" />
      <div v-if="!isCollapsed" class="user-info overflow-hidden">
        <div class="text-white font-semibold text-sm white-space-nowrap">{{ userName }}</div>
        <div class="text-gray-500 text-xs white-space-nowrap">{{ userRole }}</div>
      </div>
      <i v-if="!isCollapsed" class="pi pi-angle-up text-gray-500 ml-auto"></i>
    </div>
    
    <!-- Popup Menu -->
    <Menu ref="userMenu" id="user_menu" :model="userMenuItems" :popup="true" />
    
    <!-- Feedback Dialog -->
    <Dialog v-model:visible="showFeedbackDialog" header="Send Feedback" :modal="true" class="p-fluid" style="width: 400px">
        <div class="field">
            <label for="feedback" class="font-bold">Your Message</label>
            <Textarea id="feedback" v-model="feedbackContent" rows="5" placeholder="Tell us what you think or report a bug..." autofocus />
        </div>
        <template #footer>
            <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="showFeedbackDialog = false" />
            <Button label="Send" icon="pi pi-send" @click="submitFeedback" :loading="isSendingFeedback" :disabled="!feedbackContent.trim()" />
        </template>
    </Dialog>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import apiClient from '../api/client';
import { getWorkflows } from '../api/workflows'; // Import workflow fetcher
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
import Menu from 'primevue/menu';
import Dialog from 'primevue/dialog';
import Textarea from 'primevue/textarea';
import { useToast } from 'primevue/usetoast';

const auth = useAuthStore();
const router = useRouter();
const toast = useToast();
const userMenu = ref();

const isCollapsed = ref(false);
const showFeedbackDialog = ref(false);
const feedbackContent = ref('');
const isSendingFeedback = ref(false);
const customApps = ref<any[]>([]); // Store custom workflows

onMounted(async () => {
    if (auth.state.token) {
        try {
            const wfs = await getWorkflows();
            customApps.value = wfs.map(w => ({
                label: w.name,
                path: `/workflows?load=${w.id}`, // Open in Builder/Runner
                icon: 'pi pi-box'
            }));
        } catch (e) {
            console.error("Failed to fetch custom apps", e);
        }
    }
});

const userName = computed(() => auth.state.user?.full_name || 'User');
const userRole = computed(() => auth.state.isSuperuser ? 'Administrator' : 'User');
const userInitials = computed(() => {
    const name = auth.state.user?.full_name || 'User';
    return name.charAt(0).toUpperCase();
});

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const toggleUserMenu = (event: Event) => {
    userMenu.value.toggle(event);
};

const submitFeedback = async () => {
    if (!feedbackContent.value.trim()) return;
    
    isSendingFeedback.value = true;
    console.log("Submitting feedback:", feedbackContent.value);
    try {
        const res = await apiClient.post('/feedback', { content: feedbackContent.value });
        console.log("Feedback success:", res);
        toast.add({ severity: 'success', summary: 'Sent', detail: 'Thank you for your feedback!', life: 3000 });
        showFeedbackDialog.value = false;
        feedbackContent.value = '';
    } catch (e: any) {
        console.error("Failed to send feedback", e);
        const errorMsg = e.response?.data?.detail || e.message || 'Failed to send feedback';
        toast.add({ severity: 'error', summary: 'Error', detail: errorMsg, life: 5000 });
    } finally {
        isSendingFeedback.value = false;
    }
};

const userMenuItems = [
    {
        label: 'Profile',
        icon: 'pi pi-user',
        command: () => {
            router.push('/profile');
        }
    },
    {
        separator: true
    },
    {
        label: 'Sign Out',
        icon: 'pi pi-sign-out',
        command: () => {
            auth.logout();
            router.push('/login');
        }
    }
];

const menuGroups = computed(() => {
    const appsItems = [
          { label: 'Contract Assistant', path: '/apps/contracts', icon: 'pi pi-file-pdf' },
          { label: 'Expense Helper', path: '/apps/expenses', icon: 'pi pi-wallet' },
          ...customApps.value // Add user custom apps here
    ];

    const groups = [
      {
        title: 'Core',
        items: [
          { label: 'Dashboard', path: '/dashboard', icon: 'pi pi-home' },
          { label: 'Workflows', path: '/workflows', icon: 'pi pi-sitemap' },
          { label: 'Skills', path: '/skills', icon: 'pi pi-compass' },
          { label: 'Components', path: '/components', icon: 'pi pi-box' },
          { label: 'Capability Map', path: '/capability-map', icon: 'pi pi-th-large' },
        ]
      },
      // Enterprise Apps - Only for Pro/Enterprise
      ...(auth.state.user?.plan_name && auth.state.user.plan_name !== 'Starter' ? [{
        title: 'Enterprise Apps', 
        items: appsItems
      }] : []),
      {
        title: 'Operations',
        items: [
          { label: 'Monitoring', path: '/monitoring', icon: 'pi pi-chart-line' },
          { label: 'Models', path: '/models', icon: 'pi pi-server' },
          { label: 'News / Posts', path: '/news', icon: 'pi pi-megaphone' },
          { label: 'Settings', path: '/profile', icon: 'pi pi-cog' },
        ]
      },
      {
        title: 'Playbooks',
        items: [
          { label: 'Templates', path: '/templates', icon: 'pi pi-clone' },
        ]
      }
    ];

    if (auth.state.isSuperuser) {
        // Ensure groups[2] exists and has items. However, if Plan is Starter, groups[1] might be Operations.
        // Safer to find by title or just append. 
        // For simplicity: Admin is likely Pro, so [2] is Operations.
        // Let's protect it:
        const opsGroup = groups.find(g => g.title === 'Operations');
        if (opsGroup) {
             // Check if already exists?
             const hasUserManagement = opsGroup.items.some(i => i.label === 'User Management');
             if (!hasUserManagement) {
               opsGroup.items.unshift(
                   { label: 'User Management', path: '/users', icon: 'pi pi-users' },
                   { label: 'User Feedback', path: '/feedback', icon: 'pi pi-inbox' }
               );
             }
        }
    }

    return groups;
});
</script>

<style scoped>
.sidebar {
  width: 260px;
  background-color: var(--brand-black);
  height: 100vh;
  border-right: 1px solid #1f1f1f;
}

.sidebar.collapsed {
  width: 70px;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05); /* Slight hover effect */
  color: var(--brand-white);
}

.nav-item.active-route {
  background-color: #1a1a1a;
  color: var(--brand-white);
  border-left: 3px solid var(--brand-green);
  padding-left: calc(0.5rem - 3px); /* Compensate for border to keep icon aligned, or just accept the shift */
}

/* Tooltip handling usually done via PrimeVue Directive, ensuring it's installed in main.ts */
</style>
