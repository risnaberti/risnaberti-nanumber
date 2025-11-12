from nanumber.storage.sqlalchemy_storage import SQLAlchemyStorage, AutoNumber
from nanumber.core import NumberGenerator

# ganti sesuai database kamu
# storage = SQLAlchemyStorage("sqlite:///test_nanumber.db")
storage = SQLAlchemyStorage("postgresql+psycopg2://postgres:admin123@localhost/test_db")

gen = NumberGenerator(storage)

print("=== Test Basic ===")
print(gen.generate("supplier", "#SUP-{y}{number}"))
print(gen.generate("supplier", "#SUP-{y}{number}"))

print("=== Test Tahun Berganti ===")
# simulasi ubah tahun lama
# with storage.Session() as s:
#     record = s.get(AutoNumber, "supplier")   # ambil baris supplier
#     record.last_reset_year -= 1              # ubah jadi tahun lalu
#     s.commit()

# print(gen.generate("supplier", "#SUP-{y}{number}"))

