THRESHOLDS = {
    "cpu": 75,
    "memory": 75,
    "disk": 90
}


def check_threshold(metric, value):
    threshold = THRESHOLDS[metric]

    if value > threshold:
        return {
            "metric": metric,
            "value": value,
            "message": f"{metric.upper()} is high: {value:.1f}%"
        }

    return None
