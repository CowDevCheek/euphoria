FROM python:3.12-slim

WORKDIR /app

COPY . .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose relevant ports
EXPOSE 5000    # ADK server
EXPOSE 8080    # Streamlit UI

# Default (can be overridden)
CMD ["streamlit", "run", "apps/gui_app.py", "--server.port=8080", "--server.enableCORS=false"]
