# 🚗 Automotive Risk Agent

This project is a GenAI-powered assistant that helps automotive companies make informed decisions about **sourcing parts** by analyzing **geopolitical risk** and **cost**. It can also **predict demand** for parts when asked.

Built with:
- **Streamlit** for a clean web interface
- **Google ADK (Agent Development Kit)** for intelligent agent orchestration
- **GDELT data** and cost models for sourcing decisions

---

## 💡 What Can It Do?

This AI assistant understands natural language and supports two main capabilities:

### 🛠 Supplier Recommendation
- "Where is the best place to source *brakes*?"
- "Recommend the cheapest and safest country for *engine* suppliers"

It returns:
- ✅ Best supplier country
- ✅ Risk level
- ✅ Estimated cost
- ✅ Supplier name (if available)

### 📈 Demand Prediction
- "Predict the demand for alternators in Q4"
- "How much demand will there be for tires in the next 3 months?"

It uses the agent's `forecast_demand` tool to give estimates based on historical patterns.

---

## ⚙️ Getting Started

### 📦 1. Clone the Repo
```bash
git clone https://github.com/your-username/automotive-agent-app.git
cd automotive-agent-app
```

### 🐍 2. Create & Activate a Virtual Environment
```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 📥 3. Install Requirements
```bash
pip install -r requirements.txt
```

---

## ☁️ Running the App on Google Cloud Console (or locally)

### 🧠 Terminal 1: Start the ADK Agent API Server
```bash
cd agent
adk api_server
```

> This will expose an API on `http://localhost:8000` that the Streamlit frontend will use.

---

### 🌐 Terminal 2: Launch the Streamlit App
In a **separate terminal**:
```bash
streamlit run streamlit_app.py
```

> This will start the frontend at `http://localhost:8501`.

---

## 💬 Example Questions to Ask

- "Where should I buy engines from?"
- "What is the safest country to source brakes?"
- "Can you predict demand for tires?"
- "What’s the risk if I source batteries from China?"

---

## 📁 Project Structure

```
automotive-agent-app/
├── agent/                  # Your ADK agent files
│   └── agent.py
├── streamlit_app.py        # Streamlit frontend
├── requirements.txt
├── Dockerfile              # (Optional) Docker support
├── start.sh                # Shell script to run both agent + frontend
└── README.md
```

---

## 🐳 Docker (Optional)

If you want to containerize and run it easily:

```bash
# Build the container
docker build -t auto-agent-app .

# Run the app
docker run -p 8501:8501 auto-agent-app
```

---

## 🌍 Future Improvements

- Add audio/text-to-speech support for voice input
- Deploy to Google Cloud Run or Streamlit Cloud
- Add fine-tuned demand forecasting using real data

---

## 🛡 License

MIT License. Feel free to fork and customize!
