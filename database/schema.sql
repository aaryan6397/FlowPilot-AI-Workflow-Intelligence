CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'completed')),
    deadline TEXT NOT NULL,
    estimated_minutes INTEGER NOT NULL CHECK(estimated_minutes BETWEEN 5 AND 2400),
    importance INTEGER NOT NULL CHECK(importance BETWEEN 1 AND 10),
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline);
CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category);
