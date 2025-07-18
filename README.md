                                            Toprak Steam Cracker & Manifest Oluşturucu
                                                                                                                                   
                                                                                                                                   
                                                                                                                                   
                                                                                                                                   
<img width="492" height="524" alt="image" src="https://github.com/user-attachments/assets/8033ee05-efd6-42e9-9195-bcf0dba72708" /> <img width="492" height="524" alt="image" src="https://github.com/user-attachments/assets/025f51e8-f4ea-40a9-886c-92c041d112f5" />


# 📄 Toprak Steam Cracker & Manifest Oluşturucu

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
- Bilgisayarınızda **Python 3.x** sürümünün kurulu olması gerekmektedir.  
  [Python İndir](https://www.python.org/downloads/)

### 2. Bağımlılıkların Kurulumu
CMD veya PowerShell’de aşağıdaki komutu çalıştırın:

```bash
pip install -r requirements.txt
