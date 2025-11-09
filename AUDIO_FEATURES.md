# 🎛️ Enhanced Audio Experience

## Drum'n'Bass / Dub Techno Background Loop

Il sistema audio è stato completamente rinnovato con un'esperienza **analogica, imprevedibile e wow** progettata per sorprendere nerd e artisti.

### 🎵 Caratteristiche Principali

#### 1. **Loop Drum'n'Bass (174 BPM)**
- Kick drum pattern dinamico (4/4 con variazioni)
- Snare su battute 2 e 4
- Hi-hat breakbeat con pattern imprevedibili (16th notes randomizzati)
- Bassline dub techno con progressione armonica (A1, C2, D2, E2)

#### 2. **Effetti Analogici**
- **Saturazione armonica**: Wave shaper per calore analogico
- **Vinyl crackle**: Texture di vinile sottile e continua
- **Dub delay**: Echo classico con feedback filtrato (dotted 8th note)
- **Tape wow**: Variazioni casuali di pitch su tutti i suoni
- **Lowpass filtering**: Filtri risonanti sulla bassline

#### 3. **Imprevedibilità & Glitch**
- **Random breakdowns** ogni 32-64 battute
- **Glitch effects** casuali ogni ~3 secondi:
  - Bitcrushing improvviso
  - Pitch bends imprevedibili  
  - Filter sweeps
- **Pattern variations**: Drum pattern che cambiano dinamicamente
- **Riser effects**: Build-up durante i breakdown

#### 4. **Sound Design Avanzato**
- Tutti gli effetti sonori passano attraverso catena analogica
- Detune casuale su ogni suono per carattere organico
- Multi-layer su effetti glitch
- Suoni connessi al dub delay per eco spaziali

### 🎚️ Parametri Audio

```javascript
Master Volume: 0.28 (ridotto per non disturbare)
Music Gain: 0.08 (background molto sottile)
Vinyl Crackle: 0.003 (texture leggera)
Dub Delay: 0.375s feedback, filtro @2.8kHz
Analog Warmth: 15 amount, 4x oversampling
```

### 🎼 Elementi Musicali

**Kick**: Sine wave 150Hz → 40Hz in 0.5s  
**Snare**: White noise con highpass @1kHz  
**Hi-hat**: White noise con highpass @7kHz (open/closed random)  
**Bass**: Sawtooth wave con lowpass resonante (Q=8)

### 🎭 Carattere Sonoro

L'audio è progettato per essere:
- **Analogico**: Saturazione, crackle, detuning
- **Imprevedibile**: Glitch, breakdowns, variazioni random
- **Spaziale**: Dub delay per profondità
- **Organico**: Nessun loop identico si ripete mai
- **Sorprendente**: Effetti che emergono in momenti inaspettati

### 🔊 Controlli

- **Toggle audio**: Click sull'icona speaker in navbar
- **Auto-start**: Audio parte automaticamente alla prima interazione
- **Console logs**: Messaggi per debugging (breakdown, glitch, etc.)

### 🎨 Integrazione Visuale

Gli effetti audio sono sincronizzati con:
- Police flash effects (con dub delay!)
- Avatar animations (glitch, spin, strobe)
- Cursor interactions
- Scroll velocity triggers

### 🚀 Performance

- Volume ottimizzato per non essere invasivo
- Effetti CPU-efficient (buffer pre-calcolati)
- Garbage collection minimizzata
- Graceful degradation su errori

---

**Per artisti e nerd**: L'esperienza è progettata per essere scoperta progressivamente. Ogni sessione sarà diversa grazie alla casualità incorporata nel sistema. Enjoy the ride! 🎧✨
