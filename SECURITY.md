# Security Policy

## 🛡️ Progetto Sentinel - Security Overview

Questo progetto implementa misure di sicurezza multi-livello attraverso l'iniziativa **Progetto Sentinel**, che copre sicurezza frontend, supply chain e pipeline CI/CD.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| current   | :white_check_mark: |

## 🔒 Security Measures Implemented

### 1. Frontend Security (Modulo 1)

#### Content Security Policy (CSP)
- **Implementato**: Plugin `vite-plugin-csp` nel build process
- **Protezione**: Prevenzione attacchi XSS limitando le fonti di contenuti eseguibili
- **Configurazione**: `frontend/vite.config.ts`
- **Policy attive**:
  - `default-src 'self'`: Solo risorse dallo stesso dominio
  - `script-src 'self'`: Solo script dal dominio
  - `style-src 'self' 'unsafe-inline'`: Stili sicuri (inline necessario per librerie UI)
  - `img-src 'self' data: https:`: Immagini locali e data URIs
  - `object-src 'none'`: Blocco completo di object/embed
  - `frame-ancestors 'none'`: Protezione da clickjacking

#### Input Sanitization (Future-Ready)
- **Documentazione**: `frontend/SECURITY_NOTES.md`
- **Libreria raccomandata**: DOMPurify
- **Applicazione**: Sanificazione di contenuti generati dall'utente prima del rendering

### 2. Supply Chain Security (Modulo 2)

#### Automated Dependency Scanning
- **Dependabot**: Configurato per npm, pip e GitHub Actions
  - File: `.github/dependabot.yml`
  - Scansioni settimanali automatiche
  - Pull Request automatiche per vulnerabilità
  - Raggruppamento intelligente degli update

#### Continuous Security Scanning
- **GitHub CodeQL**: Analisi statica avanzata del codice
  - Linguaggi: JavaScript/TypeScript e Python
  - Query: `security-extended` e `security-and-quality`
  - Esecuzione: Ad ogni push, PR e settimanalmente
  
- **npm audit**: Scansione vulnerabilità npm
  - Livello minimo: `moderate`
  - Esecuzione automatica nel workflow

- **Python Security**:
  - **Safety**: Check delle dipendenze Python per CVE note
  - **Bandit**: Linter di sicurezza per codice Python
  - Report artefatti conservati per 30 giorni

- **Trivy**: Scanner universale di vulnerabilità
  - Scansione filesystem completa
  - Severità: CRITICAL, HIGH, MEDIUM
  - Integrazione con GitHub Security tab (SARIF)

#### Reproducible Builds
- **pip-tools**: Build Python riproducibili
  - File sorgente: `requirements.in`
  - File lockato: `requirements.txt` (da generare con hash)
  - Documentazione: `docs/PIP_TOOLS_GUIDE.md`
  - Benefici: Versioni esatte, hash verification, protezione da tampering

### 3. Pipeline Validation (Modulo 3)

#### Pre-commit Hooks
- **Husky + lint-staged**: Validazione automatica pre-commit
  - Location: `frontend/.husky/pre-commit`
  - Esecuzione: Prettier su tutti i file staged
  - Configurazione: `frontend/package.json` (lint-staged)
  - Beneficio: Codice formattato e consistente, errori bloccati prima del commit

#### Branch Protection (Configurazione manuale richiesta)
- **Guida completa**: `docs/BRANCH_PROTECTION_GUIDE.md`
- **Status checks richiesti**:
  - `build-data`: Generazione dati e test Python
  - `build-and-deploy`: Build frontend Vite/Vue
  - `CodeQL Security Analysis`: JavaScript e Python
  - `NPM Security Audit`: Vulnerabilità npm
  - `Python Security Scan`: Safety + Bandit
  - `Trivy Vulnerability Scanner`: Scansione filesystem

## 🚨 Reporting a Vulnerability

### Come Segnalare

1. **NON aprire issue pubbliche** per vulnerabilità di sicurezza
2. Invia una segnalazione privata:
   - Via GitHub Security Advisories: [Create Security Advisory](https://github.com/fabriziosalmi/repos/security/advisories/new)
   - O via email a: fabrizio.salmi@gmail.com

### Cosa Includere

- Descrizione della vulnerabilità
- Passi per riprodurre il problema
- Versione/branch affetto
- Possibile impatto
- Suggerimenti per la mitigazione (se disponibili)

### Cosa Aspettarsi

- **Conferma entro**: 48 ore
- **Valutazione iniziale**: 7 giorni
- **Aggiornamenti**: Settimanali durante la risoluzione
- **Disclosure coordinato**: Patch prima della pubblicazione

### Severity Levels

| Livello | Descrizione | Tempo di risposta |
|---------|-------------|-------------------|
| 🔴 **Critical** | Esecuzione codice remoto, data breach | 24-48 ore |
| 🟠 **High** | Escalation privilegi, XSS stored | 1 settimana |
| 🟡 **Medium** | XSS reflected, CSRF | 2 settimane |
| 🟢 **Low** | Information disclosure limitata | 1 mese |

## 🔐 Security Best Practices per Contributor

### 1. Secrets Management
- **MAI** committare API keys, token o credenziali
- Usare GitHub Secrets per informazioni sensibili
- File `.env` devono essere in `.gitignore`

### 2. Dependencies
- Eseguire `npm audit` e `safety check` regolarmente
- Aggiornare dipendenze con vulnerabilità note immediatamente
- Verificare nuove dipendenze prima dell'aggiunta

### 3. Code Review
- Tutte le modifiche richiedono PR e review
- Focus su: input validation, authorization, data sanitization
- Non bypassare i pre-commit hooks

### 4. Testing
- Test di sicurezza devono passare prima del merge
- Non disabilitare scanner di sicurezza
- Verificare l'output dei security scan

## 📚 Security Documentation

- [Frontend Security Notes](frontend/SECURITY_NOTES.md)
- [Branch Protection Guide](docs/BRANCH_PROTECTION_GUIDE.md)
- [pip-tools Guide](docs/PIP_TOOLS_GUIDE.md)
- [Dependabot Config](.github/dependabot.yml)
- [Security Workflow](.github/workflows/security.yml)

## 🏆 Security Acknowledgments

Ringraziamenti a chi contribuisce alla sicurezza del progetto saranno elencati qui.

## 📊 Security Metrics

- **Last Security Audit**: Automated (continuous)
- **Dependencies Scanned**: npm + pip + GitHub Actions
- **SAST Tools**: CodeQL, Bandit
- **Vulnerability Scanner**: Trivy, npm audit, Safety
- **Pre-commit Validation**: ✅ Enabled

---

**Progetto Sentinel** - Sicurezza integrata in ogni fase del ciclo di sviluppo 🛡️
