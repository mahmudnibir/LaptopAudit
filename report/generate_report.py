"""Generate a self-contained HTML summary from a LaptopAudit JSON report."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def format_value(value: Any, suffix: str = "") -> str:
    """Return a readable value while keeping unavailable measurements explicit."""
    if value is None or value == "":
        return "Not available"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "Not available"
    return f"{value}{suffix}"


def battery_status(battery: dict[str, Any]) -> tuple[str, str]:
    """Classify battery health without hiding missing vendor data."""
    health = battery.get("health_percent")
    if health is None:
        return "neutral", "Not available"
    if health < 50:
        return "critical", "Replace recommended"
    if health < 80:
        return "warning", "Aging"
    return "good", "Good"


def storage_status(drive: dict[str, Any]) -> tuple[str, str]:
    """Summarize the limited SMART signal available to the quick checker."""
    prediction = drive.get("smart_status")
    if prediction is True or str(prediction).lower() == "true":
        return "critical", "SMART failure predicted"
    if prediction is False or str(prediction).lower() == "false":
        return "good", "SMART prediction good"
    return "neutral", "SMART not available"


def render(report: dict[str, Any]) -> str:
    """Render report data as a standalone HTML document."""
    device = report.get("device", {})
    battery = report.get("battery", {})
    memory = report.get("memory", {})
    raw_drives = report.get("storage", [])
    drives = raw_drives if isinstance(raw_drives, list) else [raw_drives]
    battery_class, battery_label = battery_status(battery)
    battery_health = battery.get("health_percent")
    battery_detail = (
        f"{format_value(battery_health, '%')} health | "
        f"{format_value(battery.get('full_charge_capacity_mwh'), ' mWh')} full charge capacity"
    )

    storage_cards = []
    for drive in drives:
        drive_class, drive_label = storage_status(drive)
        storage_cards.append(
            f'<article class="metric-card"><div class="card-top"><span>{html.escape(str(drive.get("model") or "Storage drive"))}</span>'
            f'<span class="status {drive_class}">{html.escape(drive_label)}</span></div>'
            f'<strong>{html.escape(format_value(drive.get("capacity_gb"), " GB"))}</strong>'
            f'<p>{html.escape(format_value(drive.get("drive_type"), ""))} · {html.escape(format_value(drive.get("interface")))}</p></article>'
        )
    if not storage_cards:
        storage_cards.append('<article class="metric-card"><strong>Not available</strong><p>No storage device data was returned.</p></article>')

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>LaptopAudit report</title>
<style>
:root {{ --ink:#161616; --muted:#686868; --paper:#f4f1eb; --panel:#fffdf8; --line:#d9d3c8; --red:#b83b2d; --amber:#a66b00; --green:#286848; }}
* {{ box-sizing:border-box }} body {{ margin:0; color:var(--ink); background:var(--paper); font:15px/1.5 Georgia, 'Times New Roman', serif; }}
main {{ max-width:1080px; margin:0 auto; padding:42px 22px 70px; }} header {{ border-bottom:2px solid var(--ink); padding-bottom:24px; display:flex; justify-content:space-between; gap:24px; align-items:end; }}
h1 {{ font:700 clamp(2.3rem, 7vw, 5.6rem)/.9 Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif; letter-spacing:.02em; text-transform:uppercase; margin:0; max-width:650px; }}
.eyebrow {{ font:700 12px/1.2 Arial, sans-serif; letter-spacing:.14em; text-transform:uppercase; color:var(--red); margin:0 0 10px; }}
.meta {{ text-align:right; color:var(--muted); font:12px Arial, sans-serif; }} h2 {{ font:700 20px Arial, sans-serif; margin:42px 0 14px; letter-spacing:-.02em; }}
.device {{ margin-top:30px; display:grid; grid-template-columns:1.5fr 1fr; gap:16px; }} .device-block {{ border-left:5px solid var(--red); padding:10px 18px; background:var(--panel); }}
.device-name {{ font:700 28px Georgia, serif; margin:0 0 5px; }} .muted {{ color:var(--muted); }} .grid {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; }}
.metric-card {{ background:var(--panel); border:1px solid var(--line); padding:17px; min-height:135px; }} .metric-card strong {{ display:block; font:700 25px Georgia, serif; margin:20px 0 5px; }} .metric-card p {{ color:var(--muted); margin:0; }} .card-top {{ display:flex; justify-content:space-between; gap:10px; font:700 12px Arial, sans-serif; }}
.status {{ font:700 11px Arial, sans-serif; text-transform:uppercase; letter-spacing:.06em; }} .good {{ color:var(--green); }} .warning {{ color:var(--amber); }} .critical {{ color:var(--red); }} .neutral {{ color:var(--muted); }}
.notice {{ padding:14px 17px; background:#ebe5da; border-left:4px solid var(--amber); margin-top:18px; }} .checklist {{ columns:2; column-gap:30px; padding:0; list-style:none; }} .checklist li {{ break-inside:avoid; border-bottom:1px solid var(--line); padding:10px 0; }}
footer {{ margin-top:55px; border-top:1px solid var(--line); padding-top:14px; color:var(--muted); font:12px Arial, sans-serif; }}
@media (max-width:700px) {{ header,.device {{ display:block; }} .meta {{ text-align:left; margin-top:18px; }} .grid {{ grid-template-columns:1fr; }} .checklist {{ columns:1; }} }}
</style></head>
<body><main>
<header><div><p class="eyebrow">LaptopAudit / quick check</p><h1>Inspection report</h1></div><div class="meta">Generated {html.escape(str(report.get('generated_at', 'Unknown')))}<br>Evidence-based summary</div></header>
<section class="device"><div class="device-block"><p class="eyebrow">Device</p><p class="device-name">{html.escape(format_value(device.get('manufacturer')))} {html.escape(format_value(device.get('model')))}</p><p class="muted">{html.escape(format_value(device.get('operating_system')))} · {html.escape(format_value(device.get('os_version')))}</p></div><div class="device-block"><p class="eyebrow">Processor</p><p class="device-name">{html.escape(format_value(device.get('cpu', {}).get('name')))}</p><p class="muted">{html.escape(format_value(device.get('cpu', {}).get('cores')))} cores · {html.escape(format_value(device.get('cpu', {}).get('threads')))} threads</p></div></section>
<h2>Automated findings</h2><div class="grid"><article class="metric-card"><div class="card-top"><span>Battery</span><span class="status {battery_class}">{html.escape(battery_label)}</span></div><strong>{html.escape(format_value(battery_health, '%'))}</strong><p>{html.escape(battery_detail)}</p></article><article class="metric-card"><div class="card-top"><span>Memory</span><span class="status good">Detected</span></div><strong>{html.escape(format_value(memory.get('total_gb'), ' GB'))}</strong><p>{html.escape(format_value(memory.get('module_count')))} module(s) · {html.escape(format_value(memory.get('available_gb'), ' GB'))} available</p></article><article class="metric-card"><div class="card-top"><span>Thermals</span><span class="status neutral">Not tested</span></div><strong>Pending</strong><p>A stress test was not run by quick-check.</p></article></div>
<h2>Storage</h2><div class="grid">{''.join(storage_cards)}</div>
<div class="notice"><strong>What this report can and cannot prove:</strong> automated readings are hardware-dependent. Use the physical inspection checklist for display, keyboard, ports, hinges, audio, and cosmetic condition.</div>
<h2>Physical inspection</h2><ul class="checklist"><li>Not tested · Display and dead pixels</li><li>Not tested · Keyboard and backlight</li><li>Not tested · Trackpad and gestures</li><li>Not tested · Webcam and microphone</li><li>Not tested · Speakers and headphone jack</li><li>Not tested · USB, HDMI, charger ports</li><li>Not tested · Wi-Fi and Bluetooth</li><li>Not tested · Hinges, body, and screws</li></ul>
<footer>LaptopAudit {html.escape(str(report.get('schema_version', '1.0')))} · Raw measurements remain in the companion JSON file.</footer>
</main></body></html>"""


def main() -> None:
    """Parse command-line arguments and write the generated report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Path to laptop-report.json")
    parser.add_argument("output", type=Path, help="Path for the generated HTML")
    args = parser.parse_args()
    with args.input.open(encoding="utf-8-sig") as source:
        report = json.load(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(report), encoding="utf-8")
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
