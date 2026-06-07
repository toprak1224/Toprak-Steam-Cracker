# ⚡ Toprak Steam Cracker V5.0

<div align="center">
  <img src="ui_web/static/logo.png" alt="Logo" width="150"/>
  <h3>Advanced DRM Bypass & API Hooking Utility for Steam</h3>
  <p>
    <img src="https://img.shields.io/badge/Version-5.0-red.svg" alt="Version">
    <img src="https://img.shields.io/badge/Language-Python_|_C++-blue.svg" alt="Stack">
    <img src="https://img.shields.io/badge/Architecture-x86_/_x64-purple.svg" alt="Architecture">
    <img src="https://img.shields.io/badge/License-MIT-brightgreen.svg" alt="License">
  </p>
</div>

---

## 🇹🇷 Türkçe

**Toprak Steam Cracker**, Steam istemcisi üzerindeki DRM (Digital Rights Management) denetimlerini dinamik bellek manipülasyonu ile bypass etmek amacıyla geliştirilmiş gelişmiş bir araç setidir. Sistem, IAT (Import Address Table) ve VTable hooking yöntemlerini kullanarak ISteamApps ve ISteamUser arayüzlerini (interface) çalışma zamanında (runtime) yamalar ve yetkilendirme (authorization) sorgularını manipüle eder.

> 🛑 **GÜVENLİK VE MİMARİ NOTU:**  
> Projemiz; arka planda izinsiz kripto madencilik (cryptomining) yaptığı, telemetri topladığı ve bellek sızıntılarına (memory leak) yol açtığı bilinen **"Steam Tools"** kapalı kaynak kod yapısını **KULLANMAZ.** Kullanıcı tarafındaki (client-side) tüm API hook işlemleri, sıfırdan derlenmiş kendi kütüphanelerimiz (`xinput1_4.dll` ve `toprakcracker.dll`) üzerinden yönetilmektedir. Mimari tamamen şeffaf ve denetlenebilir durumdadır.

### 🌟 Temel Modüller ve Özellikler

* 🎮 **Dinamik Ownership Enjeksiyonu:** Entegre edilmiş 62.000+ AppID barındıran veritabanı üzerinden, seçilen uygulamanın AppID ve DLC ID argümanlarını `.lua` payload'larına dönüştürerek doğrudan Steam'in `m_mapOwnedApps` bellek yapısına işler.
* 🌐 **Online Fix (Multiplayer Bypass) Desteği:** Çevrimiçi oyunlar için gereken "Spacewar" (AppID 480) yönlendirmelerini veya özel network bypass yamalarını uygulama içinden asenkron olarak indirip oyun dizinine entegre eder.
* ⚙️ **Modüler Hooking Motoru (Engine):** Steam istemcisinin güncellemelerinden etkilenmemek adına dinamik offset taraması (signature scanning) kullanır. `ISteamApps::BIsSubscribedApp` ve `BIsDlcInstalled` fonksiyonları return değerlerini daima `true` (1) dönecek şekilde manipüle edilir.
* 🎨 **Asenkron UI ve IPC İletişimi:** PyWebView tabanlı frontend ile Python backend arasındaki iletişim, asenkron REST/JS API köprüsü üzerinden sağlanır. Arayüz render işlemleri Chromium/Edge-Webview2 motoruyla donanım hızlandırmalı (hardware-accelerated) olarak çalışır.

### 📸 Arayüz (UI)
<div align="center">
  <!-- GÖRSELLERİNİZİ AŞAĞIDAKİ "LİNK_BURAYA_GELECEK" YAZAN YERLERE YAPIŞTIRIN -->
  <img width="1253" height="805" alt="image" src="https://github.com/user-attachments/assets/e5010cc3-1a7c-483f-aa1b-483ac6032e69" />
  <img width="1256" height="803" alt="image" src="https://github.com/user-attachments/assets/6b3e4d5b-b070-451a-8ad3-6e9b7448343b" />

</div>

### 🚀 Teknik İşleyiş (Under The Hood)
1. **DLL Hijacking:** Proje, sistemde standart bir Windows kütüphanesi gibi davranan `xinput1_4.dll` modülünü Steam root dizinine konumlandırır.
2. **Payload Yüklemesi:** Steam.exe başlatıldığında DllMain tetiklenir ve orijinal fonksiyonlar export edilirken (crash önlemek amacıyla), `LoadLibrary()` çağrısı ile asıl payload olan `toprakcracker.dll` belleğe (memory) alınır.
3. **API Hooking:** VTable pointer'ları tespit edilerek lisans kontrolü yapan Steam API arayüzleri hook'lanır.
4. **Data Ayrıştırma (Parsing):** Yüklenen oyunların `.manifest` ve `.lua` yapılandırmaları okunur, bellek içi ownership tablosu güncellenir ve Steam API yetki sorguları başarılı (Status: OK) olarak döndürülür.

> **⚠️ YASAL UYARI VE SORUMLULUK REDDİ:**  
> Bu yazılım yalnızca **Tersine Mühendislik (Reverse Engineering) analizi, API çalışma mantığının incelenmesi ve Güvenlik Araştırmaları** (Security Research) kapsamında "Proof of Concept (PoC)" olarak hazırlanmıştır. Dijital korsanlığı teşvik etmez. Yazılımın amacı dışında kullanımından doğacak hesap yasaklamaları (VAC/Game Ban) veya yasal yükümlülüklerden kullanıcı sorumludur. Lütfen kullandığınız ürünlerin lisanslarını satın alarak geliştiricilere destek olunuz.

---

## 🌍 English

**Toprak Steam Cracker** is an advanced toolset designed to bypass DRM (Digital Rights Management) verifications on the Steam client via dynamic memory manipulation. The system utilizes IAT (Import Address Table) and VTable hooking methods to patch the `ISteamApps` and `ISteamUser` interfaces at runtime, effectively manipulating authorization queries.

> 🛑 **SECURITY & ARCHITECTURE NOTICE:**  
> Our project absolutely **DOES NOT UTILIZE** the closed-source "Steam Tools" infrastructure, which is known for unconsented background cryptomining, telemetry collection, and memory leaks. All client-side API hooking is strictly handled by our custom-compiled, transparent libraries (`xinput1_4.dll` and `toprakcracker.dll`).

### 🌟 Core Modules & Features

* 🎮 **Dynamic Ownership Injection:** Converts selected AppID and DLC ID arguments into `.lua` payloads from a built-in database of 62,000+ entries, injecting them directly into Steam's internal `m_mapOwnedApps` memory structure.
* 🌐 **Online Fix (Multiplayer Bypass) Support:** Asynchronously fetches and integrates "Spacewar" (AppID 480) redirects or custom network bypass patches required for online multiplayer functionality directly into the game directory.
* ⚙️ **Modular Hooking Engine:** Implements dynamic signature scanning to maintain stability across Steam client updates. Core functions such as `ISteamApps::BIsSubscribedApp` and `BIsDlcInstalled` are hooked to forcefully return `true` (1).
* 🎨 **Asynchronous UI & IPC Communication:** The PyWebView-based frontend communicates with the Python backend via an asynchronous JS/REST API bridge. UI rendering is fully hardware-accelerated using the Chromium/Edge-Webview2 engine.

### 📸 User Interface
<div align="center">
  <!-- INSERT YOUR IMAGE LINKS BELOW REPLACING THE TEXT -->
  <img width="1253" height="805" alt="image" src="https://github.com/user-attachments/assets/e5010cc3-1a7c-483f-aa1b-483ac6032e69" />
  <img width="1256" height="803" alt="image" src="https://github.com/user-attachments/assets/6b3e4d5b-b070-451a-8ad3-6e9b7448343b" />
</div>

### 🚀 Under The Hood (Technical Flow)
1. **DLL Hijacking:** The application deploys our custom `xinput1_4.dll` into the Steam root directory, mimicking a standard Windows controller library.
2. **Payload Execution:** Upon Steam.exe initialization, the `DllMain` entry point is triggered. Original xinput functions are properly exported to prevent process crashes, while a `LoadLibrary()` call fetches our main payload, `toprakcracker.dll`.
3. **API Hooking:** VTable pointers are intercepted, allowing the engine to detour Steam API interfaces responsible for license verification.
4. **Data Parsing:** The configuration files (`.manifest` and `.lua`) of the user-selected games are parsed, the in-memory ownership cache is updated, and all subsequent authorization queries return an "OK" status.

> **⚠️ LEGAL DISCLAIMER:**  
> This software is strictly intended as a "Proof of Concept (PoC)" for **Reverse Engineering analysis, API flow investigation, and Security Research**. It does not encourage or promote digital piracy. The developers bear no responsibility for any misuse, account bans (VAC/Game Ban), or legal liabilities resulting from the use of this software. Please support software developers by purchasing legitimate licenses for the products you use.

---
<div align="center">
  <i>Developed with ❤️ by Toprak</i>
</div>
