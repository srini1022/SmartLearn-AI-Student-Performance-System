import pickle
import numpy as np
import os

# ---------- Try loading trained model ----------
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'student_model.pkl')
model = None

if os.path.exists(MODEL_PATH):
    try:
        model = pickle.load(open(MODEL_PATH, 'rb'))
    except Exception as e:
        print(f"[Warning] Could not load trained model: {e}")
else:
    print("[Info] student_model.pkl not found — fallback to rule-based logic.")

def predict_performance(data):
    """
    Supports both dynamic and fixed input formats.
    Returns (prediction, suggestion, avg_marks, score)
    """

    try:
        # ✅ Case 1: Dynamic Subjects (new UI)
        if 'avg_marks' in data:
            avg_marks = data['avg_marks']
            attendance = data['attendance']
            assignments = data['assignments_done']

            # Compute score manually (universal fallback)
            score = (avg_marks * 0.7) + (attendance * 0.2) + (assignments * 1.5)

            if model:
                # optional model prediction if compatible
                try:
                    X = np.array([[avg_marks, attendance, assignments]])
                    pred = model.predict(X)[0]
                    return *interpret_label(pred), avg_marks, score
                except:
                    pass

            # If model not used
            return *interpret_score(score), avg_marks, score

        # ✅ Case 2: Fixed Inputs (old model)
        else:
            X = np.array([[data['python'], data['math'], data['ds'], data['ai'],
                           data['attendance'], data['assignments_done']]])
            pred = model.predict(X)[0] if model else None

            avg_marks = np.mean([data['python'], data['math'], data['ds'], data['ai']])
            score = (avg_marks * 0.7) + (data['attendance'] * 0.2) + (data['assignments_done'] * 1.5)

            if not pred:
                return *interpret_score(score), avg_marks, score
            else:
                return *interpret_label(pred), avg_marks, score

    except Exception as e:
        print(f"[Error] in predict_performance: {e}")
        return "Error", "Unable to generate prediction.", 0, 0


def interpret_score(score):
    """Simple rule-based prediction if model not found."""
    if score >= 85:
        return "Excellent", "Outstanding! Keep up your consistent performance."
    elif score >= 70:
        return "Good", "You’re doing well. Keep focusing on improving weaker areas."
    elif score >= 50:
        return "Average", "Study regularly, practice daily, and complete assignments on time."
    else:
        return "Needs Improvement", "Focus on core topics and seek help where needed."


def interpret_label(pred):
    """Interpret ML model prediction into readable text + suggestions."""
    if pred == "Needs Improvement":
        return pred, "Revise fundamentals, practice more daily, and seek help from mentors."
    elif pred == "Average":
        return pred, "You’re doing well. Focus on weak topics and increase consistency."
    else:
        return pred, "Excellent performance! Keep learning and aim for advanced topics."
