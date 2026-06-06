# Pull Request: Proposal — Multi-Stage Redline Support & LMU GT3 Car Profiles

## Description
Some Le Mans Ultimate GT3 cars (like the 2025 Z06) feature RPM LED clusters with multi-stage redline behavior, where all LEDs change color in sequence (e.g.Red → Blue) as RPM climbs past specific thresholds. The current format doesn't have a clear way to represent this. This PR proposes a small, (hopefully) backward-compatible extension to the file format spec alongside three new car profiles that rely on this structure.

Open to feedback on the approach — happy to adjust based on your preferences.

### Changes

1. **Proposed update to `README.md` — File Format Specification:**
   - Added optional `redline1`–`redlineN` entries to the `ledColor` and `ledRpm` documentation, prepended before the existing `led1`–`ledN` entries.
   - Consumers can detect the extra array length (`ledColor.length > ledNumber`) and use the offset to drive sequential redline stages. Existing files with no redline stages are unaffected.
   - Open to alternative structural approaches if a different convention would be preferred.

2. **Proposed update to `README.md` — Per-Stage Blinking:**
   - Modified `redlineBlinkInterval` to support both `Int` and `Array` types.
   - For multi-stage cases, an array maps 1:1 with stages (e.g., `[0, 250]` for static then blinking).
   - Downstream consumers (Python/JS) can handle this union type dynamically, while strictly typed languages (C#/Rust) would use standard JSON sum-type patterns.
   - This ensures backward compatibility for single-stage cars while enabling high-fidelity behavior for complex GT3 dashes.

3. **Updated `ferrari296gt3.json` (iRacing) as an example:**
   - Ferrari 296 GT3 profile with 6 LEDs and 2 redline stages.
   - Stage 1 (Static Red): `0` ms blink.
   - Stage 2 (Blinking Red): `250` ms blink.

## Considerations
- **Union Type Handling**: Adopting `Int | Array<Int>` is safe for modern JSON consumers. Python/JS tools used for SimHub profile generation handle this with simple type checks.
- **Backward Compatibility**: Single-stage profiles continue to use a single integer, preventing any breaking changes for existing repositories.
- **Telemetry Fidelity**: This change allows for exact matching of real-world LED behaviors like "solid color change -> final warning blink" sequences.

> **Note:** I included these Z06 GT3R and Ferrari 296 updates as examples. LMU v1.3 updates may change some car ID logic, but this format extension remains robust regardless of car identification methods.

## Testing
- All JSON files pass `pre-commit run --all-files` (check json + pretty format).
- Array lengths are consistent: `ledColor` has 10 entries, each gear RPM array has 10 entries, matching `ledNumber (8) + redline stages (2)`.
- Format aligns with the proposed README specification for `redline1`–`redlineN` handling.
