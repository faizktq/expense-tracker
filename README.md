# 💸 Expense Tracker

**Master your finances, empower your future today.**

![Last Commit](https://img.shields.io/github/last-commit/faizktq/expense-tracker)
![Python](https://img.shields.io/badge/Python-3.10.9-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Data%20Analysis-Pandas-purple?logo=pandas&logoColor=white)

---

## 📖 Overview

**Expense Tracker** is a simple and powerful app to track your income and expenses with an intuitive UI.

### ✨ Features

- 💵 Track income & expenses
- 🧮 Monthly summary and category breakdown
- 📈 Visualize data with charts
- 📤 Export data to CSV
- 🎨 Built with [Streamlit](https://streamlit.io/)
- 📊 Powered by [Pandas](https://pandas.pydata.org/)

---

## 📦 Getting Started

### 🔧 Prerequisites

Make sure you have Python 3.10+ installed.

### 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/faizktq/expense-tracker
cd expense-tracker/expense-tracker

# Install dependencies
pip install -r requirements.txt
```

### 🚀 Running the App

```bash
# Start the Streamlit application
streamlit run exp_app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```
expense-tracker/
├── expense-tracker/
│   ├── exp_app.py          # Main application file
│   ├── requirements.txt    # Python dependencies
│   ├── expense_tracker.db  # SQLite database (created automatically)
│   └── data/              # Data directory
└── README.md              # This file
```

**Key Files:**
- [`exp_app.py`](expense-tracker/exp_app.py) - Main Streamlit application
- [`requirements.txt`](expense-tracker/requirements.txt) - Python dependencies

---

## 🎯 Usage

1. **Add Expenses**: Enter your expense details including amount, category, and description
2. **Set Budgets**: Define monthly budgets for different categories
3. **View Analytics**: Explore your spending patterns with interactive charts
4. **Export Data**: Download your expense data as CSV files for further analysis

---

## 🛠️ Built With

- **[Streamlit](https://streamlit.io/)** - Web app framework
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis
- **[Matplotlib](https://matplotlib.org/)** - Data visualization
- **[SQLite](https://www.sqlite.org/)** - Database

---

## 📄 License

This project is open source and available for use.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

**Happy tracking! 💰**