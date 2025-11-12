## 🧠 SmartLearn – AI Student Performance & Learning Management System

> 🎓 An AI-powered web application that helps track student performance, manage academics, and generate intelligent insights using Flask, MySQL, and Machine Learning.

---

### 🚀 Features

* 🔐 **Secure Student & Admin Authentication**
* 📊 **Student Dashboard** with attendance, assignments, and academic performance
* 🧮 **AI Study Helper** – predicts student performance using ML
* 📝 **Dynamic Grade Management** – admin can add, edit, or delete marks
* 📁 **File Uploads** – admin can upload study materials or assignments for each student
* 🧾 **PDF Report Generation** – download detailed student performance reports
* 📈 **Interactive Graphs** – visualize marks with beautiful charts
* 👑 **Multi-Admin Support** – register staff or super admins

---

### 🧩 Tech Stack

| Layer                | Technology                |
| -------------------- | ------------------------- |
| **Frontend**         | HTML, CSS, Bootstrap 5    |
| **Backend**          | Flask (Python)            |
| **Database**         | MySQL with SQLAlchemy ORM |
| **Machine Learning** | scikit-learn, numpy       |
| **PDF Generation**   | fpdf                      |
| **Version Control**  | Git & GitHub              |

---

### ⚙️ Installation & Setup

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/srini1022/SmartLearn-AI-Student-Performance-System.git
cd SmartLearn-AI-Student-Performance-System
```

#### 2️⃣ Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4️⃣ Configure the Database

Make sure MySQL is installed and running.
Then log in to MySQL and create a database:

```sql
CREATE DATABASE smartlearn_db;
```

Open **`app.py`** and update your database URI if needed:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/smartlearn_db'
```

#### 5️⃣ Run the Application

```bash
python app.py
```

Then visit:

> 🌐 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

### 👨‍💼 Default Admin Login

| Email                  | Password   |
| ---------------------- | ---------- |
| `admin@smartlearn.com` | `admin123` |

(You can also register new admins using the Admin Registration page.)

---

### 🧮 AI Study Helper

SmartLearn uses a trained ML model (`student_model.pkl`) to predict student performance based on:

* Subject Marks
* Attendance Percentage
* Number of Assignments Completed

It classifies performance as:

> 🟢 **Excellent**
> 🟡 **Average**
> 🔴 **Needs Improvement**

and provides **personalized study suggestions**.

---

### 🧾 PDF Report Example

Each student can download a **performance report** including:

* Grades
* Attendance
* Assignments
* AI Study Insights
  Generated dynamically using **FPDF**.

---

### 📸 Screenshots (Optional)

Add your screenshots here later:

```
/screenshots
 ├── dashboard.png
 ├── admin_dashboard.png
 ├── ai_helper.png
 ├── report_sample.png
```

---

### 🌟 Future Enhancements

* 📬 Email notifications for uploads and reports
* 📊 Advanced ML model for performance forecasting
* 📱 Mobile-responsive student dashboard
* 🎓 Integration with online classes and test modules

---

### 💡 Author

**Srinidhi M D**
📍 India

