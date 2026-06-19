# SKB Audit Rubric

## Criticality
- CRITICAL — factually wrong AND causes user harm/broken workflow/data loss. Immediate.
- HIGH — feature no longer works as described, major version mismatch, core steps wrong. Soon.
- MEDIUM — partially outdated, missing important context, workaround exists. Next cycle.
- LOW — minor inaccuracy, cosmetic UI drift. When convenient.
- NONE — accurate and current.

## Support-Readiness (product/snippet/operational)
- Resolve-ready — clear steps + prerequisites or expected outcome; an agent can act immediately.
- Usable — correct but missing steps/visuals/context.
- Thin — too short to resolve a ticket (type-aware threshold).
- Misleading — present but likely to cause a wrong action.

## Findability
- Good — well-titled, categorized, cross-linked.
- Weak — vague title or poor tags.
- Orphaned — no inbound internal links.
- Duplicated — overlaps another article (see Duplicate-Of).

## Effort
- Quick Fix (<1h) / Medium (1–4h) / Rewrite (4h+).

## Recommendation
Keep / Update / Rewrite / Merge / Retire / Reassign-owner.

## Evidence rule (anti-hallucination)
Every CRITICAL/HIGH finding MUST cite a repo file/commit/issue, or be labeled
"Repo evidence not found — flag for manual review," or be downgraded.
