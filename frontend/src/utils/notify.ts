import type { useToast } from 'primevue/usetoast';

type Toast = ReturnType<typeof useToast>;

const STATUS_MESSAGES: Record<number, string> = {
    400: '請求格式不正確',
    401: '登入已過期，請重新登入',
    403: '沒有權限執行此動作',
    404: '找不到資源',
    409: '資料衝突，請重新整理後再試',
    422: '資料驗證失敗，請檢查輸入',
    429: '請求過於頻繁，請稍後再試',
    500: '伺服器錯誤，請稍後再試',
    502: '後端連線失敗',
    503: '服務暫時無法使用',
};

export const friendlyError = (err: any, fallback = '操作失敗，請稍後再試'): string => {
    const status = err?.response?.status;
    if (status && STATUS_MESSAGES[status]) return STATUS_MESSAGES[status];
    return fallback;
};

export const notifyError = (
    toast: Toast,
    err: any,
    summary = '錯誤',
    fallback?: string
) => {
    toast.add({
        severity: 'error',
        summary,
        detail: friendlyError(err, fallback),
        life: 4000,
    });
};

export const notifySuccess = (toast: Toast, detail: string, summary = '成功') => {
    toast.add({ severity: 'success', summary, detail, life: 3000 });
};

export const notifyInfo = (toast: Toast, detail: string, summary = '提示') => {
    toast.add({ severity: 'info', summary, detail, life: 3000 });
};
