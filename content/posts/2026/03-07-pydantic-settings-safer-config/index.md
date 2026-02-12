---
date: 2026-03-07
title: "Pydantic Settings: A Safer Config Option for your Python Apps"
description: |-
  Environment variables are easy to start with but hard to scale safely.
  This post shows how Pydantic Settings gives you typed, validated config with clean layering for local dev and cloud secrets.
slug: pydantic-settings-safer-config
image: /images/posts/2026/03-07-pydantic-settings-safer-config.jpg
tags:
  - Python
  - Configuration
  - Tooling
---

Environment variables are the default way many Python apps handle configuration.
They are simple, portable, and work in every deployment environment.
But as soon as you add more than a handful of settings, raw env vars become fragile and hard to reason about.

Pydantic used to solve this with `BaseSettings` in v1.
In v2 the approach moved to a dedicated package, `pydantic-settings`, which is what we will use here.
If you want more Python posts, check the [Python]({{< ref "/tags/python" >}}) tag.

## Why Env Vars Alone Fall Short

Env vars are all strings, which means type errors are easy to miss until runtime.
Defaults often live in multiple places, and missing values can fail late in your startup path.
You also end up with scattered config in `os.environ` lookups across the codebase, which makes change tracking and testing harder.

## What Pydantic Settings Gives You

Pydantic Settings gives you a single, typed place to declare configuration for your app.
You get validation, sensible defaults, clear precedence rules, and better error messages when something is missing or invalid.
It also keeps the wiring between env vars, `.env` files, and secret stores predictable.

If you want the short version, it gives you:

- One schema to scan instead of scattered `os.environ` lookups.
- Type conversion and validation as config is loaded.
- A predictable order for where values come from and how they override each other.
- Easier testing because you can override settings explicitly.

## What Belongs In Settings

Settings work best for configuration that varies by environment but does not change at runtime.
That usually includes things like:

- Connection strings, hostnames, and ports.
- Feature flags and operational toggles.
- Limits, timeouts, and worker counts.
- Third-party API keys and credentials (loaded from secret stores, not committed).

Keeping these values in one settings class makes it obvious what your app needs to run and how to configure it for each environment.

## Quick Start With Pydantic Settings

Start by installing the package and defining a minimal settings class.
We will keep this example small but complete enough to run.

```bash
pip install pydantic-settings
```

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    environment: str = "local"
    database_url: str
    log_level: str = "INFO"
    max_workers: int = Field(default=4, ge=1)

settings = Settings()
print(settings.model_dump())
```

This reads from environment variables like `APP_DATABASE_URL` and validates types.
If `APP_DATABASE_URL` is missing, Pydantic fails fast with a clear error instead of your app stumbling later.
Defaults are not required to exist in the environment, and Pydantic will use them directly when a variable is not set.

### How env var names map to settings fields

By default, the environment variable name matches the field name, and `env_prefix` simply adds a prefix to every field.
With the `env_prefix="APP_"` used above, the mapping looks like this:

- `environment` -> `APP_ENVIRONMENT`
- `database_url` -> `APP_DATABASE_URL`
- `log_level` -> `APP_LOG_LEVEL`
- `max_workers` -> `APP_MAX_WORKERS`

Environment variable names are case-insensitive by default, so `APP_DATABASE_URL` and `app_database_url` are treated the same unless you enable `case_sensitive=True`.

### Defaults vs required values

Any field with a default value is optional; Pydantic will use the default when no matching environment variable is set.
Fields without defaults, such as `database_url`, are required and must be present in the environment (or supplied in code) or you will get a validation error on startup.
That means you can set only the required variables and let the defaults cover the rest.

For example, if you only define `APP_DATABASE_URL`, you will still get:

- `environment="local"`
- `log_level="INFO"`
- `max_workers=4`

## Layering Local Dev With .env Files

For local development, you often want a `.env` file that provides defaults without committing secrets to the repo.
Pydantic Settings supports this directly.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str
    log_level: str = "INFO"
```

With this setup, values are loaded from multiple places in a consistent order.
By default, the priority is:

- Explicit arguments passed to `Settings(...)`
- Environment variables
- Variables from the `.env` file
- Default values in the class

That means your `.env` file provides local defaults, but a host environment variable will override it when present.
For example, if `.env` contains `APP_LOG_LEVEL=INFO` and your deployment sets `APP_LOG_LEVEL=DEBUG`, the environment wins so production can override local settings safely.
This is intentional: environment variables are the most reliable way for a platform to inject configuration at runtime.
You can also pass a list of env files if you want layered config, with later files overriding earlier ones.

Here is a small `.env` example to make the behavior concrete:

```bash
APP_DATABASE_URL=postgresql://localhost:5432/app
APP_LOG_LEVEL=INFO
```

And here is an example of multiple `.env` files:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=(".env", ".env.local"),
    )

    database_url: str
    log_level: str = "INFO"
```

In this setup, `.env.local` overrides `.env`, and environment variables override both.
That lets you keep team defaults in `.env`, personal overrides in `.env.local`, and production values in the host environment.

## Secret Stores in Cloud Environments

In production you should not store secrets in plain env files.
Instead, use a cloud secret store and inject the values into your process at startup.
AWS Secrets Manager, GCP Secret Manager, and Azure Key Vault all provide ways to fetch secrets securely.

Pydantic Settings can read from these systems directly by adding a secrets source with `settings_customise_sources`.
This keeps the integration inside your settings class instead of spreading secret fetch logic across your app.

Here is a minimal AWS example:

```python
import os

from pydantic_settings import (
    AWSSecretsManagerSettingsSource,
    BaseSettings,
    PydanticBaseSettingsSource,
)

class Settings(BaseSettings):
    database_url: str
    api_key: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        aws_settings = AWSSecretsManagerSettingsSource(
            settings_cls,
            os.environ["AWS_SECRETS_MANAGER_SECRET_ID"],
        )
        return (init_settings, env_settings, dotenv_settings, aws_settings)

settings = Settings()
```

To use other providers, swap in their source classes:

- AWS Secrets Manager: `AWSSecretsManagerSettingsSource` (requires a `secret_id`).
- Azure Key Vault: `AzureKeyVaultSettingsSource` with `azure-identity` for credentials.
- GCP Secret Manager: `GoogleSecretManagerSettingsSource` and the `pydantic-settings[gcp-secret-manager]` extra.

These sources can be combined with env vars and `.env` files, and the order in `settings_customise_sources` controls the precedence.
If your platform already injects secrets as environment variables, you can skip the custom source and let Pydantic Settings read them directly.

## Practical Tips

- Fail fast by keeping required values required.
- Keep settings grouped and small rather than passing raw env vars through your app.
- Avoid loading secrets at import time so your modules stay testable.
- Document your settings in a single place so new contributors know what is required.

## Wrapping Up

Pydantic Settings gives you a typed, validated configuration layer that scales beyond a few environment variables.
You can start small with a single `Settings` class, layer local `.env` files for convenience, and plug in cloud secret stores in production.
Now you know how to layer safe settings parsing for your Python apps.
