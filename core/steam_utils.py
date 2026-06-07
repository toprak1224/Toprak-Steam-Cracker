import os
import subprocess
import time
import urllib.request
import winreg
import requests

# DLL dosyalarının indirileceği URL'leri kendi repo'nuzla doldurun
# Örnek: ("https://raw.githubusercontent.com/KULLANICI_ADI/REPO_ADI/refs/heads/main/xinput1_4.dll", "xinput1_4.dll")
HID_DLL_URLS = [
    ("", "xinput1_4.dll"),
    ("", "toprakcracker.dll"),
]

def detect_steam_path():
    """Steam kurulum yolunu döndürür, bulunamazsa None."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
            path = winreg.QueryValueEx(key, "InstallPath")[0]
            if os.path.exists(path):
                return path
    except Exception:
        pass

    common_paths = [
        os.path.expanduser("~") + "\\Program Files (x86)\\Steam",
        os.path.expanduser("~") + "\\Program Files\\Steam",
        "C:\\Program Files (x86)\\Steam",
        "C:\\Program Files\\Steam",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path

    return None

def get_lua_dir(steam_path):
    """Steam lua klasör yolunu döndürür."""
    return os.path.join(steam_path, 'config', 'lua') if steam_path else ""

def restart_steam(steam_path):
    """Steam'i kapatıp yeniden başlatır. Hata durumunda exception fırlatır."""
    steam_exe = os.path.join(steam_path, 'steam.exe')
    if not os.path.isfile(steam_exe):
        raise FileNotFoundError(steam_exe)
    subprocess.run(['taskkill', '/F', '/IM', 'steam.exe'])
    subprocess.Popen([steam_exe])

def remove_hid_dll():
    """HID DLL dosyalarını Steam klasöründen kaldırır. Kaldırılan dosya listesini döndürür."""
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
        steam_path = winreg.QueryValueEx(key, "InstallPath")[0]

    subprocess.run(['taskkill', '/F', '/IM', 'steam.exe'])
    time.sleep(2)

    removed = []
    for dll_name in ["xinput1_4.dll", "toprakcracker.dll"]:
        dll_path = os.path.join(steam_path, dll_name)
        if os.path.exists(dll_path):
            os.remove(dll_path)
            removed.append(dll_name)
    return removed

def download_hid_dll(steam_path):
    """HID DLL dosyalarını steam_path'e indirir. Kaydedilen yolu döndürür."""
    for url, filename in HID_DLL_URLS:
        if not url:
            raise ValueError(f"{filename} için indirme URL'si yapılandırılmamış. config.py dosyasını düzenleyin.")
        urllib.request.urlretrieve(url, os.path.join(steam_path, filename))
    return steam_path

def get_dlc_ids(app_id):
    """Steam API'den oyunun DLC ID listesini çeker."""
    try:
        response = requests.get(
            f'https://store.steampowered.com/api/appdetails?appids={app_id}',
            timeout=5
        )
        dlc_ids = response.json().get(app_id, {}).get('data', {}).get('dlc', [])
        return dlc_ids if isinstance(dlc_ids, list) else []
    except Exception:
        return []
