---
version: alpha
name: Alumni Portal
description: Dell 1996 kataloğundan esinlenen, Alumni Portal kimliğine uyarlanmış arayüz tasarımı.
colors:
  primary: "#18362B"
  on-primary: "#F8F7F2"
  accent: "#D9ECAC"
  canvas: "#F8F7F2"
  surface: "#FFFFFF"
  ink: "#202C25"
  muted: "#52635A"
  frame: "#101713"
  link: "#0000B8"
  alumni: "#B3BD95"
  announcements: "#E8AE9C"
  jobs: "#ABC5D5"
  applications: "#B4BCE9"
  error: "#9F252D"
typography:
  display:
    fontFamily: "Arial Black, Helvetica, Arial, sans-serif"
    fontSize: 36px
    fontWeight: 900
    lineHeight: 1.05
  heading:
    fontFamily: "Helvetica, Arial, sans-serif"
    fontSize: 20px
    fontWeight: 700
    lineHeight: 1.2
  body:
    fontFamily: "Times New Roman, Times, serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Helvetica, Arial, sans-serif"
    fontSize: 14px
    fontWeight: 700
    lineHeight: 1.35
rounded:
  none: 0px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  section: 32px
components:
  page-frame:
    backgroundColor: "{colors.frame}"
    rounded: "{rounded.none}"
    padding: "{spacing.sm}"
  top-banner:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label}"
    padding: "12px 16px"
  card-title:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    borderColor: "{colors.frame}"
    typography: "{typography.heading}"
    padding: "8px 16px"
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "10px 16px"
---

# Alumni Portal arayüz tasarımı

Bu rehber, portal ekranlarında kullanılabilecek Dell 1996 esintili bir tasarım tarif eder. Koyu çerçeve, düz renkli kartlar ve kalın sans-serif başlıklar katalog stilini yansıtır. Orman yeşili, krem ve Türkçe arayüz dili portalın marka kimliğini sürdürür. [VoltAgent Dell 1996 tasarım rehberi](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/dell-1996/DESIGN.md) · [Alumni Portal marka rehberi](./brand.md)

## Yerleşim

- Krem sayfa yüzeyini 8 px koyu çerçeveyle çevreleyin. Üst şeritte portal adı ve temel gezinme bağlantıları yer alsın.
- İçeriği en fazla 1120 px genişlikte ortalayın. Liste sayfalarında geniş ekranda dar bir filtre sütunu ve geniş bir sonuç alanı kullanın. 768 px altında filtreleri sonuçların üstüne taşıyın.
- Dar ekranlarda çerçeveyi 4 px olarak uygulayın ve gezinme öğelerinin satır atlamasına izin verin. Eylemler ve kart metinleri yatay kaydırma gerektirmeden erişilebilir olsun.
- Kartlarda ve formlarda düz yüzey, köşeli kenar ve 1 px ayırıcı çizgiler kullanın. Ana başlıkları Arial Black, uzun açıklamaları Times New Roman, form ve düğme etiketlerini Helvetica ile dizin.

## Bölüm kartları

Her kart beyaz bir başlık şeridi, koyu bir ayırıcı ve bölüm renginde düz bir gövdeden oluşur. Gövdeye kısa bir açıklama ve hedefi açıkça belirten bir bağlantı ekleyin.

| Bölüm | Kart gövdesi | Rota |
| --- | --- | --- |
| Mezunlar | Adaçayı `#B3BD95` | `/users/` |
| Duyurular | Somon `#E8AE9C` | `/announcements/` |
| İş ve staj ilanları | Gök mavisi `#ABC5D5` | `/jobs/` |
| Başvurular | Açık mor `#B4BCE9` | `/applications/` |

## Bileşenler ve etkileşim

- Birincil düğmede orman yeşili zemin ve krem metin kullanın. İkincil düğmeyi beyaz zemin ve koyu çerçeveyle gösterin. Metin bağlantıları mavi ve altı çizili olsun.
- Her form alanına görünür bir etiket ekleyin. Alan hatasını ilgili girişin yanında gösterin. Tablo başlıklarını ayırıcı çizgiyle vurgulayın ve başvuru durumlarını metinle belirtin.
- Hata sayfalarında durum kodunu, kısa açıklamayı ve ana sayfaya dönüş bağlantısını tek bir çerçeveli panelde sunun.
- Hakkımızda kartları önceki ve sonraki düğmeleriyle dönsün. Açık kartın sırasını ve başlığını gösterin. `prefers-reduced-motion` etkinse kartı anında değiştirin.
- Klavye odağı belirgin olsun. Etkileşim hedeflerini en az 44 × 44 px boyutunda tutun. Normal metinde en az 4,5:1 kontrast sağlayın.
