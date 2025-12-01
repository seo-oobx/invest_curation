import { getEvents } from '@/lib/api';
import { EventCard } from '@/components/event-card';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Terminal } from "lucide-react"
import { Event } from '@/types/event';
import { LoginButton } from '@/components/auth/login-button';

// Force dynamic rendering to ensure we get fresh data on every request
export const dynamic = 'force-dynamic';

export default async function Home() {
  let events: Event[] = [];
  let error = null;

  try {
    events = await getEvents();
  } catch (e) {
    console.error("Failed to fetch events:", e);
    error = "Backend API is not reachable. Please make sure the FastAPI server is running.";
  }

  // Sort by Hype Score descending
  const sortedEvents = Array.isArray(events)
    ? [...events].sort((a, b) => b.hype_score - a.hype_score)
    : [];

  return (
    <main className="container mx-auto py-8 px-4">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Alpha Calendar</h1>
          <p className="text-muted-foreground mt-2">
            Buy the Rumor, Sell the News.
          </p>
        </div>
        <LoginButton />
      </header>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <Terminal className="h-4 w-4" />
          <AlertTitle>Connection Error</AlertTitle>
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedEvents.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>

      {!error && sortedEvents.length === 0 && (
        <div className="text-center py-20 text-muted-foreground border rounded-lg bg-slate-50">
          <p className="text-lg font-medium">No active events found.</p>
          <p className="text-sm">Run the crawler or add events manually.</p>
        </div>
      )}
    </main>
  );
}
