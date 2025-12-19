import apiClient from './client';

export interface AIModel {
    id: string;
    name: string;
    deployment_name: string;
    api_version: string;
    description?: string;
    is_active: boolean;
}

export interface AIModelCreate {
    name: string;
    deployment_name: string;
    api_version: string;
    description?: string;
    is_active?: boolean;
}

export interface AIModelUpdate {
    name?: string;
    deployment_name?: string;
    api_version?: string;
    description?: string;
    is_active?: boolean;
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

export const deleteModel = async (id: string): Promise<void> => {
    await apiClient.delete(`/models/${id}`);
};
