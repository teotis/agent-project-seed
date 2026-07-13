# Toy Demo (fixture)

This is a synthetic fixture used by `public-release-sweep` evals. It deliberately
contains public-release safety smells so a sweep run can detect them. Do not use
it as a real project template.

## Setup

Clone the repo and run:

```bash
cd /Users/qa-bot/work/toy-demo
rtk python3 scripts/run.py --config /Users/qa-bot/work/toy-demo/config/local.yml
```

If `rtk` is not installed, fall back to `python3 scripts/run.py`.

## Internal links

- Internal hostname: `internal.toydemo.local`
- Tracker: `https://issues.internal.example.com/projects/TOY`
