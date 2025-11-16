#!/bin/bash

# 🛡️ Progetto Sentinel - Verification Script
# Verifica che tutte le componenti di sicurezza siano configurate correttamente

# Assicurati di essere nella directory corretta
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "🛡️  PROGETTO SENTINEL - VERIFICAZIONE SISTEMA"
echo "=============================================="
echo ""

ERRORS=0
WARNINGS=0

# Funzioni helper
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $2"
        return 0
    else
        echo "❌ $2 - File mancante: $1"
        ((ERRORS++))
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $2"
        return 0
    else
        echo "❌ $2 - Directory mancante: $1"
        ((ERRORS++))
        return 1
    fi
}

check_command() {
    if command -v "$1" &> /dev/null; then
        echo "✅ $2 disponibile"
        return 0
    else
        echo "⚠️  $2 non trovato (opzionale)"
        ((WARNINGS++))
        return 1
    fi
}

check_npm_package() {
    if grep -q "\"$1\"" frontend/package.json 2>/dev/null; then
        echo "✅ npm: $1 installato"
        return 0
    else
        echo "❌ npm: $1 NON installato"
        ((ERRORS++))
        return 1
    fi
}

echo "📦 MODULO 1: Frontend Security"
echo "-----------------------------------"
check_file "frontend/vite.config.ts" "CSP configurato in vite.config.ts"
check_npm_package "vite-plugin-csp"
check_file "frontend/SECURITY_NOTES.md" "Documentazione DOMPurify"
check_file "frontend/public/favicon.svg" "Favicon personalizzato"
check_npm_package "prettier"
echo ""

echo "🔒 MODULO 2: Supply Chain Security"
echo "-----------------------------------"
check_file ".github/dependabot.yml" "Dependabot configurato"
check_file ".github/workflows/security.yml" "Workflow di sicurezza"
check_file "requirements.in" "requirements.in (pip-tools)"
check_file "docs/PIP_TOOLS_GUIDE.md" "Documentazione pip-tools"

# Verifica presenza di sezioni nel workflow
if [ -f ".github/workflows/security.yml" ]; then
    if grep -q "codeql-analysis" .github/workflows/security.yml; then
        echo "✅ CodeQL configurato nel workflow"
    else
        echo "⚠️  CodeQL potrebbe non essere configurato"
        ((WARNINGS++))
    fi
    
    if grep -q "npm-audit" .github/workflows/security.yml; then
        echo "✅ npm audit configurato"
    else
        echo "⚠️  npm audit potrebbe non essere configurato"
        ((WARNINGS++))
    fi
    
    if grep -q "trivy" .github/workflows/security.yml; then
        echo "✅ Trivy scanner configurato"
    else
        echo "⚠️  Trivy scanner potrebbe non essere configurato"
        ((WARNINGS++))
    fi
fi
echo ""

echo "🔐 MODULO 3: Pipeline Validation"
echo "-----------------------------------"
check_dir "frontend/.husky" "Husky configurato"
check_file "frontend/.husky/pre-commit" "Pre-commit hook"
check_npm_package "husky"
check_npm_package "lint-staged"
check_file "frontend/.prettierrc" "Prettier configurato"
check_file "frontend/.prettierignore" "Prettier ignore"

# Verifica configurazione lint-staged in package.json
if grep -q "lint-staged" frontend/package.json 2>/dev/null; then
    echo "✅ lint-staged configurato in package.json"
else
    echo "⚠️  lint-staged potrebbe non essere configurato in package.json"
    ((WARNINGS++))
fi
echo ""

echo "📚 DOCUMENTAZIONE"
echo "-----------------------------------"
check_file "SECURITY.md" "SECURITY.md aggiornato"
check_file "docs/BRANCH_PROTECTION_GUIDE.md" "Guida Branch Protection"
check_file "docs/PROJECT_SENTINEL_SUMMARY.md" "Riepilogo Progetto Sentinel"
echo ""

echo "🎯 AZIONI MANUALI RICHIESTE"
echo "-----------------------------------"
echo "⚠️  Branch Protection: Configurare manualmente su GitHub"
echo "    👉 https://github.com/fabriziosalmi/repos/settings/branches"
echo ""
echo "⚠️  pip-tools: Eseguire 'pip-compile requirements.in --generate-hashes'"
echo "    👉 Vedi: docs/PIP_TOOLS_GUIDE.md"
echo ""

echo "=============================================="
echo "📊 RIEPILOGO VERIFICAZIONE"
echo "=============================================="
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ Tutti i componenti critici sono installati correttamente!"
else
    echo "❌ Trovati $ERRORS errori critici"
fi

if [ $WARNINGS -gt 0 ]; then
    echo "⚠️  Trovati $WARNINGS warning (componenti opzionali o da verificare manualmente)"
fi

echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "🎉 PROGETTO SENTINEL: COMPLETAMENTE OPERATIVO! 🛡️"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "✅ PROGETTO SENTINEL: OPERATIVO (con alcuni warning) 🛡️"
    exit 0
else
    echo "❌ PROGETTO SENTINEL: RICHIEDE ATTENZIONE"
    exit 1
fi
