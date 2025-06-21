import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers


class NoKoreanPasswordValidator:
    def validate(self, password, user=None):
        if re.search(r"[ㄱ-ㅎㅏ-ㅣ가-힣]", password):
            raise ValidationError(
                _("Passwords cannot contain Korean characters."),
                code="password_no_korean",
            )

    def get_help_text(self):
        return _("Passwords cannot contain Korean characters.")


def validate_strong_password(password, user=None):
    try:
        validate_password(password=password, user=user)
    except ValidationError as e:
        raise ValidationError(
            {
                "detail": "비밀번호가 보안 기준을 만족하지 않습니다.",
                "error_message": list(e.messages),
            }
        )


def validate_phone_number(value):
    cleaned = re.sub(r"\D", "", value)
    if not cleaned.isdigit() or len(cleaned) < 11:
        raise serializers.ValidationError("올바른 전화번호를 입력하세요.")
    return cleaned
