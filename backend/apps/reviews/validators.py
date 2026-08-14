from rest_framework import serializers

ALLOWED_FEEDBACK = {
    "noise_feedback": ("VERY_QUIET", "AVERAGE", "NOISY"),
    "wifi_feedback": ("EXCELLENT", "GOOD", "AVERAGE", "POOR"),
}


def validate_feedback(value, allowed, field_name):
    if value in ("", None):
        return value
    if value not in allowed:
        raise serializers.ValidationError(f"{field_name} uchun qiymatlar: {', '.join(allowed)}")
    return value