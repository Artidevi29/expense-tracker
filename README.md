# 💰 Personal Expense Tracker

A full‑stack web application to help hostel students (and anyone) manage their monthly budget, track daily expenses, and visualize spending patterns. Built with Flask, SQLite, and Bootstrap.

## ✨ Features

- **User authentication** – Register / login with session management
- **Monthly budget** – Set your monthly income (in **Pakistani Rupee – PKR**)
- **Expense tracking** – Add, edit, and delete expenses with category, description, and date
- **Dashboard** – Shows:
  - Monthly budget, total spent, remaining balance, and savings
  - Pie chart of spending by category (using Chart.js)
  - Transaction list for the current month
- **Savings / overspent alerts** – Visual feedback when you exceed your budget
- **Responsive design** – Works on desktop, tablet, and mobile

## 🛠️ Tech Stack

| Layer          | Technology                               |
|----------------|------------------------------------------|
| Backend        | Flask (Python)                           |
| Database       | SQLite + SQLAlchemy ORM                  |
| Frontend       | HTML, Bootstrap 5, Jinja2 templates      |
| Charts         | Chart.js                                 |
| Authentication | Flask‑Login                              |
| Deployment     | Render (PaaS)                            |

## 🚀 Live Demo

[![Render](https://img.shields.io/badge/Render-Deployed-success?logo=render)](https://your-app-name.onrender.com)  
*(Replace the URL with your actual Render deployment link after deploying)*

## 📦 Local Setup

### Prerequisites
- Python 3.7 or higher
- Git (optional)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Artidevi29/expense-tracker.git
   cd expense-tracker
