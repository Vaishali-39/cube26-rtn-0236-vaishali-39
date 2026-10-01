# Returns Manager - Architecture

## Purpose

The Returns Manager processes customer-return evidence and produces a structured, traceable decision record for downstream Recovery Manager processing.

## Workflow

``text
ReturnCase
    |
Return Images
    |
Vision Pipeline
    |
Identity
    |
Completeness
    |
Condition
    |
Disposition
    |
Structured Evidence Record
`` 

## Core Components

### ReturnCase

Represents the returned unit and contains identifiers, image references, order information, expected parts, missing parts, observed state and operator information.

### Vision Pipeline

Processes one or more return images, produces structured observations, aggregates observations across images and applies the resulting observation to the return case.

The current implementation uses deterministic fixture vision behaviour for local development and testing.

### Identity

Evaluates whether the available evidence supports the returned item's identity matching the expected item.

### Completeness

Evaluates whether expected components are present or missing.

### Condition

Evaluates the observed return state and produces a PASS, FAIL or UNCERTAIN result.

### Disposition

Produces an operational recommendation such as restock, refurbish, liquidate, dispose or pending_review.

### Evidence

Builds the final structured evidence record containing record_id, schema_version, organization_id, client_id, agent, subject, captured_at, operator_label, images, checks, outcome, overrides, status and content_hash.

Individual checks contain verdict, confidence, supporting detail and evidence references where applicable.

## Uncertainty Handling

The system supports PASS, FAIL and UNCERTAIN. Ambiguous visual evidence is not forced into PASS or FAIL and can be preserved for review.

## Evidence Traceability

Image references can be attached to checks so decisions can be traced back to supporting return evidence. The evidence record also contains a deterministic SHA-256 content hash.

## Testing

The project includes automated tests covering the core workflow, identity, completeness, condition, disposition, evidence handling and vision pipeline.

The current local test suite passes successfully.

## Downstream Compatibility

Returns Manager is stage 04 in the Buildathon operational chain: Receiving -> Prep -> Pack -> Returns Manager -> Recovery Manager.

The output is a structured evidence record intended to be understandable by the downstream Recovery Manager.
