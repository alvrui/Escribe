# Graph / Dramatic Composition v1

## Hierarchy

The Map composes three independent derived layers:

1. `GraphProjection` shows structural nodes and relations.
2. Its issue topology shows where pending attention is attached.
3. `DramaticProjection` adds explicit motivations, conflicts, and possible
   cold regions.

The frontend composes these payloads for reading only. None is a new source
of truth and none mutates `SharedWorld`.

## Visual reading

The base node keeps its identity and size. `connection_count` continues to
mean structural density, not dramatic importance. When **Presión dramática**
is enabled, small markers are added around nodes:

- `◆` motivation;
- `⚡` conflict;
- `⚠` pending issue.

Tooltips expose counts, while the inspector exposes the returned summaries.
Cold regions are highlighted only when explicitly returned by
`DramaticProjection`; the browser never derives them from absence.

Selecting a node dims unrelated graph elements without changing positions.
The inspector presents related elements as clickable chips, then
motivations, conflicts, possible cold-region explanations, pending issues,
and finally the existing structured evidence. Selecting an edge continues to
show its relation and evidence and also shows dramatic signals only when
their explicit subjects touch that edge.

## Paco / Laura observation

The real Paco/Laura validation produced three motivations and one conflict,
with valid evidence and authority states. In the composition this gives the
author a quick distinction between a character with an explicit drive, one
involved in conflict, and ordinary structural connections. Laura is not
assigned a motivation by the frontend: it displays only what the projection
returns.

## Limitations

- Enabling the toggle requests the existing dramatic projection once; there
  is no cache yet.
- Graph geometry remains structural and does not encode dramatic scores.
- The UI does not infer decisions, consequences, change, quality, or
  importance.
- Empty or weakly connected nodes are not cold unless the AI projection
  explicitly returns a cold region.
- Evidence and authority remain available structurally, but the frontend
  does not yet offer a complete provenance browser.

## Product question

**YES, WITH WATCH ITEMS.** The composition makes it faster to see who wants
something, where pressure is present, and where issues gather without making
the map claim to measure story quality. Its usefulness still depends on the
coverage and stability of the existing `DramaticProjection`.

**Next real gap:** observe repeated use with a larger real story to determine
whether the AI-derived dramatic layer is stable enough for navigation rather
than merely useful as an occasional reading.
