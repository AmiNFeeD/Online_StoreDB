# Online Store Database Project
### Made by Amin Kubanychbekov (ka12363) and Khusnidin Kurbanov (kk12364)

---

## Overview

This project is a **full-stack e-commerce web application** developed for the  
**AUCA Databases Final Project**.

It demonstrates:
- Proper relational database design (PostgreSQL)
- SQL queries, transactions, views, and indexes
- A Flask backend connected to PostgreSQL
- An admin dashboard with analytics

The project is designed to be **cross-platform** and works on:

- ✅ Windows
- ✅ macOS
- ✅ Linux

---

## Features

### Customer Features
- Browse products with images, categories, and prices
- Stock indicators:
  - **Out of stock**
  - **Only X left**
  - **In stock**
- Add products to cart
- Increase / decrease quantity using **+ / −**
- Remove items from cart
- Transaction-safe checkout
- View order history and order details

### Authentication
- User registration
- Login / logout
- Secure password hashing (Werkzeug)

### Orders
- Transaction-based order placement
- Product price & quantity snapshot stored in `order_items`
- Automatic stock decrease
- Full rollback on failure

### Admin Panel
- Manage products (create, update, deactivate, delete)
- Manage categories (CRUD)
- Manage orders and update status
- View order details
- Analytics dashboard

---

## Database Schema

### Main Tables
- `users`
- `categories`
- `products`
- `cart_items`
- `orders`
- `order_items`

### Design Highlights
- Fully normalized (3NF)
- Foreign key constraints
- CHECK constraints (price, stock, quantity)
- `ON CONFLICT` handling for cart merging
- Indexes for performance

---

## SQL Requirements (For Evaluation)

All SQL requirements are implemented as **separate SQL files**.

| Requirement | File |
|------------|------|
| SQL Queries | `db/queries.sql` |
| SQL Transactions | `db/transactions.sql` |
| SQL Views | `db/views.sql` |
| SQL Indexes | `db/indexes.sql` |

---

## Tech Stack

- **Backend:** Flask (Python 3.10+)
- **Database:** PostgreSQL 13+
- **Driver:** psycopg2
- **Frontend:** HTML, Bootstrap
- **Auth:** Werkzeug password hashing

---

## Project Structure

```
ProjectShop/
│── app/
│── db/
│── .env.example
│── README.md
│── requirements.txt
│── screens/
```

---

## Prerequisites

Before starting, make sure you have installed:

- **Python 3.10+**
- **PostgreSQL 13+**
- **pip** (comes with Python)

---

## Installation 

### 1. Create Virtual Environment

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
If not working use, 'py' instead of 'python'

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

This project uses environment variables to avoid OS‑specific configuration.

### 1. Create `.env` file

#### macOS / Linux
```bash
cp .env.example .env
```

#### Windows (PowerShell)
```powershell
copy .env.example .env
```


---

## Database Setup 

Run **ONE command** to fully set up the database.

Works on some machines
```bash
psql -U postgres -f db/setup_all.sql
```
### OR
```bash
psql -d postgres -v ON_ERROR_STOP=1 -f db/setup_all.sql
```


Works on:
- Windows
- macOS
- Linux

This script:
- Creates the database
- Creates all tables
- Creates SQL views
- Creates indexes
- Inserts sample data
- Creates a master admin account

---

## Running the Application

```bash
python -m app.app
```

Open in browser:
```
http://127.0.0.1:5000
```

---

## Admin Access

### Default Master Admin 

```
Email: anfd@mail.fun
Password: anfd
```

### Promote Any User to Admin

```sql
UPDATE users
SET role = 'admin'
WHERE email = 'user@email.com';
```

Admin access is stored **inside the database**, not tied to PostgreSQL OS users.

---

## Images

All product images are stored locally:

```
app/static/images/
```
Also you can add your images throw the UI on the website it will be stored in the ```app/static/uploads/``` folder.

Relative paths are used so images work on all operating systems.

---

## Backup / Restore 

### Backup
```bash
pg_dump online_store_db > backup.sql
```

### Restore
```bash
psql online_store_db < backup.sql
```

---
## Project Contribution
This project was developed collaboratively by two team members as a final project for the Database course. The responsibilities were divided to ensure effective teamwork and balanced contribution.

### Amin's Contribution:

- Developed the Full frontend interface, including layout, design, and user interaction.
- Implemented the backend logic, including server-side functionality and database integration.
- Implemented and tested database queries and system operations.

### Khusnidin's Contribution:

- Served as Project Manager (PM), overseeing project planning, task distribution, and overall coordination.
-  Contributed to defining system requirements and core functionalities of the online store.
-  Provided technical suggestions and recommendations on backend logic and database operations.

### Joint Contribution:

- Designing and developed the database schema collaboratively.
-  Worked together on debugging, testing, and final project preparation.

 This division of responsibilities ensured that both team members actively contributed to the successful completion of the project.

---
# "Certificates" screenshots

Due to the paywall of the w3schools website, the screenshots of the certificates are not available.But the course it self was completed.

## Amin's
![image](/screens/Amin.png)

## Khusnidin's
![image](/screens/Khuska.png)
---
## Final Notes

This project successfully fulfills all requirements of the AUCA Databases Final Project 2025, demonstrating a fully functional, well-structured, and cross-platform online store application. Key accomplishments include:

- ✔ Design and implementation of a fully normalized relational database schema
- ✔ Comprehensive SQL queries, transactions, views, and indexes
- ✔ Robust backend integration with Flask and PostgreSQL
- ✔ Secure user authentication and transaction-safe order processing
- ✔ Feature-rich admin dashboard with analytics and order management
- ✔ Cross-platform compatibility across Windows, macOS, and Linux

The project reflects careful planning, collaborative development, and adherence to best practices in database design and web application development.

Prepared for **AUCA Databases Final Project 2025**.
