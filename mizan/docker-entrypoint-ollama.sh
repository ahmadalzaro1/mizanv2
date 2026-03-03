#!/bin/sh
set -e

MODEL=${OLLAMA_MODEL:-qwen3.5:9b}

# Start ollama server in background
ollama serve &
SERVER_PID=$!

# Wait for ollama to be ready (up to 60s)
MAX_RETRIES=30
SLEEP_TIME=2
i=0
until wget -qO- http://localhost:11434/api/tags > /dev/null 2>&1; do
  i=$((i + 1))
  if [ $i -ge $MAX_RETRIES ]; then
    echo "Ollama did not start in time"
    exit 1
  fi
  sleep $SLEEP_TIME
done

echo "Ollama ready. Pulling model: $MODEL"
ollama pull "$MODEL"

# Kill background server
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true

# Launch production server in foreground
exec ollama serve
