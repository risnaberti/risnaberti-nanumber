import threading
from nanumber.storage.sqlalchemy_storage import SQLAlchemyStorage
from nanumber.core import NumberGenerator

# Gunakan SQLite dulu (atau ganti ke PostgreSQL untuk uji sesungguhnya)
# storage = SQLAlchemyStorage("sqlite:///test_concurrency.db")
storage = SQLAlchemyStorage("postgresql+psycopg2://postgres:admin123@localhost/test_db")
generator = NumberGenerator(storage)

# Reset data biar bersih
storage.reset("supplier")

results = []
lock = threading.Lock()

def worker(thread_id):
    """Simulasi worker yang generate nomor supplier"""
    try:
        code = generator.generate("supplier", "#SUP-{y}{number}")
        with lock:
            results.append(code)
    except Exception as e:
        print(f"Thread {thread_id} error: {e}")

# Jalankan 50 thread bersamaan
threads = [threading.Thread(target=worker, args=(i,)) for i in range(500)]

print("🚀 Mulai generate kode secara bersamaan...")
for t in threads:
    t.start()

for t in threads:
    t.join()

print("✅ Semua thread selesai.")
print(f"Total hasil: {len(results)}")

# Urutkan hasil biar gampang dicek
sorted_results = sorted(results)

print("\n=== 10 kode pertama ===")
for r in sorted_results[:10]:
    print(r)

# Cek apakah ada duplikat
if len(sorted_results) == len(set(sorted_results)):
    print("\n🎉 Semua kode unik dan aman dari race condition!")
else:
    print("\n⚠️ Ada duplikasi! Locking belum bekerja dengan benar.")
