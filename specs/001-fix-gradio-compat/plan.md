# Implementation Plan: Fix Gradio Library Compatibility

**Branch**: `001-fix-gradio-compat` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fix-gradio-compat/spec.md`

## Summary

Update the Nestlé HR Assistant chatbot UI code to be compatible with Gradio 6.x API. The application currently crashes on startup because it uses deprecated Gradio 4.x Chatbot parameters (`type="tuples"`) and tuple-based message formats (`[[user, bot], ...]`) that are no longer supported in Gradio 6.x. The fix involves removing deprecated parameters and migrating to the new dictionary-based message format (`[{"role": "user", "content": "..."}]`).

## Technical Context

**Language/Version**: Python 3.12.7
**Primary Dependencies**: Gradio 6.0.2, OpenAI 1.x, LangChain 1.1.0, FAISS-CPU 1.13.0
**Storage**: In-memory vector store (FAISS), PDF file on disk
**Testing**: Manual verification (user explicitly requested no test phase)
**Target Platform**: Local development server (macOS/Linux), localhost:7860
**Project Type**: Single project (single `app.py` file)
**Performance Goals**: <5s response latency (p95), <60s startup time
**Constraints**: <2GB memory, 10 concurrent sessions
**Scale/Scope**: Single-user local deployment, ~32 text chunks from PDF

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Code Quality** | ✅ PASS | Single file modification; follows existing code style |
| **II. Testing Standards** | ⚠️ WAIVED | User explicitly requested "don't create any test phase" |
| **III. User Experience Consistency** | ✅ PASS | UI behavior preserved; only internal message format changes |
| **IV. Performance Requirements** | ✅ PASS | No performance impact; same operations with updated API |

**Waiver Justification**: Testing Standards are waived per explicit user request. This is a targeted bug fix with clear before/after states that can be manually verified by running the application.

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-gradio-compat/
├── plan.md              # This file
├── research.md          # Gradio 6.x migration research
├── data-model.md        # Message format specification
├── quickstart.md        # Verification steps
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
nestle_hr_assistant/
├── app.py                          # Main application (MODIFY)
├── requirements.txt                # Dependencies (no change needed)
├── .env                            # API key configuration
├── Nestle_hr_policy_pdf_2012.pdf  # HR policy document
└── venv/                           # Virtual environment
```

**Structure Decision**: Single-file project. All changes are isolated to `app.py`. The RAG pipeline (PDF extraction, chunking, embeddings, retrieval) remains untouched; only the Gradio UI layer functions are modified.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Testing waiver | User explicitly requested no tests | N/A - user requirement |

---

## Phase 0: Research Summary

### Gradio 6.x Chatbot API Changes

**Decision**: Migrate from tuple-based to dictionary-based message format

**Rationale**: Gradio 6.x removed the `type` parameter and standardized on dictionary format for better extensibility (supports metadata, custom roles, file attachments).

**Key Changes Identified**:

1. **Chatbot initialization**: Remove `type="tuples"` parameter
2. **Message format**: Change from `[[user_msg, bot_msg], ...]` to `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`
3. **History handling**: Update all functions that read/write chat history to use new format
4. **Streaming**: Append new message dicts instead of modifying tuple indices

**Alternatives Considered**:
- Downgrade to Gradio 4.x: Rejected - user wants to keep current dependencies
- Use gradio-chatbot-legacy: Rejected - unofficial package, not maintained

### Affected Code Sections in app.py

| Function | Line | Change Required |
|----------|------|-----------------|
| `create_chat_interface` | 281 | Remove `type="tuples"` from Chatbot init |
| `user_input` | 242-246 | Return dict format instead of tuple list |
| `bot_response` | 248-266 | Read/write dict format for history |
| `generate_response` | 150-171 | Convert dict history to OpenAI messages |
| `generate_response_streaming` | 173-199 | Convert dict history to OpenAI messages |
| `clear_chat` | 268-269 | Return empty list (no format change needed) |
