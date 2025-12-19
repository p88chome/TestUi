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

export const getModels = async (): Promise<AIModel[]> => {
    return await apiClient.get<AIModel[]>('/models/');
};

export const createModel = async (data: AIModelCreate): Promise<AIModel> => {
    return await apiClient.post<AIModel>('/models/', data);
};

export const updateModel = async (id: string, data: AIModelUpdate): Promise<AIModel> => {
    return await apiClient.put<AIModel>(`/models/${id}`, data);
};

export const deleteModel = async (id: string): Promise<void> => {
    await apiClient.delete(`/models/${id}`);
};
