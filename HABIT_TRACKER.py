import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import csv
import threading

DB_NAME = "habit_tracker.db"

class HabitTracker:
    def __init__(self):
        self.setup_database()
        self.reminders = {}
        
    def connect(self):
        return sqlite3.connect(DB_NAME)
    
    def setup_database(self):
        conn = self.connect()
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS habits_registry435256 (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        date_created TEXT NOT NULL,
                        reminder_time TEXT,
                        reminder_enabled INTEGER DEFAULT 0
                    )''')

        c.execute('''CREATE TABLE IF NOT EXISTS habits_registry435256_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        habit_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        FOREIGN KEY (habit_id) REFERENCES habits_registry435256(id)
                    )''')

        conn.commit()
        conn.close()
    
    def add_habit(self, name, reminder_time=None):
        conn = self.connect()
        c = conn.cursor()
        
        date_created = datetime.now().strftime("%Y-%m-%d")
        reminder_enabled = 1 if reminder_time else 0
        
        c.execute("INSERT INTO habits_registry435256 (name, date_created, reminder_time, reminder_enabled) VALUES (?, ?, ?, ?)", 
                  (name, date_created, reminder_time, reminder_enabled))
        
        habit_id = c.lastrowid
        conn.commit()
        conn.close()
        
        if reminder_time:
            self.setup_reminder(habit_id, name, reminder_time)
        
        return habit_id
    
    def edit_habit(self, habit_id, new_name, new_reminder_time=None):
        conn = self.connect()
        c = conn.cursor()
        
        reminder_enabled = 1 if new_reminder_time else 0
        
        c.execute("UPDATE habits_registry435256 SET name = ?, reminder_time = ?, reminder_enabled = ? WHERE id = ?", 
                  (new_name, new_reminder_time, reminder_enabled, habit_id))
        
        conn.commit()
        conn.close()
        
        if habit_id in self.reminders:
            self.reminders[habit_id].cancel()
            del self.reminders[habit_id]
        
        if new_reminder_time:
            self.setup_reminder(habit_id, new_name, new_reminder_time)
    
    def view_habits(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("SELECT id, name, date_created, reminder_time, reminder_enabled FROM habits_registry435256")
        habits = c.fetchall()
        conn.close()
        return habits
    
    def mark_done(self, habit_id):
        conn = self.connect()
        c = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        c.execute("SELECT id FROM habits_registry435256_log WHERE habit_id = ? AND date = ?", (habit_id, today))
        existing = c.fetchone()
        
        if existing:
            conn.close()
            return False
        else:
            c.execute("INSERT INTO habits_registry435256_log (habit_id, date) VALUES (?, ?)", (habit_id, today))
            conn.commit()
            conn.close()
            return True
    
    def delete_habit(self, habit_id):
        conn = self.connect()
        c = conn.cursor()
        
        c.execute("DELETE FROM habits_registry435256_log WHERE habit_id = ?", (habit_id,))
        c.execute("DELETE FROM habits_registry435256 WHERE id = ?", (habit_id,))
        
        conn.commit()
        conn.close()
        
        if habit_id in self.reminders:
            self.reminders[habit_id].cancel()
            del self.reminders[habit_id]
    
    def get_streak(self, habit_id):
        conn = self.connect()
        c = conn.cursor()
        
        c.execute("SELECT date FROM habits_registry435256_log WHERE habit_id = ? ORDER BY date DESC", (habit_id,))
        dates = [row[0] for row in c.fetchall()]
        
        conn.close()
        
        if not dates:
            return 0
        
        streak = 0
        current_date = datetime.now().date()
        
        for date_str in dates:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            if date_obj == current_date - timedelta(days=streak):
                streak += 1
            else:
                break
        
        return streak
    
    def get_history(self, habit_id, days=30):
        conn = self.connect()
        c = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        c.execute("SELECT date FROM habits_registry435256_log WHERE habit_id = ? AND date >= ? ORDER BY date", 
                  (habit_id, start_date))
        dates = [row[0] for row in c.fetchall()]
        
        conn.close()
        return dates
    
    def get_weekly_stats(self, habit_id):
        conn = self.connect()
        c = conn.cursor()
        
        weeks_stats = []
        for week in range(4):
            start_date = (datetime.now() - timedelta(days=(week+1)*7)).strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(days=week*7)).strftime("%Y-%m-%d")
            
            c.execute("SELECT COUNT(*) FROM habits_registry435256_log WHERE habit_id = ? AND date >= ? AND date < ?", 
                      (habit_id, start_date, end_date))
            count = c.fetchone()[0]
            weeks_stats.append(count)
        
        conn.close()
        return weeks_stats[::-1]
    
    def get_monthly_stats(self, habit_id):
        conn = self.connect()
        c = conn.cursor()
        
        monthly_stats = []
        for month in range(6):
            if month == 0:
                start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")
            else:
                date = datetime.now().replace(day=1) - timedelta(days=month*30)
                start_date = date.strftime("%Y-%m-%d")
                end_date = (date + timedelta(days=30)).strftime("%Y-%m-%d")
            
            c.execute("SELECT COUNT(*) FROM habits_registry435256_log WHERE habit_id = ? AND date >= ? AND date <= ?", 
                      (habit_id, start_date, end_date))
            count = c.fetchone()[0]
            monthly_stats.append(count)
        
        conn.close()
        return monthly_stats[::-1]
    
    def export_csv(self, filename="habit_report.csv"):
        conn = self.connect()
        c = conn.cursor()
        
        c.execute("""SELECT h.name, h.date_created, l.date
                     FROM habits_registry435256 h
                     LEFT JOIN habits_registry435256_log l ON h.id = l.habit_id
                     ORDER BY h.name, l.date""")
        
        data = c.fetchall()
        conn.close()
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Habit Name', 'Date Created', 'Completion Date'])
            writer.writerows(data)
        
        return filename
    
    def setup_reminder(self, habit_id, habit_name, reminder_time):
        try:
            hour, minute = map(int, reminder_time.split(':'))
            now = datetime.now()
            reminder_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if reminder_datetime <= now:
                reminder_datetime += timedelta(days=1)
            
            seconds_until = (reminder_datetime - now).total_seconds()
            
            timer = threading.Timer(seconds_until, self.trigger_reminder, [habit_name])
            timer.start()
            
            self.reminders[habit_id] = timer
            
        except ValueError:
            pass
    
    def trigger_reminder(self, habit_name):
        print(f"Reminder: Time to do '{habit_name}'!")


class HabitGUI:
    def __init__(self):
        self.tracker = HabitTracker()
        self.root = tk.Tk()
        self.root.title("Habit Tracker")
        self.root.geometry("800x600")
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="Habit Tracker", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        ttk.Button(buttons_frame, text="Add", command=self.add_habit).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Edit", command=self.edit_habit).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Delete", command=self.delete_habit).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Done", command=self.mark_done).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Export", command=self.export_data).pack(side=tk.LEFT, padx=(0, 5))
        
        columns = ('ID', 'Name', 'Created', 'Streak', 'Last Done', 'Reminder')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.grid(row=2, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(stats_frame, text="View Stats", command=self.show_stats).pack(side=tk.LEFT)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        self.update_list()
    
    def add_habit(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Habit")
        dialog.geometry("400x150")
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        ttk.Label(dialog, text="Reminder (HH:MM):").pack(pady=5)
        time_entry = ttk.Entry(dialog, width=40)
        time_entry.pack(pady=5)
        
        def save():
            name = name_entry.get().strip()
            reminder = time_entry.get().strip() or None
            
            if name:
                self.tracker.add_habit(name, reminder)
                self.update_list()
                dialog.destroy()
                messagebox.showinfo("Done", f"Added '{name}'")
            else:
                messagebox.showerror("Error", "Enter name")
        
        ttk.Button(dialog, text="Add", command=save).pack(pady=15)
    
    def edit_habit(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Choose a habit first")
            return
        
        item = self.tree.item(selection[0])
        habit_id = item['values'][0]
        current_name = item['values'][1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Habit")
        dialog.geometry("400x150")
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        name_entry.insert(0, current_name)
        name_entry.focus()
        
        ttk.Label(dialog, text="Reminder (HH:MM):").pack(pady=5)
        time_entry = ttk.Entry(dialog, width=40)
        time_entry.pack(pady=5)
        
        def save():
            new_name = name_entry.get().strip()
            reminder = time_entry.get().strip() or None
            
            if new_name:
                self.tracker.edit_habit(habit_id, new_name, reminder)
                self.update_list()
                dialog.destroy()
                messagebox.showinfo("Done", "Updated")
            else:
                messagebox.showerror("Error", "Enter name")
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=15)
    
    def delete_habit(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Choose a habit first")
            return
        
        item = self.tree.item(selection[0])
        habit_name = item['values'][1]
        habit_id = item['values'][0]
        
        if messagebox.askyesno("Delete", f"Delete '{habit_name}'?"):
            self.tracker.delete_habit(habit_id)
            self.update_list()
            messagebox.showinfo("Done", "Deleted")
    
    def mark_done(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Choose a habit first")
            return
        
        item = self.tree.item(selection[0])
        habit_id = item['values'][0]
        habit_name = item['values'][1]
        
        if self.tracker.mark_done(habit_id):
            self.update_list()
            messagebox.showinfo("Done", f"Marked '{habit_name}' done")
        else:
            messagebox.showinfo("Already done", f"'{habit_name}' already done today")
    
    def export_data(self):
        filename = self.tracker.export_csv()
        messagebox.showinfo("Export", f"Saved to {filename}")
    
    def show_stats(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select", "Choose a habit first")
            return
        
        item = self.tree.item(selection[0])
        habit_id = item['values'][0]
        habit_name = item['values'][1]
        
        streak = self.tracker.get_streak(habit_id)
        history = self.tracker.get_history(habit_id, 30)
        weekly = self.tracker.get_weekly_stats(habit_id)
        monthly = self.tracker.get_monthly_stats(habit_id)
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title(f"Stats - {habit_name}")
        stats_window.geometry("450x350")
        
        text = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        stats_info = f"""Stats for: {habit_name}

Current streak: {streak} days

Last 30 days: {len(history)} completions
Recent: {', '.join(history[-5:]) if history else 'None'}

Weekly (last 4 weeks):
Week 1: {weekly[0]}
Week 2: {weekly[1]}
Week 3: {weekly[2]}
Week 4: {weekly[3]}

Monthly (last 6 months):
Month 1: {monthly[0]}
Month 2: {monthly[1]}
Month 3: {monthly[2]}
Month 4: {monthly[3]}
Month 5: {monthly[4]}
Month 6: {monthly[5]}
"""
        
        text.insert(tk.END, stats_info)
        text.config(state=tk.DISABLED)
    
    def update_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        habits = self.tracker.view_habits()
        for habit in habits:
            habit_id, name, date_created, reminder_time, reminder_enabled = habit
            
            streak = self.tracker.get_streak(habit_id)
            
            history = self.tracker.get_history(habit_id, 1)
            last_done = history[-1] if history else "Never"
            
            reminder_text = reminder_time if reminder_enabled else "None"
            
            self.tree.insert('', tk.END, values=(habit_id, name, date_created, streak, last_done, reminder_text))
    
    def run(self):
        self.root.mainloop()


def run_cli():
    tracker = HabitTracker()
    
    def show_habits():
        habits = tracker.view_habits()
        if not habits:
            print("No habits.")
            return
        
        print("\nHabits:")
        for habit in habits:
            habit_id, name, date_created, reminder_time, reminder_enabled = habit
            streak = tracker.get_streak(habit_id)
            history = tracker.get_history(habit_id, 1)
            last_done = history[-1] if history else "Never"
            
            print(f"{habit_id}: {name}")
            print(f"   Created: {date_created}")
            print(f"   Streak: {streak} days")
            print(f"   Last: {last_done}")
            if reminder_enabled:
                print(f"   Reminder: {reminder_time}")
            print()
    
    while True:
        print("\nHabit Tracker")
        print("1. Add")
        print("2. View")
        print("3. Edit")
        print("4. Done")
        print("5. Delete")
        print("6. Stats")
        print("7. Export")
        print("8. GUI")
        print("9. Exit")
        
        choice = input("Choice: ")
        
        if choice == "1":
            name = input("Name: ")
            reminder = input("Reminder (HH:MM): ").strip()
            tracker.add_habit(name, reminder if reminder else None)
            print(f"Added '{name}'")
            
        elif choice == "2":
            show_habits()
            
        elif choice == "3":
            show_habits()
            try:
                habit_id = int(input("ID: "))
                new_name = input("New name: ")
                new_reminder = input("New reminder (HH:MM): ").strip()
                tracker.edit_habit(habit_id, new_name, new_reminder if new_reminder else None)
                print("Updated")
            except ValueError:
                print("Invalid ID")
                
        elif choice == "4":
            show_habits()
            try:
                habit_id = int(input("ID: "))
                if tracker.mark_done(habit_id):
                    print("Done!")
                else:
                    print("Already done today")
            except ValueError:
                print("Invalid ID")
                
        elif choice == "5":
            show_habits()
            try:
                habit_id = int(input("ID: "))
                confirm = input("Sure? (y/n): ")
                if confirm.lower() == 'y':
                    tracker.delete_habit(habit_id)
                    print("Deleted")
            except ValueError:
                print("Invalid ID")
                
        elif choice == "6":
            show_habits()
            try:
                habit_id = int(input("ID: "))
                streak = tracker.get_streak(habit_id)
                history = tracker.get_history(habit_id, 30)
                weekly = tracker.get_weekly_stats(habit_id)
                monthly = tracker.get_monthly_stats(habit_id)
                
                print(f"\nStats:")
                print(f"Streak: {streak} days")
                print(f"Last 30 days: {len(history)}")
                print(f"Weekly: {weekly}")
                print(f"Monthly: {monthly}")
                
            except ValueError:
                print("Invalid ID")
                
        elif choice == "7":
            filename = tracker.export_csv()
            print(f"Exported to {filename}")
            
        elif choice == "8":
            gui = HabitGUI()
            gui.run()
            
        elif choice == "9":
            print("Bye!")
            break
            
        else:
            print("Invalid")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        gui = HabitGUI()
        gui.run()
    else:
        run_cli()