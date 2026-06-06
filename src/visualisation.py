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