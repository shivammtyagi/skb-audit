# Report Design (distilled, adapted)

Principles distilled from the taste-skill (anti-slop) + output-skill (no truncation) and
BAKED IN here — no runtime dependency on those skills. Adapted because this is a data-dense
report, which is outside the taste-skill's landing-page scope.

- Self-contained: single report.html, inline CSS, system-font stack, ZERO external/CDN/font/network requests.
- Anti-slop: no AI-purple, no decorative gradients, no motion.
- Color: neutral base (slate/zinc) + a SEMANTIC severity palette (CRITICAL #b91c1c, HIGH #c2410c,
  MEDIUM #a16207, LOW #2563eb, NONE #16a34a), used consistently. Accent = meaning, not decoration.
- Typography: system sans, clear hierarchy, tabular numerals for counts, ~65ch prose.
- Layout/density: cockpit/data density; CSS grid; max-width container; wide tables scroll in
  an overflow container so the page never scrolls horizontally.
- Completeness: never truncate findings or drop rows; long sections collapse, never "...and N more".
- Credit the taste-skill inspiration in an HTML comment.
