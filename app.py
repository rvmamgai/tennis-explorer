import pandas as pd
import plotly.express as px
import streamlit as st

from database import engine

# =====================================================================
# PAGE SETUP
# =====================================================================
st.set_page_config(page_title="Tennis Rankings Explorer", page_icon="🎾", layout="wide")

BAR_COLOR = "#2E7D32"  # one single color -> no extra color-scale bar
GENDER_COLORS = {"Men": "#1f77b4", "Women": "#e377c2", "Mixed": "#2ca02c",
                  "Not Specified": "#9e9e9e"}


@st.cache_data
def run_query(sql, params=None):
    return pd.read_sql(sql, engine, params=params)


def chart_header(title, explanation):
    """Clear title + one-line plain-English explanation above every chart."""
    st.subheader(title)
    st.caption(explanation)


def clean_bar(fig, height=420):
    fig.update_layout(
        height=height,
        coloraxis_showscale=False,
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


# =====================================================================
# FIND THE LATEST RANKING PERIOD (rankings are published weekly)
# =====================================================================
latest_period = run_query("""
    SELECT year, week FROM competitor_rankings
    ORDER BY year DESC, week DESC LIMIT 1
""").iloc[0]
latest_year, latest_week = int(latest_period["year"]), int(latest_period["week"])

# =====================================================================
# LOAD DATA  (rankings pinned to the latest week so each player appears once)
# =====================================================================
rankings_full = run_query("""
    SELECT c.competitor_id, c.name, c.country, c.country_code, c.abbreviation,
           r.`rank` AS `rank`, r.movement, r.points, r.ranking_name, r.gender
    FROM competitors c
    JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
    WHERE r.year = %(year)s AND r.week = %(week)s
""", params={"year": latest_year, "week": latest_week})
rankings_full["movement"] = pd.to_numeric(rankings_full["movement"], errors="coerce")

# LEFT JOIN so competitions without a matching category are not dropped
competitions_full = run_query("""
    SELECT c.competition_name, c.type, c.gender, cat.category_name
    FROM competitions c
    LEFT JOIN categories cat ON c.category_id = cat.category_id
""")
competitions_full["gender"] = (
    competitions_full["gender"].astype(str).str.strip().str.title()
)
competitions_full.loc[
    competitions_full["gender"].isin(["None", "Nan", ""]), "gender"
] = "Not Specified"
competitions_full["type"] = competitions_full["type"].fillna("Not Specified")
competitions_full["category_name"] = competitions_full["category_name"].fillna("Not Specified")

venues_full = run_query("""
    SELECT v.venue_name, v.city_name, v.country_name, cx.complex_name
    FROM venues v
    LEFT JOIN complexes cx ON v.complex_id = cx.complex_id
""")
venues_full["country_name"] = venues_full["country_name"].fillna("Not Specified")
venues_full["complex_name"] = venues_full["complex_name"].fillna("Not Specified")

# =====================================================================
# SIDEBAR FILTERS
# =====================================================================
st.sidebar.title("🎛️ Filters")

st.sidebar.markdown("### 👤 Players")
max_rank = int(rankings_full["rank"].max())
rank_range = st.sidebar.slider("World ranking range", 1, max_rank, (1, min(100, max_rank)))
country_filter = st.sidebar.multiselect(
    "Player country (leave empty = all)",
    sorted(rankings_full["country"].dropna().unique().tolist()),
)
name_filter = st.sidebar.text_input("Search player name")
top_n = st.sidebar.slider("How many players in the 'Top players' chart", 5, 30, 10)

st.sidebar.markdown("### 🏆 Competitions")
gender_filter = st.sidebar.multiselect(
    "Competition gender (leave empty = all)",
    sorted(competitions_full["gender"].unique().tolist()),
)
type_filter = st.sidebar.multiselect(
    "Competition type (leave empty = all)",
    sorted(competitions_full["type"].unique().tolist()),
)
category_filter = st.sidebar.multiselect(
    "Competition category (leave empty = all)",
    sorted(competitions_full["category_name"].unique().tolist()),
)
comp_search = st.sidebar.text_input("Search competition name")

st.sidebar.markdown("### 🏟️ Venues")
venue_country_filter = st.sidebar.multiselect(
    "Venue country (leave empty = all)",
    sorted(venues_full["country_name"].unique().tolist()),
)
venue_search = st.sidebar.text_input("Search venue / city")

# =====================================================================
# APPLY FILTERS
# =====================================================================
df = rankings_full[
    (rankings_full["rank"] >= rank_range[0]) & (rankings_full["rank"] <= rank_range[1])
]
if country_filter:
    df = df[df["country"].isin(country_filter)]
if name_filter:
    df = df[df["name"].str.contains(name_filter, case=False, na=False)]
df = df.sort_values("rank")

comp_df = competitions_full.copy()
if gender_filter:
    comp_df = comp_df[comp_df["gender"].isin(gender_filter)]
if type_filter:
    comp_df = comp_df[comp_df["type"].isin(type_filter)]
if category_filter:
    comp_df = comp_df[comp_df["category_name"].isin(category_filter)]
if comp_search:
    comp_df = comp_df[
        comp_df["competition_name"].str.contains(comp_search, case=False, na=False)
    ]

venue_df = venues_full.copy()
if venue_country_filter:
    venue_df = venue_df[venue_df["country_name"].isin(venue_country_filter)]
if venue_search:
    mask = venue_df["venue_name"].str.contains(venue_search, case=False, na=False) | \
           venue_df["city_name"].str.contains(venue_search, case=False, na=False)
    venue_df = venue_df[mask]

# =====================================================================
# HEADER + KPIs
# =====================================================================
st.title("🎾 Tennis Rankings Explorer")
st.caption("Game Analytics: Unlocking Tennis Data with SportRadar API")

st.info(
    f"Showing players ranked **#{rank_range[0]} to #{rank_range[1]}**"
    + (f" from **{', '.join(country_filter)}**" if country_filter else " from **all countries**")
    + f" — ranking period: **{latest_year} / Week {latest_week}**."
    + " Change the filters in the left sidebar - every number and chart below updates."
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Players Shown", f"{df['competitor_id'].nunique():,}",
          help="Number of ranked players that match your ranking range, country and name filters.")
k2.metric("Countries Represented", f"{df['country'].nunique():,}",
          help="How many different countries those players come from.")
k3.metric("Highest Ranking Points", f"{int(df['points'].max()):,}" if not df.empty else "0",
          help="Points of the best player in the current selection.")
k4.metric("Competitions Found", f"{comp_df.shape[0]:,}",
          help=f"Out of {competitions_full.shape[0]:,} total competitions, after your competition filters.")
k5.metric("Venues Found", f"{venue_df.shape[0]:,}",
          help=f"Out of {venues_full.shape[0]:,} total venues, after your venue filters.")

st.markdown("---")

# =====================================================================
# TABS
# =====================================================================
tab_over, tab_players, tab_comp, tab_venue = st.tabs(
    ["📊 Overview", "👤 Players", "🏆 Competitions", "🏟️ Venues"]
)

# ---------------------------------------------------------------- OVERVIEW
with tab_over:
    c1, c2 = st.columns(2)

    with c1:
        chart_header(
            f"Top {top_n} Players by Ranking Points",
            "Each bar is one player. Longer bar = more ranking points.",
        )
        if df.empty:
            st.info("No players match the current filters.")
        else:
            top_df = df.sort_values("points", ascending=False).head(top_n)
            fig = px.bar(
                top_df, x="points", y="name", orientation="h", text="points",
                color_discrete_sequence=[BAR_COLOR],
                labels={"points": "Ranking Points", "name": "Player"},
                hover_data={"rank": True, "country": True, "points": True, "name": False},
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(clean_bar(fig), use_container_width=True)

    with c2:
        chart_header(
            "Competitions: Men vs Women vs Mixed",
            "Share of competitions for each gender category (after your competition filters).",
        )
        if comp_df.empty:
            st.info("No competitions match the current filters.")
        else:
            g = comp_df["gender"].value_counts().reset_index()
            g.columns = ["Gender", "Number of Competitions"]
            fig = px.pie(g, names="Gender", values="Number of Competitions", hole=0.4,
                         color="Gender", color_discrete_map=GENDER_COLORS)
            fig.update_traces(textinfo="label+percent+value")
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        chart_header(
            "Number of Players per Country",
            "Which countries have the most players in the current ranking selection.",
        )
        if df.empty:
            st.info("No players match the current filters.")
        else:
            pc = df["country"].value_counts().head(15).reset_index()
            pc.columns = ["Country", "Number of Players"]
            fig = px.bar(pc, x="Number of Players", y="Country", orientation="h",
                         text="Number of Players", color_discrete_sequence=[BAR_COLOR])
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(clean_bar(fig), use_container_width=True)

    with c4:
        chart_header(
            "Rank vs Points (every player is a dot)",
            "Top-ranked players (left) have the most points. Hover over a dot to see the player.",
        )
        if df.empty:
            st.info("No players match the current filters.")
        else:
            fig = px.scatter(
                df, x="rank", y="points", hover_name="name",
                hover_data={"country": True},
                color_discrete_sequence=[BAR_COLOR],
                labels={"rank": "World Rank (1 = best)", "points": "Ranking Points"},
            )
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- PLAYERS
with tab_players:
    chart_header(
        "Rank Movement (how many places players moved up or down)",
        "Positive = climbed up the rankings, negative = dropped, 0 = no change.",
    )
    mv = df["movement"].dropna()
    if mv.empty:
        st.info("No movement data for the current selection.")
    else:
        fig = px.histogram(mv, x="movement", nbins=30, color_discrete_sequence=[BAR_COLOR],
                           labels={"movement": "Places Moved", "count": "Number of Players"})
        fig.update_layout(height=350, showlegend=False, yaxis_title="Number of Players",
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔎 Player Profile")
    if df.empty:
        st.info("No players match the current filters.")
    else:
        player = st.selectbox("Pick a player", df["name"].tolist())
        row = df[df["name"] == player].iloc[0]
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("World Rank", int(row["rank"]))
        p2.metric("Ranking Points", f"{int(row['points']):,}")
        p3.metric("Places Moved", int(row["movement"]) if pd.notna(row["movement"]) else "-")
        p4.metric("Ranking Type", row["ranking_name"] if pd.notna(row["ranking_name"]) else "-")
        st.caption(f"Country: {row['country']}")

    st.subheader("Filtered Rankings Table")
    table = df[["rank", "name", "country", "movement", "points", "ranking_name"]].rename(
        columns={"rank": "Rank", "name": "Player", "country": "Country",
                 "movement": "Places Moved", "points": "Points",
                 "ranking_name": "Ranking Type"})
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download rankings (CSV)", table.to_csv(index=False),
                       "tennis_rankings.csv", "text/csv")

# ---------------------------------------------------------------- COMPETITIONS
with tab_comp:
    cc1, cc2 = st.columns(2)
    with cc1:
        chart_header(
            "Competitions by Type",
            "How many competitions are singles, doubles, mixed, etc.",
        )
        if comp_df.empty:
            st.info("No competitions match the current filters.")
        else:
            t = comp_df["type"].value_counts().reset_index()
            t.columns = ["Type", "Number of Competitions"]
            fig = px.bar(t, x="Type", y="Number of Competitions", text="Number of Competitions",
                         color_discrete_sequence=[BAR_COLOR])
            st.plotly_chart(clean_bar(fig, 380), use_container_width=True)

    with cc2:
        chart_header(
            "Top 15 Competition Categories",
            "Categories (e.g. ATP, WTA, ITF) that have the most competitions.",
        )
        if comp_df.empty:
            st.info("No competitions match the current filters.")
        else:
            cat = comp_df["category_name"].value_counts().head(15).reset_index()
            cat.columns = ["Category", "Number of Competitions"]
            fig = px.bar(cat, x="Number of Competitions", y="Category", orientation="h",
                         text="Number of Competitions", color_discrete_sequence=[BAR_COLOR])
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(clean_bar(fig, 380), use_container_width=True)

    st.subheader("Competitions Table")
    ctable = comp_df.rename(columns={
        "competition_name": "Competition", "type": "Type",
        "gender": "Gender", "category_name": "Category"})
    st.dataframe(ctable, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download competitions (CSV)", ctable.to_csv(index=False),
                       "tennis_competitions.csv", "text/csv")

# ---------------------------------------------------------------- VENUES
with tab_venue:
    vc1, vc2 = st.columns(2)
    with vc1:
        chart_header(
            "Top 15 Countries by Number of Venues",
            "Countries that host the most tennis venues.",
        )
        if venue_df.empty:
            st.info("No venues match the current filters.")
        else:
            vcnt = venue_df["country_name"].value_counts().head(15).reset_index()
            vcnt.columns = ["Country", "Number of Venues"]
            fig = px.bar(vcnt, x="Number of Venues", y="Country", orientation="h",
                         text="Number of Venues", color_discrete_sequence=[BAR_COLOR])
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(clean_bar(fig, 400), use_container_width=True)

    with vc2:
        chart_header(
            "Top 15 Complexes by Number of Venues",
            "A complex is a facility containing several courts/venues.",
        )
        if venue_df.empty:
            st.info("No venues match the current filters.")
        else:
            cx = venue_df[venue_df["complex_name"] != "Not Specified"]["complex_name"] \
                .value_counts().head(15).reset_index()
            cx.columns = ["Complex", "Number of Venues"]
            if cx.empty:
                st.info("No complex information available.")
            else:
                fig = px.bar(cx, x="Number of Venues", y="Complex", orientation="h",
                             text="Number of Venues", color_discrete_sequence=[BAR_COLOR])
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(clean_bar(fig, 400), use_container_width=True)

    st.subheader("Venues and Complexes Table")
    vtable = venue_df.rename(columns={
        "venue_name": "Venue", "city_name": "City",
        "country_name": "Country", "complex_name": "Complex"})
    st.dataframe(vtable, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download venues (CSV)", vtable.to_csv(index=False),
                       "tennis_venues.csv", "text/csv")