# MIT License
# Copyright (c) 2025 Faruk
# Bu yazılımın kullanımına, değiştirilmesine ve dağıtılmasına izin verilir. Detaylar için LICENSE dosyasına bakınız.


import cv2
import numpy as np
from scipy.spatial import distance as dist

cap = cv2.VideoCapture('Train.mp4')

ret, frame = cap.read()
background = np.float32(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))


obje_takip = {}
sonraki_obje_İd = 0
kayboldu = {} # Kaybolan nesneleri tutan dizi

# Hız hesaplaması (piksel/saniye)
fps = cap.get(cv2.CAP_PROP_FPS)
hiz_aralik = 1 / fps  # Zaman aralığı (saniye)

# Sınıflandırma için eşikler
yaya_threshold = 2000  # Yayalar için maksimum alan
tasit_threshold = 5000  # Taşıtlar için minimum alan
enboy_threshold = 0.5 # Yayalar için en-boy oranı (h/w)
hiz_threshold = 10  # Hız değeri (px/s)

# Toplam sayılar için değişkenler
toplam_yaya = 0
toplam_tasit = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    #gri(x,y)=0.299⋅R(x,y)+0.587⋅G(x,y)+0.114⋅B(x,y)
    #[R(x,y),G(x,y),B(x,y) görüntünün her pikselindeki kırmızı,yeşil ve mavi renk bileşenlerinin ifade eder.]
    gri = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #background′(x,y)=α⋅gri(x,y)+(1−α)⋅background(x,y) Background'u hareketli ortalama formülü ile güncelliyoruz.
    cv2.accumulateWeighted(gri, background, 0.01)

    # fark(x,y)=|background′(x,y)−gri(x,y)|
    fark = cv2.absdiff(cv2.convertScaleAbs(background), gri)

    #fgMask(x,y)={eğer fark(x,y)>Threshold 255} |arka plan-gri|>Threshold 255
    #            {değilse                   0 } |arka plan-gri|<=Threshold 0
    _, maske = cv2.threshold(fark, 50, 255, cv2.THRESH_BINARY)


    # Kapama(closing) işlemi ile küçük boşlukları kapatıyoruz.{A•B = (A⊕B)⊖B}
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    maske = cv2.morphologyEx(maske, cv2.MORPH_CLOSE, kernel, iterations=1)  # 1 iterasyon

    # Konturları buluyoruz.(Kontur,görüntüde figürlerin sınırlarını belli eden çizgilerdir.)
    konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Algılanan nesnelerin merkez noktaları,alanları ve oranlar burada saklanıyor.
    merkezler = []
    alanlar = []
    oranlar = []#(en/boy oranı veya px/s oranı gibi)

    for kontur in konturlar:
        alan = cv2.contourArea(kontur)#kontur alanı hesaplama ∑(Piksellerin içindeki Alan)
        if alan > 500:# Minimum threshold'u belirliyoruz.(Gürültüyü nesne olarak saymaması için)
            x, y, w, h = cv2.boundingRect(kontur)#dikdörtgen koordinatları(görüntü çerçevesi için) x ve y kenarları width(genişlik) height(yükseklik)
            merkez_x, merkez_y = (x + w // 2, y + h // 2)#x_merkez=x+w/2,y_merkez=y+h/2
            enboy = h / w  # en/boy oranı
            merkezler.append((merkez_x, merkez_y))
            alanlar.append(alan)
            oranlar.append(enboy)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)#frame'in(çerçeve)sol üst köşesinden(x,y),sağ alt köşesine(x+w,y+h)kadar olan alanı çizdiriyoruz.

    # Nesneleri takip edip sınıflandırma
    if len(merkezler) > 0:
        if len(obje_takip) == 0:  # Eğer daha önce izlenen nesne yoksa
            for i, merkez in enumerate(merkezler):
                if alanlar[i] < yaya_threshold and oranlar[i] > enboy_threshold:#belirlediğimiz maksimum yaya thresholdu ve en/boy oranı uyuyorsa yayadır.
                    obje_tipi = "Yaya"
                elif alanlar[i] > tasit_threshold:#belirlediğimiz minimum tasit thresholduna göre karar veriyoruz.
                    obje_tipi = "Tasit"
                else:
                    obje_tipi = "Belirsiz"#bu ikisine uymuyorsa belirsiz kabul ediyoruz.(Threshold>500 aralığından kaçan bazı gürültüler mesela.)

                obje_takip[sonraki_obje_İd] = (merkez, obje_tipi, 0.0)  # Başlangıç hızı 0
                sonraki_obje_İd += 1
        else:#Eğer daha önce izlenen nesne varsa.

            # Mevcut ve önceki nesneler arasında eşleşme yapıyoruz.
            obje_idleri = list(obje_takip.keys())
            object_centroids = [v[0] for v in obje_takip.values()]

            distances = dist.cdist(np.array(object_centroids), np.array(merkezler))#d(i,j)= √(xi​−xj)^2 +(yi​ −yj)^2 


            # Minimum mesafeye göre eşleştirme
            satirlar = distances.min(axis=1).argsort()
            sutunlar = distances.argmin(axis=1)[satirlar]

            kullanılan_satirlar = set()
            kullanılan_sutunlar = set()

            for (satir, sutun) in zip(satirlar, sutunlar):
                if satir in kullanılan_satirlar or sutun in kullanılan_sutunlar:
                    continue

                obje_id = obje_idleri[satir]
                onceki_konum = obje_takip[obje_id][0]
                simdiki_konum = merkezler[sutun]
                mesafe_px = np.linalg.norm(np.array(simdiki_konum) - np.array(onceki_konum))#mesafe_px=simdiki_konum-onceki_konum
                hiz = mesafe_px / hiz_aralik  # hız = mesafe_px/zaman(px/s)

                #Tip belirleme(alan,en/boy oranı ve hız bilgisine göre)
                alan = alanlar[sutun]
                enboy = oranlar[sutun]

                if alan < yaya_threshold and enboy > enboy_threshold:
                    obje_tipi = "Yaya"
                elif alan > tasit_threshold and hiz > hiz_threshold:
                    obje_tipi = "Tasit"
                else:
                    obje_tipi = "Belirsiz"

                # Güncelleme
                obje_takip[obje_id] = (simdiki_konum, obje_tipi, hiz)

                # Tipi ve hızı ekrana yazdırma
                cv2.putText(frame, f"{obje_tipi} ID {obje_id} Hiz: {hiz:.2f} px/s",
                            (simdiki_konum[0], simdiki_konum[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                kullanılan_satirlar.add(satir)
                kullanılan_sutunlar.add(sutun)

            # Yeni nesneleri ekleme
            kullanılmayan_sutunlar = set(range(distances.shape[1])) - kullanılan_sutunlar
            for sutun in kullanılmayan_sutunlar:
                if alanlar[sutun] < yaya_threshold and oranlar[sutun] > enboy_threshold:
                    obje_tipi = "Yaya"
                elif alanlar[sutun] > tasit_threshold:
                    obje_tipi = "Tasit"
                else:
                    obje_tipi = "Belirsiz"

                obje_takip[sonraki_obje_İd] = (merkezler[sutun], obje_tipi, 0.0)
                sonraki_obje_İd += 1

    # Çerçeveyi ve maske'yi gösterme
    cv2.imshow("Frame", frame)
    cv2.imshow("Maske", maske)

    # 'ESC' tuşuna basıldığında çıkış
    if cv2.waitKey(30) & 0xFF == 27:
        break

# Döngüden çıktıktan sonra toplam yaya ve tasit sayıları hesaplama
toplam_yaya = sum(1 for obj in obje_takip.values() if obj[1] == "Yaya")
toplam_tasit = sum(1 for obj in obje_takip.values() if obj[1] == "Tasit")

# Sonuçları yazdırma
print(f"Toplam Yaya: {toplam_yaya}")
print(f"Toplam Tasit: {toplam_tasit}")

# Ekran Temizleme
cap.release()
cv2.destroyAllWindows()
