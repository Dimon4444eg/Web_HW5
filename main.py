import sys
import asyncio
import httpx

from datetime import datetime, timedelta


class HTTPException(Exception):
    pass


async def request(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise HTTPException(f"Error code: {r.status_code} for {url}")


async def main(index_day, *currencies):
    if int(index_day) > 10:
        print("Max index day is 10")
        return None
    d = datetime.now() - timedelta(days=int(index_day))
    shift = d.strftime("%d.%m.%Y")
    try:
        response = await request(f"https://api.privatbank.ua/p24api/exchange_rates?date={shift}")

        selected_currencies = ['EUR', 'USD'] + list(currencies)
        parsed_data = {
            shift: {
                currency['currency']: {
                    'sale': currency.get('saleRate', currency['saleRateNB']),
                    'purchase': currency.get('purchaseRate', currency['purchaseRateNB'])
                } for currency in response['exchangeRate'] if currency.get('currency') in selected_currencies
            }
        }

        return parsed_data

    except HTTPException as err:
        print(err)
        return None


if __name__ == "__main__":
    r = asyncio.run(main(sys.argv[1], *sys.argv[2:]))
    print(r)
