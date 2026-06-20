from app.db.database import SessionLocal
from app.models.user import User

db = SessionLocal()

user = db.query(User).filter(User.id == 1).first()

# Calculate fit_to_teach_level based on best score
# User has: Math=83, Science=75, English=15
# Best score is 83 (Math)

# According to logic: 85+ → grade-2, 70-84 → grade-3, 50-69 → grade-4
# User's best is 83%, current_level=10
# So: fit_to_teach = max(1, 10 - 3) = 7

fit_to_teach = max(1, (user.current_level or 10) - 3)  # 83% falls in 70-84 range
user.fit_to_teach_level = fit_to_teach

db.commit()
print(f"✅ Updated user {user.name}")
print(f"   Current Level: {user.current_level}")
print(f"   Math Level: {user.math_level}%")
print(f"   Fit to Teach Level: {user.fit_to_teach_level}")

db.close()
