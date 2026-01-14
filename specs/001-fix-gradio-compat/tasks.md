# Tasks: Fix Gradio Library Compatibility

**Input**: Design documents from `/specs/001-fix-gradio-compat/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Tests**: NOT INCLUDED - User explicitly requested "don't create any test phase"

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: All changes in `app.py` at repository root
- No separate src/ or tests/ directories for this fix

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup required - this is a bug fix to an existing application

*No tasks in this phase - project already exists and is configured.*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Remove the crash-causing deprecated parameter

**⚠️ CRITICAL**: This must be complete before any other changes can be tested

- [x] T001 Remove deprecated `type="tuples"` parameter from Chatbot initialization in app.py:281

**Checkpoint**: Application should now start without TypeError (but messages won't work correctly yet)

---

## Phase 3: User Story 1 - Application Startup (Priority: P1) 🎯 MVP

**Goal**: Application starts successfully and displays the Gradio interface

**Independent Test**: Run `python app.py` and verify the interface loads at http://localhost:7860

### Implementation for User Story 1

- [x] T002 [US1] Verify Chatbot component initializes correctly after T001 in app.py:281-286

**Checkpoint**: US1 complete - Application starts and displays the chat interface

---

## Phase 4: User Story 2 - Send and Receive Messages (Priority: P1)

**Goal**: Users can send messages and receive streaming responses

**Independent Test**: Type a question, press Send, verify message appears and assistant responds with streaming

### Implementation for User Story 2

- [x] T003 [US2] Update `user_input()` function to return dict format instead of tuple list in app.py:242-246
- [x] T004 [US2] Update `bot_response()` function to read user message from dict format in app.py:248-266
- [x] T005 [US2] Update `bot_response()` function to append and update assistant dict for streaming in app.py:248-266
- [x] T006 [US2] Update `generate_response()` function to use dict history directly (remove tuple conversion loop) in app.py:150-171
- [x] T007 [US2] Update `generate_response_streaming()` function to use dict history directly (remove tuple conversion loop) in app.py:173-199

**Checkpoint**: US2 complete - Users can send messages and receive streaming responses

---

## Phase 5: User Story 3 - Maintain Conversation History (Priority: P2)

**Goal**: Chat history is maintained within session and context is passed to the LLM

**Independent Test**: Ask a question, then ask "tell me more about that" and verify contextual response

### Implementation for User Story 3

- [x] T008 [US3] Verify history is correctly passed through event chain in app.py:305-325
- [x] T009 [US3] Verify `clear_chat()` function still works correctly (should already be compatible) in app.py:268-269

**Checkpoint**: US3 complete - Conversation history is maintained and context-aware

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup

- [x] T010 Run quickstart.md validation steps to verify all acceptance criteria
- [x] T011 Verify no remaining tuple index patterns (`[0]`, `[1]`) in chat-related functions in app.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A - no setup needed
- **Foundational (Phase 2)**: No dependencies - must complete first (fixes crash)
- **User Story 1 (Phase 3)**: Depends on Phase 2 - verifies startup works
- **User Story 2 (Phase 4)**: Depends on Phase 3 - enables message exchange
- **User Story 3 (Phase 5)**: Depends on Phase 4 - verifies history works
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

```
T001 (Foundation)
  └─> T002 (US1: Startup)
        └─> T003-T007 (US2: Messaging) - Execute sequentially within same file
              └─> T008-T009 (US3: History)
                    └─> T010-T011 (Polish)
```

### Within Each User Story

- **US1**: Single verification task
- **US2**: 5 tasks modifying related functions - execute sequentially (same file, related changes)
- **US3**: 2 verification tasks

### Parallel Opportunities

**Note**: Limited parallelization due to single-file nature of this fix.

- T003 and T006 modify different functions but both affect message handling - recommend sequential
- T010 and T011 (Polish) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete T001 (Foundation) - Fix crash
2. Complete T002 (US1) - Verify startup
3. Complete T003-T007 (US2) - Enable messaging
4. **STOP and VALIDATE**: Application should be fully functional at this point
5. Continue to US3 for conversation history verification

### Incremental Delivery

1. T001 → Application starts (no longer crashes)
2. T002 → Interface loads correctly
3. T003-T007 → Full chat functionality restored
4. T008-T009 → History confirmed working
5. T010-T011 → Full validation complete

### Recommended Execution

Since all changes are in a single file (`app.py`), execute tasks sequentially:

```bash
# Execute in order:
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011
```

---

## Notes

- All tasks modify the same file (`app.py`) - sequential execution recommended
- No test tasks included per user request
- Each checkpoint allows manual verification before continuing
- Commit recommended after each phase completion
- Total: 11 tasks (1 foundational, 1 US1, 5 US2, 2 US3, 2 polish)
