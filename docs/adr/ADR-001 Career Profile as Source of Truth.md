# ADR-001 Career Profile as Source of Truth

## Status

Accepted

## Context

The MVP generates multiple structured career artifacts from a single Brain Dump:

- Master CV
- Skills Library
- Achievement Library
- Career Metadata

Generating each artifact independently would duplicate processing and increase the risk of inconsistencies.

## Decision

The application will first transform the user's Brain Dump into a structured Career Profile.

The Career Profile will serve as the single source of truth for all generated artifacts in the MVP.

The initial version of the profile will contain:

- Metadata
- Skills
- Achievements
- Hero Stories

The Master CV will be generated from this profile.

## Consequences

Advantages

- One canonical representation of career data
- Consistent outputs
- Easier extension in future iterations
- Clear separation between knowledge extraction and document generation