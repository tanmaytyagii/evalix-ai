"""
Centralised CSS for the Streamlit dashboard.
A single string keeps the visual identity consistent across pages.
"""

EVALIX_LOGO_SVG = """
<svg width="100%" height="100%" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Brain outline/base -->
  <path d="M60 10C35 10 15 30 15 55C15 68 21 80 30 88C35 93 42 105 45 110C48 114 53 115 60 115C67 115 72 114 75 110C78 105 85 93 90 88C99 80 105 68 105 55C105 30 85 10 60 10Z" fill="url(#brainGrad)" />
  <!-- Circuit lines -->
  <path d="M30 55H50L60 40H80" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M40 75H55L65 90H75" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M50 55L60 70H85" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="30" cy="55" r="5" fill="white"/>
  <circle cx="80" cy="40" r="5" fill="white"/>
  <circle cx="40" cy="75" r="5" fill="white"/>
  <circle cx="75" cy="90" r="5" fill="white"/>
  <circle cx="85" cy="70" r="5" fill="white"/>
  <defs>
    <linearGradient id="brainGrad" x1="15" y1="10" x2="105" y2="115" gradientUnits="userSpaceOnUse">
      <stop stop-color="#020617"/>
      <stop offset="0.5" stop-color="#1e40af"/>
      <stop offset="1" stop-color="#3b82f6"/>
    </linearGradient>
  </defs>
</svg>
"""

def get_css() -> str:
    # Theme Variables (Dark Mode Only)
    bg_primary = "#030303"
    bg_secondary = "rgba(10, 10, 12, 0.7)"
    bg_tertiary = "rgba(255, 255, 255, 0.02)"
    bg_glass = "rgba(15, 15, 20, 0.4)"
    
    text_primary = "#ffffff"
    text_secondary = "#a1a1aa"
    text_muted = "#52525b"
    
    border = "rgba(255, 255, 255, 0.06)"
    border_light = "rgba(255, 255, 255, 0.1)"
    border_hover = "rgba(255, 255, 255, 0.2)"
    
    hero_gradient = "linear-gradient(135deg, #ffffff 0%, #a1a1aa 100%)"
    logo_text_gradient = "linear-gradient(to right, #fff, #a1a1aa)"
    glass_shadow = "0 30px 60px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)"
    card_shadow_hover = "0 20px 40px rgba(0,0,0,0.4), 0 0 20px rgba(139, 92, 246, 0.1), inset 0 1px 0 rgba(255,255,255,0.1)"
    input_bg = "rgba(0,0,0,0.4)"

    return f"""
<style>
/* Import Inter & Space Grotesk fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {{
  --bg-primary: {bg_primary};
  --bg-secondary: {bg_secondary};
  --bg-tertiary: {bg_tertiary};
  --bg-glass: {bg_glass};
  
  --text-primary: {text_primary};
  --text-secondary: {text_secondary};
  --text-muted: {text_muted};
  
  --accent-primary: #8b5cf6;
  --accent-secondary: #3b82f6;
  --accent-tertiary: #10b981;
  --accent-gradient: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 50%, #10b981 100%);
  --accent-glow: rgba(139, 92, 246, 0.4);
  
  --success: #10b981;
  --success-bg: rgba(16, 185, 129, 0.1);
  --warning: #f59e0b;
  --warning-bg: rgba(245, 158, 11, 0.1);
  --danger: #ef4444;
  --danger-bg: rgba(239, 68, 68, 0.1);
  
  --border: {border};
  --border-light: {border_light};
  --border-hover: {border_hover};
  
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}}

/* Top Navigation Bar */
.top-right-nav {{
    position: fixed; top: 24px; right: 24px; z-index: 999999;
    display: flex; gap: 16px; align-items: center;
}}
.nav-bell, .nav-avatar {{
    width: 36px; height: 36px; border-radius: 50%;
    background: var(--bg-secondary); border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    color: var(--text-secondary); font-size: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}
.nav-avatar {{ background: rgba(59, 130, 246, 0.1); color: var(--accent-secondary); font-weight: 600; font-size: 14px; }}


/* Global Typography */
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-primary);
}}

h1, h2, h3, .metric-card .value, .hero-title {{
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.04em;
}}

/* App Background & Grain */
.stApp {{ 
    background-color: var(--bg-primary);
    color: var(--text-primary); 
}}
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 9999;
}}

/* Ambient Background Orbs */
.ambient-orb {{
    position: fixed;
    border-radius: 50%;
    filter: blur(120px);
    z-index: -1;
    opacity: 0.4;
    animation: float 20s infinite ease-in-out alternate;
}}
.orb-1 {{ top: -10%; left: -10%; width: 50vw; height: 50vw; background: rgba(139, 92, 246, 0.15); animation-delay: 0s; }}
.orb-2 {{ bottom: -20%; right: -10%; width: 60vw; height: 60vw; background: rgba(59, 130, 246, 0.15); animation-delay: -5s; }}
.orb-3 {{ top: 40%; left: 60%; width: 40vw; height: 40vw; background: rgba(16, 185, 129, 0.1); animation-delay: -10s; }}

@keyframes float {{
    0% {{ transform: translate(0, 0) scale(1); }}
    100% {{ transform: translate(5%, 5%) scale(1.1); }}
}}

/* Container Spacing */
section.main > div.block-container {{ 
    padding-top: 3rem; 
    padding-bottom: 6rem;
    max-width: 1280px; 
}}

/* Sticky Sidebar Customization */
section[data-testid="stSidebar"] {{
    background-color: var(--bg-secondary);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-right: 1px solid var(--border);
    box-shadow: 1px 0 20px rgba(0,0,0,0.02);
}}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{ display: none; }}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1, 
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2, 
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
    color: var(--text-primary) !important;
}}

.sidebar-logo {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 0 32px 0;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border);
}}
.sidebar-logo-icon {{
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.sidebar-logo-text {{
    font-size: 22px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    letter-spacing: -0.04em;
    background: {logo_text_gradient};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.sidebar-status-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 14px;
    padding: 12px 16px;
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
}}
.sidebar-status-item:hover {{
    background: rgba(139, 92, 246, 0.05);
    border-color: var(--border-light);
    transform: translateX(4px);
}}
.status-indicator {{ width: 8px; height: 8px; border-radius: 50%; position: relative; }}
.status-indicator::after {{
    content: ''; position: absolute; inset: -4px; border-radius: 50%;
    background: inherit; opacity: 0.4; animation: pulse-ring 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}}
@keyframes pulse-ring {{ 0% {{ transform: scale(0.5); opacity: 0; }} 50% {{ opacity: 0.5; }} 100% {{ transform: scale(1.5); opacity: 0; }} }}
.status-indicator.green {{ background: var(--success); }}
.status-indicator.yellow {{ background: var(--warning); }}
.status-indicator.blue {{ background: var(--accent-secondary); }}

/* ─── Hero Section (premium) ─── */
@keyframes heroOrbDrift {{
    0%, 100% {{ transform: translate(0, 0) scale(1); }}
    50% {{ transform: translate(4%, -3%) scale(1.06); }}
}}
@keyframes heroBorderPulse {{
    0%, 100% {{ opacity: 0.55; }}
    50% {{ opacity: 1; }}
}}
@keyframes heroShine {{
    0% {{ transform: translateX(-120%) skewX(-12deg); }}
    100% {{ transform: translateX(220%) skewX(-12deg); }}
}}
@keyframes illustFloat {{
    0%, 100% {{ transform: translateY(0) rotate(0deg); }}
    50% {{ transform: translateY(-10px) rotate(0.6deg); }}
}}
@keyframes illustBadgePulse {{
    0%, 100% {{ box-shadow: 0 12px 40px rgba(99, 102, 241, 0.45), 0 0 0 0 rgba(139, 92, 246, 0.35); }}
    50% {{ box-shadow: 0 16px 48px rgba(59, 130, 246, 0.55), 0 0 0 12px rgba(139, 92, 246, 0); }}
}}
@keyframes illustLineShimmer {{
    0% {{ background-position: 200% center; }}
    100% {{ background-position: -200% center; }}
}}

.hero {{
    position: relative;
    margin-bottom: 48px;
    border-radius: 28px;
    overflow: hidden;
    isolation: isolate;
    background: linear-gradient(
        145deg,
        rgba(14, 14, 24, 0.72) 0%,
        rgba(6, 6, 12, 0.55) 48%,
        rgba(10, 12, 22, 0.65) 100%
    );
    backdrop-filter: blur(40px) saturate(1.25);
    -webkit-backdrop-filter: blur(40px) saturate(1.25);
    box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.06),
        0 32px 64px -16px rgba(0, 0, 0, 0.65),
        0 0 80px -20px rgba(99, 102, 241, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
}}
.hero::before {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(
        135deg,
        rgba(167, 139, 250, 0.65) 0%,
        rgba(59, 130, 246, 0.35) 35%,
        rgba(34, 211, 238, 0.25) 65%,
        rgba(167, 139, 250, 0.5) 100%
    );
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    z-index: 2;
    animation: heroBorderPulse 5s ease-in-out infinite;
}}
.hero-border-glow {{
    position: absolute;
    inset: -1px;
    border-radius: inherit;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.25), transparent 40%, rgba(34, 211, 238, 0.15));
    filter: blur(20px);
    opacity: 0.7;
    z-index: 0;
    pointer-events: none;
}}
.hero-noise {{
    position: absolute;
    inset: 0;
    opacity: 0.35;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 1;
}}
.hero-orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(70px);
    pointer-events: none;
    z-index: 0;
    will-change: transform;
    animation: heroOrbDrift 18s ease-in-out infinite alternate;
}}
.hero-orb-violet {{
    width: 320px; height: 320px;
    top: -40%; left: -8%;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.35), transparent 68%);
}}
.hero-orb-cyan {{
    width: 280px; height: 280px;
    bottom: -35%; right: 15%;
    background: radial-gradient(circle, rgba(34, 211, 238, 0.22), transparent 70%);
    animation-delay: -6s;
}}
.hero-orb-blue {{
    width: 200px; height: 200px;
    top: 20%; right: 38%;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.28), transparent 72%);
    animation-delay: -11s;
}}
.hero-inner {{
    position: relative;
    z-index: 3;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: clamp(28px, 5vw, 56px);
    padding: clamp(36px, 5vw, 60px) clamp(28px, 5vw, 64px);
}}
.hero-inner::after {{
    content: '';
    position: absolute;
    top: 0; left: -30%;
    width: 45%;
    height: 100%;
    background: linear-gradient(105deg, transparent 30%, rgba(255,255,255,0.04) 50%, transparent 70%);
    animation: heroShine 9s ease-in-out infinite;
    pointer-events: none;
}}
.hero-content {{
    position: relative;
    z-index: 4;
    max-width: 620px;
    flex: 1;
    min-width: 0;
}}
.hero-title {{
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.04em;
    line-height: 1.05;
}}
.hero-brand {{
    display: block;
    font-size: clamp(36px, 5vw, 52px);
    font-weight: 700;
    background: linear-gradient(120deg, #ffffff 0%, #c4b5fd 28%, #93c5fd 55%, #67e8f9 85%, #a78bfa 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 28px rgba(139, 92, 246, 0.35));
    animation: heroGradientShift 8s ease-in-out infinite alternate;
}}
@keyframes heroGradientShift {{
    0% {{ background-position: 0% center; }}
    100% {{ background-position: 100% center; }}
}}
.hero-title-rest {{
    display: block;
    font-size: clamp(22px, 3.2vw, 30px);
    font-weight: 600;
    color: rgba(244, 244, 245, 0.92);
    letter-spacing: -0.03em;
}}
.gradient-text {{
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.hero-desc {{
    color: var(--text-secondary);
    margin: 22px 0 0;
    font-size: clamp(15px, 1.7vw, 17px);
    line-height: 1.75;
    font-weight: 400;
    max-width: 54ch;
    text-wrap: pretty;
}}
.hero-badges {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 34px;
}}
.hero-badge {{
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 18px 10px 14px;
    background: rgba(8, 8, 14, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    color: rgba(244, 244, 245, 0.95);
    letter-spacing: 0.01em;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.06);
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s, box-shadow 0.25s;
    overflow: hidden;
}}
.hero-badge::before {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    opacity: 0;
    transition: opacity 0.25s;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(59, 130, 246, 0.08));
}}
.hero-badge:hover {{
    transform: translateY(-3px);
    border-color: rgba(167, 139, 250, 0.45);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35), 0 0 24px rgba(139, 92, 246, 0.15);
}}
.hero-badge:hover::before {{ opacity: 1; }}
.hero-badge-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    font-size: 14px;
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}}
.hero-badge-speed .hero-badge-icon {{
    background: rgba(251, 191, 36, 0.12);
    box-shadow: 0 0 16px rgba(251, 191, 36, 0.2);
}}
.hero-badge-shield .hero-badge-icon {{
    background: rgba(52, 211, 153, 0.12);
    box-shadow: 0 0 16px rgba(52, 211, 153, 0.2);
}}
.hero-badge-chart .hero-badge-icon {{
    background: rgba(96, 165, 250, 0.12);
    box-shadow: 0 0 16px rgba(96, 165, 250, 0.2);
}}

/* Hero illustration */
.hero-illustration {{
    position: relative;
    width: min(400px, 42vw);
    height: min(300px, 32vw);
    min-height: 260px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    perspective: 900px;
}}
.illust-bg-glow {{
    position: absolute;
    width: 240px;
    height: 240px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.45) 0%, rgba(59, 130, 246, 0.15) 45%, transparent 70%);
    border-radius: 50%;
    filter: blur(36px);
    z-index: 1;
    animation: heroOrbDrift 14s ease-in-out infinite alternate;
}}
.illust-ring {{
    position: absolute;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    border: 1px solid rgba(167, 139, 250, 0.15);
    box-shadow: 0 0 60px rgba(139, 92, 246, 0.08), inset 0 0 40px rgba(59, 130, 246, 0.05);
    z-index: 1;
    animation: illustFloat 7s ease-in-out infinite;
}}
.illust-resume {{
    position: relative;
    z-index: 2;
    width: 272px;
    max-width: 92%;
    background: linear-gradient(165deg, rgba(22, 22, 34, 0.92) 0%, rgba(12, 12, 20, 0.88) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 26px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow:
        0 24px 48px rgba(0, 0, 0, 0.45),
        0 0 0 1px rgba(255, 255, 255, 0.04),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    animation: illustFloat 6s ease-in-out infinite;
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s;
}}
.hero:hover .illust-resume {{
    transform: translateY(-8px) rotateX(4deg) rotateY(-3deg);
    box-shadow:
        0 36px 64px rgba(0, 0, 0, 0.5),
        0 0 48px rgba(99, 102, 241, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.12);
}}
.illust-header {{ display: flex; gap: 16px; align-items: center; }}
.illust-avatar {{
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.35), rgba(139, 92, 246, 0.25));
    border: 1px solid rgba(147, 197, 253, 0.35);
    box-shadow: 0 0 24px rgba(59, 130, 246, 0.25);
}}
.illust-lines {{ display: flex; flex-direction: column; gap: 9px; flex: 1; }}
.illust-lines.mt {{ margin-top: 4px; }}
.illust-line {{
    height: 8px;
    border-radius: 6px;
    background: linear-gradient(90deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.12) 50%, rgba(255,255,255,0.06) 100%);
    background-size: 200% 100%;
    animation: illustLineShimmer 3.5s linear infinite;
}}
.illust-line.w-1 {{ width: 100%; animation-delay: 0s; }}
.illust-line.w-2 {{ width: 58%; animation-delay: 0.4s; }}
.illust-line.w-3 {{ width: 78%; animation-delay: 0.8s; }}
.illust-stars {{
    color: #fbbf24;
    font-size: 17px;
    letter-spacing: 3px;
    text-shadow: 0 0 20px rgba(251, 191, 36, 0.45);
}}
.illust-badge {{
    position: absolute;
    bottom: -22px;
    right: -22px;
    width: 84px;
    height: 84px;
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 50%, #22d3ee 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 4px solid rgba(12, 12, 20, 0.9);
    animation: illustBadgePulse 3s ease-in-out infinite;
    transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}}
.hero:hover .illust-badge {{
    transform: scale(1.08) rotate(-4deg);
}}
.illust-badge svg {{ width: 38px; height: 38px; color: white; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2)); }}

@media (max-width: 1100px) {{
    .hero-inner {{
        flex-direction: column;
        text-align: center;
        align-items: center;
    }}
    .hero-content {{ max-width: 100%; }}
    .hero-desc {{ margin-left: auto; margin-right: auto; }}
    .hero-badges {{ justify-content: center; }}
    .hero-illustration {{
        width: 100%;
        max-width: 380px;
        height: 280px;
        margin-top: 8px;
    }}
}}
@media (max-width: 640px) {{
    .hero {{ border-radius: 22px; margin-bottom: 32px; }}
    .hero-inner {{ padding: 28px 20px; gap: 24px; }}
    .hero-badges {{ gap: 8px; }}
    .hero-badge {{ font-size: 12px; padding: 8px 14px 8px 10px; }}
    .illust-resume {{ width: 240px; padding: 20px; }}
}}
@media (prefers-reduced-motion: reduce) {{
    .hero-orb, .hero-inner::after, .hero-brand, .illust-resume, .illust-ring,
    .illust-bg-glow, .illust-line, .illust-badge, .hero::before {{
        animation: none !important;
    }}
    .hero:hover .illust-resume,
    .hero:hover .illust-badge {{
        transform: none;
    }}
}}

/* KPI Cards */
.metric-card {{
    background: var(--bg-glass);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 28px;
    height: 100%;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    box-shadow: {glass_shadow};
}}
.metric-card::before {{
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(800px circle at var(--mouse-x, 50%) var(--mouse-y, -20%), rgba(255,255,255,0.06), transparent 40%);
    opacity: 0; transition: opacity 0.5s; pointer-events: none;
}}
.metric-card:hover {{
    transform: translateY(-8px);
    border-color: var(--border-hover);
    box-shadow: {card_shadow_hover};
}}
.metric-card:hover::before {{ opacity: 1; }}

.metric-header {{
    display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;
}}
.metric-card .label {{ 
    color: var(--text-secondary); font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; 
}}
.metric-icon {{
    width: 44px; height: 44px; border-radius: 12px;
    background: var(--bg-tertiary); border: 1px solid var(--border-light);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; color: var(--text-primary);
}}
.metric-card .value {{ 
    font-size: 42px; font-weight: 700; color: var(--text-primary); line-height: 1;
}}
.metric-card .sub {{ 
    color: var(--text-muted); font-size: 14px; margin-top: 12px; font-weight: 500;
}}

/* Custom Table */
.elite-table {{
    width: 100%; border-collapse: separate; border-spacing: 0;
    background: var(--bg-glass); border: 1px solid var(--border);
    border-radius: var(--radius-xl); overflow: hidden;
    backdrop-filter: blur(16px);
}}
.elite-table th {{
    background: var(--bg-tertiary); color: var(--text-secondary);
    font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
    padding: 18px 24px; text-align: left; border-bottom: 1px solid var(--border);
}}
.elite-table td {{
    padding: 18px 24px; color: var(--text-primary);
    border-bottom: 1px solid var(--border); font-size: 14px; font-weight: 500;
    transition: background 0.2s;
}}
.elite-table tr:hover td {{ background: var(--bg-tertiary); }}
.elite-table tr:last-child td {{ border-bottom: none; }}

.candidate-cell {{ display: flex; align-items: center; gap: 12px; }}
.candidate-avatar {{
    width: 36px; height: 36px; border-radius: 50%;
    background: var(--accent-gradient);
    color: white;
    display: flex; align-items: center; justify-content: center;
    font-weight: 600; font-size: 14px; border: 1px solid var(--border);
    box-shadow: 0 4px 10px var(--accent-glow);
}}

/* Progress Rings */
.circular-chart {{ display: block; margin: 0 auto; max-width: 80%; max-height: 250px; }}
.circle-bg {{ fill: none; stroke: var(--border); stroke-width: 2.5; }}
.circle {{ fill: none; stroke-width: 2.5; stroke-linecap: round; animation: progress 1s ease-out forwards; }}
@keyframes progress {{ 0% {{ stroke-dasharray: 0 100; }} }}
.percentage {{ fill: var(--text-primary); font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.5em; text-anchor: middle; }}

/* Badges */
.badge {{
    display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 999px;
    font-weight: 600; font-size: 12px; letter-spacing: 0.02em;
}}
.badge::before {{ content: ''; width: 6px; height: 6px; border-radius: 50%; }}
.badge.strong  {{ background: var(--success-bg); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.2); }}
.badge.strong::before {{ background: var(--success); box-shadow: 0 0 8px var(--success); }}
.badge.short   {{ background: rgba(59, 130, 246, 0.1); color: var(--accent-secondary); border: 1px solid rgba(59, 130, 246, 0.2); }}
.badge.short::before {{ background: var(--accent-secondary); box-shadow: 0 0 8px var(--accent-secondary); }}
.badge.cons    {{ background: var(--warning-bg); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.2); }}
.badge.cons::before {{ background: var(--warning); box-shadow: 0 0 8px var(--warning); }}
.badge.reject  {{ background: var(--danger-bg); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.2); }}
.badge.reject::before {{ background: var(--danger); box-shadow: 0 0 8px var(--danger); }}

/* Section headings */
h2.section {{ 
    font-family: 'Space Grotesk', sans-serif !important; font-size: 13px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.15em; color: var(--text-primary); 
    margin: 48px 0 24px; display: flex; align-items: center; gap: 12px;
}}
h2.section::before {{
    content: ''; width: 4px; height: 16px; background: var(--accent-secondary); border-radius: 4px;
}}

/* Linear Progress Bar */
.bar-track {{ background: var(--border-light); border-radius: 999px; height: 8px; overflow: hidden; }}
.bar-fill  {{ height: 100%; background: var(--accent-gradient); border-radius: 999px; position: relative; }}

/* Chips */
.chip {{
    display: inline-flex; align-items: center; padding: 6px 14px; border-radius: var(--radius-sm);
    background: var(--bg-tertiary); color: var(--text-secondary); border: 1px solid var(--border); 
    font-size: 13px; font-weight: 500; margin: 4px 6px 4px 0;
}}
.chip:hover {{ border-color: var(--border-light); color: var(--text-primary); background: var(--bg-tertiary); }}
.chip.miss {{ color: var(--danger); border-color: rgba(239, 68, 68, 0.2); background: var(--danger-bg); }}
.chip.match {{ color: var(--success); border-color: rgba(16, 185, 129, 0.2); background: var(--success-bg); }}

/* Recruiter summary block */
.summary-card {{
    background: var(--bg-glass); border: 1px solid var(--border); border-radius: var(--radius-xl);
    padding: 32px; color: var(--text-primary); line-height: 1.7; font-size: 16px;
    position: relative; overflow: hidden; backdrop-filter: blur(12px);
    box-shadow: {glass_shadow};
}}
.summary-card::before {{ content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 4px; background: var(--accent-gradient); }}

/* Streamlit Override: Inputs & Uploader */
.stTextArea textarea, .stTextInput input, .stSelectbox > div > div {{
    background-color: {input_bg} !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important; color: var(--text-primary) !important; font-size: 15px !important;
    padding: 16px !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
    transition: all 0.3s ease !important;
}}
.stTextArea textarea::placeholder, .stTextInput input::placeholder {{
    color: var(--text-muted) !important; font-weight: 400 !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus, .stSelectbox > div > div:focus {{
    border-color: var(--accent-primary) !important; box-shadow: 0 0 0 1px var(--accent-primary), 0 4px 16px rgba(139, 92, 246, 0.15) !important;
    background-color: var(--bg-primary) !important;
}}

[data-testid="stFileUploader"] {{ background: transparent; padding: 0; }}
[data-testid="stFileUploader"] section {{ 
    border-radius: var(--radius-xl) !important; border: 2px dashed var(--border-light) !important;
    background-color: var(--bg-tertiary) !important; padding: 48px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
[data-testid="stFileUploader"] section:hover {{
    border-color: var(--accent-secondary) !important; background-color: var(--success-bg) !important;
    transform: scale(1.01) translateY(-2px); box-shadow: 0 10px 30px rgba(59, 130, 246, 0.1) !important;
}}
[data-testid="stFileUploaderDropzone"] div[data-testid="stMarkdownContainer"] p {{
    color: var(--text-primary) !important; font-weight: 600 !important; font-size: 15px !important;
}}
[data-testid="stFileUploaderDropzone"] small {{
    color: var(--text-secondary) !important; font-size: 13px !important;
}}
[data-testid="stFileUploaderDropzone"] svg {{
    stroke: var(--text-secondary) !important; fill: var(--text-secondary) !important;
}}

/* Streamlit Override: Buttons */
.stButton > button {{
    background: var(--bg-glass); color: var(--text-primary) !important; 
    border: 1px solid var(--border-light) !important; border-radius: var(--radius-md) !important;
    font-weight: 600 !important; letter-spacing: 0.02em !important; padding: 16px 28px !important;
    width: 100% !important; font-size: 15px !important;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease !important;
}}
.stButton > button:hover {{ border-color: var(--accent-primary) !important; background: var(--bg-tertiary); transform: translateY(-2px) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;}}

/* Primary Button Override for "Analyse candidates" */
button[kind="primary"] {{
    background: var(--accent-gradient) !important; color: #fff !important;
    border: none !important; box-shadow: 0 4px 20px var(--accent-glow) !important;
}}
button[kind="primary"]:hover {{ box-shadow: 0 8px 30px var(--accent-glow) !important; border: none !important; }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 12px; background: transparent; border-bottom: 1px solid var(--border); padding-bottom: 0; }}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important; border: none !important; border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; padding: 16px 20px !important; color: var(--text-secondary) !important;
    font-weight: 600 !important; font-size: 15px !important;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: var(--text-primary) !important; }}
.stTabs [aria-selected="true"] {{ color: var(--text-primary) !important; border-bottom: 2px solid var(--accent-primary) !important; }}

/* Expander */
.streamlit-expanderHeader {{
    background: var(--bg-glass) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important; color: var(--text-primary) !important;
    font-weight: 600 !important; padding: 20px 24px !important; backdrop-filter: blur(10px);
}}
[data-testid="stExpanderDetails"] {{
    border: 1px solid var(--border); border-top: none; border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    background: var(--bg-primary); padding: 32px;
}}

/* Hide default elements */
footer, header, #MainMenu {{ visibility: hidden; }}
.stDataFrame {{ border-radius: var(--radius-lg); border: 1px solid var(--border); background: var(--bg-glass); }}
.stProgress > div > div > div > div {{ background: var(--accent-gradient) !important; }}

/* Custom Scrollbar */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border-hover); border-radius: 999px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}
</style>
"""


def badge_for(rec: str) -> str:
    cls = {
        "Strong Hire": "strong",
        "Shortlist":   "short",
        "Consider":    "cons",
        "Reject":      "reject",
    }.get(rec, "short")
    return f'<span class="badge {cls}">{rec}</span>'


def metric_card(label: str, value: str, sub: str = "", icon: str = "") -> str:
    icon_html = f'<div class="metric-icon">{icon}</div>' if icon else ""
    return (
        f'<div class="metric-card">'
        f'  <div class="metric-header">'
        f'    <div class="label">{label}</div>'
        f'    {icon_html}'
        f'  </div>'
        f'  <div class="value">{value}</div>'
        f'  <div class="sub">{sub}</div>'
        f'</div>'
    )


def bar(score10: float) -> str:
    pct = max(0, min(100, int(score10 * 10)))
    return f'<div class="bar-track"><div class="bar-fill" style="width:{pct}%;"></div></div>'


def circular_progress(score: float, max_score: float = 100, size: int = 120) -> str:
    pct = max(0, min(100, (score / max_score) * 100))
    stroke_dasharray = f"{pct}, 100"
    
    # Color based on score
    color = "var(--success)" if pct >= 80 else ("var(--warning)" if pct >= 60 else "var(--danger)")
    
    return f'''
    <div style="width: {size}px; height: {size}px; position: relative;">
        <svg viewBox="0 0 36 36" class="circular-chart">
            <path class="circle-bg"
                d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path class="circle"
                stroke="{color}"
                stroke-dasharray="{stroke_dasharray}"
                d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <text x="18" y="20.35" class="percentage">{score:.0f}</text>
        </svg>
    </div>
    '''
