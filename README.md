# 📦 Risnaberti Nanumber

![PyPI version](https://img.shields.io/pypi/v/risnaberti-nanumber.svg?style=flat-square)
![Python version](https://img.shields.io/badge/python-3.7%2B-blue?style=flat-square)
![License](https://img.shields.io/github/license/risnaberti/nanumber?style=flat-square)
![Status](https://img.shields.io/pypi/status/risnaberti-nanumber?style=flat-square)

> **Universal auto-number generator library by Risna Berti**  
> Aman, fleksibel, dan mudah diintegrasikan ke **FastAPI**, **Django**, **Flask**, atau framework lainnya.

---

## ✨ Fitur Utama

✅ **Format fleksibel** dengan placeholder yang mudah  
✅ **Auto-reset** per tahun otomatis  
✅ **Thread-safe & Process-safe** - aman dari race condition  
✅ **Multi-database support** - SQLite, PostgreSQL, MySQL  
✅ **Production-ready** - siap pakai untuk aplikasi skala besar  
✅ **Zero configuration** - langsung pakai tanpa setup rumit

---

## 🚀 Instalasi

```bash
pip install risnaberti-nanumber
```

**Untuk PostgreSQL:**
```bash
pip install risnaberti-nanumber psycopg2-binary
```

**Untuk MySQL:**
```bash
pip install risnaberti-nanumber pymysql
```

---

## 🎯 Quick Start

### Basic Usage

```python
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

# Setup storage (SQLite untuk demo)
storage = SQLAlchemyStorage("sqlite:///nanumber.db")
gen = NumberGenerator(storage)

# Generate number dengan template
code = gen.generate(
    key="supplier",
    template="SUP-{y}{number}",
    pad=4
)
print(code)  # SUP-250001
```

### Using Templates (Recommended)

```python
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

storage = SQLAlchemyStorage("sqlite:///nanumber.db")

# Define templates sekali di awal
gen = NumberGenerator(
    storage=storage,
    templates={
        "supplier": {
            "template": "SUP-{y}{number}",
            "pad": 4,
        },
        "invoice": {
            "template": "INV-{Y}-{number}",
            "pad": 5,
        },
        "purchase": {
            "template": "PO-{y}{m}{number}",
            "pad": 3,
        }
    }
)

# Sekarang tinggal panggil dengan key
print(gen.generate("supplier"))   # SUP-250001
print(gen.generate("invoice"))    # INV-2025-00001
print(gen.generate("purchase"))   # PO-2511001
```

---

## 📋 Format Placeholders

| Placeholder | Output | Deskripsi |
|------------|--------|-----------|
| `{Y}` | `2025` | Tahun 4 digit |
| `{y}` | `25` | Tahun 2 digit |
| `{m}` | `01`-`12` | Bulan 2 digit |
| `{d}` | `01`-`31` | Tanggal 2 digit |
| `{H}` | `00`-`23` | Jam 2 digit |
| `{M}` | `00`-`59` | Menit 2 digit |
| `{S}` | `00`-`59` | Detik 2 digit |
| `{number}` | `0001` | Nomor urut auto-increment |

### Contoh Format

```python
# Tahun 2 digit + nomor
"SUP-{y}{number}"  → SUP-250001

# Tahun penuh + separator + nomor
"INV-{Y}-{number}"  → INV-2025-00001

# Dengan tanggal
"TRX-{Y}{m}{d}-{number}"  → TRX-20251113-0001

# Custom prefix
"CUST-{y}-{number}"  → CUST-25-00001
```

**PENTING:** Padding diatur via parameter `pad`, bukan di template!

```python
# ❌ SALAH - Ini akan error
gen.generate("invoice", "INV-{number:05d}")

# ✅ BENAR - Gunakan parameter pad
gen.generate("invoice", "INV-{number}", pad=5)
```

---

## 💾 Storage Options

### 1️⃣ MemoryStorage (Development/Testing)

```python
from risnaberti.nanumber import NumberGenerator, MemoryStorage

storage = MemoryStorage()
gen = NumberGenerator(storage)

code = gen.generate("test", "TEST-{number}", pad=4)
print(code)  # TEST-0001
```

**Karakteristik:**
- ✅ Cepat, tidak butuh database
- ❌ Data hilang saat restart
- 🎯 **Use case:** Testing, demo, unit tests

---

### 2️⃣ SQLAlchemyStorage (Production)

#### SQLite (Simple projects)

```python
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

storage = SQLAlchemyStorage("sqlite:///nanumber.db")
gen = NumberGenerator(storage)
```

**Karakteristik:**
- ✅ File-based, mudah setup
- ⚠️ Concurrency terbatas (single process recommended)
- 🎯 **Use case:** Small apps, prototypes, single-server

---

#### PostgreSQL (Production recommended)

```python
storage = SQLAlchemyStorage(
    "postgresql://user:password@localhost:5432/mydb"
)
gen = NumberGenerator(storage)
```

**Karakteristik:**
- ✅ Excellent concurrency (row-level locking)
- ✅ Multi-process safe (Gunicorn, Celery, etc)
- ✅ Production-grade reliability
- 🎯 **Use case:** Production apps, microservices, high-traffic

---

#### MySQL/MariaDB

```python
storage = SQLAlchemyStorage(
    "mysql+pymysql://user:password@localhost:3306/mydb"
)
gen = NumberGenerator(storage)
```

**Karakteristik:**
- ✅ Good concurrency support
- ✅ Wide compatibility
- 🎯 **Use case:** Production apps, existing MySQL infrastructure

---

## 🔧 Integrasi dengan Framework

### FastAPI Integration

```python
# app/main.py
from fastapi import FastAPI, Depends
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

app = FastAPI()

# Initialize once (singleton pattern)
_storage = None
_generator = None

def get_generator() -> NumberGenerator:
    global _storage, _generator
    if _generator is None:
        _storage = SQLAlchemyStorage("sqlite:///nanumber.db")
        _generator = NumberGenerator(
            storage=_storage,
            templates={
                "supplier": {"template": "SUP-{y}{number}", "pad": 4},
                "invoice": {"template": "INV-{Y}-{number}", "pad": 5},
            }
        )
    return _generator

@app.post("/suppliers")
async def create_supplier(gen: NumberGenerator = Depends(get_generator)):
    supplier_code = gen.generate("supplier")
    return {"code": supplier_code}

@app.post("/invoices")
async def create_invoice(gen: NumberGenerator = Depends(get_generator)):
    invoice_number = gen.generate("invoice")
    return {"number": invoice_number}

@app.get("/generate/{entity}")
async def generate_code(
    entity: str, 
    gen: NumberGenerator = Depends(get_generator)
):
    try:
        code = gen.generate(entity)
        return {"entity": entity, "code": code}
    except Exception as e:
        return {"error": str(e)}, 400
```

**Test endpoints:**
```bash
curl http://localhost:8000/generate/supplier
# {"entity": "supplier", "code": "SUP-250001"}

curl http://localhost:8000/generate/invoice
# {"entity": "invoice", "code": "INV-2025-00001"}
```

---

### Django Integration

#### Step 1: Setup di `settings.py`

```python
# myproject/settings.py
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

# Initialize Nanumber (singleton)
NANUMBER_STORAGE = SQLAlchemyStorage(
    f"postgresql://{DATABASES['default']['USER']}:"
    f"{DATABASES['default']['PASSWORD']}@"
    f"{DATABASES['default']['HOST']}/"
    f"{DATABASES['default']['NAME']}"
)

NANUMBER_GENERATOR = NumberGenerator(
    storage=NANUMBER_STORAGE,
    templates={
        "supplier": {"template": "SUP-{y}{number}", "pad": 4},
        "invoice": {"template": "INV-{Y}-{number}", "pad": 5},
        "customer": {"template": "CUST-{y}{number}", "pad": 4},
    }
)
```

#### Step 2: Gunakan di Models/Signals

```python
# apps/supplier/models.py
from django.db import models

class Supplier(models.Model):
    code = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=255)
    # ... other fields

# apps/supplier/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Supplier

@receiver(pre_save, sender=Supplier)
def generate_supplier_code(sender, instance, **kwargs):
    if not instance.code:  # Only generate if empty
        instance.code = settings.NANUMBER_GENERATOR.generate("supplier")

# apps/supplier/apps.py
from django.apps import AppConfig

class SupplierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.supplier'

    def ready(self):
        import apps.supplier.signals  # Register signals
```

---

### Flask Integration

```python
# app.py
from flask import Flask, jsonify
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

app = Flask(__name__)

# Initialize Nanumber
storage = SQLAlchemyStorage("sqlite:///nanumber.db")
gen = NumberGenerator(
    storage=storage,
    templates={
        "supplier": {"template": "SUP-{y}{number}", "pad": 4},
        "invoice": {"template": "INV-{Y}-{number}", "pad": 5},
    }
)

@app.route("/generate/<entity>")
def generate_number(entity):
    try:
        code = gen.generate(entity)
        return jsonify({"entity": entity, "code": code})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
```

---

## 🧪 Advanced Usage

### Auto-reset per Tahun

```python
from datetime import datetime

# Generate untuk tahun 2024
code_2024 = gen.generate(
    "invoice", 
    "INV-{Y}-{number}",
    pad=5,
    date=datetime(2024, 12, 31)
)
print(code_2024)  # INV-2024-00001

# Generate untuk tahun 2025 - otomatis reset ke 1
code_2025 = gen.generate(
    "invoice",
    "INV-{Y}-{number}",
    pad=5,
    date=datetime(2025, 1, 1)
)
print(code_2025)  # INV-2025-00001
```

**Catatan:** Reset otomatis dilakukan oleh `SQLAlchemyStorage` berdasarkan kolom `last_reset_year` di database.

---

### Manual Reset

```python
# Reset nomor ke 0 (next generate akan jadi 1)
gen.reset("supplier", 0)

# Reset ke nilai tertentu
gen.reset("invoice", 100)  # Next generate akan jadi 101

# Get last number
last_num = gen.storage.get_last_number("supplier")
print(f"Last number: {last_num}")
```

---

### Custom Padding

```python
# Default padding (4 digit)
gen.generate("test", "T-{number}")  # T-0001

# Custom padding (6 digit)
gen.generate("test", "T-{number}", pad=6)  # T-000001

# No padding (1 digit minimal)
gen.generate("test", "T-{number}", pad=1)  # T-1

# Padding dengan karakter lain
gen.generate("test", "T-{number}", pad=4, pad_char="X")  # T-XXX1

# Padding kanan
gen.generate("test", "T-{number}", pad=4, pad_side="right")  # T-1000
```

---

## 🧠 Thread Safety Test

```python
import threading
from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage

storage = SQLAlchemyStorage("sqlite:///test.db")
gen = NumberGenerator(storage)

results = []

def worker():
    code = gen.generate("test", "T-{number}", pad=4)
    results.append(code)
    print(code)

# Spawn 100 threads
threads = [threading.Thread(target=worker) for _ in range(100)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Check uniqueness
print(f"Generated: {len(results)}")
print(f"Unique: {len(set(results))}")
assert len(results) == len(set(results)), "Duplikasi terdeteksi!"
```

**Output:**
```
T-0001
T-0002
T-0003
...
T-0100
Generated: 100
Unique: 100
```

Semua nomor **unik** - tidak ada duplikasi! ✅

---

## 📊 Database Schema

Nanumber otomatis membuat tabel `auto_numbers`:

```sql
CREATE TABLE auto_numbers (
    key VARCHAR(100) PRIMARY KEY,
    last_value INTEGER NOT NULL DEFAULT 0,
    last_reset_year INTEGER NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**Contoh data:**

| key | last_value | last_reset_year | updated_at |
|-----|-----------|----------------|------------|
| supplier | 42 | 2025 | 2025-11-13 10:30:00 |
| invoice | 158 | 2025 | 2025-11-13 11:15:00 |

---

## 🎨 Real-world Examples

### E-commerce System

```python
templates = {
    "customer": {
        "template": "CUST-{y}{number}",
        "pad": 6
    },
    "order": {
        "template": "ORD-{Y}{m}{d}-{number}",
        "pad": 4
    },
    "invoice": {
        "template": "INV-{Y}-{number}",
        "pad": 8
    },
    "shipment": {
        "template": "SHIP-{y}{m}{number}",
        "pad": 5
    }
}

gen = NumberGenerator(storage, templates=templates)

# Generate codes
customer_code = gen.generate("customer")     # CUST-25000001
order_number = gen.generate("order")         # ORD-20251113-0001
invoice_number = gen.generate("invoice")     # INV-2025-00000001
shipment_code = gen.generate("shipment")     # SHIP-251100001
```

---

### Manufacturing System

```python
templates = {
    "production_order": {
        "template": "PO-{Y}-{number}",
        "pad": 5
    },
    "batch": {
        "template": "BATCH-{y}{m}{d}{H}{number}",
        "pad": 3
    },
    "quality_check": {
        "template": "QC-{y}{number}",
        "pad": 6
    }
}

gen = NumberGenerator(storage, templates=templates)

po_number = gen.generate("production_order")  # PO-2025-00001
batch_code = gen.generate("batch")            # BATCH-25111310001
qc_number = gen.generate("quality_check")     # QC-25000001
```

---

## 🐛 Troubleshooting

### Error: `TemplateNotFoundError`

```python
# ❌ Error
gen.generate("unknown_key")
# TemplateNotFoundError: Template 'unknown_key' not found

# ✅ Solution 1: Tambahkan template
gen.templates["unknown_key"] = {
    "template": "UK-{number}",
    "pad": 4
}

# ✅ Solution 2: Provide template inline
gen.generate("unknown_key", "UK-{number}", pad=4)
```

---

### Error: `TemplateError: Unknown placeholder`

```python
# ❌ Error
gen.generate("test", "T-{number:04d}")
# TemplateError: Unknown placeholder: {number:04d}

# ✅ Solution: Gunakan parameter pad
gen.generate("test", "T-{number}", pad=4)
```

---

### Error: Database locked (SQLite)

```python
# ❌ Problem: SQLite tidak handle concurrent writes dengan baik

# ✅ Solution: Gunakan PostgreSQL atau MySQL
storage = SQLAlchemyStorage(
    "postgresql://user:pass@localhost/mydb"
)
```

---

## 📚 API Reference

### `NumberGenerator`

#### `__init__(storage, default_pad=4, default_pad_char="0", default_pad_side="left", templates=None)`

Initialize number generator.

**Parameters:**
- `storage`: Storage backend (MemoryStorage or SQLAlchemyStorage)
- `default_pad`: Default padding length (default: 4)
- `default_pad_char`: Padding character (default: "0")
- `default_pad_side`: Padding side "left" or "right" (default: "left")
- `templates`: Dict of predefined templates

---

#### `generate(key, template=None, pad=None, pad_char=None, pad_side=None, date=None)`

Generate auto-number for given key.

**Parameters:**
- `key`: Unique identifier for sequence
- `template`: Format template string
- `pad`: Number padding length
- `pad_char`: Character for padding
- `pad_side`: "left" or "right"
- `date`: Date for placeholders (default: now)

**Returns:** Generated number string

**Raises:**
- `TemplateNotFoundError`: If key not in templates and template not provided
- `TemplateError`: If template contains invalid placeholders

---

#### `reset(key, value=0)`

Reset number sequence.

**Parameters:**
- `key`: Unique identifier for sequence
- `value`: Reset to this value (default: 0)

---

### `SQLAlchemyStorage`

#### `__init__(db_url="sqlite:///nanumber.db")`

Initialize storage with database URL.

**Parameters:**
- `db_url`: SQLAlchemy database URL

**Examples:**
```python
# SQLite
SQLAlchemyStorage("sqlite:///nanumber.db")

# PostgreSQL
SQLAlchemyStorage("postgresql://user:pass@localhost/db")

# MySQL
SQLAlchemyStorage("mysql+pymysql://user:pass@localhost/db")
```

---

## 🤝 Contributing

Contributions are welcome! Silakan buat Pull Request atau Issue di GitHub.

### Development Setup

```bash
# Clone repository
git clone https://github.com/risnaberti/nanumber.git
cd nanumber

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=risnaberti.nanumber
```

---

## 📄 License

MIT © 2025 **Risna Berti**

---

## 💬 Support & Contact

Ada pertanyaan atau butuh bantuan?

📧 **Email:** risnaberti07@gmail.com  
🐙 **GitHub:** [@risnaberti](https://github.com/risnaberti)  
💼 **LinkedIn:** [Risna Berti](https://linkedin.com/in/risnaberti)

---

## 🌟 Show Your Support

Jika library ini bermanfaat, kasih ⭐ di GitHub ya!

👉 [https://github.com/risnaberti/nanumber](https://github.com/risnaberti/nanumber)

---

✨ *Made with ❤️ by Risna Berti (Nana)*  
> _"Because numbering should be smart, safe, and beautiful."_
