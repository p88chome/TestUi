import apiClient from './client';

export type LLMProvider = 'azure' | 'google' | 'openai';

export interface AIModel {
    id: string;
    name: string;
    provider: LLMProvider;
    model_name: string | null;
    deployment_name: string | null;
    api_version: string | null;
    description?: string;
    is_active: boolean;
    is_reasoning_model: boolean;
}

export interface AIModelCreate {
    name: string;
    provider: LLMProvider;
    model_name?: string | null;
    deployment_name?: string | null;
    api_version?: string | null;
    description?: string;
    is_active?: boolean;
    is_reasoning_model?: boolean;
}

export interface AIModelUpdate {
    name?: string;
    provider?: LLMProvider;
    model_name?: string | null;
    deployment_name?: string | null;
    api_version?: string | null;
    description?: string;
    is_active?: boolean;
    is_reasoning_model?: boolean;
}

export const getModels = (): Promise<AIModel[]> => {
    return apiClient.get('/models') as Promise<AIModel[]>;
};

export const createModel = (data: AIModelCreate): Promise<AIModel> => {
    return apiClient.post('/models', data) as Promise<AIModel>;
};

export const updateModel = (id: string, data: AIModelUpdate): Promise<AIModel> => {
    return apiClient.put(`/models/${id}`, data) as Promise<AIModel>;
};

export const setActiveModel = (id: string): Promise<AIModel> => {
    return apiClient.post(`/models/${id}/set-active`, {}) as Promise<AIModel>;
};

export const deleteModel = async (id: string): Promise<void> => {
    await apiClient.delete(`/models/${id}`);
};
