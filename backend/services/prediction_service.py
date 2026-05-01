"""
Random Forest Adaptive Wait-Time Prediction Service
----------------------------------------------------
- Uses Admin's set average_service_time as the FALLBACK (cold start).
- Once 3+ real service times have been recorded, it switches to a 
  Random Forest Regressor trained on actual completed token data.
- Retrains every time this function is called (lightweight for small queues).
"""

MIN_SAMPLES_FOR_ML = 3  # minimum real data points before RF kicks in

def predict_service_time(queue):
    """
    Returns the predicted average service time (in minutes) for a queue.
    Uses Random Forest if enough historical data exists; 
    otherwise falls back to admin-set average.
    """
    from models.token import Token

    completed = Token.query.filter_by(
        queue_id=queue.id, status='completed'
    ).filter(Token.actual_service_time.isnot(None)).all()

    actual_times = [t.actual_service_time for t in completed if t.actual_service_time and t.actual_service_time > 0]

    if len(actual_times) < MIN_SAMPLES_FOR_ML:
        print(f"[PREDICTION] Queue '{queue.name}': Using Admin average ({queue.average_service_time} min). Real samples so far: {len(actual_times)}/{MIN_SAMPLES_FOR_ML}")
        return queue.average_service_time

    # Build features: [token_number, time_of_day_hour, position_in_queue]
    X = []
    y = []
    for i, t in enumerate(completed):
        if not t.actual_service_time or t.actual_service_time <= 0:
            continue
        hour = t.served_at.hour if t.served_at else 12
        X.append([t.token_number, hour, i + 1])
        y.append(t.actual_service_time)

    if len(X) < MIN_SAMPLES_FOR_ML:
        return queue.average_service_time

    try:
        from sklearn.ensemble import RandomForestRegressor
        import numpy as np

        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)

        # Predict for the "next" token (approximate features)
        next_position = len(completed) + 1
        from datetime import datetime
        current_hour = datetime.utcnow().hour
        predicted = model.predict([[next_position, current_hour, next_position]])[0]

        # Safety clamp: don't let prediction go below 1 min or above 5x admin average
        predicted = max(1.0, min(predicted, queue.average_service_time * 5))
        print(f"[PREDICTION] Queue '{queue.name}': 🤖 Random Forest predicts {round(predicted,1)} min (was {queue.average_service_time} min admin avg). Trained on {len(X)} real samples.")
        return round(predicted, 1)

    except Exception as e:
        # If scikit-learn not installed or any error, gracefully fall back
        print(f"[RF Prediction fallback] {e}")
        return queue.average_service_time
