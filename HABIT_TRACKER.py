import sqlite3,tkinter as tk
from tkinter import ttk,messagebox
from datetime import datetime,timedelta
import csv,threading

class HabitTracker:
    def __init__(self):
        self.db=sqlite3.connect("habits.db")
        self.db.execute('''CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY,name TEXT,created TEXT,reminder TEXT)''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY,habit_id INTEGER,date TEXT)''')
        self.db.commit()
    
    def add(self,name,reminder=None):
        self.db.execute("INSERT INTO habits(name,created,reminder)VALUES(?,?,?)",(name,datetime.now().strftime("%Y-%m-%d"),reminder))
        self.db.commit()
        if reminder:threading.Timer(self.calc_delay(reminder),lambda:print(f"⏰ {name}!")).start()
    
    def edit(self,id,name,reminder=None):
        self.db.execute("UPDATE habits SET name=?,reminder=? WHERE id=?",(name,reminder,id))
        self.db.commit()
    
    def delete(self,id):
        self.db.execute("DELETE FROM logs WHERE habit_id=?",(id,))
        self.db.execute("DELETE FROM habits WHERE id=?",(id,))
        self.db.commit()
    
    def mark(self,id):
        today=datetime.now().strftime("%Y-%m-%d")
        if not self.db.execute("SELECT 1 FROM logs WHERE habit_id=? AND date=?",(id,today)).fetchone():
            self.db.execute("INSERT INTO logs(habit_id,date)VALUES(?,?)",(id,today))
            self.db.commit()
            return True
        return False
    
    def get_habits(self):
        return self.db.execute("SELECT id,name,created,reminder FROM habits").fetchall()
    
    def get_streak(self,id):
        dates=[r[0]for r in self.db.execute("SELECT date FROM logs WHERE habit_id=? ORDER BY date DESC",(id,)).fetchall()]
        if not dates:return 0
        streak,curr=0,datetime.now().date()
        for d in dates:
            if datetime.strptime(d,"%Y-%m-%d").date()==curr-timedelta(days=streak):streak+=1
            else:break
        return streak
    
    def get_stats(self,id):
        logs=self.db.execute("SELECT date FROM logs WHERE habit_id=?",(id,)).fetchall()
        return len(logs),self.get_streak(id)
    
    def export(self):
        data=self.db.execute('''SELECT h.name,h.created,l.date FROM habits h LEFT JOIN logs l ON h.id=l.habit_id''').fetchall()
        with open("export.csv",'w',newline='')as f:
            csv.writer(f).writerows([['Habit','Created','Done']]+data)
        return "export.csv"
    
    def calc_delay(self,time_str):
        try:h,m=map(int,time_str.split(':'));t=datetime.now().replace(hour=h,minute=m,second=0);return max(0,(t+timedelta(days=1)if t<=datetime.now()else t-datetime.now()).total_seconds())
        except:return 86400

class GUI:
    def __init__(self):
        self.tracker=HabitTracker()
        self.root=tk.Tk()
        self.root.title("Habits")
        self.root.geometry("600x400")
        
        ttk.Button(self.root,text="Add",command=self.add_dlg).pack(side=tk.LEFT,padx=5)
        ttk.Button(self.root,text="Edit",command=self.edit_dlg).pack(side=tk.LEFT,padx=5)
        ttk.Button(self.root,text="Delete",command=self.delete_habit).pack(side=tk.LEFT,padx=5)
        ttk.Button(self.root,text="Done",command=self.mark_done).pack(side=tk.LEFT,padx=5)
        ttk.Button(self.root,text="Stats",command=self.show_stats).pack(side=tk.LEFT,padx=5)
        ttk.Button(self.root,text="Export",command=self.export).pack(side=tk.LEFT,padx=5)
        
        self.tree=ttk.Treeview(self.root,columns=('ID','Name','Streak','Reminder'),show='headings')
        for col in self.tree['columns']:self.tree.heading(col,text=col)
        self.tree.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)
        self.refresh()
    
    def add_dlg(self):
        d=tk.Toplevel();d.title("Add");d.geometry("300x100")
        ttk.Label(d,text="Name:").pack();name=ttk.Entry(d);name.pack()
        ttk.Label(d,text="Reminder(HH:MM):").pack();rem=ttk.Entry(d);rem.pack()
        def save():self.tracker.add(name.get(),rem.get()or None);self.refresh();d.destroy()
        ttk.Button(d,text="Save",command=save).pack()
    
    def edit_dlg(self):
        if not self.tree.selection():return messagebox.showwarning("","Select habit")
        id=self.tree.item(self.tree.selection()[0])['values'][0]
        d=tk.Toplevel();d.title("Edit");d.geometry("300x100")
        ttk.Label(d,text="Name:").pack();name=ttk.Entry(d);name.pack()
        ttk.Label(d,text="Reminder(HH:MM):").pack();rem=ttk.Entry(d);rem.pack()
        def save():self.tracker.edit(id,name.get(),rem.get()or None);self.refresh();d.destroy()
        ttk.Button(d,text="Save",command=save).pack()
    
    def delete_habit(self):
        if not self.tree.selection():return messagebox.showwarning("","Select habit")
        if messagebox.askyesno("Delete","Sure?"):
            id=self.tree.item(self.tree.selection()[0])['values'][0]
            self.tracker.delete(id);self.refresh()
    
    def mark_done(self):
        if not self.tree.selection():return messagebox.showwarning("","Select habit")
        id=self.tree.item(self.tree.selection()[0])['values'][0]
        if self.tracker.mark(id):messagebox.showinfo("","Done!");self.refresh()
        else:messagebox.showinfo("","Already done today")
    
    def show_stats(self):
        if not self.tree.selection():return messagebox.showwarning("","Select habit")
        id,name=self.tree.item(self.tree.selection()[0])['values'][:2]
        total,streak=self.tracker.get_stats(id)
        messagebox.showinfo("Stats",f"{name}\nTotal: {total}\nStreak: {streak}")
    
    def export(self):
        file=self.tracker.export()
        messagebox.showinfo("Export",f"Saved: {file}")
    
    def refresh(self):
        for i in self.tree.get_children():self.tree.delete(i)
        for habit in self.tracker.get_habits():
            id,name,created,reminder=habit
            streak=self.tracker.get_streak(id)
            self.tree.insert('',tk.END,values=(id,name,streak,reminder or"None"))
    
    def run(self):self.root.mainloop()

def cli():
    t=HabitTracker()
    while True:
        print("\n1.Add 2.View 3.Edit 4.Done 5.Delete 6.Stats 7.Export 8.GUI 9.Exit")
        c=input("Choice:")
        if c=="1":t.add(input("Name:"),input("Reminder(HH:MM):")or None);print("Added")
        elif c=="2":[print(f"{h[0]}:{h[1]} streak:{t.get_streak(h[0])}")for h in t.get_habits()]
        elif c=="3":t.edit(int(input("ID:")),input("Name:"),input("Reminder:")or None);print("Updated")
        elif c=="4":print("Done!"if t.mark(int(input("ID:")))else"Already done")
        elif c=="5":t.delete(int(input("ID:")));print("Deleted")
        elif c=="6":id=int(input("ID:"));total,streak=t.get_stats(id);print(f"Total:{total} Streak:{streak}")
        elif c=="7":print(f"Exported:{t.export()}")
        elif c=="8":GUI().run()
        elif c=="9":break

if __name__=="__main__":
    import sys
    GUI().run()if len(sys.argv)>1 and sys.argv[1]=="--gui"else cli()
