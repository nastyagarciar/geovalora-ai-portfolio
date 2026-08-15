# GeoValora AI

### Explainable and uncertainty-aware real estate valuation in Spain

GeoValora AI is an end-to-end Machine Learning project for residential property valuation in **Madrid, Barcelona and Valencia**.

The project goes beyond producing a single price estimate by combining predictive modeling with **uncertainty quantification, SHAP explainability, territorial context and an interactive Streamlit application**.

---

## Project Highlights

- End-to-end Data Science workflow
- Real-world residential property data
- Data cleaning and feature engineering
- Leakage prevention
- XGBoost regression
- Robust model validation
- SHAP model explainability
- Calibrated prediction intervals
- Territorial analysis
- Streamlit application
- Buyer and investor analytical tools
- Automated reporting

---

## Problem

Real estate price prediction is not only about estimating a number.

A useful analytical system should also answer:

- How reliable is the prediction?
- Which variables influenced the estimate?
- Is the property similar to observations seen during training?
- How does the estimate compare across geographical contexts?
- What are the limitations of the model?

GeoValora AI was designed around these questions.

---

## Machine Learning Approach

The project follows a structured experimental workflow:

1. Data quality assessment
2. Data cleaning
3. Exploratory Data Analysis
4. Feature engineering
5. Leakage prevention
6. Experimental design
7. Baseline modeling
8. Hyperparameter selection
9. Robust validation
10. Final evaluation
11. SHAP explainability
12. Uncertainty analysis and application packaging

The final model is based on **XGBoost** using a frozen feature contract of **52 predictors**.

---

## Final Model Performance

Final evaluation on the held-out TEST partition:

| Metric | Result |
|---|---:|
| R² (log target) | 0.9377 |
| MAE (log target) | 0.1348 |
| RMSE (log target) | 0.1843 |
| MAE | €47,936 |
| RMSE | €97,772 |
| Median Absolute Percentage Error | 10.26% |

The TEST partition was reserved for final evaluation and was not reused for subsequent model-selection decisions.

---

## Uncertainty

GeoValora AI complements point predictions with calibrated prediction intervals.

The final uncertainty framework achieved approximately:

- **90% target coverage**
- **90.17% observed TEST coverage**

This allows the system to communicate uncertainty instead of presenting a prediction as false precision.

---

## Explainability

Local predictions are explained using **SHAP**.

SHAP values help identify which features contribute positively or negatively to an individual prediction.

They describe model behavior and **should not be interpreted as causal effects**.

---

## GeoValora AI Application

The final project includes a Streamlit application with:

- Property valuation
- Prediction intervals
- Analytical confidence
- Local SHAP explanations
- City / district / neighborhood context
- Scenario comparison
- Buyer analysis
- Investor analysis
- JSON, HTML and PDF reports

The production application consumes frozen model artifacts and does not retrain the model during inference.

---
## Example Output

Below is an example of a GeoValora AI valuation report showing the historical estimate, prediction interval, analytical confidence, 2026 contextualization and local SHAP explanation.

![GeoValora AI valuation report](images/geovalora_report_page1.png)


## Technology Stack

- Python
- pandas
- NumPy
- scikit-learn
- XGBoost
- SHAP
- Matplotlib
- PyArrow
- joblib
- Streamlit
- Jupyter / Google Colab
- Git / GitHub

---

## Portfolio Repository Structure

```text
geovalora-ai-portfolio/
├── images/       Selected visual results
├── notebooks/    Selected portfolio notebooks
├── results/      Aggregated model results
├── src/          Selected reusable Python code
└── README.md
```

This repository is a **public portfolio version** of the project.

The complete academic repository, datasets and restricted artifacts are not redistributed here.

---

## Data Policy

The underlying project uses historical residential property listing data.

Complete original, cleaned and modeled datasets are **not included in this public repository**.

Only selected code, aggregated results and visualizations are published.

---

## Important Limitations

- The predictive model is based on historical 2018 listing-price data.
- Predictions represent estimated listing prices rather than guaranteed transaction prices.
- Territorial information may be approximate.
- SHAP explanations are not causal.
- Prediction intervals communicate model uncertainty but are not official appraisal intervals.
- GeoValora AI is an analytical prototype and not an official property appraisal service.

---

## Author

**Anastasia García Reziapova**

Master's Final Project  
Data Science, Big Data & Business Analytics
