import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Підключення до бази даних PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                database="deadline_slayer",
                user="postgres",  # Твій юзер
                password="qwerty16"  # Твій пароль
            )
            self.cursor = self.connection.cursor()
            print("✓ Підключення до БД успішне")
            return True
        except Error as e:
            print(f"✗ Помилка підключення до БД: {e}")
            return False
    
    def disconnect(self):
        """Закриття з'єднання"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("✓ З'єднання закрито")
    
    # ========== КОРИСТУВАЧІ ==========
    
    def create_user(self, username, email):
        """Створення нового користувача"""
        try:
            query = """
                INSERT INTO users (username, email) 
                VALUES (%s, %s) 
                RETURNING user_id
            """
            self.cursor.execute(query, (username, email))
            user_id = self.cursor.fetchone()[0]
            self.connection.commit()
            print(f"✓ Користувач '{username}' створений (ID: {user_id})")
            return user_id
        except Error as e:
            print(f"✗ Помилка створення користувача: {e}")
            self.connection.rollback()
            return None
    
    def get_user_by_username(self, username):
        """Отримання користувача за іменем"""
        try:
            query = "SELECT * FROM users WHERE username = %s"
            self.cursor.execute(query, (username,))
            return self.cursor.fetchone()
        except Error as e:
            print(f"✗ Помилка пошуку користувача: {e}")
            return None
    
    # ========== ЗАВДАННЯ ==========
    
    def add_task(self, user_id, title, description, deadline, category_id, priority_id):
        """Додавання нового завдання"""
        try:
            query = """
                INSERT INTO tasks (user_id, title, description, deadline, 
                                 category_id, priority_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING task_id
            """
            self.cursor.execute(query, (user_id, title, description, 
                                       deadline, category_id, priority_id))
            task_id = self.cursor.fetchone()[0]
            self.connection.commit()
            print(f"✓ Завдання '{title}' додано (ID: {task_id})")
            return task_id
        except Error as e:
            print(f"✗ Помилка додавання завдання: {e}")
            self.connection.rollback()
            return None
    
    def get_user_tasks(self, user_id, include_completed=False):
        """Отримання всіх завдань користувача"""
        try:
            query = """
                SELECT t.task_id, t.title, t.description, t.deadline,
                       c.name as category, p.level as priority, t.is_completed,
                       t.created_at
                FROM tasks t
                LEFT JOIN categories c ON t.category_id = c.category_id
                LEFT JOIN priorities p ON t.priority_id = p.priority_id
                WHERE t.user_id = %s
            """
            if not include_completed:
                query += " AND t.is_completed = FALSE"
            
            query += " ORDER BY p.weight DESC, t.deadline ASC"
            
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        except Error as e:
            print(f"✗ Помилка отримання завдань: {e}")
            return []
    
    def update_task(self, task_id, **kwargs):
        """Оновлення завдання"""
        try:
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f"{key} = %s")
                values.append(value)
            
            values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(fields)} WHERE task_id = %s"
            
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"✓ Завдання {task_id} оновлено")
            return True
        except Error as e:
            print(f"✗ Помилка оновлення завдання: {e}")
            self.connection.rollback()
            return False
    
    def delete_task(self, task_id):
        """Видалення завдання"""
        try:
            query = "DELETE FROM tasks WHERE task_id = %s"
            self.cursor.execute(query, (task_id,))
            self.connection.commit()
            print(f"✓ Завдання {task_id} видалено")
            return True
        except Error as e:
            print(f"✗ Помилка видалення завдання: {e}")
            self.connection.rollback()
            return False
    
    def complete_task(self, task_id):
        """Позначити завдання як виконане"""
        return self.update_task(task_id, 
                               is_completed=True, 
                               completed_at=datetime.now())
    
    # ========== КАТЕГОРІЇ ТА ПРІОРИТЕТИ ==========
    
    def get_categories(self):
        """Отримання всіх категорій"""
        try:
            query = "SELECT * FROM categories ORDER BY category_id"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"✗ Помилка отримання категорій: {e}")
            return []
    
    def get_priorities(self):
        """Отримання всіх пріоритетів"""
        try:
            query = "SELECT * FROM priorities ORDER BY weight DESC"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"✗ Помилка отримання пріоритетів: {e}")
            return []
    
    # ========== НАГАДУВАННЯ ==========
    
    def add_reminder(self, task_id, remind_at, message):
        """Додавання нагадування"""
        try:
            query = """
                INSERT INTO reminders (task_id, remind_at, message)
                VALUES (%s, %s, %s)
                RETURNING reminder_id
            """
            self.cursor.execute(query, (task_id, remind_at, message))
            reminder_id = self.cursor.fetchone()[0]
            self.connection.commit()
            print(f"✓ Нагадування додано (ID: {reminder_id})")
            return reminder_id
        except Error as e:
            print(f"✗ Помилка додавання нагадування: {e}")
            self.connection.rollback()
            return None
    
    def get_pending_reminders(self):
        """Отримання невідправлених нагадувань"""
        try:
            query = """
                SELECT r.reminder_id, r.task_id, r.message, t.title
                FROM reminders r
                JOIN tasks t ON r.task_id = t.task_id
                WHERE r.is_sent = FALSE 
                  AND r.remind_at <= %s
                ORDER BY r.remind_at
            """
            self.cursor.execute(query, (datetime.now(),))
            return self.cursor.fetchall()
        except Error as e:
            print(f"✗ Помилка отримання нагадувань: {e}")
            return []
    
    def mark_reminder_sent(self, reminder_id):
        """Позначити нагадування як відправлене"""
        try:
            query = "UPDATE reminders SET is_sent = TRUE WHERE reminder_id = %s"
            self.cursor.execute(query, (reminder_id,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"✗ Помилка оновлення нагадування: {e}")
            self.connection.rollback()
            return False
    
    # ========== СТАТИСТИКА ==========
    
    def get_statistics(self, user_id):
        """Статистика користувача"""
        try:
            stats = {}
            
            # Всього завдань
            self.cursor.execute(
                "SELECT COUNT(*) FROM tasks WHERE user_id = %s",
                (user_id,)
            )
            stats['total'] = self.cursor.fetchone()[0]
            
            # Виконані
            self.cursor.execute(
                "SELECT COUNT(*) FROM tasks WHERE user_id = %s AND is_completed = TRUE",
                (user_id,)
            )
            stats['completed'] = self.cursor.fetchone()[0]
            
            # Активні
            stats['active'] = stats['total'] - stats['completed']
            
            # Прострочені
            self.cursor.execute(
                """SELECT COUNT(*) FROM tasks 
                   WHERE user_id = %s 
                     AND is_completed = FALSE 
                     AND deadline < %s""",
                (user_id, datetime.now())
            )
            stats['overdue'] = self.cursor.fetchone()[0]
            
            return stats
        except Error as e:
            print(f"✗ Помилка отримання статистики: {e}")
            return {}