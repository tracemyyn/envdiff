# envdiff

Compare `.env` files across environments and flag missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/youruser/envdiff.git
cd envdiff && pip install .
```

---

## Usage

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DATABASE_URL
  - REDIS_HOST

Mismatched keys:
  - APP_ENV: "development" vs "production"
  - DEBUG: "true" vs "false"

✔ All other keys match.
```

You can also compare multiple files at once:

```bash
envdiff .env.development .env.staging .env.production
```

Use the `--keys-only` flag to ignore values and check only for missing keys:

```bash
envdiff --keys-only .env.development .env.production
```

---

## Why envdiff?

Misconfigured environment files are a common source of bugs when deploying across environments. `envdiff` gives you a fast, clear diff so nothing slips through.

---

## License

[MIT](LICENSE)