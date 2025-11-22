#!/bin/bash

echo "🚀 FinSpeak Setup & Start"
echo "=========================="

# Check if database exists and is not empty
if [ ! -f finspeak.db ] || [ ! -s finspeak.db ]; then
    echo ""
    echo "📊 Initializing database..."
    python init_db.py
    echo ""
fi

echo "✅ Database ready!"
echo ""
echo "🌐 Starting server..."
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo ""

python server.py
