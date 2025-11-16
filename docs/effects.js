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
        this.settings = {
            particlesEnabled: true,
            parallaxEnabled: true,
            glowEnabled: true,
            tooltipsEnabled: true,
            focusModeEnabled: true,
            soundEnabled: false // Future feature
        };
        
        this.init();
    }

    init() {
        this.createParticleCanvas();
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
            /* Focus Mode Transitions */
            .focusable-item {
                transition: filter 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                           transform 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                           box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                           z-index 0s;
                filter: grayscale(0.7) blur(0px) brightness(0.7);
                will-change: filter, transform;
            }

            .focusable-item.focused {
                filter: grayscale(0) blur(0px) brightness(1) !important;
                transform: scale(1.03) translateZ(0);
                box-shadow: 0 20px 60px rgba(88, 166, 255, 0.3),
                           0 0 0 1px rgba(88, 166, 255, 0.2) !important;
                z-index: 100 !important;
                position: relative;
            }

            .focusable-item.blurred {
                filter: grayscale(0.9) blur(3px) brightness(0.5);
                transform: scale(0.98);
                opacity: 0.6;
            }

            /* Keep UI elements always visible */
            .no-blur {
                filter: none !important;
                opacity: 1 !important;
            }

            /* Smooth transitions for charts */
            .chart-card canvas {
                transition: filter 0.4s ease;
            }

            /* Enhanced glow on focus */
            .focusable-item.focused::before {
                content: '';
                position: absolute;
                inset: -2px;
                background: linear-gradient(45deg, #58a6ff, #3fb950, #bc8cff, #f78166);
                border-radius: 14px;
                z-index: -1;
                opacity: 0;
                animation: borderGlow 3s ease infinite;
            }

            @keyframes borderGlow {
                0%, 100% { opacity: 0.3; }
                50% { opacity: 0.6; }
            }

            /* Pulsing effect on focused element */
            .focusable-item.focused {
                animation: focusPulse 2s ease-in-out infinite;
            }

            @keyframes focusPulse {
                0%, 100% { 
                    box-shadow: 0 20px 60px rgba(88, 166, 255, 0.3),
                               0 0 0 1px rgba(88, 166, 255, 0.2);
                }
                50% { 
                    box-shadow: 0 25px 70px rgba(88, 166, 255, 0.5),
                               0 0 0 2px rgba(88, 166, 255, 0.4);
                }
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

        // Mouse enter handler
        const handleMouseEnter = (e) => {
            if (!this.settings.focusModeEnabled) return;
            
            const target = e.currentTarget;
            
            // Clear previous timeout
            if (focusTimeout) clearTimeout(focusTimeout);

            // Remove previous focus
            if (currentFocus && currentFocus !== target) {
                currentFocus.classList.remove('focused');
            }

            // Blur all other focusable items
            document.querySelectorAll('.focusable-item').forEach(item => {
                if (item !== target) {
                    item.classList.add('blurred');
                    item.classList.remove('focused');
                }
            });

            // Focus current item with slight delay for smooth effect
            focusTimeout = setTimeout(() => {
                target.classList.add('focused');
                target.classList.remove('blurred');
                currentFocus = target;
            }, 50);
        };

        // Mouse leave handler with delay
        const handleMouseLeave = (e) => {
            if (!this.settings.focusModeEnabled) return;

            if (focusTimeout) clearTimeout(focusTimeout);

            // Delay before removing effects to prevent flickering
            focusTimeout = setTimeout(() => {
                // Check if mouse is not over any focusable item
                const hoveredElement = document.querySelector('.focusable-item:hover');
                
                if (!hoveredElement) {
                    // Reset all items
                    document.querySelectorAll('.focusable-item').forEach(item => {
                        item.classList.remove('focused', 'blurred');
                    });
                    currentFocus = null;
                }
            }, 100);
        };

        // Attach event listeners
        document.querySelectorAll('.focusable-item').forEach(item => {
            item.addEventListener('mouseenter', handleMouseEnter);
            item.addEventListener('mouseleave', handleMouseLeave);
        });

        // Handle dynamic content (for repo cards loaded later)
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

        // Initial state - slight grayscale on all
        if (this.settings.focusModeEnabled) {
            document.querySelectorAll('.focusable-item').forEach(item => {
                item.style.filter = 'grayscale(0.7) blur(0px) brightness(0.7)';
            });
        }
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

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'p':
                        e.preventDefault();
                        this.toggleParticles();
                        break;
                    case 'g':
                        e.preventDefault();
                        this.toggleGlow();
                        break;
                    case 'f':
                        e.preventDefault();
                        this.toggleFocusMode();
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
                border: 1px solid #30363d;
                border-radius: 12px;
                padding: 16px;
                z-index: 9999;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(10px);
                transition: transform 0.3s ease, opacity 0.3s ease;
            " onmouseenter="this.style.transform='scale(1.02)'" onmouseleave="this.style.transform='scale(1)'">
                <div style="color: #e6edf3; font-weight: 600; margin-bottom: 12px; font-size: 14px;">
                    ✨ Visual Effects
                </div>
                <label style="display: flex; align-items: center; gap: 8px; color: #8b949e; font-size: 12px; cursor: pointer; margin-bottom: 8px;">
                    <input type="checkbox" id="toggle-particles" checked style="cursor: pointer;">
                    <span>Particle Background</span>
                </label>
                <label style="display: flex; align-items: center; gap: 8px; color: #8b949e; font-size: 12px; cursor: pointer; margin-bottom: 8px;">
                    <input type="checkbox" id="toggle-parallax" checked style="cursor: pointer;">
                    <span>Parallax Scroll</span>
                </label>
                <label style="display: flex; align-items: center; gap: 8px; color: #8b949e; font-size: 12px; cursor: pointer; margin-bottom: 8px;">
                    <input type="checkbox" id="toggle-glow" checked style="cursor: pointer;">
                    <span>Card Glow Effects</span>
                </label>
                <label style="display: flex; align-items: center; gap: 8px; color: #8b949e; font-size: 12px; cursor: pointer; margin-bottom: 8px;">
                    <input type="checkbox" id="toggle-tooltips" checked style="cursor: pointer;">
                    <span>Smart Tooltips</span>
                </label>
                <label style="display: flex; align-items: center; gap: 8px; color: #8b949e; font-size: 12px; cursor: pointer; margin-bottom: 8px;">
                    <input type="checkbox" id="toggle-focus" checked style="cursor: pointer;">
                    <span>🎯 Focus Mode</span>
                </label>
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #30363d; color: #58a6ff; font-size: 10px;">
                    ⌨️ Shortcuts: Ctrl+P, Ctrl+G, Ctrl+F
                </div>
            </div>
        `;
        document.body.appendChild(panel);

        // Wire up toggles
        document.getElementById('toggle-particles').addEventListener('change', (e) => {
            this.settings.particlesEnabled = e.target.checked;
            this.canvas.style.opacity = e.target.checked ? '0.3' : '0';
        });

        document.getElementById('toggle-parallax').addEventListener('change', (e) => {
            this.settings.parallaxEnabled = e.target.checked;
            if (!e.target.checked) {
                document.querySelectorAll('.stat-card, .chart-card, .repo-card').forEach(el => {
                    el.style.transform = '';
                });
            }
        });

        document.getElementById('toggle-glow').addEventListener('change', (e) => {
            this.settings.glowEnabled = e.target.checked;
        });

        document.getElementById('toggle-tooltips').addEventListener('change', (e) => {
            this.settings.tooltipsEnabled = e.target.checked;
        });

        document.getElementById('toggle-focus').addEventListener('change', (e) => {
            this.settings.focusModeEnabled = e.target.checked;
            
            if (!e.target.checked) {
                // Reset all items when disabled
                document.querySelectorAll('.focusable-item').forEach(item => {
                    item.classList.remove('focused', 'blurred');
                    item.style.filter = '';
                });
            } else {
                // Apply initial grayscale when enabled
                document.querySelectorAll('.focusable-item').forEach(item => {
                    item.style.filter = 'grayscale(0.7) blur(0px) brightness(0.7)';
                });
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
        
        if (!this.settings.focusModeEnabled) {
            document.querySelectorAll('.focusable-item').forEach(item => {
                item.classList.remove('focused', 'blurred');
                item.style.filter = '';
            });
        } else {
            document.querySelectorAll('.focusable-item').forEach(item => {
                item.style.filter = 'grayscale(0.7) blur(0px) brightness(0.7)';
            });
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
