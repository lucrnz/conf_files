---
status: accepted
---

# ask-user replaces the native questions tool

Desktop `ask-user` is the primary multiple-choice picker. A native questions tool runs only when the window cannot open (no display, uv/Qt failure, timeout, missing skill); cancel is a decline, not a second prompt; numbered chat is last resort. v1 preferred the native tool and left consumers saying “questions tool if available,” so the window never replaced a working native tool.

## Considered Options

- Native-first (v1): use the questions tool when present; load ask-user only when it is missing.
- ask-user only: never fall back to the native tool.
- This invert: ask-user first; native tool only on cannot-open.
