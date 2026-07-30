# Contribution Guide

## Before changing code

- Read the project README and architecture notes.
- Check whether a utility or provider already solves the problem.
- Prefer extending existing modules over creating parallel implementations.
- Keep the current folder structure unless a real navigation problem exists.

## Pull request scope

A pull request should describe:

- what changed
- why it changed
- testing performed
- breaking changes, when applicable

Keep unrelated refactors out of feature changes.

## Documentation

Update documentation in the same change when behavior, configuration, commands, or supported providers change.

## Generated files

Do not commit personal generated outputs, API keys, local configuration, virtual environments, or model caches.
