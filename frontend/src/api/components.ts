import apiClient from './client';
import type { ComponentCreate, ComponentOut, ComponentUpdate } from '../types';

export const getComponents = async (): Promise<ComponentOut[]> => {
    const response = await apiClient.get<ComponentOut[]>('/components/');
    return response.data;
};

export const getComponent = async (id: string): Promise<ComponentOut> => {
    const response = await apiClient.get<ComponentOut>(`/components/${id}`);
    return response.data;
};

export const createComponent = async (data: ComponentCreate): Promise<ComponentOut> => {
    const response = await apiClient.post<ComponentOut>('/components/', data);
    return response.data;
};

export const updateComponent = async (id: string, data: ComponentUpdate): Promise<ComponentOut> => {
    const response = await apiClient.put<ComponentOut>(`/components/${id}`, data);
    return response.data;
};

export const deleteComponent = async (id: string): Promise<void> => {
    await apiClient.delete(`/components/${id}`);
};
