# Adding a Provider

Providers belong in the individual media projects, not in the FastAPI application.

## Example: add an image provider

Create `image-process/providers/my_provider.py`:

```python
from pathlib import Path

from config import ImageConfig


class MyImageProvider:
    file_extension = ".png"

    def generate(
        self,
        prompt: str,
        negative_prompt: str | None,
        output_path: Path,
        config: ImageConfig,
    ) -> Path:
        if not prompt.strip():
            raise ValueError("A prompt is required.")

        # Call the local model or provider API here.
        # Save the final image to output_path.
        return output_path
```

Register it in `image-process/providers/__init__.py`:

```python
if normalized == "my-provider":
    from providers.my_provider import MyImageProvider

    return MyImageProvider()
```

Test the CLI before the API:

```bash
cd image-process
python cli.py generate --provider my-provider --prompt "A quiet mountain lake"
```

Then add discoverability metadata in `media-process-api/app/config.py`:

```python
"image": {
    "demo": ["prompt-card-svg"],
    "my-provider": ["my-model-name"],
},
```

The existing `/image/generate` route now accepts `"provider": "my-provider"` without route changes.

## Provider rules

- Keep the provider focused on one external model or service.
- Validate only provider-specific constraints inside the provider.
- Save the final artifact to the supplied output path.
- Return the output path.
- Raise readable exceptions.
- Add a dependency only when the provider requires it.
- Keep large optional dependencies out of the base API requirements.
