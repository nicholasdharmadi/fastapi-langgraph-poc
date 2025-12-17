export interface Lead {
  id: number;
  name: string;
  phone: string;
  email?: string;
  company?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface Workflow {
  id: number;
  name: string;
  description?: string;
  config: any; // Stores nodes and edges
  is_template: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Campaign {
  id: number;
  name: string;
  description?: string;
  agent_type: "sms" | "voice" | "both";
  status:
    | "draft"
    | "pending"
    | "processing"
    | "completed"
    | "failed"
    | "paused";
  sms_system_prompt?: string;
  sms_temperature: number;
  workflow_config?: any;
  stats?: any;
  campaign_leads?: CampaignLead[];
  created_at: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
}

export interface CampaignLead {
  id: number;
  campaign_id: number;
  lead_id: number;
  status: string;
  sms_sent: boolean;
  sms_message?: string;
  sms_response?: string;
  voice_call_made: boolean;
  trace_id?: string;
  error_message?: string;
  created_at: string;
  updated_at?: string;
  processed_at?: string;
  lead?: Lead;
}

export interface ProcessingLog {
  id: number;
  campaign_lead_id: number;
  level: string;
  node_name?: string;
  message: string;
  metadata?: any;
  created_at: string;
}

export interface DashboardStats {
  campaigns: {
    total: number;
    active: number;
    completed: number;
  };
  leads: {
    total: number;
    in_campaigns: number;
    sms_sent: number;
    completed: number;
    failed: number;
    success_rate: number;
  };
}

export interface WorkingHoursConfig {
  enforce_working_hours: boolean;
  working_hours_start: number;
  working_hours_end: number;
  allow_weekend_sending: boolean;
}

export interface WorkingHoursSettings extends WorkingHoursConfig {
  current_hour: number;
  current_day: string;
  is_currently_allowed: boolean;
}
