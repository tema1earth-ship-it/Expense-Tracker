import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime
import os

# --- Глобальные переменные ---
expenses = []  # Список для хранения расходов


# --- Функции для работы с данными ---

def load_data():
    """Загружает расходы из файла expenses.json, если он существует."""
    global expenses
    if os.path.exists("expenses.json"):
        try:
            with open("expenses.json", "r", encoding="utf-8") as f:
                expenses = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
            expenses = []
    else:
        expenses = []


def save_data():
    """Сохраняет список расходов в файл expenses.json."""
    try:
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(expenses, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")


# --- Функции для валидации и логики ---

def validate_input(amount_str, date_str):
    """Проверяет корректность введённых суммы и даты."""
    try:
        amount = float(amount_str)
        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
            return False
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректный формат суммы")
        return False

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректный формат даты (используйте ГГГГ-ММ-ДД)")
        return False

    return True


def add_expense():
    """Обрабатывает добавление нового расхода."""
    amount_str = amount_entry.get()
    category = category_combo.get()
    date_str = date_entry.get()

    if not all([amount_str, category, date_str]):
        messagebox.showerror("Ошибка", "Заполните все поля")
        return

    if not validate_input(amount_str, date_str):
        return

    expense = {
        "id": len(expenses) + 1,
        "amount": float(amount_str),
        "category": category,
        "date": date_str
    }

    expenses.append(expense)
    save_data()
    refresh_table()
    clear_input()


def clear_input():
    """Очищает поля ввода после добавления расхода."""
    amount_entry.delete(0, tk.END)
    category_combo.set("")
    date_entry.delete(0, tk.END)


# --- Функции для отображения и фильтрации ---

def refresh_table(filtered_expenses=None):
    """Обновляет таблицу расходов. Если передан список filtered_expenses, отображает его."""
    data = filtered_expenses if filtered_expenses is not None else expenses

    # Очищаем текущую таблицу
    for item in tree.get_children():
        tree.delete(item)

    # Заполняем таблицу данными
    for expense in data:
        tree.insert("", "end", values=(
            expense["id"],
            f"{expense['amount']:.2f} руб.",
            expense["category"],
            expense["date"]
        ))


def apply_filter():
    """Применяет фильтры по категории и дате к таблице расходов."""
    filtered = expenses.copy()

    # Фильтр по категории
    category_filter = filter_category.get()
    if category_filter != "Все":
        filtered = [e for e in filtered if e["category"] == category_filter]

    # Фильтр по дате (начало)
    start_date_str = start_date_entry.get()
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= start_date]
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат начальной даты")
            return

    # Фильтр по дате (конец)
    end_date_str = end_date_entry.get()
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= end_date]
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат конечной даты")
            return

    refresh_table(filtered)


def calculate_total():
    """Считает и отображает сумму расходов за выбранный период."""
    total = 0.0
    start_date_str = start_date_entry.get()
    end_date_str = end_date_entry.get()

    # Если даты не указаны, считаем все расходы
    if not start_date_str and not end_date_str:
        total = sum(expense["amount"] for expense in expenses)
    else:
        filtered_expenses = expenses.copy()

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                filtered_expenses = [e for e in filtered_expenses if
                                     datetime.strptime(e["date"], "%Y-%m-%d") >= start_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат начальной даты")
                return

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                filtered_expenses = [e for e in filtered_expenses if
                                     datetime.strptime(e["date"], "%Y-%m-%d") <= end_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат конечной даты")
                return

        total = sum(expense["amount"] for expense in filtered_expenses)

    total_label.config(text=f"Общая сумма: {total:.2f} руб.")


# --- Создание главного окна ---
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("800x600")

# Загрузка данных при запуске
load_data()

# --- Создание интерфейса ---

# Фрейм для ввода данных
input_frame = ttk.Frame(root)
input_frame.pack(pady=10)

ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5)
amount_entry = ttk.Entry(input_frame)
amount_entry.grid(row=0, column=1, padx=5)

ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5)
category_combo = ttk.Combobox(
    input_frame,
    values=["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
)
category_combo.grid(row=0, column=3, padx=5)

ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5)
date_entry = ttk.Entry(input_frame)
date_entry.grid(row=0, column=5, padx=5)

add_button = ttk.Button(input_frame, text="Добавить расход", command=add_expense)
add_button.grid(row=0, column=6, padx=5)

# Таблица расходов
columns = ("ID", "Сумма", "Категория", "Дата")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.pack(padx=10, pady=10, fill="both", expand=True)
refresh_table()  # Первоначальное заполнение таблицы

# Фрейм для фильтрации и подсчёта
filter_frame = ttk.Frame(root)
filter_frame.pack(pady=10)

ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, padx=5)
filter_category = ttk.Combobox(
    filter_frame,
    values=["Все"] + ["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
)
filter_category.set("Все")
filter_category.grid(row=0, column=1, padx=5)

ttk.Label(filter_frame, text="С даты (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
start_date_entry = ttk.Entry(filter_frame)
start_date_entry.grid(row=0, column=3, padx=5)

ttk.Label(filter_frame, text="По дату (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5)
end_date_entry = ttk.Entry(filter_frame)
end_date_entry.grid(row=0, column=5, padx=5)

filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=apply_filter)
filter_button.grid(row=0, column=6, padx=5)

total_button = ttk.Button(filter_frame, text="Подсчитать сумму за период", command=calculate_total)
total_button.grid(row=0, column=7, padx=5)

total_label = ttk.Label(root, text="Общая сумма: 0 руб.")
total_label.pack(pady=5)

# Запуск приложения
root.mainloop()
