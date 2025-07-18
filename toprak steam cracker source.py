import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from io import BytesIO
import requests
import os
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

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    class TkinterDnD:
        pass
    DND_FILES = None

class LegalNotice:
    def __init__(self, root):
        self.root = root
        self.root.title("Yasal Uyarı")
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

        main_frame = tk.Frame(root, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(side=tk.BOTTOM, pady=(20, 0))

        self.var = tk.IntVar()
        checkbox = tk.Checkbutton(main_frame, text="Yukarıdaki uyarıyı okudum ve kabul ediyorum",
                                variable=self.var, font=("Segoe UI", 11),
                                bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color,
                                activebackground=self.bg_color, activeforeground=self.text_color,
                                highlightthickness=0)
        checkbox.pack(side=tk.BOTTOM, pady=(10, 0))

        continue_btn = tk.Button(button_frame, text="Devam Et", command=self.check_acceptance,
                               font=("Segoe UI", 12, "bold"), bg=self.primary_button, fg=self.text_color,
                               relief=tk.FLAT, padx=30, pady=10)
        continue_btn.pack(side=tk.LEFT, padx=10)

        exit_btn = tk.Button(button_frame, text="Çıkış", command=self.root.quit,
                           font=("Segoe UI", 12, "bold"), bg=self.danger_button, fg=self.text_color,
                           relief=tk.FLAT, padx=30, pady=10)
        exit_btn.pack(side=tk.LEFT, padx=10)

        title_label = tk.Label(main_frame, text="⚠️ YASAL UYARI",
                             font=("Segoe UI", 20, "bold"),
                             fg='#ffcc00', bg=self.bg_color)
        title_label.pack(side=tk.TOP, pady=(0, 20))

        text_frame = tk.Frame(main_frame, bg='#1a1a1a')
        text_frame.pack(fill=tk.BOTH, expand=True)

        text = """📌 Yasal Uyarı ve Sorumluluk Reddi

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
Lütfen bu yazılımı yalnızca **etik ve yasal sınırlar içinde** kullanınız.
"""

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Segoe UI", 11),
                            bg='#1a1a1a', fg=self.text_color, padx=20, pady=20,
                            borderwidth=0, highlightthickness=0)
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

    def check_acceptance(self):
        if self.var.get() == 1:
            self.root.destroy()
        else:
            messagebox.showwarning("Uyarı", "Devam etmek için kutuyu işaretlemeniz gerekmektedir!")

class SteamManifestTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Toprak Steam Cracker & Manifest Oluşturucu")
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

        self.title_label = tk.Label(title_frame, text="💀 TOPRAK STEAM CRACKER",
                              font=("Segoe UI", 24, "bold"),
                              fg=self.text_color, bg=self.bg_color)
        self.title_label.pack()

        self.subtitle_label = tk.Label(title_frame, text="⚡ MANIFEST OLUŞTURUCU & STEAM ENTEGRASYONU ⚡",
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

    def apply_theme(self, initial_setup=False):

        self.root.configure(bg=self.bg_color)
        if hasattr(self, 'bg_canvas'):
             self.bg_canvas.configure(bg=self.bg_color)

        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) or isinstance(widget, tk.Label):
                try:
                    widget_bg = widget.cget('bg')
                    if widget_bg == '#0a0a0a' or widget_bg == '#f0f0f0':
                        widget.config(bg=self.bg_color)
                except tk.TclError:
                    pass

        if hasattr(self, 'title_label'):
            self.title_label.config(bg=self.bg_color, fg=self.text_color)
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.config(bg=self.bg_color, fg=self.primary_button)
        if hasattr(self, 'separator'):
            self.separator.config(bg=self.primary_button)

        if hasattr(self, 'path_frame'): self.path_frame.config(bg=self.secondary_bg)
        if hasattr(self, 'path_inner_frame'): self.path_inner_frame.config(bg=self.secondary_bg)
        if hasattr(self, 'path_entry_frame'): self.path_entry_frame.config(bg=self.secondary_bg)
        if hasattr(self, 'path_label'): self.path_label.config(bg=self.secondary_bg, fg=self.text_color)
        if hasattr(self, 'path_entry'): self.path_entry.config(bg=self.highlight_color, fg=self.text_color, insertbackground=self.entry_insert_color)
        if hasattr(self, 'browse_btn'): self.browse_btn.config(bg=self.primary_button, fg=self.text_color)
            
        if hasattr(self, 'input_frame'): self.input_frame.config(bg=self.secondary_bg)
        if hasattr(self, 'inner_frame'): self.inner_frame.config(bg=self.secondary_bg)
        if hasattr(self, 'id_label'): self.id_label.config(bg=self.secondary_bg, fg=self.text_color)
        if hasattr(self, 'app_id_entry'): self.app_id_entry.config(bg=self.highlight_color, fg=self.text_color, insertbackground=self.entry_insert_color)

        if hasattr(self, 'drag_frame'): self.drag_frame.config(bg=self.secondary_bg)
        if hasattr(self, 'drop_area'): self.drop_area.config(bg=self.highlight_color, fg=self.text_color)

        if hasattr(self, 'download_process_btn'): self.download_process_btn.config(bg=self.success_button, fg=self.text_color)
        if hasattr(self, 'remove_btn'): self.remove_btn.config(bg=self.danger_button, fg=self.text_color)
        if hasattr(self, 'restart_btn'): self.restart_btn.config(bg=self.primary_button, fg=self.text_color)

        if hasattr(self, 'status_container'): self.status_container.config(bg=self.secondary_bg)
        if hasattr(self, 'status_label'): self.status_label.config(bg=self.secondary_bg, fg=self.primary_button)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar",
                       background=self.primary_button,
                       troughcolor=self.secondary_bg,
                       borderwidth=0,
                       lightcolor=self.primary_button,
                       darkcolor=self.primary_button,
                       thickness=8)

        if hasattr(self, 'footer_label'): self.footer_label.config(bg=self.bg_color, fg='#666666')

        if not initial_setup:
            self.add_button_hover_effects(self.browse_btn, self.primary_button, self._get_hover_color(self.primary_button))
            self.add_button_hover_effects(self.download_process_btn, self.success_button, self._get_hover_color(self.success_button))
            self.add_button_hover_effects(self.remove_btn, self.danger_button, self._get_hover_color(self.danger_button))
            self.add_button_hover_effects(self.restart_btn, self.primary_button, self._get_hover_color(self.primary_button))
            self.add_button_hover_effects(self.search_btn, self.info_button, self._get_hover_color(self.info_button))
            self.add_button_hover_effects(self.hid_btn, self.info_button, self._get_hover_color(self.info_button))
            self.add_button_hover_effects(self.hid_remove_btn, self.danger_button, self._get_hover_color(self.danger_button))
            self.add_button_hover_effects(self.steamdb_btn, self.info_button, self._get_hover_color(self.info_button))
            self.add_button_hover_effects(self.sss_btn, self.info_button, self._get_hover_color(self.info_button))
            self.add_button_hover_effects(self.zip_btn, self.info_button, self._get_hover_color(self.info_button))
            self.add_button_hover_effects(self.installed_games_btn, self.info_button, self._get_hover_color(self.info_button))
            self.add_button_hover_effects(self.about_btn, self.info_button, self._get_hover_color(self.info_button))


        if hasattr(self, 'particles'):
            for particle in self.particles:
                self.bg_canvas.itemconfig(particle['id'], fill=self.particle_color)

    def _get_hover_color(self, base_hex_color):
        base_hex = base_hex_color.lstrip('#')
        rgb = tuple(int(base_hex[i:i+2], 16) for i in (0, 2, 4))
        
        hover_rgb = tuple(min(255, c + 30) for c in rgb)
        
        return '#%02x%02x%02x' % hover_rgb

    def create_about_button(self, parent):
        self.about_btn = tk.Button(
            parent,
            text="ℹ️ Hakkında",
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
        about_window.title("Hakkında")
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
        tk.Label(about_window, text="Sürüm: 1.0.0",
                 font=("Segoe UI", 10), fg=self.text_color, bg=self.bg_color).pack(pady=2)
        tk.Label(about_window, text="Geliştirici: Toprak",
                 font=("Segoe UI", 10), fg=self.text_color, bg=self.bg_color).pack(pady=2)

        tk.Label(about_window, text="Bu yazılım eğitimsel ve deneysel amaçlı geliştirilmiştir.",
                 font=("Segoe UI", 10, "italic"), fg=self.text_color, bg=self.bg_color, wraplength=400).pack(pady=10)

        github_label = tk.Label(about_window, text="GitHub Deposu (ManifestHub)",
                                font=("Segoe UI", 10, "underline"), fg=self.primary_button, bg=self.bg_color, cursor="hand2")
        github_label.pack(pady=5)
        github_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/SteamAutoCracks/ManifestHub"))

        message_label = tk.Label(about_window, text="""
Bu yazılım herhangi bir ticari amaç taşımamaktadır.
Lütfen etik ve yasal sınırlar içinde kullanınız.
""",
                 font=("Segoe UI", 9), fg=self.text_color, bg=self.bg_color, wraplength=400, justify=tk.CENTER)
        message_label.pack(pady=10)

        close_btn = tk.Button(about_window, text="Kapat", command=about_window.destroy,
                              bg=self.accent_color, fg=self.text_color, font=("Segoe UI", 10, "bold"),
                              relief=tk.FLAT, padx=20, pady=8)
        self.add_button_hover_effects(close_btn, self.accent_color, self._get_hover_color(self.accent_color), original_padx=20, original_pady=8)
        close_btn.pack(pady=10)


    def create_show_installed_games_button(self, parent):
        self.installed_games_btn = tk.Button(
            parent,
            text="🎮 Yüklü Oyunlar",
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
            json.dump(games, f, indent=4)

    def add_installed_game(self, app_id, game_name):
        installed_games = self.load_installed_games()
        installed_games[app_id] = game_name
        self.save_installed_games(installed_games)

    def remove_installed_game_entry(self, app_id):
        installed_games = self.load_installed_games()
        if app_id in installed_games:
            del installed_games[app_id]
            self.save_installed_games(installed_games)

    def show_installed_games(self):
        installed_games_window = tk.Toplevel(self.root)
        installed_games_window.title("Yüklü Oyunlar")
        installed_games_window.geometry("600x500")
        installed_games_window.configure(bg=self.secondary_bg)
        installed_games_window.resizable(False, False)

        tk.Label(installed_games_window, text="🎮 Yüklü Oyunlar", font=("Segoe UI", 16, "bold"),
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
        
        close_btn = tk.Button(button_frame, text="Kapat", command=installed_games_window.destroy,
                            bg=self.primary_button, fg=self.text_color, font=("Segoe UI", 10, "bold"),
                            relief=tk.FLAT, padx=20)
        self.add_button_hover_effects(close_btn, self.primary_button, self._get_hover_color(self.primary_button), original_padx=20)
        close_btn.pack(side=tk.LEFT, padx=10)

    def populate_installed_games_list(self):
        self.installed_games_listbox.delete(0, tk.END)
        installed_games = self.load_installed_games()
        if not installed_games:
            self.installed_games_listbox.insert(tk.END, "Yüklü oyun bulunmuyor.")
            return

        for app_id, game_name in installed_games.items():
            self.installed_games_listbox.insert(tk.END, f"{game_name} (ID: {app_id})")

    def on_installed_game_select(self, event):
        selection = self.installed_games_listbox.curselection()
        if not selection:
            return

        selected_text = self.installed_games_listbox.get(selection[0])
        if '(' in selected_text and ')' in selected_text:
            app_id = selected_text.split('(')[-1].replace(')', '').replace('ID: ', '')
            self.app_id_var.set(app_id)
            game_name = selected_text.split(' (')[0]
            self.animate_status_message(f"🎮 OYUN SEÇİLDİ: {game_name}", self.success_button)

    def remove_hid_dll(self):
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'steam.exe'])
            time.sleep(2)

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                dll_path = os.path.join(steam_path, "hid.dll")

                if os.path.exists(dll_path):
                    os.remove(dll_path)
                    messagebox.showinfo("Başarılı", "hid.dll başarıyla kaldırıldı!\nSteam'i yeniden başlatabilirsiniz.")
                    self.animate_status_message("✅ HID.dll BAŞARIYLA KALDIRILDI", self.success_button)
                else:
                    messagebox.showinfo("Bilgi", "hid.dll dosyası bulunamadı!")
                    self.animate_status_message("ℹ️ HID.dll BULUNAMADI", self.primary_button)
        except Exception as e:
            messagebox.showerror("Hata", f"hid.dll kaldırılırken hata oluştu:\n{str(e)}")
            self.animate_status_message("❌ HID.dll KALDIRILAMADI", self.danger_button)

    def create_hid_remove_button(self, parent):
        self.hid_remove_btn = tk.Button(
            parent,
            text="🗑️ HID.dll Kaldır",
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
            text="📦 Manuel Olarak Zip Yükle",
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
            self.show_error_message("Lütfen önce Steam kurulum klasörünü seçin!")
            return

        file_path = filedialog.askopenfilename(
            title="ZIP Dosyası Seçin",
            filetypes=[("ZIP Dosyaları", "*.zip"), ("Tüm Dosyalar", "*.*")]
        )

        if not file_path:
            return

        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                valid_files = [f for f in zip_ref.namelist() if f.lower().endswith(('.manifest', '.lua'))]

                if not valid_files:
                    self.show_error_message("ZIP dosyasında .manifest veya .lua dosyası bulunamadı!")
                    return

                self.process_zip_files(zip_ref, steam_path)

        except Exception as e:
            self.show_error_message(f"ZIP dosyası işlenirken hata oluştu:\n{str(e)}")

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

        messagebox.showinfo("✅ BAŞARILI",
            f"🎉 {lua_count} LUA ve {manifest_count} manifest dosyası eklendi!\n\n"
            "🚀 Oyununuzu oynamak için Steam'i yeniden başlatın!")
        self.animate_status_message(f"📦 ZIP'DEN {lua_count + manifest_count} DOSYA EKLENDİ", self.success_button)

    def auto_detect_steam_path(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                if os.path.exists(steam_path):
                    self.steam_path_var.set(steam_path)
                    self.animate_status_message("✅ STEAM KONUMU OTOMATİK BULUNDU", self.success_button)
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
                self.animate_status_message("✅ STEAM KONUMU OTOMATİK BULUNDU", self.success_button)
                return

        self.animate_status_message("⚠️ STEAM KONUMU OTOMATİK BULUNAMADI", self.primary_button)

    def create_sss_button(self, parent):
        self.sss_btn = tk.Button(
            parent,
            text="❓ SSS",
            command=lambda: webbrowser.open("https://rentry.co/topraksteamcrackerSSS"),
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

        drag_label = tk.Label(inner_frame, text="📂 MANUEL DOSYA EKLEME (Sürükle & Bırak)",
                            font=("Segoe UI", 13, "bold"),
                            fg=self.text_color, bg=self.secondary_bg)
        drag_label.pack(anchor=tk.W, pady=(0, 15))

        self.drop_area = tk.Label(inner_frame, text="Manifest ve Lua dosyalarını buraya sürükle & bırak\n(.manifest, .lua)",
                                font=("Segoe UI", 11),
                                bg=self.highlight_color, fg=self.text_color,
                                relief=tk.RAISED, bd=2,
                                padx=50, pady=40)
        self.drop_area.pack(fill=tk.BOTH, expand=True)

        if hasattr(self.drop_area, 'drop_target_register'):
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
        else:
            self.drop_area.config(text="Sürükle-bırak desteklenmiyor\n(tkinterdnd2 kurulu değil)")

        self.drop_area.bind('<Enter>', lambda e: self.drop_area.config(bg=self._get_hover_color(self.highlight_color)))
        self.drop_area.bind('<Leave>', lambda e: self.drop_area.config(bg=self.highlight_color))

    def on_drop(self, event):
        steam_path = self.steam_path_var.get().strip()
        if not steam_path:
            self.show_error_message("Lütfen önce Steam kurulum klasörünü seçin!")
            return

        files = []
        if isinstance(event.data, str):
            files = [f.strip('{}') for f in event.data.split('} {')]
        elif isinstance(event.data, list):
            files = event.data
        else:
            self.show_error_message("Desteklenmeyen dosya bırakma formatı!")
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
            self.show_error_message("Sadece .manifest veya .lua dosyaları kabul edilir!")
            return

        try:
            stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
            depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
            os.makedirs(stplugin_dir, exist_ok=True)
            os.makedirs(depotcache_dir, exist_ok=True)

            lua_count = 0
            manifest_count = 0

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

            messagebox.showinfo("✅ BAŞARILI",
                f"🎉 {lua_count} LUA ve {manifest_count} manifest dosyası eklendi!\n\n"
                "🚀 Oyununuzu oynamak için Steam'i yeniden başlatın!")
            self.animate_status_message(f"📂 {lua_count + manifest_count} DOSYA EKLENDİ", self.success_button)

        except Exception as e:
            self.show_error_message(f"Dosyalar işlenirken hata oluştu:\n{str(e)}")

    def download_hid_dll(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
        except Exception:
            steam_path = None

        save_path = os.path.join(steam_path, "hid.dll") if steam_path else os.path.join(os.path.expanduser("~"), "Desktop", "hid.dll")

        if not steam_path:
            messagebox.showwarning("Uyarı", "Steam kurulum yolu bulunamadı. Dosya masaüstüne kaydedilecek.")

        try:
            url = "https://raw.githubusercontent.com/toprak1224/hid.dll/main/hid.dll "
            urllib.request.urlretrieve(url, save_path)
            messagebox.showinfo("Başarılı", f"DLL başarıyla indirildi!\nKaydedilen konum: {save_path}")
            self.animate_status_message("✅ HID.dll BAŞARIYLA İNDİRİLDİ", self.success_button)
        except Exception as e:
            messagebox.showerror("Hata", f"DLL indirilirken hata oluştu:\n{str(e)}")
            self.animate_status_message("❌ HID.dll İNDİRİLEMEDİ", self.danger_button)

    def create_hid_download_button(self, parent):
        self.hid_btn = tk.Button(
            parent,
            text="💾 HID.dll İndir",
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
            text="🔍 Oyun Ara",
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
            url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
            response = requests.get(url, timeout=30)
            data = response.json()
            self.game_list = data.get("applist", {}).get("apps", [])
        except Exception as e:
            print(f"Oyun listesi alınamadı: {str(e)}")

    def show_game_search(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Steam Oyun Arama")
        search_window.geometry("800x800")
        search_window.configure(bg=self.secondary_bg)
        search_window.resizable(False, False)

        tk.Label(search_window, text="🎮 Steam Oyun Ara", font=("Segoe UI", 16, "bold"),
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


        selected_label = tk.Label(search_window, text="Seçilen Oyun: ", font=("Segoe UI", 11),
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
                image = Image.open(BytesIO(response.content))
                image = image.resize((400, 190))
                photo = ImageTk.PhotoImage(image)
                cover_label.config(image=photo)
                cover_label.image = photo
            except:
                cover_label.config(image="", text="Kapak yüklenemedi")

        
        def update_suggestions(event=None):
            keyword = search_var.get().lower()
            suggestion_box.delete(0, tk.END)
            if keyword and self.game_list:
                filtered = [g for g in self.game_list if keyword in g['name'].lower()]
                for game in filtered[:20]:
                    suggestion_box.insert(tk.END, f"{game['name']} ({game['appid']})")

        def select_suggestion(event):
            selection = suggestion_box.curselection()
            if selection:
                selected_text = suggestion_box.get(selection[0])
                if '(' in selected_text and ')' in selected_text:
                    app_id = selected_text.split('(')[-1].replace(')', '')
                    game_name = selected_text.split(' (')[0]
                    self.app_id_var.set(app_id)
                    selected_label.config(text=f"Seçilen Oyun: {game_name} (ID: {app_id})")
                    self.animate_status_message(f"🎮 OYUN SEÇİLDİ: {game_name}", self.success_button)
                    fetch_and_show_cover(app_id)
                    fetch_and_show_details(app_id)

        
        def fetch_and_show_details(app_id):
            try:
                url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
                response = requests.get(url, timeout=10)
                data = response.json()
                if not data[app_id]["success"]:
                    detail_label.config(text="Detaylar alınamadı.")
                    return

                app_data = data[app_id]["data"]
                name = app_data.get("name", "Bilinmiyor")
                release = app_data.get("release_date", {}).get("date", "Bilinmiyor")
                publishers = ", ".join(app_data.get("publishers", [])) or "Bilinmiyor"
                genres = ", ".join([g['description'] for g in app_data.get("genres", [])]) or "Bilinmiyor"
                price = app_data.get("price_overview", {}).get("final_formatted", "Ücretsiz / Bilinmiyor")

                text = f"""
📌 Ad: {name}
📅 Çıkış: {release}
🏢 Yayıncı: {publishers}
📚 Tür: {genres}
💵 Fiyat: {price}
"""
                detail_label.config(text=text.strip())
            except Exception as e:
                detail_label.config(text=f"Detaylar alınamadı: {e}")



        button_frame = tk.Frame(search_window, bg=self.secondary_bg)
        button_frame.pack(pady=10)

        select_btn = tk.Button(button_frame, text="Seç", command=lambda: select_suggestion(None),
                             bg=self.primary_button, fg=self.text_color, font=("Segoe UI", 10, "bold"),
                             relief=tk.FLAT, padx=20)
        self.add_button_hover_effects(select_btn, self.primary_button, self._get_hover_color(self.primary_button), original_padx=20)
        select_btn.pack(side=tk.LEFT, padx=10)

        close_btn = tk.Button(button_frame, text="Kapat", command=search_window.destroy,
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
            text="🔍 SteamDB Aç",
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

        self.path_label = tk.Label(self.path_inner_frame, text="🔧 STEAM KURULUM KONUMU",
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

        self.browse_btn = tk.Button(self.path_entry_frame, text="📁 GÖZAT",
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

        self.id_label = tk.Label(self.inner_frame, text="🎮 STEAM OYUN ID",
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
            text="🚀 İNDİR & KUR",
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
            text="💀 OYUNU KALDIR",
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
            text="⚡ STEAM'İ YENİDEN BAŞLAT",
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

        self.status_label = tk.Label(self.status_container, text="⚡ HAZIR - STEAM KONUMU VE OYUN ID GİRİN",
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

        self.footer_label = tk.Label(footer_frame, text="👑 TOPRAK TARAFINDAN YAPILDI - 2025 ",
                              font=("Segoe UI", 9, "italic"),
                              fg='#666666', bg=self.bg_color)
        self.footer_label.pack(side=tk.RIGHT)

    def add_button_hover_effects(self, button, normal_color, hover_color, original_padx=None, original_pady=None):
        if original_padx is None:
            original_padx = button.cget('padx')
        if original_pady is None:
            original_pady = button.cget('pady')

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
            return False, "Oyun ID boş olamaz!"

        try:
            int(app_id)
            if len(app_id) < 1:
                return False, "Geçerli bir Oyun ID girin!"
            return True, ""
        except ValueError:
            return False, "Oyun ID sadece sayılardan oluşmalıdır!"

    def generate_url(self, app_id):
        return "https://codeload.github.com/SteamAutoCracks/ManifestHub/zip/refs/heads/" + app_id

    def show_progress(self):
        self.progress.pack(fill=tk.X, pady=(10, 0))
        self.progress.start(15)
        self.download_process_btn.configure(state='disabled', text="⏳ İŞLENİYOR...")
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


    def hide_progress(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.download_process_btn.configure(state='normal', text="🚀 İNDİR & KUR")
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


    def select_steam_folder(self):
        folder = filedialog.askdirectory(title="Steam Kurulum Klasörünü Seçin")
        if folder:
            self.steam_path_var.set(folder)
            self.animate_status_message("✅ STEAM KONUMU SEÇİLDİ", self.success_button)

    def download_and_process(self):
        app_id = self.app_id_var.get().strip()
        steam_path = self.steam_path_var.get().strip()

        is_valid, error_message = self.validate_app_id(app_id)
        if not is_valid:
            self.show_error_message(error_message)
            return

        if not steam_path:
            self.show_error_message("Lütfen önce Steam kurulum klasörünü seçin!")
            return

        threading.Thread(target=self._download_and_process_thread, args=(app_id, steam_path), daemon=True).start()

    def _download_and_process_thread(self, app_id, steam_path):
        url = self.generate_url(app_id)

        try:
            self.root.after(0, lambda: self.animate_status_message("🌐 MANIFEST DOSYALARI İNDİRİLİYOR...", self.primary_button))
            self.root.after(0, self.show_progress)

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            temp_zip = f"{app_id}.zip"
            with open(temp_zip, 'wb') as f:
                f.write(response.content)

            self.root.after(0, lambda: self.animate_status_message("⚙️ STEAM'E KURULUYOR...", self.primary_button))

            success, message = self.process_zip(temp_zip, steam_path, app_id)

            try:
                os.remove(temp_zip)
            except:
                pass

            self.root.after(0, self.hide_progress)

            if success:
                self.root.after(0, lambda: self.animate_status_message(
                    f"🎉 OYUN BAŞARIYLA KIRILDI: ID {app_id}", self.success_button))
                self.root.after(0, lambda: messagebox.showinfo("🎉 BAŞARILI", message))
            else:
                self.root.after(0, lambda: self.animate_status_message("❌ KURULUM BAŞARISIZ!", self.danger_button))
                self.root.after(0, lambda: messagebox.showerror("❌ HATA", message))

        except requests.exceptions.RequestException as e:
            self.root.after(0, self.hide_progress)
            self.root.after(0, lambda: self.animate_status_message("❌ İNDİRME BAŞARISIZ!", self.danger_button))
            self.root.after(0, lambda: messagebox.showerror("❌ İNDİRME HATASI", f"İndirme hatası: {str(e)}"))
        except Exception as e:
            self.root.after(0, self.hide_progress)
            self.root.after(0, lambda: self.animate_status_message("❌ HATA OLUŞTU!", self.danger_button))
            self.root.after(0, lambda: messagebox.showerror("❌ HATA", f"Beklenmeyen hata: {str(e)}"))

    def process_zip(self, zip_path, steam_path, app_id=None):
        try:
            stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
            depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
            os.makedirs(stplugin_dir, exist_ok=True)
            os.makedirs(depotcache_dir, exist_ok=True)

            game_id = os.path.splitext(os.path.basename(zip_path))[0]
            if not game_id.isdigit():
                return False, "ZIP dosya adı sadece Oyun ID'si (sayılar) içermelidir!"

            api_url = f'https://store.steampowered.com/api/appdetails?appids={game_id}'
            game_name = f"Oyun ID: {game_id}"
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

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.lower().endswith('.lua'):
                        target = os.path.join(stplugin_dir, os.path.basename(file))
                        with zip_ref.open(file) as src, open(target, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
                        lua_count += 1
                    elif file.lower().endswith('.manifest'):
                        target = os.path.join(depotcache_dir, os.path.basename(file))
                        with zip_ref.open(file) as src, open(target, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
                        manifest_count += 1

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
                self.add_installed_game(app_id, game_name)


            success_msg = f'''🎉 OYUN BAŞARIYLA KIRILDI!

📊 İSTATİSTİKLER:
• {lua_count} LUA dosyası işlendi
• {manifest_count} manifest dosyası kuruldu
• {new_count} yeni DLC eklendi

🚀 Oyununuzu oynamak için Steam'i yeniden başlatın!'''

            return True, success_msg

        except Exception as e:
            return False, f"İşleme sırasında hata:\n{str(e)}"

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
            self.show_error_message("Lütfen önce Steam kurulum klasörünü seçin!")
            return

        if not messagebox.askyesno("ONAY", f"{app_id} ID'li oyun kaldırılacak. Emin misiniz?"):
            return

        threading.Thread(target=self._remove_game_thread, args=(app_id,), daemon=True).start()

    def _remove_game_thread(self, app_id):
        steam_path = self.steam_path_var.get().strip()
        try:
            self.root.after(0, lambda: self.animate_status_message(f"🗑️ {app_id} ID'Lİ OYUN KALDIRILIYOR...", self.danger_button))
            self.root.after(0, self.show_progress)

            stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
            depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')

            lua_files_removed = 0
            manifest_files_removed = 0

            for filename in os.listdir(stplugin_dir):
                if filename.startswith(app_id) and filename.lower().endswith('.lua'):
                    os.remove(os.path.join(stplugin_dir, filename))
                    lua_files_removed += 1

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
            self.root.after(0, lambda: messagebox.showinfo("✅ BAŞARILI", f"{app_id} ID'li oyun ve ilgili dosyalar başarıyla kaldırıldı!\nLUA: {lua_files_removed}, Manifest: {manifest_files_removed}"))
            self.root.after(0, lambda: self.animate_status_message(f"🗑️ {app_id} ID'Lİ OYUN KALDIRILDI", self.success_button))
            self.root.after(0, self.populate_installed_games_list)

        except Exception as e:
            self.root.after(0, self.hide_progress)
            self.root.after(0, lambda: self.show_error_message(f"Oyun kaldırılırken hata:\n{str(e)}"))

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
            self.show_error_message("Lütfen önce Steam kurulum klasörünü seçin!")
            return

        steam_exe = os.path.join(steam_path, 'steam.exe')
        if not os.path.isfile(steam_exe):
            self.show_error_message("steam.exe bulunamadı! Lütfen doğru Steam klasörünü seçtiğinizden emin olun.")
            return

        try:
            subprocess.run(['taskkill', '/F', '/IM', 'steam.exe'])
            subprocess.Popen([steam_exe])
            messagebox.showinfo('✅ BAŞARILI', '🔄 Steam başarıyla yeniden başlatıldı!\n\n🎮 Artık oyununuzu oynayabilirsiniz!')
            self.animate_status_message("⚡ STEAM YENİDEN BAŞLATILDI", self.success_button)
        except Exception as e:
            self.show_error_message(f"Steam yeniden başlatılamadı:\n{str(e)}")

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
            print(f"Font animasyon hatası: {str(e)}")
            self.status_label.configure(font=("Segoe UI", 11, "bold"))

    def show_error_message(self, message):
        self.animate_status_message(f"❌ {message}", self.danger_button)
        messagebox.showerror("❌ HATA", message)

    def show_success_message(self, message):
        self.animate_status_message(f"✅ {message}", self.success_button)

def main():
    try:
        if 'TkinterDnD' in globals():
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()

        root.withdraw()

        legal_window = tk.Toplevel(root)

        legal = LegalNotice(legal_window)

        legal_window.wait_window(legal_window)

        if not hasattr(legal, 'var') or legal.var.get() != 1:
            root.destroy()
            return

        root.deiconify()
        
        
        system32_path = os.path.join(os.environ['SystemRoot'], 'System32')
        if system32_path not in os.environ['PATH']:
            os.environ['PATH'] = system32_path + ';' + os.environ['PATH']

        app = SteamManifestTool(root)

        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        root.mainloop()

    except Exception as e:
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("Kritik Hata", f"Uygulama başlatılamadı:\n{str(e)}", parent=error_root)
        error_root.destroy()
        raise


if __name__ == "__main__":
    main()
