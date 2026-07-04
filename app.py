from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
import yaml
import os

app = FastAPI()

# Allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Defaults
# ------------------------

defaults = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000"
}

# ------------------------
# YAML
# ------------------------

yaml_cfg = {}

if os.path.exists("config.development.yaml"):
    with open("config.development.yaml") as f:
        yaml_cfg = yaml.safe_load(f) or {}

# ------------------------
# .env
# ------------------------

env_cfg = dotenv_values(".env")

# ------------------------
# Helpers
# ------------------------

def to_bool(x):
    if isinstance(x, bool):
        return x
    return str(x).lower() in (
        "true",
        "1",
        "yes",
        "on"
    )

def merge():

    cfg = defaults.copy()

    # YAML
    cfg.update(yaml_cfg)

    # .env

    if "NUM_WORKERS" in env_cfg:
        cfg["workers"] = int(env_cfg["NUM_WORKERS"])

    if "APP_DEBUG" in env_cfg:
        cfg["debug"] = to_bool(env_cfg["APP_DEBUG"])

    if "APP_LOG_LEVEL" in env_cfg:
        cfg["log_level"] = env_cfg["APP_LOG_LEVEL"]

    if "APP_API_KEY" in env_cfg:
        cfg["api_key"] = env_cfg["APP_API_KEY"]

    # OS ENV

    if os.getenv("APP_DEBUG") is not None:
        cfg["debug"] = to_bool(os.getenv("APP_DEBUG"))

    if os.getenv("APP_API_KEY") is not None:
        cfg["api_key"] = os.getenv("APP_API_KEY")

    if os.getenv("APP_LOG_LEVEL") is not None:
        cfg["log_level"] = os.getenv("APP_LOG_LEVEL")

    if os.getenv("NUM_WORKERS") is not None:
        cfg["workers"] = int(os.getenv("NUM_WORKERS"))

    return cfg


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    cfg = merge()

    # CLI overrides

    for item in set:

        if "=" not in item:
            continue

        k, v = item.split("=", 1)

        if k in ("port", "workers"):
            cfg[k] = int(v)

        elif k == "debug":
            cfg[k] = to_bool(v)

        else:
            cfg[k] = v

    # Mask secret

    cfg["api_key"] = "****"

    return cfg
