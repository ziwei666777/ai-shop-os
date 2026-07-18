# Ponytail Working Rules

This project uses the Ponytail instruction-only mode (MIT, derived from
DietrichGebert/ponytail). Prefer the smallest correct change after tracing the
real workflow end to end.

Before adding code, use the first option that satisfies the requirement:

1. Do not build it when the requirement does not need it.
2. Reuse an existing project pattern, helper, or dependency.
3. Use the standard library.
4. Use a native platform feature.
5. Use the smallest implementation that works.

Keep product requirements, validation, error handling, security,
accessibility, data integrity, and tests intact. Do not introduce a new
abstraction or dependency unless it removes demonstrated complexity. Fix root
causes rather than adding path-specific patches. For non-trivial logic, leave
one focused runnable check that would fail if the behavior regresses.

For AI Shop OS, simplicity must not weaken the core workflow evidence chain:
refund collaboration, warehouse/ERP notification, Savings Engine, CEO daily
reporting, and live-operation evidence must remain auditable.
