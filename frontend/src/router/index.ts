import { createRouter, createWebHistory } from 'vue-router';
import Layout from '../components/Layout.vue';
import ChatbotPage from '../pages/ChatbotPage.vue';
import LoginPage from '../pages/LoginPage.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: LoginPage
    },
    {
        path: '/',
        component: Layout,
        redirect: '/dashboard',
        meta: { requiresAuth: true },
        children: [
            // Workflows, Components, Runs removed as per request (Token usage -> Dashboard)

            // Enterprise Apps
            { path: 'apps/contracts', name: 'ContractAssistant', component: ChatbotPage, meta: { requiresPro: true } },
            { path: 'apps/expenses', name: 'ExpenseHelper', component: ChatbotPage, meta: { requiresPro: true } },

            // Operations
            { path: 'monitoring', name: 'Monitoring', component: () => import('../pages/ComingSoonPage.vue') },
            { path: 'models', name: 'Models', component: () => import('../pages/ComingSoonPage.vue') },
            { path: 'settings', name: 'Settings', component: () => import('../pages/ComingSoonPage.vue') },
            // Playbooks
            { path: 'templates', name: 'Templates', component: () => import('../pages/ComingSoonPage.vue') },
            { path: 'domains', name: 'Domains', component: () => import('../pages/ComingSoonPage.vue') },
            // Dashboard
            { path: 'dashboard', name: 'Dashboard', component: () => import('../pages/DashboardPage.vue') },

            // Admin
            {
                path: 'users',
                name: 'Users',
                component: () => import('../pages/UsersPage.vue'),
                meta: { adminOnly: true }
            },

            // Profile
            {
                path: 'profile',
                name: 'Profile',
                component: () => import('../pages/ProfilePage.vue')
            }
        ],
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach(async (to, _from, next) => {
    const token = localStorage.getItem('token');
    const isAuthenticated = !!token;

    // Basic check. ideally decode token or check store state if persisted/restored before guard.
    // For MVP, if route requires auth and no token -> login.

    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!isAuthenticated) {
            next('/login');
            return;
        }
    }

    // Check admin
    if (to.matched.some(record => record.meta.adminOnly)) {
        if (!isAuthenticated) { // Should ideally check isSuperuser here too, but rely on backend 403 for now or store
            next('/login');
            return;
        }
    }

    // Check Plan (Pro/Enterprise)
    // Check Plan (Pro/Enterprise)
    if (to.matched.some(record => record.meta.requiresPro)) {
        try {
            // Dynamic import to ensure Pinia is active
            const { useAuthStore } = await import('../stores/auth');
            const auth = useAuthStore();

            // If user is loaded and is Starter, block access
            if (auth.state.user && auth.state.user.plan_name === 'Starter') {
                // alert('Upgrade to Professional to access this feature.'); // Optional: simple alert before redirect
                next('/profile');
                return;
            }
        } catch (e) {
            console.error("Auth store access error in router", e);
        }
    }

    if (!isAuthenticated && to.matched.some(record => record.meta.requiresAuth)) {
        next('/login');
    } else {
        // If logged in and trying to go to login, redirect to dashboard
        if (isAuthenticated && to.name === 'Login') {
            next('/dashboard');
        } else {
            next();
        }
    }
});

export default router;
