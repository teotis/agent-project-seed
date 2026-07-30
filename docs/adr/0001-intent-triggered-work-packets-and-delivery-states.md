# Keep Work Packets intent-triggered and delivery states separate

Status: accepted

The seed keeps an active Work Packet as background context unless the current
user explicitly continues, resumes, or names it. Verification, handoff artifact
generation, and deployment remain distinct states so an evidence check cannot
quietly create or externally deliver a result.

## Considered Options

- Automatically enter any active Work Packet and bundle review or delivery
  pipelines into the seed.
- Keep user intent authoritative and let projects add narrow manifests, review
  surfaces, and deployment gates only after a repeated need is proven.

## Consequences

Copied projects retain a lightweight portable core and avoid stale task context
or accidental external effects. Projects with durable artifact workflows must
define their own domain-specific evidence and enforcement.
