# Video Troubleshooting

## No video file is created

The initial demo provider creates a JSON generation request artifact. This is expected.

## The config file fails to load

Confirm the file is valid JSON and uses only keys from `config.json.example`.

## A provider is unknown

Only `demo` is included initially. Implement and register a real provider before selecting another name.

## A future provider stays pending

Provider implementations should include a documented timeout and clear status logging. Polling should use the shared retry pattern only when the provider's API behavior makes retries safe.
