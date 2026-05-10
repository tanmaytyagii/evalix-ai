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

h1, h2, h3, .metric-card .value, .hero h1 {{
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

/* Hero Section */
.hero {{
    position: relative; background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: var(--radius-xl); padding: 56px 64px; margin-bottom: 48px;
    overflow: hidden; box-shadow: {glass_shadow};
    display: flex; justify-content: space-between; align-items: center; gap: 48px;
    backdrop-filter: blur(24px);
}}
.hero::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent-gradient); opacity: 0.8;
}}
.hero-content {{ position: relative; z-index: 10; max-width: 600px; flex: 1; }}
.hero h1 {{ 
    margin: 0; font-size: 48px; font-weight: 700; letter-spacing: -0.04em; 
    line-height: 1.1; color: var(--text-primary);
}}
.gradient-text {{
    background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.hero p {{ 
    color: var(--text-secondary); margin: 20px 0 0; font-size: 17px; line-height: 1.6; font-weight: 400;
}}
.hero-badges {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 32px; }}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px;
    background: var(--bg-primary); border: 1px solid var(--border);
    border-radius: var(--radius-md); font-size: 13px; font-weight: 500;
    color: var(--text-primary); box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s ease;
}}
.hero-badge:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-color: var(--border-hover); }}

/* Hero Illustration */
.hero-illustration {{
    position: relative; width: 380px; height: 280px; display: flex; align-items: center; justify-content: center;
}}
.illust-bg-glow {{
    position: absolute; width: 200px; height: 200px; background: rgba(59, 130, 246, 0.15);
    border-radius: 50%; filter: blur(40px); z-index: 1;
}}
.illust-resume {{
    position: relative; z-index: 2; width: 260px; background: var(--bg-secondary);
    border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 24px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.08); display: flex; flex-direction: column; gap: 20px;
}}
.illust-header {{ display: flex; gap: 16px; align-items: center; }}
.illust-avatar {{ width: 48px; height: 48px; border-radius: 50%; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); }}
.illust-lines {{ display: flex; flex-direction: column; gap: 8px; flex: 1; }}
.illust-lines.mt {{ margin-top: 16px; }}
.illust-line {{ height: 8px; border-radius: 4px; background: var(--bg-tertiary); }}
.illust-line.w-1 {{ width: 100%; }}
.illust-line.w-2 {{ width: 60%; }}
.illust-line.w-3 {{ width: 80%; }}
.illust-stars {{ color: #f59e0b; font-size: 18px; letter-spacing: 2px; }}
.illust-badge {{
    position: absolute; bottom: -20px; right: -20px; width: 80px; height: 80px;
    background: var(--accent-gradient); border-radius: 50%; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3); border: 4px solid var(--bg-secondary);
}}
.illust-badge svg {{ width: 40px; height: 40px; color: white; }}

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
