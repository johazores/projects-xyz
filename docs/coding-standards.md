# Coding Standards

## Python style

- Use Python 3.10 or newer.
- Add type hints to public functions and meaningful internal boundaries.
- Keep functions focused and short.
- Prefer dataclasses and standard-library modules when they are sufficient.
- Raise clear exceptions with actionable messages.
- Use comments only when the reason is not obvious from the code.

## Simplicity rules

- Prefer a function over a class when no state is needed.
- Prefer one provider file over a provider framework.
- Do not introduce dependency injection containers, plugin loaders, registries, or database configuration without a current requirement.
- Do not share code across projects until duplication becomes costly enough to justify packaging.
- Avoid hidden behavior and implicit global state.

## Naming

- Use `snake_case` for Python files, functions, and variables.
- Use `PascalCase` for classes and protocols.
- Use clear media-specific names such as `generate_image` rather than generic names such as `execute`.

## Logging

Use `logging` for progress and diagnostics. CLI errors should be concise and should not expose full stack traces unless debug logging is enabled.
