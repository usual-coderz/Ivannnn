from __future__ import annotations

import logging
import os
import re
from typing import List, Tuple

from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)

# Load .env file if it exists
load_dotenv()

# ⚠️ WARNING: Test credentials below - NEVER use in production!
# Replace with your own credentials via .env file or environment variables
# See .env.example for setup instructions
DEFAULT_API_ID = 31495607  # Test only
DEFAULT_API_HASH = "4402573449fdb0514abaef0556fb5610"  # Test only
DEFAULT_BOT_TOKEN = "8070754586:AAF-7yd6_SV028bcTb7iK3TASREOiaHnhEk"  # Test only
DEFAULT_OWNER_IDS = [8518729045]  # Test only
DEFAULT_MONGO_URI = "mongodb+srv://AniaBots_db_user:1122334455%40SkY%2AMoNgO%2A%23%23SaUrAv%21%21AnIaBoTs@aniabots.juoyxrb.mongodb.net/?appName=AniaBots"  # Test only


def _parse_owner_ids(raw: str) -> Tuple[List[int], List[str]]:
    tokens = [x for x in re.split(r"[,\s]+", raw.strip()) if x]
    owners: List[int] = []
    invalid: List[str] = []
    for token in tokens:
        if token.isdigit():
            owners.append(int(token))
        else:
            invalid.append(token)
    return owners, invalid


def _parse_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        LOGGER.error("Invalid %s value %r. Falling back to %s.", name, raw, default)
        return default


class Config:
    ALLOW_DEFAULTS = os.getenv("ALLOW_DEFAULTS", "0") == "1"
    API_ID = _parse_int_env("API_ID", 0)
    API_HASH = os.getenv("API_HASH") or ""
    BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
    _owner_raw = os.getenv("OWNER_IDS", "")
    OWNERS, _OWNER_INVALID = _parse_owner_ids(_owner_raw)
    MONGO_URI = os.getenv("MONGO_URI") or ""
    DB_NAME = os.getenv("DB_NAME", "preban_db")
    PREBAN_WORKERS = _parse_int_env("PREBAN_WORKERS", 2)
    SESSION_CONCURRENCY = _parse_int_env("SESSION_CONCURRENCY", 3)
    QUEUE_MAXSIZE = _parse_int_env("QUEUE_MAXSIZE", 0)
    _prefix_raw = os.getenv("COMMAND_PREFIXES", "/ ! .")
    COMMAND_PREFIXES = [p for p in re.split(r"[,\s]+", _prefix_raw.strip()) if p]
    if not COMMAND_PREFIXES:
        COMMAND_PREFIXES = ["/"]
    elif "/" not in COMMAND_PREFIXES:
        COMMAND_PREFIXES = ["/", *COMMAND_PREFIXES]

    @classmethod
    def validate(cls) -> None:
        errors: List[str] = []
        if not isinstance(cls.API_ID, int) or cls.API_ID <= 0:
            errors.append("API_ID must be a valid integer greater than 0.")
        if not cls.API_HASH:
            errors.append("API_HASH is required and cannot be empty.")
        if not cls.BOT_TOKEN or not re.match(r"^\d+:[\w-]{20,}$", cls.BOT_TOKEN):
            errors.append("BOT_TOKEN is required and must look like '123456:ABC...'.")
        if cls._OWNER_INVALID:
            errors.append(f"OWNER_IDS contains invalid values: {', '.join(cls._OWNER_INVALID)}.")
        if not cls.OWNERS:
            errors.append("OWNER_IDS must contain at least one numeric Telegram user ID.")
        if not cls.MONGO_URI:
            errors.append("MONGO_URI is required and cannot be empty.")
        elif not re.match(r"^mongodb(\+srv)?://", cls.MONGO_URI):
            errors.append("MONGO_URI must be a valid MongoDB connection string.")
        if cls.PREBAN_WORKERS < 1:
            errors.append("PREBAN_WORKERS must be >= 1.")
        if cls.SESSION_CONCURRENCY < 0:
            errors.append("SESSION_CONCURRENCY must be >= 0.")
        if cls.QUEUE_MAXSIZE < 0:
            errors.append("QUEUE_MAXSIZE must be >= 0.")

        if errors:
            for err in errors:
                LOGGER.error("Config validation error: %s", err)
            
            if cls.ALLOW_DEFAULTS:
                LOGGER.warning(
                    "⚠️ ALLOW_DEFAULTS=1 - Using test credentials (UNSAFE for production!)"
                )
                if cls.API_ID <= 0:
                    cls.API_ID = DEFAULT_API_ID
                if not cls.API_HASH:
                    cls.API_HASH = DEFAULT_API_HASH
                if not cls.BOT_TOKEN or not re.match(r"^\d+:[\w-]{20,}$", cls.BOT_TOKEN):
                    cls.BOT_TOKEN = DEFAULT_BOT_TOKEN
                if not cls.OWNERS:
                    cls.OWNERS = DEFAULT_OWNER_IDS.copy()
                if not cls.MONGO_URI or not re.match(r"^mongodb(\+srv)?://", cls.MONGO_URI):
                    cls.MONGO_URI = DEFAULT_MONGO_URI
                return
            
            error_msg = "\n❌ Configuration Invalid!\n\nRequired environment variables not set:\n"
            error_msg += "1. API_ID - Your Telegram API ID\n"
            error_msg += "2. API_HASH - Your Telegram API Hash\n"
            error_msg += "3. BOT_TOKEN - Your Telegram Bot Token\n"
            error_msg += "4. OWNER_IDS - Your Telegram User ID\n"
            error_msg += "5. MONGO_URI - MongoDB connection string\n\n"
            error_msg += "Setup options:\n"
            error_msg += "A) Create a .env file with your credentials (see .env.example)\n"
            error_msg += "B) Set environment variables directly\n"
            error_msg += "C) For local testing only: set ALLOW_DEFAULTS=1\n"
            
            LOGGER.error(error_msg)
            raise SystemExit(1)
