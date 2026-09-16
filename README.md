# LaptopAudit

LaptopAudit is a Windows-first used laptop inspection system. Run one checker, keep the raw evidence, and generate a report that separates measured hardware facts from physical inspection notes.

It is designed for buyers, sellers, repair shops, and anyone evaluating a second-hand laptop without pretending that incomplete hardware telemetry is certainty.

## Project status

The current release is an early Windows quick-check MVP. It collects system, CPU, GPU, memory, battery, and storage information, then creates a portable HTML report. The physical inspection page covers the hardware that software cannot reliably judge.

## Quick start

From PowerShell in this folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\windows\quick-check.ps1 -OutputPath .\output\laptop-report.json
python .\report\generate_report.py .\output\laptop-report.json .\output\laptop-report.html
Start-Process .\output\laptop-report.html
```

For the physical checklist, open `physical-check/index.html` in a browser. It stores completion state and notes in local browser storage.

No administrator account, network connection, package installation, or telemetry service is required for the quick check.

## What is included

- `windows/quick-check.ps1`: collects Windows system, CPU, GPU, RAM, battery, and storage facts.
- `report/generate_report.py`: creates a portable HTML report from the JSON evidence.
- `physical-check/index.html`: records display, keyboard, trackpad, camera, audio, ports, wireless, and body checks.
- `schemas/report.schema.json`: documents the cross-platform report contract.

## Report semantics

LaptopAudit keeps raw measurements and uses conservative statuses:

- `Good`: the available measurement is within a broadly healthy range.
- `Warning`: the measurement suggests aging or needs attention.
- `Critical`: the measurement indicates a likely repair or failure concern.
- `Not available`: Windows or the hardware did not expose the value.
- `Not tested`: the check was intentionally not run.

The report does not calculate a universal score. Laptop priorities differ, and a buyer should be able to weigh battery life, storage, repair cost, and physical condition differently.

## Privacy and safety

Reports can include device model, serial numbers, operating-system details, and hardware identifiers. Review `laptop-report.json` before sharing it publicly. The collector writes only to the path you provide and does not upload data.

The quick check does not stress the CPU, modify firmware, write to storage devices, or claim to verify physical condition. Use the physical checklist while inspecting the actual laptop.

## Development

Run the dependency-free tests with:

```powershell
python -m unittest discover -s tests -v
```

The HTML generator uses only Python's standard library. PowerShell validation requires Windows PowerShell or PowerShell 7 and is run on the target laptop.

## Important limitations

Hardware telemetry depends on the laptop manufacturer and Windows permissions. Missing values are reported as `Not available`, not guessed. The quick check does not run a stress test or make claims about dead pixels, physical damage, upgradeability, or port condition.

Future layers can add `full-check` thermal testing, richer SMART attributes, Linux collectors, and optional Bangladesh repair-cost notes without changing the report format.

## Contributing

Keep collectors conservative: preserve raw evidence, return explicit unavailable states, avoid universal hardware thresholds, and update the schema and tests when adding fields. Do not commit generated reports from the `output/` directory.
