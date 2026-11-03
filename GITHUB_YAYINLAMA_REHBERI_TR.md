# Lithos'u GitHub'da yayımlama

## 1. GitHub deposu aç

1. https://github.com/new adresine git ve hesabınla giriş yap.
2. Repository name: `Lithos-Lithic-Analysis` (öneri).
3. Description: `Bilingual Palaeolithic lithic analysis and reporting desktop application (TR/EN).`
4. **Public** seçersen kaynak kod herkes tarafından görüntülenebilir. İlk kontrol için **Private** ile başlamak istersen daha sonra Public yapabilirsin.
5. Bu ZIP'in içinde README ve .gitignore bulunduğu için GitHub'da yeni README, .gitignore veya LICENSE seçme. **Create repository**.

## 2. Dosyaları yükle (tarayıcıdan)

1. `Lithos_GitHub_Hazir_Kaynak_Kod.zip` dosyasını bilgisayarında çıkar.
2. GitHub'da yeni deponun ana sayfasında **uploading an existing file** veya **Add file → Upload files** seç.
3. ZIP dosyasının kendisini değil, **çıkardığın klasörün içindeki dosyaları ve alt klasörleri** yükle. `README.md`, `.gitignore`, `lithos/`, `assets/`, `tests/` vb. deponun kökünde görünmeli.
4. Commit mesajı: `Initial public source release of Lithos v1.0.2`.
5. **Commit changes**.

GitHub tarayıcı yüklemesinin sınırları nedeniyle gerekirse GitHub Desktop kullanabilirsin: https://desktop.github.com/.

## 3. Son kontrol (Public yapmadan önce)

- `GURBELEN-18.accdb` **YOK**.
- `Templates/*.accdb` **YOK** (public yayımlamayı ayrıca değerlendirmeden paylaşma).
- `dist/`, `build/`, özel raporlar, kişisel CSV/XLSX/DOCX, `*.exe` **YOK**.
- README başta, ekran resmi ise **tasarım referansı** olarak açıklanıyor.
- Uygulamanın Hakkında bölümünde geliştirici e-posta adresi yer alıyor; herkese açık olmasını isteyip istemediğini kontrol et.
- Lisansı henüz seçmediysen `LICENSE` ekleme. Açık kaynak olmasını istiyorsan MIT, GPL-3.0 vb. lisansları ayrı değerlendir.

## 4. İndirilebilir Windows sürümü (sonraki adım)

Windows'ta **başlatılması test edilmiş** `Setup.exe` ve/veya bütün portable klasörün ZIP'i hazır olunca GitHub deposunda **Releases → Draft a new release** yolunu kullan. Etiket `v1.0.2` olabilir. EXE/ZIP dosyalarını **source code dosyalarının arasına değil**, Release bölümüne ekle.

**Önemli:** Bu kaynak ZIP'i hazır Windows kurulum paketi olarak tanıtma. Access/ACE sürücü gereksinimini ve boş veritabanlarının kaynağını belgede açıkça belirt.
