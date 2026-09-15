# Araç Görev Programı (APTS)

Kocaeli Büyükşehir Belediyesi Yol ve Bakım Dairesi için **Kiralık Araç Görev Emri** sistemi.

Django **5.2 LTS** + **SQLite** (varsayılan) / isteğe bağlı PostgreSQL + Bootstrap 5.

## Roller

| Rol | Kullanıcı (örnek) | Parola | Yetki |
|-----|-------------------|--------|--------|
| İhale | `cagla` | `cagla123` | Bölge, firma, formen, araç, şoför yönetimi |
| Formen | `muhammet` | `formen123` | Kendi bölgesindeki görev emirleri (CRUD) |
| Formen | `m.yanik` | `formen123` | Kendi bölgesindeki görev emirleri (CRUD) |

## Gereksinimler

- Python 3.12+ (3.10+ de olur)
- Veritabanı: **SQLite** (varsayılan, ekstra kurulum yok)

## Kurulum (Windows)

```powershell
cd C:\Projeler\ARAC
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver 8765
```

`.env` içinde `DB_ENGINE=sqlite` olsun.

Tarayıcı: http://127.0.0.1:8765/giris/

## PostgreSQL kullanmak isterseniz

`.env`:

```env
DB_ENGINE=postgresql
POSTGRES_DB=apts_db
POSTGRES_USER=apts
POSTGRES_PASSWORD=apts123
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

## Ortam değişkenleri

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DB_ENGINE` — `sqlite` (varsayılan) veya `postgresql`

## PythonAnywhere

[DEPLOY_PYTHONANYWHERE.md](DEPLOY_PYTHONANYWHERE.md) — ücretsiz hesap + SQLite.

## Repolar

- Origin: https://cursor.com/codebase/mer-g-lsoy/task-master
- GitHub: https://github.com/gul58/ARAC
