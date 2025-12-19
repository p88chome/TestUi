import apiClient from './client';
import type { ComponentCreate, ComponentOut, ComponentUpdate } from '../types';

export const getComponents = (): Promise<ComponentOut[]> => {
    return apiClient.get('/components') as Promise<ComponentOut[]>;
};

export const getComponent = (id: string): Promise<ComponentOut> => {
    return apiClient.get(`/components/${id}`) as Promise<ComponentOut>;
};

export const createComponent = (data: ComponentCreate): Promise<ComponentOut> => {
    return apiClient.post('/components', data) as Promise<ComponentOut>;
};

export const updateComponent = (id: string, data: ComponentUpdate): Promise<ComponentOut> => {
    return apiClient.put(`/components/${id}`, data) as Promise<ComponentOut>;
};

export const deleteComponent = async (id: string): Promise<void> => {
    await apiClient.delete(`/components/${id}`);
};
