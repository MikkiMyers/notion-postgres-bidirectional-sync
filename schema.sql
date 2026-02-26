CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY,
    task_name TEXT NOT NULL,
    status TEXT,
    due_date DATE,
    last_edited TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);