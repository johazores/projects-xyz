# FAQ

## Are the demo providers real AI models?

No. They create deterministic local outputs so the complete CLI, configuration, logging, retry, and output flow can be tested without credentials or model downloads.

## Why not include every provider now?

Provider APIs, capabilities, and billing models change. Adding untested adapters would make the repository look complete while increasing maintenance risk. The foundation makes providers easy to add one at a time.

## Why use JSON configuration instead of only environment variables?

JSON is easier to read, review, copy, and version as an example. Environment variables remain useful for secrets and the config-file path.

## Why is there no database or Admin CMS?

These projects are local command-line tools. A database and CMS would add infrastructure without solving a current requirement. They can be considered later if the toolkit becomes a hosted application.

## Why are the projects separate?

A developer can learn or use one media type without installing dependencies for the others.

## Why is there no CI?

The repository is still in active foundation development. Local smoke checks are enough until commands, providers, and supported Python versions stabilize.
