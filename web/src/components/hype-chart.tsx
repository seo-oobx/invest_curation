"use client"

import { HypeMetric } from '@/types/event';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Legend } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface HypeChartProps {
    data: HypeMetric[];
}

export function HypeChart({ data }: HypeChartProps) {
    // Format data for chart
    const chartData = data.map(metric => ({
        date: new Date(metric.recorded_at).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
        search: metric.search_volume,
        buzz: metric.community_buzz,
        youtube: metric.youtube_count
    })).reverse(); // Assuming API returns newest first, we want oldest first for chart

    if (data.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Hype Trend</CardTitle>
                </CardHeader>
                <CardContent className="h-[300px] flex items-center justify-center text-muted-foreground">
                    No data available yet.
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Hype Trend</CardTitle>
            </CardHeader>
            <CardContent className="pl-0">
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis
                                dataKey="date"
                                tickLine={false}
                                axisLine={false}
                                tickMargin={8}
                                tick={{ fontSize: 12 }}
                            />
                            <YAxis
                                tickLine={false}
                                axisLine={false}
                                tickMargin={8}
                                tick={{ fontSize: 12 }}
                            />
                            <Tooltip
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="search"
                                name="Search Volume"
                                stroke="#2563eb"
                                strokeWidth={2}
                                dot={false}
                                activeDot={{ r: 6 }}
                            />
                            <Line
                                type="monotone"
                                dataKey="buzz"
                                name="Community Buzz"
                                stroke="#e11d48"
                                strokeWidth={2}
                                dot={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    )
}
