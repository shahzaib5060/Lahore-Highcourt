-- Punjab Lawyers Dashboard: Supabase setup.
-- Run once in Supabase: SQL Editor -> New query -> paste all of this -> Run.

create table if not exists public.lawyers (
  id              bigint generated always as identity primary key,
  name            text not null,
  parentage       text,
  station         text not null,
  vote_no         integer,
  life_member     boolean not null default false,
  membership_no   integer,
  gender          text,
  chambers        text,
  office_address  text,
  photo_sheet     integer not null default -1,   -- which sheet_N.jpg holds the photo; -1 = no photo
  photo_pos       integer not null default -1,   -- position on that sheet (40 photos per row)
  photo_url       text,                          -- optional: a direct image link, used instead of the sheet
  created_at      timestamptz not null default now()
);

create index if not exists lawyers_station_idx on public.lawyers (station);
create index if not exists lawyers_name_idx    on public.lawyers (name);

-- Only people who have signed in can read the table. Nobody can change it
-- through the app; edits are made by you in the Supabase Table Editor.
alter table public.lawyers enable row level security;

drop policy if exists "Signed-in users can read lawyers" on public.lawyers;
create policy "Signed-in users can read lawyers"
  on public.lawyers for select
  to authenticated
  using (true);
