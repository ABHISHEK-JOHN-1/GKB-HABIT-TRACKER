# GKB-HABIT-TRACKER
This project is a comprehensive Habit Tracker application designed to help users establish and maintain daily habits, providing robust progress tracking, statistics, and reminders . It utilises an SQLite database for data persistence and offers both a command-line interface (CLI) and a graphical user interface (GUI) for user interaction .
Key Features:
• Habit Management:
    ◦ Add Habits: Create new habits with a name and optional reminder time, automatically recording the creation date.
    ◦ Edit Habits: Modify existing habit names or update reminder times, cancelling and rescheduling reminders as needed.
    ◦ Delete Habits: Remove habits, which also purges all associated completion records and cancels reminders.
    ◦ Mark as Done: Record habit completion for the current date, preventing duplicate entries for the same day.
• Progress & Statistics:
    ◦ Streak Tracking: Calculates the number of consecutive days a habit has been completed.
    ◦ History View: Retrieve completion dates for a habit within a specified period (e.g., last 30 days).
    ◦ Weekly & Monthly Statistics: Analyse habit completion counts over the last four weeks and six months, respectively.
• Reminders: Set time-based reminders for habits, triggering a console message at the specified time, managed concurrently using threading.
• Data Export: Export all habit and completion data to a CSV file (habit_report.csv) for external use.
Technical Details:
• Database: A local SQLite database (habit_tracker.db) manages persistent storage.
    ◦ habits_registry435256 Table: Stores habit details including id, name, date_created, reminder_time, and reminder_enabled.
    ◦ habits_registry435256_log Table: Records each habit completion with habit_id and date.
• User Interfaces:
    ◦ Command-Line Interface (CLI): A text-based menu for full interaction.
    ◦ Graphical User Interface (GUI): Built with tkinter, providing an interactive visual experience with dedicated windows for actions and statistics.
• Concurrency: Uses Python's threading module to manage and trigger reminders without blocking the main application flow.
How to Run:
Launch the application from your terminal:
• Default CLI Mode: python your_script_name.py
• GUI Mode: python your_script_name.py --gui

 👤 Author
**Abhishek John**  
[GitHub Profile](https://github.com/ABHISHEK-JOHN-1)  


    ◦ The GUI can also be launched from within the CLI menu.
