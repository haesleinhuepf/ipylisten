from __future__ import annotations

import configparser
import os
from pathlib import Path
from typing import Optional


def get_config_dir() -> Path:
    """Get the configuration directory for ipylisten."""
    home_dir = Path.home()
    config_dir = home_dir / ".cache" / "ipylisten"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Get the path to the config.ini file."""
    return get_config_dir() / "config.ini"


def _get_config() -> configparser.ConfigParser:
    """Get the configuration parser, creating the config file if it doesn't exist."""
    config_path = get_config_path()
    config = configparser.ConfigParser()
    
    if config_path.exists():
        # Read using UTF-8 to preserve any non-ASCII chars
        config.read(config_path, encoding='utf-8')
    else:
        # Create default config
        config['DEFAULT'] = {'prefix_text': ''}
        _save_config(config)
    
    return config


def _save_config(config: configparser.ConfigParser) -> None:
    """Save the configuration to the config file."""
    config_path = get_config_path()
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)


def set_prefix(prefix_text: str) -> None:
    """Set the prefix text that will be prepended to all corrected text.
    
    Args:
        prefix_text: The text to prepend to corrected text from listen()
    """
    config = _get_config()
    
    # Ensure DEFAULT section exists
    if 'DEFAULT' not in config:
        config.add_section('DEFAULT')

    # Normalize Windows newlines and escape newlines for INI storage
    normalized = prefix_text.replace('\r\n', '\n')
    escaped = normalized.replace('\n', r'\n')
    config['DEFAULT']['prefix_text'] = escaped
    _save_config(config)


def get_prefix() -> str:
    """Get the current prefix text.
    
    Returns:
        The current prefix text, or empty string if none is set.
    """
    config = _get_config()
    raw = config.get('DEFAULT', 'prefix_text', fallback='')
    # Only unescape our stored newline representation
    return raw.replace(r'\n', '\n')


def clear_prefix() -> None:
    """Clear the prefix text."""
    set_prefix('')
