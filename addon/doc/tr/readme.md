# ffAraçları

Multimedya dosyalarının işlenebilmesi için ffmpeg programının araç seti.

[Gerardo Kessler](http://gera.ar/sonido/sobremi.php)  

[ffmpeg programına dayalı](https://ffmpeg.org/)  

İkili dosyaları indirin: <https://github.com/yt-dlp/FFmpeg-Builds/wiki/Latest>

Önemli: Bu modül FF ikili dosyalarını temel alır, bu nedenle bu dosyaların indirilmesi önemlidir. Eklenti, bunları indirmeyi ve doğru yere kaydetmeyi önerir, ancak kullanıcı bunu, ffmpeg.exe ve ffplay.exe dosyalarının bulunduğu bin klasörünü eklentinin kök dizinine kopyalayarak da yapabilir: 

    %AppData%\nvda\addons\ffTools\globalPlugins\ffTools

## Eklenti Komutları:

* Ses veya video dosyasına odaklanarak önizleme; Atanmadı
* Komut katmanını etkinleştirme; Atanmadı

### önizleme komutları

Önizleme etkinleştirildiğinde, aşağıdaki komutlar izleme penceresinde çalışır:

* Boşluk çubuğu; oynatmayı duraklatır ve devam ettirir.
* Sayfa beslemesi; Baştan oynat
* Sol ok; zaman çizelgesinde geri gider
* sağ ok; Zaman çizelgesinde ileri gider
* Yukarı ok; oynatma sesini artırır
* Aşağı ok; oynatma sesini azaltır
* Escape; pencereyi kapatır

### komut katmanı

* f1; Bu belgeyi varsayılan tarayıcıda açar
* F; Odaklı dosyanın hacmini, biçimini ve bit hızını değiştirmemize izin veren bir pencereyi etkinleştirir
* C; Hızı değiştirmemize, dosyanın başını ve sonunu kesmemize izin veren bir pencereyi etkinleştirir.foco
* l; Bir toplu dönüştürme penceresini etkinleştirir

## kırpma

Komut katmanını etkinleştirmek ve c harfine basmak, hız ve kırpma penceresini etkinleştirir.
"Dosya hızını değiştir" onay kutusu işaretlenirse, yalnızca seçilecek yüzdeler listesi görüntülenir.  

Aksi takdirde, kesimin başlangıcını ve bitişini seçmek için 2 adet düzenlenebilir kutu mevcuttur. Dosyanın ilk 10 saniyesi kırpılacaksa çerçeve 00:10 olarak düzenlenmelidir. Dakikalar için 2 ve saniyeler için 2 rakamının biçimine uyulması önemlidir.
Nihai kesim kutusundaki etiket, dosyanın toplam süresini belirtir ve bu süre aynı zamanda alanın değerine de yansır.
Dosyanın son 10 saniyesini kesmek için, mevcut değeri saniyeler çıkarılmış olarak yazarak kutuyu düzenlemeniz gerekir. Dosyanın süresi 03:07 ise, 02:57 olmalıdır.

### toplu dönüştürme

Bu seçenek, bir dizindeki tüm mevcut FFMpeg destekli dosyaları dönüştürmenize olanak tanır.  

Komut katmanı etkinleştirildiğinde ve l tuşuna basıldığında, aşağıdaki seçeneklerin yer aldığı bir diyalog penceresi görüntülenir:

* Klasör Yolu: Dosyaların bulunduğu klasörün yolu burada görüntülenir.
* Gözat: Dönüştürülecek dosyalara sahip bir klasör aramak için tipik Windows iletişim kutusunu açan düğme.
* Dönüştürülecek biçim: Kullanılabilir çıktı biçimlerinin listesi.
* Ses düzeyini normalleştir: Sesi -16 LUFS ve 11 LRA hedef ses yüksekliği düzeyine normalleştirmenizi sağlar.
Loudnorm komutunun yalnızca mp3 biçimindeki ve ffmpeg tarafından desteklenen diğer biçimlerdeki ses dosyalarıyla çalıştığını unutmamak önemlidir.
* Bit Hızı: Değeri desteklenen biçimlerde atamanıza izin verir.

Dönüştürme komutları arka planda kabuk aracılığıyla yürütülür. Yumuşak ve sabit bir ses işlemeyi temsil eder, tamamlandıktan sonra işlemin tamamlandığını bildiren kalıcı bir iletişim kutusu etkinleştirilir.
Dönüştürülen dosyalar, seçilen dizindeki dönüştürülen klasöre kaydedilir.

### üçüncü taraf lisansları

[git/FFMpeg git özeti](https://git.ffmpeg.org/ffmpeg.git)
