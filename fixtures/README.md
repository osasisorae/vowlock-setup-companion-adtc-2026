# Synthetic fixture policy

`development/` contains invented scenarios used to build and regress the deterministic evaluator. They contain no physical-device identifiers, customer data, secrets, APKs or observed values copied from a user device.

The future held-out set belongs under `sealed/`, which is ignored by Git. Its hashes and evaluation protocol may be published after the experiment, but its case content must not guide prompt or evaluator revision. If it does, those cases become development data and a new sealed set is required.

Fixture labels are independent test expectations. Production evaluation code must not read `expected_outcome` to make a decision; the test suite includes an invariance check for this boundary.
