# Image Architecture

```text
CLI -> config -> main
                  ├── generation provider
                  ├── prompt preset
                  ├── sequential batch loop
                  └── rembg background removal
```

Prompt presets are plain JSON. They add reusable wording without coupling the toolkit to one model or provider.

Batch generation is intentionally sequential. It is easier to debug and avoids assuming that every local or cloud provider supports safe parallel requests.

Background removal is a focused utility rather than an image provider because it transforms an existing file instead of generating a new image from a prompt.

The next real generation integration should be a thin adapter to a tested local system such as ComfyUI or Diffusers.
