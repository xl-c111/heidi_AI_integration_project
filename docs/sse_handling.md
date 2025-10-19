# Heidi AI SSE Handling Overview

## High-Level Flow

1. **Client Trigger**  
   - Frontend (e.g., `/ask-question`) or backend service issues a request that eventually calls `app/api/ask_heidi.ask_ai_stream`.

2. **Prepare Request**  
   - `ask_ai_stream` constructs the Heidi endpoint `POST /sessions/{session_id}/ask-ai`.  
   - Payload includes the prompt (`ai_command_text`), user content, and content type (default `MARKDOWN`).  
   - `Authorization` header carries the JWT; `Content-Type` is `application/json`.

3. **HTTP Call With Streaming**  
   - `requests.post(..., stream=True, timeout=(10, 70))` opens a streaming response so chunks are available as Heidi emits them.  
   - Connect/read timeouts are separated to avoid hanging connections.

4. **Content-Type Dispatch**  
   - Response headers are inspected:
     - `text/event-stream` ➜ handle as SSE (`_consume_sse_stream`).  
     - `application/json` ➜ parse JSON (`response.json()`); fall back to text if parsing fails.  
     - Other types ➜ treat the body as raw text.

5. **Streaming Consumption**  
   - `_consume_sse_stream` iterates `response.iter_lines(decode_unicode=True)`.  
   - Each `data:` line is passed to `_extract_sse_chunk`, which safely attempts `json.loads`.  
   - Supported payload shapes:
     - `{"data": "<string>"}`  
     - `{"content": "<string>"}`  
     - `<string>` (plain text)  
   - Successfully parsed chunks append to `combined_chunks`; malformed chunks are logged and skipped.

6. **Return Structured Result**  
   - On success: `{"success": True, "response": "<combined text>", "format": "sse"}`.  
   - Empty stream ➜ error payload noting the absence of content.  
   - 401/404 and other HTTP errors produce descriptive error dictionaries with remediation hints.

7. **Fallback Strategy**  
   - `ask_ai_with_fallbacks` retries `ask_ai_stream` with content types `MARKDOWN`, `TEXT`, `PLAIN_TEXT` until success or exhaustion, surfacing the last error if all fail.

8. **Buffered Parsing Utility**  
   - `parse_sse_response` remains available for legacy callers that receive the entire SSE body at once (useful in debugging scripts). It reuses `_extract_sse_chunk` for consistency.

9. **Testing Coverage**  
   - `tests/test_ask_heidi.py` stubs streaming responses to verify:  
     - Incremental SSE aggregation  
     - JSON content handling  
     - Auth error propagation

## Logic Flow Diagram

```
Caller invokes ask_ai_stream
    ↓
Build URL, headers, payload
    ↓
requests.post(stream=True)
    ↓ (status 200)
Check Content-Type
 ├─ text/event-stream → _consume_sse_stream → _extract_sse_chunk → append to buffer → return success + combined text
 ├─ application/json → response.json()
 │     ├─ parse ok → return success + JSON
 │     └─ parse fail → return success + raw text
 └─ other → return raw text or empty-error message

Non-200 status:
 ├─ 401/404 → return auth/session error
 ├─ other codes → return generic error
 └─ timeout/connection → return timeout/connection message
```

## Practical Notes

- Frontend consumers still receive complete strings; to stream to browsers, adapt `_consume_sse_stream` to yield chunks as they arrive.  
- The helper functions emit debug `print` statements; swap with structured logging for production.  
- When adding new Heidi endpoints that use SSE, reuse `_consume_sse_stream` and `_extract_sse_chunk` to keep parsing logic consistent.
