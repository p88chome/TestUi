import apiClient from './client';
import type { RunExecutionOut } from '../types';

export const getRun = (id: string): Promise<RunExecutionOut> => {
    return apiClient.get(`/runs/${id}`) as Promise<RunExecutionOut>;
};
