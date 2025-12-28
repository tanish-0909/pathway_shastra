# Stocks Agent Framework

## Overview

This repository contains the Stocks Agent Framework, a multi-agent system designed for automated stock analysis. The system leverages various data sources including Zerodha (for market data), Google Search, and Twitter to provide comprehensive technical and fundamental analysis. It utilizes Pathway for real-time data processing and LangGraph for agent orchestration.

## Features

- **Real-time Technical Analysis**: computes indicators such as RSI, MACD, and Bollinger Bands on live data streams.
- **Fundamental Analysis**: Performs Discounted Cash Flow (DCF) valuation using financial data.
- **Sentiment Analysis**: Aggregates and analyzes sentiment from news and social media (Twitter).
- **Monte Carlo Simulations**: Runs risk assessment simulations.
- **Agent Orchestrator**: Intelligently routes user queries to the appropriate specialized agents.

## Prerequisites

- Python 3.10 or higher
- Linux environment (recommended)
- MongoDB instance (local or Atlas)
- Docker (optional, for containerized deployment)

## Installation

1.  **Clone the repository** (if not already done).

2.  **Set up the Virtual Environment**:
    
    Recreate the virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Install Language Models**:
    The system uses Spacy for NLP tasks. Ensure the model is downloaded:
    ```bash
    python -m spacy download en_core_web_sm
    ```

## Configuration

1.  **Environment Variables**:
    Create a `.env` file in the root directory. Refer to `.env.example` or ensure the following keys are set:
    - `ZERODHA_API_KEY`
    - `ZERODHA_ACCESS_TOKEN`
    - `OPENAI_API_KEY`
    - `MONGO_URI`
    - `GOOGLE_SEARCH_API_KEY`
    - `GOOGLE_CSE_ID`
    - `KAFKA_BOOTSTRAP_SERVERS` (if using Kafka)

2.  **Data Directories**:
    Ensure the `data` and `historical_data` directories exist and contain necessary configuration files like `UNIVERSE.json` and `Zerodha_Instrument_Tokens.csv`.

## Usage

### Running the Orchestrator / Server

To start the main API server:

```bash
python stocks_agent/server.py
```

The server will start on port 3000 by default.

### Running Data Pipelines

To run the Pathway-based indicator pipeline:

```bash
python pathway_indicators/pw_indicators3.py
```

### Running Kafka Consumers

To start the Kafka consumer for processing signals:

```bash
python kafka_listeners/kafka_consumer.py
```

## Directory Structure

- `stocks_agent/`: Main application code.
  - `agents/`: Specialized agent implementations (Technical, Fundamental, News, etc.).
  - `services/`: External service integrations (Zerodha, Twitter, Kafka).
  - `schemas/`: Pydantic models for data validation.
- `pathway_indicators/`: Real-time data processing pipelines using Pathway.
- `kafka_listeners/`: Consumers for handling asynchronous events.
- `data/`: Configuration and static data files.
- `venv/`: Python virtual environment.


