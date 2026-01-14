<!--
=============================================================================
SYNC IMPACT REPORT
=============================================================================
Version change: N/A → 1.0.0 (Initial constitution)
Modified principles: None (new constitution)
Added sections:
  - Core Principles (4 principles)
  - Quality Gates
  - Development Workflow
  - Governance
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md: ✅ Compatible (Success Criteria aligns with performance principle)
  - .specify/templates/tasks-template.md: ✅ Compatible (test-first workflow, checkpoints align)
Follow-up TODOs: None
=============================================================================
-->

# Nestlé HR Assistant Constitution

## Core Principles

### I. Code Quality

All code contributions MUST adhere to established quality standards that ensure
maintainability, readability, and reliability across the entire codebase.

**Non-Negotiable Rules:**

- **Single Responsibility**: Each module, class, and function MUST have one clearly
  defined purpose. Functions exceeding 50 lines SHOULD be refactored.
- **Consistent Style**: All Python code MUST follow PEP 8 style guidelines. Linting
  (flake8/ruff) and formatting (black) MUST pass before merge.
- **Type Annotations**: All public functions and methods MUST include type hints.
  Internal functions SHOULD include type hints for non-trivial signatures.
- **Documentation**: Public APIs MUST have docstrings. Complex business logic MUST
  include inline comments explaining the "why", not the "what".
- **No Dead Code**: Unused imports, variables, and functions MUST be removed. No
  commented-out code blocks permitted in production.
- **Dependency Management**: All dependencies MUST be pinned to specific versions
  in requirements.txt. New dependencies require justification.

**Rationale**: A conversational AI system handling HR policies must be trustworthy.
Clean, well-documented code ensures auditability and enables safe iteration.

### II. Testing Standards

Testing is a first-class activity. All features MUST be verifiable through automated
tests before deployment.

**Non-Negotiable Rules:**

- **Test Coverage Threshold**: New code MUST achieve minimum 80% line coverage.
  Critical paths (RAG retrieval, response generation) MUST achieve 90% coverage.
- **Test Pyramid**: Unit tests MUST form the base (fast, isolated). Integration
  tests MUST verify component interactions. End-to-end tests SHOULD cover critical
  user journeys.
- **Test Independence**: Each test MUST be independently runnable. Tests MUST NOT
  depend on execution order or shared mutable state.
- **Meaningful Assertions**: Tests MUST assert behavior, not implementation details.
  Each test MUST have at least one explicit assertion.
- **Test Naming**: Test names MUST describe the scenario and expected outcome using
  the pattern `test_<action>_<condition>_<expected_result>`.
- **Mocking External Services**: OpenAI API calls and external dependencies MUST be
  mocked in unit tests. Integration tests MAY use sandboxed external services.

**Rationale**: An HR assistant providing policy guidance must be reliable. Comprehensive
testing prevents regressions and ensures consistent behavior across updates.

### III. User Experience Consistency

The user interface and conversational experience MUST maintain consistency with
Nestlé's corporate identity and provide predictable, accessible interactions.

**Non-Negotiable Rules:**

- **Brand Alignment**: UI colors, typography, and styling MUST align with Nestlé's
  corporate design language as defined in the Gradio theme configuration.
- **Response Format Consistency**: All chatbot responses MUST follow a consistent
  structure: direct answer, supporting context from policy documents, and source
  attribution when applicable.
- **Error Messaging**: User-facing error messages MUST be clear, actionable, and
  free of technical jargon. Internal errors MUST log details without exposing them
  to users.
- **Conversation Continuity**: The system MUST maintain conversation context within
  a session. Context switches MUST be handled gracefully with acknowledgment.
- **Accessibility**: UI components MUST support keyboard navigation. Text contrast
  ratios MUST meet WCAG 2.1 AA standards.
- **Loading States**: Long-running operations MUST display progress indicators.
  Users MUST NOT encounter unresponsive UI states exceeding 500ms without feedback.

**Rationale**: HR policy queries are sensitive. A consistent, professional experience
builds trust and ensures employees can rely on the assistant for accurate guidance.

### IV. Performance Requirements

The system MUST meet defined performance targets to ensure responsive interactions
and efficient resource utilization.

**Non-Negotiable Rules:**

- **Response Latency**: Standard queries MUST return responses within 5 seconds
  (p95). Initial load (embedding initialization) is exempt but MUST complete
  within 30 seconds.
- **Memory Efficiency**: Application memory usage MUST NOT exceed 2GB under normal
  operation. Vector store operations MUST NOT cause memory leaks.
- **Concurrent Users**: The system MUST handle at least 10 concurrent chat sessions
  without degradation in response quality or latency.
- **Retrieval Accuracy**: RAG retrieval MUST return relevant chunks with >80%
  precision for policy-related queries (measured via evaluation dataset).
- **Graceful Degradation**: When OpenAI API is unavailable, the system MUST display
  a clear maintenance message rather than crashing or hanging.
- **Startup Time**: Application MUST be ready to serve requests within 60 seconds
  of startup, including PDF processing and vector store initialization.

**Rationale**: Employees seeking HR policy information need timely, accurate responses.
Performance standards ensure the assistant remains a reliable resource during peak usage.

## Quality Gates

All changes MUST pass through these quality gates before merge:

| Gate | Requirement | Enforcement |
|------|-------------|-------------|
| Lint | Zero errors from ruff/flake8 | CI pipeline |
| Format | Black formatting applied | CI pipeline |
| Type Check | mypy passes with no errors | CI pipeline |
| Unit Tests | All pass, coverage >= 80% | CI pipeline |
| Integration Tests | All pass | CI pipeline |
| Performance | No regression in response latency | Manual review |
| Security | No hardcoded secrets, dependencies scanned | CI pipeline |

## Development Workflow

### Code Review Requirements

- All changes MUST be submitted via pull request
- PRs MUST have at least one approving review before merge
- PRs MUST pass all quality gates before merge is enabled
- Large PRs (>500 lines) SHOULD be split into smaller, reviewable chunks

### Branch Strategy

- `main` branch MUST always be deployable
- Feature branches MUST follow naming: `feature/short-description`
- Bug fixes MUST follow naming: `fix/issue-description`
- All branches MUST be deleted after merge

### Commit Standards

- Commit messages MUST follow conventional commit format:
  `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Each commit SHOULD represent a single logical change

## Governance

This constitution supersedes all other development practices for the Nestlé HR
Assistant project. All contributors MUST adhere to these principles.

### Amendment Process

1. Proposed amendments MUST be documented with rationale
2. Amendments MUST be reviewed by project maintainers
3. Breaking changes (principle removals/redefinitions) require migration plan
4. Version number MUST be incremented per semantic versioning rules

### Compliance Review

- All pull requests MUST include Constitution Check verification
- Violations MUST be justified in the PR description with clear rationale
- Recurring violations indicate need for constitution amendment discussion

### Versioning Policy

- **MAJOR**: Backward-incompatible principle changes or removals
- **MINOR**: New principles, expanded guidance, or material additions
- **PATCH**: Clarifications, typo fixes, non-semantic refinements

**Version**: 1.0.0 | **Ratified**: 2026-01-14 | **Last Amended**: 2026-01-14
