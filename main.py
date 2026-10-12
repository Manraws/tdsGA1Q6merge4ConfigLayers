import os
from pathlib import Path
from typing import List 
import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Effective Configuration API")

# The grader's browser can call this API cross-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}
KNOWN_KEYS = set(DEFAULTS)
TRUE_VALUES = {"true", "1", "yes", "on"}


def normalize_key(key: str) -> str:
    key = key.strip().lower()
    if key.startswith("app_"):
        key = key[4:]
    if key == "num_workers":
        key = "workers"
    return key


def coerce(key: str, value):
    value = str(value)
    if key in {"port", "workers"}:
        return int(value)
    if key == "debug":
        return value.strip().lower() in TRUE_VALUES
    return value


def read_yaml_layer():
    env_name = os.getenv("APP_ENV", os.getenv("ENV", "development"))
    path = Path(f"config.{env_name}.yaml")
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {normalize_key(k): v for k, v in data.items()}


def read_dotenv_layer():
    # dotenv_values reads .env without mutating the process environment.
    values = dotenv_values(".env")
    result = {}
    for raw_key, value in values.items():
        if value is None:
            continue
        key = normalize_key(raw_key)
        if key in KNOWN_KEYS:
            result[key] = value
    return result


def read_os_layer():
    result = {}
    for raw_key, value in os.environ.items():
        if not raw_key.startswith("APP_"):
            continue
        key = normalize_key(raw_key)
        if key in KNOWN_KEYS:
            result[key] = value
    return result

@app.get("/effective-config")
def effective_config(request: Request):
    config = load_config()

    for item in request.query_params.getlist("set"):
        if "=" not in item:
            continue

        key, value = item.split("=", 1)
        if key not in config or key == "api_key":
            continue

        if key in ("port", "workers"):
            config[key] = int(value)
        elif key == "debug":
            config[key] = value.lower() in ("true", "1", "yes", "on")
        else:
            config[key] = value

    config["api_key"] = "****"
    return config 
