from typing import Annotated

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from pydantic import AfterValidator, BaseModel, Field, ValidationInfo, field_validator

from core.models import User


def _normalize_email(value: str) -> str:
    try:
        validate_email(value)
    except DjangoValidationError:
        raise ValueError('Enter a valid email address')

    return User.objects.normalize_email(value)


Email = Annotated[str, Field(max_length=255), AfterValidator(_normalize_email)]
Password = Annotated[str, Field(min_length=1, max_length=128)]


class RegisterItem(BaseModel):
    email: Email
    password: Password

    @field_validator('password')
    @classmethod
    def check_password_strength(cls, value: str, info: ValidationInfo) -> str:
        try:
            validate_password(value, user=User(email=info.data.get('email', '')))
        except DjangoValidationError as e:
            raise ValueError(' '.join(e.messages))

        return value


class LoginItem(BaseModel):
    email: Email
    password: Password


class AuthTokenResponse(BaseModel):
    token: str
    expires_at: str
