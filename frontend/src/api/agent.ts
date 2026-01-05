import client from './client';

export interface AgentResponse {
    response: string;
    tool_used?: string;
    tool_result?: any;
    agent_thought?: string;
    error?: string;
}

export const runAgent = async (query: string, userId: string = "anonymous"): Promise<AgentResponse> => {
    const response = await client.post('/agent/run', { query, user_id: userId });
    return response as unknown as AgentResponse;
};
