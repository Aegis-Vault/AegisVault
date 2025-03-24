#!/bin/bash

set -euo pipefail

MODEL="gpt-4"
NETWORK_NAME="attackathon-stacks.devnet"
LOG_FILE=".devnet_log.tmp"
DEBUG=false
SESSION_LOG=".openai_helper_log"

log() {
  echo -e "👉 $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

check_dependencies() {
  for cmd in curl jq clarinet; do
    if ! command -v "$cmd" &> /dev/null; then
      echo "❌ $cmd is not installed. Please install it and try again."
      exit 1
    fi
  done
}

check_env() {
  if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    echo "❌ OPENAI_API_KEY is not set. Export it and try again."
    exit 1
  fi
}

cleanup_network() {
  log "Cleaning up Docker network: $NETWORK_NAME"
  
  if docker network ls | grep -q "$NETWORK_NAME"; then
    log "Network exists. Inspecting attached containers..."
    
    CONTAINERS=$(docker network inspect "$NETWORK_NAME" -f '{{range .Containers}}{{.Name}} {{end}}')

    if [ -n "$CONTAINERS" ]; then
      log "Stopping containers: $CONTAINERS"
      for c in $CONTAINERS; do
        if docker ps -a --format '{{.Names}}' | grep -q "^$c$"; then
          docker stop "$c" || true
          docker rm "$c" || true
        else
          log "⚠️  Container $c not found. Skipping."
        fi
      done
    fi

    log "Removing network $NETWORK_NAME"
    docker network rm "$NETWORK_NAME"
  else
    log "✅ No conflicting Docker network found."
  fi
}

cleanup_cache() {
  log "Removing local devnet cache..."
  rm -rf ./.cache
}

run_clarinet() {
  log "Starting Clarinet devnet..."
  if ! clarinet devnet start 2> "$LOG_FILE"; then
    log "❌ Clarinet failed. Checking for errors..."
    handle_error
  fi
}

handle_error() {
  ERROR_MSG=$(<"$LOG_FILE")
  
  log "💡 Asking OpenAI for suggestions..."
  JSON_PAYLOAD=$(jq -n \
    --arg model "$MODEL" \
    --arg role_sys "system" \
    --arg content_sys "You are a DevOps expert helping troubleshoot issues with Stacks blockchain devnets, Docker, and Clarinet." \
    --arg role_user "user" \
    --arg content_user "Clarinet devnet failed with the following error:\n\n$ERROR_MSG\n\nPlease explain the issue and suggest how to fix it." \
    '{model: $model, messages: [{role: $role_sys, content: $content_sys}, {role: $role_user, content: $content_user}]}')

  RESPONSE=$(curl -s https://api.openai.com/v1/chat/completions \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD")

  SUGGESTION=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')

  if [[ -z "$SUGGESTION" ]]; then
    echo -e "\n⚠️ No suggestion received from OpenAI. Here's the raw response for debugging:\n$RESPONSE"
  else
    echo -e "\n🧠 OpenAI Suggestion:\n$SUGGESTION"
  fi

  if [[ "$DEBUG" == true ]]; then
    echo -e "\n🔍 Raw OpenAI response:\n$RESPONSE"
  fi

  # Log the session
  echo -e "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')\nPrompt: $JSON_PAYLOAD\nResponse: $RESPONSE\n" >> "$SESSION_LOG"

  # Auto-fix prompt
  read -p "🛠️  Do you want to auto-remove the Docker network now? [y/N] " choice
  if [[ "$choice" =~ ^[Yy]$ ]]; then
    cleanup_network
    cleanup_cache
    log "✅ Removed Docker network and cache."
    
    # Retry support
    read -p "🔄 Do you want to re-run Clarinet devnet start? [y/N] " retry_choice
    if [[ "$retry_choice" =~ ^[Yy]$ ]]; then
      run_clarinet
    fi
  fi
}

cleanup() {
  log "Cleaning up temporary files..."
  rm -f "$LOG_FILE"
}

trap cleanup EXIT

check_dependencies
check_env
run_clarinet