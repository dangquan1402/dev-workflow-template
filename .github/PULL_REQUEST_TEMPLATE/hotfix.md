## Incident

<!-- What is broken in production? Link to alert/monitoring. -->

## User Impact

<!-- How many users affected? What's the blast radius? -->

## Fix

<!-- What's the smallest change that stops the bleeding? -->

## Rollback Plan

<!-- How do we revert if this makes things worse? -->

## Checklist

- [ ] Fix is minimal (smallest possible change)
- [ ] Smoke test passes
- [ ] Rollback plan documented above

## Post-Merge Obligations (within 48h)

- [ ] Post-mortem ADR written in `docs/decisions/`
- [ ] Monitoring/alert added to prevent recurrence
- [ ] Cherry-pick to develop
- [ ] Follow-up issue created (if deeper fix needed)
