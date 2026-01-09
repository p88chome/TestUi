export const components = [
    { id: 'aiocr', label: 'AIOCR', icon: 'pi pi-image', description: '文字擷取與結構化' },
    { id: 'airead', label: 'AIREAD', icon: 'pi pi-file', description: '長文閱讀與摘要' },
    { id: 'aiexcel', label: 'AI Excel', icon: 'pi pi-table', description: '表格處理與計算' },
    { id: 'aiintent', label: 'AI Intent', icon: 'pi pi-compass', description: '意圖識別路由器' },
    { id: 'aisql', label: 'AI to SQL', icon: 'pi pi-database', description: '自然語言轉查詢' },
    { id: 'aidraw', label: 'AI Drawing', icon: 'pi pi-chart-bar', description: '數據視覺化' },
    { id: 'aicomp', label: 'AI Doc Compare', icon: 'pi pi-arrow-right-arrow-left', description: '文件比對' },
];

export const flows = [
    {
        id: 'expense',
        label: '費用申報流程',
        activeComponents: ['aiocr', 'aiexcel', 'aiintent'],
        routeName: 'ExpenseHelper'
    },
    {
        id: 'legal',
        label: '合約審閱流程',
        activeComponents: ['aiocr', 'airead', 'aiintent'],
        routeName: 'ContractAssistant'
    },
    {
        id: 'audit',
        label: '稽核抽樣分析',
        activeComponents: ['aisql', 'aidraw', 'aiintent'],
        routeName: undefined
    },
    {
        id: 'compare',
        label: '公文版次比對',
        activeComponents: ['aiocr', 'aicomp', 'aiintent'],
        routeName: undefined
    }
];
