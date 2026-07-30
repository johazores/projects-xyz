# Contributing

Thank you for helping improve the local media toolkit.

## Before changing code

- Read the project README and relevant architecture notes.
- Check whether an existing utility or provider already solves the problem.
- Prefer extending existing modules over creating parallel implementations.
- Keep the current folder structure unless a real navigation problem exists.
- Use Python 3.11 for the simplest setup across optional tools.

## Development principles

- Keep local processing useful without cloud infrastructure.
- Keep optional model dependencies isolated.
- Add provider integrations only when they can be tested.
- Prefer clear functions and subprocess calls over unnecessary orchestration.
- Preserve stable CLI behavior and output locations.
- Do not add queues, databases, or large frameworks without a real workflow requirement.
- Do not add or modify GitHub Actions without a separate workflow and cost review.

## Branches and commits

Use focused branches such as `feat/<feature-name>`, `fix/<issue-name>`, or `docs/<topic>`. Use Conventional Commits and keep each commit focused.

## Pull requests

Describe:

- what changed;
- why it changed;
- dependencies required;
- testing performed;
- breaking or output-compatibility changes.

Keep unrelated refactors out of feature changes.

## Documentation and generated files

Update documentation when behavior, configuration, commands, or supported providers change. Do not commit personal outputs, API keys, local configuration, virtual environments, downloaded models, or model caches.
