# 🎨 Guida Personalizzazione

## Come Modificare la Nuova Pagina

### 🎨 Cambiare i Colori

Nel file `index.html`, cerca la sezione `:root` (circa linea 24):

```css
:root {
    --neon-cyan: #00ffff;      /* Cambia per highlight diverso */
    --neon-magenta: #ff00ff;   /* Cambia per accenti diversi */
    --neon-yellow: #ffff00;    /* Cambia per glow diverso */
    --deep-space: #0a0a0f;     /* Background principale */
    --cosmic-purple: #1a0a2e;  /* Background gradient */
    --electric-blue: #0066ff;  /* Colore bottoni */
    --plasma-pink: #ff0080;    /* Effetti speciali */
}
```

#### Esempi di Palette Alternative

**Palette Oceano:**
```css
--neon-cyan: #00d4ff;
--neon-magenta: #0088ff;
--neon-yellow: #00ffaa;
--deep-space: #0a1520;
--cosmic-purple: #0a1f3e;
```

**Palette Fuoco:**
```css
--neon-cyan: #ff6600;
--neon-magenta: #ff0066;
--neon-yellow: #ffaa00;
--deep-space: #1a0a00;
--cosmic-purple: #2e0a0a;
```

**Palette Matrix:**
```css
--neon-cyan: #00ff00;
--neon-magenta: #00cc00;
--neon-yellow: #00ff88;
--deep-space: #000000;
--cosmic-purple: #001100;
```

---

### 🎵 Modificare l'Audio

#### Cambiare BPM
Cerca `const bpm = 174` (circa linea 629) e modifica:

```javascript
const bpm = 140;  // House
const bpm = 160;  // Techno
const bpm = 174;  // Drum'n'Bass (default)
const bpm = 180;  // Hardcore
```

#### Cambiare Volume
Cerca `musicGain.gain.value` (circa linea 616):

```javascript
musicGain.gain.value = 0.05;  // Più basso
musicGain.gain.value = 0.08;  // Default
musicGain.gain.value = 0.12;  // Più alto
```

#### Disabilitare Glitch Effects
Commenta la funzione (circa linea 743):

```javascript
// if (isMusicEnabled) {
//     startGlitchEffects();
// }
```

#### Cambiare Bassline
Modifica le frequenze (circa linea 720):

```javascript
const frequencies = [55, 65, 73, 82];  // Default (A1, C2, D2, E2)
const frequencies = [110, 130, 146, 164];  // Un'ottava sopra
const frequencies = [41, 49, 55, 61];  // Un'ottava sotto (più profondo)
```

---

### ⭐ Modificare le Stelle

#### Numero di Stelle
Cerca `for (let i = 0; i < 200` (circa linea 825):

```javascript
for (let i = 0; i < 100; i++) {  // Meno stelle
for (let i = 0; i < 200; i++) {  // Default
for (let i = 0; i < 500; i++) {  // Più stelle
```

#### Velocità Twinkle
Nel CSS, cerca `animation: twinkle 3s` (circa linea 53):

```css
animation: twinkle 1s infinite;   /* Veloce */
animation: twinkle 3s infinite;   /* Default */
animation: twinkle 6s infinite;   /* Lento */
```

---

### 🖱️ Modificare il Cursore

#### Dimensione
Cerca `.cursor` nel CSS (circa linea 35):

```css
.cursor {
    width: 30px;   /* Più grande */
    height: 30px;
    /* ... */
}
```

#### Colore
```css
.cursor {
    border: 2px solid var(--neon-magenta);  /* Magenta invece di cyan */
}
```

#### Disabilitare Trail
Commenta nel JavaScript (circa linea 816):

```javascript
// Trail effect
// if (Math.random() > 0.9) {
//     const trail = document.createElement('div');
//     // ...
// }
```

---

### 📊 Modificare Stats Display

#### Mostrare Più/Meno Repositories
Cerca `.slice(0, 12)` (circa linea 858):

```javascript
.slice(0, 6)   // Top 6
.slice(0, 12)  // Top 12 (default)
.slice(0, 20)  // Top 20
```

#### Cambiare Ordinamento
```javascript
// Per stars (default)
const topRepos = repos.sort((a, b) => b.stars - a.stars)

// Per forks
const topRepos = repos.sort((a, b) => b.forks - a.forks)

// Per commits
const topRepos = repos.sort((a, b) => b.commits - a.commits)

// Per data aggiornamento (più recenti)
// Richiede conversione della data
```

---

### 🎨 Animazioni

#### Velocità Float Avatar
Cerca `animation: float 6s` (circa linea 167):

```css
animation: float 3s ease-in-out infinite;   /* Veloce */
animation: float 6s ease-in-out infinite;   /* Default */
animation: float 12s ease-in-out infinite;  /* Lento */
```

#### Velocità Glow Text
Cerca `animation: glow 3s` (circa linea 211):

```css
animation: glow 1s ease-in-out infinite;   /* Veloce */
animation: glow 3s ease-in-out infinite;   /* Default */
animation: glow 6s ease-in-out infinite;   /* Lento */
```

---

### 📱 Responsive Breakpoints

Modifica i breakpoint (circa linea 480):

```css
@media (max-width: 480px) {  /* Smartphone piccoli */
@media (max-width: 768px) {  /* Tablet (default) */
@media (max-width: 1024px) { /* Desktop piccolo */
```

---

### 🎯 Personalizzare il Testo

#### Tagline
Cerca `<p class="tagline">` (circa linea 568):

```html
<p class="tagline">code, sound, creativity</p>
<!-- Cambia in: -->
<p class="tagline">Il tuo testo qui</p>
```

#### Titoli Sezioni
```html
<h2 class="section-title">GitHub Statistics</h2>
<!-- Cambia in: -->
<h2 class="section-title">Le Mie Stats</h2>
```

---

### 🚀 Performance Tweaks

#### Ridurre Blur Effect
Troppo blur può rallentare su dispositivi lenti:

```css
backdrop-filter: blur(10px);  /* Ridurre a 5px */
backdrop-filter: blur(20px);  /* Ridurre a 10px */
```

#### Disabilitare Glassmorphism
Commenta tutte le linee `backdrop-filter` nel CSS.

#### Ridurre Ombre
```css
box-shadow: 0 10px 30px rgba(0, 255, 255, 0.2);
/* Ridurre a: */
box-shadow: 0 5px 15px rgba(0, 255, 255, 0.1);
```

---

### 🎨 Aggiungere Nuovi Effetti

#### Aggiungere Particelle
Dopo le stelle, puoi aggiungere altri elementi animati:

```javascript
// Esempio: Particelle fluttuanti
for (let i = 0; i < 50; i++) {
    const particle = document.createElement('div');
    particle.style.cssText = `
        position: fixed;
        width: 3px;
        height: 3px;
        background: var(--neon-cyan);
        border-radius: 50%;
        top: ${Math.random() * 100}%;
        left: ${Math.random() * 100}%;
        animation: float ${3 + Math.random() * 4}s infinite;
    `;
    document.body.appendChild(particle);
}
```

---

### 📝 Tips & Tricks

#### 1. Test Locale
Apri `index.html` direttamente nel browser per testare modifiche.

#### 2. Browser DevTools
Usa F12 per modificare CSS in tempo reale.

#### 3. Backup
Fai sempre backup prima di modifiche importanti:
```bash
cp index.html index.html.backup
```

#### 4. Validazione
Usa [W3C Validator](https://validator.w3.org/) per verificare HTML.

#### 5. Audio Testing
Console del browser mostra log audio utili.

#### 6. Mobile Testing
Usa DevTools > Toggle Device Toolbar per testare responsive.

---

### 🐛 Troubleshooting

#### Audio non parte
- Controlla console browser per errori
- Alcuni browser richiedono interazione utente prima
- Verifica che AudioContext sia supportato

#### Cursore non appare
- Potrebbe essere `cursor: auto` in CSS
- Verifica che JavaScript sia abilitato

#### Stelle non animate
- Controlla performance del dispositivo
- Riduci numero stelle se troppo lento

#### Layout rotto su mobile
- Verifica breakpoint CSS
- Controlla overflow-x su body

---

### 🎨 Risorse

- [CSS Gradient Generator](https://cssgradient.io/)
- [Color Picker](https://colorpicker.me/)
- [Google Fonts](https://fonts.google.com/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [Web Audio API Docs](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

---

**Buona personalizzazione! 🚀✨**
