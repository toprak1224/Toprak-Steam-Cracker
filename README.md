# 📄 Toprak Steam Cracker & Manifest Oluşturucu

➡️ Looking for the English version? [Click here to read in English 🇬🇧](#-toprak-steam-cracker--manifest-generator)

<img width="392" height="424" alt="image" src="https://github.com/user-attachments/assets/8033ee05-efd6-42e9-9195-bcf0dba72708" />
<img width="392" height="424" alt="image" src="https://github.com/user-attachments/assets/025f51e8-f4ea-40a9-886c-92c041d112f5" />

Toprak Steam Cracker, Steam oyunları için manifest ve LUA dosyalarının yönetimini kolaylaştırmak amacıyla geliştirilmiş, Windows için hazırlanmış bir masaüstü uygulamasıdır.  
Bu yazılım yalnızca eğitimsel ve deneysel amaçlarla kullanılmak üzere tasarlanmıştır.

---

### 🔖 İçindekiler  
[Yasal Uyarı](#yasal-uyarı) • [Özellikler](#özellikler) • [Kurulum ve Kullanım](#kurulum-ve-kullanım) • [Lisans](#lisans) • [Katkıda Bulunma](#katkıda-bulunma) • [İletişim](#iletişim) • [Hakkında](#hakkında)

---

## ⚠️ Yasal Uyarı

Bu yazılım yalnızca eğitimsel ve deneysel amaçlarla geliştirilmiştir.

- Hiçbir şekilde ticari kazanç amacı taşımaz.
- Dijital içeriklerin izinsiz kullanımını, dağıtımını veya çoğaltılmasını teşvik etmez.
- Kullanım amacı, yalnızca Steam istemcisi üzerinde teknik analiz ve entegrasyon testleri gerçekleştirmektir.

**Hukuki Bilgilendirme:**  
Steam’e ait içeriklerin lisanssız kullanımı;  
5846 Sayılı Fikir ve Sanat Eserleri Kanunu, Türk Ceza Kanunu’nun 135., 136. ve 137. maddeleri ve uluslararası telif yasaları kapsamında suç teşkil eder.

**Geliştirici Sorumluluğu:**  
Bu yazılımın amacı dışında veya hukuka aykırı şekilde kullanılması halinde geliştirici hiçbir sorumluluk kabul etmez.

---

## 🚀 Özellikler

### 🔧 Steam Manifest Yönetimi
- Steam AppID girerek manifest ve LUA dosyalarını GitHub’daki `ManifestHub` üzerinden indirir.
- Aşağıdaki klasörlere otomatik olarak yerleştirir:
  - `config/depotcache`
  - `config/stplug-in`
- Oyun ve varsa DLC içeriklerinin yüklenme durumunu takip eder.
- Girilen AppID’ye göre oyunları kaldırabilir.

### 📂 Manuel Dosya Ekleme
- ZIP dosyaları içinden manifest ve LUA belgelerini çıkarır.
- `.manifest` ve `.lua` dosyalarını doğrudan sürükle-bırak ile kabul eder.

### 🛠️ HID.dll Yönetimi
- Gerekli `hid.dll` dosyasını otomatik olarak Steam dizinine veya masaüstüne indirir.
- İstenirse kaldırma işlemi yapılabilir.

### 🔍 Oyun Bilgisi & Keşif
- Steam API üzerinden oyun araması yapılabilir (isim → AppID).
- “Yüklü Oyunları Göster” özelliği ile mevcut oyunlar listelenir.
- SteamDB sayfasına hızlı erişim sağlanır.
- Sıkça Sorulan Sorular bağlantısı mevcuttur.

### 🖥️ Steam Kontrol
- Steam istemcisi kapatılabilir veya yeniden başlatılabilir.

### 🎨 Kullanıcı Arayüzü
- Karanlık tema desteği.
- Etkileşimli butonlar ve giriş alanları.
- Anlık durum mesajları ve animasyonlu yükleme çubuğu.

### 📊 Yeni Özellik – Detaylı Oyun Bilgisi
- Seçilen oyun için aşağıdaki bilgiler kapak görselinin altında otomatik olarak gösterilir:
  - Oyun adı
  - Yayıncı
  - Tür(ler)
  - Çıkış tarihi
  - Fiyat bilgisi (Steam API üzerinden alınır)

---

## ⚙️ Kurulum ve Kullanım

### 1. Python Kurulumu
Bilgisayarınızda **Python 3.x** sürümünün kurulu olması gerekmektedir.  
[Python İndir](https://www.python.org/downloads/)

### 2. Bağımlılıkların Kurulumu
CMD veya PowerShell’de aşağıdaki komutu çalıştırın:

## 📄 Toprak Steam Cracker & Manifest Generator

⬅️ Türkçe sürüm için [buraya tıklayın 🇹🇷](#-toprak-steam-cracker--manifest-oluşturucu)

<img width="392" height="424" alt="image" src="https://github.com/user-attachments/assets/8033ee05-efd6-42e9-9195-bcf0dba72708" />
<img width="392" height="424" alt="image" src="https://github.com/user-attachments/assets/025f51e8-f4ea-40a9-886c-92c041d112f5" />


Toprak Steam Cracker is a desktop application developed for Windows, designed to simplify the management of manifest and LUA files for Steam games.  
This software is intended strictly for **educational and experimental purposes**.

---

### 🔖 Contents  
[Legal Notice](#legal-notice) • [Features](#features) • [Installation & Usage](#installation--usage) • [License](#license) • [Contributing](#contributing) • [Contact](#contact) • [About](#about)

---

## ⚠️ Legal Notice

This software is developed for **educational and experimental purposes only**.

- It is not intended for any commercial use.
- It does **not promote** the unauthorized use, distribution, or reproduction of digital content.
- It is intended solely for technical analysis and integration testing on the Steam client.

**Legal Disclaimer:**  
Unauthorized use of Steam-related content may constitute a legal offense under:
- Turkish Law on Intellectual and Artistic Works (Law No. 5846)
- Turkish Penal Code Articles 135–137
- International copyright laws

**Developer Responsibility:**  
The developer assumes **no responsibility** for any use of this software outside its intended scope or in violation of the law.

---

## 🚀 Features

### 🔧 Steam Manifest Management
- Download manifest and LUA files from `ManifestHub` on GitHub using Steam AppID.
- Automatically places files in the following folders:
  - `config/depotcache`
  - `config/stplug-in`
- Tracks the installation status of games and their DLCs.
- Supports game uninstallation via AppID.

### 📂 Manual File Addition
- Extracts manifest and LUA files from ZIP archives.
- Supports drag-and-drop for `.manifest` and `.lua` files.

### 🛠️ HID.dll Management
- Automatically downloads the required `hid.dll` to the Steam directory or desktop.
- Optionally allows removing the DLL.

### 🔍 Game Info & Discovery
- Search games via Steam API (name → AppID).
- Show installed games feature.
- Quick access to SteamDB page.
- Includes a Frequently Asked Questions link.

### 🖥️ Steam Control
- Steam client can be closed or restarted from the app.

### 🎨 User Interface
- Dark mode support.
- Interactive buttons and input fields.
- Real-time status messages and animated loading bar.

### 📊 New Feature – Detailed Game Info
- For a selected game, displays the following automatically under the cover image:
  - Game name
  - Publisher
  - Genre(s)
  - Release date
  - Price info (retrieved via Steam API)

---

## ⚙️ Installation & Usage

### 1. Install Python
Ensure **Python 3.x** is installed on your system.  
[Download Python](https://www.python.org/downloads/)

### 2. Install Dependencies  
Run the following command in CMD or PowerShell:

```bash
pip install -r requirements.txt

