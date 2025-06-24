import os
from dotenv import load_dotenv
from google.adk import Agent
from google.cloud import bigquery
import datetime
from google.genai import types
import pandas as pd

model_name = os.getenv("MODEL")

from google.adk.tools.tool_context import ToolContext
from google.cloud import bigquery


def forecast_demand(part_name: str, look_back_days: int = 1000, forecast_period: int = 30) -> dict:
    """
    Forecasts demand for a given automotive part using historical sales data.

    Args:
        part_name: The name of the automotive part.
        look_back_days: The number of days of historical data to consider.
        forecast_period: The number of days into the future to forecast.

    Returns:
        A dictionary containing the forecast results, or an error message.
    """
    try:
        client = bigquery.Client()
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(days=look_back_days)
        end_date_str = end_date.strftime("%Y-%m-%d")
        start_date_str = start_date.strftime("%Y-%m-%d")

        # Example using a public dataset (replace with your actual dataset)
        query = f"""
            SELECT 
                DATE(order_date) as order_day,
                SUM(quantity) as total_quantity
            FROM `hacker2025-team-3-dev.DemandDS.auto_sales`
            WHERE product_name = '{part_name}'
              AND DATE(order_date) BETWEEN '{start_date_str}' AND '{end_date_str}'
            GROUP BY 1
            ORDER BY 1
        """

        print(f"Running query:\n{query}")  # Debug log
        query_job = client.query(query)
        df = query_job.to_dataframe()

        if df.empty:
            return {"status": "No data found", "message": f"No sales data for '{part_name}' in the specified period."}

        # Simple Moving Average Forecasting
        window_size = 7  # Adjust the window size as needed
        if len(df) < window_size:
            return {"status": "error", "message": f"Not enough data points for a moving average with window size {window_size}."}

        # Calculate the moving average of the quantity
        df['moving_average'] = df['total_quantity'].rolling(window=window_size).mean()

        # The forecast is the last moving average value repeated for the forecast period
        last_moving_average = df['moving_average'].iloc[-1]
        forecast = [last_moving_average] * forecast_period
        forecast_dates = [end_date + datetime.timedelta(days=i) for i in range(1, forecast_period + 1)]

        forecast_df = pd.DataFrame({'forecast_date': forecast_dates, 'predicted_demand': forecast})

        return {
            "status": "success",
            "text": f"Forecast for {part_name} over the next {forecast_period} days:",
            "data": {
                "part_name": part_name,
                "forecast_period": forecast_period,
                "forecast": forecast_df.to_dict(orient='records')
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to forecast demand: {str(e)}"
        }


# Define the agent
root_agent = Agent(
    name="demand_prediction_agent",
    model=model_name,
    description="Forecasts demand for automotive parts using historical sales data.",
    instruction=(
        "You are a helpful agent that forecasts the demand for automotive parts. "
        "You use historical sales data from a database to make predictions. "
        "When asked to forecast demand, provide the part name and the number of days to forecast. "
        "The agent will return a forecast for the specified period."
    ),
    tools=[forecast_demand]
)
