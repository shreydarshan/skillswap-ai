import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
sys.path.insert(0, os.path.abspath("backend"))

from sqlalchemy import text
from app.core.database import SessionLocal

db = SessionLocal()
db.execute(text("UPDATE profiles SET is_test = true WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'test_%' OR email LIKE 'stage4%')"))
db.commit()
db.close()
print("Test accounts successfully marked with is_test = true in PostgreSQL!")
