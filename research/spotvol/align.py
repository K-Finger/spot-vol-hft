import pandas as pd


def align_ticks(
    spot_df: pd.DataFrame,
    option_df: pd.DataFrame,
) -> pd.DataFrame:
    spot_sorted = spot_df.sort_values("time")
    option_sorted = option_df.sort_values("time")
    return pd.merge_asof(option_sorted, spot_sorted, on="time", direction="backward")
