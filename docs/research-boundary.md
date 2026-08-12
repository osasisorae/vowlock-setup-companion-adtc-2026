# Research and product boundary

## Product statement

Setup Companion is a new, unlaunched experimental proof of concept created for ADTC 2026. VowLock is an existing experimental alpha used as its first integration case study and source workflow. Setup Companion—not VowLock—is the submitted product.

This repository must not imply that the challenge created VowLock or that Setup Companion has completed a safe physical installation. It must not contain payment keys, customer data, production activation secrets or a signed commercial APK.

## Current research scope

- Ubuntu 22.04 challenge environment.
- Public GGUF model through `llama.cpp`.
- Synthetic Android provisioning states derived from the workflow.
- Deterministic state machine with known success and failure fixtures.
- Static, ordinary one-shot, bounded and adaptive-bounded explanation variants.
- Append-only synthetic evidence and independently scored outputs.

## Model authority

The model may:

- explain a known state in plain language;
- classify an observation into a known failure category;
- request specific missing non-sensitive evidence;
- choose from an approved explanation vocabulary;
- return `STOP` when the state is unknown or consequential evidence is absent.

The model may not:

- create or execute shell/ADB commands;
- select or control a device;
- disable or restore a security control;
- install an APK or assign Device Owner;
- erase or reboot a device;
- redeem a key or activate a commitment;
- improvise an action for an unknown failure.

Operational authority belongs exclusively to deterministic code with typed states, evidence requirements and explicit stop conditions. A model response never authorizes a transition.

## Frozen physical work

Until a disposable Google-certified phone is available and a later experiment is explicitly approved, do not query or mutate the activated phone, run ADB against a physical device, test verifier restoration, build/distribute a signed release APK or activate a commitment.

The first prototype must use synthetic identifiers. Passing its tests is evidence about the simulator and explanation architecture only; it is not evidence of Play Protect compatibility, verifier restoration or physical-device safety.
