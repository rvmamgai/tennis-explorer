# 🎾 Tennis Explorer — Game Analytics with Sportradar API

**An end-to-end tennis analytics project using Python, MySQL, SQL, and Streamlit.**

🔗 **Live Application:** https://tennis-explorer-zawxixnorsxujz6ttykgnm.streamlit.app/

💻 **GitHub Repository:** https://github.com/rvmamgai/tennis-explorer

## 📌 Project Overview

Tennis Explorer transforms tennis data from the Sportradar Tennis API into a structured relational database and an interactive analytics dashboard.

The project extracts nested JSON data, cleans and transforms it using Python, stores it in MySQL, and uses SQL queries to generate insights presented through interactive Streamlit charts, filters, and tables.

## 🎯 Project Objectives

- Analyze tennis competitions, categories, and tournament hierarchies.
- Explore sports complexes, venues, locations, and time zones.
- Analyze ATP and WTA doubles competitor rankings.
- Develop reusable SQL queries for filtering, aggregation, and ranking analysis.
- Build an interactive dashboard for exploring tennis data.
- Implement repeatable data loading and secure credential management.

## 🛠️ Technology Stack

- **Programming:** Python
- **API:** Sportradar Tennis API
- **Database:** MySQL
- **Data Analysis:** Pandas, SQL
- **Database Connectivity:** SQLAlchemy, PyMySQL
- **Dashboard:** Streamlit
- **Visualization:** Plotly
- **Configuration:** python-dotenv and Streamlit Secrets

## 📊 Dataset Summary

The project processes **13,595 rows across six MySQL tables**.

| Table | Records |
|---|---:|
| Categories | 18 |
| Competitions | 6,681 |
| Complexes | 778 |
| Venues | 4,116 |
| Competitors | 1,000 |
| Competitor Rankings | 1,000 |
| **Total** | **13,595** |

## ✨ Key Features

- Interactive ranking dashboard with KPIs and competitor search.
- Top 10 doubles competitors by ranking points.
- Competition distribution by gender and category.
- Country-wise competitor counts and average ranking points.
- Searchable, filterable venue and sports complex explorer.
- Competition and parent–sub-competition exploration.
- Paginated database results using SQL LIMIT and OFFSET.
- Relational database design with primary and foreign keys.
- Repeatable data loading designed to avoid duplicate records.
- Secure configuration for local and cloud environments.

## 📈 Key Analytical Insights

- Compare leading doubles competitors by ranking points.
- Explore the distribution of competitions by gender and category.
- Compare competitor counts with average points across countries.
- Investigate venue locations, associated complexes, and time zones.
- Examine competition structures and categories.

*Findings reflect the captured dataset and should not be interpreted as live rankings.*

## 🗂️ Project Structure

```text
tennis-explorer/
├── app.py
├── database.py
├── explore_complexes.py
├── explore_rankings.py
├── load_data.py
├── transform.py
├── sql_queries.sql
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── sample_*.json
```

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/rvmamgai/tennis-explorer.git
cd tennis-explorer
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

Configure your Sportradar API key and MySQL connection details in your local `.env` file, following the configuration expected by the project.

For cloud deployment, configure the required credentials through Streamlit Secrets.

**Never commit API keys, database passwords, or your `.env` file to GitHub.**

### 5. Launch the dashboard

Ensure the configured database is accessible, then run:

```bash
streamlit run app.py
```

## 🔐 Security and Data Integrity

- Keep sensitive credentials outside source control.
- Use environment variables locally and Streamlit Secrets in deployment.
- Validate API responses and database row counts.
- Use relational keys to maintain connections between datasets.
- Verify repeatability when loading data again.

## 🚀 Live Demo

Explore the deployed application:

**https://tennis-explorer-zawxixnorsxujz6ttykgnm.streamlit.app/**

## 📝 Conclusion

Tennis Explorer demonstrates an end-to-end analytics workflow, from API extraction and data transformation to relational database management, SQL analysis, and interactive visualization.

The project showcases practical skills in Python, SQL, MySQL, data processing, dashboard development, and deployment.