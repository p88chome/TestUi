import apiClient from './client';
import type { ComponentCreate, ComponentOut, ComponentUpdate } from '../types';

export const getComponents = async (): Promise<ComponentOut[]> => {
    return await apiClient.get<ComponentOut[]>('/components/');
};

export const getComponent = async (id: string): Promise<ComponentOut> => {
    return await apiClient.get<ComponentOut>(`/components/${id}`);
};

export const createComponent = async (data: ComponentCreate): Promise<ComponentOut> => {
    return await apiClient.post<ComponentOut>('/components/', data);
};

export const updateComponent = async (id: string, data: ComponentUpdate): Promise<ComponentOut> => {
    return await apiClient.put<ComponentOut>(`/components/${id}`, data);
};

export const deleteComponent = async (id: string): Promise<void> => {
    await apiClient.delete(`/components/${id}`);
};
