from celery import shared_task

@shared_task
def run_prediction(source_name: str = "sensor"):
    # we import here what we need, to avoid circular imports with django setup:
    from api.models import RawData, DataSource, Prediction
    from ml.predictor import Predictor
    from django.utils import timezone

    try:
        # we grab the data source from the db:
        source = DataSource.objects.get(name=source_name)
        # we pull the last 50 values for this source:
        recent_data = RawData.objects.filter(
            source=source
        ).order_by("-timestamp")[:50]
        
        if recent_data.count() < 20:
            return "not enough data to predict yet"
        
        values = list(recent_data.values_list("value", flat=True))
        # we reverse so the oldest value is first
        values = list(reversed(values))
        # we load the predictor and run it:
        predictor = Predictor()
        if not predictor.load():
            return "no trained model found"
        predictions = predictor.predict_next_n(values, steps=10)
        
        # we save each prediction in the db
        for pred in predictions:
            Prediction.objects.create(
                source=source,
                target_timestamp=timezone.now(),
                predicted_value=pred["predicted_value"],
                confidence=None,
            )
        return f"saved {len(predictions)} predictions for {source_name}"

    except DataSource.DoesNotExist:
        return f"source {source_name} not found in db"
    except Exception as e:
        return f"prediction failed: {str(e)}"