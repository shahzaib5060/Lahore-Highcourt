-- Punjab Lawyers Dashboard: table for Supabase.
-- Run this once in Supabase: SQL Editor -> New query -> paste -> Run.
-- Then load the data: Table Editor -> lawyers -> Insert -> Import data from CSV -> lawyers.csv

create table if not exists public.lawyers (
  id              bigint generated always as identity primary key,
  name            text not null,
  parentage       text,
  station         text not null,
  vote_no         integer,
  life_member     boolean default false,
  membership_no   integer,
  gender          text check (gender in ('Male', 'Female')),
  chambers        text check (chambers in ('Local courts', 'Lahore', 'Not listed')),
  office_address  text,
  photo_sheet     integer,          -- which sheet_N.jpg holds the photo (blank if none)
  photo_pos       integer,          -- position on that sheet (40 photos per row)
  photo_url       text,             -- optional: a direct image link per lawyer, used instead of the sheet
  created_at      timestamptz default now()
);

create index if not exists lawyers_station_idx on public.lawyers (station);
create index if not exists lawyers_name_idx    on public.lawyers (name);

-- Keep the table private. The Streamlit app reads it with the service_role key,
-- which stays on the server in Streamlit's secrets and never reaches visitors.
alter table public.lawyers enable row level security;
