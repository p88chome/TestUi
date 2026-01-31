import type { ThemeConfig } from '../types/theme';

export const deloitteTheme: ThemeConfig = {
    name: 'Deloitte',
    colors: {
        // Brand Primary
        brandPrimary: '#86BC25',      // Deloitte Green
        brandPrimaryDark: '#6B9C1E',

        // Brand Neutrals
        brandBlack: '#000000',
        brandCharcoal: '#2C2C2C',
        brandGray: '#666666',

        // UI Structure
        brandBorder: '#E5E5E5',
        surface: '#FFFFFF',
        surfaceMuted: '#F4F4F4',
        background: '#F4F5F7',

        // Semantic - Mapped to Brand or standard
        statusSuccess: '#86BC25',
        statusInfo: '#0076CE',
        statusWarning: '#F5A623',
        statusError: '#D0021B'
    },
    sidebar: {
        widthExpanded: '260px',
        widthCollapsed: '70px'
    },
    logo: {
        text: 'Ɐ Platform',
        dotColor: '#86BC25'
    }
};
