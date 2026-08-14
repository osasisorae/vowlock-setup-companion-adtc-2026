# Synthetic fixture policy

`development/` contains invented scenarios used to build and regress the deterministic evaluator. They contain no physical-device identifiers, customer data, secrets, APKs or observed values copied from a user device.

The held-out set belongs under `sealed/`, which is ignored by Git. Its private generation seed is also ignored. `sealed-manifest.json` publishes only opaque filenames and SHA-256 hashes so the local files can be checked for mutation without revealing their content. The set must not guide prompt or evaluator revision. If it does, those cases become development data and a new untouched test set is required.

This is a synthetic, seed-private holdout—not independently collected ground truth. The generator shares the public state vocabulary but does not call the production evaluator to create labels. The set tests whether frozen behavior generalizes to uninspected combinations; organizer-supplied hidden prompts provide the external evaluation.

Fixture labels are independent test expectations. Production evaluation code must not read `expected_outcome` to make a decision; the test suite includes an invariance check for this boundary.
