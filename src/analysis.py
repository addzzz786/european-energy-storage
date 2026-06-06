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



def compute_switching_signal(merged_df: pd.DataFrame,
                             switch_threshold: float = 55.0
                             ) -> pd.DataFrame:
    """
    Compute coal-gas switching signal from TTF price

    When TTF exceeds the switching threshold, gas-fired power generation becomes uneconomic relative to coal. Utilities will switch to coal

    The threshold represents the approximate TTF price at which a gas plant and a coal plant have equal generation cost, accounts for typical thermal efficincies and EU carbon price

    Parameters
    - - - - - -

    merged_df: pd.Dataframe
        Must contain 'ttf_price' column
    switch_threshold: float
        TTF price in EUR/MWh above which coal swithcing occurs
        Default 55.0 EUR/MWh reflects ~EUR25/t carbon price assumption

    Returns
    - - - - - 
    pd.DataFrame
        Input df plus columns:
        - switching_active: bool, True when TTF > threshold
        - switching_intensity: float, (TTF - threshold) / threshold
        normalised measure of how far above threshold we are
        0 when switching inactive, positive when active
    """

    df = merged_df.copy()

    df["switching_active"] = df["ttf_price"] > switch_threshold

    df["switching_intensity"] = (
        (df["ttf_price"] - switch_threshold) / switch_threshold
    ).clip(lower=0)

    return df