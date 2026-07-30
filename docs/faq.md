# FAQ

## Is the toolkit useful without additional generation providers?

Yes. Transcription, subtitles, audio cleanup, background removal, video resizing, frame extraction, prompt presets, and batching are practical local operations.

## Are the demo providers real AI models?

No. They remain lightweight smoke-test providers. Real generation should use tested providers added behind the existing contracts.

## Why not build a model manager?

ComfyUI, Diffusers, faster-whisper, rembg, and provider SDKs already manage their own models. The toolkit should integrate them with thin adapters instead of duplicating that complexity.

## Why use local file paths in the API?

The server is for one developer on one machine. Local paths avoid uploads and copies of large files. The API should remain bound to localhost unless security is added.

## Why are batches sequential?

Different models have different memory and rate-limit behavior. Sequential execution is predictable and easy to debug. Parallelism can be added for a specific provider after measurement.

## Why is there no database?

Project folders are enough for the current personal workflow. An asset database should be added only when files become difficult to find or annotate.

## Why is there no CI?

The repository is in rapid active development. Selective CI can be introduced after commands, supported Python versions, and provider dependencies stabilize.
