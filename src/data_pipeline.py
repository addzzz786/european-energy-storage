import requests
import pandas as pd
import os
import time
import yfinance as yf


def fetch_agsi_storage(country_code: str = "eu",
                       start: str = "2019-01-01",
                       end: str = "2024-12-31") -> pd.DataFrame:
    """
    Fetch European gas storage data from GIE AGSI+ public API.

    Loops over each date in range, fetching one row per request.
    Saves to data/processed/ on first fetch, loads from disk on 
    subsequent runs.

    Parameters
    ----------
    country_code : str
        'eu' for aggregate Europe, 'de' for Germany etc. (lowercase)
    start : str
        Start date YYYY-MM-DD
    end : str
        End date YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        DatetimeIndex, columns: [full_pct, injection, withdrawal,
                                  working_gas_volume]
    """

    cache_path = (
        f"data/processed/agsi_{country_code}_{start}_{end}.parquet"
    )
    if os.path.exists(cache_path):
        print("Loading from cache...")
        return pd.read_parquet(cache_path)

    base_url = "https://agsi.gie.eu/api"
    headers = {"x-key": os.environ.get("AGSI_API_KEY")}

    date_range = pd.date_range(start=start, end=end, freq="D")

    all_rows = []

    for i, date in enumerate(date_range):
        date_str = date.strftime("%Y-%m-%d")

        params = {
            "country": country_code,
            "date": date_str,
            "size": 10
        }

        response = requests.get(base_url,
                                params=params,
                                headers=headers)
        response.raise_for_status()

        data = response.json().get("data", [])

        if not data:
            continue

        row = data[0]
        all_rows.append({
            "date": date_str,
            "full_pct": row.get("full"),
            "injection": row.get("injection"),
            "withdrawal": row.get("withdrawal"),
            "working_gas_volume": row.get("workingGasVolume")
        })

        if i % 50 == 0:
            print(f"Fetched {i}/{len(date_range)} dates...")

        time.sleep(0.1)

    df = pd.DataFrame(all_rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    numeric_cols = ["full_pct", "injection", "withdrawal",
                    "working_gas_volume"]
    df[numeric_cols] = df[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    os.makedirs("data/processed", exist_ok=True)
    df.to_parquet(cache_path)
    print(f"Saved to cache: {cache_path}")

    return df


def fetch_ttf_prices(start: str = "2019-01-01",
                     end: str = "2024-12-31") -> pd.DataFrame:
    """
    Fetch TTF natural gas front-month futures price using Yahoo Finance

    Parameters
    - - - - - - -
    start: str
        Start date YYYY-MM-DD
    end str
        End date YYYY-MM-DD

    Returns
    - - - - - - - 
    pd.DataFrame
        DatetimeIndex, columns: [ttf_price]
    """

    cache_path = f"data/processed/ttf_{start}_{end}.parquet"
    if os.path.exists(cache_path):
        print("Loading TTF data from cache")
        return pd.read_parquet(cache_path)
    
    print("Fetching TTF prices from yFinance")
    raw = yf.download("TTF=F", start=start, end=end, progress=False)

    if raw.empty:
        raise ValueError(
            "No TTF data downloaded, check parameters"
        )
    
    df = raw[["Close"]].copy()
    df.columns = ["ttf_price"]
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df.sort_index()
    df["ttf_price"] = pd.to_numeric(df["ttf_price"], errors="coerce")
    df = df.dropna()

    os.makedirs("data/processed", exist_ok=True)
    df.to_parquet(cache_path)
    print(f"Saved TTF to cache: {cache_path}")

    return df
