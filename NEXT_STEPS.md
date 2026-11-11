# Next Steps

**Status:** The database is built. It has 80,135 Gaia DR3 stars across 92 streams, from 15 papers. The data, schema, tests, and a basic website are all committed.

## 1. Fix the failing tests

- The monthly scheduled tests have failed since August with `too many SQL variables`. A query sends more values than SQLite allows in one statement, which can happen with 80k sources.
- The "Make ER diagram" and "Test astrodb-utils" workflows also fail.
- `astrodb-build-artifacts/erd.md` and `generate_erd.py` are not committed yet.

## 2. Check the publications

- They were added without checking NASA ADS (`ignore_ads=True`), because no ADS token was set up. They should be checked against ADS.
- `Awad2024` doesn't follow the naming rule (4 letters + 2-digit year). It should be `Awad24`.

## 3. Add the full membership table

- Only `all_streams_unique.fits` (one row per star) is in the database. `all_stream.fits` (all memberships) could be added later, as agreed in the July 6 meeting.

## 4. Plan for new Gaia data

- Write an `astrodb-update-gaia` skill. When new Gaia data comes out, it adds new proper motion rows with `adopted = True` and changes the old rows to `adopted = False`. Old rows are never overwritten.

## 5. Open a GitHub issue on proper motions

- Write down how accurate the proper motions are and why we added the `pmra_pmdec_corr` field.

## July 6th Meeting Notes

Changes to make in the [astrodb_bot](https://github.com/astrodbtoolkit/astrodb-bot) skills before building version 4. Status is as of November 2026.

### Stop and ask the user more

- Parse-table and schema-match should stop so the scientist can check the results before moving on. **Done**
- Skills should not assume decisions in `directions.md`. Review `directions.md` with the user before starting. **Partly done:** schema-match follows `directions.md`, but no skill asks the user to review it first.
- Before making the website, check that the schema match was reviewed. **Not done**
- Figure out the skill order, and which skill creates `schema.yaml` first. **Done:** skills are numbered, and schema-generate (build-05) creates `schema.yaml`.

### Outputs and reports

- Put all outputs in `astrodb-build-artifacts/` instead of making many folders. **Done**
- Make one report for all tables. Separate reports are too hard to review. **Not done**
- End each skill with a checklist, gotchas, and what to do next. **Done**

### workflow.md (the plan document)

- Always create `workflow.md`. Every skill adds to it and explains why it made each decision (for example, why it converted a file to another format). **Done**
- Keep the shared directions in one markdown file under `skills/`, linked into each skill's `references/` folder. **Done:** the file is `astrodb-instructions.md`.

### README

- Explain where schema-generate fits: it runs after schema-match, reads the column-to-table mapping, writes `schema.yaml`, then runs `felis validate`. **Done**

### Personal

- Write my own workflow notes.

## Where to find more

- Build log with exact prompts: [`astrodb-build-artifacts/workflow.md`](astrodb-build-artifacts/workflow.md)
- Meeting decisions: [`astrodb-build-artifacts/directions.md`](astrodb-build-artifacts/directions.md)
- Database contents: [`docs/data_description.md`](docs/data_description.md)
