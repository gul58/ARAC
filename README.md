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
- PostgreSQL 14+

## Kurulum

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
```

PostgreSQL'de veritabanı oluşturun:

```sql
CREATE USER apts WITH PASSWORD 'apts123' CREATEDB;
CREATE DATABASE apts_db OWNER apts;
GRANT ALL ON SCHEMA public TO apts;
```

```bash
python manage.py migrate
python manage.py seed_data
python manage.py runserver 8765
```

Tarayıcı: http://127.0.0.1:8765/giris/

## Ortam değişkenleri (`.env`)

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`

## Özellikler

### İhale
- Bölge / Firma / Formen / Araç / Şoför ekleme, düzenleme, silme

### Formen
- Kendi bölgesindeki görev emirleri (kayıt, liste, düzenle, sil)
- Araç / şoför / çıkış-giriş saatleri
- Varış > Çıkış kontrolü (frontend + backend)

## Repolar

- Origin: https://cursor.com/codebase/mer-g-lsoy/task-master
- GitHub: https://github.com/gul58/ARAC
