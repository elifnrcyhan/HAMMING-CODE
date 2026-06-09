# BLM230 Bilgisayar Mimarisi - Hamming Code Simülatörü

Bu proje, bilgisayar mimarisinde bellek güvenliği ve hata tespiti/düzeltmesi amacıyla sıkça kullanılan **Hamming Code (Hamming Kodu)** algoritmasını görselleştiren interaktif bir simülatördür. Python'ın `tkinter` kütüphanesi kullanılarak geliştirilen bu masaüstü uygulaması, veri bitlerinin belleğe yazılma (kodlanma) ve bellekten okunma (kod çözme/düzeltme) süreçlerini donanımsal mantığa uygun olarak simüle eder.

## 🚀 Özellikler

* **Çoklu Bit Modu Desteği:** Uygulama, modern bilgisayar mimarilerindeki standartlara uygun olarak **8-Bit**, **16-Bit** ve **32-Bit** veri uzunluklarını destekler.
* **Otomatik Parite ve Bit Dağılım Hesaplaması:** Çift Parite (*Even Parity*) yöntemini kullanarak $2^n$ (1, 2, 4, 8, 16, 32...) konumlarındaki parite bitlerini otomatik hesaplar ve matrise yerleştirir.
* **Yapay Hata Enjeksiyonu (Fault Injection):** Bellek matrisi oluştuktan sonra, herhangi bir bit hücresine (veri veya parite fark etmeksizin) farenizle tıklayarak yapay olarak **bit değiştirme (hata) hatası** oluşturabilirsiniz.
* **Sendrom Analizi ve Otomatik Düzeltme:** Bellekten okuma yapıldığında algoritma bir *Sendrom Kelimesi (Syndrome Word)* üretir. Eğer hata varsa, donanımsal *Compare & Corrector* bloğu gibi çalışarak hatanın tam konumunu tespit eder ve veriyi orijinal haline getirip bozulmamış temiz çıktıyı verir.

---

## 🛠️ Hamming Yapılandırma Tablosu

Uygulamanın mimari arka planda kullandığı bit dağılım tablosu şu şekildedir:

| Seçilen Mod | Veri Bitleri (M) | Parite Bitleri (K) | Toplam Kod Uzunluğu (M + K) |
| :--- | :---: | :---: | :---: |
| **8-Bit** | 8 | 4 | 12 Bit |
| **16-Bit** | 16 | 5 | 21 Bit |
| **32-Bit** | 32 | 6 | 38 Bit |

---

## 💻 Ekran Görüntüsü ve Arayüz Tasarımı

Uygulama arayüzü 3 ana donanım katmanından oluşur:
1. **Giriş Paneli (Data In):** Kullanıcıdan ikilik tabanda (binary) veri alır.
2. **Bellek Matrisi (Memory):** Kodlanmış veriyi tutar. Mavi renkli hücreler parite bitlerini, yeşil renkli hücreler ise veri bitlerini temsil eder.
3. **Düzeltici Çıktıları (Compare & Corrector):** Sendrom kelimesini ve nihai temiz veriyi (*Data Out*) gösterir.

---

## 🔧 Kurulum ve Çalıştırma

Projenin çalışabilmesi için bilgisayarınızda **Python 3** yüklü olması yeterlidir. Ekstra bir kütüphane kurulumuna (pip) gerek yoktur çünkü `tkinter` Python ile birlikte yerleşik olarak gelmektedir.

1. Depoyu bilgisayarınıza klonlayın veya zip olarak indirin:
   ```bash
   git clone [https://github.com/elifnrcyhan/HAMMING-CODE.git](https://github.com/elifnrcyhan/HAMMING-CODE.git)
