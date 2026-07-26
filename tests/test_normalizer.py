import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parser.normalizer import normalize_api_salary, normalize_text_salary  # noqa: E402


class TestNormalizeApiSalary:
    def test_full_gross_range(self):
        result = normalize_api_salary({"from": 100000, "to": 150000, "currency": "RUR", "gross": True})
        assert result.salary_from == 100000
        assert result.salary_to == 150000
        assert result.basis == "gross"
        assert result.currency == "RUR"

    def test_net_salary(self):
        result = normalize_api_salary({"from": 80000, "to": None, "currency": "RUR", "gross": False})
        assert result.salary_from == 80000
        assert result.salary_to is None
        assert result.basis == "net"

    def test_missing_gross_flag(self):
        result = normalize_api_salary({"from": 90000, "currency": "RUR"})
        assert result.basis == "unknown"

    def test_none_salary_object(self):
        result = normalize_api_salary(None)
        assert result.salary_from is None
        assert result.salary_to is None
        assert result.basis == "unknown"


class TestNormalizeTextSalary:
    def test_from_only(self):
        result = normalize_text_salary("от 100 000")
        assert result.salary_from == 100000
        assert result.salary_to is None

    def test_range_gross(self):
        result = normalize_text_salary("100 000 – 150 000 ₽ до вычета налогов")
        assert result.salary_from == 100000
        assert result.salary_to == 150000
        assert result.basis == "gross"

    def test_net_single_number(self):
        result = normalize_text_salary("120000 на руки")
        assert result.salary_from == 120000
        assert result.basis == "net"

    def test_empty_string(self):
        result = normalize_text_salary("")
        assert result.salary_from is None
        assert result.salary_to is None
        assert result.basis == "unknown"

    def test_usd_currency_detected(self):
        result = normalize_text_salary("from $2000 to $3000")
        assert result.currency == "USD"
        assert result.salary_from == 2000
        assert result.salary_to == 3000
