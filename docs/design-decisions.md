# Design Decisions

## CLI projects with an optional API

Each media project remains CLI-first because that is the simplest way to learn, test, and reuse it. `media-process-api` is an optional thin HTTP entry point and does not replace the CLIs.

## Subprocess integration

The API invokes the existing CLIs in subprocesses. This preserves the current folders, avoids collisions between repeated top-level module names, and isolates optional provider dependencies. In-process model reuse can be introduced one media project at a time when repeated loading becomes a measured performance problem.

## Independent projects

Audio, image, and video projects intentionally keep their own small utilities. A shared package would create installation and import complexity before the duplicated code becomes difficult to maintain.

## Demo providers

Every project includes a local demo provider. This ensures a new developer can clone the repository and run the main workflow immediately.

## Configuration files as the default

Normal runtime values use JSON configuration. Secrets remain outside source control through environment variables.

## Optional heavy dependencies

Audio generation with Bark remains available as an optional provider. Its dependencies are separated from the base requirements so the reference workflow stays lightweight.

## No workflow automation yet

GitHub Actions are intentionally absent during rapid foundation work. Selective checks can be added later when their value and trigger rules are clear.

## Honest video foundation

The video demo provider creates a generation request manifest rather than pretending to produce an AI video. Real video providers often use asynchronous jobs, polling, and downloads, so that behavior will be added with the first tested integration.
