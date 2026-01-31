import { defineStore } from 'pinia';
import { ref, watchEffect } from 'vue';
import type { ThemeConfig } from '../types/theme';
import { deloitteTheme } from '../themes/deloitte';
import { clientATheme } from '../themes/client_a';
import { clientBTheme } from '../themes/client_b';

export const useThemeStore = defineStore('theme', () => {
    // Current active theme - default to Deloitte
    const currentTheme = ref<ThemeConfig>(deloitteTheme);

    // Registry of available themes for testing
    const availableThemes = [deloitteTheme, clientATheme, clientBTheme];

    // Apply theme variables to root document
    const applyTheme = () => {
        const theme = currentTheme.value;
        const root = document.documentElement;

        // Colors
        root.style.setProperty('--color-brand-primary', theme.colors.brandPrimary);
        root.style.setProperty('--color-brand-primary-dark', theme.colors.brandPrimaryDark);
        root.style.setProperty('--color-black', theme.colors.brandBlack);
        root.style.setProperty('--color-charcoal', theme.colors.brandCharcoal);
        root.style.setProperty('--color-gray', theme.colors.brandGray);
        root.style.setProperty('--color-border', theme.colors.brandBorder);
        root.style.setProperty('--color-surface', theme.colors.surface);
        root.style.setProperty('--color-surface-muted', theme.colors.surfaceMuted);
        root.style.setProperty('--color-bg', theme.colors.background);

        // Semantic
        root.style.setProperty('--status-success', theme.colors.statusSuccess);
        root.style.setProperty('--status-info', theme.colors.statusInfo);
        root.style.setProperty('--status-warning', theme.colors.statusWarning);
        root.style.setProperty('--status-error', theme.colors.statusError);

        // Layout
        root.style.setProperty('--sidebar-width-expanded', theme.sidebar.widthExpanded);
        root.style.setProperty('--sidebar-width-collapsed', theme.sidebar.widthCollapsed);
    };

    // Watch for changes and apply (also runs on init)
    watchEffect(() => {
        applyTheme();
    });

    const setTheme = (theme: ThemeConfig) => {
        currentTheme.value = theme;
    };

    const switchThemeByName = (name: string) => {
        const found = availableThemes.find(t => t.name === name);
        if (found) {
            currentTheme.value = found;
        }
    };

    return {
        currentTheme,
        availableThemes,
        setTheme,
        switchThemeByName
    };
});
