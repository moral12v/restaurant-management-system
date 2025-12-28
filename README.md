# 🍽️ RESTAURANT MANAGEMENT SYSTEM

---

## 🚀 SETUP INSTRUCTIONS

**1. Extract the Project**
Unzip the project folder to your local directory.

**2. Create a Virtual Environment**
Open your terminal in the project folder and run:
`python -m venv venv`

**3. Activate the Environment**

- Windows: `.\venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

**4. Install Dependencies**
`pip install -r requirements.txt`

**5. Database Setup**
`python manage.py migrate`

**6. Start the Server**
`python manage.py runserver`

**7. View the Dashboard**
Open your browser and go to: http://127.0.0.1:8000/api/dashboard/

---

## 🔐 DEMO CREDENTIALS

**Admin/Manager Role**

- **Username:** admin
- **Password:** 9565333567

---

## 🏗️ ARCHITECTURE & FEATURES

**Backend (Django & DRF)**

- **RESTful API:** Uses ViewSets for Tables, Menu, and Orders.
- **Signals:** Automatically changes table status to 'Occupied' when an order is created.
- **Custom Actions:** Dedicated endpoints for PDF generation and clearing tables.

**Frontend (Real-time Dashboard)**

- **Live Updates:** JavaScript AJAX polling refreshes table status every 5 seconds.
- **UI Logic:** Tables dynamically change color (Green = Available, Red = Occupied).

**Billing (ReportLab)**

- **PDF Generation:** Creates professional receipts with calculated totals and taxes.

---

## ✅ DELIVERABLES INCLUDED

- **Source Code:** All Python logic and HTML templates.
- **Database:** `db.sqlite3` with pre-seeded data.
- **Tests:** Automated logic tests in `tests.py`.
- **Requirements:** `requirements.txt` for one-click installation.

---

## 📝 ASSUMPTIONS

1. Each table supports one active order at a time.
2. "Clear Table" action confirms the guest has finished and paid.
3. System uses SQLite for portability and easy grading.

---

