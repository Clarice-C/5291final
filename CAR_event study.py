# -*- coding: utf-8 -*-
"""Untitled9.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aCataoVKAOuKLmVvJiMgj6O2QP3o5K1z
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from datetime import timedelta
from scipy import stats

estimation_window_length = 60
event_window_length = 10

market_df = pd.read_csv('GSPC.csv', parse_dates=['Date'])
market_df.set_index('Date', inplace=True)
market_prices = market_df['Adj Close']

boeing_df = pd.read_csv('airbus_stock.csv', parse_dates=['Date'])
boeing_df.set_index('Date', inplace=True)
boeing_prices = boeing_df['Close']

events_df = pd.read_csv('Airbus.csv', parse_dates=['EventDate'])
events_df['EventDate'] = events_df['EventDate'].dt.normalize()

for col in ['FatalInjuryCount', 'SeriousInjuryCount', 'MinorInjuryCount']:
    if col in events_df.columns:
        events_df[col] = events_df[col].fillna(0)
    else:
        events_df[col] = 0


events_df['TotalInjury'] = events_df['FatalInjuryCount'] + events_df['SeriousInjuryCount'] + events_df['MinorInjuryCount']
events_df['InjuryScale'] = events_df['TotalInjury'].apply(lambda x: 'MajorInjury' if x > 100 else 'MinorInjury') ##set to >=0 for total

trading_days = pd.Series(market_prices.index.date)

boeing_start_date = boeing_prices.index.min().date()
min_valid_event_date = boeing_start_date + timedelta(days=estimation_window_length)

def get_closest_trading_day(event_date, trading_days):
    if isinstance(event_date, pd.Timestamp):
        event_date = event_date.date()

    if event_date in trading_days.values:
        return event_date

    closest_day = trading_days[trading_days <= event_date].max()
    if pd.isna(closest_day):
        return None
    return closest_day

def get_event_window_date(event_date, trading_days):
    day_0 = get_closest_trading_day(event_date, trading_days)
    if day_0 is None:
        return None, None, None, None

    try:
        day_neg1_idx = trading_days[trading_days < day_0].index[-1]
        day_neg1 = trading_days.iloc[day_neg1_idx]

        start_idx = day_neg1_idx - estimation_window_length + 1
        if start_idx < 0:
            return None, None, None, None

        start = trading_days.iloc[start_idx]

        estimation_window = trading_days[(trading_days >= start) & (trading_days <= day_neg1)]

        day_0_idx = trading_days[trading_days == day_0].index[0]
        end_event_idx = day_0_idx + event_window_length
        if end_event_idx >= len(trading_days):
            return None, None, None, None

        event_window = trading_days.iloc[day_neg1_idx:end_event_idx+1]

        return estimation_window, day_neg1, day_0, event_window
    except (IndexError, KeyError):
        return None, None, None, None

def compute_ar(event_date):
    estimation_window, day_neg1, day_0, event_window = get_event_window_date(event_date, trading_days)
    if any(x is None for x in (estimation_window, day_neg1, day_0, event_window)):
        return None

    market_returns = market_prices.pct_change().dropna()
    boeing_returns = boeing_prices.pct_change().dropna()

    try:
        estimation_dates = [pd.Timestamp(d) for d in estimation_window]
        X = market_returns.loc[estimation_dates]
        y = boeing_returns.loc[estimation_dates]

        if len(X) < estimation_window_length * 0.9:
            return None

        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()

        event_dates = [pd.Timestamp(d) for d in event_window]
        X_event = sm.add_constant(market_returns.loc[event_dates], has_constant='add')
        predicted = model.predict(X_event)
        actual = boeing_returns.loc[event_dates]
        ar = actual - predicted

        return ar
    except Exception:
        return None

def perform_event_study(event_dates):
    all_ar = []

    for date in event_dates:
        ar = compute_ar(date)
        if ar is not None:
            all_ar.append(ar)

    if len(all_ar) == 0:
        return None

    ar_df = pd.concat(all_ar, axis=1)
    ar_df.columns = [f'Event_{i}' for i in range(len(all_ar))]

    aar = ar_df.mean(axis=1)
    caar = aar.cumsum()

    L2 = event_window_length + 1

    car_values = []
    for col in ar_df.columns:
        car = ar_df[col].sum()
        car_values.append(car)

    mean_car = np.mean(car_values)

    s_car_squared = 0
    Mi = estimation_window_length

    for col in ar_df.columns:
        ar_squared_sum = (ar_df[col] ** 2).sum()
        s_car_squared += L2 * (1 / (Mi - 2)) * ar_squared_sum

    s_car_squared /= len(ar_df.columns)
    s_car = np.sqrt(s_car_squared)

    t_statistic = mean_car / s_car

    degrees_of_freedom = Mi - 2
    p_value = 2 * (1 - stats.t.cdf(abs(t_statistic), df=degrees_of_freedom))

    return {
        'event_count': len(ar_df.columns),
        'mean_car': mean_car,
        't_statistic': t_statistic,
        'p_value': p_value,
        'caar': caar,
        'car_values': car_values
    }

injury_scales = ['MajorInjury', 'MinorInjury']
results = {}


for scale in injury_scales:
    filtered_events_df = events_df[events_df['InjuryScale'] == scale]
    event_dates = sorted(filtered_events_df['EventDate'].dropna().unique())

    event_dates = [pd.Timestamp(d).date() if not isinstance(d, pd.Timestamp) else d.date() for d in event_dates]
    event_dates = [d for d in event_dates if d >= min_valid_event_date]

    result = perform_event_study(event_dates)
    if result is None:
        print(f"Warning: No valid event data for {scale} category!")
        continue

    results[scale] = result

summary_data = []
for scale, result in results.items():
    scale_label = 'Major Injury' if scale == 'MajorInjury' else 'Minor Injury'
    summary_data.append({
        'Event Category': scale_label,
        'Average CAR': result['mean_car'],
        't-statistic': result['t_statistic'],
        'p-value': result['p_value'],
        'Reject at 5%': 'Yes' if result['p_value'] < 0.05 else 'No',
    })

summary_df = pd.DataFrame(summary_data)