from django import template

register = template.Library()


@register.filter
def to_roman(value: int) -> str:
    """Convert an integer to a Roman numeral."""
    if not isinstance(value, int) or value <= 0:
        return ""

    roman_numerals = [
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    result = []
    for arabic, roman in roman_numerals:
        count, value = divmod(value, arabic)
        result.append(roman * count)

    return "".join(result)
