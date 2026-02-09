# 🛡️ KALORİ TAKİP

Bu proje, mevcut beslenme ve kalori takip uygulamalarının karmaşık arayüzleri, kısıtlayıcı yapıları ve estetikten uzak tasarımları nedeniyle, kişisel ihtiyaçlarıma ve görsel zevkime uygun bir alternatif oluşturma amacıyla geliştirilmiştir. 
## 🎯 Projenin Amacı

Beslenme takibi sürecini sıkıcı bir veri girişinden çıkarıp, bir oyun envanteri yönetimi hissiyatına taşımayı hedeflemektedir. Mevcut çözümlerin aksine; gereksiz karmaşıklıktan arındırılmış, görsel sadeliği pikselli bir dünya ile birleştiren ve tamamen yerel ortamda çalışan güvenli bir yapı sunulmuştur.

## 🛠️ Kullanılan Teknolojiler ve Diller

- Python 3: Uygulamanın temel mantığı ve veri işleme süreçleri için kullanılmıştır.
- Flask: Web sunucusu ve yönlendirme (routing) işlemleri için tercih edilen Python mikro-çerçevesidir.
- SQLite: Verilerin yerel olarak güvenli ve yüksek performanslı bir şekilde saklanması için kullanılan ilişkisel veritabanıdır.
- HTML5 & CSS3: Pikselli  render özellikleri ve özelleştirilmiş temalar ile kullanıcı arayüzü oluşturulmuştur.
- Jinja2: HTML şablonları içerisinde dinamik veri yönetimi ve matematiksel hesaplamalar için entegre edilmiştir.

## ⚙️ Kurulum ve Çalıştırma

Projeyi kendi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

1. Projeyi klonlayın:  
   `git clone https://github.com/HakanURAL06/Kalori-Takip.git`

2. Sanal ortamı oluşturun ve aktif edin:  
   `python3 -m venv venv`  
   `source venv/bin/activate`

3. Gerekli kütüphaneleri yükleyin:  
   `pip install -r requirements.txt`

4. Uygulamayı başlatın:  
   `python3 app.py`

5. Tarayıcınızdan şu adrese gidin:  
   `http://127.0.0.1:5001`
