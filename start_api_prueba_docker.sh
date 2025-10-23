#!/bin/bash

# Startup script for Property Price Prediction API (Docker version)

echo "🏠 Starting Property Price Prediction API..."
echo "=================================="

# Check if required model files exist
echo ""
echo "🔍 Checking required files..."

MODEL_FILE="Pipeline/models/model_api_test.pkl"
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
echo "   API will be available at: http://0.0.0.0:8000"
echo "   Interactive docs at: http://0.0.0.0:8000/docs"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000
