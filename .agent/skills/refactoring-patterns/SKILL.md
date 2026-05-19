---
name: refactoring-patterns
description: Safe refactoring workflow for improving existing code without changing behavior.
when_to_use: "When modernizing legacy code, reducing duplication, splitting large files, renaming APIs, or changing structure while preserving behavior. NOT for new feature work unless refactoring is required first."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Refactoring Patterns

## Goal

Improve structure while preserving observable behavior.

## Protocol

1. Identify the existing behavior and public contracts.
2. Find direct consumers before editing shared code.
3. Add or locate regression coverage for the behavior being preserved.
4. Make one structural change at a time.
5. Run the narrowest reliable verification after each meaningful step.
6. Update docs only when the public API, setup, or workflow changes.

## Safe Patterns

- Extract function when a block has one clear purpose and repeated inputs.
- Extract component when UI state, rendering, or responsibility is separable.
- Rename only after finding all call sites.
- Replace conditionals with maps only when keys are stable and validation exists.
- Introduce abstractions only when they remove real duplication or clarify a domain boundary.

## Guardrails

- Do not mix refactoring with feature changes unless the user asked for both.
- Do not change response shapes, database schema, or public component props without updating consumers.
- Do not remove tests unless they are invalid and replaced by equivalent or stronger coverage.
- Do not increase hidden coupling through global state or shared mutable helpers.
