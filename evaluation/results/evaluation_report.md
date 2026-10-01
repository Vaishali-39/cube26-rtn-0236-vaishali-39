# Returns Manager — Evaluation Results

## Evaluation scope

This evaluation measures the deterministic fixture vision pipeline using the
five return-image fixtures currently available in the repository.

This is a development evaluation, not a 50-unit unseen/held-out evaluation
set. The repository does not currently contain the recommended 50 unseen units
or two independent human labels, so no claim of that evaluation standard is
made here.

## Vision observations

| Fixture | Expected scenario | Observed state | Identity | Confidence |
|---|---|---|---|---:|
| sealed_complete.jpg | Factory sealed complete item | factory_sealed | match | 1.0 |
| opened_unused.jpg | Opened unused item | opened_unused | match | 1.0 |
| missing_parts.jpg | Missing/partial components | opened_unused | match | 1.0 |
| damaged_item.jpg | Damaged returned item | damaged | match | 1.0 |
| uncertain_identity.jpg | Ambiguous identity | uncertain | uncertain | 0.0 |

## Uncertainty handling

The `uncertain_identity.jpg` fixture produced:

- identity: `uncertain`
- state: `uncertain`
- confidence: `0.0`

This demonstrates that ambiguous visual evidence is not automatically converted
into a confident identity match.

## Coverage

The fixture set covers:

- factory-sealed evidence
- opened/unused evidence
- missing-parts scenario
- damaged-item scenario
- ambiguous identity evidence

## Limitations

This evaluation does not establish production accuracy.

It does not include:

- 50 unseen evaluation units
- two independent human labels
- human-agreement measurement
- statistically representative return data

The results should therefore be interpreted as development/functional
validation rather than a production accuracy benchmark.

## Test suite

The automated project test suite currently passes:

`48 passed`

The test suite covers the core Returns Manager workflow, vision pipeline,
identity, completeness, condition, disposition, evidence, and evidence
traceability behaviour.
