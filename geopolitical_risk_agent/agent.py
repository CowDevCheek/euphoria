import os
from dotenv import load_dotenv
from google.adk import Agent
from google.cloud import bigquery
import datetime
from google.genai import types
from google.adk.tools.tool_context import ToolContext
from demand_predict_agent.agent import forecast_demand
from google.cloud import bigquery



model_name = os.getenv("MODEL")
def analyze_geopolitical_risk(country_code: str = "USA", days_back: int = 7) -> dict:
    """
    Analyzes geopolitical risk for a given country based on GDELT data of last 15 days.

    Args:
        country_code (str): The 3-letter country code (e.g., "CHN", "USA").
        days_back (int): The number of days back from today to analyze.

    Returns:
        dict: A dictionary containing the risk level, average Goldstein score,
              event count, and source URLs of relevant events.
              Returns an error message if an exception occurs.
    """
    
    try:
        client = bigquery.Client()
        today = datetime.datetime.utcnow()
        query = f"""
        SELECT SQLDATE, Actor1Name, Actor2Name, EventCode, GoldsteinScale, SOURCEURL
        FROM `gdelt-bq.gdeltv2.events`
        WHERE Actor1CountryCode = '{country_code}'
        ORDER BY SQLDATE DESC
        LIMIT 15
        """

        print(f"Running query:\n{query}")  # Debug log

        query_job = client.query(query)
        rows = list(query_job.result())
        print(rows)

        if not rows:
            print(f"No rows returned for {country_code} since {start_date}")  # Debug log
            return {
                "risk_level": "Unknown",
                "debug": f"No rows returned for {country_code} since {start_date}"
            }
        avg_goldstein = sum(row.GoldsteinScale for row in rows) / len(rows)
        sourceurls = [row.SOURCEURL for row in rows]


        if avg_goldstein < -3:
            risk = "High"
        elif avg_goldstein < 0:
            risk = "Moderate"
        else:
            risk = "Low"

        return {
            "risk_level": risk,
            "average_goldstein": avg_goldstein,
            "event_count": len(rows),
            "reasons": sourceurls
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to fetch risk data: {str(e)}"
        }




def recommend_supplier(part_name: str):
    """
    Recommends a supplier for a given automotive part.
    """
    client = bigquery.Client()
    dataset_id = "hacker2025-team-3-dev.gdelt_data_set"  # Replace with your dataset ID
    table_id = "automotive_parts"

    query = f"""
        SELECT supplier, country_code, cost
        FROM `{dataset_id}.{table_id}`
        WHERE part_name = '{part_name}'
    """
    print(f"Running query:\n{query}")  # Debug log
    query_job = client.query(query)
    parts = list(query_job.result())

    if not parts:
        return f"No suppliers found for {part_name}."

    recommendations = []
    for part in parts:
        risk_analysis = analyze_geopolitical_risk(country_code=part.country_code)
        if not risk_analysis:
            risk_level = "Unknown"
            reasons = ["No data available."]
        else:
            risk_level = risk_analysis.get("risk_level", "Unknown")
            reasons = risk_analysis.get("reasons", ["No specific geopolitical events found."])

        recommendations.append({
            "supplier": part.supplier,
            "country": part.country_code,
            "cost": part.cost,
            "risk_level": risk_level,
            "reasons": risk_analysis.get("reasons", [])[:3]
        })

    # Sort by risk (Low < Moderate < High < Unknown) and then by cost
    risk_order = {"Low": 0, "Moderate": 1, "High": 2, "Unknown": 3}
    sorted_recommendations = sorted(
        recommendations,
        key=lambda x: (risk_order.get(x["risk_level"], 3), x["cost"])
    )

    best = sorted_recommendations[0]
    reasons_text = "\n".join(best["reasons"][:3])  # show up to 3 reasons

    return best

    



# Define the agent
root_agent = Agent(
    name="geopolitical_risk_agent",
    model=model_name,
    description="Analyzes geopolitical risks, recommends automotive part suppliers, and predicts demand.",
    instruction=(
    "You are a helpful agent that recommends suppliers for automotive parts based on geopolitical risk and cost, "
    "or predicts demand for parts. First, determine whether the user is asking for a demand prediction or a supplier "
    "recommendation:\n"
    "- If the user asks for a demand forecast, use the 'forecast_demand' tool.\n"
    "- If the user asks for a supplier recommendation (e.g. 'Where should I get brakes from?', or 'Best place to source alternators'), "
    "use the 'analyze_geopolitical_risk' and 'recommend_supplier' tools together.\n"
    "\n"
    "For supplier recommendations:\n"
    "- Do NOT ask the user 'from which country are you sourcing?' unless the user explicitly asks for the risk/cost *of a specific country*.\n"
    "- Use the tools to automatically find and recommend the best country to source the part from, considering both cost and geopolitical risk.\n"
    "- Use 'recommend_supplier' to get supplier info, including supplier name, country, cost, and risk level.\n"
    "\n"
    "If the user explicitly mentions a country (e.g. 'What is the risk if I buy brakes from China?'), convert the country to its 3-letter ISO code, "
    "use 'analyze_geopolitical_risk' for that country, and return the result.\n"
    "\n"
    "Always respond clearly and include: Supplier Name, Country, Cost, and Risk Level — unless the user asked for something else."
    )
,
    tools=[forecast_demand, analyze_geopolitical_risk, recommend_supplier]
)
