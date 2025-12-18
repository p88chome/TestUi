import apiClient from './client';
import type { WorkflowCreate, WorkflowOut, WorkflowUpdate, RunExecutionOut } from '../types';

export const getWorkflows = async (): Promise<WorkflowOut[]> => {
    const response = await apiClient.get<WorkflowOut[]>('/workflows/');
    return response.data;
};

export const getWorkflow = async (id: string): Promise<WorkflowOut> => {
    const response = await apiClient.get<WorkflowOut>(`/workflows/${id}`);
    return response.data;
};

export const createWorkflow = async (data: WorkflowCreate): Promise<WorkflowOut> => {
    const response = await apiClient.post<WorkflowOut>('/workflows/', data);
    return response.data;
};

export const updateWorkflow = async (id: string, data: WorkflowUpdate): Promise<WorkflowOut> => {
    const response = await apiClient.put<WorkflowOut>(`/workflows/${id}`, data);
    return response.data;
};

export const deleteWorkflow = async (id: string): Promise<void> => {
    await apiClient.delete(`/workflows/${id}`);
};

export const runWorkflow = async (id: string, input_payload: Record<string, any>): Promise<RunExecutionOut> => {
    const response = await apiClient.post<RunExecutionOut>(`/workflows/${id}/run`, {
        workflow_id: id,
        input_payload
    });
    return response.data;
};
