export type EventType = 'TYPE_A' | 'TYPE_B';
export type EventStatus = 'PENDING' | 'ACTIVE' | 'FINISHED';

export interface HypeMetric {
    id: number;
    event_id: number;
    search_volume: number;
    community_buzz: number;
    youtube_count: number;
    recorded_at: string; // Date string
    created_at: string;
}

export interface EventProxy {
    id: number;
    parent_event_id: number;
    proxy_name: string;
    detected_at: string; // ISO Datetime
}

export interface Event {
    id: number;
    title: string;
    description?: string;
    source_url?: string;
    target_date: string; // YYYY-MM-DD
    is_date_confirmed: boolean;
    event_type: EventType;
    hype_score: number;
    gpt_confidence?: number; // GPT extraction confidence (0.0-1.0)
    related_tickers: string[];
    status: EventStatus;
    created_at: string;
    updated_at: string;

    // Relationships
    hype_metrics?: HypeMetric[];
    proxies?: EventProxy[];
}
