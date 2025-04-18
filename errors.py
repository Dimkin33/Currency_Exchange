from dataclasses import dataclass, field

import logging


logger = logging.getLogger(__name__)


# === Базовая ошибка API ===

@dataclass
class APIError(Exception):

    message: str = field(init=False)
    status_code: int = field(init=False)

    def to_dict(self):

        return {"error": self.message}

    def __str__(self):

        return self.message


# === Универсальный шаблон ошибок ===

@dataclass
class TemplateAPIError(APIError):
    template: str = field(init=False, repr=False)
    status: int = field(init=False, repr=False)

    def __post_init__(self):

        self.message = self.template.format(**self.__dict__)

        self.status_code = self.status


# ==== Ошибки валют ====
@dataclass
class RouteNotFoundError(TemplateAPIError):
    status: int = field(init=False, default=404)
    template: str = field(init=False, default="Route not found")


@dataclass
class MissingRequiredFieldsError(TemplateAPIError):

    status: int = field(init=False, default=400, repr=False)

    template: str = field(
        init=False, default="Отсутствует нужное поле формы: {fields}", repr=False)


@dataclass
class MissingCurrencyCodeError(TemplateAPIError):
    status: int = field(init=False, default=400, repr=False)
    template: str = field(
        init=False, default="Currency code is required", repr=False)


@dataclass
class CurrencyNotFoundError(TemplateAPIError):

    logger.error("CurrencyNotFoundError")
    code: str
    status: int = field(init=False, default=404, repr=False)
    template: str = field(
        init=False, default="Currency '{code}' not found", repr=False)


@dataclass
class CurrencyAlreadyExistsError(TemplateAPIError):
    code: str
    status: int = field(init=False, default=409, repr=False)
    template: str = field(
        init=False, default="Currency '{code}' already exists", repr=False)


# ==== Ошибки курсов обмена ====


@dataclass
class ExchangeRateNotFoundError(TemplateAPIError):

    from_currency: str
    to_currency: str
    status: int = field(init=False, default=404, repr=False)
    template: str = field(
        init=False, default="Exchange rate {from_currency} → {to_currency} not found", repr=False)


@dataclass
class ExchangeRateAlreadyExistsError(TemplateAPIError):

    from_currency: str
    to_currency: str
    status: int = field(init=False, default=409, repr=False)
    template: str = field(
        init=False, default="Exchange rate {from_currency} → {to_currency} already exists", repr=False)


# ==== Ошибки запроса ====


@dataclass
class InvalidCurrencyPairError(TemplateAPIError):
    pair: str

    status: int = field(init=False, default=400, repr=False)

    template: str = field(
        init=False, default="Invalid currency pair format: '{pair}'", repr=False)


@dataclass
class MissingRateFieldError(TemplateAPIError):

    status: int = field(init=False, default=400, repr=False)

    template: str = field(
        init=False, default="Missing required form field: 'rate'", repr=False)


@dataclass
class InvalidRateFormatError(TemplateAPIError):

    rate_value: str

    status: int = field(init=False, default=400, repr=False)

    template: str = field(
        init=False, default="Invalid rate format: '{rate_value}' (expected a number)", repr=False)
