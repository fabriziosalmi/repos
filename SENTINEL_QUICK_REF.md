# 🛡️ Progetto Sentinel - Quick Reference

## ✅ Verifica Rapida Stato Sistema

```bash
./verify_sentinel.sh
```

## 🚀 Comandi Essenziali

### Frontend Development
```bash
cd frontend
npm install          # Installa dipendenze
npm run dev          # Dev server
npm run build        # Build produzione
npm run format       # Formatta codice manualmente
```

### Pre-commit (Automatico)
I pre-commit hooks si attivano automaticamente ad ogni `git commit`:
- Prettier formatta automaticamente i file staged
- Se ci sono errori, il commit viene bloccato

### Python Development
```bash
# Installazione dipendenze (current)
pip install -r requirements.txt

# Con pip-tools (recommended)
pip install pip-tools
pip-compile requirements.in --generate-hashes
pip-sync requirements.txt
```

## 🔒 Security Scans

### Locale (Manuale)
```bash
# Frontend
cd frontend
npm audit
npm audit fix

# Python
pip install safety bandit
safety check
bandit -r . -f json
```

### Automatico (CI/CD)
- Ogni push/PR esegue: CodeQL, npm audit, Safety, Bandit, Trivy
- Risultati visibili in: **Security** tab su GitHub
- Dependabot: Crea PR automatiche per vulnerabilità

## 📋 Workflow Contribuzione

```bash
# 1. Crea branch
git checkout -b feature/my-feature

# 2. Sviluppa
# ... codice ...

# 3. Commit (pre-commit hooks si attivano automaticamente)
git add .
git commit -m "feat: my feature"

# 4. Push
git push origin feature/my-feature

# 5. Crea PR su GitHub
# 6. Attendi che tutti i check passino ✅
# 7. Richiedi review
# 8. Merge su main (solo dopo approval + tutti i check verdi)
```

## 🎯 Status Checks Richiesti per Merge

| Check | Cosa Verifica |
|-------|---------------|
| build-data | Generazione dati Python + test pytest |
| build-and-deploy | Build frontend Vite/Vue |
| CodeQL (JavaScript) | Vulnerabilità sicurezza JS/TS |
| CodeQL (Python) | Vulnerabilità sicurezza Python |
| npm audit | Vulnerabilità dipendenze npm |
| Python Security | Safety + Bandit scan |
| Trivy | Scanner vulnerabilità filesystem |

## 📁 File di Configurazione Chiave

```
.github/
├── dependabot.yml          # Auto-updates dipendenze
└── workflows/
    ├── deploy.yml          # Build & deploy
    └── security.yml        # Security scans

frontend/
├── .husky/
│   └── pre-commit          # Hook pre-commit
├── .prettierrc             # Config Prettier
├── vite.config.ts          # Config Vite + CSP
└── package.json            # Dipendenze + scripts

SECURITY.md                 # Policy sicurezza
requirements.in             # Dipendenze Python (source)
requirements.txt            # Dipendenze Python (locked)
```

## 🆘 Troubleshooting

### "Pre-commit hook non funziona"
```bash
cd frontend
npx husky install
chmod +x .husky/pre-commit
```

### "Status checks non appaiono in PR"
- I check appaiono solo dopo la prima esecuzione
- Crea una PR di test per farli apparire
- Poi configura branch protection

### "Build fallisce con errore CSP"
- Verifica `frontend/vite.config.ts`
- La sintassi corretta è: `'default-src': ['self']`
- Non `["'self'"]`

### "Dependabot non crea PR"
- Verifica `.github/dependabot.yml` esista
- I check partono il lunedì successivo alla configurazione
- Controlla tab "Insights" > "Dependency graph" > "Dependabot"

## 📚 Documentazione Completa

- **Panoramica**: `docs/PROJECT_SENTINEL_SUMMARY.md`
- **Sicurezza**: `SECURITY.md`
- **Branch Protection**: `docs/BRANCH_PROTECTION_GUIDE.md`
- **pip-tools**: `docs/PIP_TOOLS_GUIDE.md`
- **Frontend Security**: `frontend/SECURITY_NOTES.md`

## 🏆 Best Practices

✅ **DO**:
- Committare spesso, il pre-commit ti protegge
- Creare PR piccole e focalizzate
- Risolvere i security alerts appena appaiono
- Aggiornare le dipendenze regolarmente
- Testare in locale prima di pushare

❌ **DON'T**:
- Mai fare push diretto su `main`
- Mai disabilitare i security checks
- Mai committare secrets/API keys
- Mai bypassare i pre-commit hooks
- Mai ignorare i security warnings

---

**Tutto pronto!** Il sistema è completamente operativo 🛡️
