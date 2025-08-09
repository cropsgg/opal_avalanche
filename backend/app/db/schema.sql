-- Users and Firms
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  clerk_id text unique not null,
  email text not null,
  role text default 'lawyer' check (role in ('lawyer', 'admin', 'paralegal', 'client')),
  wallet_address text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists ix_users_clerk_id on users(clerk_id);

create table if not exists firms (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  gstin text,
  pan text,
  address text,
  city text,
  state text,
  pincode text,
  phone text,
  email text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists user_firms (
  user_id uuid references users(id) on delete cascade,
  firm_id uuid references firms(id) on delete cascade,
  role text default 'member' check (role in ('owner', 'partner', 'associate', 'member', 'intern')),
  joined_at timestamptz default now(),
  primary key (user_id, firm_id)
);

-- Updated_at trigger function
create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language 'plpgsql';

-- Triggers for updated_at
create trigger update_users_updated_at before update on users
  for each row execute function update_updated_at_column();

create trigger update_firms_updated_at before update on firms
  for each row execute function update_updated_at_column();

-- Authorities
create table if not exists authorities (
  id uuid primary key default gen_random_uuid(),
  court text not null,
  title text not null,
  neutral_cite text,
  reporter_cite text,
  date date,
  bench text,
  url text,
  metadata_json jsonb default '{}',
  storage_path text not null,
  hash_keccak256 text not null,
  created_at timestamptz default now()
);

-- Chunks
create table if not exists chunks (
  id uuid primary key default gen_random_uuid(),
  authority_id uuid references authorities(id) on delete cascade,
  para_from int,
  para_to int,
  text text not null,
  tokens int,
  vector_id text,
  statute_tags text[],
  has_citation boolean default false
);

-- FTS (keyword search)
alter table authorities add column if not exists fts_doc tsvector;
create index if not exists idx_authorities_fts on authorities using gin (fts_doc);
create index if not exists idx_chunks_authority on chunks(authority_id);
create index if not exists idx_chunks_statutes on chunks using gin(statute_tags);

-- Trigram
create extension if not exists pg_trgm;
create index if not exists idx_authorities_neutral_trgm on authorities using gin (neutral_cite gin_trgm_ops);
create index if not exists idx_authorities_reporter_trgm on authorities using gin (reporter_cite gin_trgm_ops);

-- Matters / Documents
create table if not exists matters (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  title text not null,
  language text default 'en',
  created_at timestamptz default now()
);

create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid references matters(id) on delete cascade,
  storage_path text not null,
  filetype text not null,
  size bigint,
  uploaded_by uuid,
  ocr_status text default 'pending',
  checksum_sha256 text,
  created_at timestamptz default now()
);

-- Runs & votes
create table if not exists queries (
  id uuid primary key default gen_random_uuid(),
  matter_id uuid references matters(id) on delete cascade,
  message text not null,
  mode text not null check (mode in ('general','precedent','limitation','draft')),
  filters_json jsonb default '{}',
  created_at timestamptz default now()
);

create table if not exists runs (
  id uuid primary key default gen_random_uuid(),
  query_id uuid references queries(id) on delete cascade,
  answer_text text,
  confidence numeric,
  retrieval_set_json jsonb default '[]',
  created_at timestamptz default now()
);

create table if not exists agent_votes (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references runs(id) on delete cascade,
  agent text not null,
  decision_json jsonb not null,
  confidence numeric not null,
  aligned boolean,
  weights_before jsonb,
  weights_after jsonb
);

-- On-chain proofs
create table if not exists onchain_proofs (
  run_id uuid primary key references runs(id) on delete cascade,
  merkle_root text not null,
  tx_hash text not null,
  network text not null,
  block_number bigint,
  created_at timestamptz default now()
);

-- Billing
create table if not exists billing_accounts (
  user_id uuid primary key references users(id) on delete cascade,
  plan text default 'starter',
  credits_balance int default 0,
  renews_at date
);

create table if not exists billing_ledger (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  run_id uuid,
  credits_delta int not null,
  cost_usd numeric,
  created_at timestamptz default now()
);

-- FTS population helper (example)
-- update authorities set fts_doc =
--   setweight(to_tsvector('simple', coalesce(title,'')), 'A') ||
--   setweight(to_tsvector('english', coalesce(metadata_json->>'headnote','')), 'B');


