# 🛡️ Branch Protection Guide - Progetto Sentinel

## Configurazione Branch Protection Rules per `main`

Questa guida ti mostra come configurare le **branch protection rules** per rendere il branch `main` inviolabile, garantendo che tutto il codice passi attraverso validazioni rigorose.

## Passi per la Configurazione

### 1. Accedi alle Impostazioni della Repository

1. Vai alla tua repository su GitHub: `https://github.com/fabriziosalmi/repos`
2. Clicca su **Settings** (in alto a destra)
3. Nel menu laterale sinistro, seleziona **Branches** sotto la sezione "Code and automation"

### 2. Aggiungi una Branch Protection Rule

1. Clicca su **Add branch protection rule**
2. Nel campo **Branch name pattern**, inserisci: `main`

### 3. Configura le Regole di Protezione

Abilita le seguenti opzioni (✅ = consigliato):

#### ✅ Require a pull request before merging
- **Cosa fa**: Impedisce il push diretto su `main`, richiede PR
- **Impostazioni consigliate**:
  - ✅ Require approvals: **1** (o più per team più grandi)
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (se hai un file CODEOWNERS)

#### ✅ Require status checks to pass before merging
- **Cosa fa**: Il cuore della validazione automatica
- **Impostazioni**:
  - ✅ Require branches to be up to date before merging
  - **Seleziona i seguenti status checks** (devono corrispondere ai job nei tuoi workflow):
    - `build-data` (dal workflow deploy.yml)
    - `build-and-deploy` (dal workflow deploy.yml)
    - `CodeQL Security Analysis (javascript)` (dal workflow security.yml)
    - `CodeQL Security Analysis (python)` (dal workflow security.yml)
    - `NPM Security Audit` (dal workflow security.yml)
    - `Python Security Scan` (dal workflow security.yml)
    - `Trivy Vulnerability Scanner` (dal workflow security.yml)

> **Nota**: I status checks appaiono solo dopo che il workflow è stato eseguito almeno una volta. Crea una PR di test per vederli apparire.

#### ✅ Require conversation resolution before merging
- **Cosa fa**: Tutti i commenti nella PR devono essere risolti prima del merge
- **Beneficio**: Assicura che tutte le questioni sollevate vengano affrontate

#### ✅ Require linear history
- **Cosa fa**: Richiede una cronologia lineare (no merge commits)
- **Beneficio**: Mantiene la cronologia Git pulita e leggibile
- **Alternativa**: Usa "Squash and merge" come metodo di merge predefinito

#### ✅ Include administrators
- **Cosa fa**: Applica le regole anche agli amministratori
- **Beneficio**: Nessuno è sopra la legge, neanche tu

#### ⚠️ Opzionale: Do not allow bypassing the above settings
- **Cosa fa**: Impedisce completamente il bypass delle regole
- **Quando usarlo**: Per progetti critici in produzione
- **Attenzione**: Potrebbe bloccarti in caso di emergenze (usa con cautela)

#### ✅ Require deployments to succeed before merging (Opzionale)
- Se hai deployment automatici configurati

### 4. Altre Impostazioni Consigliate

#### Lock branch
- ❌ Non abilitare (blocca completamente le modifiche)

#### Allow force pushes
- ❌ **Disable** (mai permettere force push su main)

#### Allow deletions
- ❌ **Disable** (previene la cancellazione accidentale di main)

### 5. Salva le Modifiche

Clicca su **Create** o **Save changes** in fondo alla pagina.

## 🎯 Risultato Finale

Una volta configurato, la tua repository avrà:

- ✅ **Impossibile** fare push diretto su `main`
- ✅ **Obbligatorio** passare da Pull Request
- ✅ **Obbligatorio** superare tutti i test di sicurezza
- ✅ **Obbligatorio** superare build e validazioni
- ✅ **Obbligatorio** risolvere tutti i commenti di review
- ✅ **Protezione** contro force push e cancellazioni
- ✅ **Cronologia** pulita e lineare

## 📋 Workflow Tipico

1. Sviluppatore crea un branch: `git checkout -b feature/my-feature`
2. Sviluppatore fa commit (pre-commit hooks eseguono lint-staged automaticamente)
3. Sviluppatore pusha: `git push origin feature/my-feature`
4. Sviluppatore crea una Pull Request su GitHub
5. GitHub Actions esegue automaticamente:
   - Build del frontend
   - Generazione dati Python
   - Scansioni di sicurezza (CodeQL, npm audit, Trivy)
   - Tutti i test
6. Se **TUTTO** passa ✅, la PR può essere approvata
7. Dopo approvazione, merge su `main` (con squash consigliato)
8. Il codice su `main` è **garantito** di alta qualità

## 🔧 Troubleshooting

### "Status checks non appaiono nella lista"
- I status checks appaiono solo dopo che il workflow è stato eseguito almeno una volta
- Crea una PR di test per far apparire i check

### "Non riesco a fare merge anche se tutto è verde"
- Verifica che tutti i check richiesti siano presenti e passati
- Controlla che tutti i commenti siano risolti
- Assicurati che il branch sia aggiornato con `main`

### "Ho bisogno di fare un hotfix urgente"
- Opzione 1: Crea una PR rapida che passi tutti i check (preferito)
- Opzione 2: Disabilita temporaneamente le regole (non consigliato)
- Opzione 3: Usa "Allow bypass" per amministratori (solo in emergenze)

## 📚 Best Practices Aggiuntive

1. **Squash and merge**: Mantieni la cronologia di main pulita
2. **Delete branch after merge**: Pulisci automaticamente i branch mergiati
3. **Auto-merge**: Abilita l'auto-merge quando tutti i check passano
4. **CODEOWNERS**: Definisci chi deve approvare quali file
5. **Required reviews**: Aumenta a 2+ per progetti critici

## 🔗 Risorse

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
- [Code Owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

---

**Progetto Sentinel - Fortificazione Completata** 🛡️
