import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
try:
    
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False
from io import BytesIO
import requests
import os
import sys
import threading
import zipfile
import shutil
import subprocess
from urllib.parse import urlparse
import math
import time
import urllib.request
import winreg
import json
import re

VERSION = "4.2"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/toprak1224/Toprak-Steam-Cracker/refs/heads/main/verison"
STEAM_APP_LIST_CACHE_FILE = "steam_app_list_cache.json"
STEAM_APP_LIST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}

STEAM_APP_LIST_GITHUB_SOURCES = [
    {
        "name": "github_games",
        "url": "https://raw.githubusercontent.com/jsnli/steamappidlist/refs/heads/master/data/games_appid.json",
        "name_suffix": "",
    },
    {
        "name": "github_dlc",
        "url": "https://raw.githubusercontent.com/jsnli/steamappidlist/refs/heads/master/data/dlc_appid.json",
        "name_suffix": " (DLC)",
    },
]


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


def fetch_steam_app_list(session=None):
    session = session or requests.Session()
    errors = []

    try:
        github_apps = _fetch_github_app_lists(session)
        if github_apps:
            _save_app_list_cache(github_apps)
            return github_apps
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
                _save_app_list_cache(apps)
                return apps
        except Exception as exc:
            errors.append(f"{source['name']}: {exc}")

    cached = _load_cached_app_list()
    if cached:
        return cached

    raise RuntimeError("Steam oyun listesi alınamadı. Denenen kaynaklar: " + "; ".join(errors))


def show_version_check(root, session=None):
    overlay = tk.Toplevel(root)
    overlay.title("🔄 Sürüm Kontrolü // Version Check")
    overlay.configure(bg='#050505')
    overlay.geometry("420x220")
    overlay.resizable(False, False)
    overlay.transient(root)
    overlay.grab_set()
    overlay.lift()
    try:
        overlay.attributes('-topmost', True)
    except Exception:
        pass

    root.update_idletasks()
    overlay.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width = overlay.winfo_width()
    height = overlay.winfo_height()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    overlay.geometry(f"{width}x{height}+{x}+{y}")

    frame = tk.Frame(overlay, bg='#050505', padx=30, pady=30)
    frame.pack(fill=tk.BOTH, expand=True)

    title_label = tk.Label(
        frame,
        text="Sürüm kontrol ediliyor...\nChecking version...",
        font=("Segoe UI", 13, "bold"),
        fg="#ffcc00",
        bg='#050505',
        justify='center'
    )
    title_label.pack(pady=(0, 10))

    subtitle = tk.Label(
        frame,
        text=f"Kurulu sürüm / Installed: v{VERSION}",
        font=("Segoe UI", 10),
        fg="#cfcfcf",
        bg='#050505'
    )
    subtitle.pack(pady=(0, 10))

    style = ttk.Style()
    try:
        style.theme_use(style.theme_use())
    except tk.TclError:
        pass
    style.configure(
        "Version.Horizontal.TProgressbar",
        troughcolor='#1a1a1a',
        background='#4a90e2',
        bordercolor='#1a1a1a',
        lightcolor='#4a90e2',
        darkcolor='#4a90e2'
    )

    progress = ttk.Progressbar(
        frame,
        orient="horizontal",
        mode="determinate",
        length=260,
        style="Version.Horizontal.TProgressbar",
        maximum=100
    )
    progress.pack(pady=(5, 0))
    progress['value'] = 0

    animation_label = tk.Label(
        frame,
        text="🔍 Kontrol ediliyor...",
        font=("Segoe UI", 10),
        fg="#8ad4ff",
        bg='#050505'
    )
    animation_label.pack(pady=(12, 4))

    result_label = tk.Label(
        frame,
        text="",
        font=("Segoe UI", 10, "bold"),
        fg="#ffffff",
        bg='#050505',
        wraplength=360,
        justify='center'
    )
    result_label.pack()

    status = {'latest': None, 'error': None}
    done_event = threading.Event()
    finished = {'value': False}
    animation_index = {'value': 0}
    progress_value = {'value': 0}

    animation_frames = [
        "🔍 Kontrol ediliyor...",
        "🔍 Kontrol ediliyor..",
        "🔍 Kontrol ediliyor.",
        "⚡ Sunucu yanıtı bekleniyor...",
        "☁️ Github bağlantısı doğrulanıyor...",
        "🔐 İmza doğrulanıyor...",
    ]

    def animate():
        if finished['value']:
            return
        frame = animation_frames[animation_index['value'] % len(animation_frames)]
        animation_label.config(text=frame)
        animation_index['value'] += 1
        overlay.after(220, animate)

    def animate_progress():
        if finished['value']:
            return
        if progress_value['value'] < 90:
            progress_value['value'] += 2
            progress['value'] = progress_value['value']
        overlay.after(80, animate_progress)

    mismatch_message = {'text': None}

    def finish():
        if finished['value']:
            return
        finished['value'] = True
        progress['value'] = 100
        latest = status.get('latest')
        error = status.get('error')

        def close_after_delay():
            if overlay.winfo_exists():
                overlay.grab_release()
                overlay.destroy()

        if latest:
            subtitle.config(text=f"Kurulu: v{VERSION} • Uzak: v{latest}")
            if latest == VERSION:
                animation_label.config(text="✅ Sürümünüz güncel!", fg="#50c878")
                result_label.config(
                    text=f"Mevcut sürüm: v{VERSION}\nVersion ok!",
                    fg="#50c878"
                )
            else:
                animation_label.config(text="⚠️ Yeni sürüm bulundu!", fg="#ffcc00")
                result_label.config(
                    text=f"Kurulu: v{VERSION} • Güncel: v{latest}\nLütfen yeni sürümü indirin.",
                    fg="#ffcc00"
                )
                mismatch_message['text'] = (
                    "⚠️ Yeni sürüm mevcut!\n\n"
                    f"Kurulu sürüm: v{VERSION}\n"
                    f"Güncel sürüm: v{latest}\n\n"
                    "Lütfen en son paketi indirip güncelleyin."
                )
        elif error:
            animation_label.config(text="⚠️ Sürüm kontrolü tamamlanamadı", fg="#ff6b6b")
            subtitle.config(text=f"Kurulu: v{VERSION} • Durum: Hata")
            result_label.config(
                text=f"Hata: {error}",
                fg="#ff6b6b"
            )

        def close_after_delay():
            if overlay.winfo_exists():
                overlay.grab_release()
                overlay.destroy()
            if mismatch_message['text']:
                messagebox.showwarning("Yeni Sürüm Mevcut", mismatch_message['text'], parent=root)

        overlay.after(2000, close_after_delay)

    def worker():
        try:
            latest = fetch_latest_version(session=session)
            status['latest'] = latest
        except Exception as exc:
            status['error'] = str(exc)
        finally:
            done_event.set()

    def poll():
        if done_event.is_set():
            finish()
        else:
            overlay.after(100, poll)

    threading.Thread(target=worker, daemon=True).start()
    overlay.after(0, animate)
    overlay.after(0, animate_progress)
    overlay.after(150, poll)
    overlay.wait_window()


def show_preflight_notice(parent, strings):
    popup = tk.Toplevel(parent)
    popup.title(strings.get('preflight_title', 'Info'))
    popup.configure(bg='#0a0a0a')
    popup.geometry("460x320")
    popup.resizable(False, False)
    popup.transient(parent)
    popup.grab_set()

    parent.update_idletasks()
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")

    frame = tk.Frame(popup, bg='#0f0f0f', padx=25, pady=25)
    frame.pack(fill=tk.BOTH, expand=True)

    header = tk.Label(
        frame,
        text=strings.get('preflight_header', ''),
        font=("Segoe UI", 16, "bold"),
        fg="#ffcc00",
        bg='#0f0f0f'
    )
    header.pack(anchor='w')

    body = tk.Label(
        frame,
        text=strings.get('preflight_message', ''),
        font=("Segoe UI", 11),
        fg="#ffffff",
        bg='#0f0f0f',
        justify='left',
        wraplength=380
    )
    body.pack(fill=tk.X, pady=(12, 15))

    checklist_text = strings.get('preflight_checklist')
    if checklist_text:
        checklist = tk.Label(
            frame,
            text=checklist_text,
            font=("Segoe UI", 10),
            fg="#c8c8c8",
            bg='#1a1a1a',
            justify='left',
            anchor='w',
            padx=15,
            pady=12,
            wraplength=380
        )
        checklist.pack(fill=tk.X, pady=(0, 20))

    action_btn = tk.Button(
        frame,
        text=strings.get('preflight_button', 'OK'),
        bg="#4a90e2",
        fg="#ffffff",
        font=("Segoe UI", 11, "bold"),
        relief=tk.FLAT,
        padx=24,
        pady=8,
        command=popup.destroy,
        cursor='hand2'
    )
    action_btn.pack()

    popup.focus_set()
    popup.wait_window()


LANGUAGES = {
    'tr': {
        "legal_title": "Yasal Uyarı",
        "legal_checkbox": "Yukarıdaki uyarıyı okudum ve kabul ediyorum",
        "continue_btn": "Devam Et",
        "exit_btn": "Çıkış",
        "legal_header": "⚠️ YASAL UYARI",
        "legal_text": """📌 Yasal Uyarı ve Sorumluluk Reddi

Bu yazılım yalnızca **eğitimsel ve deneysel** amaçlarla geliştirilmiştir.

**Toprak Steam Cracker**, hiçbir şekilde **ticari kazanç amacı** taşımaz ve **dijital içeriklerin izinsiz kullanımını, dağıtımını veya çoğaltılmasını teşvik etmez**.

🔧 Yazılımın kullanım amacı, yalnızca **Steam istemcisi üzerinde teknik analiz ve entegrasyon testleri gerçekleştirmek** ile sınırlıdır.

❗ Önemli Hukuki Bilgilendirme:
Steam platformuna ait içeriklerin **lisans satın alınmadan kullanılması**;

- **5846 Sayılı Fikir ve Sanat Eserleri Kanunu**,
- **Türk Ceza Kanunu’nun 135., 136. ve 137. maddeleri**,
- ve **uluslararası fikri mülkiyet yasaları** kapsamında **suç teşkil eder**.

🚫 Bu tür yasa dışı kullanım; **hukuki yaptırımların yanı sıra cezai sorumluluklara** da neden olabilir.

💬 Geliştirici Sorumluluk Reddi:
Bu yazılımın amacı dışında veya hukuka aykırı şekilde kullanılması halinde, **geliştirici hiçbir sorumluluk kabul etmez**.
Lütfen bu yazılımı yalnızca **etik ve yasal sınırlar içinde** kullanınız.""",
        "preflight_title": "⚙️ Sistem Uyarısı",
        "preflight_header": "🚀 Başlamadan Önce",
        "preflight_message": "Programın tüm özelliklerini kullanabilmek için aşağıdaki hazırlıkları tamamlayın:",
        "preflight_checklist": "• Gerekli tüm Python kütüphanelerini kurduğunuzdan emin olun.\n• Antivirüs ve güvenlik duvarı korumalarını geçici olarak devre dışı bırakın.\n• Uygulamayı yönetici olarak çalıştırmanız önerilir.",
        "preflight_button": "Hazırım, Devam Et",
        "warning": "Uyarı",
        "accept_warning": "Devam etmek için kutuyu işaretlemeniz gerekmektedir!",
        "main_title": "Toprak Steam Cracker & Manifest Oluşturucu",
        "app_header": "💀 TOPRAK STEAM CRACKER",
        "app_subtitle": "⚡ MANIFEST OLUŞTURUCU & STEAM ENTEGRASYONU ⚡",
        "about_btn": "ℹ️ Hakkında",
        "about_title": "Hakkında",
        "version": f"Sürüm: {VERSION}",
        "developer": "Geliştirici: Toprak",
        "about_desc": "Bu yazılım eğitimsel ve deneysel amaçlı geliştirilmiştir.",
        "github_repo": "GitHub Deposu (ManifestHub)",
        "about_disclaimer": "Bu yazılım herhangi bir ticari amaç taşımamaktadır.\nLütfen etik ve yasal sınırlar içinde kullanınız.",
        "close_btn": "Kapat",
        "installed_games_btn": "🎮 Yüklü Oyunlar",
        "installed_games_title": "Yüklü Oyunlar",
        "no_installed_games": "Yüklü oyun bulunmuyor.",
        "game_id_format": " (ID: {app_id})",
        "game_selected_status": "🎮 OYUN SEÇİLDİ: {game_name}",
        "success": "Başarılı",
        "hid_removed_success": "hid.dll başarıyla kaldırıldı!\nSteam'i yeniden başlatabilirsiniz.",
        "hid_removed_status": "✅ HID.dll BAŞARIYLA KALDIRILDI",
        "info": "Bilgi",
        "hid_not_found": "hid.dll dosyası bulunamadı!",
        "hid_not_found_status": "ℹ️ HID.dll BULUNAMADI",
        "error": "Hata",
        "hid_remove_error": "hid.dll kaldırılırken hata oluştu:\n{error}",
        "hid_remove_error_status": "❌ HID.dll KALDIRILAMADI",
        "remove_hid_btn": "🗑️ HID.dll Kaldır",
        "zip_upload_btn": "📦 Manuel Olarak Zip Yükle",
        "select_steam_folder_prompt": "Lütfen önce Steam kurulum klasörünü seçin!",
        "select_zip_title": "ZIP Dosyası Seçin",
        "zip_files_filter": "ZIP Dosyaları",
        "all_files_filter": "Tüm Dosyalar",
        "zip_no_manifest_lua": "ZIP dosyasında .manifest veya .lua dosyası bulunamadı!",
        "zip_process_error": "ZIP dosyası işlenirken hata oluştu:\n{error}",
        "zip_success_msg": "🎉 {lua_count} LUA ve {manifest_count} manifest dosyası eklendi!\n\n🚀 Oyununuzu oynamak için Steam'i yeniden başlatın!",
        "zip_success_status": "📦 ZIP'DEN {count} DOSYA EKLENDİ",
        "steam_path_auto_detected": "✅ STEAM KONUMU OTOMATİK BULUNDU",
        "steam_path_not_detected": "⚠️ STEAM KONUMU OTOMATİK BULUNAMADI",
        "faq_btn": "❓ SSS",
        "drag_drop_title": "📂 MANUEL DOSYA EKLEME (Sürükle & Bırak)",
        "drag_drop_label": "Manifest ve Lua dosyalarını buraya sürükle & bırak\n(.manifest, .lua)",
        "dnd_not_supported": "Sürükle-bırak desteklenmiyor\n(tkinterdnd2 kurulu değil)",
        "unsupported_drop_format": "Desteklenmeyen dosya bırakma formatı!",
        "only_manifest_lua_accepted": "Sadece .manifest veya .lua dosyaları kabul edilir!",
        "file_process_error": "Dosyalar işlenirken hata oluştu:\n{error}",
        "drag_drop_success_msg": "🎉 {lua_count} LUA ve {manifest_count} manifest dosyası eklendi!\n\n🚀 Oyununuzu oynamak için Steam'i yeniden başlatın!",
        "drag_drop_success_status": "📂 {count} DOSYA EKLENDİ",
        "download_hid_btn": "💾 HID.dll İndir",
        "hid_path_not_found_warning": "Steam kurulum yolu bulunamadı. Dosya masaüstüne kaydedilecek.",
        "dll_download_success": "DLL başarıyla indirildi!\nKaydedilen konum: {save_path}",
        "dll_download_success_status": "✅ HID.dll BAŞARIYLA İNDİRİLDİ",
        "dll_download_error": "DLL indirilirken hata oluştu:\n{error}",
        "dll_download_error_status": "❌ HID.dll İNDİRİLEMEDİ",
        "search_game_btn": "🔍 Oyun Ara",
        "game_list_fetch_error": "Oyun listesi alınamadı: {error}",
        "game_search_title": "Steam Oyun Arama",
        "search_steam_game_header": "🎮 Steam Oyun Ara",
        "cover_load_error": "Kapak yüklenemedi",
        "selected_game_label": "Seçilen Oyun: ",
        "details_fetch_error": "Detaylar alınamadı.",
        "unknown": "Bilinmiyor",
        "detail_name": "📌 Ad: {name}",
        "detail_release": "📅 Çıkış: {release}",
        "detail_publisher": "🏢 Yayıncı: {publishers}",
        "detail_genre": "📚 Tür: {genres}",
        "detail_price": "💵 Fiyat: {price}",
        "free_or_unknown": "Ücretsiz / Bilinmiyor",
        "details_fetch_exception": "Detaylar alınamadı: {error}",
        "select_btn": "Seç",
        "open_steamdb_btn": "🔍 SteamDB Aç",
        "steam_path_section_title": "🔧 STEAM KURULUM KONUMU",
        "browse_btn": "📁 GÖZAT",
        "game_id_section_title": "🎮 STEAM OYUN ID",
        "download_install_btn": "🚀 İNDİR & KUR",
        "remove_game_btn": "💀 OYUNU KALDIR",
        "restart_steam_btn": "⚡ STEAM'İ YENİDEN BAŞLAT",
        "initial_status": "⚡ HAZIR - STEAM KONUMU VE OYUN ID GİRİN",
        "footer_text": "👑 TOPRAK TARAFINDAN YAPILDI - 2025 ",
        "appid_empty_error": "Oyun ID boş olamaz!",
        "appid_invalid_error": "Geçerli bir Oyun ID girin!",
        "appid_numeric_error": "Oyun ID sadece sayılardan oluşmalıdır!",
        "processing_status": "⏳ İŞLENİYOR...",
        "select_steam_folder_title": "Steam Kurulum Klasörünü Seçin",
        "steam_path_selected": "✅ STEAM KONUMU SEÇİLDİ",
        "downloading_manifests_status": "🌐 MANIFEST DOSYALARI İNDİRİLİYOR...",
        "installing_to_steam_status": "⚙️ STEAM'E KURULUYOR...",
        "game_crack_success_status": "� OYUN BAŞARIYLA KIRILDI: ID {app_id}",
        "install_fail_status": "❌ KURULUM BAŞARISIZ!",
        "download_fail_status": "❌ İNDİRME BAŞARISIZ!",
        "download_error_title": "❌ İNDİRME HATASI",
        "download_error_msg": "İndirme hatası: {error}",
        "unexpected_error_status": "❌ HATA OLUŞTU!",
        "unexpected_error_msg": "Beklenmeyen hata: {error}",
        "zip_name_error": "ZIP dosya adı sadece Oyun ID'si (sayılar) içermelidir!",
        "game_id_prefix": "Oyun ID: {game_id}",
        "game_crack_success_msgbox_title": "🎉 OYUN BAŞARIYLA KIRILDI!",
        "crack_stats": "📊 İSTATİSTİKLER:",
        "lua_processed": "• {count} LUA dosyası işlendi",
        "manifest_installed": "• {count} manifest dosyası kuruldu",
        "dlc_added": "• {count} yeni DLC eklendi",
        "restart_steam_prompt": "🚀 Oyununuzu oynamak için Steam'i yeniden başlatın!",
        "processing_error": "İşleme sırasında hata:\n{error}",
        "confirmation_title": "ONAY",
        "remove_game_confirm": "{app_id} ID'li oyun kaldırılacak. Emin misiniz?",
        "removing_game_status": "🗑️ {app_id} ID'Lİ OYUN KALDIRILIYOR...",
        "remove_game_success_msgbox": "{app_id} ID'li oyun ve ilgili dosyalar başarıyla kaldırıldı!\nLUA: {lua_files}, Manifest: {manifest_files}",
        "remove_game_success_status": "🗑️ {app_id} ID'Lİ OYUN KALDIRILDI",
        "remove_game_error": "Oyun kaldırılırken hata:\n{error}",
        "steam_exe_not_found": "steam.exe bulunamadı! Lütfen doğru Steam klasörünü seçtiğinizden emin olun.",
        "steam_restart_success_msgbox": "🔄 Steam başarıyla yeniden başlatıldı!\n\n🎮 Artık oyununuzu oynayabilirsiniz!",
        "steam_restart_success_status": "⚡ STEAM YENİDEN BAŞLATILDI",
        "steam_restart_error": "Steam yeniden başlatılamadı:\n{error}",
        "font_animation_error": "Font animasyon hatası: {error}",
        "critical_error_title": "Kritik Hata",
        "app_start_error": "Uygulama başlatılamadı:\n{error}",
        "faq_url": "https://rentry.co/topraksteamcrackerSSS",
        "online_fix_btn": "🔗 Online Fix İndirici",
        "online_fix_not_found": "online_fix.py dosyası bulunamadı!",
        "online_fix_error": "Online fix betiği çalıştırılırken hata oluştu:\n{error}",
        "online_fix_success_msg": "Online Fix betiği başarıyla başlatıldı.",
        "online_fix_success_status": "✅ ONLINE FIX BAŞLATILDI"
        },
    'en': {
        "legal_title": "Legal Notice",
        "legal_checkbox": "I have read and agree to the notice above",
        "continue_btn": "Continue",
        "exit_btn": "Exit",
        "legal_header": "⚠️ LEGAL NOTICE",
        "legal_text": """📌 Legal Notice and Disclaimer

This software has been developed for **educational and experimental** purposes only.

**Toprak Steam Cracker** has absolutely **no commercial purpose** and **does not encourage the unauthorized use, distribution, or reproduction of digital content**.

🔧 The intended use of this software is limited to **performing technical analysis and integration tests on the Steam client**.

❗ Important Legal Information:
Using Steam content **without a license** is a violation of **international copyright laws** and the **Steam Subscriber Agreement**, and may be a crime in your jurisdiction.
🚫 Such unauthorized use can result in severe **legal and criminal penalties**, including the termination of your Steam account.
💬 Developer Disclaimer:
The developer **accepts no responsibility** for how this software is used. The user is solely responsible for acting within **ethical and legal boundaries**.
""",
        "preflight_title": "⚙️ System Notice",
        "preflight_header": "🚀 Before You Start",
        "preflight_message": "To make sure everything works smoothly, please review this quick checklist:",
        "preflight_checklist": "• Install every required Python dependency.\n• Temporarily disable antivirus and firewall protection.\n• Running the app as Administrator is recommended.",
        "preflight_button": "Ready, Continue",
        "warning": "Warning",
        "accept_warning": "You must check the box to continue!",
        "main_title": "Toprak Steam Cracker & Manifest Generator",
        "app_header": "💀 TOPRAK STEAM CRACKER",
        "app_subtitle": "⚡ MANIFEST GENERATOR & STEAM INTEGRATION ⚡",
        "about_btn": "ℹ️ About",
        "about_title": "About",
        "version": f"Version: {VERSION}",
        "developer": "Developer: Toprak",
        "about_desc": "This software was developed for educational and experimental purposes.",
        "github_repo": "GitHub Repository (ManifestHub)",
        "about_disclaimer": "This software has no commercial purpose.\nPlease use it within ethical and legal limits.",
        "close_btn": "Close",
        "installed_games_btn": "🎮 Installed Games",
        "installed_games_title": "Installed Games",
        "no_installed_games": "No installed games found.",
        "game_id_format": " (ID: {app_id})",
        "game_selected_status": "🎮 GAME SELECTED: {game_name}",
        "success": "Success",
        "hid_removed_success": "hid.dll has been successfully removed!\nYou can restart Steam.",
        "hid_removed_status": "✅ HID.dll REMOVED SUCCESSFULLY",
        "info": "Info",
        "hid_not_found": "hid.dll file not found!",
        "hid_not_found_status": "ℹ️ HID.dll NOT FOUND",
        "error": "Error",
        "hid_remove_error": "An error occurred while removing hid.dll:\n{error}",
        "hid_remove_error_status": "❌ FAILED TO REMOVE HID.dll",
        "remove_hid_btn": "🗑️ Remove HID.dll",
        "zip_upload_btn": "📦 Upload Zip Manually",
        "select_steam_folder_prompt": "Please select the Steam installation folder first!",
        "select_zip_title": "Select ZIP File",
        "zip_files_filter": "ZIP Files",
        "all_files_filter": "All Files",
        "zip_no_manifest_lua": "No .manifest or .lua file found in the ZIP archive!",
        "zip_process_error": "An error occurred while processing the ZIP file:\n{error}",
        "zip_success_msg": "🎉 {lua_count} LUA and {manifest_count} manifest files added!\n\n🚀 Restart Steam to play your game!",
        "zip_success_status": "📦 {count} FILES ADDED FROM ZIP",
        "steam_path_auto_detected": "✅ STEAM LOCATION AUTO-DETECTED",
        "steam_path_not_detected": "⚠️ STEAM LOCATION NOT AUTO-DETECTED",
        "faq_btn": "❓ FAQ",
        "drag_drop_title": "📂 MANUAL FILE ADDITION (Drag & Drop)",
        "drag_drop_label": "Drag & drop Manifest and Lua files here\n(.manifest, .lua)",
        "dnd_not_supported": "Drag-and-drop is not supported\n(tkinterdnd2 is not installed)",
        "unsupported_drop_format": "Unsupported file drop format!",
        "only_manifest_lua_accepted": "Only .manifest or .lua files are accepted!",
        "file_process_error": "An error occurred while processing files:\n{error}",
        "drag_drop_success_msg": "🎉 {lua_count} LUA and {manifest_count} manifest files added!\n\n🚀 Restart Steam to play your game!",
        "drag_drop_success_status": "📂 {count} FILES ADDED",
        "download_hid_btn": "💾 Download HID.dll",
        "hid_path_not_found_warning": "Steam installation path not found. The file will be saved to the Desktop.",
        "dll_download_success": "DLL downloaded successfully!\nSaved to: {save_path}",
        "dll_download_success_status": "✅ HID.dll DOWNLOADED SUCCESSFULLY",
        "dll_download_error": "An error occurred while downloading the DLL:\n{error}",
        "dll_download_error_status": "❌ FAILED TO DOWNLOAD HID.dll",
        "search_game_btn": "🔍 Search Game",
        "game_list_fetch_error": "Could not fetch game list: {error}",
        "game_search_title": "Steam Game Search",
        "search_steam_game_header": "🎮 Search Steam Game",
        "cover_load_error": "Could not load cover",
        "selected_game_label": "Selected Game: ",
        "details_fetch_error": "Could not fetch details.",
        "unknown": "Unknown",
        "detail_name": "📌 Name: {name}",
        "detail_release": "📅 Release: {release}",
        "detail_publisher": "🏢 Publisher: {publishers}",
        "detail_genre": "📚 Genre: {genres}",
        "detail_price": "💵 Price: {price}",
        "free_or_unknown": "Free / Unknown",
        "details_fetch_exception": "Could not fetch details: {error}",
        "select_btn": "Select",
        "open_steamdb_btn": "🔍 Open SteamDB",
        "steam_path_section_title": "🔧 STEAM INSTALLATION LOCATION",
        "browse_btn": "📁 BROWSE",
        "game_id_section_title": "🎮 STEAM GAME ID",
        "download_install_btn": "🚀 DOWNLOAD & INSTALL",
        "remove_game_btn": "💀 REMOVE GAME",
        "restart_steam_btn": "⚡ RESTART STEAM",
        "initial_status": "⚡ READY - ENTER STEAM LOCATION AND GAME ID",
        "footer_text": "👑 MADE BY TOPRAK - 2025 ",
        "appid_empty_error": "Game ID cannot be empty!",
        "appid_invalid_error": "Please enter a valid Game ID!",
        "appid_numeric_error": "Game ID must consist of numbers only!",
        "processing_status": "⏳ PROCESSING...",
        "select_steam_folder_title": "Select Steam Installation Folder",
        "steam_path_selected": "✅ STEAM LOCATION SELECTED",
        "downloading_manifests_status": "🌐 DOWNLOADING MANIFEST FILES...",
        "installing_to_steam_status": "⚙️ INSTALLING TO STEAM...",
        "game_crack_success_status": "🎉 GAME CRACKED SUCCESSFULLY: ID {app_id}",
        "install_fail_status": "❌ INSTALLATION FAILED!",
        "download_fail_status": "❌ DOWNLOAD FAILED!",
        "download_error_title": "❌ DOWNLOAD ERROR",
        "download_error_msg": "Download error: {error}",
        "unexpected_error_status": "❌ AN ERROR OCCURRED!",
        "unexpected_error_msg": "Unexpected error: {error}",
        "zip_name_error": "ZIP file name must contain only the Game ID (numbers)!",
        "game_id_prefix": "Game ID: {game_id}",
        "game_crack_success_msgbox_title": "🎉 GAME CRACKED SUCCESSFULLY!",
        "crack_stats": "📊 STATISTICS:",
        "lua_processed": "• {count} LUA file(s) processed",
        "manifest_installed": "• {count} manifest file(s) installed",
        "dlc_added": "• {count} new DLC(s) added",
        "restart_steam_prompt": "🚀 Restart Steam to play your game!",
        "processing_error": "Error during processing:\n{error}",
        "confirmation_title": "CONFIRMATION",
        "remove_game_confirm": "The game with ID {app_id} will be removed. Are you sure?",
        "removing_game_status": "🗑️ REMOVING GAME WITH ID {app_id}...",
        "remove_game_success_msgbox": "Game with ID {app_id} and related files removed successfully!\nLUA: {lua_files}, Manifest: {manifest_files}",
        "remove_game_success_status": "🗑️ GAME WITH ID {app_id} REMOVED",
        "remove_game_error": "Error while removing game:\n{error}",
        "steam_exe_not_found": "steam.exe not found! Please make sure you have selected the correct Steam folder.",
        "steam_restart_success_msgbox": "🔄 Steam restarted successfully!\n\n🎮 You can now play your game!",
        "steam_restart_success_status": "⚡ STEAM RESTARTED",
        "steam_restart_error": "Could not restart Steam:\n{error}",
        "font_animation_error": "Font animation error: {error}",
        "critical_error_title": "Critical Error",
        "app_start_error": "Application could not be started:\n{error}",
        "faq_url": "https://rentry.co/topraksteamcrackerSSSeng",
        "online_fix_btn": "🔗 Apply Online Fix",
        "online_fix_not_found": "online_fix.py not found in the same directory!",
        "online_fix_error": "Error while running online fix script:\n{error}",
        "online_fix_success_msg": "Online Fix script started successfully.",
        "online_fix_success_status": "✅ ONLINE FIX STARTED"
    }
}



ONLINEFIX_REPO_OWNER = "toprak1224"
ONLINEFIX_REPO_NAME = "online-fix"
ONLINEFIX_BRANCH = "main"
ONLINEFIX_RAW_BASE = f"https://raw.githubusercontent.com/{ONLINEFIX_REPO_OWNER}/{ONLINEFIX_REPO_NAME}/{ONLINEFIX_BRANCH}"
ONLINEFIX_LIST_URL = "https://raw.githubusercontent.com/toprak1224/online-fix/main/mevcut%20oyunlar.txt"
ONLINEFIX_DOWNLOAD_URL_TEMPLATE = f"{ONLINEFIX_RAW_BASE}/{'{game_id}'}.rar"


try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    TKDND_AVAILABLE = True
except ImportError:
    TkinterDnD = None
    DND_FILES = None
    TKDND_AVAILABLE = False

class LegalNotice:
    def __init__(self, root):
        self.root = root
        self.selected_lang = 'tr'  
        self.strings = LANGUAGES[self.selected_lang]
        
        self.root.geometry("800x700")
        self.root.resizable(False, False)

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.bg_color = '#0a0a0a'
        self.text_color = '#ffffff'
        self.primary_button = '#4a90e2'
        self.danger_button = '#ff6b6b'

        self.main_frame = tk.Frame(root, bg=self.bg_color, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_ui()
        self.update_texts()

    def setup_ui(self):
        
        lang_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        lang_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        tr_btn = tk.Button(lang_frame, text="Türkçe", command=lambda: self.switch_language('tr'), 
                           bg=self.primary_button, fg=self.text_color, relief=tk.FLAT, font=("Segoe UI", 10, "bold"))
        tr_btn.pack(side=tk.LEFT, padx=5)

        en_btn = tk.Button(lang_frame, text="English", command=lambda: self.switch_language('en'), 
                           bg=self.primary_button, fg=self.text_color, relief=tk.FLAT, font=("Segoe UI", 10, "bold"))
        en_btn.pack(side=tk.LEFT, padx=5)

        button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        button_frame.pack(side=tk.BOTTOM, pady=(20, 0))

        self.var = tk.IntVar()
        self.checkbox = tk.Checkbutton(self.main_frame, variable=self.var, font=("Segoe UI", 11),
                                bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color,
                                activebackground=self.bg_color, activeforeground=self.text_color,
                                highlightthickness=0)
        self.checkbox.pack(side=tk.BOTTOM, pady=(10, 0))

        self.continue_btn = tk.Button(button_frame, command=self.check_acceptance,
                               font=("Segoe UI", 12, "bold"), bg=self.primary_button, fg=self.text_color,
                               relief=tk.FLAT, padx=30, pady=10)
        self.continue_btn.pack(side=tk.LEFT, padx=10)

        self.exit_btn = tk.Button(button_frame, command=self.root.quit,
                           font=("Segoe UI", 12, "bold"), bg=self.danger_button, fg=self.text_color,
                           relief=tk.FLAT, padx=30, pady=10)
        self.exit_btn.pack(side=tk.LEFT, padx=10)

        self.title_label = tk.Label(self.main_frame, font=("Segoe UI", 20, "bold"),
                             fg='#ffcc00', bg=self.bg_color)
        self.title_label.pack(side=tk.TOP, pady=(0, 20))

        text_frame = tk.Frame(self.main_frame, bg='#1a1a1a')
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Segoe UI", 11),
                            bg='#1a1a1a', fg=self.text_color, padx=20, pady=20,
                            borderwidth=0, highlightthickness=0)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

    def switch_language(self, lang_code):
        self.selected_lang = lang_code
        self.strings = LANGUAGES[lang_code]
        self.update_texts()

    def update_texts(self):
        self.root.title(self.strings['legal_title'])
        self.checkbox.config(text=self.strings['legal_checkbox'])
        self.continue_btn.config(text=self.strings['continue_btn'])
        self.exit_btn.config(text=self.strings['exit_btn'])
        self.title_label.config(text=self.strings['legal_header'])
        
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert(tk.END, self.strings['legal_text'])
        self.text_widget.config(state=tk.DISABLED)

    def check_acceptance(self):
        if self.var.get() == 1:
            self.root.destroy()
        else:
            messagebox.showwarning(self.strings['warning'], self.strings['accept_warning'])

class OnlineFixDownloaderWindow:
    def __init__(self, parent_app: "SteamManifestTool"):
        self.parent_app = parent_app
        self.root = parent_app.root
        self.window = tk.Toplevel(self.root)
        self.window.title("🎮 Toprak Online Fix İndirici - Hızlı Batch API")
        self.window.geometry("1000x700")
        self.window.configure(bg=parent_app.bg_color)
        self.window.resizable(False, False)

        self.games = []
        self.games_with_names = {}
        self.session = requests.Session()
        self.cache_file = "game_names_cache.json"
        self.applist_map = None  # {appid(str): name(str)}

        outer = tk.Frame(self.window, bg=parent_app.bg_color, padx=15, pady=15)
        outer.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(outer, text="🎮 Toprak Online Fix İndirici", font=("Segoe UI", 18, "bold"), fg=parent_app.text_color, bg=parent_app.bg_color)
        title.pack(fill=tk.X, pady=(0, 10))

        subtitle = tk.Label(outer, text="⚡ Hızlı Batch API ile 20x Daha Hızlı Oyun İsmi Yükleme", font=("Segoe UI", 10, "italic"), fg=parent_app.primary_button, bg=parent_app.bg_color)
        subtitle.pack(fill=tk.X, pady=(0, 10))

        content = tk.Frame(outer, bg=parent_app.bg_color)
        content.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(content, bg=parent_app.secondary_bg, padx=15, pady=15)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right = tk.Frame(content, bg=parent_app.secondary_bg, padx=15, pady=15)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        header = tk.Frame(left, bg=parent_app.secondary_bg)
        header.pack(fill=tk.X)

        refresh_btn = tk.Button(header, text="🚀 Oyun Listesini Hızlı Yenile (Batch API)", command=self.refresh_game_list, bg=parent_app.primary_button, fg=parent_app.text_color, font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=12, pady=8, cursor="hand2")
        refresh_btn.pack(side=tk.LEFT)
        parent_app.add_button_hover_effects(refresh_btn, parent_app.primary_button, parent_app._get_hover_color(parent_app.primary_button))

        self.name_progress = ttk.Progressbar(left, mode="determinate")
        self.name_progress.pack(fill=tk.X, pady=(10, 10))
        self.name_progress.pack_forget()

        self.loading_label = tk.Label(left, text="", font=("Segoe UI", 10, "bold"), fg=parent_app.primary_button, bg=parent_app.secondary_bg)
        self.loading_label.pack(fill=tk.X)
        self.loading_label.pack_forget()

        list_container = tk.Frame(left, bg=parent_app.secondary_bg)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.game_list = tk.Listbox(list_container, font=("Segoe UI", 11), bg=parent_app.highlight_color, fg=parent_app.text_color, selectbackground=parent_app.primary_button, relief=tk.FLAT)
        self.game_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.game_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.game_list.yview)

        download_btn = tk.Button(left, text="⬇️ Seçili Oyunu İndir", command=self.download_selected_game, bg=parent_app.info_button, fg=parent_app.text_color, font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=12, pady=8, cursor="hand2")
        download_btn.pack(pady=(10, 0))
        parent_app.add_button_hover_effects(download_btn, parent_app.info_button, parent_app._get_hover_color(parent_app.info_button))

        manual_btn = tk.Button(right, text="🎯 Manuel Steam ID İle İndir", command=self.open_manual_input, bg=parent_app.success_button, fg=parent_app.text_color, font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=12, pady=8, cursor="hand2")
        manual_btn.pack(fill=tk.X)
        parent_app.add_button_hover_effects(manual_btn, parent_app.success_button, parent_app._get_hover_color(parent_app.success_button))

        howto_btn = tk.Button(right, text="❓ Nasıl Kullanılır?", command=self.show_howto, bg=parent_app.info_button, fg=parent_app.text_color, font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=12, pady=8, cursor="hand2")
        howto_btn.pack(fill=tk.X, pady=(10, 0))
        parent_app.add_button_hover_effects(howto_btn, parent_app.info_button, parent_app._get_hover_color(parent_app.info_button))

        clear_cache_btn = tk.Button(right, text="🗑️ Önbelleği Temizle", command=self.clear_cache, bg=parent_app.danger_button, fg=parent_app.text_color, font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=12, pady=8, cursor="hand2")
        clear_cache_btn.pack(fill=tk.X, pady=(10, 0))
        parent_app.add_button_hover_effects(clear_cache_btn, parent_app.danger_button, parent_app._get_hover_color(parent_app.danger_button))

        status_label = tk.Label(right, text="📊 İndirme Durumu", font=("Segoe UI", 12, "bold"), fg=parent_app.text_color, bg=parent_app.secondary_bg)
        status_label.pack(pady=(15, 5))

        self.status_text = tk.Text(right, height=12, bg=parent_app.highlight_color, fg=parent_app.text_color, font=("Consolas", 10), relief=tk.FLAT)
        self.status_text.pack(fill=tk.BOTH, expand=False)

        self.progress_bar = ttk.Progressbar(right, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))

        self.append_status("⚡ Hazır - Oyun listesi için 'Yenile'ye tıklayın")

    def show_howto(self):
        howto_text = (
            "Online Fix İndirici Kullanımı:\n\n"
            "1) 'Oyun Listesini Hızlı Yenile' ile listeden oyunu bulun.\n"
            "2) Oyunu seçip 'Seçili Oyunu İndir'e tıklayın (veya 'Manuel Steam ID İle İndir').\n"
            "3) İnen RAR dosyasını açın.\n"
            "4) RAR içindeki tüm dosyaları oyunun yüklü olduğu klasöre kopyalayın.\n"
            "   - Örn: C:\\Program Files (x86)\\Steam\\steamapps\\common\\<Oyun Adı>\n"
            "5) Steam'i kapatıp tekrar açın ve oyunu başlatın.\n\n"
            "Notlar:\n"
            "- Antivirüs karantinaya alırsa dosyaları geri yükleyin.\n"
            "- Admin olarak çalıştırmanız önerilir.\n"
        )
        try:
            messagebox.showinfo("Nasıl Kullanılır?", howto_text, parent=self.window)
        except Exception:
            messagebox.showinfo("Nasıl Kullanılır?", howto_text)

    def append_status(self, msg: str):
        try:
            self.status_text.insert(tk.END, msg + "\n")
            self.status_text.see(tk.END)
        except Exception:
            pass

    def load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            return {}
        return {}

    def save_cache(self, cache: dict):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.append_status(f"Cache kaydetme hatası: {e}")

    def refresh_game_list(self):
        self.append_status("🔄 Online fix listesi çekiliyor...")
        threading.Thread(target=self._refresh_game_list_thread, daemon=True).start()

    def _refresh_game_list_thread(self):
        api_url = ONLINEFIX_LIST_URL
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain; */*'
            }
            response = requests.get(api_url, headers=headers, timeout=20)
            response.raise_for_status()
            raw_text = response.text.strip()
            
            # Debug: Ham veriyi göster
            self.root.after(0, lambda: self.append_status(f"🔍 Ham veri (ilk 200 karakter): {raw_text[:200]}"))
            
            games = []
            try:
                data = response.json()
                iterable = []
                if isinstance(data, dict):
                    if data.get('status') == 'success' and 'files' in data:
                        files = data['files']
                        if isinstance(files, dict):
                            iterable = list(files.keys())
                        else:
                            iterable = files
                    elif 'ids' in data and isinstance(data['ids'], list):
                        iterable = data['ids']
                    else:
                        for key in ('list', 'data', 'games'):
                            if key in data and isinstance(data[key], list):
                                iterable = data[key]
                                break
                elif isinstance(data, list):
                    iterable = data

                for item in iterable:
                    if isinstance(item, (str, int)):
                        gid = str(item)
                    elif isinstance(item, dict):
                        gid = str(item.get('id') or item.get('appid') or item.get('game_id') or '')
                    else:
                        gid = ''
                    if gid.isdigit():
                        games.append({'game_id': gid})

                if not games and not raw_text:
                    raise ValueError('Sunucudan boş yanıt alındı')
            except json.JSONDecodeError:
                ids = re.findall(r'\b\d{3,}\b', raw_text)
                for gid in ids:
                    games.append({'game_id': gid})
            self.root.after(0, lambda: self._on_games_loaded(games))
        except Exception as e:
            err_text = str(e)
            self.root.after(0, lambda err_text=err_text: self.append_status(f"❌ Oyun listesi yüklenemedi: {err_text}"))

    def _on_games_loaded(self, games):
        self.games = games
        self.games_with_names = {}
        self.game_list.delete(0, tk.END)
        
        self.append_status("🔄 Steam API'den oyun isimleri yükleniyor...")
        
        # Önce Steam AppList'i yükle, sonra listeyi doldur
        threading.Thread(target=self._load_names_and_populate, args=(games,), daemon=True).start()
    
    def _load_names_and_populate(self, games):
        try:
            # Steam AppList'i yükle (ana programdaki gibi)
            self.root.after(0, lambda: self.append_status("🔄 Steam AppList API yükleniyor..."))
            self._load_applist_map()
            
            if self.applist_map:
                self.root.after(0, lambda: self.append_status(f"✅ Steam AppList yüklendi! {len(self.applist_map)} oyun bulundu"))
            else:
                self.root.after(0, lambda: self.append_status("❌ Steam AppList yüklenemedi"))
            
            cache = self.load_cache()
            
            # Cache'deki eski "Oyun ID" formatındaki kayıtları temizle
            cache_updated = False
            for gid in list(cache.keys()):
                if cache[gid].startswith(f"Oyun {gid}"):
                    del cache[gid]
                    cache_updated = True
            if cache_updated:
                self.save_cache(cache)
                self.root.after(0, lambda: self.append_status("🗑️ Eski cache kayıtları temizlendi"))
            
            # Tüm oyunları işle ve UI'yi tek seferde güncelle
            games_to_add = []
            found_names = 0
            for g in games:
                gid = g['game_id']
                # Debug: ID'yi kontrol et
                self.root.after(0, lambda id=gid: self.append_status(f"🔍 ID kontrol ediliyor: {id}"))
                
                # Önce cache'den bak (ama "Oyun ID" formatındaki eski kayıtları yoksay)
                game_name = cache.get(gid)
                if game_name and not game_name.startswith(f"Oyun {gid}"):
                    self.root.after(0, lambda id=gid, name=game_name: self.append_status(f"📁 Cache'den bulundu: {id} -> {name}"))
                else:
                    game_name = None  # Cache'deki eski format, Steam API'den tekrar al
                
                if not game_name and self.applist_map:
                    # Cache'de yoksa Steam AppList'ten bak
                    game_name = self.applist_map.get(gid)
                    if game_name:
                        found_names += 1
                        self.root.after(0, lambda id=gid, name=game_name: self.append_status(f"🎮 Steam API'den bulundu: {id} -> {name}"))
                    else:
                        # ID'nin AppList'te olup olmadığını kontrol et
                        self.root.after(0, lambda id=gid: self.append_status(f"❌ Steam API'de bulunamadı: {id}"))
                        
                if not game_name:
                    game_name = f"Oyun {gid}"
                
                self.games_with_names[gid] = game_name
                games_to_add.append(game_name)
            
            # UI thread'inde tüm listeyi güncelle
            def update_ui():
                for game_name in games_to_add:
                    self.game_list.insert(tk.END, f"🎮 {game_name}")
                self.append_status(f"✅ {len(games)} oyun yüklendi! ({found_names} isim Steam API'den bulundu)")
            
            self.root.after(0, update_ui)
        except Exception as e:
            self.root.after(0, lambda: self.append_status(f"❌ Oyun isimleri yüklenemedi: {str(e)}"))

    def _start_fetching_names_batch(self):
        self.loading_label.config(text="Batch API ile oyun isimleri hızla yükleniyor... (0/0)")
        self.loading_label.pack(fill=tk.X)
        self.name_progress.pack(fill=tk.X)
        threading.Thread(target=self._fetch_names_thread, daemon=True).start()

    def _fetch_names_thread(self):
        game_ids = [g['game_id'] for g in self.games]
        total = len(game_ids)
        cache = self.load_cache()
        processed = 0

        def update_progress():
            percent = int((processed / max(1, total)) * 100)
            self.name_progress['value'] = percent
            self.loading_label.config(text=f"Batch API ile oyun isimleri hızla yükleniyor... ({processed}/{total})")

        for gid in list(game_ids):
            if gid in cache:
                name = cache[gid]
                processed += 1
                self.root.after(0, lambda gid=gid, name=name: self._set_game_name(gid, name))
                self.root.after(0, update_progress)

        uncached = [gid for gid in game_ids if gid not in cache]

        
        try:
            self._load_applist_map()
            if self.applist_map:
                still_uncached = []
                for gid in uncached:
                    name = self.applist_map.get(gid)
                    if name:
                        cache[gid] = name
                        processed += 1
                        self.root.after(0, lambda gid=gid, name=name: self._set_game_name(gid, name))
                        self.root.after(0, update_progress)
                    else:
                        still_uncached.append(gid)
                uncached = still_uncached
        except Exception as e:
            err_text = str(e)
            self.append_status(f"AppList yükleme hatası: {err_text}")
        batch_size = 20
        for i in range(0, len(uncached), batch_size):
            batch = uncached[i:i + batch_size]
            try:
                results = self._fetch_steam_batch(batch)
                for gid in batch:
                    name = results.get(gid)
                    if not name:
                        name = self._get_steamspy_name(gid) or f"Oyun {gid}"
                    cache[gid] = name
                    processed += 1
                    self.root.after(0, lambda gid=gid, name=name: self._set_game_name(gid, name))
                    self.root.after(0, update_progress)
                time.sleep(0.3)
            except Exception as e:
                self.append_status(f"Batch hatası: {e}")
                for gid in batch:
                    name = f"Oyun {gid}"
                    cache[gid] = name
                    processed += 1
                    self.root.after(0, lambda gid=gid, name=name: self._set_game_name(gid, name))
                    self.root.after(0, update_progress)

        self.save_cache(cache)
        self.root.after(0, self._names_finished)

    def _load_applist_map(self):
        if self.applist_map is not None:
            return
        apps = fetch_steam_app_list(self.session)
        mapping = {}
        for item in apps:
            appid = item.get('appid')
            name = item.get('name')
            if appid and name:
                mapping[appid] = name
        self.applist_map = mapping

    def _fetch_steam_batch(self, game_ids):
        results = {}
        ids_string = ",".join(game_ids)
        url = f"https://store.steampowered.com/api/appdetails?appids={ids_string}&l=turkish&filters=basic"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        resp = self.session.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for gid in game_ids:
            try:
                if gid in data and data[gid].get('success'):
                    results[gid] = data[gid]['data'].get('name', f"Oyun {gid}")
            except Exception:
                results[gid] = f"Oyun {gid}"
        return results

    def _get_steamspy_name(self, app_id):
        try:
            url = f"https://steamspy.com/api.php?request=appdetails&appid={app_id}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = self.session.get(url, headers=headers, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            return data.get('name')
        except Exception:
            return None

    def _set_game_name(self, game_id, game_name):
        self.games_with_names[game_id] = game_name
        for i in range(self.game_list.size()):
            text = self.game_list.get(i)
            if f"ID: {game_id}" in text or text.startswith(f"🎮 Oyun ID: {game_id}"):
                self.game_list.delete(i)
                self.game_list.insert(i, f"🎮 {game_name}")
                break

    def _names_finished(self):
        self.append_status("✅ Batch API ile oyun isimleri yüklendi! (game_names_cache.json güncellendi)")
        self.name_progress.pack_forget()
        self.loading_label.pack_forget()

    def download_selected_game(self):
        sel = self.game_list.curselection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen bir oyun seçin!", parent=self.window)
            return
        index = sel[0]
        # Liste, self.games sırasıyla dolduruluyor; seçilen index'ten game_id alınır
        try:
            game_id = self.games[index]['game_id']
        except Exception:
            messagebox.showerror("Hata", "Geçersiz seçim!", parent=self.window)
            return
        game_name = self.games_with_names.get(game_id, f"Oyun {game_id}")
        self._start_download(game_id, game_name)

    def open_manual_input(self):
        game_id = simpledialog.askstring("Manuel Game ID Girişi", "Lütfen Steam ID girin:", parent=self.window)
        if not game_id:
            return
        game_id = game_id.strip()
        if not game_id.isdigit():
            messagebox.showwarning("Hata", "Lütfen geçerli bir sayısal Steam ID girin!", parent=self.window)
            return
        cache = self.load_cache()
        game_name = cache.get(game_id, f"Oyun {game_id}")
        self._start_download(game_id, game_name)

    def _start_download(self, game_id, game_name):
        self.progress_bar['value'] = 0
        self.append_status(f"🚀 '{game_name}' (ID: {game_id}) indirme başlatıldı...")
        threading.Thread(target=self._download_thread, args=(game_id, game_name), daemon=True).start()

    def _download_thread(self, game_id, game_name):
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        download_url = ONLINEFIX_DOWNLOAD_URL_TEMPLATE.format(game_id=game_id)
        try:
            self.root.after(0, lambda: self.append_status(f"'{game_name}' indiriliyor..."))
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = self.session.get(download_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            file_name = None
            cd = response.headers.get('content-disposition')
            if cd:
                m = re.search(r'filename="?([^";]+)"?', cd)
                if m:
                    file_name = m.group(1)
            if not file_name:
                # Varsayılan olarak .rar uzantısı ile game_id adına kaydet
                file_name = f"{game_id}.rar"

            file_path = os.path.join(desktop_path, file_name)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    f.write(chunk)
                    if total_size:
                        downloaded += len(chunk)
                        percent = int(100 * downloaded / total_size)
                        self.root.after(0, lambda v=percent: self.progress_bar.configure(value=v))

            if file_name.lower().endswith('.zip'):
                extract_folder = os.path.join(desktop_path, re.sub(r'[<>:"/\\|?*]', '_', f"{game_name}_Extracted"))
                os.makedirs(extract_folder, exist_ok=True)
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)
                    try:
                        os.remove(file_path)
                        msg = f"{game_name} başarıyla indirildi ve çıkarıldı.\n\nKonum: {extract_folder}\n\nZip dosyası silindi."
                    except Exception:
                        msg = f"{game_name} başarıyla indirildi ve çıkarıldı.\n\nKonum: {extract_folder}\n\nZip dosyası silinemedi."
                    self.root.after(0, lambda: [self.progress_bar.configure(value=100), self.append_status("✅ İndirme Tamamlandı!"), messagebox.showinfo("İndirme Tamamlandı", msg, parent=self.window)])
                except Exception as e:
                    err_text = str(e)
                    self.root.after(0, lambda err_text=err_text: messagebox.showerror("Hata", f"Zip dosyası çıkarılamadı: {err_text}", parent=self.window))
            else:
                self.root.after(0, lambda: [self.progress_bar.configure(value=100), self.append_status("✅ İndirme Tamamlandı!"), messagebox.showinfo("İndirme Tamamlandı", f"{game_name} masaüstüne indirildi!\n\nKonum: {file_path}", parent=self.window)])
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', 'unknown')
            self.root.after(0, lambda status_code=status_code: messagebox.showerror("Hata", f"Sunucu hatası: {status_code}. Bu oyun için dosya bulunamadı.", parent=self.window))
        except Exception as e:
            err_text = str(e)
            self.root.after(0, lambda err_text=err_text: messagebox.showerror("Hata", f"İndirme hatası: {err_text}", parent=self.window))

    def clear_cache(self):
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                self.append_status("🗑️ Önbellek başarıyla temizlendi!")
                messagebox.showinfo("Önbellek Temizlendi", "Oyun isimleri önbelleği temizlendi.", parent=self.window)
            else:
                messagebox.showinfo("Bilgi", "Temizlenecek önbellek dosyası bulunamadı.", parent=self.window)
        except Exception as e:
            self.append_status(f"❌ Önbellek temizleme hatası: {e}")
            messagebox.showerror("Hata", f"Önbellek temizlenirken hata: {e}", parent=self.window)

class SteamManifestTool:
    def __init__(self, root, lang_code='tr'):
        self.root = root
        self.strings = LANGUAGES[lang_code]
        
        self.root.title(self.strings['main_title'])
        self.root.geometry("1000x1000")
        self.root.resizable(False, False)

        self.bg_color = '#0a0a0a'
        self.secondary_bg = '#1a1a1a'
        self.accent_color = '#2d2d2d'
        self.highlight_color = '#3d3d3d'
        self.text_color = '#ffffff'
        self.primary_button = '#4a90e2'
        self.success_button = '#50c878'
        self.danger_button = '#ff6b6b'
        self.info_button = '#6a5acd'
        self.entry_insert_color = '#4a90e2'
        self.title_glow_colors = ['#ffffff', '#e0e0e0', '#c0c0c0', '#e0e0e0', '#ffffff']
        self.particle_color = '#4a90e2'

        self.installed_games_file = "installed_games.json"

        self.animation_running = False
        self.pulse_direction = 1
        self.pulse_alpha = 0.3

        self.create_animated_background()

        main_frame = tk.Frame(root, bg=self.bg_color, padx=40, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(pady=(0, 30))

        self.title_label = tk.Label(title_frame, text=self.strings['app_header'],
                              font=("Segoe UI", 24, "bold"),
                              fg=self.text_color, bg=self.bg_color)
        self.title_label.pack()

        self.subtitle_label = tk.Label(title_frame, text=self.strings['app_subtitle'],
                                 font=("Segoe UI", 12, "italic"),
                                 fg=self.primary_button, bg=self.bg_color)
        self.subtitle_label.pack(pady=(5, 0))

        self.separator = tk.Frame(title_frame, height=2, bg=self.primary_button)
        self.separator.pack(fill=tk.X, pady=(15, 0))

        self.create_steam_path_section(main_frame)
        self.create_game_id_section(main_frame)
        self.create_drag_drop_section(main_frame)
        self.create_button_section(main_frame)
        self.create_status_section(main_frame)
        self.create_footer(main_frame)

        self.create_game_search_button(main_frame)
        self.create_hid_download_button(main_frame)
        self.create_hid_remove_button(main_frame)
        self.create_steamdb_button(main_frame)
        self.create_sss_button(main_frame)
        self.create_zip_upload_button(main_frame)
        self.create_online_fix_button(main_frame)
        self.create_show_installed_games_button(main_frame)
        self.create_about_button(main_frame)

        self.app_id_entry.bind('<Return>', lambda e: self.download_and_process())
        self.app_id_entry.focus()

        self.start_animations()
        self.root.attributes('-alpha', 0.0)
        self.entrance_animation()

        self.game_list = []
        threading.Thread(target=self.load_game_list, daemon=True).start()

        self.auto_detect_steam_path()

    def _get_hover_color(self, base_hex_color):
        base_hex = base_hex_color.lstrip('#')
        rgb = tuple(int(base_hex[i:i+2], 16) for i in (0, 2, 4))
        hover_rgb = tuple(min(255, c + 30) for c in rgb)
        return '#%02x%02x%02x' % hover_rgb
        
    def create_about_button(self, parent):
        self.about_btn = tk.Button(
            parent,
            text=self.strings['about_btn'],
            command=self.show_about_dialog,
            bg=self.info_button,
            fg=self.text_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.about_btn.place(relx=0.72, rely=0.93)
        self.add_button_hover_effects(self.about_btn, self.info_button, self._get_hover_color(self.info_button))

    def show_about_dialog(self):
        about_window = tk.Toplevel(self.root)
        about_window.title(self.strings['about_title'])
        about_window.geometry("450x400")
        about_window.configure(bg=self.bg_color)
        about_window.resizable(False, False)

        about_window.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        about_width = about_window.winfo_width()
        about_height = about_window.winfo_height()
        x = main_x + (main_width // 2) - (about_width // 2)
        y = main_y + (main_height // 2) - (about_height // 2)
        about_window.geometry(f'+{x}+{y}')


        tk.Label(about_window, text="Toprak Steam Cracker",
                 font=("Segoe UI", 16, "bold"), fg=self.text_color, bg=self.bg_color).pack(pady=10)
        tk.Label(about_window, text=self.strings['version'],
                 font=("Segoe UI", 10), fg=self.text_color, bg=self.bg_color).pack(pady=2)
        tk.Label(about_window, text=self.strings['developer'],
                 font=("Segoe UI", 10), fg=self.text_color, bg=self.bg_color).pack(pady=2)

        tk.Label(about_window, text=self.strings['about_desc'],
                 font=("Segoe UI", 10, "italic"), fg=self.text_color, bg=self.bg_color, wraplength=400).pack(pady=10)

        github_label = tk.Label(about_window, text=self.strings['github_repo'],
                                font=("Segoe UI", 10, "underline"), fg=self.primary_button, bg=self.bg_color, cursor="hand2")
        github_label.pack(pady=5)
        github_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/SteamAutoCracks/ManifestHub"))

        message_label = tk.Label(about_window, text=self.strings['about_disclaimer'],
                 font=("Segoe UI", 9), fg=self.text_color, bg=self.bg_color, wraplength=400, justify=tk.CENTER)
        message_label.pack(pady=10)

        close_btn = tk.Button(about_window, text=self.strings['close_btn'], command=about_window.destroy,
                              bg=self.accent_color, fg=self.text_color, font=("Segoe UI", 10, "bold"),
                              relief=tk.FLAT, padx=20, pady=8)
        self.add_button_hover_effects(close_btn, self.accent_color, self._get_hover_color(self.accent_color), original_padx=20, original_pady=8)
        close_btn.pack(pady=10)

    def create_show_installed_games_button(self, parent):
        self.installed_games_btn = tk.Button(
            parent,
            text=self.strings['installed_games_btn'],
            command=self.show_installed_games,
            bg=self.info_button,
            fg=self.text_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.installed_games_btn.place(relx=0.01, rely=0.07)
        self.add_button_hover_effects(self.installed_games_btn, self.info_button, self._get_hover_color(self.info_button))

    def load_installed_games(self):
        if os.path.exists(self.installed_games_file):
            with open(self.installed_games_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def save_installed_games(self, games):
        with open(self.installed_games_file, 'w', encoding='utf-8') as f:
            json.dump(games, f, indent=4, ensure_ascii=False)

    def add_installed_game(self, app_id, game_name, lua_files=None, manifest_files=None):
        installed_games = self.load_installed_games()
        entry = installed_games.get(app_id)
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

        installed_games[app_id] = entry_data
        self.save_installed_games(installed_games)

    def remove_installed_game_entry(self, app_id):
        installed_games = self.load_installed_games()
        if app_id in installed_games:
            del installed_games[app_id]
            self.save_installed_games(installed_games)

    def show_installed_games(self):
        installed_games_window = tk.Toplevel(self.root)
        installed_games_window.title(self.strings['installed_games_title'])
        installed_games_window.geometry("600x500")
        installed_games_window.configure(bg=self.secondary_bg)
        installed_games_window.resizable(False, False)

        tk.Label(installed_games_window, text=self.strings['installed_games_btn'], font=("Segoe UI", 16, "bold"),
                fg=self.text_color, bg=self.secondary_bg).pack(pady=10)

        list_frame = tk.Frame(installed_games_window, bg=self.accent_color)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.installed_games_listbox = tk.Listbox(list_frame, font=("Segoe UI", 11),
                                               bg=self.highlight_color, fg=self.text_color, selectbackground=self.primary_button,
                                               yscrollcommand=scrollbar.set, relief=tk.FLAT)
        self.installed_games_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.installed_games_listbox.yview)

        self.populate_installed_games_list()
        self.installed_games_listbox.bind("<<ListboxSelect>>", self.on_installed_game_select)


        button_frame = tk.Frame(installed_games_window, bg=self.secondary_bg)
        button_frame.pack(pady=10)
        
        close_btn = tk.Button(button_frame, text=self.strings['close_btn'], command=installed_games_window.destroy,
                            bg=self.primary_button, fg=self.text_color, font=("Segoe UI", 10, "bold"),
                            relief=tk.FLAT, padx=20)
        self.add_button_hover_effects(close_btn, self.primary_button, self._get_hover_color(self.primary_button), original_padx=20)
        close_btn.pack(side=tk.LEFT, padx=10)

    def populate_installed_games_list(self):
        if not hasattr(self, 'installed_games_listbox'):
            return
        self.installed_games_listbox.delete(0, tk.END)
        installed_games = self.load_installed_games()
        if not installed_games:
            self.installed_games_listbox.insert(tk.END, self.strings['no_installed_games'])
            return

        for app_id, info in installed_games.items():
            if isinstance(info, dict):
                game_name = info.get('name', f"Oyun {app_id}")
            else:
                game_name = info
            self.installed_games_listbox.insert(tk.END, f"{game_name}{self.strings['game_id_format'].format(app_id=app_id)}")

    def on_installed_game_select(self, event):
        selection = self.installed_games_listbox.curselection()
        if not selection:
            return

        selected_text = self.installed_games_listbox.get(selection[0])
        if '(' in selected_text and ')' in selected_text:
            app_id = selected_text.split('(')[-1].replace(')', '').replace('ID: ', '')
            self.app_id_var.set(app_id)
            game_name = selected_text.split(' (')[0]
            self.animate_status_message(self.strings['game_selected_status'].format(game_name=game_name), self.success_button)

    def remove_hid_dll(self):
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'steam.exe'])
            time.sleep(2)
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                dll_path = os.path.join(steam_path, "hid.dll")
                if os.path.exists(dll_path):
                    os.remove(dll_path)
                    messagebox.showinfo(self.strings['success'], self.strings['hid_removed_success'])
                    self.animate_status_message(self.strings['hid_removed_status'], self.success_button)
                else:
                    messagebox.showinfo(self.strings['info'], self.strings['hid_not_found'])
                    self.animate_status_message(self.strings['hid_not_found_status'], self.primary_button)
        except Exception as e:
            messagebox.showerror(self.strings['error'], self.strings['hid_remove_error'].format(error=str(e)))
            self.animate_status_message(self.strings['hid_remove_error_status'], self.danger_button)

    def create_hid_remove_button(self, parent):
        self.hid_remove_btn = tk.Button(
            parent,
            text=self.strings['remove_hid_btn'],
            command=self.remove_hid_dll,
            bg=self.danger_button,
            fg=self.text_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.hid_remove_btn.place(relx=0.85, rely=0.07)
        self.add_button_hover_effects(self.hid_remove_btn, self.danger_button, self._get_hover_color(self.danger_button))

    def create_zip_upload_button(self, parent):
        self.zip_btn = tk.Button(
            parent,
            text=self.strings['zip_upload_btn'],
            command=self.upload_zip_file,
            bg=self.info_button,
            fg=self.text_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.zip_btn.place(relx=0.12, rely=0.95)
        self.add_button_hover_effects(self.zip_btn, self.info_button, self._get_hover_color(self.info_button))

    def upload_zip_file(self):
        steam_path = self.steam_path_var.get().strip()
        if not steam_path:
            self.show_error_message(self.strings['select_steam_folder_prompt'])
            return

        file_path = filedialog.askopenfilename(
            title=self.strings['select_zip_title'],
            filetypes=[(self.strings['zip_files_filter'], "*.zip"), (self.strings['all_files_filter'], "*.*")]
        )

        if not file_path:
            return

        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                valid_files = [f for f in zip_ref.namelist() if f.lower().endswith(('.manifest', '.lua'))]

                if not valid_files:
                    self.show_error_message(self.strings['zip_no_manifest_lua'])
                    return

                self.process_zip_files(zip_ref, steam_path)

        except Exception as e:
            self.show_error_message(self.strings['zip_process_error'].format(error=str(e)))

    def process_zip_files(self, zip_ref, steam_path):
        stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
        depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
        os.makedirs(stplugin_dir, exist_ok=True)
        os.makedirs(depotcache_dir, exist_ok=True)

        lua_count = 0
        manifest_count = 0

        for file in zip_ref.namelist():
            if file.endswith('.lua'):
                target = os.path.join(stplugin_dir, os.path.basename(file))
                with zip_ref.open(file) as src, open(target, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                lua_count += 1
            elif file.endswith('.manifest'):
                target = os.path.join(depotcache_dir, os.path.basename(file))
                with zip_ref.open(file) as src, open(target, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                manifest_count += 1

        messagebox.showinfo(self.strings['success'], self.strings['zip_success_msg'].format(lua_count=lua_count, manifest_count=manifest_count))
        self.animate_status_message(self.strings['zip_success_status'].format(count=lua_count + manifest_count), self.success_button)

    def auto_detect_steam_path(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                if os.path.exists(steam_path):
                    self.steam_path_var.set(steam_path)
                    self.animate_status_message(self.strings['steam_path_auto_detected'], self.success_button)
                    return
        except Exception:
            pass

        common_paths = [
            os.path.expanduser("~") + "\\Program Files (x86)\\Steam",
            os.path.expanduser("~") + "\\Program Files\\Steam",
            "C:\\Program Files (x86)\\Steam",
            "C:\\Program Files\\Steam"
        ]

        for path in common_paths:
            if os.path.exists(path):
                self.steam_path_var.set(path)
                self.animate_status_message(self.strings['steam_path_auto_detected'], self.success_button)
                return

        self.animate_status_message(self.strings['steam_path_not_detected'], self.primary_button)

    def open_faq_link(self):
        faq_url = self.strings.get("faq_url")
        if faq_url:
            webbrowser.open(faq_url)

    def create_sss_button(self, parent):
        self.sss_btn = tk.Button(
            parent,
            text=self.strings['faq_btn'],
            command=self.open_faq_link,
            bg=self.info_button,
            fg=self.text_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.sss_btn.place(relx=0.01, rely=0.95)
        self.add_button_hover_effects(self.sss_btn, self.info_button, self._get_hover_color(self.info_button))

    def create_drag_drop_section(self, parent):
        self.drag_frame = tk.Frame(parent, bg=self.secondary_bg, relief=tk.FLAT, bd=0)
        self.drag_frame.pack(fill=tk.X, pady=(0, 20))

        border_frame = tk.Frame(self.drag_frame, bg=self.info_button, height=1)
        border_frame.pack(fill=tk.X)

        inner_frame = tk.Frame(self.drag_frame, bg=self.secondary_bg, padx=25, pady=25)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        drag_label = tk.Label(inner_frame, text=self.strings['drag_drop_title'],
                            font=("Segoe UI", 13, "bold"),
                            fg=self.text_color, bg=self.secondary_bg)
        drag_label.pack(anchor=tk.W, pady=(0, 15))

        self.drop_area = tk.Label(inner_frame, text=self.strings['drag_drop_label'],
                                font=("Segoe UI", 11),
                                bg=self.highlight_color, fg=self.text_color,
                                relief=tk.RAISED, bd=2,
                                padx=50, pady=40)
        self.drop_area.pack(fill=tk.BOTH, expand=True)

        if hasattr(self.drop_area, 'drop_target_register'):
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
        else:
            self.drop_area.config(text=self.strings['dnd_not_supported'])

        self.drop_area.bind('<Enter>', lambda e: self.drop_area.config(bg=self._get_hover_color(self.highlight_color)))
        self.drop_area.bind('<Leave>', lambda e: self.drop_area.config(bg=self.highlight_color))

    def on_drop(self, event):
        steam_path = self.steam_path_var.get().strip()
        if not steam_path:
            self.show_error_message(self.strings['select_steam_folder_prompt'])
            return

        files = []
        if isinstance(event.data, str):
            files = [f.strip('{}') for f in event.data.split('} {')]
        elif isinstance(event.data, list):
            files = event.data
        else:
            self.show_error_message(self.strings['unsupported_drop_format'])
            return

        valid_files = []
        for f in files:
            if isinstance(f, str):
                if os.path.isdir(f):
                    for root_dir, _, files_in_dir in os.walk(f):
                        for file_in_dir in files_in_dir:
                            file_path = os.path.join(root_dir, file_in_dir)
                            if os.path.isfile(file_path) and file_path.lower().endswith(('.manifest', '.lua')):
                                valid_files.append(file_path)
                elif os.path.isfile(f) and f.lower().endswith(('.manifest', '.lua')):
                    valid_files.append(f)
            elif isinstance(f, dict) and 'name' in f and f['name'].lower().endswith(('.manifest', '.lua')):
                valid_files.append(f['name'])

        if not valid_files:
            self.show_error_message(self.strings['only_manifest_lua_accepted'])
            return

        try:
            stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
            depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
            os.makedirs(stplugin_dir, exist_ok=True)
            os.makedirs(depotcache_dir, exist_ok=True)

            lua_count = 0
            manifest_count = 0
            installed_lua_files = []
            installed_manifest_files = []
            installed_lua_files = []
            installed_manifest_files = []
            installed_lua_files = []
            installed_manifest_files = []
            installed_lua_files = []
            installed_manifest_files = []

            for file_path in valid_files:
                file_name = os.path.basename(file_path)
                if file_name.lower().endswith('.lua'):
                    dest = os.path.join(stplugin_dir, file_name)
                    shutil.copy2(file_path, dest)
                    lua_count += 1
                elif file_name.lower().endswith('.manifest'):
                    dest = os.path.join(depotcache_dir, file_name)
                    shutil.copy2(file_path, dest)
                    manifest_count += 1

            messagebox.showinfo(self.strings['success'], self.strings['drag_drop_success_msg'].format(lua_count=lua_count, manifest_count=manifest_count))
            self.animate_status_message(self.strings['drag_drop_success_status'].format(count=lua_count + manifest_count), self.success_button)

        except Exception as e:
            self.show_error_message(self.strings['file_process_error'].format(error=str(e)))

    def download_hid_dll(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
        except Exception:
            steam_path = None

        save_path = os.path.join(steam_path, "hid.dll") if steam_path else os.path.join(os.path.expanduser("~"), "Desktop", "hid.dll")

        if not steam_path:
            messagebox.showwarning(self.strings['warning'], self.strings['hid_path_not_found_warning'])

        try:
            url = "https://raw.githubusercontent.com/toprak1224/hid.dll/main/hid.dll "
            urllib.request.urlretrieve(url, save_path)
            messagebox.showinfo(self.strings['success'], self.strings['dll_download_success'].format(save_path=save_path))
            self.animate_status_message(self.strings['dll_download_success_status'], self.success_button)
        except Exception as e:
            messagebox.showerror(self.strings['error'], self.strings['dll_download_error'].format(error=str(e)))
            self.animate_status_message(self.strings['dll_download_error_status'], self.danger_button)

    def create_hid_download_button(self, parent):
        self.hid_btn = tk.Button(
            parent,
            text=self.strings['download_hid_btn'],
            command=self.download_hid_dll,
            bg=self.info_button,
            fg=self.text_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.hid_btn.place(relx=0.85, rely=0.01)
        self.add_button_hover_effects(self.hid_btn, self.info_button, self._get_hover_color(self.info_button))

    def create_game_search_button(self, parent):
        self.search_btn = tk.Button(
            parent,
            text=self.strings['search_game_btn'],
            command=self.show_game_search,
            bg=self.info_button,
            fg=self.text_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=1,
            pady=8,
            cursor='hand2'
        )
        self.search_btn.place(relx=0.01, rely=0.01)
        self.add_button_hover_effects(self.search_btn, self.info_button, self._get_hover_color(self.info_button))

    def load_game_list(self):
        try:
            apps = fetch_steam_app_list()
            self.game_list = apps
        except Exception as e:
            self.game_list = []
            print(self.strings['game_list_fetch_error'].format(error=str(e)))

    def show_game_search(self):
        search_window = tk.Toplevel(self.root)
        search_window.title(self.strings['game_search_title'])
        search_window.geometry("800x800")
        search_window.configure(bg=self.secondary_bg)
        search_window.resizable(False, False)

        tk.Label(search_window, text=self.strings['search_steam_game_header'], font=("Segoe UI", 16, "bold"),
                fg=self.text_color, bg=self.secondary_bg).pack(pady=10)

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_window, textvariable=search_var, font=("Segoe UI", 12),
                                bg=self.highlight_color, fg=self.text_color,
                                insertbackground=self.entry_insert_color, relief=tk.FLAT)
        search_entry.pack(pady=5, ipadx=10, ipady=6, fill=tk.X, padx=50)

        suggestion_box = tk.Listbox(search_window, font=("Segoe UI", 10),
                                  bg=self.highlight_color, fg=self.text_color, height=15, relief=tk.FLAT,
                                  selectbackground=self.primary_button)
        suggestion_box.pack(pady=5, fill=tk.BOTH, expand=True, padx=50)

        hovered_index = [-1]  

        def on_mouse_hover(event):
            index = suggestion_box.nearest(event.y)
            if 0 <= hovered_index[0] < suggestion_box.size():
                suggestion_box.itemconfig(hovered_index[0], fg=self.text_color)
            hovered_index[0] = index
            suggestion_box.itemconfig(index, fg="#FFD700")

        suggestion_box.bind("<Motion>", on_mouse_hover)


        selected_label = tk.Label(search_window, text=self.strings['selected_game_label'], font=("Segoe UI", 11),
                                  fg=self.text_color, bg=self.secondary_bg)
        selected_label.pack(pady=5)

        cover_label = tk.Label(search_window, bg=self.secondary_bg)
        cover_label.pack(pady=10)
        detail_label = tk.Label(search_window, bg=self.secondary_bg, fg=self.text_color,
                                font=("Segoe UI", 10), justify="left", anchor="w")
        detail_label.pack(padx=50, pady=(5, 15), fill=tk.X)


        
        def fetch_and_show_cover(app_id):
            try:
                url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                if PIL_AVAILABLE:
                    image = Image.open(BytesIO(response.content))
                    image = image.resize((400, 190))
                    photo = ImageTk.PhotoImage(image)
                    cover_label.config(image=photo)
                    cover_label.image = photo
                else:
                    cover_label.config(text=self.strings.get('cover_load_error', 'Kapak yüklenemedi'))
            except:
                cover_label.config(image="", text=self.strings['cover_load_error'])

        
        def update_suggestions(event=None):
            keyword = search_var.get().lower()
            suggestion_box.delete(0, tk.END)
            if keyword and self.game_list:
                filtered = [g for g in self.game_list if keyword in g['name'].lower()]
                for game in filtered[:20]:
                    suggestion_box.insert(tk.END, f"{game['name']} ({game['appid']})")

        def select_suggestion(event=None, close_after=False):
            selection = suggestion_box.curselection()
            if selection:
                selected_text = suggestion_box.get(selection[0])
                if '(' in selected_text and ')' in selected_text:
                    app_id = selected_text.split('(')[-1].replace(')', '')
                    game_name = selected_text.split(' (')[0]
                    self.app_id_var.set(app_id)
                    selected_label.config(text=f"{self.strings['selected_game_label']}{game_name} (ID: {app_id})")
                    self.animate_status_message(self.strings['game_selected_status'].format(game_name=game_name), self.success_button)
                    if close_after:
                        search_window.destroy()
                    else:
                        fetch_and_show_cover(app_id)
                        fetch_and_show_details(app_id)

        
        def fetch_and_show_details(app_id):
            try:
                url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l={self.strings.get('lang_code_steam', 'english')}"
                response = requests.get(url, timeout=10)
                data = response.json()
                if not data[app_id]["success"]:
                    detail_label.config(text=self.strings['details_fetch_error'])
                    return

                app_data = data[app_id]["data"]
                name = app_data.get("name", self.strings['unknown'])
                release = app_data.get("release_date", {}).get("date", self.strings['unknown'])
                publishers = ", ".join(app_data.get("publishers", [])) or self.strings['unknown']
                genres = ", ".join([g['description'] for g in app_data.get("genres", [])]) or self.strings['unknown']
                price = app_data.get("price_overview", {}).get("final_formatted", self.strings['free_or_unknown'])

                text = f"""
{self.strings['detail_name'].format(name=name)}
{self.strings['detail_release'].format(release=release)}
{self.strings['detail_publisher'].format(publishers=publishers)}
{self.strings['detail_genre'].format(genres=genres)}
{self.strings['detail_price'].format(price=price)}
"""
                detail_label.config(text=text.strip())
            except Exception as e:
                detail_label.config(text=self.strings['details_fetch_exception'].format(error=e))



        button_frame = tk.Frame(search_window, bg=self.secondary_bg)
        button_frame.pack(pady=10)

        select_btn = tk.Button(button_frame, text=self.strings['select_btn'], command=lambda: select_suggestion(None, True),
                             bg=self.primary_button, fg=self.text_color, font=("Segoe UI", 10, "bold"),
                             relief=tk.FLAT, padx=20)
        self.add_button_hover_effects(select_btn, self.primary_button, self._get_hover_color(self.primary_button), original_padx=20)
        select_btn.pack(side=tk.LEFT, padx=10)

        close_btn = tk.Button(button_frame, text=self.strings['close_btn'], command=search_window.destroy,
                            bg=self.danger_button, fg=self.text_color, font=("Segoe UI", 10, "bold"),
                            relief=tk.FLAT, padx=20)
        self.add_button_hover_effects(close_btn, self.danger_button, self._get_hover_color(self.danger_button), original_padx=20)
        close_btn.pack(side=tk.LEFT, padx=10)

        search_entry.bind("<KeyRelease>", update_suggestions)
        suggestion_box.bind("<<ListboxSelect>>", select_suggestion)
        search_entry.focus()

    def create_steamdb_button(self, parent):
        self.steamdb_btn = tk.Button(
            parent,
            text=self.strings['open_steamdb_btn'],
            command=lambda: webbrowser.open("https://steamdb.info/"),
            bg=self.info_button,
            fg=self.text_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.steamdb_btn.place(relx=0.85, rely=0.93)
        self.add_button_hover_effects(self.steamdb_btn, self.info_button, self._get_hover_color(self.info_button))

    def create_animated_background(self):
        self.bg_canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.particles = []
        for i in range(20):
            x = (i * 45) % 900
            y = (i * 40) % 800
            particle = self.bg_canvas.create_oval(x, y, x+3, y+3,
                                                fill=self.particle_color,
                                                outline='',
                                                width=0)
            self.particles.append({'id': particle, 'x': x, 'y': y, 'speed': 0.5 + (i % 3) * 0.3})

    def create_steam_path_section(self, parent):
        self.path_frame = tk.Frame(parent, bg=self.secondary_bg, relief=tk.FLAT, bd=0)
        self.path_frame.pack(fill=tk.X, pady=(0, 20))

        border_frame = tk.Frame(self.path_frame, bg=self.primary_button, height=1)
        border_frame.pack(fill=tk.X)

        self.path_inner_frame = tk.Frame(self.path_frame, bg=self.secondary_bg, padx=25, pady=25)
        self.path_inner_frame.pack(fill=tk.BOTH, expand=True)

        self.path_label = tk.Label(self.path_inner_frame, text=self.strings['steam_path_section_title'],
                             font=("Segoe UI", 13, "bold"),
                             fg=self.text_color, bg=self.secondary_bg)
        self.path_label.pack(anchor=tk.W, pady=(0, 15))

        self.path_entry_frame = tk.Frame(self.path_inner_frame, bg=self.secondary_bg)
        self.path_entry_frame.pack(fill=tk.X)

        self.steam_path_var = tk.StringVar()
        self.path_entry = tk.Entry(self.path_entry_frame, textvariable=self.steam_path_var,
                                 font=("Segoe UI", 12),
                                 bg=self.highlight_color, fg=self.text_color,
                                 relief=tk.FLAT, bd=0,
                                 insertbackground=self.entry_insert_color)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12)

        self.browse_btn = tk.Button(self.path_entry_frame, text=self.strings['browse_btn'],
                                  font=("Segoe UI", 10, "bold"),
                                  bg=self.primary_button, fg=self.text_color,
                                  relief=tk.FLAT, bd=0,
                                  command=self.select_steam_folder,
                                  cursor='hand2')
        self.browse_btn.pack(side=tk.RIGHT, padx=(15, 0), ipady=8, ipadx=20)

        self.add_button_hover_effects(self.browse_btn, self.primary_button, self._get_hover_color(self.primary_button))
        self.add_entry_hover_effects(self.path_entry)

    def create_game_id_section(self, parent):
        self.input_frame = tk.Frame(parent, bg=self.secondary_bg, relief=tk.FLAT, bd=0)
        self.input_frame.pack(fill=tk.X, pady=(0, 25))

        border_frame = tk.Frame(self.input_frame, bg=self.success_button, height=1)
        border_frame.pack(fill=tk.X)

        self.inner_frame = tk.Frame(self.input_frame, bg=self.secondary_bg, padx=25, pady=25)
        self.inner_frame.pack(fill=tk.BOTH, expand=True)

        self.id_label = tk.Label(self.inner_frame, text=self.strings['game_id_section_title'],
                          font=("Segoe UI", 13, "bold"),
                          fg=self.text_color, bg=self.secondary_bg)
        self.id_label.pack(anchor=tk.W, pady=(0, 15))

        self.app_id_var = tk.StringVar()
        self.app_id_entry = tk.Entry(self.inner_frame, textvariable=self.app_id_var,
                                    font=("Segoe UI", 16, "bold"),
                                    bg=self.highlight_color, fg=self.text_color,
                                    relief=tk.FLAT, bd=0,
                                    justify=tk.CENTER,
                                    insertbackground=self.entry_insert_color)
        self.app_id_entry.pack(fill=tk.X, ipady=15)

        self.add_entry_hover_effects(self.app_id_entry)
        self.app_id_entry.bind('<KeyRelease>', self.validate_input_visual)

    def create_button_section(self, parent):
        button_frame = tk.Frame(parent, bg=self.bg_color)
        button_frame.pack(pady=(0, 25))

        self.download_process_btn = tk.Button(
            button_frame,
            text=self.strings['download_install_btn'],
            command=self.download_and_process,
            bg=self.success_button,
            fg=self.text_color,
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=35,
            pady=15,
            cursor='hand2'
        )
        self.download_process_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.remove_btn = tk.Button(
            button_frame,
            text=self.strings['remove_game_btn'],
            command=self.remove_game_from_entry,
            bg=self.danger_button,
            fg=self.text_color,
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=35,
            pady=15,
            cursor='hand2'
        )
        self.remove_btn.pack(side=tk.LEFT, padx=(15, 15))

        self.restart_btn = tk.Button(
            button_frame,
            text=self.strings['restart_steam_btn'],
            command=self.restart_steam,
            bg=self.primary_button,
            fg=self.text_color,
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=35,
            pady=15,
            cursor='hand2'
        )
        self.restart_btn.pack(side=tk.LEFT, padx=(15, 0))

        self.add_button_hover_effects(self.download_process_btn, self.success_button, self._get_hover_color(self.success_button), original_padx=35, original_pady=15)
        self.add_button_hover_effects(self.remove_btn, self.danger_button, self._get_hover_color(self.danger_button), original_padx=35, original_pady=15)
        self.add_button_hover_effects(self.restart_btn, self.primary_button, self._get_hover_color(self.primary_button), original_padx=35, original_pady=15)

    def create_status_section(self, parent):
        status_frame = tk.Frame(parent, bg=self.bg_color)
        status_frame.pack(fill=tk.X, pady=(0, 20))

        self.status_container = tk.Frame(status_frame, bg=self.secondary_bg, relief=tk.FLAT, bd=0)
        self.status_container.pack(fill=tk.X)

        self.status_label = tk.Label(self.status_container, text=self.strings['initial_status'],
                                    font=("Segoe UI", 11, "bold"),
                                    fg=self.primary_button, bg=self.secondary_bg)
        self.status_label.pack(pady=15)

        progress_frame = tk.Frame(parent, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar",
                       background=self.primary_button,
                       troughcolor=self.secondary_bg,
                       borderwidth=0,
                       lightcolor=self.primary_button,
                       darkcolor=self.primary_button,
                       thickness=8)

        self.progress = ttk.Progressbar(progress_frame,
                                       style="Custom.Horizontal.TProgressbar",
                                       mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(5, 0))
        self.progress.pack_forget()

    def create_footer(self, parent):
        footer_frame = tk.Frame(parent, bg=self.bg_color)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(25, 0))

        self.footer_label = tk.Label(footer_frame, text=self.strings['footer_text'],
                              font=("Segoe UI", 9, "italic"),
                              fg='#666666', bg=self.bg_color)
        self.footer_label.pack(side=tk.RIGHT)

    def add_button_hover_effects(self, button, normal_color, hover_color, original_padx=None, original_pady=None):
        def _to_number(value):
            if isinstance(value, (int, float)):
                return value
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0

        if original_padx is None:
            original_padx = _to_number(button.cget('padx'))
        else:
            original_padx = _to_number(original_padx)

        if original_pady is None:
            original_pady = _to_number(button.cget('pady'))
        else:
            original_pady = _to_number(original_pady)

        def on_enter(e):
            button.configure(bg=hover_color)
            new_padx = math.ceil(original_padx * 1.05)
            new_pady = math.ceil(original_pady * 1.05)
            button.configure(padx=new_padx, pady=new_pady)

        def on_leave(e):
            button.configure(bg=normal_color)
            button.configure(padx=original_padx, pady=original_pady)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def add_entry_hover_effects(self, entry):
        def on_focus_in(e):
            entry.configure(bg=self._get_hover_color(self.highlight_color))

        def on_focus_out(e):
            entry.configure(bg=self.highlight_color)

        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    def animate_button_scale(self, button, scale):
        pass

    def validate_input_visual(self, event):
        app_id = self.app_id_var.get().strip()
        if app_id and app_id.isdigit():
            self.app_id_entry.configure(bg=self._get_hover_color(self.success_button))
        elif app_id:
            self.app_id_entry.configure(bg=self._get_hover_color(self.danger_button))
        else:
            self.app_id_entry.configure(bg=self.highlight_color)

    def start_animations(self):
        self.animate_particles()
        self.animate_title_glow()

    def animate_particles(self):
        for particle in self.particles:
            particle['y'] += particle['speed']

            if particle['y'] > 800:
                particle['y'] = -10
                particle['x'] = (particle['x'] + 50) % 900

            self.bg_canvas.coords(particle['id'],
                                particle['x'], particle['y'],
                                particle['x']+3, particle['y']+3)
            self.bg_canvas.itemconfig(particle['id'], fill=self.particle_color)


        self.root.after(50, self.animate_particles)

    def animate_title_glow(self):
        colors = self.title_glow_colors
        color_index = int(time.time() * 2) % len(colors)
        self.title_label.configure(fg=colors[color_index])
        self.root.after(500, self.animate_title_glow)

    def entrance_animation(self):
        alpha = self.root.attributes('-alpha')
        if alpha < 1.0:
            self.root.attributes('-alpha', alpha + 0.03)
            self.root.after(20, self.entrance_animation)

    def validate_app_id(self, app_id):
        if not app_id:
            return False, self.strings['appid_empty_error']

        try:
            int(app_id)
            if len(app_id) < 1:
                return False, self.strings['appid_invalid_error']
            return True, ""
        except ValueError:
            return False, self.strings['appid_numeric_error']

    def generate_url(self, app_id):
        return "https://codeload.github.com/SteamAutoCracks/ManifestHub/zip/refs/heads/" + app_id

    def show_progress(self):
        self.progress.pack(fill=tk.X, pady=(10, 0))
        self.progress.start(15)
        self.download_process_btn.configure(state='disabled', text=self.strings['processing_status'])
        self.remove_btn.configure(state='disabled')
        self.restart_btn.configure(state='disabled')
        self.browse_btn.configure(state='disabled')
        self.search_btn.configure(state='disabled')
        self.hid_btn.configure(state='disabled')
        self.hid_remove_btn.configure(state='disabled')
        self.steamdb_btn.configure(state='disabled')
        self.sss_btn.configure(state='disabled')
        self.zip_btn.configure(state='disabled')
        self.installed_games_btn.configure(state='disabled')
        self.about_btn.configure(state='disabled')
        self.online_fix_btn.configure(state='disabled')


    def hide_progress(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.download_process_btn.configure(state='normal', text=self.strings['download_install_btn'])
        self.remove_btn.configure(state='normal')
        self.restart_btn.configure(state='normal')
        self.browse_btn.configure(state='normal')
        self.search_btn.configure(state='normal')
        self.hid_btn.configure(state='normal')
        self.hid_remove_btn.configure(state='normal')
        self.steamdb_btn.configure(state='normal')
        self.sss_btn.configure(state='normal')
        self.zip_btn.configure(state='normal')
        self.installed_games_btn.configure(state='normal')
        self.about_btn.configure(state='normal')
        self.online_fix_btn.configure(state='normal')


    def select_steam_folder(self):
        folder = filedialog.askdirectory(title=self.strings['select_steam_folder_title'])
        if folder:
            self.steam_path_var.set(folder)
            self.animate_status_message(self.strings['steam_path_selected'], self.success_button)

    def download_and_process(self):
        app_id = self.app_id_var.get().strip()
        steam_path = self.steam_path_var.get().strip()

        is_valid, error_message = self.validate_app_id(app_id)
        if not is_valid:
            self.show_error_message(error_message)
            return

        if not steam_path:
            self.show_error_message(self.strings['select_steam_folder_prompt'])
            return

        threading.Thread(target=self._download_and_process_thread, args=(app_id, steam_path), daemon=True).start()

    def _download_and_process_thread(self, app_id, steam_path):
        url = self.generate_url(app_id)

        try:
            self.root.after(0, lambda: self.animate_status_message(self.strings['downloading_manifests_status'], self.primary_button))
            self.root.after(0, self.show_progress)

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            temp_zip = f"{app_id}.zip"
            with open(temp_zip, 'wb') as f:
                f.write(response.content)

            self.root.after(0, lambda: self.animate_status_message(self.strings['installing_to_steam_status'], self.primary_button))

            success, message = self.process_zip(temp_zip, steam_path, app_id)

            try:
                os.remove(temp_zip)
            except:
                pass

            self.root.after(0, self.hide_progress)

            if success:
                self.root.after(0, lambda: self.animate_status_message(
                    self.strings['game_crack_success_status'].format(app_id=app_id), self.success_button))
                self.root.after(0, lambda: messagebox.showinfo(self.strings['success'], message))
            else:
                self.root.after(0, lambda: self.animate_status_message(self.strings['install_fail_status'], self.danger_button))
                self.root.after(0, lambda: messagebox.showerror(self.strings['error'], message))

        except requests.exceptions.RequestException as e:
            self.root.after(0, self.hide_progress)
            self.root.after(0, lambda: self.animate_status_message(self.strings['download_fail_status'], self.danger_button))
            self.root.after(0, lambda: messagebox.showerror(self.strings['download_error_title'], self.strings['download_error_msg'].format(error=str(e))))
        except Exception as e:
            self.root.after(0, self.hide_progress)
            self.root.after(0, lambda: self.animate_status_message(self.strings['unexpected_error_status'], self.danger_button))
            self.root.after(0, lambda: messagebox.showerror(self.strings['error'], self.strings['unexpected_error_msg'].format(error=str(e))))

    def process_zip(self, zip_path, steam_path, app_id=None):
        try:
            stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
            depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
            os.makedirs(stplugin_dir, exist_ok=True)
            os.makedirs(depotcache_dir, exist_ok=True)

            game_id = os.path.splitext(os.path.basename(zip_path))[0]
            if not game_id.isdigit():
                return False, self.strings['zip_name_error']

            api_url = f'https://store.steampowered.com/api/appdetails?appids={game_id}'
            game_name = self.strings['game_id_prefix'].format(game_id=game_id)
            dlc_ids = []
            try:
                response = requests.get(api_url, timeout=5)
                data = response.json()
                if data and game_id in data and data[game_id].get('success'):
                    game_data = data[game_id]['data']
                    game_name = game_data.get('name', game_name)
                    if 'dlc' in game_data and isinstance(game_data['dlc'], list):
                        dlc_ids = game_data['dlc']
                    else:
                        dlc_ids = []
                if not isinstance(dlc_ids, list):
                    dlc_ids = []
            except Exception:
                dlc_ids = []

            lua_count = 0
            manifest_count = 0
            installed_lua_files = []
            installed_manifest_files = []

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.lower().endswith('.lua'):
                        dest_name = os.path.basename(file)
                        target = os.path.join(stplugin_dir, dest_name)
                        with zip_ref.open(file) as src, open(target, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
                        lua_count += 1
                        installed_lua_files.append(dest_name)
                    elif file.lower().endswith('.manifest'):
                        dest_name = os.path.basename(file)
                        target = os.path.join(depotcache_dir, dest_name)
                        with zip_ref.open(file) as src, open(target, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
                        manifest_count += 1
                        installed_manifest_files.append(dest_name)

            marcellus_path = os.path.join(stplugin_dir, 'marcellus.lua')
            existing_lines = []
            if os.path.exists(marcellus_path):
                with open(marcellus_path, 'r', encoding='utf-8') as f:
                    existing_lines = f.readlines()

            new_count = 0
            with open(marcellus_path, 'a', encoding='utf-8') as f:
                for dlc_id in dlc_ids:
                    add_line = f'addappid({dlc_id}, 1)\n'
                    if add_line not in existing_lines:
                        f.write(add_line)
                        new_count += 1

            if app_id:
                self.add_installed_game(app_id, game_name, installed_lua_files, installed_manifest_files)

            success_msg = f"""{self.strings['game_crack_success_msgbox_title']}

{self.strings['crack_stats']}
{self.strings['lua_processed'].format(count=lua_count)}
{self.strings['manifest_installed'].format(count=manifest_count)}
{self.strings['dlc_added'].format(count=new_count)}

{self.strings['restart_steam_prompt']}"""

            return True, success_msg

        except Exception as e:
            return False, self.strings['processing_error'].format(error=str(e))

    def remove_game_from_entry(self):
        app_id = self.app_id_var.get().strip()
        self.remove_game(app_id)

    def remove_game(self, app_id):
        steam_path = self.steam_path_var.get().strip()

        is_valid, error_message = self.validate_app_id(app_id)
        if not is_valid:
            self.show_error_message(error_message)
            return

        if not steam_path:
            self.show_error_message(self.strings['select_steam_folder_prompt'])
            return

        if not messagebox.askyesno(self.strings['confirmation_title'], self.strings['remove_game_confirm'].format(app_id=app_id)):
            return

        threading.Thread(target=self._remove_game_thread, args=(app_id,), daemon=True).start()

    def _remove_game_thread(self, app_id):
        steam_path = self.steam_path_var.get().strip()
        try:
            self.root.after(0, lambda: self.animate_status_message(self.strings['removing_game_status'].format(app_id=app_id), self.danger_button))
            self.root.after(0, self.show_progress)

            stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
            depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')

            lua_files_removed = 0
            manifest_files_removed = 0

            installed_entry = self.load_installed_games().get(app_id)
            stored_luas = []
            stored_manifests = []
            if isinstance(installed_entry, dict):
                stored_luas = installed_entry.get('lua_files', []) or []
                stored_manifests = installed_entry.get('manifest_files', []) or []

            if stored_luas:
                for filename in stored_luas:
                    file_path = os.path.join(stplugin_dir, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        lua_files_removed += 1
            elif os.path.isdir(stplugin_dir):
                for filename in os.listdir(stplugin_dir):
                    if filename.startswith(app_id) and filename.lower().endswith('.lua'):
                        os.remove(os.path.join(stplugin_dir, filename))
                        lua_files_removed += 1

            if stored_manifests:
                for filename in stored_manifests:
                    file_path = os.path.join(depotcache_dir, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        manifest_files_removed += 1
            elif os.path.isdir(depotcache_dir):
                for filename in os.listdir(depotcache_dir):
                    if filename.startswith(app_id) and filename.lower().endswith('.manifest'):
                        os.remove(os.path.join(depotcache_dir, filename))
                        manifest_files_removed += 1

            marcellus_path = os.path.join(stplugin_dir, 'marcellus.lua')
            if os.path.exists(marcellus_path):
                with open(marcellus_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                dlc_ids = self.get_dlc_ids(app_id)
                new_lines = [line for line in lines if not any(f'addappid({dlc_id},' in line for dlc_id in dlc_ids)]

                with open(marcellus_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)

            self.remove_installed_game_entry(app_id)
            
            self.root.after(0, self.hide_progress)
            self.root.after(0, lambda: messagebox.showinfo(self.strings['success'], self.strings['remove_game_success_msgbox'].format(app_id=app_id, lua_files=lua_files_removed, manifest_files=manifest_files_removed)))
            self.root.after(0, lambda: self.animate_status_message(self.strings['remove_game_success_status'].format(app_id=app_id), self.success_button))
            self.root.after(0, self.populate_installed_games_list)

        except Exception as e:
            self.root.after(0, self.hide_progress)
            self.root.after(0, lambda: self.show_error_message(self.strings['remove_game_error'].format(error=str(e))))

    def get_dlc_ids(self, app_id):
        api_url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
        try:
            response = requests.get(api_url, timeout=5)
            data = response.json()
            dlc_ids = data.get(app_id, {}).get('data', {}).get('dlc', [])
            return dlc_ids if isinstance(dlc_ids, list) else []
        except Exception:
            return []

    def restart_steam(self):
        steam_path = self.steam_path_var.get().strip()
        if not steam_path:
            self.show_error_message(self.strings['select_steam_folder_prompt'])
            return

        steam_exe = os.path.join(steam_path, 'steam.exe')
        if not os.path.isfile(steam_exe):
            self.show_error_message(self.strings['steam_exe_not_found'])
            return

        try:
            subprocess.run(['taskkill', '/F', '/IM', 'steam.exe'])
            subprocess.Popen([steam_exe])
            messagebox.showinfo(self.strings['success'], self.strings['steam_restart_success_msgbox'])
            self.animate_status_message(self.strings['steam_restart_success_status'], self.success_button)
        except Exception as e:
            self.show_error_message(self.strings['steam_restart_error'].format(error=str(e)))

    def animate_status_message(self, message, color):
        self.status_label.configure(text=message, fg=color)

    def pulse_status_message(self):
        try:
            current_font = self.status_label.cget('font')
            if isinstance(current_font, str):
                font_parts = current_font.split()
                size = int(font_parts[1]) if len(font_parts) > 1 else 11
            else:
                size = 11

            if self.pulse_direction == 1:
                size += 1
                if size >= 13:
                    self.pulse_direction = -1
            else:
                size -= 1
                if size <= 11:
                    self.pulse_direction = 1

            self.status_label.configure(font=("Segoe UI", size, "bold"))
            self.root.after(100, self.pulse_status_message)
        except Exception as e:
            print(self.strings['font_animation_error'].format(error=str(e)))
            self.status_label.configure(font=("Segoe UI", 11, "bold"))

    def show_error_message(self, message):
        self.animate_status_message(f"❌ {message}", self.danger_button)
        messagebox.showerror(self.strings['error'], message)

    def show_success_message(self, message):
        self.animate_status_message(f"✅ {message}", self.success_button)

    # --- Online Fix (entegre Tkinter penceresi) ---
    def create_online_fix_button(self, parent):
        self.online_fix_btn = tk.Button(
            parent,
            text=self.strings['online_fix_btn'],
            command=self.open_online_fix_window,
            bg=self.info_button,
            fg=self.text_color,
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.online_fix_btn.place(relx=0.37, rely=0.95)
        self.add_button_hover_effects(self.online_fix_btn, self.info_button, self._get_hover_color(self.info_button))

    def open_online_fix_window(self):
        OnlineFixDownloaderWindow(self)
    # --- Online Fix sonu ---


def main():
    try:
        if TKDND_AVAILABLE and hasattr(TkinterDnD, 'Tk'):
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()

        root.withdraw()

        try:
            root.attributes('-alpha', 0.0)
        except Exception:
            pass
        root.deiconify()
        root.lift()
        show_version_check(root)
        root.withdraw()
        try:
            root.attributes('-alpha', 1.0)
        except Exception:
            pass

        legal_window = tk.Toplevel(root)
        legal = LegalNotice(legal_window)
        legal_window.wait_window(legal_window)
        
        
        if not hasattr(legal, 'var') or legal.var.get() != 1:
            root.destroy()
            return
        
        
        selected_language = legal.selected_lang
        lang_strings = LANGUAGES.get(selected_language, LANGUAGES['tr'])

        system32_path = os.path.join(os.environ['SystemRoot'], 'System32')
        if system32_path not in os.environ['PATH']:
            os.environ['PATH'] = system32_path + ';' + os.environ['PATH']

        app = SteamManifestTool(root, lang_code=selected_language)

        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        root.deiconify()
        root.lift()

        show_preflight_notice(root, lang_strings)

        root.mainloop()

    except Exception as e:
        error_root = tk.Tk()
        error_root.withdraw()
        
        lang = LANGUAGES.get('tr', LANGUAGES['en']) 
        messagebox.showerror(lang['critical_error_title'], lang['app_start_error'].format(error=str(e)), parent=error_root)
        error_root.destroy()
        raise


if __name__ == "__main__":
    main()
