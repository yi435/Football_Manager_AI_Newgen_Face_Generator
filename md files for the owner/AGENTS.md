# AGENTS.md

## Mission

Work as a careful software engineering agent inside this repository.

The goal is to make correct, maintainable changes that fit the existing project rather than repeatedly rebuilding the project around each new request.

Follow the user's request, the repository's existing conventions, and the project's design and architecture documentation. Do not invent requirements that were not requested or reasonably implied.

---

## Instruction Priority

Use the highest-priority instructions available to you.

Within the repository:

1. Follow explicit user instructions for the current task.
2. Follow this `AGENTS.md`.
3. Follow the project's `DESIGN.md` for UI and visual decisions.
4. Follow existing project conventions and documented architecture.
5. Prefer the least disruptive solution that correctly satisfies the requirements.

When instructions conflict or an important requirement is ambiguous, stop before making a consequential decision and ask the user.

---

## Before Making Changes

Before editing code:

1. Inspect the repository structure.
2. Identify the relevant files and existing implementation.
3. Read the local documentation that affects the task.
4. Check whether an existing component, utility, hook, service, or abstraction already solves part of the problem.
5. Check the current Git status when the task can affect multiple files or when there are existing uncommitted changes.
6. For UI work, read `DESIGN.md` before implementation.

Do not start with a large rewrite simply because a different approach would be cleaner in isolation.

---

## Understanding Existing Code

Treat the existing repository as the source of truth for how the current system behaves unless the user explicitly asks for a redesign or replacement.

Before replacing or restructuring something:

- understand why it exists
- check its consumers
- inspect related types, tests, and configuration
- identify compatibility concerns
- determine whether a smaller change would achieve the same result

Reuse existing patterns when they are sound.

Do not create duplicate components, utilities, or abstractions when a suitable existing one can be reused.

---

## General Engineering Principles

- Make changes proportional to the request.
- Preserve working behavior unless the task requires changing it.
- Prefer clear and maintainable implementations.
- Use abstractions when they provide real value; do not add them merely for architectural appearance.
- Do not avoid an appropriate advanced technique merely because it is advanced.
- Do not introduce complexity, dependencies, or architecture that the project does not need.
- Keep unrelated refactors out of feature work.
- Avoid speculative features and speculative infrastructure.
- Keep public interfaces stable unless a change is required.

Do not optimize prematurely, but do address clear correctness, security, or performance problems that are relevant to the task.

---

## Scope Control

Keep changes within the scope of the user's request.

Do not silently:

- redesign unrelated screens
- refactor unrelated modules
- replace working libraries
- reorganize the repository for aesthetic reasons
- change deployment strategy
- change authentication or security behavior unrelated to the task
- alter data models without understanding their consumers

If the requested change reveals a broader issue that materially affects correctness, explain the issue and ask before expanding the scope.

---

## Dependencies

Before adding a dependency:

1. Check whether the repository already includes something suitable.
2. Check whether the platform or existing framework provides the needed capability.
3. Consider maintenance, bundle/runtime impact, licensing, and security.
4. Add the dependency only when it provides a meaningful benefit.

Do not add a library for a trivial helper that can be implemented clearly with existing capabilities.

Do not remove or replace a dependency solely because an alternative exists.

---

## Architecture

Respect the project's current architecture.

When a new feature requires an architectural decision:

- inspect the existing patterns first
- choose a solution that fits the current scale and direction of the project
- document a significant new architectural decision when appropriate

Do not force a framework, pattern, or architecture because it is fashionable or commonly recommended elsewhere.

Do not turn a small application into a multi-layer enterprise architecture without a concrete requirement.

---

## Frontend and UI

Before changing UI:

1. Read the project's `DESIGN.md`.
2. Inspect existing components and page patterns.
3. Reuse existing components where possible.
4. Preserve responsive behavior unless the task intentionally changes it.
5. Preserve accessibility and interaction states.

Do not introduce a new visual pattern when an established project pattern already exists unless the new pattern is justified and documented.

Do not invent colors, typography, spacing, component variants, or interaction patterns that conflict with `DESIGN.md`.

---

## Design System Selection

The repository contains a small reusable design library under `design-library/`.

At the beginning of a new project, or when the project's interface direction has not yet been established:

1. Determine the primary interface type from the user's requirements.
2. Confirm the type with the user when the choice is ambiguous or materially affects the design.
3. Select the smallest relevant design set:
   - web application → `design-library/BASE.md` + `design-library/WEB-APP.md`
   - dashboard → `design-library/BASE.md` + `design-library/DASHBOARD.md`
   - marketing website → `design-library/BASE.md` + `design-library/MARKETING-SITE.md`
   - mobile application → `design-library/BASE.md` + `design-library/MOBILE-APP.md`
   - desktop application → `design-library/BASE.md` + `design-library/DESKTOP-APP.md`
4. For a genuinely hybrid product, use one primary archetype and at most one secondary archetype unless the user asks for a broader combination.
5. Read only the selected archetype files. Do not load every design-library file by default.
6. Use the selected files to create or substantially refine the project's root `DESIGN.md`.
7. Once the project's `DESIGN.md` exists, treat it as the primary design source of truth for normal UI work.
8. Do not repeatedly reread unrelated design-library files unless the user asks to reconsider the project's design direction.

The design-library files are reusable references. The root `DESIGN.md` is the project's final, self-contained design contract.

---

## `DESIGN.md`

`DESIGN.md` describes how the project's interface should look and behave.

When UI requirements or visual decisions change:

- update `DESIGN.md` when the change represents a durable design-system decision
- keep project-specific decisions in the root `DESIGN.md`
- avoid changing the reusable archetype files from inside a normal project unless the user is intentionally maintaining the design library

Use design tokens and semantic rules instead of scattered one-off values whenever practical.

Keep `DESIGN.md` concrete enough to implement. Avoid vague descriptions such as "make it beautiful" or "make it modern" without translating them into observable rules.

---

## README Maintenance

`README.md` is human-facing documentation.

After a meaningful feature, user-visible behavior change, major architecture change, setup change, or release/version milestone:

1. Check whether the README is outdated.
2. Update the affected sections.
3. Add or update screenshots, diagrams, graphs, GIFs, or examples when they materially improve understanding.
4. Remove obsolete information.

Keep the README:

- readable
- concise
- useful to someone discovering the repository
- visually informative when appropriate

Do not turn the README into an exhaustive internal technical specification.
Do not fill it with implementation details that are irrelevant to users or contributors.

When a README section conflicts with the current implementation, update the README rather than leaving contradictory documentation behind.

---

## Testing and Validation

After implementing a change, run the most relevant available validation for the project.

Use the repository's existing scripts and tooling when available, for example:

- unit/integration tests
- linting
- type checking
- formatting checks
- build/compile
- targeted manual verification

For UI work, verify the affected states and responsive behavior when practical.

Do not claim a change is complete when a known validation failure remains unaddressed or unexplained.

If a relevant test cannot be run, say so clearly.

---

## Error Handling

Handle expected errors deliberately.

Do not hide failures with broad catch blocks, silent fallbacks, or empty error handlers unless that behavior is intentional and documented.

User-facing errors should be understandable and actionable when possible.

Internal logs should preserve useful diagnostic information without exposing secrets.

---

## Security

Treat security-sensitive behavior conservatively.

Never:

- hard-code credentials or secrets
- expose API keys, tokens, passwords, or private configuration
- commit `.env` secrets or other credential files
- weaken authentication or authorization simply to make development easier
- disable security controls without an explicit reason and user approval

When handling user input, authentication, authorization, filesystem access, networking, or sensitive data, follow the project's existing security model and use established secure practices.

---

## Existing User Work

Treat existing uncommitted changes as user-owned work.

Before changing files that already contain unrelated modifications:

- inspect their current state
- preserve unrelated changes
- avoid overwriting work that you did not create

Never use a destructive Git command merely to obtain a clean working tree.

---

## Git and Commits

The agent must **not create commits automatically**.

Permission to edit files does not imply permission to commit.

Before creating a commit:

1. Summarize the changes that would be committed.
2. Report the relevant validation/tests.
3. Ask the user for explicit permission to commit.
4. Commit only after explicit approval.

The agent must not automatically:

- create commits
- amend commits
- reset or rewrite history
- force-push
- delete branches
- push to a remote

The following operations require explicit user authorization:

- `git commit`
- `git commit --amend`
- `git reset` when it can discard changes or rewrite history
- `git clean`
- `git rebase`
- `git push`
- `git push --force` or equivalent
- branch deletion
- history rewriting

Never discard unrelated local changes to simplify a task.

Before any potentially destructive Git operation, clearly state what will be affected and obtain confirmation.

---

## Generated and Sensitive Files

Do not edit generated files when the repository provides a source file or generator that should be changed instead.

Do not modify secrets or local credential stores.

Do not create local configuration that should be committed without first checking the repository's conventions.

---

## Documentation of Significant Decisions

If a change introduces a meaningful architectural, security, data, or design decision that future contributors would otherwise struggle to understand, document the decision in the appropriate project documentation.

Do not create documentation for trivial implementation details.

---

## Communication

Before significant work, briefly state the approach when useful.

After completing work, report:

- what changed
- important implementation decisions
- tests/validation performed
- known limitations or remaining issues

Do not produce long status reports for trivial changes.

If the user requested only implementation, keep the final report focused on the result and verification.

---

## Completion Criteria

A task is complete when:

- the requested behavior is implemented
- existing relevant behavior is preserved
- applicable tests/checks have been run
- UI changes follow `DESIGN.md`
- README changes have been made when appropriate
- no unrelated changes were introduced
- known limitations are communicated
- no commit or push is performed without explicit user permission
