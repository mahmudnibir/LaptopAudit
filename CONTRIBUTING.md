# Contributing to LaptopAudit

Thanks for helping improve LaptopAudit.

## Design principles

LaptopAudit is an inspection and evidence-collection toolkit, not a benchmark or a universal laptop score. Contributions should favor:

1. **Measured evidence over guesses.** Preserve raw values and expose missing data explicitly.
2. **Safe checks by default.** Do not stress hardware, modify firmware, or write to storage unless a future check is explicitly designed for that purpose and clearly opt-in.
3. **Portable output.** Keep the report schema useful across collectors and platforms.
4. **Privacy by default.** Never upload collected hardware information without explicit user action.
5. **Useful uncertainty.** Distinguish measured, not available, and not tested states.

## Before opening a pull request

- Run `python -m unittest discover -s tests -v`.
- Validate JSON files with a standard JSON parser.
- If you change PowerShell, validate the script on Windows or PowerShell 7.
- Update the report schema and tests when adding or changing report fields.
- Do not commit generated reports or real device data.

## Adding a collector

Keep platform-specific collection inside its platform directory. Normalize the result into the shared report contract rather than making the report renderer depend on one operating system.

If a value cannot be collected reliably, return `null` or an explicit unavailable state instead of estimating it.

## Pull requests

Describe what changed, why it is useful for a real used-laptop inspection, what platforms were tested, and any known limitations.
