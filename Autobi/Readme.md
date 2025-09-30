#  Auto BI Dashboard

Auto BI Dashboard is a no-code Business Intelligence (BI) and data analytics platform built with Streamlit
.
It enables users to upload, clean, analyze, and visualize data — all without coding.

🔗 Live App: https://autobianalyst.streamlit.app/

## What It Does
- Upload CSV or Excel files and clean data interactively
- Detect duplicates, missing values, and inconsistencies
- Perform automated analysis with AI-generated insights
- Build interactive dashboards with charts and KPIs
- Export processed data and insights (CSV or PDF)
- Supports local AI integration via Ollama
 for private, offline insights
## Features
### Data Cleaning & Preparation
- Handle missing values (remove, mean, median, mode, or custom fill)
- Remove duplicates
- Drop unwanted columns
- Preview changes before applying
### Automated Analysis
- Smart detection of numeric, categorical, datetime, and boolean columns
- Automatic KPI generation
- Relationship discovery between variables
### Dashboard Builder
- Add KPIs and charts with one click
- Custom dashboard layout builder
- Export dashboards for reporting
### Analysis Modes
- Dashboard → Quick automated insights
- Custom Analysis → Select variables & chart types
- All Relationships → Explore all numeric vs. categorical relationships
- Data Summary → Dataset statistics + AI insights
- Custom Dashboard → Build and personalize dashboards
### AI-Powered Insights
- Local AI integration (Ollama models like phi3, llama2)
- Privacy-first: data never leaves your system
- Fallback to local insights if AI isn’t available

## Tech Stack
- Frontend/UI: Streamlit
- Data Handling: Pandas, NumPy
- Visualization: Plotly Express
- AI Integration: Ollama (local LLMs)
- Reporting: ReportLab (PDF export)

## Installation

- 1 Clone the Repository:
  - <img width="688" height="136" alt="image" src="https://github.com/user-attachments/assets/1f8820d6-e8cb-4c3b-b382-8e333f90651a" />
- 2 Create a Virtual Environment:
-  <img width="601" height="173" alt="image" src="https://github.com/user-attachments/assets/8b1cb2b6-76e1-4b32-a377-ca5cb215766b" />
- 3 Install Dependencies:
- <img width="463" height="110" alt="image" src="https://github.com/user-attachments/assets/79d2b240-15fb-4974-975a-5a9ab623b9e1" />
- 4 (Optional) Set Up Ollama for AI Insights:
- Install https://ollama.com/
- <img width="982" height="315" alt="image" src="https://github.com/user-attachments/assets/9d2f7781-1df0-4289-9854-0655872fa3d0" />
- 5 Run the App
- <img width="332" height="107" alt="image" src="https://github.com/user-attachments/assets/299bb5a7-6d59-4647-9b81-0bdc9e4cb857" />

## Project Structure
<img width="765" height="274" alt="image" src="https://github.com/user-attachments/assets/cb547cdb-b3c5-4d50-be2e-03039ab53814" />

## Contribution Guide
We welcome contributions to improve Auto BI Dashboard.
### How to Contribute

<img width="976" height="526" alt="image" src="https://github.com/user-attachments/assets/31117a31-c314-441f-8521-81aaceefb9ea" />

## Suggested Contributions
- Add drag-and-drop functionality for dashboard layout
- Add new chart types (Heatmap, Distribution, TreeMap, etc.)
- Improve UI/UX responsiveness and themes
- Add support for databases (Postgres, MySQL, MongoDB)
- Expand AI insights with more models

  
