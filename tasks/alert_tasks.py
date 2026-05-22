from celery import shared_task

# threshold values: if a reading goes above these, we create an alert
THRESHOLDS = {
    "sensor": 85.0,
    "weather": 40.0,
    "crypto": 65000.0,
}

@shared_task
def check_for_alerts():
    # we import inside the task to avoid issues with django
    from api.models import RawData, DataSource, Alert

    for source_name, threshold in THRESHOLDS.items():
        try:
            source = DataSource.objects.get(name=source_name)
            # we only check the latest reading for each source
            latest = RawData.objects.filter(
                source=source
            ).order_by("-timestamp").first()
            if latest and latest.value > threshold:
                # we create an alert if the value exceeds the threshold:
                Alert.objects.create(
                    source=source,
                    message=f"{source_name} value {latest.value} exceeded threshold {threshold}",
                    severity=_get_severity(latest.value, threshold),
                )
                print(f"[AlertTask] alert created for {source_name}: {latest.value}")

        except DataSource.DoesNotExist:
            # source hasn't been created yet, so skip it
            continue


def _get_severity(value: float, threshold: float) -> str:
    # we calculate severity based on how much the value exceeds the threshold
    ratio = value / threshold
    if ratio >= 1.5:
        return "high"
    elif ratio >= 1.2:
        return "medium"
    return "low"