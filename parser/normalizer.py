
import re
from dataclasses import dataclass

GROSS_HINTS = ("до вычета", "gross", "до ндфл")
NET_HINTS = ("на руки", "net", "после вычета", "чистыми")

# Matches "100000", "100 000", "100.000", "100,000"
_NUMBER_RE = re.compile(r"\d[\d\s.,]*\d|\d")


@dataclass
class NormalizedSalary:
    salary_from: int | None
    salary_to: int | None
    currency: str
    basis: str  # "gross" | "net" | "unknown"


def _clean_number(raw: str) -> int:
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else 0


def normalize_api_salary(salary_obj: dict | None) -> NormalizedSalary:
    """Normalizes hh.ru's structured salary object from the API."""
    if not salary_obj:
        return NormalizedSalary(None, None, "RUR", "unknown")

    basis = "unknown"
    if "gross" in salary_obj:
        basis = "gross" if salary_obj["gross"] else "net"

    return NormalizedSalary(
        salary_from=salary_obj.get("from"),
        salary_to=salary_obj.get("to"),
        currency=salary_obj.get("currency") or "RUR",
        basis=basis,
    )


def normalize_text_salary(text: str) -> NormalizedSalary:
    """Normalizes a free-text salary string scraped from HTML, e.g.:
    "от 100 000", "100 000 – 150 000 ₽ до вычета налогов", "120000 на руки".
    """
    if not text or not text.strip():
        return NormalizedSalary(None, None, "RUR", "unknown")

    lowered = text.lower()

    basis = "unknown"
    if any(hint in lowered for hint in NET_HINTS):
        basis = "net"
    elif any(hint in lowered for hint in GROSS_HINTS):
        basis = "gross"

    currency = "USD" if "$" in text or "usd" in lowered else \
        "EUR" if "€" in text or "eur" in lowered else "RUR"

    numbers = [_clean_number(match) for match in _NUMBER_RE.findall(text)]
    numbers = [n for n in numbers if n > 0]

    salary_from = salary_to = None
    if "от" in lowered and numbers:
        salary_from = numbers[0]
    elif "до" in lowered and numbers and "вычета" not in lowered:
        salary_to = numbers[0]
    elif len(numbers) >= 2:
        salary_from, salary_to = numbers[0], numbers[1]
    elif len(numbers) == 1:
        salary_from = numbers[0]

    return NormalizedSalary(salary_from, salary_to, currency, basis)
