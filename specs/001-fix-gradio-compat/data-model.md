# Data Model: Chat Message Format

**Feature**: 001-fix-gradio-compat
**Date**: 2026-01-14

## Overview

This document specifies the message format used for chat history in the Gradio 6.x-compatible implementation. The format aligns with both Gradio's native Chatbot component and OpenAI's Chat Completions API.

## Message Entity

### ChatMessage

A single message in the conversation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | Yes | The role of the message author: `"user"` or `"assistant"` |
| `content` | string | Yes | The text content of the message |

**Valid Roles**:
- `"user"` - Message from the human user
- `"assistant"` - Response from the AI assistant

**Example**:
```json
{
  "role": "user",
  "content": "What is the policy on parental leave?"
}
```

### ChatHistory

An ordered list of ChatMessage objects representing the conversation.

| Field | Type | Description |
|-------|------|-------------|
| `history` | ChatMessage[] | Chronologically ordered list of messages |

**Example**:
```json
[
  {"role": "user", "content": "What is the policy on parental leave?"},
  {"role": "assistant", "content": "According to Nestlé HR policy..."},
  {"role": "user", "content": "How long is it?"},
  {"role": "assistant", "content": "The parental leave duration is..."}
]
```

## State Transitions

### Message Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                    CHAT HISTORY                         │
│                                                         │
│  1. User types message                                  │
│     └─> Append: {"role": "user", "content": "..."}     │
│                                                         │
│  2. Bot starts responding                               │
│     └─> Append: {"role": "assistant", "content": ""}   │
│                                                         │
│  3. Bot streams response (incremental)                  │
│     └─> Update: history[-1]["content"] = partial       │
│                                                         │
│  4. Bot completes response                              │
│     └─> Final: history[-1]["content"] = full_response  │
│                                                         │
│  5. Clear chat                                          │
│     └─> Reset: history = []                            │
└─────────────────────────────────────────────────────────┘
```

## Migration Mapping

### From Gradio 4.x (Tuple Format)

| Old Format (4.x) | New Format (6.x) |
|------------------|------------------|
| `[[user, bot]]` | `[{role: "user", content: user}, {role: "assistant", content: bot}]` |
| `[[user, None]]` | `[{role: "user", content: user}]` |
| `history[-1][0]` | `history[-1]["content"]` (when last is user) |
| `history[-1][1] = x` | `history[-1]["content"] = x` (when last is assistant) |
| `history + [[msg, None]]` | `history + [{"role": "user", "content": msg}]` |

## Validation Rules

1. **Role Constraint**: `role` MUST be either `"user"` or `"assistant"`
2. **Content Constraint**: `content` MUST be a non-null string (empty string allowed during streaming)
3. **Order Constraint**: Messages SHOULD alternate between user and assistant roles
4. **First Message**: First message SHOULD have `role: "user"` (user initiates conversation)

## Integration with OpenAI API

The Gradio 6.x format is directly compatible with OpenAI's Chat Completions API:

```python
# Gradio history can be passed directly to OpenAI
messages = [
    {"role": "system", "content": SYSTEM_PROMPT.format(context=context)}
]
messages.extend(history)  # Append Gradio history directly
messages.append({"role": "user", "content": query})

response = client.chat.completions.create(
    model=LLM_MODEL,
    messages=messages
)
```

No conversion required between Gradio history and OpenAI messages format.
