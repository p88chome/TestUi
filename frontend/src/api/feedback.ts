import apiClient from './client';

export interface Feedback {
    id: number;
    user_id: number;
    content: string;
    created_at: string;
    user?: {
        email: string;
        full_name?: string;
    };
}

export const getFeedbacks = async (): Promise<Feedback[]> => {
    const response = await apiClient.get('/feedback');
    return response as any;
};

export const deleteFeedback = async (id: number): Promise<void> => {
    await apiClient.delete(`/feedback/${id}`);
};
