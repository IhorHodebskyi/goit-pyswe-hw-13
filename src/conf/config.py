from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: str
    MAIL_SSL_TLS: str
    USE_CREDENTIALS: str
    VALIDATE_CERTS: str
    REDIS_DOMAIN: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: int
    CLOUDINARY_API_SECRET: str

    @field_validator("DB_URL")
    @classmethod
    def validate_db_url(cls, v: str):
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError("DB_URL must start with 'postgresql+asyncpg://'")
        return v

    @field_validator("JWT_ALGORITHM")
    @classmethod
    def validate_jwt_algorithm(cls, v: str):
        allowed = ["HS256", "HS384", "HS512"]
        if v not in allowed:
            raise ValueError(f"JWT_ALGORITHM must be one of: {', '.join(allowed)}")
        return v

    @field_validator("MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_SERVER", "MAIL_FROM", "MAIL_FROM_NAME")
    @classmethod
    def validate_non_empty_str(cls, v: str):
        if not v or not isinstance(v, str):
            raise ValueError("This field must be a non-empty string")
        return v

    @field_validator("MAIL_PORT", "REDIS_PORT")
    @classmethod
    def validate_positive_port(cls, v: int):
        if not isinstance(v, int) or v <= 0:
            raise ValueError("Port must be a positive integer")
        return v

    @field_validator("MAIL_STARTTLS", "MAIL_SSL_TLS", "USE_CREDENTIALS", "VALIDATE_CERTS")
    @classmethod
    def validate_boolean_strings(cls, v: str):
        if v not in ["True", "False"]:
            raise ValueError("Must be 'True' or 'False' as string")
        return v

    # @field_validator("REDIS_DOMAIN", "REDIS_PASSWORD")
    # @classmethod
    # def validate_redis_str_fields(cls, v: str):
    #     if not isinstance(v, str) or not v:
    #         raise ValueError("This Redis field must be a non-empty string")
    #     return v

    model_config = ConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
