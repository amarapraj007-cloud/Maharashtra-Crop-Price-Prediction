# 🌾 Maharashtra Crop Price Prediction & Farmer Advisory Dashboard

An end-to-end Data Analytics and Machine Learning project designed to analyze agricultural crop prices, predict future price trends, and provide actionable market insights for farmers in Maharashtra.

## 📌 Project Overview

This project focuses on analyzing crop price trends across different Agricultural Produce Market Committee (APMC) markets in Maharashtra.

It uses Python, Machine Learning, MySQL, Flask, and Power BI to process agricultural price data, forecast upcoming prices, and generate farmer-oriented market advisories.

The project currently uses **synthetically generated, domain-realistic data**. Integration with live AGMARKNET data is prepared as a future enhancement and is not yet operational.

## 🎯 Project Objectives

- Analyze historical crop price trends across Maharashtra markets.
- Predict crop prices for the next 7 days using Machine Learning.
- Identify market-wise price variations.
- Generate actionable farmer advisories.
- Build interactive Power BI dashboards.
- Provide a Marathi-English farmer registration portal.
- Automate the data processing and notification workflow.

## 🌱 Crops Covered

- Onion
- Tomato
- Soybean
- Cotton
- Gram

## 📍 Markets Covered

The project covers 10 Maharashtra APMC markets:

Lasalgaon, Pimpalgaon, Nanded, Latur, Jalgaon, Aurangabad, Solapur, Amravati, Dhule, and Kolhapur.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and automation |
| Pandas & NumPy | Data cleaning and analysis |
| Scikit-learn | Machine Learning |
| Random Forest Regressor | Crop price prediction |
| MySQL 8.0 | Database management |
| SQL | Data analysis and reporting |
| Power BI | Interactive dashboards |
| Flask | Farmer registration portal |
| Gmail SMTP | Email notifications |
| Windows Task Scheduler | Workflow automation |

## ⚙️ Project Workflow

1. Generate and collect agricultural price data.
2. Clean and preprocess the dataset using Python.
3. Perform feature engineering.
4. Train separate Random Forest models for the five crops.
5. Predict crop prices for the next seven days.
6. Store processed data and predictions in MySQL.
7. Generate farmer advisories.
8. Display insights through Power BI dashboards.
9. Support farmer registration and email notifications.

## 📊 Power BI Dashboard

The interactive dashboard contains four main pages:

**1. Overview Dashboard**
- Overall crop price KPIs
- Market and crop-level summaries
- Price trend analysis

**2. Market Analysis**
- Market-wise price comparison
- Best market insights
- Geographic market analysis

**3. Crop Analysis**
- Crop-wise price trends
- Monthly price analysis
- Market comparison

**4. Price Prediction**
- Seven-day predicted price trends
- Current vs predicted price comparison
- Farmer advisory insights

## 🤖 Machine Learning

The project uses the Random Forest Regressor algorithm to predict future crop prices.

Separate models are developed for each crop to capture crop-specific price patterns.

Model performance is evaluated using regression metrics, including Mean Absolute Error (MAE), Mean Absolute Percentage Error (MAPE), and R² Score.

**Note:** Model performance is evaluated using the synthetic dataset and should not be interpreted as validated accuracy on real-world market prices.

## 👨‍🌾 Farmer Advisory Portal

A Flask-based registration portal allows farmers to submit their details and select preferred crops and markets.

The notification workflow is designed to provide email-based price alerts and advisory information.

The portal includes a Marathi-English interface to make registration easier for farmers.

## 📈 Project Dataset

The current synthetic dataset includes:

- 9,000 generated crop-price records
- 8,950 records after cleaning
- 5 crop-specific Machine Learning models
- 10 Maharashtra APMC markets
- 350 seven-day price predictions

These figures describe the generated project dataset and its processing workflow.

## 🚀 Future Enhancements

- Operational integration with live AGMARKNET data.
- Deployment of dashboards through Power BI Service.
- WhatsApp and Telegram notifications.
- Cloud-based deployment and automation.
- Marathi AI-powered farmer assistance using LLM and RAG.

## 👨‍💻 Author

**Amar Dipak Apraj**

Data Analytics | Python | SQL | Power BI | Machine Learning

