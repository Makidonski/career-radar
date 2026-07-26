import django_filters

from .models import Vacancy


class VacancyFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name="city", lookup_expr="iexact")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    skill = django_filters.CharFilter(field_name="skills__name", lookup_expr="iexact")
    salary_min = django_filters.NumberFilter(field_name="salary_from", lookup_expr="gte")
    salary_max = django_filters.NumberFilter(field_name="salary_to", lookup_expr="lte")

    class Meta:
        model = Vacancy
        fields = ["city", "title", "skill", "salary_min", "salary_max"]
