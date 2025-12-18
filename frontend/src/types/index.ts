export type EndpointType = 'api' | 'function' | 'model';
export type RunStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface ComponentBase {
    name: string;
    description: string;
    input_schema: Record<string, any>;
    output_schema: Record<string, any>;
    tags: string[];
    endpoint_type: EndpointType;
    active: boolean;
}

export interface ComponentCreate extends ComponentBase { }

export interface ComponentUpdate {
    name?: string;
    description?: string;
    input_schema?: Record<string, any>;
    output_schema?: Record<string, any>;
    tags?: string[];
    endpoint_type?: EndpointType;
    active?: boolean;
}

export interface ComponentOut extends ComponentBase {
    id: string; // UUID
}

export interface WorkflowStepConfig {
    step_id: number;
    component_id: string; // UUID
    config: Record<string, any>;
    input_mapping: Record<string, any>;
}

export interface WorkflowBase {
    name: string;
    description: string;
    steps: WorkflowStepConfig[];
}

export interface WorkflowCreate extends WorkflowBase { }

export interface WorkflowUpdate {
    name?: string;
    description?: string;
    steps?: WorkflowStepConfig[];
}

export interface WorkflowOut extends WorkflowBase {
    id: string; // UUID
}

export interface RunExecutionBase {
    workflow_id: string; // UUID
    input_payload: Record<string, any>;
}

export interface RunExecutionCreate extends RunExecutionBase { }

export interface RunExecutionOut extends RunExecutionBase {
    id: string; // UUID
    status: RunStatus;
    output_payload?: Record<string, any>;
    log: Record<string, any>[];
    started_at: string; // ISO 8601
    finished_at?: string; // ISO 8601
}
