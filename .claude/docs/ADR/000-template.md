# ADR-[number]: [Title]

**Status**: [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]
**Date**: YYYY-MM-DD
**Deciders**: [List of people involved in the decision]
**Technical Story**: [Link to issue/story if applicable]

---

## Context

What is the issue we're facing? What forces are at play?

- Describe the problem or opportunity
- Explain the context and constraints
- List any assumptions or requirements
- Include relevant background information

**Example**: "We need to choose a database for storing user data. The system will handle 10,000+ concurrent users with complex queries and JSONB support is required."

---

## Decision

What is our decision?

State the decision clearly and concisely. Be specific about what will be done.

**Example**: "We will use PostgreSQL 16 as our primary database."

---

## Consequences

### Positive Consequences

- List the benefits of this decision
- Explain how it solves the problem
- Describe any positive side effects

**Examples**:
- Excellent JSONB support for flexible schema
- Strong community and ecosystem
- Well-understood by the team

### Negative Consequences

- List the drawbacks or tradeoffs
- Explain what we're giving up
- Describe any new problems this creates

**Examples**:
- Requires PostgreSQL-specific hosting (vs. serverless options)
- More complex to scale horizontally than NoSQL
- Additional operational overhead for backups/maintenance

### Neutral Consequences

- List observations that are neither clearly positive nor negative
- Note any facts about the decision

**Examples**:
- Requires learning PostgreSQL-specific features (JSONB, RLS)
- Will need to set up connection pooling
- Migration from other databases would be non-trivial

---

## Alternatives Considered

Document other options that were evaluated and why they were not chosen.

### Alternative 1: [Name]

**Pros**:
- [benefit 1]
- [benefit 2]

**Cons**:
- [drawback 1]
- [drawback 2]

**Why Not Chosen**:
[Clear explanation of why this option was rejected]

### Alternative 2: [Name]

**Pros**:
- [benefit 1]
- [benefit 2]

**Cons**:
- [drawback 1]
- [drawback 2]

**Why Not Chosen**:
[Clear explanation of why this option was rejected]

---

## Implementation Notes

### Immediate Actions Required

- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3

### Migration Strategy (if applicable)

Describe how existing systems will transition to this decision.

### Rollback Plan (if applicable)

Describe how to revert this decision if it proves problematic.

---

## References

- [Link to relevant documentation]
- [Link to research or blog posts]
- [Link to comparative analysis]
- [Link to proof of concept]

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Initial ADR | [Name] |
| YYYY-MM-DD | Status changed to Accepted | [Name] |

---

**Template Version**: 1.0
**Based on**: [Michael Nygard's ADR template](https://github.com/joelparkerhenderson/architecture-decision-record)
