import { reactive } from 'vue';

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
