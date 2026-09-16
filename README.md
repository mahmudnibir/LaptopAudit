# LaptopAudit

**An open-source inspection toolkit for buying and selling used laptops.**

LaptopAudit collects hardware evidence locally, helps you test the things software cannot reliably see, and turns the results into a portable report. It is designed for buyers, sellers, repair shops, and anyone evaluating a second-hand laptop.

> **Principle:** evidence over false precision. LaptopAudit does not invent missing telemetry or reduce a laptop to one universal score.

## Current status

**Windows-first early MVP.** The current release provides:

- Windows system, CPU, GPU, memory, battery, and storage collection
- Battery health and cycle data where Windows exposes it
- Basic SMART failure-prediction information where available
- Portable JSON evidence
- Self-contained HTML report generation
- Browser-based physical inspection checklist with local notes
- Shared JSON schema for future platform collectors
- Dependency-free Python tests
- GitHub Actions validation for Python and PowerShell

## Quick start

### 1. Run the Windows quick check

Open PowerShell in the repository folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\windows\quick-check.ps1 -OutputPath .\output\laptop-report.json
```

### 2. Generate the report

```powershell
python .\report\generate_report.py .\output\laptop-report.json .\output\laptop-report.html
Start-Process .\output\laptop-report.html
```

### 3. Inspect the physical laptop

Open `physical-check/index.html` in a browser and work through every item. Notes and completion state are stored in that browser's local storage.

No administrator account, network connection, package installation, or telemetry service is required for the quick check.

## What gets checked

| Area | Quick check | Physical check |
|---|---|---|
| System / model | Yes | — |
| CPU | Yes | — |
| GPU | Yes | — |
| RAM | Yes | — |
| Battery | Yes, where exposed | Charging behavior |
| Storage | Model, capacity, basic SMART prediction | — |
| Thermals | Not yet | — |
| Display | — | Pixels, brightness, bleeding, flicker |
| Keyboard | — | Keys, backlight, physical feel |
| Trackpad | — | Movement, clicks, gestures |
| Camera / microphone | — | Image and recording input |
| Speakers / headphone | — | Channels, distortion, jack |
| Ports / charger | — | USB, HDMI, charging |
| Wi-Fi / Bluetooth | — | Connection and accessories |
| Body / hinges | — | Cracks, flex, screws, hinge tension |

## Report semantics

LaptopAudit intentionally separates **what was measured** from **what was not tested**.

- **Good** — available measurement is broadly healthy for the check being reported.
- **Warning** — measurement suggests aging or deserves attention.
- **Critical** — measurement indicates a likely repair or failure concern.
- **Not available** — Windows or the hardware did not expose the value.
- **Not tested** — the check was intentionally not run.

These labels are contextual signals, not a guarantee of device condition. A buyer should inspect the underlying measurements and physical evidence.

## Privacy

LaptopAudit is local-first. The collector writes to the path you provide and does not upload telemetry.

Generated reports may contain sensitive device information, including model names, serial numbers, OS details, and hardware identifiers. **Review the JSON before sharing it.** Never publish a real report containing private identifiers unless you intend to disclose them.

## Safety

The quick check is intentionally conservative. It does **not** stress the CPU, modify firmware, write test data to storage devices, or claim to verify physical condition.

A future full-check layer can add opt-in stress and thermal testing while keeping the quick check safe for normal second-hand inspection.

## Development

Run the dependency-free tests:

```powershell
python -m unittest discover -s tests -v
```

The report generator uses only Python's standard library. PowerShell validation requires Windows PowerShell or PowerShell 7.

GitHub Actions automatically validates the Python test suite, report schema JSON, and PowerShell syntax on pushes and pull requests.

## Repository layout

```text
LaptopAudit/
├── windows/              # Windows collectors
│   └── quick-check.ps1
├── physical-check/       # Browser-based manual inspection
│   └── index.html
├── report/               # Portable report generation
│   └── generate_report.py
├── schemas/              # Shared report contract
│   └── report.schema.json
├── tests/                # Automated tests
├── .github/workflows/    # CI validation
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

## Roadmap

- [ ] Full-check mode with explicit opt-in thermal testing
- [ ] Richer SATA/NVMe SMART attributes
- [ ] Display test utilities for dead/stuck pixels and uniformity
- [ ] Memory diagnostics guidance
- [ ] Linux collector
- [ ] Better upgradeability detection with conservative evidence
- [ ] Optional market/repair-cost notes without changing the evidence model
- [ ] Versioned report schema and migration guidance

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Keep collectors conservative, preserve raw evidence, expose uncertainty, and update the schema and tests when changing the report contract.

## Security

See [`SECURITY.md`](SECURITY.md) for responsible vulnerability reporting.

## License

This project does not currently declare a license. If you want others to legally reuse, modify, or distribute the code, add an explicit open-source license before calling the repository open source.
