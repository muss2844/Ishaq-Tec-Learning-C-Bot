import os
import sqlite3

# ===========================
# إعدادات البوت
# ===========================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # توكن البوت من متغير البيئة
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))  # رقم المدير

# ===========================
# إعدادات قاعدة البيانات
# ===========================
DB_NAME = "bot_database.db"

# ===========================
# دالة لإنشاء الاتصال بالقاعدة
# ===========================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # لتسهيل الوصول للأعمدة بالاسم
    return conn

# ===========================
# إنشاء الجداول إذا لم توجد
# ===========================
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # جدول المستخدمين
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            language TEXT DEFAULT 'ar',
            level TEXT DEFAULT 'beginner',
            progress INTEGER DEFAULT 0
        )
    """)

    # جدول الدروس
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            pdf_file TEXT,
            video_file TEXT,
            level TEXT DEFAULT 'beginner'
        )
    """)

    # جدول الاختبارات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER,
            question TEXT,
            options TEXT,
            answer TEXT,
            FOREIGN KEY(lesson_id) REFERENCES lessons(id)
        )
    """)

    # جدول الدروس الخاصة والمدفوعات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS private_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            transaction_id TEXT,
            status TEXT DEFAULT 'pending',
            session_link TEXT,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# ===========================
# عند الاستيراد يمكن تهيئة القاعدة تلقائيًا
# ===========================
if __name__ == "__main__":
    init_db()
