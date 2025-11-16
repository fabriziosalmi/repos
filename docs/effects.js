/**
 * GitHub Stats Dashboard - Advanced Visual Effects Module
 * Adds interactive particles, parallax, and intelligent UI enhancements
 * @version 4.0.0
 */

class DashboardEffects {
    constructor() {
        this.particles = [];
        this.mouse = { x: 0, y: 0 };
        this.canvas = null;
        this.ctx = null;
        this.animationId = null;
        this.audioContext = null;
        this.sounds = {};
        this.settings = {
            particlesEnabled: true,
            parallaxEnabled: true,
            glowEnabled: true,
            tooltipsEnabled: true,
            focusModeEnabled: true,
            soundEnabled: true,
            soundVolume: 0.15 // Very subtle
        };
        
        this.init();
    }

    init() {
        this.createParticleCanvas();
        this.initAudioSystem();
        this.initEventListeners();
        this.initParallaxEffect();
        this.initCardHoverEffects();
        this.initSmartTooltips();
        this.initChartAnimations();
        this.initScrollReveal();
        this.initFocusMode();
        this.startParticleAnimation();
    }

    // ========================================
    // AUDIO SYSTEM - Procedural Sound Generation
    // ========================================
    initAudioSystem() {
        // Create audio context on first user interaction
        const initContext = () => {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                this.createSounds();
            }
            document.removeEventListener('click', initContext);
            document.removeEventListener('keydown', initContext);
        };
        
        document.addEventListener('click', initContext, { once: true });
        document.addEventListener('keydown', initContext, { once: true });
    }

    createSounds() {
        // Pre-configure sound parameters for instant playback
        this.sounds = {
            hover: { frequency: 800, duration: 0.08, type: 'sine', gain: 0.08 },
            leave: { frequency: 600, duration: 0.06, type: 'sine', gain: 0.05 },
            click: { frequency: 1200, duration: 0.05, type: 'triangle', gain: 0.12 },
            success: { frequency: 880, duration: 0.15, type: 'sine', gain: 0.1 },
            scroll: { frequency: 400, duration: 0.03, type: 'sine', gain: 0.03 }
        };
    }

    playSound(soundName) {
        if (!this.settings.soundEnabled || !this.audioContext || !this.sounds[soundName]) return;

        const sound = this.sounds[soundName];
        const currentTime = this.audioContext.currentTime;

        // Create oscillator for tone
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        const filter = this.audioContext.createBiquadFilter();

        // Configure oscillator
        oscillator.type = sound.type;
        oscillator.frequency.setValueAtTime(sound.frequency, currentTime);

        // Subtle frequency modulation for richness
        if (soundName === 'hover' || soundName === 'success') {
            oscillator.frequency.exponentialRampToValueAtTime(
                sound.frequency * 0.95, 
                currentTime + sound.duration
            );
        }

        // Configure filter for warmth
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(2000, currentTime);
        filter.Q.setValueAtTime(1, currentTime);

        // Configure gain envelope (ADSR-like)
        const volume = sound.gain * this.settings.soundVolume;
        gainNode.gain.setValueAtTime(0, currentTime);
        gainNode.gain.linearRampToValueAtTime(volume, currentTime + 0.01); // Attack
        gainNode.gain.linearRampToValueAtTime(volume * 0.7, currentTime + sound.duration * 0.3); // Decay
        gainNode.gain.linearRampToValueAtTime(volume * 0.5, currentTime + sound.duration * 0.7); // Sustain
        gainNode.gain.exponentialRampToValueAtTime(0.01, currentTime + sound.duration); // Release

        // Connect nodes
        oscillator.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        // Play
        oscillator.start(currentTime);
        oscillator.stop(currentTime + sound.duration);
    }

    // ========================================
    // PARTICLE BACKGROUND SYSTEM
    // ========================================
    createParticleCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'particle-canvas';
        this.canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            opacity: 0.3;
        `;
        document.body.prepend(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        this.resizeCanvas();
        
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.createParticles();
    }

    createParticles() {
        this.particles = [];
        const particleCount = Math.floor((this.canvas.width * this.canvas.height) / 15000);
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 2 + 1,
                speedX: (Math.random() - 0.5) * 0.5,
                speedY: (Math.random() - 0.5) * 0.5,
                opacity: Math.random() * 0.5 + 0.2,
                color: this.getParticleColor()
            });
        }
    }

    getParticleColor() {
        const colors = ['#58a6ff', '#3fb950', '#f78166', '#bc8cff', '#ffd43b'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    updateParticles() {
        this.particles.forEach(particle => {
            particle.x += particle.speedX;
            particle.y += particle.speedY;

            // Mouse interaction
            const dx = this.mouse.x - particle.x;
            const dy = this.mouse.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 100) {
                const force = (100 - distance) / 100;
                particle.x -= dx * force * 0.02;
                particle.y -= dy * force * 0.02;
            }

            // Bounce off edges
            if (particle.x < 0 || particle.x > this.canvas.width) particle.speedX *= -1;
            if (particle.y < 0 || particle.y > this.canvas.height) particle.speedY *= -1;

            // Keep in bounds
            particle.x = Math.max(0, Math.min(this.canvas.width, particle.x));
            particle.y = Math.max(0, Math.min(this.canvas.height, particle.y));
        });
    }

    drawParticles() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw connections
        this.particles.forEach((p1, i) => {
            this.particles.slice(i + 1).forEach(p2 => {
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 120) {
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = `rgba(88, 166, 255, ${(1 - distance / 120) * 0.2})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.stroke();
                }
            });
        });

        // Draw particles
        this.particles.forEach(particle => {
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = particle.color;
            this.ctx.globalAlpha = particle.opacity;
            this.ctx.fill();
            this.ctx.globalAlpha = 1;
        });
    }

    startParticleAnimation() {
        const animate = () => {
            if (this.settings.particlesEnabled) {
                this.updateParticles();
                this.drawParticles();
            }
            this.animationId = requestAnimationFrame(animate);
        };
        animate();
    }

    // ========================================
    // PARALLAX SCROLL EFFECT
    // ========================================
    initParallaxEffect() {
        const layers = document.querySelectorAll('.stat-card, .chart-card, .repo-card');
        
        window.addEventListener('scroll', () => {
            if (!this.settings.parallaxEnabled) return;
            
            const scrolled = window.pageYOffset;
            layers.forEach((layer, index) => {
                const speed = (index % 3 + 1) * 0.05;
                const yPos = -(scrolled * speed);
                layer.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    // ========================================
    // ENHANCED CARD HOVER EFFECTS
    // ========================================
    initCardHoverEffects() {
        const cards = document.querySelectorAll('.stat-card, .chart-card, .repo-card');
        
        cards.forEach(card => {
            // Magnetic hover effect
            card.addEventListener('mousemove', (e) => {
                if (!this.settings.glowEnabled) return;
                
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const deltaX = (x - centerX) / centerX;
                const deltaY = (y - centerY) / centerY;
                
                card.style.transform = `
                    perspective(1000px)
                    rotateY(${deltaX * 5}deg)
                    rotateX(${-deltaY * 5}deg)
                    scale3d(1.02, 1.02, 1.02)
                `;
                
                // Glow effect follows cursor
                const glow = `radial-gradient(circle at ${x}px ${y}px, rgba(88, 166, 255, 0.15), transparent)`;
                card.style.background = `var(--bg-secondary), ${glow}`;
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
                card.style.background = '';
            });
        });
    }

    // ========================================
    // SMART TOOLTIPS WITH AI-LIKE INSIGHTS
    // ========================================
    initSmartTooltips() {
        const statCards = document.querySelectorAll('.stat-card');
        
        statCards.forEach(card => {
            const tooltip = this.createTooltip(card);
            
            card.addEventListener('mouseenter', (e) => {
                if (!this.settings.tooltipsEnabled) return;
                
                const insight = this.generateInsight(card);
                tooltip.textContent = insight;
                tooltip.style.opacity = '1';
                tooltip.style.transform = 'translateY(-10px)';
            });
            
            card.addEventListener('mouseleave', () => {
                tooltip.style.opacity = '0';
                tooltip.style.transform = 'translateY(0)';
            });
        });
    }

    createTooltip(card) {
        const tooltip = document.createElement('div');
        tooltip.className = 'smart-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            top: -40px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(13, 17, 23, 0.95);
            color: #58a6ff;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 12px;
            white-space: nowrap;
            pointer-events: none;
            opacity: 0;
            transition: all 0.3s ease;
            border: 1px solid #30363d;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
            z-index: 1000;
        `;
        card.style.position = 'relative';
        card.appendChild(tooltip);
        return tooltip;
    }

    generateInsight(card) {
        const label = card.querySelector('.stat-label')?.textContent || '';
        const value = card.querySelector('.stat-value')?.textContent || '0';
        
        const insights = {
            'Total Repositories': `🎯 You're managing ${value} projects`,
            'Total Stars': `⭐ ${value} developers appreciate your work`,
            'Total Forks': `🍴 ${value} times your code was reused`,
            'Languages Used': `💻 Polyglot developer with ${value} languages`,
            'Total Commits': `💾 ${value} code contributions`,
            'Contributors': `👥 ${value} people helped build this`,
            'Issues Resolved': `✅ ${value} problems solved`,
            'Resolution Rate': `📈 ${value} efficiency in issue management`,
            'Total Watchers': `👀 ${value} developers following your work`,
            'Active Repos': `🚀 ${value} live projects in development`
        };
        
        return insights[label] || `📊 ${label}: ${value}`;
    }

    // ========================================
    // CHART ENTRANCE ANIMATIONS
    // ========================================
    initChartAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'chartPulse 0.6s ease-out';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.chart-card').forEach(chart => {
            observer.observe(chart);
        });

        // Add chart pulse animation
        this.addStyleRule(`
            @keyframes chartPulse {
                0% { transform: scale(0.95); opacity: 0; }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); opacity: 1; }
            }
        `);
    }

    // ========================================
    // SCROLL REVEAL EFFECTS
    // ========================================
    initScrollReveal() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.repo-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });

        this.addStyleRule(`
            .repo-card.revealed {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
        `);
    }

    // ========================================
    // FOCUS MODE - GRAYSCALE + BLUR EVERYTHING EXCEPT HOVER
    // ========================================
    initFocusMode() {
        // Add global CSS for focus mode
        this.addStyleRule(`
            /* Focus Mode Transitions - Subtle & Elegant */
            .focusable-item {
                transition: filter 0.6s cubic-bezier(0.23, 1, 0.32, 1),
                           transform 0.6s cubic-bezier(0.23, 1, 0.32, 1),
                           box-shadow 0.6s cubic-bezier(0.23, 1, 0.32, 1);
                filter: grayscale(0.4) brightness(0.85);
                will-change: filter, transform;
            }

            .focusable-item.focused {
                filter: grayscale(0) brightness(1) saturate(1.05) !important;
                transform: translateY(-2px) scale(1.008);
                box-shadow: 0 8px 32px rgba(88, 166, 255, 0.12),
                           0 2px 8px rgba(88, 166, 255, 0.08),
                           0 0 0 1px rgba(88, 166, 255, 0.06) !important;
                z-index: 10 !important;
                position: relative;
            }

            .focusable-item.blurred {
                filter: grayscale(0.6) brightness(0.75) blur(0.5px);
                transform: scale(0.995);
                opacity: 0.8;
            }

            /* Keep UI elements always visible */
            .no-blur {
                filter: none !important;
                opacity: 1 !important;
                transform: none !important;
            }

            /* Subtle glow on focus - very refined */
            .focusable-item.focused::after {
                content: '';
                position: absolute;
                inset: -1px;
                background: linear-gradient(135deg, 
                    rgba(88, 166, 255, 0.03), 
                    rgba(63, 185, 80, 0.03),
                    rgba(188, 140, 255, 0.03));
                border-radius: inherit;
                z-index: -1;
                opacity: 0;
                transition: opacity 0.6s ease;
                pointer-events: none;
            }

            .focusable-item.focused::after {
                opacity: 1;
            }

            /* Micro-interaction: slight border enhancement */
            .focusable-item.focused {
                border-color: rgba(88, 166, 255, 0.15) !important;
            }

            /* Smooth chart transitions */
            .chart-card canvas {
                transition: opacity 0.6s ease, transform 0.6s ease;
            }

            .chart-card.blurred canvas {
                opacity: 0.7;
            }
        `);

        // Get all focusable elements
        const focusableSelectors = [
            '.stat-card',
            '.chart-card',
            '.repo-card'
        ];

        const excludeSelectors = [
            'header',
            '.filters',
            '.search-container',
            'button',
            'select',
            'input',
            '.settings-panel'
        ];

        // Mark focusable items
        focusableSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                el.classList.add('focusable-item');
            });
        });

        // Mark elements to never blur
        excludeSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                el.classList.add('no-blur');
            });
        });

        // Track current focused element
        let currentFocus = null;
        let focusTimeout = null;

        // Mouse enter handler with subtle sound
        const handleMouseEnter = (e) => {
            if (!this.settings.focusModeEnabled) return;
            
            const target = e.currentTarget;
            
            // Play subtle hover sound
            this.playSound('hover');

            // Clear previous timeout
            if (focusTimeout) clearTimeout(focusTimeout);

            // Remove previous focus
            if (currentFocus && currentFocus !== target) {
                currentFocus.classList.remove('focused');
            }

            // Blur all other focusable items with stagger
            const items = Array.from(document.querySelectorAll('.focusable-item'));
            items.forEach((item, index) => {
                if (item !== target) {
                    setTimeout(() => {
                        item.classList.add('blurred');
                        item.classList.remove('focused');
                    }, index * 3); // Subtle stagger effect
                }
            });

            // Focus current item with slight delay
            focusTimeout = setTimeout(() => {
                target.classList.add('focused');
                target.classList.remove('blurred');
                currentFocus = target;
            }, 80);
        };

        // Mouse leave handler with gentle transition
        const handleMouseLeave = (e) => {
            if (!this.settings.focusModeEnabled) return;

            if (focusTimeout) clearTimeout(focusTimeout);

            // Delay before removing effects
            focusTimeout = setTimeout(() => {
                const hoveredElement = document.querySelector('.focusable-item:hover');
                
                if (!hoveredElement) {
                    // Play subtle leave sound
                    this.playSound('leave');
                    
                    // Reset all items with stagger
                    const items = Array.from(document.querySelectorAll('.focusable-item'));
                    items.forEach((item, index) => {
                        setTimeout(() => {
                            item.classList.remove('focused', 'blurred');
                        }, index * 2);
                    });
                    currentFocus = null;
                }
            }, 150);
        };

        // Attach event listeners
        document.querySelectorAll('.focusable-item').forEach(item => {
            item.addEventListener('mouseenter', handleMouseEnter);
            item.addEventListener('mouseleave', handleMouseLeave);
        });

        // Handle dynamic content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList.contains('repo-card')) {
                        node.classList.add('focusable-item');
                        node.addEventListener('mouseenter', handleMouseEnter);
                        node.addEventListener('mouseleave', handleMouseLeave);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // ========================================
    // EVENT LISTENERS
    // ========================================
    initEventListeners() {
        // Track mouse position
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        // Subtle scroll sound
        let scrollTimeout;
        let lastScrollSound = 0;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            
            // Throttle scroll sound (max once per 200ms)
            const now = Date.now();
            if (now - lastScrollSound > 200) {
                this.playSound('scroll');
                lastScrollSound = now;
            }
        }, { passive: true });

        // Click sounds on interactive elements
        document.addEventListener('click', (e) => {
            if (e.target.matches('button, a, select, input[type="checkbox"]')) {
                this.playSound('click');
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'p':
                        e.preventDefault();
                        this.toggleParticles();
                        this.playSound('click');
                        break;
                    case 'g':
                        e.preventDefault();
                        this.toggleGlow();
                        this.playSound('click');
                        break;
                    case 'f':
                        e.preventDefault();
                        this.toggleFocusMode();
                        this.playSound('click');
                        break;
                    case 'm':
                        e.preventDefault();
                        this.toggleSound();
                        break;
                }
            }
        });

        // Add settings toggle UI
        this.createSettingsPanel();
    }

    // ========================================
    // SETTINGS PANEL
    // ========================================
    createSettingsPanel() {
        const panel = document.createElement('div');
        panel.className = 'no-blur settings-panel';
        panel.innerHTML = `
            <div style="
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(13, 17, 23, 0.98);
                border: 1px solid rgba(88, 166, 255, 0.1);
                border-radius: 12px;
                padding: 16px 18px;
                z-index: 9999;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 1px rgba(88, 166, 255, 0.2);
                backdrop-filter: blur(10px);
                transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
                font-family: 'Inter', sans-serif;
            " onmouseenter="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 32px rgba(0, 0, 0, 0.5), 0 0 2px rgba(88, 166, 255, 0.3)'" 
               onmouseleave="this.style.transform=''; this.style.boxShadow='0 4px 20px rgba(0, 0, 0, 0.4), 0 0 1px rgba(88, 166, 255, 0.2)'">
                <div style="
                    color: #e6edf3; 
                    font-weight: 600; 
                    margin-bottom: 14px; 
                    font-size: 13px;
                    letter-spacing: 0.3px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                ">
                    <span style="font-size: 16px;">✨</span>
                    <span>Effects</span>
                </div>
                <label style="display: flex; align-items: center; gap: 10px; color: #8b949e; font-size: 11px; cursor: pointer; margin-bottom: 10px; transition: color 0.2s ease;">
                    <input type="checkbox" id="toggle-particles" checked style="cursor: pointer; width: 14px; height: 14px;">
                    <span>Particles</span>
                </label>
                <label style="display: flex; align-items: center; gap: 10px; color: #8b949e; font-size: 11px; cursor: pointer; margin-bottom: 10px; transition: color 0.2s ease;">
                    <input type="checkbox" id="toggle-parallax" checked style="cursor: pointer; width: 14px; height: 14px;">
                    <span>Parallax</span>
                </label>
                <label style="display: flex; align-items: center; gap: 10px; color: #8b949e; font-size: 11px; cursor: pointer; margin-bottom: 10px; transition: color 0.2s ease;">
                    <input type="checkbox" id="toggle-glow" checked style="cursor: pointer; width: 14px; height: 14px;">
                    <span>Glow</span>
                </label>
                <label style="display: flex; align-items: center; gap: 10px; color: #8b949e; font-size: 11px; cursor: pointer; margin-bottom: 10px; transition: color 0.2s ease;">
                    <input type="checkbox" id="toggle-tooltips" checked style="cursor: pointer; width: 14px; height: 14px;">
                    <span>Tooltips</span>
                </label>
                <label style="display: flex; align-items: center; gap: 10px; color: #8b949e; font-size: 11px; cursor: pointer; margin-bottom: 10px; transition: color 0.2s ease;">
                    <input type="checkbox" id="toggle-focus" checked style="cursor: pointer; width: 14px; height: 14px;">
                    <span>Focus Mode</span>
                </label>
                <label style="display: flex; align-items: center; gap: 10px; color: #8b949e; font-size: 11px; cursor: pointer; margin-bottom: 10px; transition: color 0.2s ease;">
                    <input type="checkbox" id="toggle-sound" checked style="cursor: pointer; width: 14px; height: 14px;">
                    <span>🔊 Sound</span>
                </label>
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(48, 54, 61, 0.5);">
                    <div style="color: #58a6ff; font-size: 9px; margin-bottom: 4px; opacity: 0.8;">Shortcuts</div>
                    <div style="color: #6e7681; font-size: 9px; font-family: 'JetBrains Mono', monospace; line-height: 1.4;">
                        Ctrl+P • Ctrl+G • Ctrl+F • Ctrl+M
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(panel);

        // Add hover effects to labels
        const labels = panel.querySelectorAll('label');
        labels.forEach(label => {
            label.addEventListener('mouseenter', () => {
                label.style.color = '#c9d1d9';
            });
            label.addEventListener('mouseleave', () => {
                label.style.color = '#8b949e';
            });
        });

        // Wire up toggles
        document.getElementById('toggle-particles').addEventListener('change', (e) => {
            this.settings.particlesEnabled = e.target.checked;
            this.canvas.style.opacity = e.target.checked ? '0.3' : '0';
            this.playSound('click');
        });

        document.getElementById('toggle-parallax').addEventListener('change', (e) => {
            this.settings.parallaxEnabled = e.target.checked;
            if (!e.target.checked) {
                document.querySelectorAll('.stat-card, .chart-card, .repo-card').forEach(el => {
                    el.style.transform = '';
                });
            }
            this.playSound('click');
        });

        document.getElementById('toggle-glow').addEventListener('change', (e) => {
            this.settings.glowEnabled = e.target.checked;
            this.playSound('click');
        });

        document.getElementById('toggle-tooltips').addEventListener('change', (e) => {
            this.settings.tooltipsEnabled = e.target.checked;
            this.playSound('click');
        });

        document.getElementById('toggle-focus').addEventListener('change', (e) => {
            this.settings.focusModeEnabled = e.target.checked;
            this.playSound('click');
            
            if (!e.target.checked) {
                // Reset all items when disabled
                document.querySelectorAll('.focusable-item').forEach(item => {
                    item.classList.remove('focused', 'blurred');
                    item.style.filter = '';
                });
            } else {
                // Apply initial grayscale when enabled
                document.querySelectorAll('.focusable-item').forEach(item => {
                    item.style.filter = 'grayscale(0.4) brightness(0.85)';
                });
            }
        });

        document.getElementById('toggle-sound').addEventListener('change', (e) => {
            this.settings.soundEnabled = e.target.checked;
            if (e.target.checked) {
                this.playSound('success');
            }
        });
    }

    // ========================================
    // UTILITY METHODS
    // ========================================
    toggleParticles() {
        this.settings.particlesEnabled = !this.settings.particlesEnabled;
        document.getElementById('toggle-particles').checked = this.settings.particlesEnabled;
        this.canvas.style.opacity = this.settings.particlesEnabled ? '0.3' : '0';
    }

    toggleGlow() {
        this.settings.glowEnabled = !this.settings.glowEnabled;
        document.getElementById('toggle-glow').checked = this.settings.glowEnabled;
    }

    toggleFocusMode() {
        this.settings.focusModeEnabled = !this.settings.focusModeEnabled;
        document.getElementById('toggle-focus').checked = this.settings.focusModeEnabled;
        this.playSound('click');
        
        if (!this.settings.focusModeEnabled) {
            document.querySelectorAll('.focusable-item').forEach(item => {
                item.classList.remove('focused', 'blurred');
                item.style.filter = '';
            });
        } else {
            document.querySelectorAll('.focusable-item').forEach(item => {
                item.style.filter = 'grayscale(0.4) brightness(0.85)';
            });
        }
    }

    toggleSound() {
        this.settings.soundEnabled = !this.settings.soundEnabled;
        document.getElementById('toggle-sound').checked = this.settings.soundEnabled;
        if (this.settings.soundEnabled) {
            this.playSound('success');
        }
    }

    addStyleRule(css) {
        const style = document.createElement('style');
        style.textContent = css;
        document.head.appendChild(style);
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.canvas) {
            this.canvas.remove();
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.dashboardEffects = new DashboardEffects();
    });
} else {
    window.dashboardEffects = new DashboardEffects();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardEffects;
}
