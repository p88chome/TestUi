import client from './client';

export interface AgentResponse {
    response: string;
    tool_used?: string;
    tool_result?: any;
    agent_thought?: string;
    error?: string;
    session_id?: string;
    assistant_id?: string;
}

export const runAgent = async (query: string, sessionId?: string, assistantId?: string): Promise<AgentResponse> => {
    const response = await client.post('/agent/run', {
        query,
        session_id: sessionId,
        assistant_id: assistantId
    });
    return response as unknown as AgentResponse;
};
