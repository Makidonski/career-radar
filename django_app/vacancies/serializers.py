from rest_framework import serializers

from .models import Alert, SearchFilter, Skill, Vacancy, ViewHistory


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class VacancySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Vacancy
        fields = [
            "id", "source", "external_id", "title", "company_name", "city", "url",
            "description", "salary_from", "salary_to", "salary_currency", "salary_basis",
            "skills", "published_at", "collected_at",
        ]


class SearchFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchFilter
        fields = ["id", "name", "keyword", "city", "min_salary", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ViewHistorySerializer(serializers.ModelSerializer):
    vacancy = VacancySerializer(read_only=True)
    vacancy_id = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(), source="vacancy", write_only=True
    )

    class Meta:
        model = ViewHistory
        fields = ["id", "vacancy", "vacancy_id", "viewed_at"]
        read_only_fields = ["id", "viewed_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ["id", "skill", "city", "min_salary", "is_active", "created_at",
                  "last_triggered_at"]
        read_only_fields = ["id", "created_at", "last_triggered_at"]
        # NOTE: `user` intentionally excluded here - it's set server-side in
        # AlertViewSet.perform_create, never trusted from client input.
