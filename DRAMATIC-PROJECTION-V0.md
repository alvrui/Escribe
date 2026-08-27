# Dramatic Projection v0

## Purpose

This projection adds a first, deliberately narrow dramatic reading to
Taberna's map:

- **Motivation**: a supported want, need, goal, or fear of loss.
- **Conflict**: a supported opposition, blockage, collision, or incompatible
  pressure.
- **Possible cold region**: a conservative indication that there is enough
  structure to inspect but little explicit dramatic drive identified.

These are categories of a derived view. They are not new core primitives, are
not persisted, and never mutate `SharedWorld`. A cold region is not a quality
judgement and no score is calculated.

## Flow

```text
SharedWorld
    ↓
ContextResponse → AiContextPackage (request-local handles)
    ↓
OpenAI structured classification
    ↓
strict handle resolution
    ↓
DramaticProjection
    ↓
read-only map / inspector
```

The model sees handles such as `SO1` and `A1`, never persistent UUIDs. The
projection accepts no signal without evidence references. Subjects must be
StoryObjects and evidence must resolve to elements in the supplied context.
Unknown handles and wrong reference kinds are rejected.

## Authority

Signals preserve an `Open` or `Fixed` authority label. Evidence containing an
open assertion yields an Open signal; otherwise the signal must be Fixed. The
projection does not fix assertions, create Issues, resolve Issues, or turn
hypotheses into canon. Possible consequences remain outside this first
projection.

## Paco / Laura

For the Paco fixture, the intended useful readings are a motivation around
keeping the job and conflicts involving Paco's agreement with the diagnosis
while avoiding confrontation with his manager, plus the manager's insistence
on continuing a project without a clear purpose. The classifier is free to
omit any of these when the supplied evidence does not support them; it must
not invent a motivation for Laura.

The map's **Presión dramática** toggle requests this projection and marks
StoryObject nodes with restrained visual emphasis. The inspector lists the
returned motivations and conflicts before the ordinary structured facts. The
base graph remains a separate, deterministic projection.

## Limitations

- The projection currently uses an AI call when the toggle is enabled; it is
  not cached.
- The endpoint accepts dimensions for the UI contract, while the current
  classification uses the assembled narrative context rather than inventing
  dimension semantics.
- No decision, consequence, change, dramatic score, or quality score is
  inferred.
- Cold regions are returned only when the model identifies a structured area
  with weak or absent dramatic drive; Rust does not classify them from
  keywords.

## Product question

**PARTIALLY**. Motivation and conflict make the map more useful as an
attention surface when their evidence is present, but the first version still
depends on the quality and coverage of the supplied context. It deliberately
does not claim to measure whether a story is good or dramatic.

**Next real gap:** validate through manual Paco/Laura use whether the
AI-derived signals remain stable enough across repeated map openings to be a
reliable authoring aid.
