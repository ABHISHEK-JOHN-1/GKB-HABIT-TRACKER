# GKB-HABIT-TRACKER
This project is a comprehensive Habit Tracker application designed to help users establish and maintain daily habits. It provides a robust system for tracking progress, viewing statistics, and receiving reminders for various personal goals.
Key Features:
• Habit Management:
    ◦ Add Habits: Create new habits with a name and an optional reminder time. The creation date is automatically recorded.
    ◦ Edit Habits: Modify existing habit names or update their reminder times. Any active reminder is cancelled and re-scheduled if updated.
    ◦ Delete Habits: Remove habits completely, which also deletes all associated completion records and cancels any reminders.
• Progress Tracking:
    ◦ Mark as Done: Record the completion of a habit for a specific date. The system prevents marking the same habit as done multiple times on the same day.
    ◦ Streak Tracking: Calculates the number of consecutive days a habit has been completed.
    ◦ History View: Retrieve completion dates for a habit within a specified period, e.g., the last 30 days.
    ◦ Weekly & Monthly Statistics: Analyse habit completion counts over the last four weeks and six months, respectively.
• Reminders:
    ◦ Set time-based reminders for habits.
    ◦ Reminders trigger a console message at the specified time.
• Data Export:
    ◦ Export all habit and completion data to a CSV file (habit_report.csv) for external analysis or record-keeping.
Technical Details:
• Database: Utilises a local SQLite database (habit_tracker.db) for persistent storage.
    ◦ habits_registry435256 Table: Stores habit details including id, name, date_created, reminder_time, and reminder_enabled.
    ◦ habits_registry435256_log Table: Records each instance of a habit being marked as done, linking to the habit via habit_id and storing the date of completion.
• User Interfaces:
    ◦ Command-Line Interface (CLI): Provides a text-based menu for interacting with the tracker. It allows users to add, view, mark as done, delete, edit habits, see statistics, and export data through console commands.
    ◦ Graphical User Interface (GUI): Built using the tkinter library, offering a visual and interactive experience with buttons and a habit display table. The GUI supports all core functionalities and provides dedicated windows for adding, editing, and viewing detailed statistics.
• Concurrency: Uses threading for managing reminders without blocking the main application flow.
How to Run:
The application can be launched in either CLI or GUI mode:
• Default CLI Mode: python your_script_name.py
• GUI Mode: python your_script_name.py --gui
    ◦ You can also launch the GUI from within the CLI menu.
