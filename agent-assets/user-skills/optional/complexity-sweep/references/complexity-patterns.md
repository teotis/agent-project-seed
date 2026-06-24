# Complexity Pattern Catalog

Complete detection guide for all three scan levels. Each pattern includes: **signal** (when to flag), **detection method**, and **simplification direction**. This file is referenced by `SKILL.md` Step 2; read it before starting the evidence sweep.

All numeric thresholds and named smells in this catalog are **investigation triggers**, not findings. Keep a candidate only after proving comprehension cost, change coupling, bug risk, onboarding drag, broken contract, or unnecessary abstraction cost in the target codebase.

---

## Level 1: Micro (Function / Class)

### 1.1 Structural Complexity

#### Deep Nesting
- **Signal**: 3+ levels of `if`/`for`/`while`/`try`/`switch` nesting within a single function body.
- **Detection**: `grep -n "^\s{12,}(if\|for\|while\|try\|switch)" <file>` or cyclomatic complexity tool. Mental threshold: if you need to count braces to understand control flow, it's too deep.
- **Simplification**: Extract inner blocks into named functions. Use guard clauses (early return/continue) to flatten. Replace nested conditionals with lookup tables or pattern matching.
- **NOT a fix**: Moving the nesting elsewhere without reducing it. The point is reducing the reader's mental stack depth.

#### Long Function
- **Signal**: Function body > 50 lines (flag >30 for investigation). Multiple blank-line-separated blocks doing different things.
- **Detection**: `awk '/^def |^function |^func /{start=NR; name=$0} /^$/{if(NR-start>50) print name, NR-start}' <file>` — adapt regex for language.
- **Simplification**: Split into focused functions named after WHAT each block does. The original function becomes a composed orchestration or is deleted if each extract can be called independently.
- **Interpretation guard**: A long function may indicate multiple responsibilities, but generated code, protocol handling, linear orchestration, or locality requirements can justify its size. Inspect cohesion and change history before proposing a split.

#### Long Parameter List
- **Signal**: Function with >= 4 parameters. Especially flag when multiple parameters share the same type (easy to swap by accident).
- **Detection**: Regex for function signatures. In typed languages, check if consecutive params share types.
- **Simplification**: Introduce a parameter object or options struct. Split the function if the parameters serve different concerns. Use builder pattern if parameters are progressively constructed.
- **Edge case**: Well-known framework callbacks with fixed signatures are usually not worth refactoring.

#### Boolean Flag Parameters
- **Signal**: `function doThing(verbose, force, dryRun)` — booleans that switch behavior inside the function.
- **Detection**: Look for `if (flagParam)` branching at the top level of a function body.
- **Simplification**: Split into separate functions (`doThing()` and `doThingForcefully()`), or replace with an options object with named keys. Named call sites are self-documenting.
- **Why harmful**: Call sites read as `doThing(true, false, true)` — the reader must look up the signature to understand what's happening.

#### Nested Ternaries
- **Signal**: Ternary operator (`?:`) nested inside another ternary, or ternary chains spanning >1 line.
- **Detection**: `grep -n "? .* : .* ? .* :" <file>` or similar. Any ternary that requires horizontal scrolling to read.
- **Simplification**: Replace with `if`/`else if`/`else` chain, `switch`, or a lookup map. The goal is for the reader to see all branches at a glance without mentally parsing operator precedence.
- **Exception**: Simple two-branch ternaries on one line (`const label = isNew ? 'New' : 'Old'`) are fine.

#### Switch-on-Type / Instanceof Chains
- **Signal**: `switch` on a type discriminator, long `if (x instanceof A) ... else if (x instanceof B)` chains.
- **Detection**: Search for `instanceof`, `typeof` checks, or `switch` on a type field used for dispatch.
- **Simplification**: Use polymorphism (each type handles its own behavior). If you can't modify the types, use a visitor pattern or a dispatch map. Adding a new type should not require editing every switch statement.

#### God Object / Large Class
- **Signal**: Class with >10 public methods, or >300 lines. Multiple disparate responsibilities sharing the same instance state.
- **Detection**: Count public methods per class. Check if instance fields naturally cluster into groups used by different method subsets.
- **Simplification**: Split into smaller classes, each owning a subset of the fields. Extract collaborator objects. The original class may become a facade or be deleted.
- **Why harmful**: God objects make testing hard (you need the whole world to test one method) and create implicit coupling between unrelated features.

#### Feature Envy
- **Signal**: A method that calls many getters/methods on another object but few on its own `this`/`self`.
- **Detection**: In method body, count `otherObject.method()` vs `this.method()` calls. If >60% are on another object, flag it.
- **Simplification**: Move the method to the object it's envious of. Or extract the shared data into a new object that both can use.
- **Why harmful**: Feature envy scatters logic about one concept across multiple classes, making changes require touching many files.

#### Inappropriate Intimacy
- **Signal**: Two classes that access each other's private/protected/internal members. Bidirectional coupling at the field level.
- **Detection**: Check for classes that import each other's internal/private modules. In languages with access modifiers, check for `friend` declarations or reflection-based access.
- **Simplification**: Move the intimate logic into one of the classes. Extract a mediator. Introduce a proper public interface between them.
- **Why harmful**: Tight coupling means you can't change one class without understanding and potentially breaking the other.

### 1.2 Naming & Readability

#### Generic Names
- **Signal**: Names like `data`, `result`, `temp`, `val`, `item`, `info`, `obj`, `config`, `manager`, `handler`, `processor`, `util` without further qualification.
- **Detection**: `grep -n "\b(data|result|temp|val|item|info|obj)\b" <file>` — review each usage for whether the name could be more specific.
- **Simplification**: Rename to describe the CONTENT: `userProfile` not `data`, `validationErrors` not `result`, `pendingOrder` not `item`.
- **Why harmful**: Generic names force the reader to trace the variable back to its source to understand what it holds. Each trace is a cognitive tax paid by every future reader.

#### Abbreviated Names
- **Signal**: `usr`, `cfg`, `btn`, `evt`, `ctx`, `impl`, `mgr`, `svc` — abbreviations that save 2-5 characters at the cost of comprehension.
- **Detection**: Look for variable/function names with consonant clusters or missing vowels that aren't standard acronyms.
- **Simplification**: Use full words. Exception: universally recognized abbreviations in the language ecosystem (`id`, `url`, `api`, `db`, `io`, `http`, `json`, `xml`, `sql`).
- **Rule of thumb**: If you'd say the full word out loud when discussing the code, write the full word.

#### Misleading Names
- **Signal**: Function named `getX()` that also mutates state. Function named `validate()` that returns a bool but also sends an email. Function named `process()` that does anything.
- **Detection**: Read the function body. If it does something the name doesn't imply, flag it. Use `git log` to see if the name was once accurate but the function grew.
- **Simplification**: Rename to match actual behavior. If the function does two things, consider splitting it and give each part a clear name. Generic verbs such as `process()` are investigation triggers when the surrounding domain does not make their meaning clear.
- **Why harmful**: Misleading names cause bugs when callers use the function based on the name alone without reading the implementation.

#### Inconsistent Terminology
- **Signal**: Same concept called `user`, `account`, `profile`, `member` in different files. `fetch`/`get`/`retrieve`/`load` used interchangeably for the same operation.
- **Detection**: Search for synonyms across the codebase. For key domain concepts, grep all variations and check for consistency.
- **Simplification**: Pick one term per concept and rename all occurrences. Document the chosen term in project conventions. This is a grep-and-replace task, not architectural work.

#### Comments Explaining "What"
- **Signal**: `// increment counter` above `count++`. `// loop through items` above `for (const item of items)`. Any comment whose content is fully expressed by the code it describes.
- **Detection**: Read each comment. Delete it mentally. If the code is just as clear without it, flag the comment for removal. If the code is NOT clear without it, flag the CODE for renaming/restructuring.
- **Simplification**: Delete the comment. If the code needed the comment to be clear, rename variables or extract a named function instead.
- **Keep**: Comments explaining WHY. `// Retry 3 times because the upstream API is flaky under peak load` — this carries intent the code cannot express.

#### Missing Explanatory Variable
- **Signal**: Complex expression used directly in a conditional or return statement, where the reader must mentally evaluate the expression to understand what it checks.
- **Detection**: Any `if` condition spanning >1 line, or any boolean expression with >3 terms.
- **Simplification**: Extract the expression into a well-named const: `const isEligibleForDiscount = ...; if (isEligibleForDiscount) { ... }`.
- **Why helpful**: The variable name explains intent. The complex expression explains mechanics. Separating them makes both clearer.

### 1.3 Control Flow Complexity

#### Callback Hell / Deeply Nested Async
- **Signal**: 3+ levels of `.then()` chaining or nested callbacks. `async/await` inside loops without clear error boundaries.
- **Detection**: Count `.then(` calls in a single expression chain. Look for `})` patterns that close nested callbacks.
- **Simplification**: Flatten with `async/await`. Extract error handling to a wrapper. Use promise combinators (`Promise.all`, `Promise.allSettled`) for parallel work.

#### Excessive Branching
- **Signal**: Function with >10 `if`/`else if` branches, or a `switch` with >7 cases.
- **Detection**: Count conditional branches in each function body.
- **Simplification**: Use a lookup map/object/dict instead of branching. Use strategy pattern if each branch has non-trivial logic. Use polymorphism if branches correspond to types.
- **Why harmful**: Each branch is a separate execution path that needs testing. 10 branches = 10+ test cases minimum.

#### Hidden Side Effects
- **Signal**: Getter/accessor that modifies state. Function that writes to a file or calls an API without any indication in its name or return type.
- **Detection**: In functions named `get*`, `find*`, `compute*`, `check*`, `is*`, `has*`, look for any state mutation, I/O, or external service call.
- **Simplification**: Either rename to reflect the side effect, or separate the query from the command (CQRS pattern). A function called `getUser()` should never create a user as a side effect.

#### Exception Swallowing
- **Signal**: `catch (e) { }` — empty catch block. `catch (e) { console.log(e) }` — logging without handling. `except: pass` — Python's silent killer.
- **Detection**: `grep -A2 "catch\|except" <file>` and check for empty or log-only handlers.
- **Simplification**: At minimum, add a comment explaining why the exception is safe to ignore. Better: handle the specific expected exception types and let unexpected ones propagate. Best: redesign so the exception case can't occur.
- **Why harmful**: Swallowed exceptions hide bugs. When the system behaves unexpectedly, there's no trace of what went wrong.

#### Retry Without Backoff / Infinite Loop Risk
- **Signal**: `while (true)` with a break condition that depends on external state. Retry loops with fixed delays or no delays. No maximum retry count.
- **Detection**: Search for `while (true)`, `while (1)`, `for (;;)`, or retry logic without a counter.
- **Simplification**: Add a maximum retry count. Add exponential backoff for external calls. Add a circuit breaker if the downstream is consistently failing.

### 1.4 Redundancy

#### Duplicated Logic Blocks
- **Signal**: 5+ lines of code that appear in >=2 places with <20% variation.
- **Detection**: Use `grep` for similar code blocks, or a duplication detection tool (`jscpd`, `copy-paste-detector`). Manual approach: scan for similar-looking blocks when reviewing a module.
- **Simplification**: Extract to a shared function. Parameterize the variation. If the variation is too large, the blocks may not actually be duplicated — they may be similar by coincidence.
- **Why harmful**: A bug found and fixed in one copy lives on in all the others. Duplication is the enemy of consistent behavior.

#### Magic Numbers / Strings
- **Signal**: Numeric literals or string literals in code without a named constant. `if (status === 3)`, `setTimeout(fn, 5000)`, `width > 1024`.
- **Detection**: `grep -n "\b[0-9]{2,}\b" <file>` — review non-trivial numbers in non-test code. Check string literals used as keys, status codes, or configuration values.
- **Simplification**: Extract to a named constant. The name explains WHAT the value represents and WHY it's that value.
- **Exception**: 0, 1, -1 used as loop indices, array offsets, or mathematical identities. Domain-specific well-known values (HTTP 200, 404).

#### Dead Code
- **Signal**: Unreachable branches (after `return`, `throw`, `break`). Functions never called. Variables written but never read. Imports never used.
- **Detection**: Static analysis tools (tree-shaking, dead code elimination, IDE grayed-out code). Grep for function name to verify zero callers outside tests.
- **Simplification**: Delete it. Git history preserves it if needed later. Be certain it's truly dead — check dynamic dispatch, reflection, and config-driven invocation before deleting.
- **Caution**: Code that is "seldom used" (error recovery, edge cases) is not dead code. Only delete code that can NEVER execute.

#### Commented-Out Code Blocks
- **Signal**: Large blocks of code inside `/* ... */` or `//` prefixed lines. `# if False:` blocks in Python.
- **Detection**: `grep -n "^\s*//\|^\s*#" <file>` and review multi-line commented sections.
- **Simplification**: Delete them. They're preserved in git history. If they represent an alternative approach worth remembering, write a brief comment explaining the approach and why it wasn't chosen, not the full code.
- **Why harmful**: Commented-out code rots. Nobody updates it when the surrounding code changes. After 6 months, it's more misleading than useful.

#### Redundant Comments
- **Signal**: Javadoc/docstring on a getter that says "Returns the name." JSDoc that repeats the type signature. Comments that paraphrase the next line of code.
- **Detection**: Read each comment. If removing it costs the reader nothing, flag it.
- **Simplification**: Delete. If the function name is unclear, fix the name. If the behavior has non-obvious constraints (null handling, thread safety, side effects), keep only those notes.
- **Rule**: Comments should explain WHY, not WHAT. Types, function names, and variable names already explain WHAT.

### 1.5 Abstraction Smells

#### Mixed Abstraction Levels
- **Signal**: A function that mixes low-level operations (string concatenation, array index manipulation) with high-level business logic (calling services, making decisions) in the same body.
- **Detection**: In a function body, identify "high-level" lines (calling other domain functions) and "low-level" lines (direct data manipulation). If both are present, flag it.
- **Simplification**: Extract low-level operations into helper functions with descriptive names. The top-level function should read like a recipe, not a machine manual.

#### Primitive Obsession
- **Signal**: Using `string` for email, phone, URL, currency, ID. Using `int`/`float` for money, percentage, coordinate. Validating these primitives in every function that receives them.
- **Detection**: Look for repeated validation of the same primitive type. `if (email.contains('@'))` in 3 places. `if (amount < 0)` scattered everywhere.
- **Simplification**: Create a value type (class/struct) that encapsulates the validation. `Email` not `string`. `Money` not `float`. One place to validate, one place to fix bugs.
- **Why harmful**: Without value types, every function that receives the value must independently validate or trust it. Trust spreads and breaks.

#### Data Clumps
- **Signal**: Groups of 3+ parameters/fields that always appear together across function signatures. `(startDate, endDate)`, `(x, y, z)`, `(street, city, zip, country)`.
- **Detection**: Scan function signatures for repeated parameter groups. Check if any caller ever passes them independently.
- **Simplification**: Create a class/struct for the clump. The new type becomes a natural home for behavior currently scattered across the functions that take the clump.
- **Why helpful**: The clump is a concept the code is trying to express without having the vocabulary for it.

#### Refused Bequest
- **Signal**: Subclass that overrides most inherited methods with no-ops or throws `UnsupportedOperationException`. Subclass that only uses 20% of parent's interface.
- **Detection**: In class hierarchy, compare parent's public methods to child's meaningful overrides. If >50% are no-ops or unsupported, flag it.
- **Simplification**: Replace inheritance with composition. Extract the actually-used interface. The subclass probably isn't truly "is-a" the parent.
- **Why harmful**: It violates the Liskov substitution principle. Code that expects a Parent may break when given this Child.

#### Speculative Generality
- **Signal**: Abstract classes with one concrete implementation. Interfaces created "in case we need to swap implementations later." Plugin systems for 2 plugins. Factory factories.
- **Detection**: Count implementations per interface/abstract class. Count abstract methods that are overridden in only one way. Check git log: was the abstraction added before or after the concrete need?
- **Simplification**: Remove the abstraction and use the concrete implementation directly. If a second implementation arrives later, introduce the abstraction then — with two real examples, the right abstraction will be clearer.
- **Why harmful**: Speculative abstractions are bets placed with future readers' comprehension budget. Most of those bets lose.

---

## Level 2: Meso (Module / Package)

### 2.1 Coupling

#### Circular Dependencies
- **Signal**: Module A imports Module B, and Module B imports Module A (directly or through intermediate modules A→B→C→A).
- **Detection**: Dependency graph tools (`madge`, `dependency-cruiser`, `jdeps`). Manual: trace imports from a suspected module and see if you loop back.
- **Simplification**: Break the cycle by: (1) extracting the shared concern into a third module C that both A and B import, (2) inverting one dependency through an interface, (3) merging A and B if they're actually one concept artificially split.
- **Why harmful**: Circular deps make modules impossible to understand in isolation. Testing A requires B, which requires A. Changes ripple unpredictably.

#### Excessive Imports
- **Signal**: File with 20+ import statements. Especially when imports come from many different packages/directories.
- **Detection**: Count `import`/`require`/`use` statements per file. Sort by count, flag top 5%.
- **Simplification**: The file likely has too many responsibilities. Split it. If many imports are from the same package, the package boundary may be wrong. If many imports are for a single feature, extract a coordinator module.
- **Why harmful**: Each import is a dependency. High import count means the file is coupled to many things and will change when any of them change.

#### Import-Internals
- **Signal**: Module A imports from Module B's `internal/`, `_private/`, or `__tests__/` directory. Or imports a symbol prefixed with `_` (convention for private).
- **Detection**: Check import paths for `internal`, `private`, `impl`, `_` prefixed symbols being accessed from outside.
- **Simplification**: Either: (1) make the needed functionality part of B's public API if it's genuinely needed externally, (2) move the consuming code into B, or (3) extract the shared need into a third module.
- **Why harmful**: Internal imports break encapsulation. B's authors thought they could change that code freely; external consumers will break.

#### Shotgun Surgery Pattern
- **Signal**: Adding a simple feature requires touching >=5 files across >=3 modules. One conceptual change scatters across the codebase.
- **Detection**: For recent features in git log, count files touched per feature commit. Check if changes cluster by module or scatter.
- **Simplification**: The scattered logic likely belongs together in a single module. Co-locate related behavior. This is often a sign that the module boundaries were drawn along technical layers (controllers, services, repositories) rather than domain features.
- **Why harmful**: Shotgun surgery makes every feature change expensive and risky. It's easy to miss one of the files that needs updating.

#### Divergent Change Pattern
- **Signal**: A single module that changes for many different reasons. A module whose recent commits touch auth, billing, notifications, and UI formatting.
- **Detection**: For a given module, classify the last 20 commits by concern area. If >3 distinct concerns appear, flag it.
- **Simplification**: Split the module along concern boundaries. Each new module should have a single reason to change. This is the flip side of shotgun surgery.
- **Why harmful**: A module with many reasons to change is a merge conflict magnet and makes it hard for different teams to work independently.

### 2.2 Cohesion

#### Scattered Feature Logic
- **Signal**: A single user-facing feature (e.g., "password reset") whose implementation touches 8+ files across 4+ directories, with no single file serving as an obvious entry point.
- **Detection**: Pick a feature. Trace it end-to-end. Count files touched. Draw a diagram — if the feature's implementation graph looks like spaghetti, flag it.
- **Simplification**: Create a feature module that orchestrates the feature. The feature module imports from domain modules; domain modules don't know about specific features. This is often a move from layered architecture to feature-based architecture.

#### God Module / Kitchen Sink Package
- **Signal**: A `utils/`, `common/`, `helpers/`, or `shared/` directory with 30+ files covering unrelated concerns. Files whose names contain "misc", "util", "helper", "common".
- **Detection**: List files in `utils/` or `common/` directories. Classify each file by concern. If >3 distinct concerns, flag it.
- **Simplification**: Move each file to the package that owns its concern. `date-utils.ts` → `datetime/` package. `string-utils.ts` → `text/` package. The `utils/` directory should trend toward empty.
- **Why harmful**: A broad utilities directory can weaken ownership and discoverability when unrelated concepts accumulate there. A cohesive, well-owned utility package is not inherently problematic.

#### Mixed Unrelated Concerns
- **Signal**: A file that handles both HTTP routing, database queries, and email sending. A file that contains both UI rendering and business logic.
- **Detection**: Scan file contents for imports from very different domains (e.g., `react` AND `sqlalchemy` in the same file). Check if file name suggests one thing but content includes others.
- **Simplification**: Split into separate files by concern. Each file should be about one thing.

#### Config Duplication
- **Signal**: The same configuration value (`API_TIMEOUT`, `MAX_RETRIES`, `DEFAULT_PAGE_SIZE`) defined in 3+ files. Environment variable names inconsistently referenced.
- **Detection**: `grep -r "MAX_RETRIES\|API_TIMEOUT\|DEFAULT_" --include="*.ts\|*.js\|*.py\|*.go\|*.yaml\|*.json" .` — look for duplicated constants.
- **Simplification**: Centralize in a single config module. Use typed configuration (not raw `process.env` scattered everywhere). One source of truth for each config value.

### 2.3 Layering

#### Pass-Through Layers
- **Signal**: A function/method that does nothing but delegate to another function with the same signature. `getUser(id) { return userRepository.getUser(id); }`. Service layer that adds no transformation, validation, or orchestration.
- **Detection**: For each public function, count lines of logic (exclude delegation). If it's just a delegation call, flag it. Check if the layer adds: validation, transformation, error handling, caching, logging, transaction management, or authorization. If none, it's pass-through.
- **Simplification**: Remove the pass-through and let callers use the underlying function directly. If the layer exists for "future flexibility", see Speculative Generality above.
- **Why harmful**: Pass-through layers add indirection without adding value. They make the call stack deeper without making the code clearer.

#### Unnecessary Indirection
- **Signal**: Factory → Builder → Strategy → Implementation chain where only one Strategy ever exists. Interface with exactly one non-test implementation. DI container wiring for a dependency that never changes.
- **Detection**: Count implementations per interface. Count usages of factory methods. If the answer is 1, flag it.
- **Simplification**: Use the concrete class directly. Inline the factory. Remove the interface. The indirection can be reintroduced when a second implementation creates a real design choice.

#### Interface With Single Implementation
- **Signal**: `interface IUserService` with exactly one `class UserServiceImpl`. Every call site uses the interface type.
- **Detection**: Find all `interface`/`abstract class`/`protocol` declarations. Count implementations. Flag singles.
- **Simplification**: Evaluate whether the interface protects a real boundary, public contract, test seam, platform variant, dependency inversion rule, or planned migration. Remove it only when its abstraction cost exceeds demonstrated value.
- **Exception**: Published APIs, architecture boundaries, generated bindings, platform variants, test isolation, or ecosystem conventions may justify one current implementation.

#### Unbalanced Abstraction Depth
- **Signal**: Module A has 5 abstraction layers (controller → service → repository → dao → connector). Module B in the same project has 1 (controller → database). The extra layers in A exist because of a framework template, not because A's logic is more complex.
- **Detection**: Count abstraction layers per module. Compare. If the depth difference can't be explained by different complexity requirements, flag it.
- **Simplification**: Normalize to the depth that matches actual complexity. Remove layers that don't add value. Consistency in structure reduces cognitive switching cost between modules.

### 2.4 Duplication at Scale

#### Duplicated Validation
- **Signal**: The same validation logic for email, phone, date range appearing in frontend, backend, and admin tool. Each implementation slightly different.
- **Detection**: Search for similar regex patterns or validation rules across the codebase. Check frontend, backend, and worker directories separately.
- **Simplification**: Create a shared validation module. If cross-platform (frontend/backend), publish as a shared package or use a schema language (JSON Schema, Zod, Pydantic) that can be shared.

#### Duplicated DTOs / Types
- **Signal**: `UserDto`, `UserResponse`, `UserEntity`, `UserModel` defined in different layers with mostly overlapping fields. Conversion functions between them.
- **Detection**: Search for struct/class/interface names that share a root word but differ in suffix. Check if field definitions overlap >70%.
- **Simplification**: Consolidate to fewer representations. Often, the DTO and the Entity don't need to be separate — the distinction was created by a framework convention, not by actual need.

#### Copy-Paste Across Modules
- **Signal**: Two files in different modules with >60% similar content. Often happens when a feature was "cloned" for a new use case.
- **Detection**: Use a duplication detection tool (`jscpd`, `copy-paste-detector`). Manual: when you see similar code in two places, diff the files.
- **Simplification**: Extract the shared logic to a common module. Delete the copies. If the copies have diverged significantly, they may be different things that happen to look similar — use judgment.

#### Parallel Class Hierarchies
- **Signal**: For every `Animal` subclass (`Dog`, `Cat`), there's a corresponding `AnimalFactory` subclass (`DogFactory`, `CatFactory`). Adding a new domain class requires adding N corresponding infrastructure classes.
- **Detection**: Look for class/interface names that follow a pattern: `XxxController` ↔ `XxxService` ↔ `XxxRepository`. If each layer has the same set of names, flag it.
- **Simplification**: Generify. A single `Repository<T>` can handle any entity. A single `CrudController<T>` can handle any CRUD. Don't create per-entity infrastructure unless the entity has genuinely different behavior.

---

## Level 3: Macro (Architecture)

### 3.1 Data Flow

#### Retorted Data Paths
- **Signal**: Data passes through 4+ layers where each layer reads a value, does nothing to it, and passes it to the next. The data's journey is longer than its purpose requires.
- **Detection**: Pick a piece of data (e.g., a user preference). Trace it from source to use. Count layers. If it passes through layers that don't transform, validate, or persist it, those layers are迂回.
- **Simplification**: Shorten the path. Let the consumer access the source more directly. Remove intermediate layers that don't add value.
- **Why harmful**: Each pass-through layer is a place where the data could be corrupted, lost, or misunderstood. Longer paths mean harder debugging.

#### Unnecessary Serialization Chains
- **Signal**: JSON → Object → JSON → Object → JSON, where the intermediate Object forms exist only to satisfy a type system or framework convention.
- **Detection**: Count `JSON.parse` / `JSON.stringify` pairs or their equivalents. If serialization/deserialization happens multiple times for the same payload within a single request lifecycle, flag it.
- **Simplification**: Pass the parsed object through. Only serialize at the final boundary (HTTP response, message queue, file write).

#### Data Passing Without Transformation
- **Signal**: A function receives a data object, calls another function with the same object, which calls another function with the same object. Each layer "in case we need to transform it later."
- **Detection**: Track a data object through the call stack. If it arrives at the bottom unchanged, all intermediate layers that only passed it along are suspect.
- **Simplification**: Remove intermediate functions that don't add value. Let the top-level caller reach the bottom-level function more directly, or consolidate the intermediate functions into one.

### 3.2 Orchestration Bloat

#### Coordinator Without Value
- **Signal**: A "coordinator" or "orchestrator" class whose logic is: `a.doX(); b.doY(); return combine(a, b);` — no conditional logic, no error recovery, no transaction management. A 5-line function wrapped in a class.
- **Detection**: Review all classes named `*Coordinator`, `*Orchestrator`, `*Manager`, `*Facade`. If the body is just sequential delegation without branching or error handling, flag it.
- **Simplification**: Inline the orchestration into the caller. Or keep it as a function (not a class) if the caller doesn't want to know about a and b.

#### God Orchestrator
- **Signal**: A single orchestrator that touches 20+ services, has 500+ lines, and knows about every module in the system. The orchestrator IS the architecture.
- **Detection**: Find the largest file in the project. If it's an orchestrator/controller/service that imports from everything, flag it.
- **Simplification**: Split by feature or by process phase. Each sub-orchestrator handles one workflow. The top level composes them. Better: use events/messages so modules coordinate without a central orchestrator.

#### Scattered Workflow State
- **Signal**: The state of a multi-step workflow is split across database rows, Redis keys, environment variables, and in-memory caches, with no single place documenting the valid states and transitions.
- **Detection**: Search for status fields, state machines, or workflow step tracking across the codebase. If the valid transitions are not defined in one place, flag it.
- **Simplification**: Define a state machine (as code or config) that is the single source of truth for states and transitions. All workflow code references this machine.

### 3.3 Boundary Problems

#### Wrong Boundaries (Glue > Isolation)
- **Signal**: Two modules separated by a formal boundary (separate package, separate build, API contract) where the boundary maintenance cost (serialization, versioning, deployment coordination, contract testing) exceeds the coupling it prevents.
- **Detection**: For each module boundary, count: (1) lines of boundary code (serialization, contracts, versioning), (2) frequency of coordinated changes across the boundary. If boundary code > business logic, or coordinated changes are weekly, flag it.
- **Simplification**: Merge the modules. A single well-structured module is better than two tightly-coupled modules with a formal boundary between them.

#### Missing Boundaries
- **Signal**: Everything is in one module/package. All code can import all other code. No enforced dependency direction.
- **Detection**: If the project has no `internal/` directories, no package-level access modifiers, and everything is exported, flag it.
- **Simplification**: Define module boundaries around domain concepts. Use `internal/` directories or package-level visibility to enforce them. Start with 3-5 coarse modules; don't over-split.

#### Boundary Violations
- **Signal**: Module A's internal types appear in Module B's public API. Module B's tests import Module A's test fixtures. A dependency arrow points in a direction the architecture document says it shouldn't.
- **Detection**: Check if declared architecture (in `AGENTS.md`, `ARCHITECTURE.md`, or similar) matches actual import graph. Flag violations.
- **Simplification**: Either fix the code to match the intended architecture, or update the architecture document to match reality. Half the value is making the mismatch visible.

### 3.4 Abstraction at Scale

#### Over-Abstraction
- **Signal**: 5+ abstraction layers where 2 would suffice. Each layer exists "for flexibility" but the system has never swapped any implementation. The architecture was designed for a scale that never arrived.
- **Detection**: Count abstraction layers from entry point to data store. Compare with the actual complexity of the business logic. If abstraction layers > business logic layers, flag it.
- **Simplification**: Collapse adjacent layers that don't add independent value. The right number of layers is the number that makes each layer's responsibility clear and singular.

#### Under-Abstraction
- **Signal**: Domain concepts that exist only as comments, variable naming conventions, or tribal knowledge. Code that manipulates raw data structures where a domain type should exist.
- **Detection**: Look for repeated patterns of validating/transforming the same raw data. Look for functions that take many primitives (see Primitive Obsession) at module boundaries.
- **Simplification**: Introduce domain types at the module boundary. They serve as both documentation and validation — the type system enforces what comments can only suggest.

#### Leaky Abstractions
- **Signal**: Calling code must understand the implementation details of a dependency to use it correctly. Database connection handling visible in business logic. HTTP status codes exposed through "abstracted" API clients.
- **Detection**: In high-level code, look for imports/concepts from lower layers (SQL keywords in service layer, HTTP concepts in UI layer, filesystem paths in business logic).
- **Simplification**: Create a proper abstraction layer that fully encapsulates the low-level concern. If the low-level concept genuinely needs to be visible, the abstraction is wrong — redesign it or remove it and be explicit about the dependency.

---

## Tooling Quick Reference

| Language | Complexity | Duplication | Dependencies | Dead Code |
|---|---|---|---|---|
| TypeScript/JS | `eslint` (complexity, max-lines, max-depth) | `jscpd` | `madge`, `dependency-cruiser` | `ts-prune`, `knip` |
| Python | `radon`, `wily`, `flake8` (mccabe) | `jscpd` | `pydeps`, `import-linter` | `vulture`, `dead` |
| Go | `gocyclo`, `gocognit` | `jscpd` | `goda` | `deadcode` |
| Java/Kotlin | `SonarQube`, `Checkstyle` | `jscpd` | `jdeps`, `ArchUnit` | IDE inspections |
| Ruby | `flog`, `reek` | `flay` | `bundle --visualize` | `debride` |
| Rust | `clippy` (cognitive-complexity) | `jscpd` | `cargo-modules` | `warn(dead_code)` |
| Multi-language | `SonarQube`, `CodeClimate` | `jscpd` | — | — |

When these tools are available, run them during evidence collection and include their output in the verification ledger. When they're not available, do manual detection using the signals above.
