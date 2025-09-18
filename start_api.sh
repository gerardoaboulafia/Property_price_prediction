#!/bin/bash

# Startup script for Property Price Prediction API

echo "🏠 Starting Property Price Prediction API..."
echo "=================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Activating .venv..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Please create one with:"
        echo "   python -m venv .venv"
        echo "   source .venv/bin/activate"
        echo "   pip install -r requirements.txt"
        exit 1
    fi
fi

# Check if required model files exist
echo ""
echo "🔍 Checking required files..."

MODEL_FILE="Pipeline/models/xgb_pipeline2.pkl"
SUBTE_FILE="Pipeline/estaciones-de-subte copy.csv"
BARRIOS_FILE="Pipeline/barrios copy.csv"

if [ -f "$MODEL_FILE" ]; then
    echo "✅ Model file found: $MODEL_FILE"
else
    echo "❌ Model file missing: $MODEL_FILE"
    exit 1
fi

if [ -f "$SUBTE_FILE" ]; then
    echo "✅ Subway stations file found: $SUBTE_FILE"
else
    echo "❌ Subway stations file missing: $SUBTE_FILE"
    exit 1
fi

if [ -f "$BARRIOS_FILE" ]; then
    echo "✅ Neighborhoods file found: $BARRIOS_FILE"
else
    echo "❌ Neighborhoods file missing: $BARRIOS_FILE"
    exit 1
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "   API will be available at: http://localhost:8000"
echo "   Interactive docs at: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
