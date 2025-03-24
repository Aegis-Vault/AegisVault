#!/bin/bash
set -e

echo "📦 Building Clarity contracts..."
clarinet check

echo "🚀 Deploying Clarity contracts to devnet..."
clarinet integrate

echo "🧪 Running tests with Vitest..."
npx vitest run