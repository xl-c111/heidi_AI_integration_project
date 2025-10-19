# `app/api/ask_heidi.py` logic guide

## High-level overview
The module provides helpers that send requests to Heidi's Ask AI endpoint and interpret responses that may arrive as Server-Sent Events (SSE), JSON, or plain text. Its main responsibilities are:
- Normalizing streaming responses so callers receive the final assembled text or structured payload.
- Handling request errors with friendly messages.
- Offering a convenience function that retries the Ask AI call with different content types.

## Function-by-function walkthrough

### `parse_sse_response(sse_text: str) -> str`
Offline helper that parses a complete SSE-formatted string (e.g., captured from logs). It:
1. Splits the body into individual lines.
2. Filters for lines starting with `data:`.
3. Delegates to `_extract_sse_chunk` to decode each chunk.
4. Concatenates all extracted pieces and trims surrounding whitespace.

Use this when you already have the full response text and want the combined message.

### `_extract_sse_chunk(raw_payload: str) -> str`
Shared utility that converts an individual `data:` payload into text. Steps:
1. Attempts `json.loads` on the raw payload.
2. Accepts multiple JSON shapes:
   - `{ "data": "..." }`
   - `{ "content": "..." }`
   - A bare JSON string.
3. Returns the text fragment when found; otherwise logs the unexpected format and returns an empty string.

Both the offline parser and the streaming consumer rely on this to stay in sync.

### `_consume_sse_stream(response: requests.Response) -> str`
Processes a streaming HTTP response returned by `requests` with `stream=True`:
1. Iterates over `response.iter_lines(decode_unicode=True)`.
2. Ignores blank lines and non `data:` lines (SSE comments/other fields).
3. Uses `_extract_sse_chunk` to decode each chunk.
4. Collects non-empty chunks and returns the concatenated result.

If the stream raises chunked encoding or JSON decode errors, it logs the error and returns an empty string, signaling failure to the caller.

### `ask_ai_stream(jwt_token, session_id, ai_command_text, content, content_type="MARKDOWN")`
This is the main entry point for querying the Ask AI endpoint.

Request preparation:
1. Builds the target URL from `BASE_URL`, the session ID, and `/ask-ai`.
2. Creates request headers with bearer authorization and JSON content type.
3. Serializes the payload containing the AI command text, the document content, and the chosen content type.
4. Issues a POST with streaming enabled and a `(10, 70)` connect/read timeout tuple.

Response handling:
1. For status code 200, it inspects the final `Content-Type` header case-insensitively to pick the right parser.
2. SSE (`text/event-stream`): calls `_consume_sse_stream`. On success returns a dict containing the combined text and format tag `sse`. If parsing yields nothing, flags an error.
3. JSON (`application/json`): attempts `response.json()` and returns the decoded payload; if parsing fails, it falls back to raw text and adds a warning.
4. Any other type: reads `response.text` and returns it when non-empty; otherwise marks the response as empty.
5. For non-200 statuses it maps specific codes (401, 404) to descriptive error messages. All other responses pass through the status code and body for diagnostic purposes.

Exception handling:
- `requests.exceptions.Timeout` and `ConnectionError` return user-friendly error dictionaries.
- Any other unexpected exception is caught and wrapped in a generic error response.

Return shape:
Every successful branch includes `"success": True`, the parsed payload under `"response"`, and a `"format"` marker (`sse`, `json`, or `text`). Error branches include `"error": True` plus context.

### `test_ask_ai_with_fallbacks(...)`
Utility designed for manual experiments rather than automated tests. It:
1. Tries `ask_ai_stream` with content types `"MARKDOWN"`, `"TEXT"`, and `"PLAIN_TEXT"` in order.
2. Returns immediately on success.
3. If every attempt fails, surfaces the last error message after logging each attempt.

## Control flow summary
1. Client code calls `ask_ai_stream`.
2. The function prepares and sends the POST request.
3. It inspects the response status and content type to choose the right parsing strategy.
4. SSE responses stream through `_consume_sse_stream`, which reuses `_extract_sse_chunk` for consistency with `parse_sse_response`.
5. JSON and text responses are handled directly on the `requests.Response` object.
6. Errors and exceptions are transformed into structured dictionaries so higher layers can react (e.g., showing messages in the UI).
7. Alternative content types can be tested with the helper `test_ask_ai_with_fallbacks`.

This structure keeps streaming and non-streaming formats unified while giving clear diagnostics when Heidi's API returns unexpected data.
