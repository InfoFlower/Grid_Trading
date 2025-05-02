import polars as pl
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO

def fig_to_svg(fig) -> str:
    """
    Convertit une figure matplotlib en chaîne SVG.

    Args:
        fig (matplotlib.figure.Figure): La figure à convertir.

    Returns:
        str: Contenu SVG de la figure.
    """
    buf = StringIO()
    fig.savefig(buf, format='svg')
    svg_data = buf.getvalue()
    buf.close()
    return svg_data

def load_data(positions_file: str) -> pl.DataFrame:
    """
    Charge et prépare les données de positions à partir d'un fichier CSV.

    Args:
        positions_file (str): Chemin vers le fichier CSV des positions.

    Returns:
        pl.DataFrame: DataFrame avec colonnes Date (datetime) et MoneyBalance.
    """
    df = pl.read_csv(positions_file)

    df = (
        df
        .with_columns([
            pl.col("EventData_Time").cast(pl.Int64),
            (pl.col("EventData_Time") // 1000).alias("timestamp_s"),
        ])
        .sort("EventData_Time")
        .with_columns([
            pl.from_epoch("timestamp_s", time_unit="s").alias("Date")
        ])
        .select(["Date", "MoneyBalance"])
        .unique(subset=["Date"])
        .sort("Date")
    )
    return df


def compute_equity_curve(equity_df: pl.DataFrame) -> dict:
    dates = equity_df["Date"].to_list()
    balances = equity_df["MoneyBalance"].to_numpy()
    peaks = np.maximum.accumulate(balances)
    drawdowns = balances - peaks
    drawdowns_pct = (drawdowns / peaks) * 100
    return {
        "dates": dates,
        "balances": balances,
        "peaks": peaks,
        "drawdowns": drawdowns,
        "drawdowns_pct": drawdowns_pct,}


def plot_equity_curve(data_file: str, positions_file: str):
    equity_df = load_data(positions_file)
    metrics = compute_equity_curve(equity_df)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    ax1.plot(metrics["dates"], metrics["balances"], label="Equity Curve", color='blue')
    ax1.plot(metrics["dates"], metrics["peaks"], label="Peak", linestyle='--', color='green')
    ax1.set_title("Equity Curve")
    ax1.set_ylabel("Balance ($)")
    ax1.legend()
    ax1.grid(True)

    ax2.fill_between(metrics["dates"], metrics["drawdowns_pct"], 0, color='red', alpha=0.5)
    ax2.set_title("Drawdown (%)")
    ax2.set_ylabel("Drawdown %")
    ax2.set_xlabel("Date")
    ax2.grid(True)

    fig.tight_layout()
    return fig_to_svg(fig)

if __name__=='__main__':
    data_file='C:/Users/lenovo/Desktop/HomeLab/TradingBot/coin_datamart/data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/data_raw_BTCUSDT_2.csv'
    position_file='C:/Users/lenovo/Desktop/HomeLab/TradingBot/coin_datamart/src/OPE/reporting/data_logger/Position.csv'
    with open('C:/Users/lenovo/Desktop/HomeLab/TradingBot/coin_datamart/src/WEB/temp/essaie.svg',"w+",encoding='utf-8') as f :
        f.write(plot_equity_curve(data_file,position_file))