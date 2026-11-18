import os
import sqlite3
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

APP_NAME = "Student Management System"
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "admin123"


def db_path():
    return os.path.join(App.get_running_app().user_data_dir, "students.db")


def connect_db():
    conn = sqlite3.connect(db_path())
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            year_level TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    return conn


def make_button(text, callback, color=(0.13, 0.36, 0.72, 1), height=dp(48)):
    b = Button(text=text, size_hint_y=None, height=height,
               background_normal="", background_color=color,
               color=(1, 1, 1, 1), font_size="15sp")
    b.bind(on_release=callback)
    return b


def show_message(title, message):
    box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
    box.add_widget(Label(text=message, halign="center", valign="middle"))
    close = Button(text="OK", size_hint_y=None, height=dp(44))
    popup = Popup(title=title, content=box, size_hint=(.86, .36), auto_dismiss=True)
    close.bind(on_release=popup.dismiss)
    box.add_widget(close)
    popup.open()


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=[dp(24), dp(35)], spacing=dp(14))
        root.add_widget(Label(text="[b]STUDENT MANAGEMENT SYSTEM[/b]",
                              markup=True, font_size="23sp", size_hint_y=None, height=dp(90)))
        root.add_widget(Label(text="Admin Login", font_size="18sp",
                              size_hint_y=None, height=dp(40)))
        self.username = TextInput(hint_text="Username", multiline=False,
                                  size_hint_y=None, height=dp(50), font_size="17sp")
        self.password = TextInput(hint_text="Password", password=True, multiline=False,
                                  size_hint_y=None, height=dp(50), font_size="17sp")
        root.add_widget(self.username)
        root.add_widget(self.password)
        root.add_widget(make_button("LOGIN", self.login))
        root.add_widget(Label(text="Demo login: admin / admin123",
                              font_size="13sp", color=(.4, .45, .5, 1)))
        self.add_widget(root)

    def login(self, *_):
        if self.username.text.strip() == DEFAULT_USER and self.password.text == DEFAULT_PASSWORD:
            self.manager.current = "home"
            self.password.text = ""
        else:
            show_message("Login failed", "Incorrect username or password.")


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(22), spacing=dp(16))
        root.add_widget(Label(text="[b]Welcome, Administrator![/b]",
                              markup=True, font_size="24sp", size_hint_y=None, height=dp(100)))
        root.add_widget(Label(text="Student Management System\nManage student records in one place.",
                              halign="center", font_size="17sp"))
        root.add_widget(make_button("OPEN STUDENT DASHBOARD", self.open_dashboard))
        root.add_widget(make_button("LOG OUT", self.logout, (0.75, 0.18, 0.2, 1)))
        self.add_widget(root)

    def open_dashboard(self, *_):
        self.manager.current = "dashboard"
        self.manager.get_screen("dashboard").refresh_students()

    def logout(self, *_):
        self.manager.current = "login"


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_id = None
        self.fields = {}

        outer = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        top = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        top.add_widget(Label(text="[b]ADMIN DASHBOARD[/b]", markup=True, font_size="19sp"))
        top.add_widget(make_button("HOME", self.go_home, height=dp(42)))
        top.add_widget(make_button("LOG OUT", self.logout, (0.75, .18, .2, 1), dp(42)))
        outer.add_widget(top)

        self.total = Label(text="Total students: 0", size_hint_y=None, height=dp(30),
                           color=(.12, .3, .58, 1), font_size="16sp")
        outer.add_widget(self.total)

        form_scroll = ScrollView(size_hint_y=None, height=dp(270))
        form = GridLayout(cols=2, spacing=dp(7), padding=dp(4),
                          size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))
        labels = [
            ("Student ID", "student_id"),
            ("Full Name", "name"),
            ("Course", "course"),
            ("Year Level", "year_level"),
            ("Email", "email"),
            ("Phone", "phone")
        ]
        for label, key in labels:
            form.add_widget(Label(text=label, size_hint_y=None, height=dp(46),
                                  halign="left", valign="middle"))
            field = TextInput(hint_text=label, multiline=False,
                              size_hint_y=None, height=dp(46), font_size="15sp")
            self.fields[key] = field
            form.add_widget(field)
        form_scroll.add_widget(form)
        outer.add_widget(form_scroll)

        actions = GridLayout(cols=2, spacing=dp(7), size_hint_y=None, height=dp(105))
        actions.add_widget(make_button("ADD STUDENT", self.add_student, (0.12, .58, .32, 1)))
        actions.add_widget(make_button("UPDATE", self.update_student))
        actions.add_widget(make_button("DELETE", self.delete_student, (0.75, .18, .2, 1)))
        actions.add_widget(make_button("CLEAR FORM", self.clear_form, (.4, .45, .5, 1)))
        outer.add_widget(actions)

        search_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.search = TextInput(hint_text="Search name, ID, or course",
                                multiline=False, font_size="14sp")
        search_row.add_widget(self.search)
        search_row.add_widget(make_button("SEARCH", self.search_students, height=dp(48)))
        search_row.add_widget(make_button("ALL", self.refresh_students, (.4, .45, .5, 1), dp(48)))
        outer.add_widget(search_row)

        self.list_scroll = ScrollView()
        self.student_list = GridLayout(cols=1, spacing=dp(6), padding=[0, dp(4)],
                                       size_hint_y=None)
        self.student_list.bind(minimum_height=self.student_list.setter("height"))
        self.list_scroll.add_widget(self.student_list)
        outer.add_widget(self.list_scroll)
        self.add_widget(outer)

    def values(self):
        return {k: v.text.strip() for k, v in self.fields.items()}

    def clear_form(self, *_):
        for field in self.fields.values():
            field.text = ""
        self.selected_id = None

    def validate(self, data):
        required = ["student_id", "name", "course", "year_level"]
        if any(not data[k] for k in required):
            show_message("Missing information", "Please fill in Student ID, Full Name, Course, and Year Level.")
            return False
        return True

    def add_student(self, *_):
        data = self.values()
        if not self.validate(data):
            return
        try:
            with connect_db() as conn:
                conn.execute("""INSERT INTO students
                    (student_id, name, course, year_level, email, phone)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    tuple(data[k] for k in ["student_id", "name", "course", "year_level", "email", "phone"]))
            show_message("Success", "Student added successfully.")
            self.clear_form()
            self.refresh_students()
        except sqlite3.IntegrityError:
            show_message("Duplicate ID", "That Student ID already exists.")
        except sqlite3.Error as e:
            show_message("Database error", str(e))

    def refresh_students(self, *_):
        self.search.text = ""
        self.load_rows()

    def search_students(self, *_):
        term = self.search.text.strip()
        self.load_rows(term)

    def load_rows(self, term=""):
        self.student_list.clear_widgets()
        try:
            with connect_db() as conn:
                if term:
                    like = f"%{term}%"
                    rows = conn.execute("""SELECT id, student_id, name, course, year_level, email, phone
                        FROM students WHERE student_id LIKE ? OR name LIKE ? OR course LIKE ?
                        ORDER BY id DESC""", (like, like, like)).fetchall()
                else:
                    rows = conn.execute("""SELECT id, student_id, name, course, year_level, email, phone
                        FROM students ORDER BY id DESC""").fetchall()
            self.total.text = f"Students shown: {len(rows)}"
            if not rows:
                self.student_list.add_widget(Label(text="No student records found.",
                                                   size_hint_y=None, height=dp(55)))
            for row in rows:
                sid, student_id, name, course, year, email, phone = row
                card = BoxLayout(orientation="vertical", padding=dp(9),
                                 spacing=dp(4), size_hint_y=None, height=dp(132))
                card.add_widget(Label(
                    text=f"[b]{name}[/b]  |  {student_id}\n{course} - {year}\n{email}  |  {phone}",
                    markup=True, halign="left", valign="middle", font_size="13sp"))
                card.add_widget(make_button("SELECT / EDIT", lambda _btn, r=row: self.select_row(r),
                                            (.25, .42, .62, 1), dp(38)))
                self.student_list.add_widget(card)
        except sqlite3.Error as e:
            show_message("Database error", str(e))

    def select_row(self, row):
        self.selected_id = row[0]
        keys = ["student_id", "name", "course", "year_level", "email", "phone"]
        for key, value in zip(keys, row[1:]):
            self.fields[key].text = value or ""
        show_message("Student selected", "You can now update or delete this record.")

    def update_student(self, *_):
        if self.selected_id is None:
            show_message("Select a student", "Tap SELECT / EDIT on a student record first.")
            return
        data = self.values()
        if not self.validate(data):
            return
        try:
            with connect_db() as conn:
                conn.execute("""UPDATE students SET student_id=?, name=?, course=?,
                    year_level=?, email=?, phone=? WHERE id=?""",
                    tuple(data[k] for k in ["student_id", "name", "course", "year_level", "email", "phone"])
                    + (self.selected_id,))
            show_message("Success", "Student information updated.")
            self.clear_form()
            self.refresh_students()
        except sqlite3.IntegrityError:
            show_message("Duplicate ID", "That Student ID already exists.")
        except sqlite3.Error as e:
            show_message("Database error", str(e))

    def delete_student(self, *_):
        if self.selected_id is None:
            show_message("Select a student", "Tap SELECT / EDIT on a student record first.")
            return
        content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        content.add_widget(Label(text="Delete this student record?"))
        buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        popup = Popup(title="Confirm delete", content=content, size_hint=(.85, .3))
        yes = Button(text="DELETE", background_color=(.75, .18, .2, 1))
        no = Button(text="CANCEL")
        buttons.add_widget(yes)
        buttons.add_widget(no)
        content.add_widget(buttons)
        yes.bind(on_release=lambda *_: self.confirm_delete(popup))
        no.bind(on_release=popup.dismiss)
        popup.open()

    def confirm_delete(self, popup):
        try:
            with connect_db() as conn:
                conn.execute("DELETE FROM students WHERE id=?", (self.selected_id,))
            popup.dismiss()
            self.clear_form()
            self.refresh_students()
            show_message("Deleted", "Student record deleted.")
        except sqlite3.Error as e:
            popup.dismiss()
            show_message("Database error", str(e))

    def go_home(self, *_):
        self.manager.current = "home"

    def logout(self, *_):
        self.manager.current = "login"


class StudentApp(App):
    def build(self):
        self.title = APP_NAME
        connect_db()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        return sm


if __name__ == "__main__":
    StudentApp().run()
