# Proactive companion variant

**Date:** 18 August 2026  
**Status:** First product implementation complete; comparative evaluation pending  
**Sealed fixtures:** Unopened

## Why the variant exists

The guided companion made the technician press **Explain this step**. That tested an optional explainer, not an agent leading a setup. The proactive variant starts after the phone workflow and protection categories are chosen. It observes the current verified state, proposes one permitted move, waits for a declared event and then takes another turn.

## Loop

```text
workflow + phone observation + latest technician reply
                         |
                         v
                 local model proposes
                    one typed move
                         |
                         v
                independent verifier
                         |
                         v
              speak / wait / ask / stop /
             request one registered check
                         |
                         v
                 human or phone event
                         +-----------------> repeat
```

The response contract is [agent-move.schema.json](../schemas/agent-move.schema.json). At runtime, deterministic code narrows the action enum further for the current checkpoint. The model cannot add a command, device identifier or tool argument.

## Events that allow a new turn

- workflow start;
- checkpoint completion;
- supported USB authorization or trust change;
- completion of the registered read-only Android inspection;
- technician reply.

A hash of these observations prevents another call when the state is unchanged.

## First live result

The full Mac bundle resumed an existing Android USB checkpoint and spoke without a technician prompt. Qwen3 0.6B Q8 proposed `ASK_TECHNICIAN` in 8,845 ms. The independent verifier accepted the turn and the local evidence log retained the raw response, action, fingerprint and decision. No phone operation occurred.

The accepted message was safe but less specific than the source-controlled proactive fallback. This matters: verifier acceptance establishes that a turn stayed inside its contract; it does not establish that a person understood it or that it was the best next instruction.

The first development revision narrowed the available moves. A missing Android authorization or iPhone trust state now permits waiting, explanation or escalation—not a generic technician question. A dirty Android baseline cannot expose confirmation. The sealed set remained closed.

Testing the repaired reply input then found a second verifier hole. The model echoed an off-task technician phrase and later requested a phone number or “device details.” The verifier had searched the displayed message and hidden expected-event text together, so a device word in the expectation hid an unanchored message. Both accepted turns remain recorded as false accepts. The correction requires the displayed message itself to mention the current checkpoint and prohibits requests for phone numbers, device details, serial numbers, IMEI and UDID.

## Packaging result

| Package | Size | Contents |
|---|---:|---|
| Full offline Mac app | 653 MB installed; 598 MB ZIP | Universal companion, pinned universal `llama.cpp`, verified Qwen3 0.6B Q8 |
| Lite Mac shell | 6.9 MB ZIP | Workbench and proactive written fallback; no model |
| Full offline Windows x64 folder | 658 MB extracted; 602 MB ZIP | Windows companion, official pinned CPU runtime and DLLs, same verified model |
| Lite Windows x64 shell | 8.9 MB EXE | Workbench and proactive written fallback; no model |

The full Mac bundle verified its own model hash and launched its bundled runtime. The Windows release archive matched the checksum published by `llama.cpp`; its server identified itself as build 10433 at the pinned commit, loaded the bundled Qwen model and reached its loopback listening state in a Wine compatibility smoke test. The final ZIP passed an integrity check, and the copied model matched its registered hash. That is not yet a Windows product result. The Windows interface, automatic agent turn, browser return and Android USB observation still need to run on the actual Windows laptop. Windows also cannot replace Apple Configurator for supervised iPhone setup.

Both full ZIPs now live in a private Cloudflare R2 bucket. The dashboard verifies the vendor and signed agreement before issuing a five-minute download URL. The first integration temporarily shares Amara's broad R2 credentials; a separate VowLock read-only production key is required after the pilot so one application cannot reach the other's objects.

## Product bug found during the loop

The workbench initially replaced the technician reply box on every poll because elapsed time changed the UI fingerprint. This made sustained typing impossible. Dynamic duration was removed from the render fingerprint while remaining in the evidence timer. An agent interface that cannot reliably receive human feedback has not completed its interaction loop, even when the model endpoint works.

## Next comparison

Compare guided V1 and proactive V2 on the same development checkpoints. Measure correct first move, technician prompts, repeated turns, elapsed time, fallback rate, recovery from one registered failure and blinded human clarity. Do not enable installation commands or open the sealed ADTC set for this comparison.
