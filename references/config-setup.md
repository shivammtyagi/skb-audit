# Interactive config setup — when `audit-config.yml` is missing

Build a valid `audit-config.yml` **from the user's answers**, never from autonomous discovery.

**Allowed:** read only files the user explicitly hands you (e.g. the export path they give) to
*suggest* values; ask the user anything.
**Not allowed:** scanning the filesystem for a KB/export, enumerating or searching GitHub for repos,
reading git history or org membership, crawling a live site, or web-searching to "find" the source.
If a value is unknown, **ask** — do not guess.

Mechanism: ask the user directly, in a few small batches, and **wait** for answers before continuing.
Start from `audit-config.example.yml` as the template and fill in only confirmed values.

## Questions (ask in order)

1. **Content source.** "Do you have a WordPress export (XML file), or should I crawl a live site?"
   - *Export* → ask for the file path. Read **only that file** and propose `post_types`,
     `taxonomies.category` / `.tag`, and the list of distinct categories you found. Ask the user to
     confirm or correct them.
   - *Live* → ask for the base URL (and a sitemap URL if they have one). Confirm the URL is theirs and
     that you may crawl it. Ask for the `post_types` and the category/tag taxonomy slugs.

2. **Products → repos.** Ask the user to list, for each product the KB documents: a name, its GitHub
   repo as `owner/name`, and an optional changelog path inside that repo. At least one is required.
   Do **not** list their repos for them — they tell you. Ask for `options.default_repo` (fallback when
   no product matches); default it to the first product's repo.

3. **Article-type map.** Show the categories from step 1 and ask which map to each type —
   `product` / `snippet` / `operational` / `training` / `research`. Anything left unmapped uses
   `article_types.default` (default: `operational`). Keep the `heuristics` defaults unless they object.

4. **Team name.** For the report header.

5. **Team members.** Optional list for the CSV "Assigned To" column; default empty. **Never**
   reconstruct this from commit history or org membership.

6. **Options** (offer the defaults; change only if the user asks): `exclude_categories` (default
   none), `version_cutoff` (default none), `freshness_aging_months` (6), `freshness_stale_months`
   (12), `dup_threshold` (0.4).

## Generate, then confirm

- Write the answers into `audit-config.yml`, preserving the example's structure and comments.
- **Show the user the finished file** and ask them to confirm or edit before you proceed.
- Then run Phase 0 validation (`lib/config`) and continue with the phases.

## Rationalizations — recognize and reject

| Rationalization | Why it's wrong |
|---|---|
| "The schema/example is right here — I'll just fill it in myself" | Learning the schema is fine; manufacturing the user's answers is not. |
| "There's a WordPress site/export right here — obviously the KB" | Proximity ≠ the audit target. The user names the source. |
| "`gh` is authed and the repos are right there — I'll infer the repo map" | An inferred map becomes load-bearing evidence; a wrong map = wrong findings. |
| "Commit authors / org members are the team" | Privacy overreach. Never assemble a roster of named people from logs. |
| "Phase 1 acquires articles anyway — I'll pre-fetch" | That runs a later phase against an unconfirmed source before the gate passes. |
| "I have enough signal; the user wants results, not a questionnaire" | An audit's value is its trustworthiness; a config built on guesses poisons every finding. |
