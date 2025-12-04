-- Migration 002: Add PENDING status and gpt_confidence column
-- Run this on Supabase SQL Editor

-- Step 1: Add gpt_confidence column
ALTER TABLE public.events 
ADD COLUMN IF NOT EXISTS gpt_confidence float DEFAULT 0;

-- Step 2: Drop existing status constraint
ALTER TABLE public.events 
DROP CONSTRAINT IF EXISTS events_status_check;

-- Step 3: Add new status constraint with PENDING
ALTER TABLE public.events 
ADD CONSTRAINT events_status_check 
CHECK (status IN ('PENDING', 'ACTIVE', 'FINISHED'));

-- Step 4: Update default status to PENDING for new events
ALTER TABLE public.events 
ALTER COLUMN status SET DEFAULT 'PENDING';

-- Step 5: Create index for faster filtering by status
CREATE INDEX IF NOT EXISTS idx_events_status_pending 
ON public.events(status) 
WHERE status = 'PENDING';

-- Verify changes
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'events'
ORDER BY ordinal_position;

