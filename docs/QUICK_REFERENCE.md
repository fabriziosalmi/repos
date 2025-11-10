# ⚡ Quick Reference - Portfolio Cyberpunk

## 🎮 CONTROLS

### Desktop
```
MOUSE               → Custom cursor with magnetic effect
MOUSE NEAR CARDS    → Dynamic spotlight (blur/grayscale others)
                      < 300px = FOCUS (bright, lifted)
                      300-600px = NEAR (slight blur)
                      > 600px = DIMMED (heavy blur, grayscale)
CLICK               → Ripple waves
SHIFT + DRAG        → Draw gestures (straight = trail, curve = explosion)
HOVER BUTTONS       → Cursor scales 1.5x, turns magenta
SCROLL              → Parallax effects, progress bar
SPEAKER ICON        → Toggle audio (DnB 174 BPM)
```

### Mobile/Touch
```
TAP                 → Normal click
2-FINGER SWIPE      → Draw gestures
SCROLL              → Parallax effects
```

### Easter Eggs
```
↑↑↓↓←→←→BA         → Matrix rain (5s)
TRIPLE CLICK        → Color inversion (2s)
SHIFT (hold)        → Gesture mode indicator
```

---

## 🎨 VISUAL LAYERS

```
┌─────────────────────────────────────┐
│ Layer 7: Gesture Indicator (10001) │  ← Shift key feedback
├─────────────────────────────────────┤
│ Layer 6: Custom Cursor (9999)      │  ← Magnetic, follows mouse
├─────────────────────────────────────┤
│ Layer 5: Gesture Canvas (5)        │  ← Shift+Drag to draw
├─────────────────────────────────────┤
│ Layer 4: Audio Visualizer (1)      │  ← Circular spectrum
├─────────────────────────────────────┤
│ Layer 3: Particle Canvas (0)       │  ← Flow field physics
├─────────────────────────────────────┤
│ Layer 2: WebGL Canvas (0)          │  ← Cyberpunk shaders
├─────────────────────────────────────┤
│ Layer 1: Content (1-1000)          │  ← Cards, buttons, text
├─────────────────────────────────────┤
│ Layer 0: Stars Background (0)      │  ← Twinkling stars
└─────────────────────────────────────┘
```

**Pointer Events**:
- ✅ Content: `auto` (always clickable)
- ❌ Stars: `none` (not clickable)
- ❌ WebGL: `none` (not clickable)
- ❌ Particles: `none` (not clickable)
- ❌ Audio Viz: `none` (not clickable)
- ⚡ Gesture: `none` → `auto` (when Shift pressed)
- ❌ Cursor: `none` (not clickable)

---

## 🚀 LOADING SEQUENCE

```
0ms     → HTML loads, critical CSS inline
100ms   → Stars appear, custom cursor activates
500ms   → Magnetic cursor registers elements
1s      → Ambient effects start (aurora, meteors)
2s      → Scroll indicator, progress bar ready
5s      → Advanced effects trigger (or on first interaction)
6s      → WebGL shaders fade in (desktop only)
7s      → Particle system activates
8s      → Audio visualizer ready (needs audio ON)
9s      → Gesture system ready
```

---

## ⚡ PERFORMANCE MODES

### Desktop (4+ cores)
```
✅ WebGL Shaders     @ 30fps
✅ Particles (500)   @ 60fps
✅ Audio Viz         @ 60fps
✅ Gesture System    @ 60fps
✅ All Effects       Enabled
```

### Mobile / Low-End
```
❌ WebGL Shaders     Disabled
✅ Particles (200)   @ 30-60fps
✅ Audio Viz         @ 30-60fps
✅ Gesture System    @ 30-60fps
⚡ Effects           Reduced
```

### FPS < 30 (Auto-Adaptive)
```
❌ WebGL Shaders     Auto-disabled
✅ Other Effects     Continue
🔄 Recovery          Re-enables if FPS improves
```

---

## 🎵 AUDIO SYSTEM

### Generative DnB (174 BPM)
```
Kick        → Beats 1, 3 (sine wave, 150→40Hz)
Snare       → Beats 2, 4 (noise, highpass 1kHz)
Hi-Hat      → Every beat (noise, 7kHz)
Bass        → 4-note: A(55), B(65), C#(73), D(82)
Delay       → 375ms, filtered feedback
Glitch      → Random every ~3s
Ambience    → Vinyl crackle (3kHz highpass)
```

### Web Audio Chain
```
[Oscillator/Noise]
    ↓
[Filter (BiquadFilter)]
    ↓
[Gain Node]
    ↓
[Delay (375ms)]
    ↓
[Master Gain (25%)]
    ↓
[Analyser (FFT 512)]
    ↓
[Destination (Speakers)]
```

---

## 🎨 COLOR PALETTE

```css
--neon-cyan:      #00ffff  ■
--neon-magenta:   #ff00ff  ■
--neon-yellow:    #ffff00  ■
--deep-space:     #0a0a0f  ■
--cosmic-purple:  #1a0a2e  ■
--electric-blue:  #0066ff  ■
--plasma-pink:    #ff0080  ■
```

---

## 🔧 DEBUGGING

### Console Commands

**Check Active Effects**:
```javascript
console.log({
  webgl: webglActive,
  particles: particlesActive,
  audioViz: audioVizActive,
  gestures: gesturesActive
});
```

**Force Enable Gestures**:
```javascript
document.getElementById('gestureCanvas').style.pointerEvents = 'auto';
document.getElementById('gestureCanvas').style.opacity = '0.3';
```

**Check FPS**:
```javascript
let frames = 0;
let lastTime = performance.now();
requestAnimationFrame(function countFPS() {
  frames++;
  const now = performance.now();
  if(now - lastTime > 1000) {
    console.log('FPS:', frames);
    frames = 0;
    lastTime = now;
  }
  requestAnimationFrame(countFPS);
});
```

**List Canvas Layers**:
```javascript
[...document.querySelectorAll('canvas')].map(c => ({
  id: c.id,
  zIndex: c.style.zIndex,
  pointerEvents: c.style.pointerEvents,
  opacity: c.style.opacity
}));
```

**Test Clickability**:
```javascript
document.addEventListener('click', e => {
  console.log('Clicked:', e.target.tagName, e.target.className);
});
```

---

## 🐛 TROUBLESHOOTING

### Issue: Cards not clickable
**Fix**: Hold Shift → Does indicator appear? If yes, gesture canvas working. If no clicks work, check z-index.
```javascript
// Check what's blocking
document.elementFromPoint(500, 500); // Test at center
```

### Issue: Cursor not visible
**Fix**: Check if `html{cursor:none}` is active
```javascript
document.documentElement.style.cursor = 'default'; // Test
```

### Issue: Gesture not working
**Fix**: Press Shift → See indicator → Click and drag
```javascript
// Force enable
const canvas = document.getElementById('gestureCanvas');
canvas.style.pointerEvents = 'auto';
canvas.style.opacity = '0.3';
```

### Issue: Low FPS
**Fix**: Check WebGL status
```javascript
// Disable WebGL manually
webglActive = false;
document.getElementById('webglCanvas').style.opacity = '0';
```

### Issue: Audio not playing
**Fix**: User interaction required
```javascript
// Check audio context
console.log(window.aC?.state); // Should be "running"
```

---

## 📊 HOTKEYS SUMMARY

| Key Combo | Action | Desktop | Mobile |
|-----------|--------|---------|--------|
| Click | Normal click | ✅ | ✅ |
| Shift+Drag | Gesture draw | ✅ | ❌ |
| ↑↑↓↓←→←→BA | Matrix rain | ✅ | ❌ |
| 3× Click | Color invert | ✅ | ✅ |
| 2-Finger Drag | Gesture draw | ❌ | ✅ |

---

## 🎯 FEATURE CHECKLIST

**Core Functionality**:
- [x] Page loads < 2s
- [x] All links/buttons clickable
- [x] Smooth scroll
- [x] Responsive design

**Visual Effects**:
- [x] Custom cursor
- [x] Magnetic attraction
- [x] Parallax scroll
- [x] Click ripples
- [x] WebGL shaders (desktop)
- [x] Particle system
- [x] Audio visualizer

**Interactions**:
- [x] Gesture drawing (Shift)
- [x] Easter eggs (Konami, Triple-click)
- [x] Audio toggle
- [x] Smooth animations

**Performance**:
- [x] 60fps target
- [x] Lazy loading
- [x] Object pooling
- [x] Auto-optimization
- [x] Mobile adaptive

---

## 📱 MOBILE-SPECIFIC

### Touch Gestures
```
1 FINGER    → Tap, scroll, normal actions
2 FINGERS   → Gesture drawing
PINCH       → Browser zoom (default)
```

### Optimizations
```
✓ Reduced particle count (100 vs 500)
✓ No WebGL shaders
✓ Simplified animations
✓ Touch event optimization
✓ Viewport meta tag
```

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Test locally (open index.html)
- [ ] Test on mobile (2-finger gestures)
- [ ] Verify all clicks work
- [ ] Enable audio, check visualizer
- [ ] Try easter eggs (Konami, triple-click)
- [ ] Check FPS (should be 55-60)
- [ ] Test Shift+Drag gestures
- [ ] Verify indicator appears
- [ ] Check Lighthouse score (95+)
- [ ] Push to GitHub
- [ ] Verify on GitHub Pages
- [ ] Test on real devices

---

## 📞 SUPPORT

**Files**:
- `index.html` - Main application
- `FEATURES.md` - Feature documentation
- `TEST_GUIDE.md` - Testing instructions
- `CHANGELOG.md` - Version history
- `QUICK_REFERENCE.md` - This file

**Resources**:
- GitHub: https://github.com/fabriziosalmi
- Pages: https://fabriziosalmi.github.io

---

**Version**: 2.0.0
**Last Updated**: 2025-11-10
**Status**: ✅ Production Ready
