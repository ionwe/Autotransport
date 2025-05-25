import numpy as np
from datetime import datetime

def predict_failure_probability(maintenance_dates, current_date=None, horizon_days=30):
    """
    Оценивает вероятность поломки в течение horizon_days на основе истории ТО.
    maintenance_dates: список дат ТО (datetime)
    current_date: дата, на которую делается прогноз (по умолчанию сейчас)
    horizon_days: горизонт прогноза в днях
    """
    if len(maintenance_dates) < 2:
        return None
    maintenance_dates = sorted(maintenance_dates)
    intervals = [(maintenance_dates[i] - maintenance_dates[i-1]).days for i in range(1, len(maintenance_dates))]
    avg_interval = np.mean(intervals)
    if avg_interval == 0:
        return None
    lambda_ = 1 / avg_interval
    if current_date is None:
        current_date = datetime.now()
    days_since_last = (current_date - maintenance_dates[-1]).days
    # Вероятность отказа в течение horizon_days после последнего ТО
    prob = 1 - np.exp(-lambda_ * (days_since_last + horizon_days))
    return float(prob) 