from django.contrib import admin

from .models import Alert, ParsingSource, SearchFilter, Skill, Vacancy, ViewHistory


@admin.register(ParsingSource)
class ParsingSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "base_url", "is_active"]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ["title", "company_name", "city", "salary_from", "salary_to",
                     "salary_basis", "source", "published_at"]
    list_filter = ["source", "city", "salary_basis"]
    search_fields = ["title", "company_name"]


@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "keyword", "city", "min_salary"]


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "vacancy", "viewed_at"]


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ["user", "skill", "city", "min_salary", "is_active", "last_triggered_at"]
    list_filter = ["is_active"]
