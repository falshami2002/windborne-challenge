# https://gist.github.com/dkafayi/5334e8a3f1fc317d0f8b33141964df05

import pandas as pd
import numpy as np
from balloons import get_ballon_data
from calculations import ground_vector, wind_vector

def compute_control_vectors(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each balloon entry (hour to hour), compute:
    - Ground velocity vector (Vg)
    - Wind vector (Vw)
    - Control vector Vc = Vg - Vw
    """

    df = df.sort_values(["balloon_id", "hour_ago"]).reset_index(drop=True)

    results = []
    for balloon_id, group in df.groupby("balloon_id"):
        group = group.sort_values("hour_ago")
        group = group.reset_index(drop=True)

        for i in range(len(group) - 1):
            row_now = group.iloc[i]
            row_next = group.iloc[i + 1]

            # Ground vector (m/s)
            vx_g, vy_g, speed_g, bearing = ground_vector(
                row_now["lat"], row_now["lon"], row_next["lat"], row_next["lon"], dt_sec=3600
            )

            # Wind vector (m/s)
            wx, wy = wind_vector(row_now["wind_speed"], row_now["wind_direction"])

            # Control vector (difference), this is how much the balloon must move accounting for wind
            vx_c = vx_g - wx
            vy_c = vy_g - wy
            control_magnitude = np.sqrt(vx_c**2 + vy_c**2)

            results.append({
                "balloon_id": balloon_id,
                "hour_ago": row_now["hour_ago"],
                "lat": row_now["lat"],
                "lon": row_now["lon"],
                "alt_km": row_now["alt_km"],
                "vx_ground": vx_g,
                "vy_ground": vy_g,
                "speed_ground": speed_g,
                "wx": wx,
                "wy": wy,
                "vx_control": vx_c,
                "vy_control": vy_c,
                "control_magnitude": control_magnitude,
                "wind_speed": row_now["wind_speed"],
                "wind_direction": row_now["wind_direction"],
                "bearing": bearing
            })

    return pd.DataFrame(results)

if __name__ == "__main__":
    print("Fetching balloon data...")
    df = get_ballon_data()

    print("\nComputing control vectors...")
    result_df = compute_control_vectors(df)

    print(result_df.head())
    result_df.to_csv("balloon_control_vectors.csv", index=False)
    print("\nSaved results to balloon_control_vectors.csv")


