import os
from pathlib import Path

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULTS = {
    "port": 8000,
    "workers": 3,
    "debug": False,
    "log_level": "info",
    "api_key": "",
}

def convert_value(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return str(value).lower() in ("true", "1", "yes", "on")
    return value

def normalize_key(key):
    key = key.lower()
    if key.startswith("app_"):
        key = key[4:]
    if key == "num_workers":
        key = "workers"
    return key

def load_config():
    config = DEFAULTS.copy()

    env_name = os.getenv("APP_ENV", "development")
    yaml_path = Path(f"config.{env_name}.yaml")

    if yaml_path.exists():
        with yaml_path.open() as f:
            yaml_config = yaml.safe_load(f) or {}
        for key, value in yaml_config.items():
            key = normalize_key(key)
            if key in config:
                config[key] = convert_value(key, value)

    dotenv_config = dotenv_values(".env")
    for key, value in dotenv_config.items():
        if value is None:
            continue
        key = normalize_key(key)
        if key in config:
            config[key] = convert_value(key, value)

    for key, value in os.environ.items():
        if not key.startswith("APP_"):
            continue
        normalized = normalize_key(key)
        if normalized in config:
            config[normalized] = convert_value(normalized, value)

    return config

@app.get("/effective-config")
def effective_config(request: Request):
    config = load_config()

    for item in request.query_params.getlist("set"):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = normalize_key(key.strip())
        if key in config and key != "api_key":
            config[key] = convert_value(key, value)

    config["api_key"] = "****"
    return config
```
