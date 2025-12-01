import { getEvent } from '@/lib/api';
import { HypeChart } from '@/components/hype-chart';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Calendar, ExternalLink, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { notFound } from 'next/navigation';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

interface PageProps {
    params: Promise<{ id: string }>;
}

export default async function EventDetailPage({ params }: PageProps) {
    const { id } = await params;
    const eventId = parseInt(id);

    if (isNaN(eventId)) {
        notFound();
    }

    let event;
    try {
        event = await getEvent(eventId);
    } catch (e) {
        console.error("Failed to fetch event:", e);
        // In a real app, we might show a specific error page
        notFound();
    }

    return (
        <main className="container mx-auto py-8 px-4 max-w-5xl">
            <div className="mb-6">
                <Link href="/">
                    <Button variant="ghost" className="pl-0 hover:pl-2 transition-all">
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Back to Dashboard
                    </Button>
                </Link>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Main Info & Chart */}
                <div className="lg:col-span-2 space-y-8">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <Badge variant={event.event_type === 'TYPE_A' ? 'default' : 'secondary'}>
                                {event.event_type === 'TYPE_A' ? 'Fact' : 'Hype'}
                            </Badge>
                            {event.is_date_confirmed && (
                                <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                                    Date Confirmed
                                </Badge>
                            )}
                        </div>
                        <h1 className="text-3xl font-bold tracking-tight mb-2">{event.title}</h1>
                        <div className="flex items-center text-muted-foreground">
                            <Calendar className="mr-2 h-4 w-4" />
                            <span className="text-lg">{event.target_date}</span>
                        </div>
                    </div>

                    <HypeChart data={event.hype_metrics || []} />

                    <Card>
                        <CardHeader>
                            <CardTitle>Event Proxies (Signals)</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {event.proxies && event.proxies.length > 0 ? (
                                <div className="space-y-4">
                                    {event.proxies.map((proxy) => (
                                        <div key={proxy.id} className="flex items-start">
                                            <div className="min-w-[100px] text-sm text-muted-foreground pt-1">
                                                {new Date(proxy.detected_at).toLocaleDateString()}
                                            </div>
                                            <div className="bg-slate-50 p-3 rounded-lg flex-1 border">
                                                <p className="text-sm font-medium">{proxy.proxy_name}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-muted-foreground text-sm">No signals detected yet.</p>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Right Column: Stats & Related Stocks */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Current Hype</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-muted-foreground">Score</span>
                                <span className="text-3xl font-bold text-blue-600">{event.hype_score}</span>
                            </div>
                            <div className="w-full bg-slate-100 rounded-full h-2.5">
                                <div
                                    className="bg-blue-600 h-2.5 rounded-full"
                                    style={{ width: `${event.hype_score}%` }}
                                ></div>
                            </div>
                            <p className="text-xs text-muted-foreground mt-4">
                                Based on search volume and community buzz analysis over the last 7 days.
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Related Stocks</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {event.related_tickers && event.related_tickers.length > 0 ? (
                                <div className="space-y-2">
                                    {event.related_tickers.map((ticker) => (
                                        <div key={ticker} className="flex items-center justify-between p-3 border rounded-lg hover:bg-slate-50 transition-colors cursor-pointer group">
                                            <div className="flex items-center">
                                                <TrendingUp className="mr-3 h-4 w-4 text-muted-foreground group-hover:text-blue-500" />
                                                <span className="font-medium">{ticker}</span>
                                            </div>
                                            <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-muted-foreground text-sm">No related stocks linked.</p>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </main>
    );
}
