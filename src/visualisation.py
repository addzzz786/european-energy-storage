import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def plot_seasonal_fan(df: pd.DataFrame) -> plt.Figure:
    """
    Plot European gas storage seasonal chart.

    Shows historical distribution of storage fill by day-of-year
    as a shaded band, with individual years as lines and 2022
    highlighted as the crisis year.

    Parameters
    ----------
    df : pd.DataFrame
        DatetimeIndex, must contain 'full_pct' column

    Returns
    -------
    plt.Figure
    """


    fig, ax = plt.subplots(figsize=(12, 6))

    df = df.copy()
    df["doy"] = df.index.day_of_year
    df["year"] = df.index.year

    years = sorted(df["year"].unique())



    grouped = df.groupby("doy")["full_pct"]

    doys = np.arange(1, 366)
    p10 = grouped.quantile(0.10).reindex(doys)
    p25 = grouped.quantile(0.25).reindex(doys)
    p50 = grouped.quantile(0.50).reindex(doys)
    p75 = grouped.quantile(0.75).reindex(doys)
    p90 = grouped.quantile(0.90).reindex(doys)

    
    ax.fill_between(doys, p10, p90,
                    alpha=0.15, color="steelblue",
                    label="10th–90th percentile")
    ax.fill_between(doys, p25, p75,
                    alpha=0.25, color="steelblue",
                    label="25th–75th percentile")
    ax.plot(doys, p50,
            color="steelblue", linewidth=1.5,
            linestyle="--", label="Median")

    
    year_colors = {
        2022: "#d62728",   # red — crisis injection year
        2023: "#ff7f0e",   # orange — post-crisis
        2024: "#2ca02c",   # green — current
    }

    for year in years:
        year_data = df[df["year"] == year].set_index("doy")["full_pct"]
        year_data = year_data.reindex(doys)

        if year in year_colors:
            ax.plot(doys, year_data,
                    color=year_colors[year],
                    linewidth=2.0,
                    label=str(year),
                    zorder=5)
        else:
            ax.plot(doys, year_data,
                    color="lightgrey",
                    linewidth=0.8,
                    alpha=0.7,
                    zorder=3)

    
    for year, color in year_colors.items():
        year_data = df[df["year"] == year].set_index("doy")["full_pct"]
        if year_data.empty:
            continue
        min_doy = year_data.idxmin()
        min_val = year_data.min()
        ax.annotate(f"{year}: {min_val:.1f}%",
                    xy=(min_doy, min_val),
                    xytext=(min_doy + 10, min_val - 4),
                    fontsize=8,
                    color=color,
                    arrowprops=dict(arrowstyle="->",
                                   color=color,
                                   lw=1.0))

    
    month_starts = [1, 32, 60, 91, 121, 152,
                    182, 213, 244, 274, 305, 335]
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    ax.set_xticks(month_starts)
    ax.set_xticklabels(month_labels)
    ax.set_xlim(1, 365)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Storage Fill (%)", fontsize=11)
    ax.set_xlabel("")
    ax.set_title("European Natural Gas Storage: Seasonal Pattern 2019–2024",
                 fontsize=13, fontweight="bold", pad=15)

    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

   
    fig.text(0.99, 0.01,
             "Source: GIE AGSI+",
             ha="right", va="bottom",
             fontsize=8, color="grey")

    plt.tight_layout()
    return fig



def plot_price_storage_overlay(merged_df: pd.DataFrame) -> plt.Figure:
    """
    Plot TTF price and storage fill on dual y-axes as a time series

    This will visually show the inverse relationship between storage levels and spot prices, with the 2022 crisis period annotated

    Parameters
    - - - - - - 
    merged_df: pd.DataFrame
        DatetimeIndex, columns[full_pct, ttf_price]
    
    Returns
    - - - - - - 
    plt.Figure
    """

    fig, ax1 = plt.subplots(figsize=(14,6))

    # Storage fill on the left axis
    colour_storage = "steelblue"
    ax1.set_ylabel("Storage Fill (%)", color=colour_storage, fontsize=11)
    ax1.plot(merged_df.index, merged_df["full_pct"],
             color=colour_storage, linewidth=1.5,
             label="Storage Fill %", alpha=0.9)
    ax1.tick_params(axis="y", labelcolor=colour_storage)
    ax1.set_ylim(0,110)

    # TTF price on the right axis
    ax2 = ax1.twinx()
    color_price = "#d62728"
    ax2.set_ylabel("TTF Price (€/MWh)", color=color_price, fontsize=11)
    ax2.plot(merged_df.index, merged_df["ttf_price"],
             color=color_price, linewidth=1.5,
             label="TTF Price", alpha=0.9)
    ax2.tick_params(axis="y", labelcolor=color_price)
    ax2.set_ylim(0, 380)

    # Annotate crisis peak 
    peak_date = merged_df["ttf_price"].idxmax()
    peak_price = merged_df["ttf_price"].max()
    ax2.annotate(f"Crisis peak\n€{peak_price:.0f}/MWh\n{peak_date.strftime('%b %Y')}",
                 xy=(peak_date, peak_price),
                 xytext=(peak_date - pd.DateOffset(months=8), peak_price - 60),
                 fontsize=9,
                 color=color_price,
                 arrowprops=dict(arrowstyle="->",
                                color=color_price,
                                lw=1.0))

    # Shade crisis period
    crisis_start = pd.Timestamp("2021-10-01")
    crisis_end = pd.Timestamp("2023-01-01")
    ax1.axvspan(crisis_start, crisis_end,
                alpha=0.08, color="red",
                label="Crisis period")

    # Combined legend 
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc="upper left", fontsize=9, framealpha=0.9)

    ax1.set_xlabel("")
    ax1.set_title("European Gas Storage vs TTF Price: 2019–2024",
                  fontsize=13, fontweight="bold", pad=15)

    ax1.grid(axis="y", alpha=0.3, linestyle="--")
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    fig.text(0.99, 0.01,
             "Source: GIE AGSI+ / Yahoo Finance",
             ha="right", va="bottom",
             fontsize=8, color="grey")

    plt.tight_layout()
    return fig



def plot_switching_signal(signal_df: pd.DataFrame,
                          switch_threshold: float = 55.0) -> plt.Figure:
    """
    Plot TTF price with coal-gas switching signal highlighted.

    Shades periods where TTF exceeds the switching threshold,
    indicating coal is economically preferred for power generation.

    Parameters
    ----------
    signal_df : pd.DataFrame
        Output of compute_switching_signal(), must contain
        'ttf_price', 'switching_active', 'switching_intensity'
    switch_threshold : float
        Threshold line to draw on chart

    Returns
    -------
    plt.Figure
    """

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                    sharex=True,
                                    gridspec_kw={"height_ratios": [3, 1]})

    # --- Top panel: TTF price with switching periods shaded ---
    ax1.plot(signal_df.index, signal_df["ttf_price"],
             color="#d62728", linewidth=1.5,
             label="TTF Price (€/MWh)", zorder=3)

    ax1.axhline(y=switch_threshold,
                color="darkorange", linewidth=1.5,
                linestyle="--",
                label=f"Switching threshold (€{switch_threshold}/MWh)",
                zorder=2)

    # Shade switching active periods
    ax1.fill_between(signal_df.index,
                     0, signal_df["ttf_price"],
                     where=signal_df["switching_active"],
                     alpha=0.25, color="darkorange",
                     label="Coal switching active",
                     zorder=1)

    # Annotate switching period duration
    active = signal_df[signal_df["switching_active"]]
    if not active.empty:
        mid_point = active.index[len(active) // 2]
        ax1.annotate(f"{len(active)} days of\ncoal switching",
                    xy=(mid_point, switch_threshold),
                    xytext=(mid_point, switch_threshold + 80),
                    fontsize=9,
                    color="darkorange",
                    ha="center",
                    arrowprops=dict(arrowstyle="->",
                                   color="darkorange",
                                   lw=1.0))

    ax1.set_ylabel("TTF Price (€/MWh)", fontsize=11)
    ax1.set_ylim(0, 380)
    ax1.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax1.set_title("Coal-Gas Switching Signal: TTF Price vs Switching Threshold",
                  fontsize=13, fontweight="bold", pad=15)
    ax1.grid(axis="y", alpha=0.3, linestyle="--")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # --- Bottom panel: switching intensity ---
    ax2.fill_between(signal_df.index,
                     0, signal_df["switching_intensity"],
                     where=signal_df["switching_active"],
                     alpha=0.7, color="darkorange")

    ax2.plot(signal_df.index, signal_df["switching_intensity"],
             color="darkorange", linewidth=0.8, alpha=0.5)

    ax2.set_ylabel("Switching\nIntensity", fontsize=9)
    ax2.set_ylim(0, signal_df["switching_intensity"].max() * 1.1)
    ax2.grid(axis="y", alpha=0.3, linestyle="--")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.text(0.99, 0.01,
             "Source: GIE AGSI+ / Yahoo Finance",
             ha="right", va="bottom",
             fontsize=8, color="grey")

    plt.tight_layout()
    return fig