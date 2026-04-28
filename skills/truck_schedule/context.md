SKILL: TRUCK_SCHEDULING

DEFAULTS:
start_date: 2025-10-01
default_truck: 9MT

RULES:
- if cases_per_truck > 1000 → 16MT else 9MT

ROUTE_OVERRIDES:
Delhi: 16MT
Mumbai: 9MT

DATE_LOGIC:
- start from start_date
- increment 1 day per trip

USER_CAN_OVERRIDE:
- start_date
- route rules
- truck logic