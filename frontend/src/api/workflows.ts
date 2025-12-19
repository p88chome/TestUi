import apiClient from './client';
import type { WorkflowCreate, WorkflowOut, WorkflowUpdate, RunExecutionOut } from '../types';

export const getWorkflows = async (): Promise<WorkflowOut[]> => {
    return await apiClient.get<WorkflowOut[]>('/workflows/');
};

export const getWorkflow = async (id: string): Promise<WorkflowOut> => {
    return await apiClient.get<WorkflowOut>(`/workflows/${id}`);
};

export const createWorkflow = async (data: WorkflowCreate): Promise<WorkflowOut> => {
    return await apiClient.post<WorkflowOut>('/workflows/', data);
};

export const updateWorkflow = async (id: string, data: WorkflowUpdate): Promise<WorkflowOut> => {
    return await apiClient.put<WorkflowOut>(`/workflows/${id}`, data);
};

export const deleteWorkflow = async (id: string): Promise<void> => {
    await apiClient.delete(`/workflows/${id}`);
};



export const runWorkflow = async (id: string, input_payload: Record<string, any>): Promise<RunExecutionOut> => {
    return await apiClient.post<RunExecutionOut>(`/workflows/${id}/run`, {
        workflow_id: id,
        input_payload
    });
};
