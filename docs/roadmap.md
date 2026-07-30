# Roadmap

## Foundation — complete

- [x] Review the original repository
- [x] Establish a consistent project structure
- [x] Convert audio processing to a CLI-first reference project
- [x] Add image processing foundation
- [x] Add video processing foundation
- [x] Add demo providers and example prompts
- [x] Add repository and project documentation
- [x] Add output management, logging, retries, and graceful errors
- [x] Add a lightweight FastAPI entry point for all media projects
- [x] Add provider and model discovery endpoints
- [x] Add unified API examples and documentation

## Provider expansion

- [ ] Add one tested text-to-image provider
- [ ] Add one tested text-to-video provider
- [ ] Add additional audio generation providers
- [ ] Add local model examples
- [ ] Document provider capabilities and limitations

## API evolution

- [ ] Add a real local image provider and expose its model metadata
- [ ] Add a real local video provider and job polling only when required
- [ ] Add optional API fields only when provider capabilities require them
- [ ] Move selected providers in-process when model reload time becomes a measured bottleneck
- [ ] Add lightweight API tests during stabilization

## Workflow improvements

- [ ] Add batch prompt files
- [ ] Add generation metadata beside outputs
- [ ] Add optional seed support where providers support it
- [ ] Add cancellation and polling helpers for asynchronous providers
- [ ] Add lightweight tests for provider contracts and configuration

## Later stabilization

- [ ] Select supported Python versions
- [ ] Add formatting and static analysis configuration
- [ ] Add selective GitHub Actions only after workflows stabilize
- [ ] Review whether repeated utilities justify a small shared package
- [ ] Add release tags and changelog conventions
