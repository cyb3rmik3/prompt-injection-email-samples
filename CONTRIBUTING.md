# Contributing

Thanks for helping improve this test set. Contributions of all sizes are
welcome: new samples, new evasion techniques, results from testing against a
particular product, fixes, and documentation.

## Ways to contribute

- **Add a sample.** Cover a new intent, a new evasion technique, or a new cell
  of the existing intent × evasion matrix. Benign controls that are tricky to
  classify correctly (they look suspicious but aren't) are just as valuable.
- **Share results.** Open an issue describing which control you tested
  (product, version or date, configuration) and which samples were detected or
  changed assistant behavior. Please don't include tenant identifiers or
  anything from real mailboxes.
- **Improve docs or tooling.** Clarifications, delivery how-tos for other mail
  platforms, and improvements to `scripts/validate_samples.py`.
- **Report a problem.** If a sample is malformed, a payload doesn't decode, or
  the documentation is wrong, open an issue.

## Rules for samples

These rules keep the set safe to publish and safe to run:

1. **Fictional only.** Use the fictional MegaCorp company (or another clearly
   invented organization) and invented people. Don't impersonate real
   companies, brands or individuals.
2. **Reserved domains only.** Every address and URL must use a domain reserved
   for documentation or testing: `*.example`, `example.com`, `example.net`,
   `example.org`, `*.test` or `*.invalid` (RFC 2606 / RFC 6761). This includes
   URLs hidden in Base64 or other encodings. Users swap in their own sinks when
   testing.
3. **Benign payloads.** Injections should *attempt* a test behavior
   (disclosing a system prompt, emitting a sink URL, listing tools, and so on)
   without carrying anything harmful in themselves. No malware, working
   exploits, real phishing kits, real credentials or personal data.
4. **Format.** Plain-text RFC 5322 `.eml` files (see the README for why), in
   `samples/`, named `NN_intent_evasion.eml` with the next free number.
5. **Metadata header.** Include an `X-Injection-Test` header, for example:

   ```
   X-Injection-Test: intent=data-exfiltration-url; evasion=hidden-html-displaynone; control=false
   ```

   Reuse existing `intent` and `evasion` values where they fit, so results stay
   comparable.
6. **Message-ID.** Use a unique `Message-ID` such as
   `<mc-11-short-description@megacorp.example>`.
7. **Encoded payloads.** If you Base64 or otherwise encode an instruction,
   make sure it decodes to the plaintext you describe, and mention the plaintext
   in your PR.

## Workflow

1. Fork the repository and create a branch.
2. Add or edit files in `samples/`.
3. Run the validator (Python 3.10+, no dependencies):

   ```sh
   python scripts/validate_samples.py
   ```

4. Add your sample to the table in `README.md`.
5. Open a pull request and fill in the template. CI runs the same validator.

## Responsible use

By contributing you agree that your contribution is licensed under the
repository's [MIT License](LICENSE), and that it's intended for testing
systems you own or are authorized to test.
