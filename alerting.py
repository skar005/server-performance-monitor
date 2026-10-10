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


def is_healthy(cpu, memory, disk):
    readings = (("cpu", cpu), ("memory", memory), ("disk", disk))
    return all(check_threshold(metric, value) is None for metric, value in readings)
