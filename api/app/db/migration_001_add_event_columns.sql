-- Migration: Add missing columns to events table
-- Run this on Supabase SQL Editor to update existing table

-- Add description column
ALTER TABLE public.events ADD COLUMN IF NOT EXISTS description text;

-- Add source_url column
ALTER TABLE public.events ADD COLUMN IF NOT EXISTS source_url text;

-- Verify columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'events'
ORDER BY ordinal_position;

