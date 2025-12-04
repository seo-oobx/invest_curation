"use client"

import { useEffect, useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

type EventStatus = 'PENDING' | 'ACTIVE' | 'FINISHED';
type FilterTab = 'PENDING' | 'ACTIVE' | 'ALL';

interface Event {
    id: string;
    title: string;
    description?: string;
    target_date: string;
    event_type: string;
    hype_score: number;
    gpt_confidence?: number;
    status: EventStatus;
    related_tickers?: string[];
    source_url?: string;
    created_at: string;
}

export default function AdminPage() {
    const [loading, setLoading] = useState(true);
    const [isAdmin, setIsAdmin] = useState(false);
    const [activeTab, setActiveTab] = useState<FilterTab>('PENDING');
    const router = useRouter();
    const supabase = createClient();

    // Form State
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        event_type: 'TYPE_A',
        target_date: '',
        related_tickers: '',
        source_url: ''
    });

    // Events State
    const [events, setEvents] = useState<Event[]>([]);
    const [pendingCount, setPendingCount] = useState(0);

    useEffect(() => {
        const checkAdmin = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.push('/');
                return;
            }

            const { data: userProfile, error } = await supabase
                .from('users')
                .select('role')
                .eq('id', session.user.id)
                .single();

            if (error || userProfile?.role !== 'ADMIN') {
                console.error("Admin check failed:", error);
                alert("Access Denied: You are not an admin.");
                router.push('/');
                return;
            }

            setIsAdmin(true);
            setLoading(false);
        };

        checkAdmin();
    }, [router, supabase]);

    const fetchEvents = async () => {
        let query = supabase
            .from('events')
            .select('*')
            .order('created_at', { ascending: false });

        if (activeTab !== 'ALL') {
            query = query.eq('status', activeTab);
        }

        const { data, error } = await query;

        if (data) setEvents(data);
        if (error) console.error("Error fetching events:", error);

        // Get pending count
        const { count } = await supabase
            .from('events')
            .select('*', { count: 'exact', head: true })
            .eq('status', 'PENDING');

        setPendingCount(count || 0);
    };

    useEffect(() => {
        if (isAdmin) {
            fetchEvents();
        }
    }, [isAdmin, activeTab]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return;

            const payload = {
                ...formData,
                related_tickers: formData.related_tickers.split(',').map(t => t.trim()).filter(t => t),
                is_date_confirmed: true,
                hype_score: 50,
                status: 'ACTIVE', // Manual events are auto-approved
                gpt_confidence: 1.0
            };

            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/events`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.access_token}`
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                alert("Event created successfully!");
                setFormData({
                    title: '',
                    description: '',
                    event_type: 'TYPE_A',
                    target_date: '',
                    related_tickers: '',
                    source_url: ''
                });
                fetchEvents();
            } else {
                const error = await res.json();
                alert(`Failed to create event: ${JSON.stringify(error)}`);
            }
        } catch (err) {
            console.error(err);
            alert("Error creating event");
        }
    };

    const handleRunCrawler = async () => {
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return;

            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/admin/crawl/manual`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            });

            if (res.ok) {
                alert("Crawler started! This may take a few minutes. Refresh to see new events.");
            } else {
                const error = await res.json();
                alert(`Failed to trigger crawler: ${JSON.stringify(error)}`);
            }
        } catch (err) {
            console.error(err);
            alert("Error triggering crawler");
        }
    };

    const approveEvent = async (id: string) => {
        const { error } = await supabase
            .from('events')
            .update({ status: 'ACTIVE' })
            .eq('id', id);

        if (!error) {
            fetchEvents();
        } else {
            alert("Failed to approve event");
        }
    };

    const rejectEvent = async (id: string) => {
        const { error } = await supabase
            .from('events')
            .delete()
            .eq('id', id);

        if (!error) {
            fetchEvents();
        } else {
            alert("Failed to reject event");
        }
    };

    const toggleStatus = async (id: string, currentStatus: EventStatus) => {
        const newStatus = currentStatus === 'ACTIVE' ? 'FINISHED' : 'ACTIVE';
        const { error } = await supabase
            .from('events')
            .update({ status: newStatus })
            .eq('id', id);

        if (!error) {
            fetchEvents();
        } else {
            alert("Failed to update status");
        }
    };

    const getStatusBadge = (status: EventStatus) => {
        switch (status) {
            case 'PENDING':
                return <Badge variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-300">Pending Review</Badge>;
            case 'ACTIVE':
                return <Badge variant="outline" className="bg-green-100 text-green-800 border-green-300">Active</Badge>;
            case 'FINISHED':
                return <Badge variant="outline" className="bg-gray-100 text-gray-800 border-gray-300">Finished</Badge>;
        }
    };

    const getConfidenceBadge = (confidence?: number) => {
        if (confidence === undefined) return null;
        const percent = Math.round(confidence * 100);
        if (percent >= 80) {
            return <Badge className="bg-blue-500">GPT: {percent}%</Badge>;
        } else if (percent >= 50) {
            return <Badge variant="secondary">GPT: {percent}%</Badge>;
        }
        return <Badge variant="outline">GPT: {percent}%</Badge>;
    };

    if (loading) return <div className="p-8">Loading Admin Panel...</div>;
    if (!isAdmin) return null;

    return (
        <div className="container mx-auto py-8 px-4">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold">Admin Dashboard</h1>
                {pendingCount > 0 && (
                    <Badge variant="destructive" className="text-lg px-4 py-2">
                        {pendingCount} Pending Reviews
                    </Badge>
                )}
            </div>

            {/* Pending Review Section - Prominent when there are pending items */}
            {pendingCount > 0 && activeTab !== 'PENDING' && (
                <Card className="mb-8 border-yellow-400 bg-yellow-50">
                    <CardHeader>
                        <CardTitle className="text-yellow-800">🔔 Events Awaiting Review</CardTitle>
                        <CardDescription>
                            {pendingCount} events need your approval before appearing on the main page.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button onClick={() => setActiveTab('PENDING')} variant="outline">
                            Review Pending Events →
                        </Button>
                    </CardContent>
                </Card>
            )}

            <div className="grid gap-8 md:grid-cols-2 mb-8">
                <Card>
                    <CardHeader>
                        <CardTitle>Create New Event</CardTitle>
                        <CardDescription>Manually add events (auto-approved)</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="title">Event Title</Label>
                                <Input
                                    id="title"
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="type">Event Type</Label>
                                <Select
                                    value={formData.event_type}
                                    onValueChange={(val) => setFormData({ ...formData, event_type: val })}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select type" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="TYPE_A">Type A (Big Event)</SelectItem>
                                        <SelectItem value="TYPE_B">Type B (Wave Event)</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="date">Target Date</Label>
                                <Input
                                    id="date"
                                    type="date"
                                    value={formData.target_date}
                                    onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="tickers">Related Tickers (comma separated)</Label>
                                <Input
                                    id="tickers"
                                    placeholder="AAPL, TSLA, 삼성전자"
                                    value={formData.related_tickers}
                                    onChange={(e) => setFormData({ ...formData, related_tickers: e.target.value })}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="desc">Description</Label>
                                <Textarea
                                    id="desc"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                />
                            </div>

                            <Button type="submit" className="w-full">Create Event</Button>
                        </form>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Crawler Control</CardTitle>
                        <CardDescription>Automatic daily run at 00:00 UTC</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-sm text-muted-foreground">
                            The crawler discovers new events from news sources and calculates hype scores from Reddit and Korean news.
                        </p>
                        <div className="space-y-2">
                            <p className="text-sm font-medium">Pipeline:</p>
                            <ol className="text-xs text-muted-foreground list-decimal list-inside space-y-1">
                                <li>Crawl news for 60 target tickers</li>
                                <li>Extract events using GPT (2-6 month window)</li>
                                <li>Calculate multi-source Hype Score</li>
                                <li>Auto-publish if score ≥ 50 & confidence ≥ 0.7</li>
                            </ol>
                        </div>
                        <Button variant="outline" className="w-full" onClick={handleRunCrawler}>
                            🚀 Run Crawler Now
                        </Button>
                    </CardContent>
                </Card>
            </div>

            {/* Event Management with Tabs */}
            <Card>
                <CardHeader>
                    <CardTitle>Event Management</CardTitle>
                    <div className="flex gap-2 mt-4">
                        <Button
                            variant={activeTab === 'PENDING' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setActiveTab('PENDING')}
                        >
                            Pending {pendingCount > 0 && `(${pendingCount})`}
                        </Button>
                        <Button
                            variant={activeTab === 'ACTIVE' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setActiveTab('ACTIVE')}
                        >
                            Active
                        </Button>
                        <Button
                            variant={activeTab === 'ALL' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setActiveTab('ALL')}
                        >
                            All
                        </Button>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="rounded-md border overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-muted/50">
                                <tr>
                                    <th className="p-4 font-medium">Title</th>
                                    <th className="p-4 font-medium">Date</th>
                                    <th className="p-4 font-medium">Type</th>
                                    <th className="p-4 font-medium">Hype</th>
                                    <th className="p-4 font-medium">Confidence</th>
                                    <th className="p-4 font-medium">Status</th>
                                    <th className="p-4 font-medium">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {events.map((event) => (
                                    <tr key={event.id} className="border-t hover:bg-muted/30">
                                        <td className="p-4">
                                            <div className="max-w-xs">
                                                <p className="font-medium truncate" title={event.title}>
                                                    {event.title}
                                                </p>
                                                {event.related_tickers && event.related_tickers.length > 0 && (
                                                    <p className="text-xs text-muted-foreground">
                                                        {event.related_tickers.join(', ')}
                                                    </p>
                                                )}
                                            </div>
                                        </td>
                                        <td className="p-4">{event.target_date}</td>
                                        <td className="p-4">
                                            <Badge variant="outline">
                                                {event.event_type === 'TYPE_A' ? 'Big Event' : 'Wave'}
                                            </Badge>
                                        </td>
                                        <td className="p-4">
                                            <span className={`font-bold ${
                                                event.hype_score >= 70 ? 'text-red-600' :
                                                event.hype_score >= 50 ? 'text-orange-500' :
                                                event.hype_score >= 30 ? 'text-yellow-600' :
                                                'text-gray-500'
                                            }`}>
                                                {event.hype_score}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            {getConfidenceBadge(event.gpt_confidence)}
                                        </td>
                                        <td className="p-4">
                                            {getStatusBadge(event.status)}
                                        </td>
                                        <td className="p-4">
                                            <div className="flex gap-2">
                                                {event.status === 'PENDING' ? (
                                                    <>
                                                        <Button
                                                            size="sm"
                                                            className="bg-green-600 hover:bg-green-700"
                                                            onClick={() => approveEvent(event.id)}
                                                        >
                                                            ✓ Approve
                                                        </Button>
                                                        <Button
                                                            size="sm"
                                                            variant="destructive"
                                                            onClick={() => rejectEvent(event.id)}
                                                        >
                                                            ✗ Reject
                                                        </Button>
                                                    </>
                                                ) : (
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => toggleStatus(event.id, event.status)}
                                                    >
                                                        {event.status === 'ACTIVE' ? 'Finish' : 'Reactivate'}
                                                    </Button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                                {events.length === 0 && (
                                    <tr>
                                        <td colSpan={7} className="p-8 text-center text-muted-foreground">
                                            No events found for this filter.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
