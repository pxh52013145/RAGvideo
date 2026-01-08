from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def _default_config_dir() -> Path:
    custom = (os.getenv("RAGVIDEO_CONFIG_DIR") or "").strip()
    if custom:
        return Path(custom)

    if os.name == "nt":
        base = os.getenv("APPDATA")
        if base:
            return Path(base) / "RAGVideo"
        return Path.home() / "AppData" / "Roaming" / "RAGVideo"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "RAGVideo"

    return Path(os.getenv("XDG_CONFIG_HOME") or (Path.home() / ".config")) / "RAGVideo"


def _mask_secret(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return ""
    if len(v) <= 8:
        return "*" * len(v)
    return f"{v[:4]}{'*' * (len(v) - 8)}{v[-4:]}"


class DifyConfigManager:
    """
    Persist Dify settings locally so the desktop EXE can be configured via UI
    without editing `.env` in the packaged resources.
    """

    def __init__(self, filepath: str | Path | None = None):
        if filepath is None:
            filepath = _default_config_dir() / "dify.json"
        self.path = Path(filepath)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read_raw(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_raw(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def _read_state(self) -> tuple[str, dict[str, dict[str, Any]]]:
        """
        Returns (active_profile, profiles).

        Storage format (v2):
        {
          "version": 2,
          "active_profile": "default",
          "profiles": { "default": { ... }, "server": { ... } }
        }

        Backward compatible with legacy flat dict stored in `dify.json`.
        """
        raw = self._read_raw()
        if isinstance(raw, dict) and isinstance(raw.get("profiles"), dict):
            profiles_raw = raw.get("profiles") or {}
            profiles: dict[str, dict[str, Any]] = {}
            for name, cfg in profiles_raw.items():
                if not isinstance(name, str) or not name.strip():
                    continue
                profiles[name.strip()] = cfg if isinstance(cfg, dict) else {}

            active = str(raw.get("active_profile") or "").strip() or "default"
            if profiles:
                if active not in profiles:
                    active = next(iter(profiles.keys()))
            else:
                profiles = {"default": {}}
                active = "default"

            return active, profiles

        # Legacy format: a single config dict.
        legacy_cfg = raw if isinstance(raw, dict) else {}
        return "default", {"default": dict(legacy_cfg)}

    def _write_state(self, *, active_profile: str, profiles: dict[str, dict[str, Any]]) -> None:
        active = (active_profile or "").strip() or "default"
        safe_profiles: dict[str, dict[str, Any]] = {}
        for name, cfg in (profiles or {}).items():
            n = (name or "").strip()
            if not n:
                continue
            safe_profiles[n] = cfg if isinstance(cfg, dict) else {}

        if not safe_profiles:
            safe_profiles = {"default": {}}
            active = "default"
        elif active not in safe_profiles:
            active = next(iter(safe_profiles.keys()))

        self._write_raw(
            {
                "version": 2,
                "active_profile": active,
                "profiles": safe_profiles,
            }
        )

    def get_active_profile(self) -> str:
        active, _ = self._read_state()
        return active

    def get(self) -> dict[str, Any]:
        active, profiles = self._read_state()
        return profiles.get(active, {})

    def update(self, patch: dict[str, Any]) -> dict[str, Any]:
        active, profiles = self._read_state()
        cfg = dict(profiles.get(active) or {})
        for k, v in (patch or {}).items():
            if v is None:
                continue
            cfg[k] = v
        profiles[active] = cfg
        self._write_state(active_profile=active, profiles=profiles)
        return cfg

    def list_profiles(self) -> dict[str, dict[str, Any]]:
        _, profiles = self._read_state()
        return profiles

    def set_active_profile(self, name: str) -> None:
        target = (name or "").strip()
        if not target:
            raise ValueError("Profile name cannot be empty")
        active, profiles = self._read_state()
        if target not in profiles:
            raise KeyError(f"Profile not found: {target}")
        if target == active:
            return
        self._write_state(active_profile=target, profiles=profiles)

    def upsert_profile(
        self,
        name: str,
        patch: dict[str, Any] | None = None,
        *,
        clone_from: str | None = None,
        activate: bool = False,
    ) -> dict[str, Any]:
        profile_name = (name or "").strip()
        if not profile_name:
            raise ValueError("Profile name cannot be empty")

        active, profiles = self._read_state()
        base: dict[str, Any] = {}
        if clone_from is not None:
            source = (clone_from or "").strip()
            if not source:
                raise ValueError("clone_from cannot be empty")
            if source not in profiles:
                raise KeyError(f"Profile not found: {source}")
            base = dict(profiles[source] or {})
        else:
            base = dict(profiles.get(profile_name) or {})

        for k, v in (patch or {}).items():
            if v is None:
                continue
            base[k] = v

        profiles[profile_name] = base
        new_active = profile_name if activate else active
        self._write_state(active_profile=new_active, profiles=profiles)
        return base

    def delete_profile(self, name: str) -> None:
        target = (name or "").strip()
        if not target:
            raise ValueError("Profile name cannot be empty")
        active, profiles = self._read_state()
        if target not in profiles:
            return
        if len(profiles) <= 1:
            raise ValueError("Cannot delete the last profile")
        del profiles[target]
        new_active = active
        if active == target:
            new_active = next(iter(profiles.keys()))
        self._write_state(active_profile=new_active, profiles=profiles)

    def clear(self) -> None:
        self._write_state(active_profile="default", profiles={"default": {}})

    def get_safe(self) -> dict[str, Any]:
        active, profiles = self._read_state()
        data = profiles.get(active) or {}
        service_key = str(data.get("service_api_key") or "")
        app_key = str(data.get("app_api_key") or "")
        return {
            "active_profile": active,
            "base_url": data.get("base_url") or "",
            "dataset_id": data.get("dataset_id") or "",
            "note_dataset_id": data.get("note_dataset_id") or "",
            "transcript_dataset_id": data.get("transcript_dataset_id") or "",
            "indexing_technique": data.get("indexing_technique") or "",
            "app_user": data.get("app_user") or "",
            "timeout_seconds": data.get("timeout_seconds"),
            "service_api_key_set": bool(service_key.strip()),
            "app_api_key_set": bool(app_key.strip()),
            "service_api_key_masked": _mask_secret(service_key),
            "app_api_key_masked": _mask_secret(app_key),
            "config_path": str(self.path),
        }

    def get_profiles_safe(self) -> dict[str, Any]:
        active, profiles = self._read_state()
        safe_profiles: list[dict[str, Any]] = []
        for name, cfg in sorted(profiles.items(), key=lambda kv: kv[0].lower()):
            service_key = str((cfg or {}).get("service_api_key") or "")
            app_key = str((cfg or {}).get("app_api_key") or "")
            safe_profiles.append(
                {
                    "name": name,
                    "base_url": (cfg or {}).get("base_url") or "",
                    "dataset_id": (cfg or {}).get("dataset_id") or "",
                    "note_dataset_id": (cfg or {}).get("note_dataset_id") or "",
                    "transcript_dataset_id": (cfg or {}).get("transcript_dataset_id") or "",
                    "indexing_technique": (cfg or {}).get("indexing_technique") or "",
                    "app_user": (cfg or {}).get("app_user") or "",
                    "timeout_seconds": (cfg or {}).get("timeout_seconds"),
                    "service_api_key_set": bool(service_key.strip()),
                    "app_api_key_set": bool(app_key.strip()),
                    "service_api_key_masked": _mask_secret(service_key),
                    "app_api_key_masked": _mask_secret(app_key),
                }
            )

        return {
            "active_profile": active,
            "profiles": safe_profiles,
            "config_path": str(self.path),
        }
