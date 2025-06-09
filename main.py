from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QMessageBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime
from dataclasses import dataclass
import json

@dataclass
class Habit:
    name: str
    done: bool

def save_habits(habits: list[Habit]):
    if not habits:
        habits = []
    try:
        with open("habits.json", "w") as file:
            json.dump([habit.__dict__ for habit in habits], file, indent=4)
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Failed to save habits: {e}")

def load_habits() -> list[Habit]:
    try:
        with open("habits.json", "r") as file:
            habits_data = json.load(file)
            return [Habit(**habit) for habit in habits_data]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        QMessageBox.warning(None, "Error", "Failed to load habits from file.")
        return []

def save_dates(date: str):
    if not date:
        QMessageBox.warning(None, "Input Error", "Date cannot be empty.")
        return
    try:
        with open("date.txt", "r") as file:
            existing_date = file.read().strip()
            if existing_date == date:
                return
    except FileNotFoundError:
        pass
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Failed to read date file: {e}")
        return
    # Write the new date to file
    try:
        with open("date.txt", "w") as file:
            file.write(date)
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Failed to save date: {e}")

def load_dates() -> str:
    try:
        with open("date.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Failed to load date: {e}")
        return ""

def save_daily_progress(habits: list[Habit]):
    current_date = datetime.now().strftime("%Y-%m-%d")
    progress_data = {current_date: {habit.name: habit.done for habit in habits}}
    
    try:
        with open("progress.json", "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}
    
    existing_data.update(progress_data)
    
    with open("progress.json", "w") as file:
        json.dump(existing_data, file)

def load_daily_progress() -> dict:
    try:
        with open("progress.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        QMessageBox.warning(None, "Error", "Failed to load progress data from file.")
        return {}

def mark_todays_habits(habits: list[Habit]):
    if not habits:
        QMessageBox.information(None, "No Habits", "No habits found to mark.")
        return
    for habit in habits:
        completed, ok = QInputDialog.getItem(None, "Mark Habit", f"Did you complete '{habit.name}' today?", ["Yes", "No"], 0, False)
        if ok and completed == "Yes":
            habit.done = True
        
    save_habits(habits)
    save_daily_progress(habits)

def add_habit(habits: list[Habit]):
    habit_name, ok = QInputDialog.getText(None, "Add Habit", "Enter habit name:")
    if not ok or not habit_name:
        return
    if any(habit.name == habit_name for habit in habits):
        QMessageBox.warning(None, "Input Error", f"Habit '{habit_name}' already exists.")
        return
    else:
        QMessageBox.information(None, "Success", f"Habit '{habit_name}' added successfully.")
        habits.append(Habit(name=habit_name, done=False))
    save_habits(habits)

def view_habits(habits: list[Habit]):
    if not habits:
        QMessageBox.information(None, "No Habits", "No habits found.")
        return
    
    habit_list = []
    for index, habit in enumerate(habits, start=1):
            status_color = 'green' if habit.done else 'red'
            status_text = 'Done' if habit.done else 'Not Done'
            habit_list.append(f"{index}. {habit.name} - <b style='color: {status_color};'>{status_text}</b><br>")
    
    QMessageBox.information(None, "Habits", "\n".join(habit_list))
    
def mark_habits(habits: list[Habit]):
    if not habits:
        QMessageBox.information(None, "No Habits", "No habits found to mark.")
        return
    for habit in habits:
        if habit.done:
            continue
        else:
            completed, ok = QInputDialog.getItem(None, "Mark Habit", f"Have you done {habit.name} yet?", ["Yes", "No"], 0, False)
            if ok and completed == "Yes":
                habit.done = True
    save_habits(habits)
    save_daily_progress(habits)

def remove_habit(habits: list[Habit]):
    if not habits:
        QMessageBox.information(None, "No Habits", "No habits found to delete.")
        return
    
    habit_names = [habit.name for habit in habits]
    habit_name, ok = QInputDialog.getItem(None, "Delete Habit", "Select the habit you would like to remove:", habit_names, 0, False)
    if not ok or not habit_name:
        return
    for habit in habits:
        if habit.name == habit_name:
            habits.remove(habit)
            QMessageBox.information(None, "Success", f"Habit '{habit.name}' removed successfully.")
            save_habits(habits)
            return
    QMessageBox.warning(None, "Input Error", f"Habit '{habit_name}' not found.")

def view_progress(habits: list[Habit]):
    progress_data = load_daily_progress()

    if not progress_data:
        QMessageBox.warning(None, "Error", "No progress data found.")
        return
    
    progress_text = "Habit Progress:\n\n"
    
    for habit in habits:
        total_days = 0
        completed_days = 0
        
        for date, habits_status in progress_data.items():
            if habit.name in habits_status:
                total_days += 1
                if habits_status[habit.name]:
                    completed_days += 1
        
        if total_days > 0:
            percentage = (completed_days / total_days) * 100
            progress_text += f"{habit.name}: {completed_days}/{total_days} days ({percentage:.1f}%)\n"
        else:
            progress_text += f"{habit.name}: No data\n"

    QMessageBox.information(None, "Progress", progress_text)

def main():
    # Setup
    app = QApplication([])
    
    # Create the main window
    main_window = QWidget()
    main_window.setWindowTitle("Habit Tracker")
    main_window.resize(800, 600)
    
    # Title label
    title_label = QLabel("Habit Tracker", main_window)
    title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF; padding: 10px;")
    title_label.setAlignment(Qt.AlignCenter)  # type: ignore
    title_label.setGeometry(0, 10, main_window.width(), 40)

    # Set custom font
    custom_font = QFont("Fira Sans", 18)
    app.setFont(custom_font)

    # Style
    app.setStyleSheet("""
        QWidget, QMessageBox, QInputDialog {
            background-color: #212529;
            color: #FFFFFF;
            font-size: 18px;
        }

        QPushButton {
            border-radius: 10px;
            background-color: #343A40;
            color: #FFFFFF;
            font-size: 18px;
        }

        QPushButton:hover {
            background-color: #495057;
        }
        """)
    # Load habits from file
    habits = load_habits()
    if not habits:
        habits = []

    # Date logic
    current_date = datetime.now().strftime("%Y-%m-%d")
    last_saved_date = load_dates().strip()
    if not last_saved_date:
        last_saved_date = current_date
        save_dates(current_date)

    if current_date != last_saved_date:
        save_dates(current_date)

        # Reset habits if the date has changed
        for habit in habits:
            habit.done = False
        mark_todays_habits(habits)
        save_habits(habits)
        save_daily_progress(habits)
    
    # Add habit button
    add_habit_button = QPushButton("Add Habit", main_window)
    add_habit_button.setGeometry((main_window.width() - 250) // 2, 50, 250, 60)
    add_habit_button.clicked.connect(lambda: add_habit(habits))

    # View habits buttons
    view_habits_button = QPushButton("View Habits", main_window)
    view_habits_button.setGeometry((main_window.width() - 250) // 2, 140, 250, 60)
    view_habits_button.clicked.connect(lambda: view_habits(habits))

    # Mark habits button
    mark_habits_button = QPushButton("Mark Habits", main_window)
    mark_habits_button.setGeometry((main_window.width() - 250) // 2, 230, 250, 60)
    mark_habits_button.clicked.connect(lambda: mark_habits(habits))

    # Remove habit button
    remove_habit_button = QPushButton("Remove Habit", main_window)
    remove_habit_button.setGeometry((main_window.width() - 250) // 2, 320, 250, 60)
    remove_habit_button.clicked.connect(lambda: remove_habit(habits))

    # View progress button
    view_progress_button = QPushButton("View Progress", main_window)
    view_progress_button.setGeometry((main_window.width() - 250) // 2, 410, 250, 60)
    view_progress_button.clicked.connect(lambda: view_progress(habits))

    # Show the main window
    main_window.show()

    # Start the application event loop
    app.exec()
    
# Call the main function
if __name__ == "__main__":
    main()
