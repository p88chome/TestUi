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
            // Workflows & Components
            {
                path: 'workflows',
                name: 'Workflows',
                component: () => import('../pages/WorkflowsPage.vue')
            },
            {
                path: 'components',
                name: 'Components',
                component: () => import('../pages/ComponentsPage.vue')
            },
            {
                path: 'runs/:id',
                name: 'RunDetail',
                component: () => import('../pages/RunDetailPage.vue')
            },
            {
                path: 'capability-map',
                name: 'CapabilityMap',
                component: () => import('../pages/CapabilityMap.vue')
            },


            // Enterprise Apps
            { path: 'apps/meeting-ai', name: 'MeetingMinutes', component: () => import('../pages/MeetingMinutesPage.vue'), meta: { requiresPro: true } },
            { path: 'apps/policy-analysis', name: 'PolicyAnalysis', component: () => import('../pages/PolicyAnalysisPage.vue'), meta: { requiresPro: true } },
            { path: 'apps/ppt-generator', name: 'PPTGenerator', component: () => import('../pages/PPTGeneratorPage.vue'), meta: { requiresPro: true } },
            { path: 'apps/contracts', name: 'ContractAssistant', component: ChatbotPage, meta: { requiresPro: true } },
            { path: 'apps/expenses', name: 'ExpenseHelper', component: ChatbotPage, meta: { requiresPro: true } },

            // Legacy routes (redirect to new paths)
            { path: 'meeting-minutes', redirect: '/apps/meeting-ai' },
            { path: 'policy-analysis', redirect: '/apps/policy-analysis' },

            // Dashboard
            { path: 'dashboard', name: 'Dashboard', component: () => import('../pages/DashboardPage.vue') },

            // Operations
            { path: 'monitoring', name: 'Monitoring', component: () => import('../pages/ComingSoonPage.vue') },
            { path: 'models', name: 'Models', component: () => import('../pages/ModelsPage.vue') },
            { path: 'skills', name: 'Skills', component: () => import('../pages/SkillsPage.vue') },
            { path: 'news', name: 'News', component: () => import('../pages/NewsPage.vue') },
            { path: 'settings', name: 'Settings', component: () => import('../pages/ComingSoonPage.vue') },

            // Playbooks
            { path: 'templates', name: 'Templates', component: () => import('../pages/ComingSoonPage.vue') },
            { path: 'domains', name: 'Domains', component: () => import('../pages/ComingSoonPage.vue') },


            // Admin
            {
                path: 'feedback',
                name: 'Feedback',
                component: () => import('../pages/FeedbackPage.vue'),
                meta: { adminOnly: true }
            },
            {
                path: 'users',
                name: 'Users',
                component: () => import('../pages/UsersPage.vue'),
                meta: { adminOnly: true }
            },

            // System Info
            {
                path: 'about',
                name: 'About',
                component: () => import('../pages/AboutPage.vue')
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

    // 1. If going to login while authenticated, redirect to dashboard
    if (isAuthenticated && to.name === 'Login') {
        next('/dashboard');
        return;
    }

    // 2. Check authentication requirement
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const adminOnly = to.matched.some(record => record.meta.adminOnly);
    const requiresPro = to.matched.some(record => record.meta.requiresPro);

    if ((requiresAuth || adminOnly) && !isAuthenticated) {
        next('/login');
        return;
    }

    // 3. Check Plan requirement (Pro/Enterprise)
    if (requiresPro && isAuthenticated) {
        try {
            const { useAuthStore } = await import('../stores/auth');
            const auth = useAuthStore();

            // If user is loaded and is on Starter plan, block access
            if (auth.state.user && auth.state.user.plan_name === 'Starter') {
                next('/profile');
                return;
            }
        } catch (e) {
            console.error("Auth store access error in router", e);
        }
    }

    // 4. Proceed to route
    next();
});

export default router;
