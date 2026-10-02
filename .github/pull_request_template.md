## What does this PR add or change?

<!-- e.g. new sample 11_exfiltration_markdown_image.eml, fix to 05, README update -->

## For new or changed samples

- Intent:
- Evasion / delivery technique:
- Scenario (the benign-looking cover story):
- Controls you tested it against, and what happened (optional):

## Checklist

- [ ] `python scripts/validate_samples.py` passes
- [ ] All people, companies and domains are fictional; only reserved domains are used (`.example`, `example.com`, `.test`, `.invalid`)
- [ ] Payloads are limited to the benign test intents (no working malware, real phishing kits, real credentials or real exfiltration endpoints)
- [ ] The `X-Injection-Test` header is set and the README matrix is updated
