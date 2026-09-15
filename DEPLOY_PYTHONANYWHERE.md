# PythonAnywhere'e kurulum (SQLite — ücretsiz hesap uyumlu)

Bu proje varsayılan olarak **SQLite** kullanır. PythonAnywhere ücretsiz hesapta çalışır.

---

## 1) Hesap

https://www.pythonanywhere.com → ücretsiz hesap oluşturun.

---

## 2) Kodu yükleyin (Bash konsolu)

**Consoles → Bash:**

```bash
cd ~
git clone https://github.com/gul58/ARAC.git
cd ARAC
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> GitHub güncel değilse ZIP yükleyin veya güncel commit’i push ettikten sonra `git pull` yapın.

---

## 3) Ortam dosyası

```bash
nano ~/ARAC/.env
```

(`KULLANICI` = PythonAnywhere kullanıcı adınız)

```env
DJANGO_SECRET_KEY=uzun-rastgele-gizli-anahtar
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=KULLANICI.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://KULLANICI.pythonanywhere.com
DB_ENGINE=sqlite
```

Kaydet: `Ctrl+O`, Enter, `Ctrl+X`

---

## 4) Veritabanı + statik dosyalar

```bash
cd ~/ARAC
source .venv/bin/activate
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
```

`db.sqlite3` proje klasöründe oluşur.

---

## 5) Web uygulaması

1. **Web** → **Add a new web app**
2. **Manual configuration** → Python **3.10** (veya mevcut sürüm)
3. **Virtualenv:** `/home/KULLANICI/ARAC/.venv`
4. **WSGI configuration file** linkine tıklayın; içeriği silip şunu yazın:

```python
import os
import sys
from pathlib import Path

project_home = "/home/KULLANICI/ARAC"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from dotenv import load_dotenv
load_dotenv(Path(project_home) / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. **Reload**

---

## 6) Test

`https://KULLANICI.pythonanywhere.com/giris/`

- İhale: `cagla` / `cagla123`
- Formen: `muhammet` / `formen123`

Canlıda parolaları değiştirin.

---

## Güncelleme

```bash
cd ~/ARAC
source .venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Web → **Reload**

---

## Notlar

- Ücretsiz hesapta site bir süre kullanılmazsa uykuya geçebilir; ilk istekte uyanır.
- SQLite tek dosyadır; yoğun eşzamanlı yazım için sınırlıdır. İleride Postgres’e geçmek için `.env` içinde `DB_ENGINE=postgresql` yeterlidir (ücretli plan gerekir).
