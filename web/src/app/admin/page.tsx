"use client"

import { useEffect, useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function AdminPage() {
    const [loading, setLoading] = useState(true);
    const [isAdmin, setIsAdmin] = useState(false);
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

    useEffect(() => {
        const checkAdmin = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.push('/');
                return;
            }

            // Check Admin Role from DB
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

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return;

            const payload = {
                ...formData,
                related_tickers: formData.related_tickers.split(',').map(t => t.trim()).filter(t => t),
                is_date_confirmed: true, // Default to true for manual entry
                hype_score: 50 // Default initial score
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
                alert("Crawler started in background! Please wait about 10-20 seconds for data to update, then refresh the Home page.");
                router.refresh(); // Refresh admin page to ensure session is kept alive
            } else {
                const error = await res.json();
                alert(`Failed to trigger crawler: ${JSON.stringify(error)}`);
            }
        } catch (err) {
            console.error(err);
            alert("Error triggering crawler");
        }
    };

    if (loading) return <div className="p-8">Loading Admin Panel...</div>;
    if (!isAdmin) return null;

    return (
        <div className="container mx-auto py-8 px-4">
            <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

            <div className="grid gap-8 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Create New Event</CardTitle>
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
                                        <SelectItem value="TYPE_A">Type A (Fact)</SelectItem>
                                        <SelectItem value="TYPE_B">Type B (Hype)</SelectItem>
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
                                    placeholder="AAPL, TSLA, BTC"
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
                        <CardTitle>Crawler Status</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-muted-foreground">Crawler controls will be implemented here.</p>
                        <Button variant="outline" className="mt-4" disabled>Run Type A Crawler</Button>
                        <Button variant="outline" className="mt-2 ml-2" onClick={handleRunCrawler}>Run Type B Crawler</Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
