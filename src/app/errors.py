class APIError(Exception):
    def __init__(self, message='Internal Server Error', status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {'error': self.message}


class RouteNotFoundError(APIError):
    def __init__(self):
        super().__init__('Route not found', status_code=404)


class CurrencyNotFoundError(APIError):
    def __init__(self, *missing_codes: str):
        if not missing_codes:
            message = 'Currency not found'
        elif len(missing_codes) == 1:
            message = f"Currency '{missing_codes[0]}' not found"
        else:
            missing = "', '".join(missing_codes)
            message = f"Currencies not found: '{missing}'"
        super().__init__(message, status_code=404)


class CurrencyAlreadyExistsError(APIError):
    def __init__(self, code: str):
        super().__init__(f"Currency '{code}' already exists", status_code=409)


class InvalidPairError(APIError):
    def __init__(self):
        super().__init__('Invalid pair format', status_code=400)


class ExchangeRateNotFoundError(APIError):
    def __init__(self, from_currency: str, to_currency: str):
        super().__init__(
            f'Exchange rate {from_currency} → {to_currency} not found', status_code=404
        )


class ExchangeRateAlreadyExistsError(APIError):
    def __init__(self, from_currency: str, to_currency: str):
        super().__init__(
            f'Exchange rate {from_currency} → {to_currency} already exists',
            status_code=409,
        )


class InvalidAmountFormatError(APIError):
    def __init__(self):
        super().__init__('Invalid amount format', status_code=400)


class MissingFormFieldError(APIError):
    def __init__(self):
        super().__init__('Missing required form field', status_code=400)


class UnknownCurrencyCodeError(APIError):
    def __init__(self, code: str):
        super().__init__(f'Unknown currency code: {code}', status_code=400)
