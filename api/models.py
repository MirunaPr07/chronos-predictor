from django.db import models


class DataSource(models.Model):
    """Sursele de date din care colectam"""
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_fetched = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RawData(models.Model):
    """Datele brute colectate de thread-uri"""
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True)
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['source', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.source.name} | {self.timestamp} | {self.value}"


class Prediction(models.Model):
    """Predictiile generate de modelul LSTM"""
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    predicted_at = models.DateTimeField(auto_now_add=True)
    target_timestamp = models.DateTimeField()
    predicted_value = models.FloatField()
    confidence = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-predicted_at']

    def __str__(self):
        return f"{self.source.name} | {self.target_timestamp} | {self.predicted_value}"


class Alert(models.Model):
    """Alerte generate cand valorile depasesc threshold-uri"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='low')
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.severity.upper()} | {self.source.name} | {self.timestamp}"