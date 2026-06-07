import os
import sys
import shutil
import zipfile
import tempfile
import requests

from config import MANIFEST_HUB_BASE_URL

def generate_url(app_id):
    if not MANIFEST_HUB_BASE_URL:
        raise ValueError("ManifestHub URL'si yapılandırılmamış. config.py dosyasındaki MANIFEST_HUB_BASE_URL'yi doldurun.")
    return MANIFEST_HUB_BASE_URL + app_id

def _fetch_game_info(game_id):
    """Steam API'den oyun adı ve DLC listesini çeker."""
    game_name = f"Game {game_id}"
    dlc_ids = []
    try:
        response = requests.get(
            f'https://store.steampowered.com/api/appdetails?appids={game_id}',
            timeout=5
        )
        data = response.json()
        if data and game_id in data and data[game_id].get('success'):
            game_data = data[game_id]['data']
            game_name = game_data.get('name', game_name)
            dlc_ids = game_data.get('dlc', [])
            if not isinstance(dlc_ids, list):
                dlc_ids = []
    except Exception:
        pass
    return game_name, dlc_ids

def _write_dlc_entries(lua_dir, dlc_ids):
    """Yeni DLC addappid satırlarını marcellus.lua'ya ekler. Eklenen satır sayısını döndürür."""
    marcellus_path = os.path.join(lua_dir, 'marcellus.lua')
    existing_lines = []
    if os.path.exists(marcellus_path):
        with open(marcellus_path, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()

    new_count = 0
    with open(marcellus_path, 'a', encoding='utf-8') as f:
        for dlc_id in dlc_ids:
            line = f'addappid({dlc_id}, 1)\n'
            if line not in existing_lines:
                f.write(line)
                new_count += 1
    return new_count

def download_zip(app_id, timeout=30):
    """ManifestHub'dan oyun zip'ini indirir. Geçici dosya yolunu döndürür."""
    url = generate_url(app_id)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{app_id}.zip")
    tmp.write(response.content)
    tmp.close()
    return tmp.name

def install_from_zip(zip_path, steam_path, game_id=None):
    """
    Zip içindeki lua dosyalarını Steam klasörlerine kurar.
    """
    lua_dir = os.path.join(steam_path, 'config', 'lua')
    depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
    os.makedirs(lua_dir, exist_ok=True)
    os.makedirs(depotcache_dir, exist_ok=True)

    if game_id is None:
        base = os.path.basename(zip_path)
        game_id = os.path.splitext(base)[0].split('_')[-1]

    if not game_id.isdigit():
        raise ValueError(game_id)

    game_name, dlc_ids = _fetch_game_info(game_id)

    lua_count = 0
    manifest_count = 0
    lua_files = []
    manifest_files = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.lower().endswith('.lua'):
                dest_name = os.path.basename(file)
                with zip_ref.open(file) as src, open(os.path.join(lua_dir, dest_name), 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                lua_count += 1
                lua_files.append(dest_name)

    dlc_count = _write_dlc_entries(lua_dir, dlc_ids)

    return {
        'game_id': game_id,
        'game_name': game_name,
        'lua_count': lua_count,
        'manifest_count': manifest_count,
        'dlc_count': dlc_count,
        'lua_files': lua_files,
        'manifest_files': manifest_files,
    }

def install_from_zip_ref(zip_ref, steam_path):
    """Açık bir ZipFile nesnesinden kurulum yapar. (lua_count, manifest_count) döndürür."""
    lua_dir = os.path.join(steam_path, 'config', 'lua')
    depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
    os.makedirs(lua_dir, exist_ok=True)
    os.makedirs(depotcache_dir, exist_ok=True)

    lua_count = 0
    manifest_count = 0

    for file in zip_ref.namelist():
        if file.lower().endswith('.lua'):
            with zip_ref.open(file) as src, open(os.path.join(lua_dir, os.path.basename(file)), 'wb') as dst:
                shutil.copyfileobj(src, dst)
            lua_count += 1

    return lua_count, 0

def install_files(valid_files, steam_path):
    """Seçilen .lua ve .manifest dosyalarını Steam klasörlerine kopyalar. (lua_count, manifest_count) döndürür."""
    lua_dir = os.path.join(steam_path, 'config', 'lua')
    depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
    os.makedirs(lua_dir, exist_ok=True)
    os.makedirs(depotcache_dir, exist_ok=True)

    lua_count = 0
    manifest_count = 0

    for file_path in valid_files:
        file_name = os.path.basename(file_path)
        if file_name.lower().endswith('.lua'):
            shutil.copy2(file_path, os.path.join(lua_dir, file_name))
            lua_count += 1
        elif file_name.lower().endswith('.manifest'):
            shutil.copy2(file_path, os.path.join(depotcache_dir, file_name))
            manifest_count += 1

    return lua_count, manifest_count

def remove_dlc_entries(lua_dir, dlc_ids):
    """marcellus.lua'dan DLC satırlarını temizler."""
    marcellus_path = os.path.join(lua_dir, 'marcellus.lua')
    if not os.path.exists(marcellus_path):
        return
    with open(marcellus_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_lines = [line for line in lines if not any(f'addappid({dlc_id},' in line for dlc_id in dlc_ids)]
    with open(marcellus_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
