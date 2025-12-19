import apiClient from './client';
import type { RunExecutionOut } from '../types';

export const getRun = async (id: string): Promise<RunExecutionOut> => {
    return await apiClient.get<RunExecutionOut>(`/runs/${id}`);
};
