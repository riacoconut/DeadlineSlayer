-- Створення бази даних DeadlineSlayer
-- Виконайте цей скрипт в pgAdmin після створення БД

-- Таблиця користувачів
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Додано для хешування пароля
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблиця категорій
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(20)
);

-- Вставка базових категорій
INSERT INTO categories (name, color) VALUES
('Навчання', 'blue'),
('Робота', 'green'),
('Особисте', 'orange'),
('Інше', 'gray');

-- Таблиця пріоритетів
CREATE TABLE priorities (
    priority_id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL UNIQUE,
    weight INT NOT NULL
);

-- Вставка пріоритетів
INSERT INTO priorities (level, weight) VALUES
('Високий', 3),
('Середній', 2),
('Низький', 1);

-- Таблиця завдань
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline TIMESTAMP NOT NULL,
    category_id INT REFERENCES categories(category_id),
    priority_id INT REFERENCES priorities(priority_id),
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Таблиця нагадувань
CREATE TABLE reminders (
    reminder_id SERIAL PRIMARY KEY,
    task_id INT REFERENCES tasks(task_id) ON DELETE CASCADE,
    remind_at TIMESTAMP NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    message TEXT
);

-- Індекси для оптимізації запитів
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(is_completed);
CREATE INDEX idx_reminders_time ON reminders(remind_at);
CREATE INDEX idx_reminders_sent ON reminders(is_sent);

-- Коментарі до таблиць
COMMENT ON TABLE users IS 'Таблиця користувачів системи';
COMMENT ON TABLE tasks IS 'Таблиця завдань з дедлайнами';
COMMENT ON TABLE categories IS 'Категорії завдань';
COMMENT ON TABLE priorities IS 'Рівні пріоритетів';
COMMENT ON TABLE reminders IS 'Нагадування про дедлайни';