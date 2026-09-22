# Security Policy

CI Health Monitor is an offline, read-only analyzer. It does not require credentials and should never be given tokens.

## Supported version
Security fixes target the latest version on `main`.

## Reporting a vulnerability
Please use GitHub's private vulnerability reporting feature when available. Otherwise open a minimal issue that does **not** disclose secrets, private repository names, private run URLs, or exploit details that would put users at immediate risk.

## Data handling
Input JSON remains local to the process. The tool makes no network requests. Exported workflow metadata can still be sensitive; sanitize it before sharing. The example file in this repository is synthetic and uses reserved `.invalid` URLs.