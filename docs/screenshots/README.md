# Submission screenshots

This folder stores the public visual evidence for the ADTC Gate 1 report and two-minute video.

Use synthetic test orders and resettable test phones only. Before committing an image, remove or obscure customer emails, phone numbers, activation keys, session tokens, device serials, vendor secrets and private order references.

## Capture list

1. `01-offline-companion-home.png` — installed companion open as a desktop application, showing the local model as ready.
2. `02-agent-starts-the-workflow.png` — the offline agent leads the first turn without waiting for a technician prompt.
3. `03-paid-order-selection.png` — a synthetic unpaid/paid-order state and the generated order-selection control.
4. `04-device-connection-check.png` — the companion distinguishes disconnected, unauthorized and exactly-one-authorized-phone states.
5. `05-read-only-baseline.png` — the captured clean Android state before any phone-changing action.
6. `06-action-preview-and-consent.png` — the registered provisioning action, its effect, risk and technician approval boundary.
7. `07-evidence-gated-progress.png` — workflow progress with evidence provenance rather than chat confirmation alone.
8. `08-restoration-and-reboot-verification.png` — verifier restoration and post-reboot persistence evidence from the disposable-phone pilot.
9. `09-completion-receipt.png` — the final installation evidence record, using synthetic identifiers.
10. `10-ubuntu-profiler-result.png` — reviewed summary of the virtual Ubuntu 22.04 development and official-profiler integration results.
11. `11-sealed-q4-result.png` — the one-time 24-case sealed result, including the failed zero-contract-failure gate.
12. `12-physical-ubuntu-compatibility-result.png` — the completed profiler run on a non-target physical Ubuntu laptop, including the CPU and thermal limitation.
13. `13-physical-ubuntu-target-result.png` — the final official profiler result from a conforming physical Ubuntu 22.04 laptop, with accuracy and thermals.

## Naming and format

- Store lossless PNG files at their original readable resolution.
- Keep the numbered order above so the report tells one continuous story.
- Add a short caption and the producing build/commit to the table below.

| File | Build or commit | Caption | Captured |
|---|---|---|---|
| `10-ubuntu-profiler-result.png` | `9cbd484` + uncommitted Ubuntu evidence pass | Q4 passed 11/11 without repair; virtual profiler limits shown on the image | 20 Aug 2026 |
| `11-sealed-q4-result.png` | `2da2845` | Q4 passed 23/24; one response and repair both ended as incomplete JSON | 20 Aug 2026 |
| `12-physical-ubuntu-compatibility-result.png` | `4666b41` + returned physical evidence | Full profiler completed; CPU fell outside target and throttled at 86°C | 20 Aug 2026 |
