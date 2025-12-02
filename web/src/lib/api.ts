import { Event } from '@/types/event';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function getEvents(): Promise<Event[]> {
    console.log('Fetching events from:', `${API_BASE_URL}/events`);
    try {
        const res = await fetch(`${API_BASE_URL}/events`, {
            cache: 'no-store', // Always fetch fresh data for now
        });

        if (!res.ok) {
            const errorText = await res.text();
            console.error('API Error:', res.status, errorText);
            throw new Error(`Failed to fetch events: ${res.status} ${res.statusText}`);
        }

        return res.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

export async function getEvent(id: number): Promise<Event> {
    const res = await fetch(`${API_BASE_URL}/events/${id}`, {
        cache: 'no-store',
    });

    if (!res.ok) {
        throw new Error('Failed to fetch event');
    }

    return res.json();
}
