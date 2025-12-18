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
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Button from 'primevue/button';
import Avatar from 'primevue/avatar';
import Menu from 'primevue/menu';

const auth = useAuthStore();
const router = useRouter();
const userMenu = ref();

const isCollapsed = ref(false);

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
    const groups = [
      {
        title: 'Core',
        items: [
          { label: 'Dashboard', path: '/dashboard', icon: 'pi pi-home' },
        ]
      },
      // Enterprise Apps - Only for Pro/Enterprise
      ...(auth.state.user?.plan_name && auth.state.user.plan_name !== 'Starter' ? [{
        title: 'Enterprise Apps', 
        items: [
          { label: 'Contract Assistant', path: '/apps/contracts', icon: 'pi pi-file-pdf' },
          { label: 'Expense Helper', path: '/apps/expenses', icon: 'pi pi-wallet' },
        ]
      }] : []),
      {
        title: 'Operations',
        items: [
          { label: 'Monitoring', path: '/monitoring', icon: 'pi pi-chart-line' },
          { label: 'Models', path: '/models', icon: 'pi pi-server' },
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
        // Ensure groups[2] exists and has items
        if (groups[2] && groups[2].items) {
             groups[2].items.unshift({ label: 'User Management', path: '/users', icon: 'pi pi-users' });
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
