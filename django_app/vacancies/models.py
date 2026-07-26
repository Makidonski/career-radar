
from django.conf import settings
from django.db import models


class ParsingSource(models.Model):

    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField()
    is_active = models.BooleanField(default=True)
    # Free-form search params sent to the source, e.g. {"text": "python", "area": 1}
    default_params = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    class SalaryBasis(models.TextChoices):
        GROSS = "gross", "До вычета налогов"
        NET = "net", "На руки"
        UNKNOWN = "unknown", "Не указано"

    source = models.ForeignKey(ParsingSource, on_delete=models.CASCADE, related_name="vacancies")
    external_id = models.CharField(max_length=64, db_index=True)

    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    url = models.URLField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    work_schedule = models.CharField(max_length=20, blank=True, null=True)  # 'remote', 'full_day' и т.п.
    employment_type = models.CharField(max_length=20, blank=True, null=True)  # 'full', 'part', 'project'...
    salary_from = models.PositiveIntegerField(null=True, blank=True)
    salary_to = models.PositiveIntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=8, default="RUR")
    salary_basis = models.CharField(max_length=10, choices=SalaryBasis.choices,
                                     default=SalaryBasis.UNKNOWN)

    skills = models.ManyToManyField(Skill, blank=True, related_name="vacancies")

    published_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("source", "external_id")]
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["published_at"]),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company_name}"


class SearchFilter(models.Model):
    """A saved search a user wants tracked (used by /digest and dashboard)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="search_filters")
    name = models.CharField(max_length=120)
    keyword = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    min_salary = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user})"


class ViewHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="view_history")
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="views")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "vacancy")]


class Alert(models.Model):
    """Custom user-defined alert, e.g. 'notify me if a vacancy appears with
    skill X and salary >= Y'. Evaluated by parser.tasks.send_alert_notifications."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="alerts")
    skill = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120, blank=True)
    min_salary = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Alert(skill={self.skill!r}, min_salary={self.min_salary}) for {self.user}"
