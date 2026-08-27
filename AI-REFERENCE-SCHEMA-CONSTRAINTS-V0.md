# AI Reference Schema Constraints v0

## Boundary

Taberna keeps persistent identity in the domain (`StoryObject:<uuid>`,
`Assertion:<uuid>`, and so on), but does not expose those identities to the
model. An `AiContextPackage` gives the model deterministic, request-local
handles such as `SO1`, `A1` and `I1`.

The schema is now generated from the package before each operation that has
known references. Existing-reference fields are enumerated with the handles
that are actually present. A handle from another namespace, a UUID, or a
bootstrap local reference such as `object_4` is not a representable value in
those fields whenever the valid set is known.

In an empty world, the contribution schema removes the `existing_target`
alternative for assertion targets. A new object can therefore be proposed
with `new_story_object: "object_1"`, but there is no existing StoryObject
handle for the model to copy.

In a populated world, the same field can contain only the enumerated existing
handles. A mixed contribution remains expressible with, for example,
`existing_target: "SO1"` and `new_story_object: "object_1"`.

## Two kinds of validation

| Knowledge available before the call | Validation boundary |
| --- | --- |
| Existing handles in the context | Dynamic JSON Schema enum |
| Local references declared elsewhere in the same response | Rust response validation |

JSON Schema cannot, without making the contract unnecessarily large, prove
that every `new_story_object` value appears in the same response's
`story_objects` array. Rust continues to validate that relationship and
rejects unknown or duplicate local references.

The schema constraints are applied to contribution interpretation, evaluation,
authorial decisions and Socrates. The same handle-only policy remains in the
natural-language contracts for all AI operations. No persistent UUID is
generated or accepted at the AI boundary.

## Empty-world bootstrap

The first sentence may create an authorized StoryObject and assertions about
it. The model supplies only a temporary local reference. Governed application
creates the real UUID and resolves the local reference atomically. The local
name never enters `SharedWorld`, persistence, or a subsequent AI context.

## Failure behavior

Strict resolution is unchanged. A handle that bypasses the schema is rejected
as an unknown AI reference handle; it is never repaired by guessing a UUID or
by converting `object_N` into `SO_N`.

The schema is a structural defense, not a semantic selector. It prevents
known-invalid namespaces from being emitted, while the existing domain and
response validators retain authority over meaning, target kind, provenance,
and same-output integrity.
