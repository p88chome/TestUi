import apiClient from './client';
import type { WorkflowCreate, WorkflowOut, WorkflowUpdate, RunExecutionOut } from '../types';

export const getWorkflows = (): Promise<WorkflowOut[]> => {
    return apiClient.get('/workflows') as Promise<WorkflowOut[]>;
};

export const getWorkflow = (id: string): Promise<WorkflowOut> => {
    return apiClient.get(`/workflows/${id}`) as Promise<WorkflowOut>;
};

export const createWorkflow = (data: WorkflowCreate): Promise<WorkflowOut> => {
    return apiClient.post('/workflows', data) as Promise<WorkflowOut>;
};

export const updateWorkflow = (id: string, data: WorkflowUpdate): Promise<WorkflowOut> => {
    return apiClient.put(`/workflows/${id}`, data) as Promise<WorkflowOut>;
};

export const deleteWorkflow = (id: string): Promise<void> => {
    return apiClient.delete(`/workflows/${id}`) as Promise<void>;
};



export const runWorkflow = (id: string, payload: any): Promise<RunExecutionOut> => {
    return apiClient.post(`/workflows/${id}/run`, payload) as Promise<RunExecutionOut>;
};
