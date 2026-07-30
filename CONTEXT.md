# Agent Project Lifecycle

This context defines the portable lifecycle language shared by projects copied
from this scaffold. Project-specific contexts may add their own terms without
changing these authorization boundaries.

## Language

**Work Packet**:
An optional task-local control surface for complex, dependent work. It is active
for an agent only when the current user explicitly continues, resumes, or names it.
_Avoid_: active-task marker, background task

**Verification**:
Evidence that a stated behavior or contract holds; it may produce disposable
local output but does not itself prepare delivery or change external state.
_Avoid_: delivery, deployment

**Handoff artifact**:
A deliberately generated result prepared for user review or transfer. It stays
separate from the disposable outputs that verification may create.
_Avoid_: test output, build byproduct

**Deployment**:
An externally effective action that makes a result active for a user, device,
service, or public audience.
_Avoid_: verification, handoff artifact generation
