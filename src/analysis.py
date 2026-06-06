import pandas as pd

def merge_storage_and_price(storage_df: pd.DataFrame,
                            price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge storage fill data with TTF price series

    Storage data is daily (and includes weekends)
    Price data is business days only
    Forward-filling price data into weekend/holiday gaps solves the issue

    Parameters
    - - - - - - 
    storage_df: pd.DataFrame
        DatetimeIndex, must contain 'full_pct' column
    price_df: pd.DataFrame
        DatetimeIndex, must contain 'ttf_price' column
    
    Returns
    - - - - - - 
    pd.DataFrame
        DatetimeIndex, columns: [full_pct, ttf_price]
        No NaNs in ttf_price - we use forward filling from Friday close price
    """

    df = storage_df[["full_pct"]].join(
        price_df[["ttf_price"]],
        how="left"
    )

    df["ttf_price"] = df["ttf_price"].ffill()
    df = df.dropna()
    return df