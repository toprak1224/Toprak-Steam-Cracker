import os
import sys
import json

if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_GAMES_FILE = os.path.join(_BASE_DIR, "installed_games.json")

def load_installed_games():
    """Yüklü oyunlar JSON dosyasını okur. Dict döndürür."""
    if os.path.exists(INSTALLED_GAMES_FILE):
        with open(INSTALLED_GAMES_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_installed_games(games):
    """Yüklü oyunları JSON dosyasına yazar."""
    with open(INSTALLED_GAMES_FILE, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=4, ensure_ascii=False)

def add_installed_game(app_id, game_name, lua_files=None, manifest_files=None):
    """Yüklü oyun kaydını ekler veya günceller."""
    installed = load_installed_games()
    entry = installed.get(app_id)

    if isinstance(entry, dict):
        entry_data = entry
    elif isinstance(entry, str):
        entry_data = {"name": entry}
    else:
        entry_data = {}

    entry_data['name'] = game_name
    if lua_files is not None:
        entry_data['lua_files'] = sorted(set(lua_files))
    if manifest_files is not None:
        entry_data['manifest_files'] = sorted(set(manifest_files))

    installed[app_id] = entry_data
    save_installed_games(installed)

def remove_installed_game_entry(app_id):
    """Yüklü oyun kaydını siler."""
    installed = load_installed_games()
    if app_id in installed:
        del installed[app_id]
        save_installed_games(installed)

def get_installed_app_ids(steam_path):
    """Lua klasöründeki sayısal .lua dosyalarının app_id listesini döndürür."""
    lua_dir = os.path.join(steam_path, 'config', 'lua') if steam_path else ""
    app_ids = []
    if lua_dir and os.path.isdir(lua_dir):
        for fname in os.listdir(lua_dir):
            name_part = os.path.splitext(fname)[0]
            if fname.lower().endswith('.lua') and name_part.isdigit():
                app_ids.append(name_part)
    return app_ids

def remove_game_files(app_id, steam_path):
    """
    Oyuna ait lua ve manifest dosyalarını siler.
    (lua_kaldırılan, manifest_kaldırılan) tuple döndürür.
    """
    lua_dir = os.path.join(steam_path, 'config', 'lua')
    depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')

    installed_entry = load_installed_games().get(app_id)
    stored_luas = []
    stored_manifests = []
    if isinstance(installed_entry, dict):
        stored_luas = installed_entry.get('lua_files', []) or []
        stored_manifests = installed_entry.get('manifest_files', []) or []

    lua_removed = 0
    manifest_removed = 0

    if stored_luas:
        for filename in stored_luas:
            file_path = os.path.join(lua_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                lua_removed += 1
    elif os.path.isdir(lua_dir):
        for filename in os.listdir(lua_dir):
            if filename.startswith(app_id) and filename.lower().endswith('.lua'):
                os.remove(os.path.join(lua_dir, filename))
                lua_removed += 1

    if stored_manifests:
        for filename in stored_manifests:
            file_path = os.path.join(depotcache_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                manifest_removed += 1
    elif os.path.isdir(depotcache_dir):
        for filename in os.listdir(depotcache_dir):
            if filename.startswith(app_id) and filename.lower().endswith('.manifest'):
                os.remove(os.path.join(depotcache_dir, filename))
                manifest_removed += 1

    return lua_removed, manifest_removed
