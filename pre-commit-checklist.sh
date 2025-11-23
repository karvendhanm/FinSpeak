#!/bin/bash

echo "🔒 FinSpeak Pre-Commit Security Checklist"
echo "=========================================="
echo ""

# Check for .env files
echo "1. Checking for .env files..."
if git status --porcelain | grep -q "\.env$"; then
    echo "   ❌ DANGER: .env file detected in staging!"
    echo "   Run: git rm --cached backend/.env"
    exit 1
else
    echo "   ✅ No .env files in staging"
fi

# Check for database files
echo "2. Checking for database files..."
if git status --porcelain | grep -q "\.db$"; then
    echo "   ❌ DANGER: Database file detected in staging!"
    echo "   Run: git rm --cached backend/*.db"
    exit 1
else
    echo "   ✅ No database files in staging"
fi

# Check for AWS credentials in files
echo "3. Checking for AWS credentials..."
if git diff --cached | grep -qi "AWS_ACCESS_KEY_ID\|AWS_SECRET_ACCESS_KEY"; then
    echo "   ❌ DANGER: AWS credentials detected in staged changes!"
    exit 1
else
    echo "   ✅ No AWS credentials detected"
fi

# Check for __pycache__
echo "4. Checking for Python cache..."
if git status --porcelain | grep -q "__pycache__"; then
    echo "   ⚠️  WARNING: __pycache__ detected"
    echo "   Run: git rm -r --cached backend/__pycache__"
else
    echo "   ✅ No Python cache in staging"
fi

# Check for node_modules
echo "5. Checking for node_modules..."
if git status --porcelain | grep -q "node_modules"; then
    echo "   ⚠️  WARNING: node_modules detected"
    echo "   Run: git rm -r --cached finspeak-frontend/node_modules"
else
    echo "   ✅ No node_modules in staging"
fi

echo ""
echo "=========================================="
echo "✅ All security checks passed!"
echo "Safe to commit and push to GitHub"
echo "=========================================="
