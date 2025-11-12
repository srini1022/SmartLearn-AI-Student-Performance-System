import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# ---- Sample Dataset ----
data = {
    'python': [85,45,65,92,55,70,82,50,60,90],
    'math': [78,52,68,95,58,75,88,45,65,93],
    'ds': [90,50,60,90,62,72,84,55,63,89],
    'ai': [88,49,63,94,60,70,80,58,66,91],
    'attendance': [95,70,85,98,72,80,90,60,75,96],
    'assignments_done': [5,3,4,5,2,4,5,2,3,5],
    'performance': ['Good','Needs Improvement','Average','Good','Needs Improvement','Average','Good','Needs Improvement','Average','Good']
}

df = pd.DataFrame(data)

# ---- Split dataset ----
X = df[['python','math','ds','ai','attendance','assignments_done']]
y = df['performance']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ---- Train Model ----
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ---- Save Model ----
pickle.dump(model, open('ai_helper/student_model.pkl', 'wb'))

print("✅ Model trained and saved as ai_helper/student_model.pkl")
