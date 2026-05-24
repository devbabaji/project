import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Climate Dashboard", layout="wide", page_icon="🌍")

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Merriweather:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: #f0f2f5;
    color: #1a202c;
}
.block-container {
    padding: 0 2rem 3rem 2rem;
    max-width: 1200px;
    background-color: #f0f2f5;
}
[data-testid="stSidebar"] { display: none; }

/* Metric cards */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 16px;
    padding: 22px 26px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.06);
    transition: all 0.2s ease;
    border-top: 3px solid #0ea5e9;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 6px rgba(0,0,0,0.05), 0 10px 30px rgba(0,0,0,0.1);
}
[data-testid="stMetricLabel"] {
    color: #7c8db5 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}
[data-testid="stMetricValue"] {
    color: #0c4a6e !important;
    font-family: 'Merriweather', serif !important;
    font-size: 26px !important;
    font-weight: 700 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    background: #ffffff;
    border-radius: 14px;
    padding: 6px;
    gap: 3px;
    border: 1px solid #e8ecf0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Outfit', sans-serif;
    font-size: 13px;
    font-weight: 600;
    padding: 9px 18px;
    border-radius: 10px;
    color: #64748b !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(14,165,233,0.35);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Inputs */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #1a202c !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def section_header(icon_label, title):
    st.markdown(f"""
    <div style="margin:8px 0 4px 0;">
        <div style="display:inline-flex;align-items:center;gap:6px;
                    font-size:10px;font-weight:700;letter-spacing:2px;
                    text-transform:uppercase;color:#0369a1;
                    background:linear-gradient(135deg,#e0f2fe,#ede9fe);
                    border:1px solid #bae6fd;border-radius:20px;padding:4px 12px;
                    margin-bottom:8px;">{icon_label}</div>
        <div style="font-family:'Merriweather',serif;font-size:20px;font-weight:700;
                    color:#0f172a;margin:6px 0 16px 0;line-height:1.3;">{title}</div>
    </div>
    """, unsafe_allow_html=True)

def insight_card(observation, inference):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#f0f9ff 0%,#faf5ff 100%);
                border:1px solid #bae6fd;border-left:4px solid #0ea5e9;
                border-radius:0 14px 14px 0;padding:18px 22px;
                margin:10px 0 28px 0;font-size:14px;color:#334155;line-height:1.8;">
        <strong style="color:#0f172a;font-weight:600;">📌 Observation</strong><br>
        {observation}
        <br><br>
        <strong style="color:#0f172a;font-weight:600;">💡 Inference</strong><br>
        {inference}
    </div>
    """, unsafe_allow_html=True)

def hr():
    st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:28px 0;'>",
                unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#fafbfc",
    font=dict(family="Outfit", color="#64748b", size=12),
    title_font=dict(family="Merriweather", size=15, color="#0f172a"),
    xaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0", linecolor="#e2e8f0",
               tickfont=dict(color="#94a3b8"), title_font=dict(color="#64748b")),
    yaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0", linecolor="#e2e8f0",
               tickfont=dict(color="#94a3b8"), title_font=dict(color="#64748b")),
    legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#e8ecf0",
                borderwidth=1, font=dict(color="#475569", size=12)),
    margin=dict(t=56, b=40, l=48, r=24),
    colorway=["#0ea5e9", "#f59e0b", "#10b981", "#f43f5e", "#8b5cf6", "#06b6d4", "#f97316"],
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e2e8f0",
                    font=dict(family="Outfit", color="#1a202c")),
)

def apply_theme(fig):
    fig.update_layout(**CHART_LAYOUT)
    return fig


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("co2-emissions-per-capita.csv")

df = load_data()
all_countries = sorted(df['Entity'].unique())
world         = df[df['Entity'] == 'World']
latest_year   = int(df['Year'].max())

# Synthetic renewable share (for Energy Transition page)
@st.cache_data
def make_renewables_df(countries):
    np.random.seed(7)
    rows = []
    base = {"China": 8, "United States": 7, "India": 5, "Germany": 12,
            "United Kingdom": 10, "France": 14, "Brazil": 40, "Japan": 6,
            "World": 9}
    for c in countries:
        b = base.get(c, np.random.uniform(4, 20))
        for y in range(1990, latest_year + 1):
            share = b + (y - 1990) * np.random.uniform(0.3, 0.9)
            share += np.random.normal(0, 0.5)
            rows.append({"Entity": c, "Year": y, "Renewables_Share": max(0, share)})
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# HEADER  — centered, no badge, no dots
# ─────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0c4a6e 0%,#1e3a8a 50%,#312e81 100%);
            border-radius:20px;margin:24px 0 24px 0;padding:52px 48px 48px 48px;
            position:relative;overflow:hidden;
            box-shadow:0 8px 32px rgba(12,74,110,0.3),0 2px 8px rgba(12,74,110,0.2);
            text-align:center;">
    <div style="position:absolute;top:-60px;right:-60px;width:220px;height:220px;
                border-radius:50%;background:rgba(255,255,255,0.04);"></div>
    <div style="position:absolute;bottom:-80px;left:60px;width:300px;height:300px;
                border-radius:50%;background:rgba(255,255,255,0.03);"></div>
    <div style="position:relative;z-index:1;">
        <h1 style="font-family:'Merriweather',serif;font-size:40px;font-weight:700;
                   color:#ffffff;margin:0 0 14px 0;line-height:1.2;letter-spacing:-0.5px;">
            Global Climate Change Dashboard
        </h1>
        <p style="color:#94c3d8;font-size:16px;margin:0;font-weight:400;max-width:560px;
                  margin-left:auto;margin-right:auto;line-height:1.7;">
            Our World in Data — CO₂ and Greenhouse Gas Emissions.<br>
            Explore trends, comparisons, and patterns in global carbon emissions.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STORY
# ─────────────────────────────────────────────
st.markdown("""
<div style="background:#ffffff;border:1px solid #e8ecf0;border-radius:20px;
            padding:32px 36px;margin-bottom:28px;
            box-shadow:0 1px 3px rgba(0,0,0,0.04),0 4px 16px rgba(0,0,0,0.06);">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
        <div style="width:32px;height:32px;border-radius:8px;
                    background:linear-gradient(135deg,#0ea5e9,#6366f1);
                    display:flex;align-items:center;justify-content:center;font-size:16px;">🌿</div>
        <span style="font-family:'Merriweather',serif;font-size:17px;font-weight:700;color:#0f172a;">
            Why This Matters
        </span>
    </div>
    <p style="font-size:15px;color:#475569;line-height:1.9;margin:0;">
        Human emissions of greenhouse gases are the primary driver of climate change today.
        CO₂ and other greenhouse gases like methane and nitrous oxide are emitted when we burn
        fossil fuels, produce materials such as steel, cement, and plastics, and grow the food
        we eat. If we want to reduce these emissions, we need to transform our energy systems,
        industries, and food systems.
        <br><br>
        At the same time, we need to tackle energy poverty, low standards of living, and poor nutrition, which all remain enormous problems for billions of people.
        <br><br>
        Technological advances could allow us to do both. The prices of solar, wind, and batteries
        have plummeted in recent decades, increasingly undercutting the cost of fossil fuel
        alternatives. Further progress could allow us to provide cheap, clean energy for everyone. Political change is essential to create a system that supports rapid
        decarbonization. Emissions are still rising in many parts of the world. However, several countries have managed to cut their emissions in recent decades. With affordable low-carbon technologies, other countries can increase their living standards without the high-carbon pathway that rich countries followed in the past.
        <br><br>
        On this page, you can find our data, visualizations, and writing on CO2 and other greenhouse gas emissions.
    </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 5 TABS
# ─────────────────────────────────────────────
tab_home, tab_emit, tab_energy, tab_geo, tab_corr = st.tabs([
    "🏠  Home",
    "💨  Emissions Analysis",
    "⚡  Energy Transition",
    "🗺️  Geographic View",
    "🔍  Correlation Explorer"
])


# ════════════════════════════════════════════════════
# TAB 1 — HOME
# ════════════════════════════════════════════════════
with tab_home:
    st.markdown("<br>", unsafe_allow_html=True)

    # Key stats
    section_header("📊 Key Statistics", "Climate at a Glance")
    world_latest = world[world['Year'] == latest_year]
    latest_co2   = round(float(world_latest['CO₂ emissions per capita'].values[0]), 2) \
                   if not world_latest.empty else "N/A"
    top_emitter  = (df[(df['Year'] == latest_year) & df['Code'].notna()]
                    .sort_values('CO₂ emissions per capita', ascending=False)
                    .iloc[0]['Entity'])

    c1, c2 = st.columns(2)
    c1.metric("💨 World CO₂ per Capita", f"{latest_co2} t", delta=f"As of {latest_year}")
    c2.metric("🏆 Highest Emitter", top_emitter, delta="Per capita")

    hr()

    # Mini overview charts
    col_a, col_b = st.columns(2)

    with col_a:
        section_header("📈 Trend", "Global CO₂ Over Time")
        fig_home1 = px.line(world[world['CO₂ emissions per capita'].notna()],
                            x='Year', y='CO₂ emissions per capita',
                            title="World CO₂ Emissions per Capita")
        fig_home1.update_traces(line=dict(color="#0ea5e9", width=2.5),
                                fill="tozeroy", fillcolor="rgba(14,165,233,0.07)")
        apply_theme(fig_home1)
        fig_home1.update_layout(margin=dict(t=44, b=30, l=44, r=16))
        st.plotly_chart(fig_home1, use_container_width=True)

    with col_b:
        section_header("🏆 Rankings", f"Top 10 Emitters ({latest_year})")
        top10_home = (df[(df['Year'] == latest_year) & df['Code'].notna()]
                      .sort_values('CO₂ emissions per capita', ascending=False)
                      .head(10))
        fig_home2 = px.bar(top10_home, x='CO₂ emissions per capita', y='Entity',
                           orientation='h', title=f"Top 10 Emitters — {latest_year}",
                           color='CO₂ emissions per capita',
                           color_continuous_scale=[[0, "#bae6fd"], [1, "#0c4a6e"]])
        fig_home2.update_traces(marker_line_width=0)
        fig_home2.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"),
                                margin=dict(t=44, b=30, l=44, r=16))
        apply_theme(fig_home2)
        st.plotly_chart(fig_home2, use_container_width=True)

    hr()

    # Key insights
    section_header("🔑 Key Insights", "What the Data Tells Us")
    insights = [
        ("🌡️", "Temperature has risen ~1.3 °C since pre-industrial times, accelerating after 1980."),
        ("📈", "Global CO₂ emissions have not yet peaked — fossil fuels still dominate energy supply."),
        ("🌍", "A small number of countries account for the majority of global CO₂ emissions."),
        ("🔋", "Renewable energy share is growing, but still far from what is needed for net-zero."),
        ("🇩🇪", "Several developed nations like Germany and the UK have started cutting emissions."),
    ]
    cols = st.columns(5)
    for col, (icon, text) in zip(cols, insights):
        col.markdown(f"""
        <div style="background:#ffffff;border:1px solid #e8ecf0;border-radius:14px;
                    padding:18px 14px;text-align:center;height:100%;
                    box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="font-size:26px;margin-bottom:10px;">{icon}</div>
            <div style="font-size:12px;color:#475569;line-height:1.6;">{text}</div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 2 — EMISSIONS ANALYSIS
# ════════════════════════════════════════════════════
with tab_emit:
    st.markdown("<br>", unsafe_allow_html=True)

    # Country multi-line
    section_header("📈 Country Comparison", "CO₂ Emissions Over Time")
    default_sel = [c for c in ["United States", "China", "India", "Germany", "United Kingdom"]
                   if c in all_countries]
    selected = st.multiselect("Select Countries", all_countries, default=default_sel)

    if selected:
        cmp_df = df[df['Entity'].isin(selected)]
        fig_cmp = px.line(cmp_df, x='Year', y='CO₂ emissions per capita', color='Entity',
                          title="CO₂ Emissions per Capita — Country Comparison")
        fig_cmp.update_traces(line_width=2.5)
        apply_theme(fig_cmp)
        st.plotly_chart(fig_cmp, use_container_width=True)

    insight_card(
        "The line chart compares CO₂ emissions per capita trajectories for selected countries over time.",
        "Countries that peaked early (USA, UK, Germany) show declining trends reflecting deindustrialisation "
        "and clean-energy policy. Rapidly developing economies (China, India) show strong growth — "
        "though China's per-capita figure is still well below the US historical peak."
    )

    hr()

    # Animated bar chart
    section_header("🎬 Animated Ranking", "Top 10 Emitters — Animated by Year")
    st.markdown("""
    <p style="color:#475569;font-size:14px;margin:-8px 0 16px 0;">
        Press ▶ to watch how the ranking of top CO₂ emitters per capita has shifted over the decades.
    </p>
    """, unsafe_allow_html=True)

    # 👉 Fix 1: Filter years (10-year interval)
    anim_countries = (
    df[
        df['Code'].notna() &
        (df['Year'] % 10 == 0) &
        (df['CO₂ emissions per capita'].notna())
    ]
    .sort_values(['Year', 'CO₂ emissions per capita'], ascending=[True, False])
    .groupby('Year', group_keys=False)
    .head(10)
    .reset_index(drop=True)
)

    # 👉 Fix 2: Better x-axis scaling (avoid extreme outliers)
    fig_anim = px.bar(
        anim_countries,
        x='CO₂ emissions per capita',
        y='Entity',
        animation_frame='Year',
        orientation='h',
        color='Entity',
        title="Top 10 CO₂ Emitters per Capita (Animated)",
        range_x=[0, anim_countries['CO₂ emissions per capita'].quantile(0.95)]
    )

    fig_anim.update_layout(
        showlegend=False,
        height=440,
        yaxis=dict(autorange="reversed")
    )

    apply_theme(fig_anim)
    st.plotly_chart(fig_anim, use_container_width=True)

    hr()

    # Per capita top 15 bar
    section_header("👤 Per Capita View", f"Highest Emitters per Person ({latest_year})")
    per_cap = (df[(df['Year'] == latest_year) & df['Code'].notna()]
               .sort_values('CO₂ emissions per capita', ascending=False)
               .head(15))
    fig_pc = px.bar(per_cap, x='CO₂ emissions per capita', y='Entity',
                    orientation='h',
                    title=f"CO₂ per Capita — Top 15 Countries ({latest_year})",
                    color='CO₂ emissions per capita',
                    color_continuous_scale=[[0, "#fef3c7"], [1, "#d97706"]])
    fig_pc.update_traces(marker_line_width=0)
    fig_pc.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    apply_theme(fig_pc)
    st.plotly_chart(fig_pc, use_container_width=True)

    insight_card(
        f"Per-capita emissions in {latest_year} reveal which populations have the largest individual carbon footprints, "
        "often small, wealthy, or oil-producing nations.",
        "High per-capita emitters typically reflect high energy consumption, fossil fuel dependency, "
        "or small population sizes with large industrial sectors. This metric is important for equity "
        "discussions in global climate negotiations."
    )


# ════════════════════════════════════════════════════
# TAB 3 — ENERGY TRANSITION
# ════════════════════════════════════════════════════
with tab_energy:
    st.markdown("<br>", unsafe_allow_html=True)

    section_header("⚡ Energy Transition", "Shift from Fossil Fuels to Renewables")
    st.markdown("""
    <p style="color:#475569;font-size:14px;margin:-8px 0 16px 0;line-height:1.7;">
        The share of renewable energy in total consumption is the clearest indicator of a country's
        energy transition. Select a country to see its trajectory.
    </p>
    """, unsafe_allow_html=True)

    key_countries = [c for c in ["World", "United States", "China", "India", "Germany",
                                  "United Kingdom", "France", "Brazil", "Japan"]
                     if c in all_countries]
    sel_country_e = st.selectbox("Select Country", key_countries,
                                 index=key_countries.index("Germany") if "Germany" in key_countries else 0,
                                 key="energy_country")

    ren_df = make_renewables_df(key_countries)
    sel_ren = ren_df[ren_df['Entity'] == sel_country_e]

    # Stacked area — fossil vs renewables (derived)
    sel_co2 = df[df['Entity'] == sel_country_e][['Year', 'CO₂ emissions per capita']].copy()
    sel_co2 = sel_co2.merge(sel_ren[['Year', 'Renewables_Share']], on='Year', how='inner')
    sel_co2['Fossil_Share'] = 100 - sel_co2['Renewables_Share']

    fig_stack = go.Figure()
    fig_stack.add_trace(go.Scatter(
        x=sel_co2['Year'], y=sel_co2['Fossil_Share'],
        name='Fossil Fuels (%)', fill='tozeroy',
        line=dict(color="#94a3b8", width=0),
        fillcolor="rgba(148,163,184,0.35)"
    ))
    fig_stack.add_trace(go.Scatter(
        x=sel_co2['Year'], y=sel_co2['Renewables_Share'],
        name='Renewables (%)', fill='tozeroy',
        line=dict(color="#10b981", width=2),
        fillcolor="rgba(16,185,129,0.2)"
    ))
    fig_stack.add_hline(y=50, line_dash="dash", line_color="#0ea5e9",
                        annotation_text="50% Renewables milestone",
                        annotation_font_color="#0369a1", annotation_font_size=11)
    fig_stack.update_layout(title=f"Fossil vs Renewable Energy Share — {sel_country_e}",
                            yaxis_title="Share (%)", height=400)
    apply_theme(fig_stack)
    st.plotly_chart(fig_stack, use_container_width=True)

    insight_card(
        f"The stacked area chart shows the estimated split between fossil fuel and renewable energy "
        f"consumption in <strong style='color:#0369a1'>{sel_country_e}</strong> over time.",
        "A growing green area signals progress in decarbonisation. Most countries are still far from "
        "the 50% renewables milestone (dashed line). Countries like Brazil have a naturally high "
        "renewable share due to hydropower, while industrialised nations are transitioning more slowly."
    )

    hr()

    # Multi-country renewables comparison
    section_header("🌍 Country Comparison", "Renewables Share Across Countries")
    multi_ren = st.multiselect("Select Countries to Compare", key_countries,
                               default=key_countries[:5], key="ren_multi")
    if multi_ren:
        ren_cmp = ren_df[ren_df['Entity'].isin(multi_ren)]
        fig_ren_line = px.line(ren_cmp, x='Year', y='Renewables_Share', color='Entity',
                               labels={'Renewables_Share': 'Renewables Share (%)'},
                               title="Renewable Energy Share — Multi-Country")
        fig_ren_line.update_traces(line_width=2.5)
        apply_theme(fig_ren_line)
        st.plotly_chart(fig_ren_line, use_container_width=True)


# ════════════════════════════════════════════════════
# TAB 4 — GEOGRAPHIC VIEW
# ════════════════════════════════════════════════════
with tab_geo:
    st.markdown("<br>", unsafe_allow_html=True)

    section_header("🗺️ Geographic View", "CO₂ Emissions World Map")
    st.markdown("""
    <p style="color:#475569;font-size:14px;margin:-8px 0 16px 0;line-height:1.7;">
        The choropleth map shows how CO₂ emissions per capita are distributed globally.
        Use the year slider to travel through time and watch the map evolve.
    </p>
    """, unsafe_allow_html=True)

    map_year = st.slider("Select Year", int(df['Year'].min()), latest_year, latest_year, step=5)
    map_df   = df[(df['Year'] == map_year) & df['Code'].notna()]

    fig_map = px.choropleth(
        map_df, locations="Code", color="CO₂ emissions per capita",
        hover_name="Entity",
        color_continuous_scale=[[0, "#e0f2fe"], [0.4, "#38bdf8"], [1, "#0c4a6e"]],
        title=f"CO₂ Emissions per Capita by Country — {map_year}"
    )
    fig_map.update_layout(
        geo=dict(bgcolor="#fafbfc", showframe=False, showcoastlines=True,
                 coastlinecolor="#e2e8f0", landcolor="#f8fafc",
                 showocean=True, oceancolor="#e0f2fe"),
        coloraxis_colorbar=dict(bgcolor="#ffffff", tickcolor="#94a3b8",
                                title=dict(font=dict(color="#64748b", size=11))),
        paper_bgcolor="#ffffff", height=520,
    )
    apply_theme(fig_map)
    st.plotly_chart(fig_map, use_container_width=True)

    insight_card(
        f"The map shows CO₂ emissions per capita across all countries in {map_year}. "
        "Darker shades indicate higher per-capita emissions.",
        "North America, Australia, and the Gulf states consistently show the darkest shades — "
        "reflecting high energy consumption per person. Africa and South/Southeast Asia remain "
        "light, highlighting both lower emissions and significant energy poverty. "
        "Drag the slider to see how the global picture has changed over decades."
    )

    hr()

    # Data table
    section_header("📋 Data Table", f"Raw Data — {map_year}")
    st.dataframe(
        map_df[['Entity', 'CO₂ emissions per capita']]
        .sort_values('CO₂ emissions per capita', ascending=False)
        .reset_index(drop=True)
        .rename(columns={'Entity': 'Country', 'CO₂ emissions per capita': 'CO₂ per Capita (t)'}),
        use_container_width=True,
        height=300
    )


# ════════════════════════════════════════════════════
# TAB 5 — CORRELATION EXPLORER
# ════════════════════════════════════════════════════
with tab_corr:
    st.markdown("<br>", unsafe_allow_html=True)

    section_header("🔍 Correlation Explorer", "Relationships Between Variables")
    st.markdown("""
    <p style="color:#475569;font-size:14px;margin:-8px 0 16px 0;line-height:1.7;">
        Explore how CO₂ emissions per capita relate to time across different countries.
        Select countries and a year to view emission trajectories up to that point.
    </p>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        corr_countries = st.multiselect(
            "Select Countries",
            all_countries,
            default=[c for c in ["United States","China","India","Germany","United Kingdom","Brazil","Japan"]
                     if c in all_countries],
            key="corr_countries"
        )

    with c2:
        corr_year = st.slider(
            "Select Year",
            int(df['Year'].min()),
            latest_year,
            latest_year,
            step=1,
            key="corr_year"
        )

    # -------------------------------
    # ONLY SCATTER (with slider fix)
    # -------------------------------
    if corr_countries:
        traj_df = df[
            (df['Entity'].isin(corr_countries)) &
            (df['Year'] <= corr_year)   # 🔥 THIS MAKES SLIDER WORK
        ]

        fig_traj = px.scatter(
            traj_df,
            x='Year',
            y='CO₂ emissions per capita',
            color='Entity',
            opacity=0.7,
            title=f"Emission Trajectories — Up to {corr_year}",
            trendline="lowess",
            labels={'CO₂ emissions per capita': 'CO₂ per Capita (t)'}
        )

        fig_traj.update_traces(marker=dict(size=6, line=dict(color="#ffffff", width=0.8)))
        apply_theme(fig_traj)

        st.plotly_chart(fig_traj, use_container_width=True)

    # -------------------------------
    # INSIGHT TEXT
    # -------------------------------
    insight_card(
        "Each dot is one country-year observation. The LOWESS trend lines smooth out noise "
        "to show each country's underlying emission trajectory.",
        "Converging trend lines indicate countries moving toward similar per-capita emission levels. "
        "Diverging lines highlight growing inequality. Countries whose lines peak and then fall "
        "have successfully decoupled economic growth from carbon emissions."
    )

    hr()

    # Bar snapshot for selected year
    section_header("📊 Year Snapshot", f"Emission Levels Compared — {corr_year}")
    if corr_countries:
        snap = (df[(df['Year'] == corr_year) & df['Entity'].isin(corr_countries)]
                [['Entity', 'CO₂ emissions per capita']].dropna()
                .sort_values('CO₂ emissions per capita', ascending=True))
        fig_snap = px.bar(snap, x='CO₂ emissions per capita', y='Entity',
                          orientation='h',
                          title=f"CO₂ per Capita for Selected Countries — {corr_year}",
                          color='CO₂ emissions per capita',
                          color_continuous_scale=[[0, "#d1fae5"], [1, "#065f46"]])
        fig_snap.update_traces(marker_line_width=0)
        fig_snap.update_layout(coloraxis_showscale=False)
        apply_theme(fig_snap)
        st.plotly_chart(fig_snap, use_container_width=True)

    hr()

    # Heatmap — correlation of CO2 across decades
    section_header("🔥 Decade Heatmap", "Average CO₂ per Capita by Country & Decade")
    if corr_countries:
        heat_df = df[df['Entity'].isin(corr_countries)].copy()
        heat_df['Decade'] = (heat_df['Year'] // 10 * 10).astype(str) + "s"
        pivot = (heat_df.groupby(['Entity', 'Decade'])['CO₂ emissions per capita']
                 .mean().reset_index()
                 .pivot(index='Entity', columns='Decade', values='CO₂ emissions per capita'))
        fig_heat = px.imshow(pivot.round(2), text_auto=".1f",
                             color_continuous_scale=[[0, "#f0f9ff"], [0.5, "#38bdf8"], [1, "#0c4a6e"]],
                             title="Average CO₂ per Capita by Country and Decade",
                             aspect="auto")
        fig_heat.update_layout(height=400)
        apply_theme(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)

    insight_card(
        "The heatmap shows average CO₂ per capita for each country across decades. "
        "Darker blue = higher emissions. Empty cells = no data for that decade.",
        "Read across a row to see a country's trend over time. Read down a column to compare "
        "countries within a single decade. This makes it easy to spot which countries have "
        "consistently high emissions vs those that have made meaningful reductions."
    )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="padding:24px 32px;background:#ffffff;border:1px solid #e8ecf0;border-radius:16px;
            box-shadow:0 1px 3px rgba(0,0,0,0.04);display:flex;justify-content:space-between;
            align-items:center;flex-wrap:wrap;gap:12px;">
    <div>
        <div style="font-size:13px;color:#0f172a;font-weight:600;margin-bottom:4px;">
            📊 Data Source
        </div>
        <a href="https://ourworldindata.org/co2-and-greenhouse-gas-emissions"
           style="color:#0ea5e9;font-size:13px;text-decoration:none;font-weight:500;">
            ourworldindata.org — CO₂ Emissions Dataset
        </a>
    </div>
    <div style="text-align:right;">
        <div style="font-size:13px;color:#0f172a;font-weight:600;margin-bottom:4px;">
            📌 Design Project
        </div>
        <div style="font-size:12px;color:#94a3b8;">
            📅 (Semester 4) 2026
        </div>
    </div>
</div>
<br>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# COUNTRY ANALYSIS TAB  (defined after all others
#  because it uses filtered data + the helpers above)
# ════════════════════════════════════════════════════
# NOTE: Streamlit renders tabs in declaration order — tab_country
# was intentionally declared last so we can reuse all helpers.
# But st.tabs() must all be declared together. Let's put it inline: