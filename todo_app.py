import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton,
    QLabel, QListWidget, QLineEdit, QDialog, QDialogButtonBox,
    QFormLayout, QWidget, QTabWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from openai import OpenAI
import re 
from dotenv import load_dotenv  # Add this import
import os



# Load environment variables first
load_dotenv()


# Initialize OpenAI client

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Modified line

# client = OpenAI(api_key=your_api_key_here)


class TaskApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List")
        self.setGeometry(100, 100, 500, 600)

        # Initialize the database
        self.initialize_database()

        # Set application-wide styles
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 18px;
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#deleteTabButton {
                background-color: #f44336; /* Red button for delete */
            }
            QPushButton#deleteTabButton:hover {
                background-color: #d32f2f;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                padding: 5px;
                color: #000;  /* Text color */
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: #f9f9f9;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 5px;
                margin: 2px;
                border-radius: 3px;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
        """)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # ChatGPT Button
        self.chatgpt_button = QPushButton("Ask ChatGPT")
        self.chatgpt_button.clicked.connect(self.ask_chatgpt)
        self.layout.addWidget(self.chatgpt_button)

        # Title
        self.title_label = QLabel("My To-Do List", alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Tabs for different dates
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Add Task Button
        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.show_add_task_dialog)
        self.layout.addWidget(self.add_task_button)

        # Mark as Done Button
        self.mark_done_button = QPushButton("Mark as Done")
        self.mark_done_button.clicked.connect(self.mark_task_done)
        self.layout.addWidget(self.mark_done_button)

        # Mark as Undone Button
        self.mark_undone_button = QPushButton("Mark as Undone")
        self.mark_undone_button.clicked.connect(self.mark_task_undone)
        self.layout.addWidget(self.mark_undone_button)

        # Delete Task Button
        self.delete_task_button = QPushButton("Delete Task")
        self.delete_task_button.clicked.connect(self.delete_task)
        self.layout.addWidget(self.delete_task_button)

        # Add New Date Tab Button
        self.add_tab_button = QPushButton("Add New Date")
        self.add_tab_button.clicked.connect(self.add_new_tab)
        self.layout.addWidget(self.add_tab_button)

        # Delete Tab Button
        self.delete_tab_button = QPushButton("Delete Tab")
        self.delete_tab_button.setObjectName("deleteTabButton")
        self.delete_tab_button.clicked.connect(self.delete_tab)
        self.layout.addWidget(self.delete_tab_button)

        # Load data from the database
        self.load_data()

    def initialize_database(self):
        """Initialize the SQLite database and create tables."""
        self.conn = sqlite3.connect("todo_app.db")
        self.cursor = self.conn.cursor()

        # Create tables for tabs and tasks
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tabs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tab_name TEXT NOT NULL,
                description TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (tab_name) REFERENCES tabs (name) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def load_data(self):
        """Load tabs and tasks from the database."""
        self.cursor.execute("SELECT name FROM tabs")
        tabs = self.cursor.fetchall()

        for (tab_name,) in tabs:
            task_list = self.add_tab(tab_name)

            self.cursor.execute("SELECT description, done FROM tasks WHERE tab_name = ?", (tab_name,))
            tasks = self.cursor.fetchall()
            for description, done in tasks:
                item = QListWidgetItem(description)
                if done:
                    item.setText(f"{description} (Done)")
                    item.setForeground(Qt.GlobalColor.gray)
                task_list.addItem(item)

    def add_tab(self, date):
        """Add a new tab for the specified date and return its task list."""
        tab = QWidget()
        layout = QVBoxLayout()
        task_list = QListWidget()  # Create the task list widget
        layout.addWidget(task_list)
        tab.setLayout(layout)

        # Add the tab to the tab widget
        self.tabs.addTab(tab, date)
        self.tabs.setCurrentWidget(tab)  # Automatically switch to the newly created tab

        # Save the tab to the database
        self.cursor.execute("INSERT OR IGNORE INTO tabs (name) VALUES (?)", (date,))
        self.conn.commit()

        print(f"Added tab '{date}' with associated task list.")  # Debugging
        return task_list



    def add_new_tab(self):
        """Dialog to add a new date tab."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Date Tab")

        layout = QFormLayout()
        date_input = QLineEdit()
        layout.addRow("Date:", date_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        if dialog.exec():
            date = date_input.text().strip()
            if date:
                self.add_tab(date)

    def delete_tab(self):
        """Delete the currently selected tab."""
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            tab_name = self.tabs.tabText(current_index)
            self.cursor.execute("DELETE FROM tabs WHERE name = ?", (tab_name,))
            self.cursor.execute("DELETE FROM tasks WHERE tab_name = ?", (tab_name,))
            self.conn.commit()
            self.tabs.removeTab(current_index)

    def current_task_list(self):
        """Get the task list of the currently active tab."""
        current_tab = self.tabs.currentWidget()
        if current_tab is None:
            print("No active tab found.")  # Debugging
            return None
        layout = current_tab.layout()
        if layout is None or layout.count() == 0:
            print("No layout or empty layout for the current tab.")  # Debugging
            return None
        task_list_widget = layout.itemAt(0).widget()
        if not isinstance(task_list_widget, QListWidget):
            print("No valid task list found in the current tab.")  # Debugging
            return None
        return task_list_widget




    def show_add_task_dialog(self):
        """Dialog to add a new task."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Task")

        layout = QFormLayout()
        task_input = QLineEdit()
        layout.addRow("Task:", task_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        if dialog.exec():
            task = task_input.text()
            if task:
                task_list = self.current_task_list()
                if task_list:
                    task_list.addItem(task)
                    current_tab = self.tabs.tabText(self.tabs.currentIndex())
                    self.cursor.execute(
                        "INSERT INTO tasks (tab_name, description, done) VALUES (?, ?, ?)",
                        (current_tab, task, False)
                    )
                    self.conn.commit()

    def mark_task_done(self):
        """Mark selected task as done."""
        task_list = self.current_task_list()
        if task_list:
            selected_items = task_list.selectedItems()
            for item in selected_items:
                if "(Done)" not in item.text():
                    description = item.text()
                    item.setText(f"{description} (Done)")
                    item.setForeground(Qt.GlobalColor.gray)
                    current_tab = self.tabs.tabText(self.tabs.currentIndex())
                    self.cursor.execute(
                        "UPDATE tasks SET done = ? WHERE tab_name = ? AND description = ?",
                        (True, current_tab, description)
                    )
                    self.conn.commit()

    def mark_task_undone(self):
        """Mark selected task as undone."""
        task_list = self.current_task_list()
        if task_list:
            selected_items = task_list.selectedItems()
            for item in selected_items:
                if "(Done)" in item.text():
                    description = item.text().replace(" (Done)", "")
                    item.setText(description)
                    item.setForeground(Qt.GlobalColor.black)
                    current_tab = self.tabs.tabText(self.tabs.currentIndex())
                    self.cursor.execute(
                        "UPDATE tasks SET done = ? WHERE tab_name = ? AND description = ?",
                        (False, current_tab, description)
                    )
                    self.conn.commit()

    def delete_task(self):
        """Delete selected task."""
        task_list = self.current_task_list()
        if task_list:
            selected_items = task_list.selectedItems()
            for item in selected_items:
                description = item.text()
                task_list.takeItem(task_list.row(item))
                current_tab = self.tabs.tabText(self.tabs.currentIndex())
                self.cursor.execute(
                    "DELETE FROM tasks WHERE tab_name = ? AND description = ?",
                    (current_tab, description)
                )
                self.conn.commit()

    def ask_chatgpt(self):
        """Interact with ChatGPT."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ask ChatGPT")

        layout = QVBoxLayout()
        prompt_input = QLineEdit()
        layout.addWidget(prompt_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        if dialog.exec():
            prompt = prompt_input.text()
            if prompt:
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an assistant for a to-do list app. Respond concisely and format lists with bullet points."},  # Improved instruction
                            {"role": "user", "content": prompt}
                        ]
                    )
                    reply = response.choices[0].message.content.strip()
                    self.handle_chatgpt_response(reply)
                except Exception as e:
                    error_dialog = QDialog(self)
                    error_dialog.setWindowTitle("Error")
                    layout = QVBoxLayout()
                    layout.addWidget(QLabel(f"Error: {e}"))
                    error_dialog.setLayout(layout)
                    error_dialog.exec()


    def handle_chatgpt_response(self, reply):
        """Process ChatGPT's response with enhanced parsing and preview."""
        print(f"ChatGPT reply: {reply}")

        # Validate active tab
        current_tab_index = self.tabs.currentIndex()
        if current_tab_index == -1:
            self.show_error("No active tab selected!")
            return

        current_tab_name = self.tabs.tabText(current_tab_index)
        current_task_list = self.current_task_list()
        if current_task_list is None:
            self.show_error(f"No task list found in tab: {current_tab_name}")
            return

        # Parse tasks with multi-line support
        try:
            task_lines = self.parse_tasks_from_response(reply)
            if not task_lines:
                self.show_error("No valid tasks found in ChatGPT response")
                return
        except Exception as e:
            self.show_error(f"Error parsing tasks: {str(e)}")
            return

        # Show preview dialog
        confirmed_tasks = self.show_preview_dialog(task_lines)
        if not confirmed_tasks:
            return  # User canceled

        # Add validated tasks
        try:
            for task in confirmed_tasks:
                if task:  # Skip empty tasks
                    self.add_task_to_system(current_tab_name, task)
            print(f"Tasks added to '{current_tab_name}': {confirmed_tasks}")
        except Exception as e:
            self.show_error(f"Error saving tasks: {str(e)}")
        
        

    
    def parse_tasks_from_response(self, reply):
        """Improved parser with multi-line task support."""
        task_lines = []
        current_task = None
        pattern = re.compile(r'^(\d+[.)]|[-*•])\s+')  # Bullet/number pattern
        
        for line in reply.split('\n'):
            stripped = line.strip()
            
            # Start new task if bullet found
            if pattern.match(stripped):
                if current_task is not None:  # Save previous task
                    task_lines.append(current_task)
                current_task = pattern.sub('', stripped).strip()
            # Continue existing task if indented line
            elif current_task is not None and stripped:
                current_task += '\n' + stripped
        
        # Add final task if exists
        if current_task is not None:
            task_lines.append(current_task)
        
        # Fallback to comma-separation if no bullets
        if not task_lines and ',' in reply:
            task_lines = [t.strip() for t in reply.split(',') if t.strip()]
        
        return task_lines
    

    def show_preview_dialog(self, tasks):
        """Preview dialog with editable tasks."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Tasks")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Editable task list
        list_widget = QListWidget()
        for task in tasks:
            item = QListWidgetItem(task)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            list_widget.addItem(item)
        
        # Buttons
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        
        layout.addWidget(QLabel("Edit tasks before adding:"))
        layout.addWidget(list_widget)
        layout.addWidget(btn_box)
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return [list_widget.item(i).text().strip() 
                   for i in range(list_widget.count())]
        return None
    
    def add_task_to_system(self, tab_name, task):
        """Add task directly to UI and database simultaneously"""
        if not task:
            return
        
        # Add to database
        self.cursor.execute(
            "INSERT INTO tasks (tab_name, description, done) VALUES (?, ?, ?)",
            (tab_name, task, False)
        )
        self.conn.commit()
        
        # Add directly to UI without full refresh
        current_task_list = self.current_task_list()
        if current_task_list:
            item = QListWidgetItem(task)
            current_task_list.addItem(item)
            current_task_list.scrollToItem(item)  # Ensure visibility

    
    def refresh_tab_ui(self, tab_name):
        """Explicitly refresh the tab's task list from database"""
        # Find the tab's QListWidget
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) == tab_name:
                tab_widget = self.tabs.widget(index)
                task_list = tab_widget.findChild(QListWidget)
                if task_list:
                    task_list.clear()
                    
                    # Reload from database
                    self.cursor.execute("SELECT description, done FROM tasks WHERE tab_name = ?", (tab_name,))
                    tasks = self.cursor.fetchall()
                    for description, done in tasks:
                        item = QListWidgetItem(description)
                        if done:
                            item.setText(f"{description} (Done)")
                            item.setForeground(Qt.GlobalColor.gray)
                        task_list.addItem(item)
                break


    def show_error(self, message):
        """Standardized error display."""
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Error")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        error_dialog.setLayout(layout)
        error_dialog.exec()










    def closeEvent(self, event):
        """Close database connection on app close."""
        self.conn.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskApp()
    window.show()
    sys.exit(app.exec())
