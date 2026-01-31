import type { ThemeConfig } from '../types/theme';

export const clientBTheme: ThemeConfig = {
    name: 'Sunrise Energy',
    colors: {
        // Brand Primary - Energetic Orange
        brandPrimary: '#FF832B',
        brandPrimaryDark: '#E06C18',

        // Brand Neutrals
        brandBlack: '#212121',
        brandCharcoal: '#424242',
        brandGray: '#757575',

        // UI Structure
        brandBorder: '#EEEEEE',
        surface: '#FFFFFF',
        surfaceMuted: '#FFF8F5', // Slight orange tint
        background: '#FAFAFA',

        // Semantic
        statusSuccess: '#4CAF50',
        statusInfo: '#2196F3',
        statusWarning: '#FF9800',
        statusError: '#F44336'
    },
    sidebar: {
        widthExpanded: '260px',
        widthCollapsed: '70px'
    },
    logo: {
        text: 'Sunrise',
        dotColor: '#FF832B'
    }
};
