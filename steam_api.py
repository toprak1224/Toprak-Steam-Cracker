import requests
import json
import os

from config import (
    STEAM_APP_LIST_CACHE_FILE,
    STEAM_APP_LIST_HEADERS,
    STEAM_APP_LIST_GITHUB_SOURCES,
    VERSION_CHECK_URL,
    MANIFEST_HUB_REFS_URL,
)

def _extract_steam_web_api_apps(payload):
    if isinstance(payload, dict):
        return payload.get('applist', {}).get('apps', [])
    return []

def _extract_steamcmd_apps(payload):
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get('apps'), list):
        return payload['apps']
    data = payload.get('data')
    if isinstance(data, dict):
        if isinstance(data.get('apps'), list):
            return data['apps']
        if isinstance(data.get('list'), list):
            return data['list']
    return []

STEAM_APP_LIST_SOURCES = [
    {
        "name": "steam_web_api",
        "url": "https://api.steampowered.com/ISteamApps/GetAppList/v2/",
        "extract": _extract_steam_web_api_apps,
        "timeout": 45,
    },
    {
        "name": "steamcmd_api",
        "url": "https://api.steamcmd.net/v1/apps",
        "extract": _extract_steamcmd_apps,
        "timeout": 45,
    },
]

def _normalize_app_entries(entries):
    normalized = {}
    keys = ('appid', 'app_id', 'appID', 'id', 'appId', 'game_id')
    name_keys = ('name', 'Name', 'title', 'app_name', 'AppName', 'label')

    for item in entries or []:
        app_id = None
        name = ""

        if isinstance(item, dict):
            for key in keys:
                if key in item and item[key]:
                    app_id = item[key]
                    break
            for key in name_keys:
                if key in item and item[key]:
                    name = item[key]
                    break
        elif isinstance(item, (int, float)):
            app_id = int(item)
        elif isinstance(item, str) and item.isdigit():
            app_id = item

        if app_id is None:
            continue

        app_id = str(app_id)
        if not app_id.isdigit():
            continue

        if not name:
            name = normalized.get(app_id, f"App {app_id}")

        normalized[app_id] = name

    ordered = sorted(normalized.items(), key=lambda pair: int(pair[0]))
    return [{"appid": app_id, "name": name} for app_id, name in ordered]

def _load_cached_app_list():
    try:
        if os.path.exists(STEAM_APP_LIST_CACHE_FILE):
            with open(STEAM_APP_LIST_CACHE_FILE, 'r', encoding='utf-8') as cache_file:
                cached = json.load(cache_file)
            if isinstance(cached, list):
                valid = [entry for entry in cached if 'appid' in entry and 'name' in entry]
                if valid:
                    return valid
    except Exception:
        pass
    return []

def _save_app_list_cache(apps):
    try:
        with open(STEAM_APP_LIST_CACHE_FILE, 'w', encoding='utf-8') as cache_file:
            json.dump(apps, cache_file, ensure_ascii=False)
    except Exception:
        pass

def fetch_latest_version(session=None):
    if not VERSION_CHECK_URL:
        return None
    session = session or requests.Session()
    response = session.get(VERSION_CHECK_URL, headers=STEAM_APP_LIST_HEADERS, timeout=15)
    response.raise_for_status()
    return response.text.strip()

def _fetch_github_app_lists(session):
    combined = []
    errors = []

    for source in STEAM_APP_LIST_GITHUB_SOURCES:
        try:
            response = session.get(source["url"], headers=STEAM_APP_LIST_HEADERS, timeout=60)
            response.raise_for_status()
            data = response.json()
            normalized = _normalize_app_entries(data)
            suffix = source.get("name_suffix", "")
            if suffix:
                for entry in normalized:
                    entry['name'] = f"{entry.get('name', '')}{suffix}".strip()
            combined.extend(normalized)
        except Exception as exc:
            errors.append(f"{source['name']}: {exc}")

    if combined:
        unique = {}
        for entry in combined:
            app_id = entry.get('appid')
            if not app_id:
                continue
            unique[app_id] = entry
        return list(unique.values())

    if errors:
        raise RuntimeError("; ".join(errors))
    return []

def _filter_supported_games(apps, session):
    if not MANIFEST_HUB_REFS_URL:
        return apps
    try:
        res = session.get(MANIFEST_HUB_REFS_URL, timeout=15)
        res.raise_for_status()

        supported_ids = set()
        for line in res.text.split('\n'):
            if "refs/heads/" in line:
                branch = line.split("refs/heads/")[-1].strip()
                if branch != "main":
                    supported_ids.add(branch)

        filtered = [app for app in apps if str(app.get("appid")) in supported_ids]
        return filtered
    except Exception:
        return apps

def fetch_steam_app_list(session=None):
    cached = _load_cached_app_list()
    if cached and len(cached) > 50000:  # Eğer cache varsa ve doluysa (filtreli hali)
        return cached

    session = session or requests.Session()
    errors = []

    try:
        github_apps = _fetch_github_app_lists(session)
        if github_apps:
            filtered_apps = _filter_supported_games(github_apps, session)
            _save_app_list_cache(filtered_apps)
            return filtered_apps
    except Exception as exc:
        errors.append(f"github_sources: {exc}")

    for source in STEAM_APP_LIST_SOURCES:
        try:
            response = session.get(
                source["url"],
                headers=STEAM_APP_LIST_HEADERS,
                timeout=source.get("timeout", 30)
            )
            response.raise_for_status()
            raw_entries = source["extract"](response.json())
            apps = _normalize_app_entries(raw_entries)
            if apps:
                filtered_apps = _filter_supported_games(apps, session)
                _save_app_list_cache(filtered_apps)
                return filtered_apps
        except Exception as exc:
            errors.append(f"{source['name']}: {exc}")

    raise RuntimeError("Steam oyun listesi alınamadı. Denenen kaynaklar: " + "; ".join(errors))
