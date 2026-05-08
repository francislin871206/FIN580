"""
==============================================================================
  FIN580 Multi-Agent Trading System — Agents Package
==============================================================================
  Provides config loading, prompt template loading, and project-root resolution.
==============================================================================
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env from project root ─────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


def get_project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return _PROJECT_ROOT


def load_config() -> dict:
    """Load config.yaml from the project root. Returns a dict."""
    config_path = _PROJECT_ROOT / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt(template_name: str, **kwargs) -> str:
    """
    Load a prompt template from the prompts/ directory.

    Placeholders use {VARIABLE_NAME} syntax and are filled via
    str.replace() to avoid conflicts with JSON braces in templates.

    Args:
        template_name: Filename in prompts/ (e.g., "event_classification.txt")
        **kwargs: Key-value pairs for placeholder replacement.
                  Keys should match placeholder names (case-insensitive).
    Returns:
        The filled prompt string.
    """
    prompt_path = _PROJECT_ROOT / "prompts" / template_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()

    for key, value in kwargs.items():
        template = template.replace(f"{{{key.upper()}}}", str(value))

    return template


def resolve_path(relative_path: str) -> Path:
    """Resolve a path relative to the project root."""
    return _PROJECT_ROOT / relative_path
