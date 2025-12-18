import apiClient from './client';

export interface User {
    id: number;
    email: string;
    full_name?: string;
    is_active: boolean;
    is_superuser: boolean;
}

export interface UserCreate {
    email: string;
    password: string;
    full_name?: string;
    is_superuser?: boolean;
}

export const getUsers = async (): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/users/');
    return response as any; // apiClient interceptor returns response.data
};

export const createUser = async (data: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>('/users/', data);
    return response as any;
};

export const updateMe = async (data: Partial<UserCreate>): Promise<User> => {
    const response = await apiClient.put<User>('/users/me', data);
    return response as any;
};
