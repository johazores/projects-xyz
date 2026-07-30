# Architecture Overview

## Repository model

The toolkit is a collection of independent Python projects rather than one large application. Each project can be opened, understood, and run on its own.

```text
CLI -> configuration -> orchestration -> provider -> output
                         |
                         -> media utilities
```

## Shared project pattern

Each media project contains:

- `cli.py`: parses terminal commands and prints user-facing errors
- `config.py`: loads defaults and optional JSON configuration
- `main.py`: coordinates providers, retries, logging, and output paths
- `providers/`: contains the built-in demo provider and future integrations
- `utils/`: contains focused local helpers
- `examples/`: contains prompts and sample output metadata
- `outputs/`: stores generated files and is ignored by Git
- `docs/`: contains architecture and troubleshooting notes

## Provider boundary

A provider has one responsibility: accept a generation request and create an output. The CLI does not know how the provider works.

This keeps future services isolated. A new provider should not require changes to argument parsing, output naming, retries, or logging unless the provider introduces a genuinely new capability.

## Configuration

Normal settings belong in JSON files because they are visible, portable, and easy to review. Environment variables are limited to:

- the path to a configuration file
- API keys or tokens
- secrets that should not be committed

There is no database or Admin CMS in the current toolkit. Adding either would create unnecessary infrastructure for local command-line projects.

## Dependency strategy

The demo providers use only the Python standard library. Large model libraries and provider SDKs are optional and should be installed only by users who need them.
