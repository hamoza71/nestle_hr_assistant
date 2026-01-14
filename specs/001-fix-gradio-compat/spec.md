# Feature Specification: Fix Gradio Library Compatibility

**Feature Branch**: `001-fix-gradio-compat`
**Created**: 2026-01-14
**Status**: Draft
**Input**: User description: "the current code is not working because of tech stack libraries conflict, review project directory and collect needed information then fix it and don't create any test phase"

## Problem Statement

The Nestlé HR Assistant application fails to launch due to incompatibility between the installed UI framework version (Gradio 6.0.2) and the application code written for an earlier version (Gradio 4.x). The application crashes on startup with the error:

```
TypeError: Chatbot.__init__() got an unexpected keyword argument 'type'
```

### Root Cause Analysis

1. **Version Mismatch**: The `requirements.txt` specifies `gradio>=4.0.0` (minimum version) but pip installed version 6.0.2
2. **Breaking API Changes**: Gradio 6.x introduced breaking changes to the Chatbot component:
   - Removed the `type` parameter (previously used to specify `"tuples"` or `"messages"` format)
   - Changed the default message format from tuple-based `[[user_msg, bot_msg], ...]` to dictionary-based `[{"role": "user", "content": "..."}]`
3. **Affected Code Locations**: The chatbot initialization, message handling, and history management all use the deprecated tuple format

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Application Startup (Priority: P1)

As an HR department employee, I need the HR Assistant application to start successfully so that I can access HR policy information through the chatbot interface.

**Why this priority**: Without successful startup, no other functionality is accessible. This is a complete blocker for all users.

**Independent Test**: Can be fully tested by running `python app.py` and verifying the Gradio interface loads at `http://localhost:7860` without errors.

**Acceptance Scenarios**:

1. **Given** the application dependencies are installed, **When** I run `python app.py`, **Then** the system initializes without errors and displays "Launching Gradio interface..."
2. **Given** the application is starting, **When** initialization completes, **Then** the web interface is accessible at the configured port (7860)
3. **Given** the application is running, **When** I open the browser to the interface URL, **Then** I see the chatbot UI with the Nestlé HR Assistant header

---

### User Story 2 - Send and Receive Messages (Priority: P1)

As an HR department employee, I need to send questions and receive responses in the chat interface so that I can get answers about HR policies.

**Why this priority**: Core functionality - if users cannot interact with the chatbot, the application serves no purpose.

**Independent Test**: Can be fully tested by typing a question in the chat input and verifying a response appears in the conversation.

**Acceptance Scenarios**:

1. **Given** the chatbot interface is loaded, **When** I type a question and press Send, **Then** my message appears in the conversation
2. **Given** I have sent a message, **When** the system processes my query, **Then** a response from the assistant appears below my message
3. **Given** the assistant is generating a response, **When** streaming is in progress, **Then** the response text appears incrementally (not all at once)

---

### User Story 3 - Maintain Conversation History (Priority: P2)

As an HR department employee, I need the chatbot to remember my previous messages in the session so that I can have a contextual conversation about related HR topics.

**Why this priority**: Important for user experience but the app is functional without it for single-question interactions.

**Independent Test**: Can be fully tested by asking a follow-up question that references a previous answer and verifying the assistant understands the context.

**Acceptance Scenarios**:

1. **Given** I have asked a question and received a response, **When** I ask a follow-up question, **Then** the previous exchange is visible in the chat history
2. **Given** a conversation with multiple exchanges exists, **When** I ask a contextual question like "tell me more about that", **Then** the assistant responds with awareness of the previous context
3. **Given** I click the "Clear Chat" button, **When** the action completes, **Then** all previous messages are removed and the chat starts fresh

---

### Edge Cases

- What happens when the user submits an empty message? System should ignore empty submissions and not add blank entries to the conversation.
- What happens when the OpenAI API returns an error? System should display a user-friendly error message in the chat without crashing.
- What happens when the user rapidly submits multiple messages? System should queue and process them in order without losing messages.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Application MUST start successfully with the currently installed dependency versions (Gradio 6.0.2, LangChain 1.1.0, OpenAI 1.x)
- **FR-002**: Chatbot component MUST initialize without passing deprecated parameters
- **FR-003**: User messages MUST be displayed in the conversation immediately after submission
- **FR-004**: Assistant responses MUST appear in the conversation with streaming (incremental display)
- **FR-005**: Conversation history MUST be maintained within a session and passed to the response generator for context
- **FR-006**: Clear Chat functionality MUST remove all messages and reset the conversation state
- **FR-007**: Error messages from failed API calls MUST be displayed to the user in the chat interface (not as application crashes)

### Assumptions

- The Gradio 6.x version will remain installed (we are updating code to match the library, not downgrading the library)
- All other dependencies (OpenAI, LangChain ecosystem, FAISS) are functioning correctly and do not require changes
- The existing RAG pipeline (PDF extraction, chunking, embeddings, retrieval) works correctly and only the UI layer needs updates

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Application starts and serves the web interface within 60 seconds (including PDF processing and embedding initialization)
- **SC-002**: Users can send a message and receive a response within 10 seconds under normal conditions
- **SC-003**: 100% of chat interactions (send message, receive response, clear chat) complete without application errors
- **SC-004**: Conversation context is correctly maintained across at least 10 consecutive message exchanges
- **SC-005**: The fix requires no changes to the existing RAG pipeline, only the UI/presentation layer
