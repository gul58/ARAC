# PythonAnywhere'e kurulum (PostgreSQL)

> **Önemli:** PythonAnywhere'de **PostgreSQL yalnızca ücretli planda** vardır.
> Ücretsiz hesapta Postgres yok (sadece sınırlı MySQL/SQLite).
> Bu proje PostgreSQL kullandığı için **ücretli plan + Postgres eklentisi** gerekir.

Resmi bilgi: https://help.pythonanywhere.com/pages/Postgres/

---

## 1) Hesap

1. https://www.pythonanywhere.com adresinden kayıt olun.
2. **Account** → ücretli plana geçin.
3. Postgres seçeneğini açın (disk alanı seçin) ve onaylayın.

---

## 2) PostgreSQL veritabanı

1. **Databases** → **Postgres**
2. Superuser şifresi belirleyin.
3. Postgres konsolunu açıp:

```sql
CREATE DATABASE apts_db;
CREATE USER apts WITH PASSWORD 'GUCLU_BIR_SIFRE';
ALTER ROLE apts SET client_encoding TO 'utf8';
ALTER ROLE apts SET default_transaction_isolation TO 'read committed';
ALTER ROLE apts SET timezone TO 'Europe/Istanbul';
GRANT ALL PRIVILEGES ON DATABASE apts_db TO apts;
\c apts_db
GRANT ALL ON SCHEMA public TO apts;
```

4. Databases sekmesinden not edin:
   - **Hostname** (örn. `kullanici-123.postgres.pythonanywhere-services.com`)
   - **Port** (örn. `10667`)

---

## 3) Kodu yükleyin (Bash konsolu)

PythonAnywhere → **Consoles** → **Bash**:

```bash
cd ~
git clone https://github.com/gul58/ARAC.git
cd ARAC
python3.12 -m venv .venv || python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 4) Ortam dosyası

```bash
nano ~/.env
```

Şunu yazın (değerleri kendinizinkilerle değiştirin):

```env
DJANGO_SECRET_KEY=uzun-rastgele-gizli-anahtar
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=KULLANICI.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://KULLANICI.pythonanywhere.com
POSTGRES_DB=apts_db
POSTGRES_USER=apts
POSTGRES_PASSWORD=GUCLU_BIR_SIFRE
POSTGRES_HOST=HOSTNAME.postgres.pythonanywhere-services.com
POSTGRES_PORT=10667
```

Kaydedin: `Ctrl+O`, Enter, `Ctrl+X`

---

## 5) Migrate + örnek veri

```bash
cd ~/ARAC
source .venv/bin/activate
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
```

---

## 6) Web uygulaması (WSGI)

1. **Web** sekmesi → **Add a new web app**
2. Manual configuration → Python 3.10 veya 3.12
3. **Virtualenv:** `/home/KULLANICI/ARAC/.venv`
4. **WSGI configuration file** linkine tıklayın; içeriği silip şunu yazın
   (`KULLANICI` yerine PythonAnywhere kullanıcı adınız):

```python
import sys
from pathlib import Path

project_home = "/home/KULLANICI/ARAC"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from dotenv import load_dotenv
load_dotenv(Path.home() / ".env")

from django.core.wsgi import get_wsgi_application
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
```

5. **Reload** düğmesine basın.

---

## 7) Test

Tarayıcı: `https://KULLANICI.pythonanywhere.com/giris/`

- İhale: `cagla` / `cagla123`
- Formen: `muhammet` / `formen123`

İlk girişten sonra canlıda parolaları değiştirin.

---

## Güncelleme (yeni kod gelince)

```bash
cd ~/ARAC
source .venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Web sekmesinde **Reload**.

---

## Ücretsiz hesap istiyorsanız

Ücretsiz PythonAnywhere ile bu projenin PostgreSQL hali çalışmaz.
Seçenekler:
1. Ücretli PythonAnywhere + Postgres
2. Başka hosting (Railway / Render) — ücretsiz deneme + Postgres eklentisi
