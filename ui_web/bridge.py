import os
import sys
import json
import threading
import requests

from config import VERSION, VERSION_CHECK_URL, PROJECT_GITHUB_URL
from core import installer, game_manager, steam_utils
from steam_api import fetch_steam_app_list

if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SETTINGS_FILE = os.path.join(_BASE_DIR, "tsc_settings.json")

class API:
    def __init__(self):
        self._window = None
        from steam_api import _load_cached_app_list
        self._game_list = _load_cached_app_list() or []
        self._settings = self._load_settings()
        threading.Thread(target=self._prefetch_game_list, daemon=True).start()

    def set_window(self, window):
        self._window = window

    # ── Internal ─────────────────────────────────────────────────────────────

    def _push(self, event, data=None):
        if self._window:
            payload = json.dumps({"event": event, "data": data or {}})
            self._window.evaluate_js(f"window.onPythonEvent({payload})")

    def _load_settings(self):
        defaults = {
            "steam_path": steam_utils.detect_steam_path() or "",
            "lang": "tr",
            "has_accepted_legal": False,
        }
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                defaults.update(saved)
            except Exception:
                pass
        return defaults

    def _save_settings(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=2, ensure_ascii=False)

    def _prefetch_game_list(self):
        try:
            self._game_list = fetch_steam_app_list()
        except Exception:
            self._game_list = []

    def _steam_path(self):
        return self._settings.get("steam_path", "")

    # ── Legal ─────────────────────────────────────────────────────────────────

    def get_legal_status(self):
        return {"accepted": self._settings.get("has_accepted_legal", False)}

    def accept_legal(self):
        self._settings["has_accepted_legal"] = True
        self._save_settings()
        return {"ok": True}

    def reject_legal(self):
        if self._window:
            self._window.destroy()
        return {"ok": True}

    # ── Version ───────────────────────────────────────────────────────────────

    def get_version(self):
        return {"version": VERSION}

    def check_for_updates(self):
        if not VERSION_CHECK_URL:
            return {"current": VERSION, "latest": VERSION, "has_update": False}
        try:
            r = requests.get(VERSION_CHECK_URL, timeout=5)
            latest = r.text.strip()
            return {"current": VERSION, "latest": latest, "has_update": latest != VERSION}
        except Exception:
            return {"current": VERSION, "latest": VERSION, "has_update": False}

    def open_in_browser(self, url):
        import webbrowser
        webbrowser.open(url)
        return {"ok": True}

    def get_project_github_url(self):
        return PROJECT_GITHUB_URL or ""

    # ── Settings ──────────────────────────────────────────────────────────────

    def get_settings(self):
        return {
            "steam_path": self._settings.get("steam_path", ""),
            "lang": self._settings.get("lang", "tr"),
        }

    def save_settings(self, steam_path):
        self._settings["steam_path"] = steam_path
        self._save_settings()
        return {"ok": True}

    def detect_steam_path(self):
        path = steam_utils.detect_steam_path()
        if path:
            self._settings["steam_path"] = path
            self._save_settings()
        return {"path": path or ""}

    def browse_steam_folder(self):
        import webview
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result:
            return {"path": result[0]}
        return {"path": ""}

    # ── Library ───────────────────────────────────────────────────────────────

    def get_installed_games(self):
        steam_path = self._steam_path()
        app_ids = game_manager.get_installed_app_ids(steam_path)
        installed_data = game_manager.load_installed_games()
        games = []
        for app_id in app_ids:
            entry = installed_data.get(app_id, {})
            if isinstance(entry, str):
                name = entry
            elif isinstance(entry, dict):
                name = entry.get("name", f"Game {app_id}")
            else:
                name = f"Game {app_id}"
                
            missing_name = False
            if name == f"Game {app_id}" or name == str(app_id) or not name.strip():
                found = False
                for g in self._game_list:
                    if str(g.get("appid", "")) == str(app_id):
                        name = g.get("name", name)
                        found = True
                        break
                if not found:
                    missing_name = True
                    name = f"Game {app_id}"

            games.append({
                "app_id": app_id,
                "name": name,
                "cover": f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg",
            })
            
            if missing_name:
                threading.Thread(target=self._fetch_missing_name_thread, args=(app_id,), daemon=True).start()

        return games

    def _fetch_missing_name_thread(self, app_id):
        try:
            r = requests.get(f"https://store.steampowered.com/api/appdetails?appids={app_id}", timeout=5)
            data = r.json()
            if str(app_id) in data and data[str(app_id)].get("success"):
                name = data[str(app_id)]["data"]["name"]
                game_manager.add_installed_game(app_id, name)
                self._push("game_name_updated", {"app_id": app_id, "name": name})
        except Exception:
            pass

    def remove_game(self, app_id):
        steam_path = self._steam_path()
        try:
            lua_removed, manifest_removed = game_manager.remove_game_files(app_id, steam_path)
            lua_dir = steam_utils.get_lua_dir(steam_path)
            dlc_ids = steam_utils.get_dlc_ids(app_id)
            installer.remove_dlc_entries(lua_dir, dlc_ids)
            game_manager.remove_installed_game_entry(app_id)
            return {"ok": True, "lua": lua_removed, "manifests": manifest_removed}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── Add Game ──────────────────────────────────────────────────────────────

    def search_games(self, query):
        if not query or len(query) < 2:
            return []
        q = query.lower()
        results = [g for g in self._game_list if q in g["name"].lower()]
        return results[:30]

    def get_total_games(self):
        return len(self._game_list)

    def get_popular_games(self):
        popular_ids = {
            "1091500", "1174180", "271590", "1086940", "292030",
            "1817070", "1593500", "990080", "1245620", "391220",
            "1172380", "413150", "814380", "1151640", "1888160",
            "379720", "239140", "2050650"
        }
        results = []
        for g in self._game_list:
            if str(g.get("appid")) in popular_ids:
                results.append(g)
            if len(results) >= 15:
                break

        if len(results) < 15 and len(self._game_list) > 15:
            results.extend(self._game_list[:(15 - len(results))])
            
        return results

    def add_game_by_id(self, app_id):
        steam_path = self._steam_path()
        if not steam_path:
            return {"ok": False, "error": "Steam yolu ayarlanmamış. Ayarlar sayfasından belirtin."}
        threading.Thread(
            target=self._add_game_thread,
            args=(str(app_id), steam_path),
            daemon=True,
        ).start()
        return {"ok": True}

    def _add_game_thread(self, app_id, steam_path):
        temp_zip = None
        try:
            self._push("install_progress", {"app_id": app_id, "step": "downloading"})
            temp_zip = installer.download_zip(app_id)
            self._push("install_progress", {"app_id": app_id, "step": "installing"})
            result = installer.install_from_zip(temp_zip, steam_path, game_id=app_id)
            game_manager.add_installed_game(
                app_id, result["game_name"],
                result["lua_files"], result["manifest_files"]
            )
            self._push("install_done", {
                "app_id": app_id,
                "game_name": result["game_name"],
                "lua_count": result["lua_count"],
                "manifest_count": result["manifest_count"],
                "cover": f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg",
            })
        except requests.exceptions.RequestException:
            self._push("install_error", {
                "app_id": app_id,
                "error": "Mevcut değil, lütfen Dosya Yükle kısmından ekleyin.",
            })
        except Exception as e:
            self._push("install_error", {
                "app_id": app_id, 
                "error": "Mevcut değil, lütfen Dosya Yükle kısmından ekleyin."
            })
        finally:
            if temp_zip and os.path.exists(temp_zip):
                try:
                    os.remove(temp_zip)
                except Exception:
                    pass

    def browse_game_files(self):
        import webview
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=("Manifest ve Lua Dosyaları (*.manifest;*.lua)",),
        )
        return list(result) if result else []

    def add_game_files(self, file_paths):
        steam_path = self._steam_path()
        if not steam_path:
            return {"ok": False, "error": "Steam yolu ayarlanmamış."}
        try:
            valid = [f for f in file_paths if f.lower().endswith((".lua", ".manifest"))]
            lua_count, manifest_count = installer.install_files(valid, steam_path)
            return {"ok": True, "lua": lua_count, "manifests": manifest_count}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── Steam Kontrolleri ─────────────────────────────────────────────────────

    def restart_steam(self):
        steam_path = self._steam_path()
        try:
            steam_utils.restart_steam(steam_path)
            return {"ok": True}
        except FileNotFoundError:
            return {"ok": False, "error": "steam.exe bulunamadı."}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def download_hid_dll(self):
        steam_path = self._steam_path() or steam_utils.detect_steam_path() or os.path.expanduser("~\\Desktop")
        try:
            steam_utils.download_hid_dll(steam_path)
            return {"ok": True, "path": steam_path}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def remove_hid_dll(self):
        try:
            removed = steam_utils.remove_hid_dll()
            return {"ok": True, "removed": removed}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def restart_steam(self):
        steam_path = self._steam_path()
        if not steam_path or not os.path.exists(steam_path):
            return {"ok": False, "error": "Steam dizini bulunamadı."}
        try:
            steam_utils.restart_steam(steam_path)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def check_dlls(self):
        steam_path = self._settings.get("steam_path")
        if not steam_path or not os.path.exists(steam_path):
            return {"installed": False, "msg": "Steam Yok"}
        
        d1 = os.path.join(steam_path, "xinput1_4.dll")
        d2 = os.path.join(steam_path, "toprakcracker.dll")
        if os.path.exists(d1) and os.path.exists(d2):
            return {"installed": True, "msg": "DLL'ler Aktif"}
        return {"installed": False, "msg": "DLL'ler Eksik"}

    # ── Online Fix ────────────────────────────────────────────────────────────

    def get_online_fix_games(self):
        from config import ONLINEFIX_LIST_URL
        try:
            r = requests.get(ONLINEFIX_LIST_URL, timeout=10)
            r.encoding = "utf-8"
            games = []
            for line in r.text.splitlines():
                line = line.strip()
                if not line:
                    continue
                name = line
                if line.isdigit():
                    found = False
                    for g in self._game_list:
                        if str(g.get("appid", "")) == line:
                            name = g.get("name", line)
                            found = True
                            break
                    if not found:
                        name = f"Game {line}"
                        threading.Thread(target=self._fetch_missing_name_thread, args=(line,), daemon=True).start()
                games.append({"id": line, "name": name})
            return {"ok": True, "games": games}
        except Exception as e:
            return {"ok": False, "error": str(e), "games": []}

    def download_online_fix_game(self, game_id):
        import webview
        # Klasör seçme işlemini ana thread'de (UI) yapıyoruz
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if not result or len(result) == 0:
            return {"ok": False, "error": "İndirme iptal edildi."}
            
        download_dir = result[0]
        
        threading.Thread(
            target=self._online_fix_thread,
            args=(game_id, download_dir),
            daemon=True,
        ).start()
        return {"ok": True}

    def _online_fix_thread(self, game_id, download_dir):
        import os
        from config import ONLINEFIX_DOWNLOAD_URL_TEMPLATE
        try:
            self._push("online_fix_progress", {"game_id": game_id, "step": "downloading"})
            url = ONLINEFIX_DOWNLOAD_URL_TEMPLATE.format(game_id=game_id)
            r = requests.get(url, stream=True, timeout=60)
            r.raise_for_status()
            
            filepath = os.path.join(download_dir, f"{game_id}_OnlineFix.rar")
            
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            self._push("online_fix_done", {
                "game_id": game_id
            })
            
        except Exception as e:
            self._push("online_fix_error", {"game_id": game_id, "error": str(e)})
