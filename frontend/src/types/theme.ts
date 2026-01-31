export interface ThemeColors {
    brandPrimary: string;
    brandPrimaryDark: string;
    brandBlack: string;
    brandCharcoal: string;
    brandGray: string;
    brandBorder: string;
    surface: string;
    surfaceMuted: string;
    background: string;

    // Semantic
    statusSuccess: string;
    statusInfo: string;
    statusWarning: string;
    statusError: string;
}

export interface SidebarConfig {
    widthExpanded: string;  // e.g. "260px"
    widthCollapsed: string; // e.g. "70px"
}

export interface LogoConfig {
    text: string;           // e.g. "Platform"
    dotColor?: string;      // e.g. "brandPrimary" (key) or hex
    fullComponent?: any;    // For complex SVGs if needed (optional)
}

export interface ThemeConfig {
    name: string;
    colors: ThemeColors;
    sidebar: SidebarConfig;
    logo: LogoConfig;
}
