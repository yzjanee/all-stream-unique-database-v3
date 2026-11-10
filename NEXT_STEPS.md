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

## Where to find more

- Build log with exact prompts: [`astrodb-build-artifacts/workflow.md`](astrodb-build-artifacts/workflow.md)
- Meeting decisions: [`astrodb-build-artifacts/directions.md`](astrodb-build-artifacts/directions.md)
- Database contents: [`docs/data_description.md`](docs/data_description.md)
