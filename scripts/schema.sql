-- Atlas schema for Supabase (mirrors delivery/database.py SQLite schema)

create table if not exists public.reactions (
    id bigserial primary key,
    message_id text not null,
    item_type text not null,
    item_id text not null,
    reaction text not null,
    reacted_at timestamptz default now()
);

create table if not exists public.preference_weights (
    id bigserial primary key,
    category text not null unique,
    weight double precision default 1.0,
    updated_at timestamptz default now()
);

create table if not exists public.digest_history (
    id bigserial primary key,
    digest_type text not null,
    payload_json jsonb not null,
    sent_at timestamptz default now()
);

-- one current digest row per type for fast dashboard reads
create table if not exists public.current_digest (
    digest_type text primary key,
    payload_json jsonb not null,
    updated_at timestamptz default now()
);

alter table public.reactions enable row level security;
alter table public.preference_weights enable row level security;
alter table public.digest_history enable row level security;
alter table public.current_digest enable row level security;

-- service_role bypasses RLS; anon is locked down by default (no policies).
create policy "service_manage_all" on public.reactions
    for all using (true) with check (true);
create policy "service_manage_all" on public.preference_weights
    for all using (true) with check (true);
create policy "service_manage_all" on public.digest_history
    for all using (true) with check (true);
create policy "service_manage_all" on public.current_digest
    for all using (true) with check (true);