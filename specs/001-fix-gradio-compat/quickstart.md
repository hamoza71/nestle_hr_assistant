# Quickstart: Verifying the Gradio 6.x Fix

**Feature**: 001-fix-gradio-compat
**Date**: 2026-01-14

## Prerequisites

- Python 3.12+ installed
- Virtual environment activated
- OpenAI API key configured in `.env`
- PDF document `Nestle_hr_policy_pdf_2012.pdf` in project root

## Verification Steps

### Step 1: Start the Application

```bash
cd /Users/ahmedomar/Downloads/nestle_hr_assistant
source venv/bin/activate
python app.py
```

**Expected Output**:
```
============================================================
   🏢 NESTLÉ HR ASSISTANT - RAG CHATBOT
============================================================
🔄 Initializing Nestlé HR Assistant...
📄 Extracting text from PDF...
   Extracted 14331 characters
✂️  Creating text chunks...
   Created 32 chunks
🔢 Creating embeddings and vector store...
   Vector store ready
✅ System initialized successfully!

🚀 Launching Gradio interface...
```

**Success Criteria**: No `TypeError` about unexpected keyword argument `type`.

### Step 2: Access the Web Interface

Open browser to: `http://localhost:7860`

**Expected**: Chatbot UI loads with:
- Nestlé HR Assistant header
- Empty chat area
- Text input field
- Send button
- Clear Chat button

**Success Criteria**: Interface renders without JavaScript errors.

### Step 3: Send a Test Message

1. Type: `What is the policy on parental leave?`
2. Click **Send** (or press Enter)

**Expected**:
- Your message appears in the chat
- Assistant response streams in (appears incrementally)
- Response contains HR policy information

**Success Criteria**: Message exchange completes without errors.

### Step 4: Test Conversation Context

1. After receiving a response, type: `Tell me more about that`
2. Click **Send**

**Expected**:
- Previous exchange remains visible
- Assistant responds with awareness of the parental leave context

**Success Criteria**: Conversation history is maintained.

### Step 5: Test Clear Chat

1. Click **🗑️ Clear Chat**

**Expected**:
- All messages are removed
- Chat area is empty
- Ready for new conversation

**Success Criteria**: Chat clears without errors.

## Troubleshooting

### Application Crashes on Startup

**Symptom**: `TypeError: Chatbot.__init__() got an unexpected keyword argument 'type'`

**Cause**: The `type="tuples"` parameter is still present in the code.

**Fix**: Ensure the Chatbot initialization in `app.py` does not include the `type` parameter.

### Messages Not Appearing

**Symptom**: User types message but nothing appears in chat.

**Cause**: Message format mismatch.

**Fix**: Verify `user_input` function returns dictionary format:
```python
[{"role": "user", "content": message}]
```

### Streaming Not Working

**Symptom**: Response appears all at once instead of streaming.

**Cause**: Assistant message not being updated correctly.

**Fix**: Verify `bot_response` updates `history[-1]["content"]` incrementally.

## Rollback

If issues persist, the original code can be restored from git:

```bash
git checkout master -- app.py
```

Note: This will revert to the broken Gradio 4.x code. To fix, either:
1. Downgrade Gradio: `pip install gradio==4.44.0`
2. Re-apply the Gradio 6.x compatibility fixes
