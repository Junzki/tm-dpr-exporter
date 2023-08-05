create table if not exists district_perf
(
    id                   serial primary key,
    report_year          integer              not null,
    report_month         integer              not null,
    district             character varying(8) not null,
    division             character varying(8) not null,
    area                 character varying(8) not null,
    club                 integer              not null,
    club_name            character varying    not null,
    new_members          integer              not null default 0,
    late_renewals        integer              not null default 0,
    oct_renewals         integer              not null default 0,
    apr_renewals         integer              not null default 0,
    total_renewals       integer              not null default 0,
    total_chart          integer              not null default 0,
    total_to_date        integer              not null default 0,
    distinguished_status character varying(8),
    charter_suspend_date character varying             default null,
    charter_date         date                          default null,
    suspend_date         date                          default null,
    updated_at           timestamptz          not null default current_timestamp,

    constraint "district_pref_uniq" unique (report_year, report_month, club)
);
