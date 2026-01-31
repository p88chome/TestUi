import type { ThemeConfig } from '../types/theme';

export const clientATheme: ThemeConfig = {
    name: 'TechCorp Solutions',
    colors: {
        // Brand Primary - Deep Tech Blue
        brandPrimary: '#0F62FE',
        brandPrimaryDark: '#0043CE',

        // Brand Neutrals
        brandBlack: '#161616',  // Darker gray-black
        brandCharcoal: '#393939',
        brandGray: '#6F6F6F',

        // UI Structure
        brandBorder: '#E0E0E0',
        surface: '#FFFFFF',
        surfaceMuted: '#F4F7FB', // Slight blue tint
        background: '#F2F4F8',

        // Semantic
        statusSuccess: '#24A148',
        statusInfo: '#0043CE',
        statusWarning: '#F1C21B',
        statusError: '#DA1E28'
    },
    sidebar: {
        widthExpanded: '260px',
        widthCollapsed: '70px'
    },
    logo: {
        text: 'TechCorp',
        dotColor: '#0F62FE'
    }
};
