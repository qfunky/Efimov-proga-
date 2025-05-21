from datetime import datetime, timedelta
import uuid

FILEPATH = "db.txt"
SEPARATOR = "<>"
STATUS_ACTIVE = "active"
STATUS_DONE = "done"
STATUS_OVERDUE = "overdue"


class Task:
    def __init__(self, task_id, name, date_complete, created_at, status):
        self._id = task_id
        self.name = name
        self.date_complete = date_complete
        self._created_at = created_at
        self.status = status

    @property
    def id(self):
        return self._id

    @property
    def created_at(self):
        return self._created_at

    @property
    def is_overdue(self):
        # Проверяем просрочена ли задача
        if self.status != STATUS_ACTIVE or not self.date_complete:
            return False
        try:
            deadline = datetime.strptime(self.date_complete.strip("[]"), "%d.%m.%Y")
            return deadline < datetime.now()
        except ValueError:
            return False

    def to_readable(self, index):
        # Формируем строку для вывода задачи
        if self.status == STATUS_ACTIVE:
            status_icon = "✕"
        elif self.status == STATUS_DONE:
            status_icon = "✓"
        else:
            status_icon = "⌛️"

        overdue_label = " просрочено" if self.is_overdue else ""
        return f"{index}. {status_icon}{overdue_label} {self.name} {self.date_complete}"


def read_database(filepath):
    # Читаем все строки из файла и возвращаем строчки
    with open(filepath, "r", encoding="utf8") as file:
        lines = file.read().splitlines()
    return lines


def parse_tasks():
    # Парсим строки из базы в объекты Task
    tasks = []
    lines = read_database(FILEPATH)
    for line in lines:
        if line == "":
            continue
        parts = line.split(SEPARATOR)
        task_id = parts[0]
        name = parts[1]
        date_complete = parts[2]
        created_at = datetime.fromisoformat(parts[3])
        status = parts[4]
        task = Task(task_id, name, date_complete, created_at, status)
        tasks.append(task)
    return tasks


def print_readable(tasks):
    # Выводим список задач
    print("Актуальные задачи:")
    for index, task in enumerate(tasks, 1):
        print(task.to_readable(index))


def make_new_task():
    # Вводим данные для новой задачи
    while True:
        task_name = input("Введите имя задачи: ").strip()
        if task_name:
            break
        print("Введите валидное имя задачи.")

    while True:
        date_complete = input("Введите дату выполнения в формате ДД.ММ.ГГГГ или enter: ")
        if not date_complete:
            break
        try:
            datetime.strptime(date_complete, "%d.%m.%Y")
            break
        except ValueError:
            print("Введите дату в правильном формате.")

    print("Вы собираетесь создать задание с параметрами:")
    if date_complete:
        print(f" - Имя задачи: {task_name}")
        print(f" - Дата выполнения: [{date_complete}]")
    else:
        print(f" - Имя задачи: {task_name}")
        print(f" - Дата выполнения: [не задана]")

    write_database(FILEPATH, task_name, date_complete, datetime.now())
    tasks = parse_tasks()
    print_readable(tasks)


def write_database(filepath, task_name, date_complete, timestamp):
    # Записываем новую задачу в файл
    if date_complete:
        date_complete_dt_format = datetime.strptime(date_complete, '%d.%m.%Y')
    else:
        date_complete_dt_format = timestamp + timedelta(days=1)

    if date_complete_dt_format > timestamp:
        status = STATUS_ACTIVE
    else:
        status = STATUS_OVERDUE

    with open(filepath, "a", encoding="utf8") as file:
        file.write(f"{uuid.uuid4()}{SEPARATOR}{task_name}{SEPARATOR}[{date_complete}]{SEPARATOR}{timestamp}{SEPARATOR}{status}\n")

def edit_task(tasks):
    if not tasks:
        print("Нет задач для редактирования.")
        return
    print_readable(tasks)
    try:
        idx = int(input("Введите номер задачи для редактирования: "))
        if idx < 1 or idx > len(tasks):
            print("Некорректный номер задачи.")
            return
        task = tasks[idx - 1]
        print(f"Текущая задача: {task.name} {task.date_complete}")
        field = input("Что редактировать? (1 - имя, 2 - дату): ")
        if field == "1":
            new_name = input("Новое имя задачи: ").strip()
            if new_name:
                task.name = new_name
            else:
                print("Имя не изменено.")
        elif field == "2":
            new_date = input("Новая дата выполнения (ДД.ММ.ГГГГ) или пусто: ").strip()
            if new_date:
                try:
                    datetime.strptime(new_date, "%d.%m.%Y")
                    task.date_complete = f"[{new_date}]"
                except ValueError:
                    print("Дата не изменена: неверный формат.")
            else:
                task.date_complete = ""
        else:
            print("Поле не выбрано.")
    except Exception as e:
        print("Ошибка при редактировании задачи:", e)

def delete_task(tasks):
    if not tasks:
        print("Нет задач для удаления.")
        return
    print_readable(tasks)
    try:
        idx = int(input("Введите номер задачи для удаления: "))
        if idx < 1 or idx > len(tasks):
            print("Некорректный номер задачи.")
            return
        removed = tasks.pop(idx - 1)
        print(f"Задача '{removed.name}' удалена.")
    except Exception as e:
        print("Ошибка при удалении задачи:", e)

def save_all_tasks(tasks):
    with open(FILEPATH, "w", encoding="utf8") as f:
        for task in tasks:
            date_str = task.date_complete if task.date_complete else ""
            if date_str and not date_str.startswith("["):
                date_str = f"[{date_str}]"
            f.write(f"{task.id}{SEPARATOR}{task.name}{SEPARATOR}{date_str}{SEPARATOR}{task.created_at}{SEPARATOR}{task.status}\n")

def main_menu():
    while True:
        print("\nВыберите действие:")
        print("1. Просмотр задач")
        print("2. Добавить задачу")
        print("3. Редактировать задачу")
        print("4. Удалить задачу")
        print("5. Выход")
        choice = input("Введите номер действия: ").strip()
        tasks = parse_tasks()
        if choice == "1":
            print_readable(tasks)
        elif choice == "2":
            make_new_task()
        elif choice == "3":
            edit_task(tasks)
            save_all_tasks(tasks)
        elif choice == "4":
            delete_task(tasks)
            save_all_tasks(tasks)
        elif choice == "5":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main_menu()