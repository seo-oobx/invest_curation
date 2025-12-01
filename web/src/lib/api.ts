import { Event } from '@/types/event';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function getEvents(): Promise<Event[]> {
    const res = await fetch(`${API_BASE_URL}/events`, {
        cache: 'no-store', // Always fetch fresh data for now
    });

    if (!res.ok) {
        throw new Error('Failed to fetch events');
    }

    return res.json();
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
