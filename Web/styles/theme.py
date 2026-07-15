"""
Estilos y temas CSS de la aplicación
"""

PAGE_CONFIG_STYLE = """
<style>
:root {
    color-scheme: dark;
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
body { background: #070b14; }
.game-card { position: relative; border-radius: 18px; overflow: hidden; transition: transform .25s ease, box-shadow .25s ease; box-shadow: 0 14px 45px rgba(0,0,0,0.18); }
.game-card img { width: 100%; height: 180px; object-fit: cover; transition: transform .35s ease; display: block; }
.game-card:hover { transform: translateY(-8px); box-shadow: 0 22px 56px rgba(0,0,0,0.28); }
.game-card:hover img { transform: scale(1.05); }
.game-card .meta { padding-top: 10px; color: #cbd5e1; font-size: 13px; }
.game-card__overlay { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(12, 18, 36, 0.95); color: #f8fafc; padding: 14px 16px; opacity: 0; transform: translateY(16px); transition: opacity .25s ease, transform .25s ease; font-size: 12px; line-height: 1.5; z-index: 2; }
.game-card:hover .game-card__overlay { opacity: 1; transform: translateY(0); }
.badge { position: absolute; right: 12px; top: 12px; padding: 5px 10px; border-radius: 999px; font-weight: 700; font-size: 11px; letter-spacing: .6px; text-transform: uppercase; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(155,92,255,0.7);} 70% { box-shadow: 0 0 0 10px rgba(155,92,255,0); } 100% { box-shadow: 0 0 0 0 rgba(155,92,255,0); } }
.badge.pulse { animation: pulse 2s infinite; }
.dashboard-card { position: relative; border-radius: 18px; overflow: hidden; transition: transform .2s ease, box-shadow .2s ease; box-shadow: 0 16px 42px rgba(0,0,0,0.16); }
.dashboard-card img { width: 100%; height: 130px; object-fit: cover; transition: transform .3s ease; display: block; }
.dashboard-card:hover { transform: translateY(-5px); }
.dashboard-card__overlay { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(15,23,42,0.95); color: #f8fafc; padding: 12px 14px; opacity: 0; transform: translateY(14px); transition: opacity .2s ease, transform .2s ease; font-size: 12px; line-height: 1.4; z-index: 2; }
.dashboard-card:hover .dashboard-card__overlay { opacity: 1; transform: translateY(0); }
.hero-banner { background: linear-gradient(135deg, #0b1220 0%, #131b2f 100%); border-radius: 28px; padding: 34px; margin-bottom: 26px; box-shadow: 0 28px 80px rgba(0,0,0,0.26); border: 1px solid rgba(148,163,184,0.14); }
.hero-banner .hero-left { max-width: 680px; }
.hero-banner .eyebrow { display: inline-flex; align-items: center; gap: 10px; margin-bottom: 16px; color: #a78bfa; letter-spacing: 1px; font-weight: 700; text-transform: uppercase; font-size: 0.82rem; }
.hero-banner h1 { margin: 0 0 14px 0; font-size: clamp(2.4rem, 2.8vw, 3.4rem); line-height: 1.04; color: #f8fafc; }
.hero-banner p { margin: 0; color: #cbd5e1; font-size: 1.02rem; max-width: 620px; }
.hero-right { display: grid; gap: 16px; grid-template-columns: repeat(1, minmax(180px, 1fr)); margin-top: 24px; }
.metric-card { background: rgba(255,255,255,0.06); border: 1px solid rgba(148,163,184,0.15); border-radius: 20px; padding: 22px 24px; min-height: 112px; color: #f8fafc; }
.metric-label { color: #94a3b8; font-size: 0.9rem; margin-bottom: 8px; }
.metric-value { font-size: 1.75rem; font-weight: 700; line-height: 1.1; }
.detail-hero { background: linear-gradient(135deg, rgba(15,23,42,0.96) 0%, rgba(15,23,42,0.98) 100%); border-radius: 24px; padding: 28px; display: grid; grid-template-columns: 320px minmax(0,1fr); gap: 26px; margin-bottom: 24px; box-shadow: 0 24px 60px rgba(0,0,0,0.24); }
.detail-hero img { border-radius: 20px; width: 100%; height: auto; object-fit: cover; }
.detail-hero h1 { margin: 0 0 12px 0; font-size: 2.6rem; color: #f8fafc; }
.detail-hero p { margin: 6px 0 0 0; color: #cbd5e1; line-height: 1.7; }
.tag-bar { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.tag-chip { background: rgba(99,102,241,0.16); color: #e0e7ff; padding: 10px 14px; border-radius: 999px; font-size: 0.82rem; display: inline-flex; align-items: center; }
.section-panel { background: rgba(255,255,255,0.05); border: 1px solid rgba(148,163,184,0.14); border-radius: 20px; padding: 22px; margin-bottom: 18px; }
.section-panel h3 { margin: 0 0 12px 0; color: #f8fafc; }
.streamlit-expanderHeader, .st-bf { color: #f8fafc !important; }
@media (min-width: 900px) { .hero-banner { display: grid; grid-template-columns: 1.7fr 1fr; gap: 32px; align-items: center; } .hero-right { margin-top: 0; } }
</style>
"""
