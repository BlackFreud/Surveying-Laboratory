# AGENTS.md

Guidance for AI coding agents working with code in this repository.

## General Principles

- Generate concise, maintainable solutions for new modules or code.
- Avoid over-engineering and unnecessary abstractions.
- Identify oversized files or complex modules that may require refactoring.
- Follow existing repository patterns, conventions, and architecture.
- Avoid introducing syntax, style, or patterns inconsistent with the codebase.
- Consider potential bugs, security implications, and the blast radius of changes.
- Do not use emojis or special characters in comments.
- Comments must be one sentence and explain only necessary context.
- Maintain `/docs/activity-log.md` when making significant changes for future reference.
- Review existing files before modifying, refactoring, or restructuring code.
- Do not execute large-scale changes blindly; explain the approach before major modifications.
- Markdown files must use kebab-case naming.

Examples:
- good: `database-migration-plan.md`
- bad: `DatabaseMigrationPlan.md`

---

## Code Quality

When implementing changes:

- Choose appropriate data structures and algorithms.
- Prefer simple solutions over unnecessary complexity.
- Follow the principle of least privilege.
- Avoid exposing unnecessary data.
- Do not introduce external libraries unless clearly justified.
- Use versions specified by the project's dependency files.
- Avoid duplicate code unless duplication improves readability or maintainability.
- Preserve backward compatibility unless explicitly requested otherwise.

Before adding dependencies:

1. Check existing dependencies.
2. Confirm the package is actively maintained.
3. Verify package source and security.
4. Confirm compatibility with project versions.

---

## Development Workflow

Before modifying code:

1. Inspect relevant files.
2. Understand current architecture and patterns.
3. Identify possible side effects.
4. Explain the proposed approach for major changes.

After modifications:

- Run available tests.
- Run linting or formatting tools when available.
- Verify that changes do not introduce obvious regressions.

---

## Version Control

Git rules:

- Commit after significant completed changes.
- Use clear, descriptive commit messages.
- Keep commits focused and atomic.
- Never automatically push changes to remote branches.
- Do not automatically commit activity logs or documentation changes.
- Only access approved repositories:


<REPO_ALLOWLIST>


---

## AI Restrictions

Never include or request:

- Customer personal information:
  - names
  - contact details
  - account numbers
  - transaction information

unless an explicit approved exemption exists.

Never expose:

- passwords
- API keys
- authentication tokens
- secrets
- database connection strings

Before installing packages:

- Verify package source.
- Confirm package safety.
- Use only approved package registries:


<PACKAGE_REGISTRY_HOST>


---

## Change Management

For significant changes:

- Explain what will change.
- Explain why the change is needed.
- Identify affected files.
- Identify possible risks.
- Wait for confirmation before destructive operations.

## Repository Audit Rules

When reviewing this repository:

Check:

- Architecture consistency
- Security vulnerabilities
- Dependency risks
- Duplicate logic
- Dead code
- Error handling
- Performance issues
- Test coverage gaps
- Documentation gaps

Prioritize findings by:

1. Critical security issues
2. Bugs affecting users
3. Maintainability problems
4. Performance concerns
5. Code style improvements