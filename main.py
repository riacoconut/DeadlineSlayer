import os
from datetime import datetime, timedelta
from database import DatabaseManager

class DeadlineSlayerApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None
        self.current_user_id = None
        
    def clear_screen(self):
        """Очищення екрану консолі"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Вивід заголовку"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60 + "\n")
    
    def wait_enter(self):
        """Очікування натискання Enter"""
        input("\nНатисніть Enter для продовження...")
    
    def run(self):
        """Запуск програми"""
        if not self.db.connect():
            print("Не вдалося підключитися до бази даних!")
            return
        
        try:
            self.main_menu()
        finally:
            self.db.disconnect()
    
    # ========== МЕНЮ ==========
    
    def main_menu(self):
        """Головне меню"""
        while True:
            self.clear_screen()
            self.print_header("DeadlineSlayer - Головне меню")
            
            if self.current_user:
                print(f"Користувач: {self.current_user}\n")
                print("1. Додати завдання")
                print("2. Переглянути завдання")
                print("3. Редагувати завдання")
                print("4. Видалити завдання")
                print("5. Позначити завдання виконаним")
                print("6. Статистика")
                print("7. Вийти з акаунту")
                print("0. Вихід з програми")
            else:
                print("1. Увійти")
                print("2. Зареєструватися")
                print("0. Вихід")
            
            choice = input("\nВаш вибір: ").strip()
            
            if not self.current_user:
                if choice == '1':
                    self.login()
                elif choice == '2':
                    self.register()
                elif choice == '0':
                    print("\nДо побачення!")
                    break
            else:
                if choice == '1':
                    self.add_task_menu()
                elif choice == '2':
                    self.view_tasks_menu()
                elif choice == '3':
                    self.edit_task_menu()
                elif choice == '4':
                    self.delete_task_menu()
                elif choice == '5':
                    self.complete_task_menu()
                elif choice == '6':
                    self.statistics_menu()
                elif choice == '7':
                    self.logout()
                elif choice == '0':
                    print("\nДо побачення!")
                    break
    
    # ========== АУТЕНТИФІКАЦІЯ ==========
    
    def register(self):
        """Реєстрація нового користувача"""
        self.clear_screen()
        self.print_header("Реєстрація")
        
        username = input("Введіть ім'я користувача: ").strip()
        if not username:
            print("✗ Ім'я не може бути порожнім!")
            self.wait_enter()
            return
        
        # Перевірка чи існує
        if self.db.get_user_by_username(username):
            print(f"✗ Користувач '{username}' вже існує!")
            self.wait_enter()
            return
        
        email = input("Введіть email: ").strip()
        if not email or '@' not in email:
            print("✗ Некоректний email!")
            self.wait_enter()
            return
        
        user_id = self.db.create_user(username, email)
        if user_id:
            print(f"\n✓ Реєстрація успішна! Ласкаво просимо, {username}!")
            self.current_user = username
            self.current_user_id = user_id
        
        self.wait_enter()
    
    def login(self):
        """Вхід користувача"""
        self.clear_screen()
        self.print_header("Вхід")
        
        username = input("Введіть ім'я користувача: ").strip()
        user = self.db.get_user_by_username(username)
        
        if user:
            self.current_user = username
            self.current_user_id = user[0]
            print(f"\n✓ Ласкаво просимо, {username}!")
        else:
            print(f"\n✗ Користувача '{username}' не знайдено!")
        
        self.wait_enter()
    
    def logout(self):
        """Вихід з акаунту"""
        print(f"\nДо побачення, {self.current_user}!")
        self.current_user = None
        self.current_user_id = None
        self.wait_enter()
    
    # ========== РОБОТА З ЗАВДАННЯМИ ==========
    
    def add_task_menu(self):
        """Меню додавання завдання"""
        self.clear_screen()
        self.print_header("Додати нове завдання")
        
        # Назва
        title = input("Назва завдання: ").strip()
        if not title:
            print("✗ Назва не може бути порожньою!")
            self.wait_enter()
            return
        
        # Опис
        description = input("Опис (необов'язково): ").strip()
        
        # Дедлайн
        print("\nВведіть дедлайн:")
        try:
            date_str = input("  Дата (ДД.ММ.РРРР): ").strip()
            time_str = input("  Час (ГГ:ХХ): ").strip()
            deadline = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
            
            if deadline < datetime.now():
                print("✗ Дедлайн не може бути в минулому!")
                self.wait_enter()
                return
        except ValueError:
            print("✗ Некоректний формат дати/часу!")
            self.wait_enter()
            return
        
        # Категорія
        categories = self.db.get_categories()
        print("\nКатегорії:")
        for cat in categories:
            print(f"  {cat[0]}. {cat[1]}")
        
        try:
            category_id = int(input("Оберіть категорію (номер): ").strip())
            if category_id not in [c[0] for c in categories]:
                raise ValueError
        except ValueError:
            print("✗ Некоректна категорія!")
            self.wait_enter()
            return
        
        # Пріоритет
        priorities = self.db.get_priorities()
        print("\nПріоритети:")
        for pri in priorities:
            print(f"  {pri[0]}. {pri[1]}")
        
        try:
            priority_id = int(input("Оберіть пріоритет (номер): ").strip())
            if priority_id not in [p[0] for p in priorities]:
                raise ValueError
        except ValueError:
            print("✗ Некоректний пріоритет!")
            self.wait_enter()
            return
        
        # Додавання в БД
        task_id = self.db.add_task(
            self.current_user_id, 
            title, 
            description, 
            deadline, 
            category_id, 
            priority_id
        )
        
        if task_id:
            # Додати нагадування за 1 день до дедлайну
            remind_time = deadline - timedelta(days=1)
            if remind_time > datetime.now():
                message = f"Завтра дедлайн: {title}"
                self.db.add_reminder(task_id, remind_time, message)
            
            print("\n✓ Завдання успішно додано!")
        
        self.wait_enter()
    
    def view_tasks_menu(self):
        """Меню перегляду завдань"""
        self.clear_screen()
        self.print_header("Мої завдання")
        
        print("1. Активні завдання")
        print("2. Всі завдання (включно з виконаними)")
        print("0. Назад")
        
        choice = input("\nВаш вибір: ").strip()
        
        if choice == '0':
            return
        
        include_completed = (choice == '2')
        tasks = self.db.get_user_tasks(self.current_user_id, include_completed)
        
        self.clear_screen()
        self.print_header("Список завдань")
        
        if not tasks:
            print("Завдань не знайдено.")
        else:
            for task in tasks:
                task_id, title, desc, deadline, category, priority, completed, created = task
                
                # Обчислення днів до дедлайну
                days_left = (deadline - datetime.now()).days
                
                status = "✓ Виконано" if completed else f"⏰ Залишилось {days_left} днів"
                
                print(f"\n{'='*60}")
                print(f"ID: {task_id}")
                print(f"Назва: {title}")
                if desc:
                    print(f"Опис: {desc}")
                print(f"Дедлайн: {deadline.strftime('%d.%m.%Y %H:%M')}")
                print(f"Категорія: {category}")
                print(f"Пріоритет: {priority}")
                print(f"Статус: {status}")
                print(f"Створено: {created.strftime('%d.%m.%Y %H:%M')}")
        
        self.wait_enter()
    
    def edit_task_menu(self):
        """Меню редагування завдання"""
        self.clear_screen()
        self.print_header("Редагувати завдання")
        
        try:
            task_id = int(input("Введіть ID завдання: ").strip())
        except ValueError:
            print("✗ Некоректний ID!")
            self.wait_enter()
            return
        
        print("\nЩо бажаєте змінити?")
        print("1. Назву")
        print("2. Опис")
        print("3. Дедлайн")
        print("4. Категорію")
        print("5. Пріоритет")
        print("0. Скасувати")
        
        choice = input("\nВаш вибір: ").strip()
        
        if choice == '0':
            return
        elif choice == '1':
            new_title = input("Нова назва: ").strip()
            if new_title:
                self.db.update_task(task_id, title=new_title)
        elif choice == '2':
            new_desc = input("Новий опис: ").strip()
            self.db.update_task(task_id, description=new_desc)
        elif choice == '3':
            try:
                date_str = input("Нова дата (ДД.ММ.РРРР): ").strip()
                time_str = input("Новий час (ГГ:ХХ): ").strip()
                new_deadline = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
                self.db.update_task(task_id, deadline=new_deadline)
            except ValueError:
                print("✗ Некоректний формат!")
        elif choice == '4':
            categories = self.db.get_categories()
            for cat in categories:
                print(f"  {cat[0]}. {cat[1]}")
            cat_id = int(input("Нова категорія: ").strip())
            self.db.update_task(task_id, category_id=cat_id)
        elif choice == '5':
            priorities = self.db.get_priorities()
            for pri in priorities:
                print(f"  {pri[0]}. {pri[1]}")
            pri_id = int(input("Новий пріоритет: ").strip())
            self.db.update_task(task_id, priority_id=pri_id)
        
        self.wait_enter()
    
    def delete_task_menu(self):
        """Меню видалення завдання"""
        self.clear_screen()
        self.print_header("Видалити завдання")
        
        try:
            task_id = int(input("Введіть ID завдання для видалення: ").strip())
        except ValueError:
            print("✗ Некоректний ID!")
            self.wait_enter()
            return
        
        confirm = input(f"Ви впевнені? (так/ні): ").strip().lower()
        if confirm in ['так', 'yes', 'y']:
            if self.db.delete_task(task_id):
                print("\n✓ Завдання видалено!")
        else:
            print("\n✗ Скасовано")
        
        self.wait_enter()
    
    def complete_task_menu(self):
        """Меню позначення завдання виконаним"""
        self.clear_screen()
        self.print_header("Позначити завдання виконаним")
        
        try:
            task_id = int(input("Введіть ID завдання: ").strip())
        except ValueError:
            print("✗ Некоректний ID!")
            self.wait_enter()
            return
        
        if self.db.complete_task(task_id):
            print("\n✓ Завдання виконано! 🎉")
        
        self.wait_enter()
    
    def statistics_menu(self):
        """Меню статистики"""
        self.clear_screen()
        self.print_header("Статистика")
        
        stats = self.db.get_statistics(self.current_user_id)
        
        print(f"Всього завдань: {stats.get('total', 0)}")
        print(f"Виконано: {stats.get('completed', 0)}")
        print(f"Активних: {stats.get('active', 0)}")
        print(f"Прострочених: {stats.get('overdue', 0)}")
        
        if stats.get('total', 0) > 0:
            completion_rate = (stats.get('completed', 0) / stats['total']) * 100
            print(f"\nВідсоток виконання: {completion_rate:.1f}%")
        
        self.wait_enter()


if __name__ == "__main__":
    app = DeadlineSlayerApp()
    app.run()