"""
app.py
Local Food Wastage Management System — Streamlit App

Run from project root:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from datetime import date

DB_PATH = "database/food_wastage.db"

st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =================================================================
# DESIGN SYSTEM
# Bold color-blocked stat cards (like a restaurant admin dashboard),
# dark canvas, rounded cards, donut + bar charts, scroll-style carousel.
# =================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #141318;
    --bg-card: #1E1D24;
    --bg-card-2: #25232C;
    --cream: #F4F2F8;
    --muted: #918FA0;
    --border: #322F3A;

    --c-green: #34D399;
    --c-purple: #C084FC;
    --c-blue: #818CF8;
    --c-coral: #FB7166;
    --c-amber: #FBBF24;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Fraunces', serif !important; font-weight: 700 !important; letter-spacing: -0.01em; }

[data-testid="stAppViewContainer"] { background: var(--bg); }

@keyframes fadeUp { from { opacity:0; transform: translateY(12px);} to {opacity:1; transform: translateY(0);} }
.fade-up { animation: fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) both; }
.d1{animation-delay:.05s}.d2{animation-delay:.1s}.d3{animation-delay:.15s}.d4{animation-delay:.2s}.d5{animation-delay:.25s}

/* ---------- Topbar ---------- */
.topbar {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 1.4rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border);
}
.welcome-title { font-family:'Fraunces',serif; font-size:1.5rem; font-weight:700; color:var(--cream); }
.welcome-sub { color: var(--muted); font-size: 0.88rem; margin-top:2px; }

/* ---------- Bold stat cards ---------- */
.stat-card {
    border-radius: 16px; padding: 1.2rem 1.3rem; height: 100%;
    position: relative; overflow: hidden;
    transition: transform 0.25s cubic-bezier(0.16,1,0.3,1), box-shadow 0.25s;
}
.stat-card:hover { transform: translateY(-5px); box-shadow: 0 14px 30px -10px rgba(0,0,0,0.5); }
.stat-icon {
    width: 38px; height: 38px; border-radius: 10px; background: rgba(0,0,0,0.18);
    display:flex; align-items:center; justify-content:center; font-size:1.1rem; margin-bottom: 0.8rem;
}
.stat-value { font-family:'Fraunces',serif; font-size: 1.85rem; font-weight: 700; line-height:1; }
.stat-label { font-size: 0.83rem; font-weight: 600; margin-top: 0.35rem; opacity: 0.92; }

.card-green  { background: linear-gradient(135deg, #34D399, #10B981); color: #06281C; }
.card-purple { background: linear-gradient(135deg, #C084FC, #A855F7); color: #2B0A47; }
.card-blue   { background: linear-gradient(135deg, #818CF8, #6366F1); color: #1B1750; }
.card-coral  { background: linear-gradient(135deg, #FB923C, #FB7166); color: #4A1106; }

/* ---------- Panels ---------- */
.panel-title { font-family:'Fraunces',serif; font-size: 1.15rem; font-weight: 700; color: var(--cream); }
.panel-sub { color: var(--muted); font-size: 0.82rem; margin-top: 1px; margin-bottom: 0.5rem; }

div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.1rem 1.2rem 0.6rem 1.2rem;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:has(.stat-card) {
    background: transparent; border: none; padding: 0;
}

/* ---------- Legend rows ---------- */
.legend-row { display:flex; align-items:center; gap:0.6rem; margin-bottom:0.55rem; font-size:0.86rem; }
.legend-dot { width:9px; height:9px; border-radius:50%; flex-shrink:0; }
.legend-label { color: var(--cream); flex:1; }
.legend-pct { color: var(--muted); font-weight:600; }

/* ---------- Carousel cards ---------- */
.carousel-wrap { display:flex; gap:1rem; overflow-x:auto; padding-bottom: 0.5rem; scrollbar-width: thin; }
.carousel-wrap::-webkit-scrollbar { height: 6px; }
.carousel-wrap::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
.food-card {
    min-width: 220px; background: var(--bg-card-2); border: 1px solid var(--border); border-radius: 14px;
    overflow: hidden; flex-shrink: 0; transition: transform 0.2s ease;
}
.food-card:hover { transform: translateY(-3px); }
.food-card-art {
    height: 110px; display:flex; align-items:center; justify-content:center; font-size: 2.6rem;
}
.food-card-body { padding: 0.75rem 0.9rem 0.9rem 0.9rem; }
.food-card-name { color: var(--cream); font-weight: 600; font-size: 0.92rem; }
.food-card-meta { color: var(--muted); font-size: 0.78rem; margin-top: 2px; }
.food-card-badge {
    display:inline-block; margin-top: 0.5rem; padding: 0.15rem 0.55rem; border-radius: 999px;
    font-size: 0.72rem; font-weight: 700;
}

/* ---------- Row cards (claims/listings) ---------- */
.row-card {
    background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
    padding: 0.85rem 1.1rem; margin-bottom: 0.5rem;
    display:flex; justify-content:space-between; align-items:center;
    transition: transform 0.2s ease, border-color 0.2s;
}
.row-card:hover { transform: translateX(3px); border-color: #4A4658; }
.row-title { color: var(--cream); font-weight: 600; font-size: 0.95rem; }
.row-sub { color: var(--muted); font-size: 0.84rem; }

.pill { display:inline-flex; align-items:center; gap:0.3rem; padding:0.2rem 0.65rem; border-radius:999px; font-size:0.76rem; font-weight:700; }
.pill-urgent { background: rgba(251,113,102,0.18); color: #FB7166; }
.pill-soon   { background: rgba(251,191,36,0.18); color: #FBBF24; }
.pill-fresh  { background: rgba(52,211,153,0.18); color: #34D399; }
.pill-completed { background: rgba(52,211,153,0.18); color: #34D399; }
.pill-pending    { background: rgba(251,191,36,0.18); color: #FBBF24; }
.pill-cancelled  { background: rgba(145,143,160,0.18); color: #918FA0; }

.section-eyebrow {
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.5rem;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] { background: #18171D; border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] .stRadio label { font-size: 0.95rem; }

/* ---------- Dataframe / buttons / tabs ---------- */
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow:hidden; }
.stButton button, .stFormSubmitButton button { border-radius: 10px; font-weight: 700; border: 1px solid var(--border); }
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, #FB923C, #FB7166); border: none; color: #2A0B04;
}
.stTabs [data-baseweb="tab"] { font-weight: 700; }
.stTabs [aria-selected="true"] { color: #FB7166 !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: #FB7166 !important; }
hr { border-color: var(--border) !important; }

.empty-state { text-align:center; padding:2.2rem 1rem; color:var(--muted); border:1px dashed var(--border); border-radius:14px; }

/* ---------- New topbar: search + bell + avatar ---------- */
.search-box {
    background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px;
    padding: 0.55rem 1rem; color: var(--muted); font-size: 0.85rem;
}
.bell-icon {
    width:38px; height:38px; border-radius:50%; background: var(--bg-card); border:1px solid var(--border);
    display:flex; align-items:center; justify-content:center; font-size:1rem;
}
.avatar-chip { display:flex; align-items:center; gap:0.6rem; justify-content:flex-end; }
.avatar-circle {
    width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg,#FB923C,#FB7166);
    display:flex; align-items:center; justify-content:center; font-weight:700; color:#2A0B04; flex-shrink:0;
}
.avatar-name { color: var(--cream); font-weight:600; font-size:0.88rem; }
.avatar-role { color: var(--muted); font-size:0.75rem; }

/* ---------- Sidebar nav: highlighted active item ---------- */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    display:flex; align-items:center; width:100%; padding:0.55rem 0.8rem; border-radius:10px;
    margin-bottom:0.2rem; transition: background 0.15s;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(255,255,255,0.05); }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, #FBBF24, #FB923C) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color:#2A0B04 !important; font-weight:700 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] input { display:none; }
</style>
""", unsafe_allow_html=True)


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


conn = get_connection()

FOOD_EMOJI = {
    "Rice": "🍚", "Dal": "🍲", "Chapati": "🫓", "Mixed Vegetable Curry": "🥘",
    "Paneer Tikka": "🧀", "Chicken Curry": "🍛", "Vegetable Biryani": "🍛",
    "Sandwiches": "🥪", "Fruit Salad": "🥗", "Bread Loaves": "🍞",
    "Milk Packets": "🥛", "Sweets Box": "🍬", "Idli Sambar": "🍥",
    "Pasta": "🍝", "Salad Bowl": "🥗", "Soup": "🍜", "Pulao": "🍚",
    "Khichdi": "🍲", "Vegetable Wrap": "🌯", "Egg Curry": "🍳",
}


def freshness_pill(expiry_str):
    try:
        expiry = pd.to_datetime(expiry_str).date()
    except Exception:
        return ""
    days = (expiry - date.today()).days
    if days < 0:
        return '<span class="pill pill-urgent">Expired</span>'
    elif days <= 2:
        return f'<span class="pill pill-urgent">{days}d left</span>'
    elif days <= 5:
        return f'<span class="pill pill-soon">{days}d left</span>'
    else:
        return f'<span class="pill pill-fresh">{days}d left</span>'


def status_pill(status):
    cls = {"Completed": "pill-completed", "Pending": "pill-pending", "Cancelled": "pill-cancelled"}.get(status, "pill-pending")
    return f'<span class="pill {cls}">{status}</span>'


# =================================================================
# SIDEBAR NAVIGATION
# =================================================================
with st.sidebar:
    st.markdown(
        '<div style="font-family:\'Fraunces\',serif; font-size:1.3rem; font-weight:700; '
        'color:#F4F2F8; padding: 0.5rem 0 1.2rem 0;">🍲 Food Wastage<br/>Management</div>',
        unsafe_allow_html=True
    )
    menu = st.radio(
        "Go to",
        ["Home", "View Listings", "Filter & Search", "SQL Insights",
         "Manage Listings (CRUD)", "Manage Claims", "Contact Directory"],
        label_visibility="collapsed",
    )
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.caption("A platform connecting surplus food providers with people who need it.")

# =================================================================
# HOME — dashboard style
# =================================================================
if menu == "Home":
    top_l, top_r = st.columns([2, 1.4])
    with top_l:
        st.markdown("""
        <div class="welcome-title">Welcome back 👋</div>
        <div class="welcome-sub">Here's what's happening across the platform today</div>
        """, unsafe_allow_html=True)
    with top_r:
        st.markdown("""
        <div style="display:flex; justify-content:flex-end; align-items:center; gap:0.8rem; height:100%;">
            <div class="search-box">🔍 Search...</div>
            <div class="bell-icon">🔔</div>
            <div class="avatar-chip">
                <div class="avatar-circle">A</div>
                <div>
                    <div class="avatar-name">Admin</div>
                    <div class="avatar-role">Manager</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<hr style="border-color:var(--border); margin-top:0.9rem; margin-bottom:1.4rem;"/>', unsafe_allow_html=True)

    providers_count = pd.read_sql("SELECT COUNT(*) AS c FROM providers", conn)["c"][0]
    receivers_count = pd.read_sql("SELECT COUNT(*) AS c FROM receivers", conn)["c"][0]
    listings_count = pd.read_sql("SELECT COUNT(*) AS c FROM food_listings", conn)["c"][0]
    total_qty = pd.read_sql("SELECT SUM(Quantity) AS s FROM food_listings", conn)["s"][0] or 0

    c1, c2, c3, c4 = st.columns(4)
    stat_defs = [
        (c1, "card-green", "🏪", f"{providers_count}", "Total Providers", "d1"),
        (c2, "card-purple", "🤝", f"{receivers_count}", "Total Receivers", "d2"),
        (c3, "card-blue", "📦", f"{listings_count}", "Active Listings", "d3"),
        (c4, "card-coral", "⚖️", f"{total_qty:,}", "Units Available", "d4"),
    ]
    for col, cls, icon, value, label, delay in stat_defs:
        with col:
            st.markdown(f"""
            <div class="stat-card {cls} fade-up {delay}">
                <div class="stat-icon">{icon}</div>
                <div class="stat-value">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1, 1.15])

    # ----- Donut: claim status breakdown -----
    with left:
        h1, h2 = st.columns([2, 1])
        with h1:
            st.markdown(
                '<div class="panel-title">Claim Status</div>'
                '<div class="panel-sub">All-time breakdown</div>',
                unsafe_allow_html=True
            )
        with h2:
            st.selectbox("", ["Monthly", "Weekly", "All-time"], label_visibility="collapsed", key="claim_period")

        status_counts = pd.read_sql("SELECT Status, COUNT(*) AS c FROM claims GROUP BY Status ORDER BY c DESC", conn)
        total_claims = status_counts["c"].sum()
        colors_map = {"Completed": "#34D399", "Pending": "#FBBF24", "Cancelled": "#FB7166"}
        colors = [colors_map.get(s, "#818CF8") for s in status_counts["Status"]]

        fig = go.Figure(data=[go.Pie(
            labels=status_counts["Status"], values=status_counts["c"], hole=0.68,
            marker=dict(colors=colors, line=dict(color="#1E1D24", width=3)),
            textinfo="none", sort=False,
        )])
        completed_pct = round(status_counts.loc[status_counts["Status"] == "Completed", "c"].sum() / total_claims * 100) if total_claims else 0
        fig.update_layout(
            showlegend=False, height=230, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text=f"<b>{completed_pct}%</b>", x=0.5, y=0.5, font=dict(size=26, color="#F4F2F8"), showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        legend_html = ""
        for _, row in status_counts.iterrows():
            pct = round(row["c"] / total_claims * 100, 1) if total_claims else 0
            color = colors_map.get(row["Status"], "#818CF8")
            legend_html += f"""
            <div class="legend-row">
                <span class="legend-dot" style="background:{color};"></span>
                <span class="legend-label">{row['Status']}</span>
                <span class="legend-pct">{pct}%</span>
            </div>
            """
        st.markdown(legend_html, unsafe_allow_html=True)

    # ----- Bar chart: listings per city -----
    with right:
        h1, h2 = st.columns([2, 1])
        with h1:
            st.markdown(
                '<div class="panel-title">Listings by City</div>'
                '<div class="panel-sub">Where food is available right now</div>',
                unsafe_allow_html=True
            )
        with h2:
            st.selectbox("", ["Weekly", "Monthly", "All-time"], label_visibility="collapsed", key="city_period")

        by_city = pd.read_sql("""
            SELECT Location, COUNT(*) AS Listings
            FROM food_listings GROUP BY Location ORDER BY Listings DESC LIMIT 8
        """, conn)
        max_idx = by_city["Listings"].idxmax()
        bar_colors = ["#FBBF24" if i == max_idx else "#3A3744" for i in by_city.index]

        fig2 = go.Figure(data=[go.Bar(
            x=by_city["Location"], y=by_city["Listings"],
            marker=dict(color=bar_colors, cornerradius=8),
            text=by_city["Listings"], textposition="outside",
            textfont=dict(color="#F4F2F8", size=12),
        )])
        fig2.update_layout(
            height=300, margin=dict(t=30, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, color="#918FA0"),
            yaxis=dict(showgrid=True, gridcolor="#2A2731", color="#918FA0", showticklabels=False),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.write("")

    # ----- Carousel: expiring soon -----
    st.markdown('<div class="section-eyebrow fade-up">Expiring soon — claim before it is gone</div>', unsafe_allow_html=True)
    urgent = pd.read_sql("""
        SELECT fl.Food_Name, fl.Quantity, fl.Expiry_Date, fl.Location, p.Name AS Provider
        FROM food_listings fl
        LEFT JOIN claims c ON fl.Food_ID = c.Food_ID AND c.Status = 'Completed'
        JOIN providers p ON fl.Provider_ID = p.Provider_ID
        WHERE c.Claim_ID IS NULL
          AND DATE(fl.Expiry_Date) BETWEEN DATE('now') AND DATE('now', '+5 day')
        ORDER BY fl.Expiry_Date ASC
        LIMIT 10
    """, conn)

    if urgent.empty:
        st.markdown('<div class="empty-state">Nothing urgent right now — all upcoming listings are claimed.</div>', unsafe_allow_html=True)
    else:
        bg_colors = ["#3A2A1E", "#1E2A3A", "#2A1E3A", "#1E3A2E", "#3A1E2A"]
        cards_html = '<div class="carousel-wrap fade-up">'
        for i, row in urgent.iterrows():
            emoji = FOOD_EMOJI.get(row["Food_Name"], "🍽️")
            pill = freshness_pill(row["Expiry_Date"])
            bg = bg_colors[i % len(bg_colors)]
            cards_html += f"""
            <div class="food-card">
                <div class="food-card-art" style="background:{bg};">{emoji}</div>
                <div class="food-card-body">
                    <div class="food-card-name">{row['Food_Name']}</div>
                    <div class="food-card-meta">{row['Provider']} · {row['Location']}</div>
                    <div class="food-card-meta">{row['Quantity']} units</div>
                    {pill}
                </div>
            </div>
            """
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

# =================================================================
# VIEW LISTINGS
# =================================================================
elif menu == "View Listings":
    st.markdown('<div class="section-eyebrow fade-up">Browse</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="fade-up d1">All Food Listings</h2>', unsafe_allow_html=True)

    df = pd.read_sql("SELECT * FROM food_listings ORDER BY Expiry_Date ASC", conn)
    st.caption(f"{len(df)} listings on the platform")
    st.dataframe(df, use_container_width=True, height=520)

# =================================================================
# FILTER & SEARCH
# =================================================================
elif menu == "Filter & Search":
    st.markdown('<div class="section-eyebrow fade-up">Find what you need</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="fade-up d1">Filter Food Listings</h2>', unsafe_allow_html=True)

    cities = ["All"] + sorted(pd.read_sql("SELECT DISTINCT Location FROM food_listings", conn)["Location"].dropna().tolist())
    providers_list = ["All"] + sorted(pd.read_sql("SELECT DISTINCT Provider_Type FROM food_listings", conn)["Provider_Type"].dropna().tolist())
    food_types = ["All"] + sorted(pd.read_sql("SELECT DISTINCT Food_Type FROM food_listings", conn)["Food_Type"].dropna().tolist())
    meal_types = ["All"] + sorted(pd.read_sql("SELECT DISTINCT Meal_Type FROM food_listings", conn)["Meal_Type"].dropna().tolist())

    c1, c2, c3, c4 = st.columns(4)
    city = c1.selectbox("City", cities)
    provider_type = c2.selectbox("Provider Type", providers_list)
    food_type = c3.selectbox("Food Type", food_types)
    meal_type = c4.selectbox("Meal Type", meal_types)

    query = "SELECT * FROM food_listings WHERE 1=1"
    params = []
    if city != "All":
        query += " AND Location = ?"; params.append(city)
    if provider_type != "All":
        query += " AND Provider_Type = ?"; params.append(provider_type)
    if food_type != "All":
        query += " AND Food_Type = ?"; params.append(food_type)
    if meal_type != "All":
        query += " AND Meal_Type = ?"; params.append(meal_type)
    query += " ORDER BY Expiry_Date ASC"

    result = pd.read_sql(query, conn, params=params)
    st.write("")
    st.caption(f"**{len(result)}** listing(s) found")
    st.dataframe(result, use_container_width=True, height=480)

# =================================================================
# SQL INSIGHTS
# =================================================================
elif menu == "SQL Insights":
    st.markdown('<div class="section-eyebrow fade-up">Analysis</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="fade-up d1">SQL Query Insights</h2>', unsafe_allow_html=True)
    st.caption("15 queries covering providers, listings, claims, and distribution trends.")

    QUERIES = {
        "Q1. Providers & receivers per city": """
            SELECT City, 'Provider' AS Role, COUNT(*) AS Count
            FROM providers GROUP BY City
            UNION ALL
            SELECT City, 'Receiver' AS Role, COUNT(*) AS Count
            FROM receivers GROUP BY City
            ORDER BY City, Role;
        """,
        "Q2. Provider type contributing most food (by quantity)": """
            SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
            FROM food_listings GROUP BY Provider_Type
            ORDER BY Total_Quantity DESC;
        """,
        "Q3. Contact info of providers in Pune": """
            SELECT Name, Type, Address, Contact
            FROM providers WHERE City = 'Pune';
        """,
        "Q4. Receivers who claimed the most food (top 10)": """
            SELECT r.Receiver_ID, r.Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            GROUP BY r.Receiver_ID ORDER BY Total_Claims DESC LIMIT 10;
        """,
        "Q5. Total quantity of food available from all providers": """
            SELECT SUM(Quantity) AS Total_Available_Quantity FROM food_listings;
        """,
        "Q6. City with the highest number of food listings": """
            SELECT Location, COUNT(*) AS Listing_Count
            FROM food_listings GROUP BY Location
            ORDER BY Listing_Count DESC LIMIT 1;
        """,
        "Q7. Most commonly available food types": """
            SELECT Food_Type, COUNT(*) AS Count
            FROM food_listings GROUP BY Food_Type ORDER BY Count DESC;
        """,
        "Q8. Number of claims made for each food item (top 10)": """
            SELECT fl.Food_ID, fl.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
            FROM food_listings fl LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
            GROUP BY fl.Food_ID ORDER BY Claim_Count DESC LIMIT 10;
        """,
        "Q9. Provider with highest number of Completed claims": """
            SELECT p.Provider_ID, p.Name, COUNT(*) AS Completed_Claims
            FROM claims c
            JOIN food_listings fl ON c.Food_ID = fl.Food_ID
            JOIN providers p ON fl.Provider_ID = p.Provider_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID ORDER BY Completed_Claims DESC LIMIT 1;
        """,
        "Q10. Percentage of claims by status": """
            SELECT Status, COUNT(*) AS Count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
            FROM claims GROUP BY Status;
        """,
        "Q11. Average quantity of food claimed per receiver (top 10)": """
            SELECT r.Receiver_ID, r.Name, ROUND(AVG(fl.Quantity), 2) AS Avg_Quantity_Claimed
            FROM claims c
            JOIN food_listings fl ON c.Food_ID = fl.Food_ID
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            GROUP BY r.Receiver_ID ORDER BY Avg_Quantity_Claimed DESC LIMIT 10;
        """,
        "Q12. Meal type claimed the most": """
            SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS Claim_Count
            FROM claims c JOIN food_listings fl ON c.Food_ID = fl.Food_ID
            GROUP BY fl.Meal_Type ORDER BY Claim_Count DESC;
        """,
        "Q13. Total quantity of food donated by each provider (top 10)": """
            SELECT p.Provider_ID, p.Name, SUM(fl.Quantity) AS Total_Donated
            FROM food_listings fl JOIN providers p ON fl.Provider_ID = p.Provider_ID
            GROUP BY p.Provider_ID ORDER BY Total_Donated DESC LIMIT 10;
        """,
        "Q14. Food expiring in next 3 days, still unclaimed": """
            SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date, fl.Location
            FROM food_listings fl
            LEFT JOIN claims c ON fl.Food_ID = c.Food_ID AND c.Status = 'Completed'
            WHERE c.Claim_ID IS NULL
              AND DATE(fl.Expiry_Date) BETWEEN DATE('now') AND DATE('now', '+3 day')
            ORDER BY fl.Expiry_Date ASC;
        """,
        "Q15. Provider type with highest claim completion rate": """
            SELECT p.Type AS Provider_Type, COUNT(*) AS Total_Claims,
                   SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) AS Completed_Claims,
                   ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Completion_Rate_Pct
            FROM claims c
            JOIN food_listings fl ON c.Food_ID = fl.Food_ID
            JOIN providers p ON fl.Provider_ID = p.Provider_ID
            GROUP BY p.Type ORDER BY Completion_Rate_Pct DESC;
        """,
    }

    query_choice = st.selectbox("Select a query to view", list(QUERIES.keys()))
    df = pd.read_sql(QUERIES[query_choice], conn)
    st.dataframe(df, use_container_width=True)

    if query_choice.startswith("Q2") or query_choice.startswith("Q7") or query_choice.startswith("Q12"):
        chart_col = df.columns[0]
        value_col = df.columns[-1]
        st.bar_chart(df.set_index(chart_col)[value_col], color="#FB7166")

    with st.expander("Show all 15 queries one after another"):
        for title, sql in QUERIES.items():
            st.markdown(f"**{title}**")
            st.dataframe(pd.read_sql(sql, conn), use_container_width=True)

# =================================================================
# CRUD — Manage Listings
# =================================================================
elif menu == "Manage Listings (CRUD)":
    st.markdown('<div class="section-eyebrow fade-up">Maintain the catalog</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="fade-up d1">Manage Food Listings</h2>', unsafe_allow_html=True)

    tab_add, tab_update, tab_delete = st.tabs(["➕ Add", "✏️ Update", "🗑️ Delete"])

    with tab_add:
        st.markdown("**Add a new food listing**")
        with st.form("add_form", clear_on_submit=True):
            next_id = pd.read_sql("SELECT MAX(Food_ID) AS m FROM food_listings", conn)["m"][0]
            next_id = int(next_id) + 1 if next_id else 1
            st.caption(f"New Food_ID will be: {next_id}")

            col_a, col_b = st.columns(2)
            food_name = col_a.text_input("Food Name")
            quantity = col_b.number_input("Quantity", min_value=1, step=1)

            col_c, col_d = st.columns(2)
            expiry_date = col_c.date_input("Expiry Date")
            provider_id = col_d.number_input("Provider ID", min_value=1, step=1)

            col_e, col_f = st.columns(2)
            provider_type = col_e.selectbox("Provider Type", ["Restaurant", "Grocery Store", "Supermarket", "Catering Service", "Bakery"])
            location = col_f.text_input("Location (City)")

            col_g, col_h = st.columns(2)
            food_type = col_g.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            meal_type = col_h.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])

            submitted = st.form_submit_button("Add Listing", type="primary")
            if submitted:
                if not food_name or not location:
                    st.error("Food Name and Location are required.")
                else:
                    conn.execute("""
                        INSERT INTO food_listings
                        (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (next_id, food_name, quantity, str(expiry_date), provider_id, provider_type, location, food_type, meal_type))
                    conn.commit()
                    st.success(f"Listing #{next_id} — {food_name} added.")
                    st.balloons()

    with tab_update:
        st.markdown("**Update an existing listing's quantity or expiry**")
        ids = pd.read_sql("SELECT Food_ID, Food_Name FROM food_listings ORDER BY Food_ID", conn)
        if ids.empty:
            st.markdown('<div class="empty-state">No listings available to update.</div>', unsafe_allow_html=True)
        else:
            options = {f"{row.Food_ID} — {row.Food_Name}": row.Food_ID for row in ids.itertuples()}
            choice = st.selectbox("Select listing", list(options.keys()))
            selected_id = options[choice]

            current = pd.read_sql("SELECT * FROM food_listings WHERE Food_ID = ?", conn, params=(selected_id,)).iloc[0]

            col1, col2 = st.columns(2)
            new_qty = col1.number_input("New Quantity", min_value=0, step=1, value=int(current["Quantity"]))
            new_expiry = col2.date_input("New Expiry Date", value=pd.to_datetime(current["Expiry_Date"]))

            if st.button("Update Listing", type="primary"):
                conn.execute("UPDATE food_listings SET Quantity = ?, Expiry_Date = ? WHERE Food_ID = ?",
                             (new_qty, str(new_expiry), selected_id))
                conn.commit()
                st.success(f"Listing #{selected_id} updated.")

    with tab_delete:
        st.markdown("**Delete a listing**")
        ids = pd.read_sql("SELECT Food_ID, Food_Name FROM food_listings ORDER BY Food_ID", conn)
        if ids.empty:
            st.markdown('<div class="empty-state">No listings available to delete.</div>', unsafe_allow_html=True)
        else:
            options = {f"{row.Food_ID} — {row.Food_Name}": row.Food_ID for row in ids.itertuples()}
            choice = st.selectbox("Select listing to delete", list(options.keys()), key="delete_select")
            selected_id = options[choice]

            if st.button("Delete Listing", type="primary"):
                conn.execute("DELETE FROM food_listings WHERE Food_ID = ?", (selected_id,))
                conn.commit()
                st.success(f"Listing #{selected_id} deleted.")

# =================================================================
# MANAGE CLAIMS
# =================================================================
elif menu == "Manage Claims":
    st.markdown('<div class="section-eyebrow fade-up">Track distribution</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="fade-up d1">Update Claim Status</h2>', unsafe_allow_html=True)

    claims_df = pd.read_sql("""
        SELECT c.Claim_ID, fl.Food_Name, r.Name AS Receiver_Name, c.Status, c.Timestamp
        FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        ORDER BY c.Claim_ID DESC
        LIMIT 12
    """, conn)

    for _, row in claims_df.iterrows():
        pill = status_pill(row["Status"])
        st.markdown(f"""
        <div class="row-card">
            <div>
                <div class="row-title">#{row['Claim_ID']} · {row['Food_Name']}</div>
                <div class="row-sub">→ {row['Receiver_Name']} · {row['Timestamp']}</div>
            </div>
            <div>{pill}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-eyebrow">Update a claim</div>', unsafe_allow_html=True)
    claim_ids = pd.read_sql("SELECT Claim_ID FROM claims ORDER BY Claim_ID", conn)["Claim_ID"].tolist()
    col1, col2, col3 = st.columns([2, 2, 1])
    selected_claim = col1.selectbox("Claim ID", claim_ids)
    new_status = col2.selectbox("New Status", ["Pending", "Completed", "Cancelled"])
    col3.write("")
    col3.write("")
    if col3.button("Update", type="primary"):
        conn.execute("UPDATE claims SET Status = ? WHERE Claim_ID = ?", (new_status, selected_claim))
        conn.commit()
        st.success(f"Claim #{selected_claim} updated to '{new_status}'.")

# =================================================================
# CONTACT DIRECTORY
# =================================================================
elif menu == "Contact Directory":
    st.markdown('<div class="section-eyebrow fade-up">Get in touch</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="fade-up d1">Contact Directory</h2>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Providers", "Receivers"])

    with tab1:
        city_filter = st.selectbox(
            "Filter by city",
            ["All"] + sorted(pd.read_sql("SELECT DISTINCT City FROM providers", conn)["City"].tolist()),
            key="prov_city"
        )
        q = "SELECT Name, Type, Address, City, Contact FROM providers"
        if city_filter != "All":
            q += " WHERE City = ?"
            st.dataframe(pd.read_sql(q, conn, params=(city_filter,)), use_container_width=True)
        else:
            st.dataframe(pd.read_sql(q, conn), use_container_width=True)

    with tab2:
        city_filter2 = st.selectbox(
            "Filter by city",
            ["All"] + sorted(pd.read_sql("SELECT DISTINCT City FROM receivers", conn)["City"].tolist()),
            key="recv_city"
        )
        q2 = "SELECT Name, Type, City, Contact FROM receivers"
        if city_filter2 != "All":
            q2 += " WHERE City = ?"
            st.dataframe(pd.read_sql(q2, conn, params=(city_filter2,)), use_container_width=True)
        else:
            st.dataframe(pd.read_sql(q2, conn), use_container_width=True)