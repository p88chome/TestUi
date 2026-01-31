import { reactive } from 'vue';
import { useThemeStore } from './theme';

interface AuthState {
    token: string | null;
    user: any | null;
    isAuthenticated: boolean;
    isSuperuser: boolean;
    avatarUrl: string | null;
}

const state = reactive<AuthState>({
    token: localStorage.getItem('token'),
    user: null,
    isAuthenticated: !!localStorage.getItem('token'),
    isSuperuser: false,
    avatarUrl: null
});

export const useAuthStore = () => {
    const setToken = (token: string) => {
        state.token = token;
        state.isAuthenticated = true;
        localStorage.setItem('token', token);
    };

    const setUser = (user: any) => {
        state.user = user;
        state.isSuperuser = user?.is_superuser || false;

        // Auto-switch theme based on organization/tenant
        const themeStore = useThemeStore();
        if (user?.organization) {
            // Map organization to theme name (e.g. "Deloitte" -> "Deloitte")
            // Ensure schema returns organization suitable for this, or mapping logic here.
            // Schema currently returns "Deloitte" for "deloitte" tenant.
            // Theme names in theme.ts are "Deloitte", "Customer A", "Customer B".

            // Allow exact match or lowercase match
            if (user.organization === "Deloitte") {
                themeStore.switchThemeByName("Deloitte");
            } else if (user.tenant_id === "default") {
                // Keep default or explicitly set
                themeStore.switchThemeByName("Deloitte");
            }
            // For now, simple mapping logic or just rely on the store strict match if robust enough.
            // Let's rely on the store's find logic, but we might need to exact match.
            // Since backend returns "Deloitte", and theme name is "Deloitte", it fits.
            themeStore.switchThemeByName(user.organization);
        }

        // Restore avatar
        if (user?.email) {
            const savedAvatar = localStorage.getItem(`user_avatar_${user.email}`);
            if (savedAvatar) {
                state.avatarUrl = savedAvatar;
            } else {
                state.avatarUrl = null;
            }
        }
    };

    const setAvatar = (url: string) => {
        state.avatarUrl = url;
        if (state.user?.email) {
            localStorage.setItem(`user_avatar_${state.user.email}`, url);
        }
    };

    const logout = () => {
        state.token = null;
        state.user = null;
        state.isAuthenticated = false;
        state.isSuperuser = false;
        state.avatarUrl = null;
        localStorage.removeItem('token');
    };

    return {
        state,
        setToken,
        setUser,
        setAvatar,
        logout,
    };
};
