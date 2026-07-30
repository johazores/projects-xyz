# Security Policy

## Reporting

Do not open a public issue for vulnerabilities involving command execution, unsafe file paths, uploaded media, API exposure, provider credentials, model loading, or untrusted FFmpeg input.

Contact the maintainer through the GitHub profile with a sanitized reproduction, affected project, expected behavior, actual behavior, and potential impact.

## Security boundaries

The toolkit processes local files and may invoke FFmpeg, optional machine-learning libraries, and configured providers. Users are responsible for trusted input, dependency installation, model sources, API credentials, and output storage.

## Safe operation

- Process files from trusted sources.
- Keep provider keys in environment variables.
- Review FFmpeg and model dependencies before installation.
- Run the API locally unless authentication, limits, and deployment security are deliberately added.
- Do not expose generated files or uploads through an unprotected public server.
- Do not commit local configuration, model caches, or personal media.
