# 5291final
## ✈️ Econometric Modeling of Stock Reactions to Aviation Accidents
Columbia University | March 2025 – May 2025
This project investigates how major aviation accidents affect the short- and long-term stock performance of Boeing and Airbus using econometric and statistical modeling techniques.
We adopt a multi-stage pipeline involving ANOVA, event study methodology, and GARCH-X modeling to analyze market reactions across dimensions of return, volatility, and spillover effects.

## 📊 Methodology Overview
Two-Way ANOVA

Analyzed standardized closing stock prices across accident categories and manufacturers.

Assessed volatility-based significance of accident events on returns.

Event Study Analysis

Measured abnormal returns (AR) and cumulative abnormal returns (CAR) around event windows.

Estimated spillover effects and categorized events by severity level.

Identified statistically significant negative impacts of Boeing accidents on short-term stock performance, while Airbus remained relatively unaffected.

GARCH-X Volatility Modeling

Modeled long-term volatility response using accident severity variables (e.g., FatalInjuryCount, SeriousInjuryCount).

Discovered that accident severity significantly increased Boeing’s volatility, while Airbus showed limited response after accounting for market-wide effects.

## 🧾 Dataset Description
Time frame: 2010–2025

Stock data source: Yahoo Finance (daily close prices for Boeing and Airbus)

Accident data source: National Transportation Safety Board (NTSB)

Merged on: Date

Key features:

Make (Boeing/Airbus)

FatalInjuryCount, SeriousInjuryCount, MinorInjuryCount

State, Country (for regional grouping)

Boeing_Close, Airbus_Close (time series)

## 🔍 Key Findings
Return Impact: Major Boeing accidents consistently led to abnormal negative returns within event windows.

Volatility Sensitivity: GARCH-X results revealed Boeing’s volatility is significantly affected by accident severity, especially fatal accidents.

Cross-Manufacturer Comparison: Airbus showed lower volatility shifts and weaker return deviations under similar conditions.

## Table of Contents (Full Report)
1. Introduction  
2. Literature Review  
3. Data Collection and Description  
4. Exploratory Data Analysis  
5. Methodology  
   5.1 ANOVA  
   5.2 Event Study  
   5.3 GARCH-X  
6. Results and Interpretation  
7. Conclusion and Future Work  
8. References  
9. Appendix

