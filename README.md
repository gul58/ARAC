# Araç Görev Programı (APTS)

Kocaeli Büyükşehir Belediyesi Yol ve Bakım Dairesi için **Kiralık Araç Görev Emri** sistemi.

Django **5.2 LTS** + **PostgreSQL** + Bootstrap 5 + Django Templates.

## Roller

| Rol | Kullanıcı (örnek) | Parola | Yetki |
|-----|-------------------|--------|--------|
| İhale | `cagla` | `cagla123` | Bölge, firma, formen, araç, şoför yönetimi |
| Formen | `muhammet` | `formen123` | Kendi bölgesindeki görev emirleri (CRUD) |
| Formen | `m.yanik` | `formen123` | Kendi bölgesindeki görev emirleri (CRUD) |

## Gereksinimler

- Python 3.12+
- Veritabanı:
  - **Yerel (kolay):** SQLite — ekstra kurulum yok (`DB_ENGINE=sqlite`)
  - **Canlı / üretim:** PostgreSQL 14+

## Kurulum (Windows — PostgreSQL olmadan)

1. https://github.com/gul58/ARAC adresinden **Code → Download ZIP** ile indirip açın.
2. PowerShell'de proje klasörüne girin:

```powershell
cd C:\Projeler\ARAC
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

`.env` içinde şunun olduğundan emin olun:

```env
DB_ENGINE=sqlite
```

```powershell
python manage.py migrate
python manage.py seed_data
python manage.py runserver 8765
```

Tarayıcı: http://127.0.0.1:8765/giris/

## Kurulum (PostgreSQL ile)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` içinde `DB_ENGINE=postgresql` yapın. PostgreSQL'de:

```sql
CREATE USER apts WITH PASSWORD 'apts123' CREATEDB;
CREATE DATABASE apts_db OWNER apts;
GRANT ALL ON SCHEMA public TO apts;
```

```bash
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8765
```

## Ortam değişkenleri (`.env`)

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DB_ENGINE` — `sqlite` veya `postgresql`
- `POSTGRES_*` — yalnızca PostgreSQL kullanılırken

## Özellikler

### İhale
- Bölge / Firma / Formen / Araç / Şoför ekleme, düzenleme, silme
- Plaka ve isim benzersizliği, asıl/yedek formen ayrımı

### Formen
- Yalnızca kendi bölgesindeki araçlar ve firmalar
- Görev emri kayıt, listeleme, düzenleme, silme
- Araç seçiminde asıl şoför varsayılan; yedek şoförler seçilebilir
- Varış > Çıkış kontrolü (frontend + backend)
- Başka bölgeye ait görev emrine URL ile erişim engellenir

## Proje yapısı

```
config/          # Django ayarları
fleet/           # Modeller, formlar, görünümler, şablonlar
static/fleet/css # Uygulama stilleri
templates/       # Ortak şablonlar
```
