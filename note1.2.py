import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class Note:
    def __init__(self, nid, title, priority, created, text):
        self.nid = nid
        self.title = title
        self.priority = priority
        self.created = created
        self.text = text


class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notex Pro v4.1 - Уникальные заметки")
        self.root.geometry("750x400")  # Фиксированный размер окна
        self.root.resizable(True, True)

        self.notes = []
        self.current_note_id = None

        # Конфигурация пути
        self.NOTES_DIR = r"C:\NotexNotes"
        if not os.path.exists(self.NOTES_DIR):
            os.makedirs(self.NOTES_DIR)

        # GUI
        self.setup_ui()
        self.load_notes()

    def setup_ui(self):
        # Настройка фреймов
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)

        # Дерево заметок
        self.tree = ttk.Treeview(left_frame, columns=("id", "title", "priority", "created"), show="headings", height=18)
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Заголовок")
        self.tree.heading("priority", text="Приоритет")
        self.tree.heading("created", text="Дата создания")

        self.tree.column("id", width=30, anchor=tk.CENTER)
        self.tree.column("title", width=150)
        self.tree.column("priority", width=80, anchor=tk.CENTER)
        self.tree.column("created", width=120, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.edit_note)
        self.tree.bind("<Button-3>", self.show_context_menu)  # Привязка контекстного меню к правой кнопке мыши

        # Создаем контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_selected_note)
        self.context_menu.add_command(label="Удалить", command=self.delete_selected_note)

        # Поля ввода на правой панели
        ttk.Label(right_frame, text="Введите заголовок заметки").grid(row=0, column=0, sticky="w", pady=5)
        self.title_entry = ttk.Entry(right_frame, width=30)
        self.title_entry.grid(row=1, column=0, sticky="ew", pady=2)

        ttk.Label(right_frame, text="Приоритет:").grid(row=2, column=0, sticky="w", pady=5)
        self.priority_var = tk.StringVar(value="Средний")
        priority_combo = ttk.Combobox(right_frame, textvariable=self.priority_var,
                                      values=["Низкий", "Средний", "Высокий"], state="readonly")
        priority_combo.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(right_frame, text="Введите текст заметки").grid(row=3, column=0, sticky="w", pady=5)
        self.note_text = tk.Text(right_frame, wrap=tk.WORD, width=30, height=10)
        self.note_text.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=2)

        # Чекбокс "Спрашивать при создании"
        self.ask_when_creating = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_frame, text="Спрашивать при создании новой заметки",
                        variable=self.ask_when_creating).grid(row=5, column=0, columnspan=2, sticky="w", pady=10)

        # Кнопки действий
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Button(buttons_frame, text="Новая заметка", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_note).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Удалить", command=self.delete_selected_note).pack(side=tk.RIGHT, padx=5)

    def save_note(self):
        title = self.title_entry.get().strip()
        text = self.note_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()

        if not title:
            messagebox.showwarning("Ошибка", "Введите заголовок заметки!")
            return

        if self.current_note_id is None:
            # Новая заметка
            nid = len(self.notes) + 1 if self.notes else 1
            created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note = Note(nid, title, priority, created, text)
            self.notes.append(note)
            self.tree.insert('', tk.END, values=(nid, title, priority, created))
        else:
            # Редактирование существующей
            for note in self.notes:
                if note.nid == self.current_note_id:
                    note.title = title
                    note.priority = priority
                    note.text = text
                    # Обновление в дереве
                    for item in self.tree.get_children():
                        vals = self.tree.item(item, 'values')
                        if int(vals[0]) == self.current_note_id:
                            self.tree.item(item, values=(note.nid, note.title, note.priority, note.created))
                            break

        self.save_note_to_file(note)
        self.clear_fields()
        messagebox.showinfo("Информация", "Заметка успешно сохранена!")

    def save_note_to_file(self, note):
        filename = os.path.join(self.NOTES_DIR, f"note_{note.nid}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{note.title}\n{note.priority}\n{note.created}\n{note.text}")

    def load_notes(self):
        if not os.path.exists(self.NOTES_DIR):
            return

        for fname in os.listdir(self.NOTES_DIR):
            if fname.startswith("note_") and fname.endswith(".txt"):
                try:
                    with open(os.path.join(self.NOTES_DIR, fname), encoding="utf-8") as f:
                        lines = f.read().split('\n', 3)
                        if len(lines) == 4:
                            nid = int(fname.split("_")[1].split(".")[0])
                            title, priority, created, text = lines
                            self.notes.append(Note(nid, title, priority, created, text))
                            self.tree.insert('', tk.END, values=(nid, title, priority, created))
                except Exception as e:
                    print(f"Ошибка загрузки файла {fname}: {e}")

    def edit_note(self, event):
        selected = self.tree.selection()
        if selected:
            self.edit_selected_note()

    def edit_selected_note(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите заметку для редактирования")
            return

        item = self.tree.item(selected[0])
        self.current_note_id = int(item['values'][0])
        note = next((n for n in self.notes if n.nid == self.current_note_id), None)

        if note:
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, note.title)
            self.priority_var.set(note.priority)
            self.note_text.delete("1.0", tk.END)
            self.note_text.insert("1.0", note.text)

    def delete_selected_note(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите заметку для удаления")
            return

        item = self.tree.item(selected[0])
        note_id = int(item['values'][0])

        if messagebox.askyesno("Удаление", "Вы действительно хотите удалить заметку?"):
            # Удаление из интерфейса
            self.tree.delete(selected[0])

            # Удаление из списка
            self.notes = [note for note in self.notes if note.nid != note_id]

            # Удаление файла
            try:
                file_path = os.path.join(self.NOTES_DIR, f"note_{note_id}.txt")
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Ошибка при удалении файла: {e}")

            self.clear_fields()

    def show_context_menu(self, event):
        # Показать контекстное меню при правом клике
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def clear_fields(self):
        self.current_note_id = None
        self.title_entry.delete(0, tk.END)
        self.note_text.delete("1.0", tk.END)
        self.priority_var.set("Средний")


if __name__ == "__main__":
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()
