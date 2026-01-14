# Research: Gradio 6.x Migration

**Feature**: 001-fix-gradio-compat
**Date**: 2026-01-14
**Status**: Complete

## Research Questions

### Q1: What API changes occurred between Gradio 4.x and 6.x for the Chatbot component?

**Finding**: Gradio 6.x introduced a unified message format and removed legacy parameters.

**Key Changes**:

| Aspect | Gradio 4.x | Gradio 6.x |
|--------|------------|------------|
| `type` parameter | `type="tuples"` or `type="messages"` | Removed (messages-only) |
| Message format | `[[user, bot], [user, bot]]` | `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]` |
| Empty message | `[user, None]` (pending bot response) | `{"role": "user", "content": "..."}` then append assistant message |
| Role values | Implicit (position in tuple) | Explicit: `"user"`, `"assistant"`, `"system"` |

**Source**: Gradio 6.x Chatbot documentation and `help(gr.Chatbot.__init__)` output.

### Q2: How should streaming responses be handled in Gradio 6.x?

**Finding**: Instead of modifying tuple indices, append/update dictionary messages.

**Pattern**:
```python
# Old (Gradio 4.x tuple format)
history[-1][1] = partial_response  # Modify bot slot in last tuple

# New (Gradio 6.x dict format)
history[-1]["content"] = partial_response  # Update content of last message
# OR for cleaner approach:
history.append({"role": "assistant", "content": ""})  # Add empty assistant message
history[-1]["content"] = partial_response  # Update incrementally
```

### Q3: How to convert Gradio 6.x history format to OpenAI messages format?

**Finding**: The formats are now nearly identical, simplifying conversion.

**Mapping**:
```python
# Gradio 6.x format (native)
[
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
]

# OpenAI API format (identical structure)
[
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
]
```

The Gradio 6.x dict format aligns with OpenAI's chat completion API, eliminating the need for format conversion in `generate_response` and `generate_response_streaming` functions.

### Q4: Are there any other breaking changes that affect this application?

**Finding**: No other breaking changes impact the current codebase.

**Verified Compatible**:
- `gr.Blocks()` - No changes
- `gr.Chatbot()` - Changed (addressed above)
- `gr.Textbox()` - No changes
- `gr.Button()` - No changes
- `gr.Markdown()` - No changes
- Event handlers (`.submit()`, `.click()`, `.then()`) - No changes

## Decisions

### D1: Message Format Migration Strategy

**Decision**: Adopt Gradio 6.x native dictionary format throughout.

**Rationale**:
1. Required for Gradio 6.x compatibility
2. Aligns with OpenAI API format (reduces conversion code)
3. More readable and maintainable than tuple format
4. Supports future extensibility (metadata, file attachments)

### D2: History Conversion Approach

**Decision**: Remove tuple-to-messages conversion; pass history directly to OpenAI API.

**Rationale**: Gradio 6.x history format is now compatible with OpenAI's expected format, eliminating the need for conversion logic in `generate_response` functions.

### D3: Streaming Implementation

**Decision**: Create assistant message with empty content, then update content field incrementally.

**Rationale**: Clean separation of concerns - adding a message is distinct from updating its content. This pattern is explicit and works naturally with Gradio's state management.

## Implementation Notes

### Functions Requiring Modification

1. **`user_input(message, history)`** (lines 242-246)
   - Change: Return history with appended user dict instead of tuple
   - Before: `history + [[message, None]]`
   - After: `history + [{"role": "user", "content": message}]`

2. **`bot_response(history)`** (lines 248-266)
   - Change: Read user message from dict, append/update assistant dict
   - Before: `history[-1][0]` for user msg, `history[-1][1] = response` for bot
   - After: `history[-1]["content"]` for user msg, append new assistant dict

3. **`generate_response(query, context, chat_history)`** (lines 150-171)
   - Change: History is now already in OpenAI format
   - Before: Loop converting `(user_msg, bot_msg)` tuples to dicts
   - After: Use history directly (filter out current query if needed)

4. **`generate_response_streaming(query, context, chat_history)`** (lines 173-199)
   - Change: Same as generate_response
   - History conversion loop can be removed

5. **`create_chat_interface(vector_store)`** (line 281)
   - Change: Remove deprecated `type="tuples"` parameter
   - Before: `gr.Chatbot(value=[], height=450, show_label=False, type="tuples")`
   - After: `gr.Chatbot(value=[], height=450, show_label=False)`

6. **`clear_chat()`** (lines 268-269)
   - Change: None required (already returns empty list)

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Hidden tuple references | Low | Medium | Search codebase for `[0]`, `[1]` index patterns |
| Streaming breaks | Medium | High | Test streaming with real OpenAI API call |
| State management issues | Low | Medium | Verify Gradio state updates correctly |

## References

- Gradio 6.x Chatbot documentation
- OpenAI Chat Completions API reference
- Local inspection: `help(gr.Chatbot.__init__)`
