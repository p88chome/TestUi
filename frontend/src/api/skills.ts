import client from './client';

export interface Skill {
    id: string;
    name: string;
    description: string;
    category: string;
    skill_type: string;
    configuration: Record<string, any>;
    input_schema?: Record<string, any>;
    input_output?: Record<string, any>;
    instructions?: string; // New field for progressive disclosure
    is_active: boolean;
    is_reusable: boolean;
}

export const getSkills = async () => {
    const response = await client.get<Skill[]>('/skills/');
    return response as unknown as Skill[];
};

export const refreshSkills = async () => {
    const response = await client.post('/skills/refresh');
    return response;
};

export const runSkill = async (skillName: string, input: any): Promise<any> => {
    const response = await client.post(`/skills/${skillName}/run`, { input });
    return response;
};

export const getSkillFiles = async (skillName: string) => {
    const response = await client.get<{ files: string[] }>(`/skills/${skillName}/files`);
    return (response as any).files;
};

export const getSkillFile = async (skillName: string, path: string = "skill.md") => {
    const response = await client.get<{ content: string }>(`/skills/${skillName}/file`, { params: { path } });
    return (response as any).content;
};

export const updateSkillFile = async (skillName: string, path: string, content: string) => {
    const response = await client.put(`/skills/${skillName}/file`, { content }, { params: { path } });
    return response;
};
