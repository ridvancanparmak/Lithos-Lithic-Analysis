# Lithos — Palaeolithic Lithic Analysis System

**Lithos v1.0.2** is a Windows desktop application for technological, typological and metrical analysis of Palaeolithic chipped-stone assemblages. It reads compatible Microsoft Access databases, presents hierarchical core/tool type and subtype distributions, generates charts and bilingual Word reports, and supports Turkish and English interfaces.

> **Status:** **v1.0.2 — Pre-release.** Lithos is an evolving research software project. Windows Setup and Portable packages are available below.

## Download Lithos for Windows / Lithos'u Windows için indir

**Available version: v1.0.2 — Initial Windows Release (Pre-release)**

| Package / Paket | Direct download / Doğrudan indir |
| --- | --- |
| **Windows Setup** — standard installer / normal kurulum | **[Download Lithos v1.0.2 Setup (.exe)](https://github.com/ridvancanparmak/Lithos-Lithic-Analysis/releases/download/v1.0.2/Lithos_v1.0.2_Setup.exe)** |
| **Windows Portable** — no installation required / kurulumsuz | **[Download Lithos v1.0.2 Portable (.zip)](https://github.com/ridvancanparmak/Lithos-Lithic-Analysis/releases/download/v1.0.2/Lithos_v1.0.2_Portable.zip)** |

[**Release notes and all downloads / Sürüm notları ve tüm indirmeler**](https://github.com/ridvancanparmak/Lithos-Lithic-Analysis/releases/tag/v1.0.2)

**EN:** For Setup, download the `.exe` and run it on Windows 10/11 (64-bit). For Portable, extract the **entire ZIP** and launch `Lithos_v1_0_2.exe` from the extracted folder; do not move the executable by itself. Compatible Microsoft Access/ACE drivers may be necessary for database operations. The current release is a **pre-release** and has not been independently verified on every Windows configuration. The archaeological source records are not included.

**TR:** Kurulum için `.exe` dosyasını indirip Windows 10/11 (64-bit) üzerinde çalıştırın. Portable sürümde **ZIP'in tamamını çıkarın** ve klasörün içindeki `Lithos_v1_0_2.exe` dosyasını açın; EXE'yi tek başına taşımayın. Veritabanı işlemleri için uygun Microsoft Access/ACE sürücülerine ihtiyaç duyulabilir. Bu sürüm **ön sürümdür (Pre-release)**; her Windows yapılandırmasında bağımsız olarak doğrulanmış değildir. Özgün arkeolojik araştırma kayıtları dağıtıma dahil değildir.

> **Note / Not:** GitHub's automatically generated **Source code (zip)** is **not** the Windows Portable application. Use the Portable download above. / GitHub'ın otomatik oluşturduğu **Source code (zip)** dosyası çalışan Portable sürüm değildir; yukarıdaki Portable bağlantısını kullanın.

## Create a blank Access database / Boş Access veritabanı oluşturma

**TR —** Araştırmacıların ayrı bir Access dosyası indirmesi zorunlu değildir. **Lithos v1.0.2**, kurulum paketine dahil edilmiş boş şablonları kullanarak uygulama içinden veritabanı oluşturmayı destekler:

1. Lithos'u açın ve soldaki **Veritabanı** sekmesine geçin.
2. **+ Yeni Veritabanı** düğmesine tıklayın.
3. **Türkçe** veya **English** şablonunu seçip onaylayın.
4. Yeni `.accdb` dosyasını kaydedeceğiniz konumu ve dosya adını belirleyin.
5. Verilerinizi **Microsoft Access** üzerinden kaydedin; ardından dosyanızı Lithos'ta açıp analiz edin.

**EN —** You do not need to download a separate database file if the blank templates were packaged with Lithos:

1. Open Lithos and go to the **Database** page.
2. Click **+ Create Database**.
3. Choose the **Türkçe** or **English** blank template.
4. Select the destination and filename for the new `.accdb` file.
5. Enter or edit archaeological records using **Microsoft Access**, then open the database in Lithos for analysis.

**Compatibility / Uyumluluk:** In **v1.0.2**, the database creation feature uses blank templates derived from the Gürbelen-18 schema. These are **starter templates**, not a universal archaeological data model. Other research databases with different structures are **not yet automatically imported or mapped**. Creation requires the relevant blank template to be present in the installed/portable distribution; Access/ACE drivers may also be necessary. / Bu sürüm farklı tablo ve sütun yapılarını otomatik eşleştirmez; boş şablonların dağıtım paketinde bulunması gerekir. Uygun Access/ACE sürücüsüne ihtiyaç duyulabilir.

**Data protection / Veri güvenliği:** Blank templates must contain **no original research records, identifying metadata, sensitive information, or linked external data**. / Boş şablonlar özgün araştırma kayıtlarını, kişisel verileri veya dış bağlantılı verileri içermemelidir.

## Application screenshot / Uygulama ekran görüntüsü

![Actual Lithos Windows desktop application interface showing typological analysis and visual results](docs/lithos_screenshot.jpg)

*Actual screenshot of the Lithos desktop application (Turkish interface). The archaeological research database shown in the screenshot is **not included** in this public repository.*  
*Lithos masaüstü uygulamasının gerçek ekran görüntüsü (Türkçe arayüz). Görselde kullanılan arkeolojik araştırma veritabanı **bu açık depoda paylaşılmamaktadır**.*

## Research origins and vision / Araştırma temeli ve hedefi

**EN —** Lithos began as a research-driven software initiative based on the Microsoft Access database used in Rıdvan Can Parmak's master's research on the **Middle Palaeolithic chipped-stone assemblage of Gürbelen Tepe (Korkuteli, Antalya, Türkiye)**. This case study provided the initial reference for database structure, terminology and analytical workflows; **the original archaeological records are not included in this public repository**.

The project's broader objective is to support **data standardization in Palaeolithic archaeology**, with particular emphasis on consistent documentation of lithic assemblages, transparent technological and typological classification, bilingual terminology, structured data management and reproducible, comparable analyses across research projects. Lithos is an **evolving project**: its current capabilities represent a starting point, not a universal or finalized classification standard. Future development may extend data structures, validation, interoperability, visualization and analytical methods in consultation with researchers.

**TR —** Lithos, **Korkuteli (Antalya) Gürbelen Tepe Orta Paleolitik Çağ yontmataş buluntu topluluğu** üzerine yürüttüğüm yüksek lisans araştırmasında kullandığım Microsoft Access veritabanını başlangıç örneği alan, araştırma odaklı bir yazılım girişimi olarak ortaya çıkmıştır. Bu örnek; veritabanı yapısı, terminoloji ve analiz iş akışlarının ilk geliştirme aşamasına temel oluşturmuştur. **Özgün arkeolojik buluntu kayıtları bu açık depoda paylaşılmamaktadır.**

Projenin daha geniş hedefi, **Paleolitik Çağ arkeolojisinde veri standardizasyonuna** katkıda bulunmaktır. Lithos; yontmataş buluntuların tutarlı belgelenmesini, teknolojik ve tipolojik sınıflandırmaların daha sistematik yürütülmesini, iki dilli terminoloji kullanımını, yapılandırılmış veri yönetimini ve farklı araştırmalar arasında karşılaştırılabilir analizleri desteklemeyi amaçlar. **Lithos gelişime açık bir projedir**; mevcut yapı, tamamlanmış ve evrensel bir sınıflandırma standardı olarak sunulmamaktadır. Gelecek aşamalarda veri doğrulama, birlikte çalışabilirlik, görselleştirme, yeni veri alanları ve analiz yöntemlerinin geliştirilmesi hedeflenmektedir.

## Features / Özellikler

- Turkish / English (TR / ENG) interface and Word reporting / Türkçe–İngilizce arayüz ve Word raporları
- Hierarchical core, tool type and subtype analysis / Çekirdek, alet tipi ve alt tipine dayalı hiyerarşik analiz
- Frequency, percentages, metrical statistics, bar and pie charts / Frekans, yüzde, ölçüsel istatistikler, çubuk ve pasta grafikler
- Dark user interface with responsive panels / Koyu temalı, farklı pencere boyutlarına uyumlu arayüz
- Windows portable build and optional Inno Setup installer / Portable ve kurulabilir Windows paketleri

## Important: databases / Veritabanları

**Research records are not published here.** The original `GURBELEN-18.accdb`, any derived research database, and user reports are excluded from the public repository. The two blank Access template databases are likewise not included in this source archive.

This version's template-building script derives two blank `.accdb` files from the **original GURBELEN-18 Access schema** on a Windows PC with a compatible Access/ACE/DAO installation. It is not a replacement database schema. You need a source database that you are authorized to use in order to run the template-generation script. See `KULLANIM_TR_EN.md` for the details.

**Araştırma kayıtları yayımlanmıyor.** `GURBELEN-18.accdb` ve diğer gerçek buluntu verileri bu depoda yok. Boş şablonlar, yetkili olduğunuz özgün Gürbelen şeması temel alınarak Windows ortamında üretiliyor.

## Requirements / Gereksinimler

- Windows 10/11, 64-bit
- Python 3.12–3.14 for building (Python 3.15 alone is not the supported build environment)
- Microsoft Access/ACE/DAO components to create and use the `.accdb` templates (matching architecture)
- Inno Setup for the optional Setup.exe

## Building on Windows / Windows derlemesi

1. Download or clone this repository (do not mix with old Lithos hotfix folders).
2. Place your **authorized original** `GURBELEN-18.accdb` next to the `.bat` files if you intend to generate templates; keep your own secure backup.
3. Run `00_HEPSINI_HAZIRLA.bat` for the guided build, or `01_ACCESS_SABLONLARI_OLUSTUR.bat` and `02_PORTABLE_OLUSTUR.bat` separately.
4. Only after the portable startup test passes, run `03_KURULUM_OLUSTUR.bat` to build the optional Windows installer.
5. Never commit the original `.accdb`, generated `Templates/*.accdb`, `dist/`, reports or personal data back to this repository.

**Note:** The source package does not contain a prebuilt EXE or Setup.exe. No Windows build is claimed to have been tested in this environment.

## Structure / Klasörler

- `lithos/` — application, analysis, reporting and data access / uygulama kodu
- `assets/` — icons, flags and header artwork / simgeler ve arayüz görselleri
- `veri_sozlugu/` — bilingual terminology mappings / iki dilli terim sözlükleri
- `tests/` — automated tests / otomatik testler
- `Templates/` — documentation for empty Access templates / boş Access şablon açıklamaları
- `docs/` — application screenshot and documentation / uygulama ekran görüntüsü ve belgeler
- `*.bat`, `installer.iss` — Windows build files / Windows derleme dosyaları

## Developer / Geliştirici

Rıdvan Can PARMAK — archaeology, Palaeolithic research and lithic technology.

## License / Lisans

**No open-source license has been selected yet.** Publication of source code on GitHub does not, by itself, give others permission to reuse, redistribute or modify it. If you intend to make Lithos open source, add an explicit license after reviewing the code and third-party asset rights. Until then, all rights are reserved, except as otherwise required by applicable law.

See `GITHUB_YAYINLAMA_REHBERI_TR.md` for publication steps.
