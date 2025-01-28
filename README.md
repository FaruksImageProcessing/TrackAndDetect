# TrackAndDetect

**TrackAndDetect**, video kaydındaki nesneleri (araçları ve yayaları) tespit ederek hızlarını (pixel/saniye) belirleyen ve takip eden bir görüntü işleme projesidir. Geri planda, hareketli nesneleri izlemek için bir arka plan güncelleme yöntemi (background subtraction) ve nesne tespit algoritmaları kullanılmıştır.

---

## Giriş
Amacımız, videolardaki nesneleri (yayalar ve taşıtlar) tespit etmek, hızlarını hesaplamak ve bunları takip etmektir. Projede şu yöntemler kullanılmıştır:

### 1. **Gri Tonlamaya Çevirme**
- **Neden Kullanıldı?**
  Bir video akışındaki nesneleri takip etmek için her pikselin ışık yoğunluğunun hesaplanması gereklidir. Gri tonlama, renkli görüntüleri daha hızlı işlemek için kullanılmıştır.

### 2. **Arka Plan Çıkarma ve Güncelleme**
- **Neden Kullanıldı?**
  Hareketli nesnelerin doğru bir şekilde tespiti için sabit arka plan güncellenmiştir. `cv2.accumulateWeighted()` fonksiyonu bu işlemde kullanılmıştır.

### 3. **Mesafe Hesaplama**
- **Neden Kullanıldı?**
  Yeni tespit edilen nesneler ile önceki nesneler arasındaki mesafeyi hesaplamak, doğru eşleştirme ve takip için gereklidir. `scipy.spatial.distance.cdist()` fonksiyonu ile nesneler arası mesafe hesaplanmıştır.

### 4. **Morfolojik İşlemler**
- **Neden Kullanıldı?**
  Maske üzerindeki gürültülerin azaltılması ve nesnelerin düzgün şekilde tespit edilmesi için kapama (closing) işlemi uygulanmıştır.

### 5. **Hız Hesaplama**
- **Neden Kullanıldı?**
  Nesnelerin hızını hesaplamak, taşıt ve yayaları sınıflandırmayı kolaylaştırır. Hız hesaplama, merkezler arası mesafeyi zamana bölerek yapılmıştır.

### 6. **Kurallara Uygunluk Tespiti**
- Tespit edilen nesneler, yaya yolları ve kaldırımların konumlarına göre kontrol edilmiştir. Taşıtlar yaya geçidinde durmuyorsa veya yayalar yaya yolunda değilse, bu nesneler kırmızı kutucuklarla işaretlenmiştir.

---

## Avantajlar ve Alternatif Yöntemler
| **Yöntem**             | **Avantajlar**                                                                 | **Alternatif Yöntemler**                                   |
|-------------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------|
| **Gri Tonlama**         | Bellek kullanımını ve hesaplama süresini azaltır.                            | Renkli görüntüler kullanılabilir, ancak bu işlemciyi yorar. |
| **Arka Plan Çıkarma**   | Doğru hareket tespiti, ışık değişimlerine karşı direnç.                      | `cv2.backgroundSubtractorMOG2()` kullanılabilir.           |
| **Mesafe Hesaplama**    | Hızlı ve doğru mesafe hesaplama.                                             | Manuel mesafe hesaplama da yapılabilir.                   |
| **Morfolojik İşlemler** | Gürültüyü azaltır, daha doğru nesne tespiti sağlar.                          | Gaussian Blur veya diğer filtreler kullanılabilir.         |
| **Hız Hesaplama**       | Nesne türünü (taşıt/yaya) belirlemek için etkili.                           | Alan/en-boy oranına göre sınıflandırma yapılabilir.        |

---

## Hatalar ve Çözüm Fikirleri
1. **Videonun Belirli Bir Kısmında Bozukluk:**
   - **Çözüm:** Hareketli ortalamalar yöntemi kullanılarak bu sorun giderilmiştir.

2. **Araç ve Yaya Tespit Hatası:**
   - **Çözüm:** YOLO veya Haar Cascade gibi daha gelişmiş makine öğrenmesi modelleri entegre edilebilir.

3. **Sabit Hız Tespiti Sorunu:**
   - **Çözüm:** Optik akış (optical flow) yöntemleri ile daha doğru hız tahmini yapılabilir.

---

## Öğrendiklerimiz
- Temel görüntü işleme tekniklerine (gri tonlama, arka plan çıkarma, hareket algılama) hakimiyet sağladık.
- Nesne sınıflandırma ve takip süreçlerinde pratik deneyimler kazandık.
- Görselleştirme ve hata ayıklama süreçlerini öğrenerek projeyi daha verimli hale getirdik.

---

## Katkıda Bulunma
Projeye katkıda bulunmak isterseniz pull request gönderebilir veya issue oluşturabilirsiniz. Her türlü destek için teşekkür ederiz!

---

## Lisans
Bu proje MIT Lisansı ile lisanslanmıştır.
