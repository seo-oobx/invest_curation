"use client"

import { Event } from '@/types/event';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { CalendarDays, TrendingUp, Bell } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { createClient } from '@/lib/supabase/client';
import { useState } from 'react';

interface EventCardProps {
    event: Event;
}

export function EventCard({ event }: EventCardProps) {
    const [isSubscribed, setIsSubscribed] = useState(false); // In real app, fetch from API
    const supabase = createClient();

    // Calculate D-Day
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const target = new Date(event.target_date);
    target.setHours(0, 0, 0, 0);

    const diffTime = target.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    let dDay = '';
    if (diffDays > 0) {
        dDay = `D-${diffDays}`;
    } else if (diffDays === 0) {
        dDay = 'D-Day';
    } else {
        dDay = `D+${Math.abs(diffDays)}`;
    }

    const handleAlert = async (e: React.MouseEvent) => {
        e.preventDefault(); // Prevent Link navigation
        e.stopPropagation();

        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
            alert("Please sign in to set alerts!");
            return;
        }

        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/alerts/${event.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.access_token}`
                },
                body: JSON.stringify({ email: session.user.email })
            });

            if (res.ok) {
                setIsSubscribed(!isSubscribed);
                alert(isSubscribed ? "Alert removed." : "Alert set! Check your email.");
            } else {
                alert("Failed to set alert.");
            }
        } catch (err) {
            console.error(err);
            alert("Error setting alert.");
        }
    };

    return (
        <Link href={`/events/${event.id}`} className="block h-full">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full relative group">
                <Button
                    variant="ghost"
                    size="icon"
                    className={`absolute top-2 right-2 z-10 hover:bg-slate-100 ${isSubscribed ? 'text-yellow-500' : 'text-slate-400'}`}
                    onClick={handleAlert}
                >
                    <Bell className={`h-5 w-5 ${isSubscribed ? 'fill-current' : ''}`} />
                </Button>

                <CardHeader className="pb-2">
                    <div className="flex justify-between items-start pr-8">
                        <Badge variant={event.event_type === 'TYPE_A' ? 'default' : 'secondary'}>
                            {event.event_type === 'TYPE_A' ? 'Fact' : 'Hype'}
                        </Badge>
                        <span className="text-sm font-bold text-red-500">{dDay}</span>
                    </div>
                    <CardTitle className="mt-2 text-xl line-clamp-2">{event.title}</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                            <div className="flex items-center">
                                <CalendarDays className="mr-1 h-4 w-4" />
                                {event.target_date}
                            </div>
                            {event.is_date_confirmed && (
                                <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                                    Confirmed
                                </Badge>
                            )}
                        </div>

                        <div className="space-y-1">
                            <div className="flex justify-between text-sm">
                                <span className="flex items-center font-medium">
                                    <TrendingUp className="mr-1 h-4 w-4 text-blue-500" />
                                    Hype Score
                                </span>
                                <span className="font-bold">{event.hype_score}</span>
                            </div>
                            <Progress value={event.hype_score} className="h-2" />
                        </div>

                        {event.related_tickers && event.related_tickers.length > 0 && (
                            <div className="flex flex-wrap gap-1 pt-2">
                                {event.related_tickers.map((ticker) => (
                                    <Badge key={ticker} variant="outline" className="text-xs text-gray-500">
                                        {ticker}
                                    </Badge>
                                ))}
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>
        </Link>
    );
}
