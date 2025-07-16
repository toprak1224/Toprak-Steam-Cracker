Toprak Steam Cracker & Manifest Oluşturucu
<img width="992" height="1024" alt="image" src="https://github.com/user-attachments/assets/8033ee05-efd6-42e9-9195-bcf0dba72708" />


📚 İçindekiler
Hakkında

Yasal Uyarı

Özellikler

Kurulum ve Kullanım

Lisans

Katkıda Bulunma

İletişim

ℹ️ Hakkında
"Toprak Steam Cracker & Manifest Oluşturucu", Steam platformundaki oyunlar için gerekli olan manifest ve LUA dosyalarının yönetimini kolaylaştıran bir Windows masaüstü uygulamasıdır. Bu yazılım, eğitimsel ve deneysel amaçlarla geliştirilmiştir ve kullanıcıların Steam istemcisi üzerinde teknik analiz ve entegrasyon testleri gerçekleştirmesine olanak tanır. Uygulama, kullanışlı bir arayüze sahip olup, Steam oyun ID'leri aracılığıyla otomatik dosya indirme, manuel dosya yükleme ve Steam ortamını yönetme gibi çeşitli fonksiyonlar sunar.

Not: Bu proje, hiçbir ticari kazanç amacı taşımaz ve dijital içeriklerin izinsiz kullanımını, dağıtımını veya çoğaltılmasını teşvik etmez.

⚠️ Yasal Uyarı
Bu yazılım yalnızca eğitimsel ve deneysel amaçlarla geliştirilmiştir.

Toprak Steam Cracker, hiçbir şekilde ticari kazanç amacı taşımaz ve dijital içeriklerin izinsiz kullanımını, dağıtımını veya çoğaltılmasını teşvik etmez.

Yazılımın kullanım amacı, yalnızca Steam istemcisi üzerinde teknik analiz ve entegrasyon testleri gerçekleştirmek ile sınırlıdır.

Önemli Hukuki Bilgilendirme: Steam platformuna ait içeriklerin lisans satın alınmadan kullanılması; 5846 Sayılı Fikir ve Sanat Eserleri Kanunu, Türk Ceza Kanunu’nun 135., 136. ve 137. maddeleri, ve uluslararası fikri mülkiyet yasaları kapsamında suç teşkil eder. Bu tür yasa dışı kullanım; hukuki yaptırımların yanı sıra cezai sorumluluklara da neden olabilir.

Geliştirici Sorumluluk Reddi: Bu yazılımın amacı dışında veya hukuka aykırı şekilde kullanılması halinde, geliştirici hiçbir sorumluluk kabul etmez. Lütfen bu yazılımı yalnızca etik ve yasal sınırlar içinde kullanınız.

✨ Özellikler
Otomatik Steam Yolu Algılama: Sistem kayıt defteri ve yaygın kurulum dizinleri aracılığıyla Steam'in kurulu olduğu konumu otomatik olarak tespit eder.

Steam Manifest Yönetimi:

Bir Steam Oyun ID'si girilerek ilgili manifest ve LUA dosyalarını GitHub tabanlı bir depodan (ManifestHub) indirir.

İndirilen dosyaları doğrudan Steam'in config/depotcache ve config/stplug-in klasörlerine yerleştirir.

Yüklenen oyunların ve ilgili DLC'lerin (varsa) otomatik olarak takibini yapar.

Girilen Oyun ID'sine ait dosyaları ve DLC girişlerini Steam dizininden kaldırır.

Manuel Dosya Ekleme:

ZIP dosyalarını (.zip) seçerek içerisindeki manifest ve LUA dosyalarını otomatik olarak ilgili Steam klasörlerine çıkarır.

Tek tek .manifest ve .lua dosyalarını sürükle-bırak yöntemiyle veya dosya seçici ile doğrudan uygulamaya ekleme imkanı sunar.

HID.dll Yönetimi: Gerekli hid.dll dosyasını Steam kurulum klasörüne veya masaüstüne indirme ve Steam dizininden kaldırma seçenekleri.

Oyun Bilgisi ve Keşif:

Steam API aracılığıyla oyun isimlerini arama ve AppID'lerini kolayca bulma.

Uygulama üzerinden yüklü oyunları listeleme ve hızlıca AppID'lerini giriş alanına kopyalama.

SteamDB web sitesine hızlı erişim düğmesi.

Sıkça Sorulan Sorular (SSS) bağlantısı.

Steam İstemcisi Kontrolü: Steam'i kapatma ve yeniden başlatma işlevselliği.

Kullanıcı Deneyimi:

Karanlık tema ve modern arayüz tasarımı.

Etkileşimli düğme ve giriş alanı efektleri.

Anlık durum güncellemeleri ve animasyonlu yükleme göstergesi.

🚀 Kurulum ve Kullanım
Python Kurulumu: Bilgisayarınızda Python 3.x kurulu olduğundan emin olun.
Python'u buradan indirebilirsiniz.

Gerekli Kütüphaneleri Yükleyin: Projenin bağımlılıklarını kurmak için komut istemcinizi (CMD/PowerShell) açın ve aşağıdaki komutu çalıştırın:

Bash

pip install requests tkinterdnd2 pywin32
pywin32 kütüphanesi winreg modülü için gereklidir (Windows kayıt defterine erişim).

Projeyi Klonlayın veya İndirin: Bu depoyu bilgisayarınıza klonlayın veya ZIP olarak indirin:

Bash

git clone https://github.com/KULLANICI_ADINIZ/PROJE_ADINIZ.git
cd PROJE_ADINIZ
Uygulamayı Çalıştırın: Proje klasörüne gittikten sonra, aşağıdaki komutla uygulamayı başlatın:

Bash

python "Cracker Cevo.py"
Kullanım Adımları:

Uygulama açıldığında bir Yasal Uyarı penceresi belirecektir. Uygulamayı kullanmaya devam etmek için uyarıyı okuyup kabul etmelisiniz.

Ana arayüzde "STEAM KURULUM KONUMU" alanının otomatik olarak doldurulduğunu göreceksiniz. Eğer doğru değilse veya bulunamazsa, "GÖZAT" düğmesini kullanarak Steam'in kurulu olduğu ana klasörü (steam.exe dosyasının bulunduğu yer) seçin.

"STEAM OYUN ID" alanına, kırmak istediğiniz oyunun Steam AppID'sini girin. Eğer bilmiyorsanız, "Oyun Ara" düğmesini kullanarak oyunun adıyla arama yapabilir veya SteamDB adresini ziyaret edebilirsiniz.

"İNDİR & KUR" düğmesine tıklayarak manifest dosyalarını indirme ve Steam'e kurma işlemini başlatın.

İsterseniz, "MANUEL DOSYA EKLEME" bölümüne .manifest veya .lua dosyalarını doğrudan sürükleyip bırakabilirsiniz.

Oyunları kaldırmak veya Steam'i yeniden başlatmak için ilgili düğmeleri kullanın.

Yüklü oyunlarınızı görmek için "Yüklü Oyunlar" düğmesine tıklayın.

📜 Lisans
Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için LICENSE dosyasına bakabilirsiniz.

🤝 Katkıda Bulunma
Geliştirmeye katkıda bulunmaktan memnuniyet duyarız! Hata raporları, yeni özellik önerileri veya kod katkıları için lütfen aşağıdaki adımları izleyin:

Depoyu forklayın.

Yeni bir özellik veya hata düzeltmesi için dal (branch) oluşturun: git checkout -b feature/YeniOzellik

Değişikliklerinizi yapın ve commit edin: git commit -m "feat: Yeni özellik eklendi"

Dalı orijinal depoya push edin: git push origin feature/YeniOzellik

Bir Pull Request (Çekme İsteği) oluşturun.

📧 İletişim
Herhangi bir sorunuz veya öneriniz varsa, lütfen GitHub Issues bölümünü kullanmaktan çekinmeyin.
