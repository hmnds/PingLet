/** TypeScript types matching backend schemas */

export interface MonitoredAccount {
  id: number;
  username: string;
  x_user_id: string | null;
  digest_enabled: boolean;
  alerts_enabled: boolean;
  last_seen_post_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface MonitoredAccountCreate {
  username: string;
  digest_enabled?: boolean;
  alerts_enabled?: boolean;
}

export interface MonitoredAccountUpdate {
  digest_enabled?: boolean;
  alerts_enabled?: boolean;
  last_seen_post_id?: string | null;
}

export interface Post {
  id: number;
  x_post_id: string;
  author_id: number;
  created_at: string;
  text: string;
  url: string | null;
  stored_at: string;
}

export interface Topic {
  id: number;
  name: string;
  description: string;
  threshold: number;
  created_at: string;
  updated_at: string;
}

export interface TopicCreate {
  name: string;
  description: string;
  threshold?: number;
}

export interface AlertRule {
  id: number;
  name: string;
  enabled: boolean;
  keywords: string[] | null;
  topic_ids: number[] | null;
  allowed_author_ids: number[] | null;
  similarity_threshold: number;
  cooldown_minutes: number;
  channel: string;
  created_at: string;
  updated_at: string;
}

export interface AlertRuleCreate {
  name: string;
  enabled?: boolean;
  keywords?: string[] | null;
  topic_ids?: number[] | null;
  allowed_author_ids?: number[] | null;
  similarity_threshold?: number;
  cooldown_minutes?: number;
  channel?: string;
}

export interface AlertRuleUpdate {
  enabled?: boolean;
  keywords?: string[] | null;
  topic_ids?: number[] | null;
  allowed_author_ids?: number[] | null;
  similarity_threshold?: number;
  cooldown_minutes?: number;
  channel?: string;
}

export interface AlertLog {
  id: number;
  rule_id: number;
  post_id: number;
  trigger_type: string;
  score: number | null;
  status: string;
  sent_at: string;
}

export interface Digest {
  id: number;
  digest_date: string;
  content_markdown: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: {
    id: number;
    email: string;
    username?: string;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username: string;
}

export interface User {
  id: number;
  email: string;
  username?: string;
}


