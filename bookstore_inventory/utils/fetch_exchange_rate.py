import json
import ssl
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi


def fetch_exchange_rate(currency_code: str) -> Decimal:
    api_url = "https://api.exchangerate-api.com/v4/latest/USD"
    req = Request(
        api_url,
        headers={"User-Agent": "bookstore-inventory-api/1.0"},
    )

    # This is to avoid SSL errors
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    try:
        with urlopen(req, timeout=10, context=ssl_context) as resp:
            payload = json.loads(resp.read().decode("utf-8"))


    # If there is an error throw error.
    except (HTTPError, URLError, TimeoutError, RuntimeError) as e:
        raise RuntimeError(str(e)) from e


    rates = payload.get("rates") or {}

    rate_raw = rates.get(currency_code)

    # If the currency is not found in the rates, raise an error 
    if rate_raw is None:
        raise ValueError(f"Currency '{currency_code}' not found in rates.")


    return Decimal(str(rate_raw))

