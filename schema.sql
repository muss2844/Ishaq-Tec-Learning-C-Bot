-- ===========================
-- جدول المستخدمين
-- ===========================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    language TEXT DEFAULT 'ar',
    level TEXT DEFAULT 'beginner',
    progress INTEGER DEFAULT 0
);

-- ===========================
-- جدول الدروس
-- ===========================
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    pdf_file TEXT,
    video_file TEXT,
    level TEXT DEFAULT 'beginner'
);

-- ===========================
-- جدول الاختبارات
-- ===========================
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER,
    question TEXT,
    options TEXT,
    answer TEXT,
    FOREIGN KEY(lesson_id) REFERENCES lessons(id)
);

-- ===========================
-- جدول الدروس الخاصة والمدفوعات
-- ===========================
CREATE TABLE IF NOT EXISTS private_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    transaction_id TEXT,
    status TEXT DEFAULT 'pending',
    session_link TEXT,
    date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
