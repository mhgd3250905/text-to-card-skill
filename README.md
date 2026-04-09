# text-to-card-skill

A Codex-compatible skill that turns text into a mobile share card through a strict three-step artifact pipeline:

1. `design.json`
2. `card.html`
3. `card.png`

The core design goal is reliability, not vague prompt-following. The skill now uses a fixed schema, validation scripts, and regression cases so downstream agents are much less likely to skip steps or silently return broken output.

## What This Skill Does

`card-creator` is intended for requests such as:

- share cards
- posters
- image cards
- Xiaohongshu / Moments share images
- report cards
- infographic-style mobile summaries

It is optimized for vertical mobile cards with:

- fixed `1080px` width
- adaptive height
- single-column layout
- explicit design/output checkpoints

## Repository Structure

```text
.
├── SKILL.md
├── README.md
├── evals/
├── manual-runs/
├── references/
├── scripts/
└── styles/
```

Key files:

- `SKILL.md`: the actual skill definition
- `references/design-schema.md`: required schema for `design.json`
- `scripts/validate_design_json.py`: validates Step 1 output
- `scripts/validate_html.py`: validates Step 2 output
- `scripts/validate_png.py`: validates Step 3 output, including blank-image detection
- `scripts/run_regression.py`: runs regression cases from `manual-runs/manifest.json`

## Execution Contract

The only valid execution order is:

1. generate `design.json`
2. generate `card.html`
3. generate `card.png`

Do not:

- merge Step 1 and Step 2
- write HTML without `design.json`
- screenshot without `card.html`
- treat an internal design idea as a completed Step 1
- skip validation

## Preset Styles

The skill ships with two normalized presets:

- `styles/dark-alert-report.json`
- `styles/glass-news-report.json`

If neither preset fits, the agent should generate a new `design.json` that still conforms to the same schema.

## Validation

Validate each artifact explicitly:

```powershell
python scripts/validate_design_json.py path\\to\\design.json
python scripts/validate_html.py path\\to\\card.html
python scripts/validate_png.py path\\to\\card.png --expected-width 1080 --min-height 1200 --min-ratio 1.1 --reject-blank
```

`validate_png.py` checks:

- exact width
- minimum height
- minimum aspect ratio
- near-blank / white screenshots

## Regression

This repository includes manual regression cases in `manual-runs/`.

Run validation only:

```powershell
python scripts/run_regression.py
```

Re-capture screenshots and validate again:

```powershell
python scripts/run_regression.py --recapture
```

Run a single case:

```powershell
python scripts/run_regression.py --case short
python scripts/run_regression.py --case short --recapture
```

## Step 3 Notes

Screenshot generation relies on `agent-browser`. In restricted environments, Step 3 may require elevated permissions to open local HTML and save PNG output.

The current regression runner already handles a practical failure mode:

- if the screenshot is blank or invalid, it retries capture once before failing

## Current Status

This version has been hardened against the main failure modes that previously caused agents to drift from the intended workflow:

- inconsistent preset schema
- skipping `design.json`
- invalid HTML structure
- screenshot outputs that were technically the right size but visually blank

It is substantially more reliable than the original prompt-only version, but screenshot generation still depends on the runtime environment and browser permissions.
