from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional


CONFIG_DIR = Path("/workspace/config")
CONFIG_FILE = CONFIG_DIR / "system.json"


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _read_config() -> Dict[str, str]:
    _ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {}
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        # Normalizamos solo las claves esperadas
        result: Dict[str, str] = {}
        if isinstance(data.get("source_folder"), str):
            result["source_folder"] = data["source_folder"]
        if isinstance(data.get("docs_folder"), str):
            result["docs_folder"] = data["docs_folder"]
        return result
    except Exception:
        # Si el JSON está corrupto, devolvemos vacío sin romper el flujo
        return {}


def _write_config(config: Dict[str, str]) -> Dict[str, str]:
    _ensure_config_dir()
    sanitized: Dict[str, str] = {}
    if isinstance(config.get("source_folder"), str):
        sanitized["source_folder"] = config["source_folder"]
    if isinstance(config.get("docs_folder"), str):
        sanitized["docs_folder"] = config["docs_folder"]
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(sanitized, f, ensure_ascii=False, indent=2)
    return sanitized


def get_system_config() -> Dict[str, str]:
    """Lee la configuración actual del sistema a analizar.

    Returns:
        Dict[str, str]: Diccionario con posibles claves "source_folder" y "docs_folder".
    """
    return _read_config()


def select_source_folder(path: str) -> Dict[str, str]:
    """Valida y persiste la carpeta de código fuente.

    Args:
        path (str): Ruta absoluta al directorio del código fuente.

    Returns:
        Dict[str, str]: Configuración actualizada.

    Raises:
        ValueError: Si la ruta no existe o no es un directorio.
    """
    if not path or not os.path.isdir(path):
        raise ValueError("Ruta de fuente inválida: debe existir y ser un directorio")
    config = _read_config()
    config["source_folder"] = str(Path(path).resolve())
    return _write_config(config)


def select_docs_folder(path: str) -> Dict[str, str]:
    """Valida y persiste la carpeta de documentación base del usuario.

    Args:
        path (str): Ruta absoluta al directorio de documentación.

    Returns:
        Dict[str, str]: Configuración actualizada.

    Raises:
        ValueError: Si la ruta no existe o no es un directorio.
    """
    if not path or not os.path.isdir(path):
        raise ValueError("Ruta de docs inválida: debe existir y ser un directorio")
    config = _read_config()
    config["docs_folder"] = str(Path(path).resolve())
    return _write_config(config)


def initialize_config_if_missing() -> Dict[str, str]:
    """Crea `config/system.json` vacío si no existe.

    Returns:
        Dict[str, str]: Configuración actual (posiblemente vacía).
    """
    _ensure_config_dir()
    if not CONFIG_FILE.exists():
        return _write_config({})
    return _read_config()

