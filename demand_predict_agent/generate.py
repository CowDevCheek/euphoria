import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_data(num_rows=1000, start_date=datetime(2022, 1, 1), end_date=datetime(2023, 12, 31)):
    """Generates synthetic sales data for automotive parts."""

    part_names = ["Brake Pads", "Engine Filters", "Spark Plugs", "Headlights", "Taillights", "Alternators", "Starters", "Radiators", "Water Pumps", "Fuel Pumps"]  # Example parts
    date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    data = []
    for _ in range(num_rows):
        order_date = np.random.choice(date_range)
        product_name = np.random.choice(part_names)
        quantity = np.random.randint(1, 10)  # Adjust the range as needed
        data.append([order_date.strftime("%Y-%m-%d"), product_name, quantity])

    df = pd.DataFrame(data, columns=["order_date", "product_name", "quantity"])
    return df

# Generate and save the data
synthetic_df = generate_synthetic_data(num_rows=2000)  # Adjust the number of rows as needed
synthetic_df.to_csv("synthetic_automotive_parts_data.csv", index=False)

print("Synthetic data generated and saved to synthetic_automotive_parts_data.csv")
