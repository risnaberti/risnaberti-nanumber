# 📦 Risnaberti Nanumber

![PyPI version](https://img.shields.io/pypi/v/risnaberti-nanumber.svg?style=flat-square)
![Python version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/github/license/risnaberti/nanumber?style=flat-square)
![Status](https://img.shields.io/pypi/status/risnaberti-nanumber?style=flat-square)

> **Universal auto-number generator library by Risna Berti (Nana)**  
> Aman, fleksibel, dan mudah diintegrasikan ke **FastAPI**, **Django**, **Flask**, atau framework lainnya.

---

## ✨ Fitur Utama

✅ Format fleksibel: `#SUP-{y}{number}` → `#SUP-250001`  
✅ Reset otomatis per tahun / bulan  
✅ Thread-safe (aman dari race condition)  
✅ Multi-storage (Memory, SQLite, PostgreSQL, MySQL)  
✅ Siap integrasi ke FastAPI / Django  
✅ Terinspirasi dari *Laravel Nanamber*

---

## 🧱 Instalasi

```bash
pip install risnaberti-nanumber
```

---

## ⚙️ Penggunaan Dasar

```python
from risnaberti.nanumber import NumberGenerator, MemoryStorage

# Gunakan penyimpanan in-memory
storage = MemoryStorage()
gen = NumberGenerator(storage)

print(gen.generate("supplier", "#SUP-{y}{number}"))
# 👉 #SUP-250001
```

---

## 💾 Menggunakan SQLite / PostgreSQL

```python
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

# Gunakan SQLite
storage = SQLAlchemyStorage("sqlite:///nanumber.db")

# Atau PostgreSQL
# storage = SQLAlchemyStorage("postgresql+psycopg2://user:password@localhost/nanumber_db")

gen = NumberGenerator(storage)
print(gen.generate("invoice", "INV-{Y}-{number:04d}"))
# 👉 INV-2025-0001
```

> **Catatan:**  
> Nanumber otomatis membuat tabel `auto_numbers` bila belum ada.  
> Counter di-reset otomatis ketika tahun berganti.

---

## ⚙️ Integrasi dengan FastAPI

### 1️⃣ Instal dependency

```bash
pip install fastapi[all] risnaberti-nanumber
```

### 2️⃣ Tambahkan endpoint

```python
# app/main.py
from fastapi import FastAPI
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

app = FastAPI()

storage = SQLAlchemyStorage("sqlite:///nanumber.db")
gen = NumberGenerator(storage)

@app.get("/generate/{entity}")
def generate_number(entity: str):
    format_map = {
        "supplier": "#SUP-{y}{number:04d}",
        "invoice": "INV-{Y}-{number:05d}",
    }
    fmt = format_map.get(entity, "{Y}{number:04d}")
    return {"entity": entity, "number": gen.generate(entity, fmt)}
```

### 3️⃣ Jalankan server
```bash
uvicorn app.main:app --reload
```

Lalu buka:
- 🔹 [http://localhost:8000/generate/supplier](http://localhost:8000/generate/supplier)  
- 🔹 [http://localhost:8000/generate/invoice](http://localhost:8000/generate/invoice)

---

## 🧩 Integrasi dengan Django

### 1️⃣ Tambahkan ke `requirements.txt`

```
risnaberti-nanumber
```

### 2️⃣ Gunakan di `signals.py`

```python
# apps/supplier/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Supplier
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

storage = SQLAlchemyStorage("sqlite:///db.sqlite3")
gen = NumberGenerator(storage)

@receiver(pre_save, sender=Supplier)
def generate_supplier_code(sender, instance, **kwargs):
    if not instance.code:
        instance.code = gen.generate("supplier", "#SUP-{y}{number}")
```

Sekarang setiap kali buat supplier baru, field `code` otomatis terisi.

---

## 🔢 Contoh Format Nomor

| Template | Hasil | Keterangan |
|-----------|--------|------------|
| `#SUP-{y}{number}` | `#SUP-250001` | Tahun 2 digit |
| `INV-{Y}-{number:05d}` | `INV-2025-00001` | Tahun penuh + padding |
| `{m}{number:03d}` | `11001` | Reset otomatis tiap tahun |

---

## ⚙️ Konfigurasi via YAML / ENV (opsional)

Buat file `.nanumber.yml` di root project:

```yaml
default_format: "#SUP-{y}{number}"
entities:
  supplier: "#SUP-{y}{number:04d}"
  invoice: "INV-{Y}-{number:05d}"
```

---

## 🧠 Uji Multi-thread (Concurrency Test)

```python
import threading
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

storage = SQLAlchemyStorage("sqlite:///test.db")
gen = NumberGenerator(storage)

def worker():
    print(gen.generate("supplier", "#SUP-{y}{number:04d}"))

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
```

Output:
```
#SUP-250001
#SUP-250002
#SUP-250003
...
```

Semua hasil unik — tidak ada duplikasi walaupun 10 thread berjalan bersamaan 🚀

---

## 📁 Struktur Package

```
risnaberti/
  nanumber/
    ├── core.py
    ├── exceptions.py
    ├── config.py
    └── storage/
        ├── base.py
        ├── memory.py
        ├── sqlite.py
        └── sqlalchemy_storage.py
```

---

## 📄 Lisensi
MIT © 2025 **Risna Berti**

---

## 💬 Kontribusi
Pull request selalu terbuka 🎉  
Jika kamu menemukan bug atau ide fitur baru, silakan buat issue di GitHub:

👉 [https://github.com/risnaberti/nanumber](https://github.com/risnaberti/nanumber)

---

## 🌟 Dukungan & Kontak
Jika kamu menggunakan library ini di project kamu, kasih bintang di GitHub ⭐  

📧 **Email:** your@email.com  
🐙 **GitHub:** [@risnaberti](https://github.com/risnaberti)

---

✨ *Made with ❤️ by Risna Berti*  
> _"Because numbering should be smart, safe, and beautiful."_
