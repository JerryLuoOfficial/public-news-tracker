# Public news check

A minimal, dependency-free collector for the public feed used by Sina Finance's 7x24 page. Stores only headline, a short excerpt, original URL, source and publication time. Does not grant redistribution rights. No brokerage connections, portfolio information or AI prompts belong in this repository.

The schedule requests a check every five minutes. GitHub may delay or drop scheduled jobs; this is not a guaranteed real-time feed. Public repository schedules may be disabled after inactivity. Review source terms and stop collection if access is withdrawn.

Configure repository Actions secrets: `DESK_URL`, `SITES_TOKEN`, `NEWS_SIGNING_SECRET`. Never commit their values. Signing is scoped to news ingestion, with a timestamp and replay-resistant nonce. Identity-less requests cannot read private account or chat routes.

Run `python3 collector.py --check` for a source-only test. The program prints only counts and timestamps; failures retain previous data and report a generic error. Do not print request headers, environment variables or exceptions containing credentials in CI logs.
