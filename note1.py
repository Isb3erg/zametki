import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Класс для Entry с плейсхолдером
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg'] if 'fg' in kwargs else 'black'
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _clear_placeholder(self, e):
        if self['fg'] == self.placeholder_color:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def _add_placeholder(self, e=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color

    def get_value(self):
        if self['fg'] == self.placeholder_color:
            return ""
        return self.get()

    def clear(self):
        self.delete(0, tk.END)
        self._add_placeholder()

# Класс для Text с плейсхолдером
class PlaceholderText(tk.Text):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg'] if 'fg' in kwargs else 'black'
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _clear_placeholder(self, e=None):
        if self.tag_ranges("placeholder"):
            self.delete("1.0", tk.END)
            self['fg'] = self.default_fg_color
            self.tag_remove("placeholder", "1.0", tk.END)

    def _add_placeholder(self, e=None):
        if not self.get("1.0", tk.END).strip():
            self.insert("1.0", self.placeholder)
            self['fg'] = self.placeholder_color
            self.tag_add("placeholder", "1.0", tk.END)
            self.tag_configure("placeholder", foreground=self.placeholder_color)

    def get_value(self):
        if self.tag_ranges("placeholder"):
            return ""
        return self.get("1.0", tk.END).strip()

    def clear(self):
        self.delete("1.0", tk.END)
        self._add_placeholder()

# Класс заметки
class Note:
    def __init__(self, nid, title, priority, created, text):
        self.nid = nid
        self.title = title
        self.priority = priority
        self.created = created
        self.text = text

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notex Pro v4.1 - Уникальные заметки")
        self.notes = []
        self.current_note_id = None
        self.ask_on_new = tk.BooleanVar(value=True)
        self.setup_style()
        self.create_widgets()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background='#f5f5f5', foreground='black', fieldbackground='#f5f5f5', font=('Segoe UI', 10))
        style.configure('Treeview.Heading', background='#d5d5d5', foreground='black', font=('Segoe UI', 10, 'bold'))
        style.configure('TButton', background='#b2c9d6', foreground='black', font=('Segoe UI', 10, 'bold'))
        style.map('TButton', background=[('active', '#a0b6c3')])
        style.configure('TCheckbutton', background='#f0f0f0', foreground='black', font=('Segoe UI', 9))

    def create_widgets(self):
        # Левая часть - таблица заметок
        self.tree = ttk.Treeview(self.root, columns=('ID', 'Title', 'Priority', 'Created'), show='headings', height=15)
        self.tree.heading('ID', text='ID')
        self.tree.heading('Title', text='Заголовок')
        self.tree.heading('Priority', text='Приоритет')
        self.tree.heading('Created', text='Дата создания')
        self.tree.column('ID', width=40, anchor='center')
        self.tree.column('Title', width=180)
        self.tree.column('Priority', width=90, anchor='center')
        self.tree.column('Created', width=150, anchor='center')
        self.tree.grid(row=0, column=0, rowspan=3, sticky='nsew', padx=8, pady=8)
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Double-1>', self.edit_note_from_tree)

        # Правая часть - форма заметки
        frm = tk.Frame(self.root, bg="#e0e0e0")
        frm.grid(row=0, column=1, sticky='nsew', padx=(0,8), pady=8)

        self.entry_title = PlaceholderEntry(frm, placeholder="Введите заголовок заметки", font=('Segoe UI', 11), width=30, bg="#e0e0e0", relief=tk.FLAT)
        self.entry_title.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0,5), padx=4)

        tk.Label(frm, text="Приоритет:", bg="#e0e0e0", fg="black", font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', padx=4)
        self.priority_var = tk.StringVar(value="Средний")
        self.cmb_priority = ttk.Combobox(frm, textvariable=self.priority_var, values=["Низкий", "Средний", "Высокий"], state="readonly", width=10)
        self.cmb_priority.grid(row=1, column=1, sticky='e', padx=4, pady=(0,5))

        self.txt_note = PlaceholderText(frm, placeholder="Введите текст заметки", font=('Segoe UI', 11), height=6, width=30, bg="#e0e0e0", relief=tk.FLAT)
        self.txt_note.grid(row=2, column=0, columnspan=2, pady=(0,5), padx=4)

        # Нижняя панель
        self.chk_ask = ttk.Checkbutton(frm, text="Спрашивать при создании новой заметки", variable=self.ask_on_new)
        self.chk_ask.grid(row=3, column=0, columnspan=2, sticky='w', padx=4, pady=(0,5))

        btn_frame = tk.Frame(frm, bg="#e0e0e0")
        btn_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(0,5))
        ttk.Button(btn_frame, text="Новая заметка", command=self.new_note).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Сохранить", command=self.save_note).pack(side=tk.LEFT, padx=4)

        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_note_from_menu)
        self.context_menu.add_command(label="Удалить", command=self.delete_note)

        # Настройка grid
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def new_note(self):
        if self.ask_on_new.get() and self.is_note_modified():
            if not messagebox.askyesno("Подтверждение", "Текущая заметка не сохранена. Создать новую?"):
                return
        self.current_note_id = None
        self.entry_title.clear()
        self.priority_var.set("Средний")
        self.txt_note.clear()

    def save_note(self):
        title = self.entry_title.get_value().strip()
        text = self.txt_note.get_value().strip()
        priority = self.priority_var.get()
        if not title:
            messagebox.showwarning("Ошибка", "Введите заголовок заметки!")
            return
        if self.current_note_id is None:
            nid = len(self.notes) + 1
            created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note = Note(nid, title, priority, created, text)
            self.notes.append(note)
            self.tree.insert('', tk.END, values=(nid, title, priority, created))
        else:
            for note in self.notes:
                if note.nid == self.current_note_id:
                    note.title = title
                    note.priority = priority
                    note.text = text
                    # Обновить в дереве
                    for item in self.tree.get_children():
                        vals = self.tree.item(item, 'values')
                        if int(vals[0]) == self.current_note_id:
                            self.tree.item(item, values=(note.nid, note.title, note.priority, note.created))
        self.current_note_id = None
        self.entry_title.clear()
        self.txt_note.clear()
        self.priority_var.set("Средний")

    def is_note_modified(self):
        return self.entry_title.get_value().strip() or self.txt_note.get_value().strip()

    def show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.context_menu.post(event.x_root, event.y_root)

    def edit_note_from_tree(self, event):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            vals = self.tree.item(item, 'values')
            nid = int(vals[0])
            for note in self.notes:
                if note.nid == nid:
                    self.current_note_id = nid
                    self.entry_title.clear()
                    self.entry_title.insert(0, note.title)
                    self.entry_title['fg'] = self.entry_title.default_fg_color
                    self.priority_var.set(note.priority)
                    self.txt_note.clear()
                    self.txt_note.insert('1.0', note.text)
                    self.txt_note['fg'] = self.txt_note.default_fg_color
                    break

    def edit_note_from_menu(self):
        self.edit_note_from_tree(None)

    def delete_note(self):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            vals = self.tree.item(item, 'values')
            nid = int(vals[0])
            self.tree.delete(item)
            self.notes = [note for note in self.notes if note.nid != nid]
            self.new_note()

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
