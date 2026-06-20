import sqlite3

conn = sqlite3.connect('H:/Projects/Hackstreet-Bois/backend/student_performance.db')
cursor = conn.cursor()

cursor.execute("SELECT id, name, current_level, math_level, science_level, english_level, fit_to_teach_level FROM users")
users = cursor.fetchall()

print("All Users:")
print("-" * 100)
for user in users:
    print(f"ID: {user[0]}, Name: {user[1]}, Grade: {user[2]}, Math: {user[3]}, Science: {user[4]}, English: {user[5]}, Fit to Teach: {user[6]}")

conn.close()
