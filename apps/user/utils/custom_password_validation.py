import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class NoKoreanPasswordValidator:
    def validate(self, password, user=None):
        if re.search(r"[ㄱ-ㅎㅏ-ㅣ가-힣]", password):
            raise ValidationError(
                _("Passwords cannot contain Korean characters."),
                code="password_no_korean",
            )

    def get_help_text(self):
        return _("Passwords cannot contain Korean characters.")
