import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import io
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Meta Ads AI Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* ── Root & Reset ── */
:root {
    --bg:        #0a0a0f;
    --surface:   #12121a;
    --border:    #2a2a3a;
    --accent:    #7c6aff;
    --accent2:   #ff6a9b;
    --text:      #e8e6ff;
    --muted:     #6b6880;
    --success:   #4fffb0;
    --warning:   #ffcc4f;
    --danger:    #ff4f6a;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── App bg ── */
.stApp {
    background: var(--bg) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Header ── */
.hero-header {
    padding: 2rem 0 1.5rem;
    text-align: center;
}
.hero-header h1 {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}
.hero-header p {
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-card.purple::before { background: var(--accent); }
.kpi-card.pink::before   { background: var(--accent2); }
.kpi-card.green::before  { background: var(--success); }
.kpi-card.yellow::before { background: var(--warning); }
.kpi-card.red::before    { background: var(--danger); }

.kpi-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-size: 1.7rem;
    font-weight: 800;
    line-height: 1;
    color: var(--text);
}
.kpi-sub {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.3rem;
}

/* ── Section titles ── */
.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: 0.03em;
    margin: 2rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── AI Analysis box ── */
.ai-box {
    background: linear-gradient(135deg, #12121a 60%, #1a1228 100%);
    border: 1px solid var(--accent);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    position: relative;
    overflow: hidden;
}
.ai-box::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(124,106,255,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.ai-tag {
    display: inline-block;
    background: rgba(124,106,255,0.15);
    border: 1px solid rgba(124,106,255,0.4);
    color: var(--accent);
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.ai-content {
    color: #c8c6e8;
    line-height: 1.75;
    font-size: 0.95rem;
    white-space: pre-wrap;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.8rem !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    background: var(--surface) !important;
}

/* ── Text inputs ── */
.stTextInput input, .stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

/* ── Spinner text ── */
.stSpinner > div {
    color: var(--accent) !important;
}

/* ── Alert-style info ── */
.stAlert {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

REQUIRED_COLS = [
    "campaign_name", "impressions", "clicks", "spend", "reach"
]

OPTIONAL_COLS = [
    "ctr", "cpc", "cpm", "frequency", "conversions",
    "conversion_values", "roas", "ad_name", "adset_name",
    "result_rate", "cost_per_result"
]

def fmt_currency(val: float, symbol: str = "R$") -> str:
    return f"{symbol} {val:,.2f}"

def fmt_number(val: float) -> str:
    if val >= 1_000_000:
        return f"{val/1_000_000:.2f}M"
    if val >= 1_000:
        return f"{val/1_000:.1f}K"
    return f"{val:,.0f}"

def fmt_pct(val: float) -> str:
    return f"{val:.2f}%"

def load_csv(file) -> pd.DataFrame:
    """Try multiple encodings to load the CSV."""
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=enc)
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            return df
        except Exception:
            continue
    raise ValueError("Não foi possível decodificar o arquivo CSV.")

# Regra 2: cada plataforma tem nomes de colunas distintos. Esta função mapeia
# tudo para o padrão interno único usado pelos gráficos e cálculos de KPI.
# Adicionar novas plataformas no futuro = apenas um novo bloco de mapeamento.

# Mapeamento Google Ads → padrão interno
# Chave: nome da coluna do CSV (lowercase+underscore), Valor: nome interno
GOOGLE_ADS_COLUMN_MAP: dict[str, str] = {
    # Campanha
    "campaign":                "campaign_name",
    "campanha":                "campaign_name",
    # Impressões
    "impr.":                   "impressions",
    "impressões":              "impressions",
    "impressions":             "impressions",
    # Cliques
    "clicks":                  "clicks",
    "cliques":                 "clicks",
    # Investimento
    "cost":                    "spend",
    "custo":                   "spend",
    "cost_(brl)":              "spend",
    "custo_(brl)":             "spend",
    "cost_(usd)":              "spend",
    # CTR
    "ctr":                     "ctr",
    # CPC médio
    "avg._cpc":                "cpc",
    "cpc_médio":               "cpc",
    "avg._cpc_(brl)":          "cpc",
    # CPM
    "avg._cpm":                "cpm",
    "cpm_médio":               "cpm",
    # Conversões
    "conversions":             "conversions",
    "conversões":              "conversions",
    # Valor das conversões (para ROAS)
    "conv._value":             "conversion_values",
    "valor_conv.":             "conversion_values",
    "all_conv._value":         "conversion_values",
    # Alcance (Google não exporta reach diretamente)
    "reach":                   "reach",
    # Ad / grupo de anúncios
    "ad_group":                "adset_name",
    "grupo_de_anúncios":       "adset_name",
    "ad":                      "ad_name",
    "anúncio":                 "ad_name",
    # Quota de impressão (específico Google)
    "search_impr._share":      "impression_share",
    # Data (Google exporta como "Day", "Week", "Month")
    "day":                     "date",
    "dia":                     "date",
    "week":                    "week",
    "month":                   "month",
}

# Meta Ads já usa nomes padrão; mapeamento identidade apenas para os aliases
META_ADS_COLUMN_MAP: dict[str, str] = {
    # Aliases PT-BR que podem vir no export localizado
    "campanha":            "campaign_name",
    "investimento":        "spend",
    "impressões":          "impressions",
    "cliques":             "clicks",
    "alcance":             "reach",
    "conversões":          "conversions",
    "frequência":          "frequency",
    "nome_do_anúncio":     "ad_name",
    "conjunto_de_anúncios":"adset_name",
}


def normalize_columns(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    """
    Aplica o mapeamento de colunas da plataforma selecionada para o padrão
    interno. Colunas não mapeadas são mantidas intactas.
    """
    col_map = GOOGLE_ADS_COLUMN_MAP if platform == "Google Ads" else META_ADS_COLUMN_MAP
    # Normaliza os nomes atuais do df para lowercase+underscore antes de comparar
    rename = {col: col_map[col] for col in df.columns if col in col_map}
    df = df.rename(columns=rename)
    return df

# Regra 3: o Google Ads exporta uma linha de título do relatório no topo e
# uma linha de "Total" no final. Ambas precisam ser removidas antes do parse
# para não contaminar os dados numéricos.

def clean_google_ads_csv(file) -> pd.DataFrame:
    """
    Lê o CSV do Google Ads ignorando linhas de cabeçalho extras (relatório
    gerado pelo Google tem 2 linhas antes do header real) e remove a linha
    de totais no final.
    """
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            file.seek(0)
            raw = file.read().decode(enc)
            lines = raw.splitlines()

            # Encontra a linha do header real: é a primeira linha que
            # contenha "Campaign" ou "Campanha" (case-insensitive).
            header_idx = 0
            for i, line in enumerate(lines):
                lower = line.lower()
                if "campaign" in lower or "campanha" in lower or "impr" in lower:
                    header_idx = i
                    break

            # Reconstrói o CSV a partir do header real
            clean = "\n".join(lines[header_idx:])
            import io as _io
            df = pd.read_csv(_io.StringIO(clean))
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

            # Remove linhas de total: onde a coluna de campanha é "total"
            # (Google Ads exporta "Total" em PT e EN)
            camp_col = next(
                (c for c in df.columns if c in ("campaign", "campanha", "campaign_name")),
                None,
            )
            if camp_col:
                df = df[~df[camp_col].astype(str).str.strip().str.lower().isin(
                    ["total", "totals", "grand total", "total geral"]
                )]

            # Remove linhas completamente vazias
            df = df.dropna(how="all").reset_index(drop=True)
            return df

        except Exception:
            continue

    raise ValueError("Não foi possível decodificar o CSV do Google Ads.")

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and derive metrics."""
    # Numeric coercion
    numeric_cols = [
        "impressions", "clicks", "spend", "reach", "ctr", "cpc",
        "cpm", "frequency", "conversions", "conversion_values",
        "roas", "result_rate", "cost_per_result"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[R$\s%,]", "", regex=True)
                .str.replace(",", ".", regex=False)
                .pipe(pd.to_numeric, errors="coerce")
            )

    # Derive missing metrics
    if "ctr" not in df.columns and {"clicks", "impressions"}.issubset(df.columns):
        df["ctr"] = df["clicks"] / df["impressions"].replace(0, float("nan")) * 100

    if "cpc" not in df.columns and {"spend", "clicks"}.issubset(df.columns):
        df["cpc"] = df["spend"] / df["clicks"].replace(0, float("nan"))

    if "cpm" not in df.columns and {"spend", "impressions"}.issubset(df.columns):
        df["cpm"] = df["spend"] / df["impressions"].replace(0, float("nan")) * 1000

    if "roas" not in df.columns and {"conversion_values", "spend"}.issubset(df.columns):
        df["roas"] = df["conversion_values"] / df["spend"].replace(0, float("nan"))

    return df

def build_summary(df: pd.DataFrame) -> dict:
    """Build a compact summary dict for the AI prompt."""
    s: dict = {}

    def safe_sum(col):
        return float(df[col].sum()) if col in df.columns else None

    def safe_mean(col):
        return float(df[col].mean()) if col in df.columns else None

    s["total_campaigns"] = int(df["campaign_name"].nunique()) if "campaign_name" in df.columns else len(df)
    s["total_ads"] = int(df["ad_name"].nunique()) if "ad_name" in df.columns else None
    s["total_spend"] = safe_sum("spend")
    s["total_impressions"] = safe_sum("impressions")
    s["total_clicks"] = safe_sum("clicks")
    s["total_conversions"] = safe_sum("conversions")
    s["total_revenue"] = safe_sum("conversion_values")
    s["avg_ctr"] = safe_mean("ctr")
    s["avg_cpc"] = safe_mean("cpc")
    s["avg_cpm"] = safe_mean("cpm")
    s["avg_roas"] = safe_mean("roas")
    s["avg_frequency"] = safe_mean("frequency")

    # Top / bottom campaigns by ROAS or spend
    if "campaign_name" in df.columns and "spend" in df.columns:
        grp = df.groupby("campaign_name").agg(
            spend=("spend", "sum"),
            clicks=("clicks", "sum") if "clicks" in df.columns else ("spend", "count"),
        ).reset_index().sort_values("spend", ascending=False)
        s["top_campaigns_by_spend"] = grp.head(5).to_dict(orient="records")

    return {k: v for k, v in s.items() if v is not None}

# Regra 4: a plataforma é injetada no prompt para que o Gemini assuma o papel
# correto de especialista e use a nomenclatura certa (ex: "Google Ads Manager"
# vs "Meta Ads Manager" nas recomendações de implementação).

def build_prompt(summary: dict, user_goal: str, currency: str, platform: str) -> str:
    summary_json = json.dumps(summary, ensure_ascii=False, indent=2)

    # Textos que variam por plataforma
    platform_role = (
        "Meta Ads (Facebook/Instagram)"
        if platform == "Meta Ads"
        else "Google Ads (Search, Display, Performance Max)"
    )
    platform_manager = (
        "Meta Ads Manager"
        if platform == "Meta Ads"
        else "Google Ads Manager / Editor"
    )

    return f"""Você é um especialista sênior em performance de mídia paga com foco em {platform_role}. Analise os dados abaixo e forneça uma análise aprofundada e acionável em português.

## PLATAFORMA
{platform} — use terminologia, benchmarks e recomendações específicos desta plataforma.

## DADOS DOS ANÚNCIOS
```json
{summary_json}
```

## OBJETIVO DO ANUNCIANTE
{user_goal}

## MOEDA
{currency}

## ESTRUTURA DA ANÁLISE (responda nesta ordem exata):

### 🔍 Diagnóstico Geral
Avalie o desempenho geral da conta: volume de investimento, alcance, engajamento e eficiência de custo. Seja direto e específico com os números.

### 🏆 Pontos Fortes
Liste de 2 a 4 pontos positivos concretos (com métricas), explicando por que são bons resultados para {platform}.

### ⚠️ Alertas & Problemas
Identifique de 2 a 4 problemas críticos ou métricas abaixo do ideal, com benchmarks do setor para {platform} como comparação.

### 🎯 Recomendações Prioritárias
Forneça de 3 a 5 ações específicas e priorizadas (da mais urgente para a menos urgente). Cada ação deve incluir:
- O que fazer
- Por que fazer (impacto esperado)
- Como implementar (passos concretos no {platform_manager})

### 📈 Projeção de Oportunidade
Com base nos dados, estime o potencial de melhoria se as principais recomendações forem implementadas (ex.: redução de CPC, aumento de ROAS, etc.).

Seja direto, técnico e evite generalizações. Use os números reais dos dados fornecidos.
"""


def run_gemini_analysis(api_key: str, prompt: str, model_name: str) -> str:
    genai.configure(api_key=api_key)
    modelo_oficial = "gemini-2.5-flash"
    model = genai.GenerativeModel(modelo_oficial)
    response = model.generate_content(prompt)
    return response.text


# Chart theme
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(18,18,26,0.6)",
    font=dict(family="Syne, sans-serif", color="#e8e6ff", size=12),
    xaxis=dict(gridcolor="#2a2a3a", zerolinecolor="#2a2a3a", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#2a2a3a", zerolinecolor="#2a2a3a", tickfont=dict(size=11)),
    legend=dict(
        bgcolor="rgba(18,18,26,0.8)",
        bordercolor="#2a2a3a",
        borderwidth=1,
        font=dict(size=11),
    ),
    margin=dict(l=10, r=10, t=40, b=10),
    hovermode="x unified",
)

COLORS = {
    "spend":       "#7c6aff",
    "conversions": "#ff6a9b",
    "clicks":      "#4fffb0",
    "impressions": "#ffcc4f",
    "ctr":         "#ff9f4f",
    "roas":        "#4fc3ff",
    "cpc":         "#ff4f6a",
    "cpm":         "#b06aff",
}


def detect_date_col(df: pd.DataFrame):
    """Return the first column that looks like a date, or None."""
    candidates = [c for c in df.columns if any(k in c for k in ("date", "data", "dia", "day", "week", "period", "mes", "month"))]
    for col in candidates:
        try:
            parsed = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
            if parsed.notna().sum() > len(df) * 0.5:
                return col, parsed
        except Exception:
            continue
    return None, None


def chart_spend_vs_conversions(df_t: pd.DataFrame, sym: str) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=df_t["_date"], y=df_t["spend"],
        name=f"Investimento ({sym})",
        mode="lines+markers",
        line=dict(color=COLORS["spend"], width=2.5),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(124,106,255,0.08)",
        hovertemplate=f"<b>Investimento</b>: {sym} %{{y:,.2f}}<extra></extra>",
    ), secondary_y=False)

    if "conversions" in df_t.columns:
        fig.add_trace(go.Scatter(
            x=df_t["_date"], y=df_t["conversions"],
            name="Conversões",
            mode="lines+markers",
            line=dict(color=COLORS["conversions"], width=2.5, dash="dot"),
            marker=dict(size=6, symbol="diamond"),
            hovertemplate="<b>Conversões</b>: %{y:,.0f}<extra></extra>",
        ), secondary_y=True)

    fig.update_layout(
        title=dict(text="📈 Investimento vs. Conversões ao longo do tempo", font=dict(size=15)),
        **CHART_THEME,
    )
    fig.update_yaxes(title_text=f"Investimento ({sym})", secondary_y=False, title_font=dict(color=COLORS["spend"]))
    fig.update_yaxes(title_text="Conversões", secondary_y=True, title_font=dict(color=COLORS["conversions"]))
    return fig


def chart_clicks_ctr(df_t: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=df_t["_date"], y=df_t["clicks"] if "clicks" in df_t.columns else [],
        name="Cliques",
        marker_color=COLORS["clicks"],
        opacity=0.75,
        hovertemplate="<b>Cliques</b>: %{y:,.0f}<extra></extra>",
    ), secondary_y=False)

    if "ctr" in df_t.columns:
        fig.add_trace(go.Scatter(
            x=df_t["_date"], y=df_t["ctr"],
            name="CTR (%)",
            mode="lines+markers",
            line=dict(color=COLORS["ctr"], width=2.5),
            marker=dict(size=5),
            hovertemplate="<b>CTR</b>: %{y:.2f}%<extra></extra>",
        ), secondary_y=True)

    fig.update_layout(
        title=dict(text="🖱️ Cliques & CTR diário", font=dict(size=15)),
        barmode="overlay",
        **CHART_THEME,
    )
    fig.update_yaxes(title_text="Cliques", secondary_y=False, title_font=dict(color=COLORS["clicks"]))
    fig.update_yaxes(title_text="CTR (%)", secondary_y=True, title_font=dict(color=COLORS["ctr"]))
    return fig


def chart_roas_cpc(df_t: pd.DataFrame, sym: str) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if "roas" in df_t.columns:
        fig.add_trace(go.Scatter(
            x=df_t["_date"], y=df_t["roas"],
            name="ROAS",
            mode="lines+markers",
            line=dict(color=COLORS["roas"], width=3),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(79,195,255,0.06)",
            hovertemplate="<b>ROAS</b>: %{y:.2f}x<extra></extra>",
        ), secondary_y=False)

    if "cpc" in df_t.columns:
        fig.add_trace(go.Scatter(
            x=df_t["_date"], y=df_t["cpc"],
            name=f"CPC ({sym})",
            mode="lines+markers",
            line=dict(color=COLORS["cpc"], width=2, dash="dash"),
            marker=dict(size=5),
            hovertemplate=f"<b>CPC</b>: {sym} %{{y:.2f}}<extra></extra>",
        ), secondary_y=True)

    fig.update_layout(
        title=dict(text="🚀 ROAS vs. CPC ao longo do tempo", font=dict(size=15)),
        **CHART_THEME,
    )
    fig.update_yaxes(title_text="ROAS (x)", secondary_y=False, title_font=dict(color=COLORS["roas"]))
    fig.update_yaxes(title_text=f"CPC ({sym})", secondary_y=True, title_font=dict(color=COLORS["cpc"]))
    return fig


def chart_spend_by_campaign(df: pd.DataFrame, sym: str):
    if "campaign_name" not in df.columns or "spend" not in df.columns:
        return None
    grp = (
        df.groupby("campaign_name")["spend"]
        .sum()
        .reset_index()
        .sort_values("spend", ascending=True)
        .tail(12)
    )
    fig = go.Figure(go.Bar(
        x=grp["spend"],
        y=grp["campaign_name"],
        orientation="h",
        marker=dict(
            color=grp["spend"],
            colorscale=[[0, "#2a2a3a"], [0.5, "#7c6aff"], [1, "#ff6a9b"]],
            showscale=False,
        ),
        hovertemplate=f"<b>%{{y}}</b><br>Investimento: {sym} %{{x:,.2f}}<extra></extra>",
    ))
    
    try:
        fig.update_layout(**CHART_THEME)
    except:
        pass 
    
    fig.update_layout(
        title=dict(text="💸 Investimento por Campanha", font=dict(size=15)),
        yaxis=dict(tickfont=dict(size=10), gridcolor="#2a2a3a"),
        xaxis=dict(tickfont=dict(size=11), gridcolor="#2a2a3a"),
        height=int(max(300, len(grp) * 42)), 
    )
    return fig


def chart_funnel(df: pd.DataFrame) -> go.Figure:
    stages, values = [], []
    for col, label in [
        ("impressions", "Impressões"),
        ("reach",       "Alcance"),
        ("clicks",      "Cliques"),
        ("conversions", "Conversões"),
    ]:
        if col in df.columns:
            v = df[col].sum()
            if v > 0:
                stages.append(label)
                values.append(v)

    if len(stages) < 2:
        return None

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent previous",
        marker=dict(color=["#7c6aff", "#a080ff", "#ff6a9b", "#4fffb0"]),
        connector=dict(line=dict(color="#2a2a3a", width=2)),
        hovertemplate="<b>%{y}</b>: %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="🔽 Funil de Performance", font=dict(size=15)),
        **CHART_THEME,
        height=360,
    )
    return fig


# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuração")
    st.markdown("---")

    # Regra 1: st.sidebar.radio com as duas plataformas suportadas.
    # A variável `platform` controla o mapeamento de colunas, a limpeza do
    # CSV e o papel assumido pelo Gemini no prompt.
    platform = st.radio(
        "Escolha a Plataforma",
        options=["Meta Ads", "Google Ads"],
        horizontal=True,
        help="Selecione a origem do CSV para normalização automática das colunas.",
    )
    st.markdown("---")
 
    api_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Obtenha em aistudio.google.com",
    )

    model_choice = st.selectbox(
        "🤖 Modelo Gemini",
        ["gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.5-flash"],
        index=1,
    )

    currency = st.selectbox(
        "💱 Moeda",
        ["BRL (R$)", "USD ($)", "EUR (€)", "GBP (£)"],
        index=0,
    )

    user_goal = st.text_area(
        "🎯 Objetivo da análise",
        placeholder="Ex: Reduzir CPA em campanhas de conversão de e-commerce...",
        height=110,
    )

    st.markdown("---")
    if platform == "Meta Ads":
        st.markdown("""
        <div style='font-family: Space Mono, monospace; font-size: 0.65rem; color: #6b6880; line-height: 1.8'>
        📋 <b>Colunas Meta Ads:</b><br>
        campaign_name · impressions<br>
        clicks · spend · reach<br>
        ctr · cpc · cpm · roas<br>
        conversions · frequency<br>
        ad_name · adset_name
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='font-family: Space Mono, monospace; font-size: 0.65rem; color: #6b6880; line-height: 1.8'>
        📋 <b>Colunas Google Ads:</b><br>
        Campaign / Campanha<br>
        Impr. / Impressões<br>
        Clicks / Cliques<br>
        Cost / Custo<br>
        CTR · Avg. CPC / CPC médio<br>
        Conversions / Conversões<br>
        Conv. value / Valor conv.<br>
        Search Impr. share
        </div>
        """, unsafe_allow_html=True)


# Main
platform_icon = "🟦" if platform == "Meta Ads" else "🟥"
platform_label = platform

st.markdown(f"""
<div class="hero-header">
    <h1>{platform_icon} Marketing Digital Hub</h1>
    <p>Powered by Google Gemini · Analisando: <strong>{platform_label}</strong></p>
</div>
""", unsafe_allow_html=True)

upload_hint = (
    "Arraste ou selecione o CSV exportado do Meta Ads Manager"
    if platform == "Meta Ads"
    else "Arraste ou selecione o CSV exportado do Google Ads (Relatórios → Baixar → CSV)"
)

uploaded_file = st.file_uploader(
    upload_hint,
    type=["csv"],
    label_visibility="visible",
)

if uploaded_file:
    try:
        # Meta Ads usa o loader genérico original.
        if platform == "Google Ads":
            df = clean_google_ads_csv(uploaded_file)
        else:
            df = load_csv(uploaded_file)

        df = normalize_columns(df, platform)
        df = preprocess(df)

    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        st.stop()

    # ── KPI Cards ──────────────────────────────────────────────────────────
    total_spend      = df["spend"].sum()          if "spend"            in df.columns else None
    total_impr       = df["impressions"].sum()    if "impressions"      in df.columns else None
    total_clicks     = df["clicks"].sum()         if "clicks"           in df.columns else None
    avg_ctr          = df["ctr"].mean()           if "ctr"              in df.columns else None
    avg_cpc          = df["cpc"].mean()           if "cpc"              in df.columns else None
    avg_roas         = df["roas"].mean()          if "roas"             in df.columns else None
    total_conv       = df["conversions"].sum()    if "conversions"      in df.columns else None
    total_revenue    = df["conversion_values"].sum() if "conversion_values" in df.columns else None

    sym = currency.split(" ")[1].strip("()")

    cards = []
    if total_spend    is not None: cards.append(("💸 Investimento",  fmt_currency(total_spend, sym), "", "purple"))
    if total_impr     is not None: cards.append(("👁️ Impressões",   fmt_number(total_impr),         "", "pink"))
    if total_clicks   is not None: cards.append(("🖱️ Cliques",      fmt_number(total_clicks),       "", "green"))
    if avg_ctr        is not None: cards.append(("📊 CTR Médio",    fmt_pct(avg_ctr),               "", "yellow"))
    if avg_cpc        is not None: cards.append(("💰 CPC Médio",    fmt_currency(avg_cpc, sym),     "", "purple"))
    if avg_roas       is not None: cards.append(("🚀 ROAS Médio",   f"{avg_roas:.2f}x",             "", "green"))
    if total_conv     is not None: cards.append(("✅ Conversões",   fmt_number(total_conv),          "", "pink"))
    if total_revenue  is not None: cards.append(("💵 Receita",      fmt_currency(total_revenue, sym),"", "yellow"))

    if cards:
        cols_html = "".join(
            f'<div class="kpi-card {color}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>'
            for label, value, sub, color in cards
        )
        st.markdown(f'<div class="kpi-grid">{cols_html}</div>', unsafe_allow_html=True)

    # ── Data preview ───────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Dados Importados</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, height=260)
    st.caption(f"{len(df)} linhas · {len(df.columns)} colunas detectadas")

    # ── Charts ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 Visualizações</div>', unsafe_allow_html=True)

    date_col, date_series = detect_date_col(df)
    has_time = date_col is not None

    if has_time:
        df["_date"] = date_series
        agg_cols = {c: "sum" for c in ["spend", "clicks", "impressions", "conversions", "reach", "conversion_values"]
                    if c in df.columns}
        mean_cols = {c: "mean" for c in ["ctr", "cpc", "cpm", "roas", "frequency"] if c in df.columns}
        agg_cols.update(mean_cols)

        df_t = df.groupby("_date").agg(agg_cols).reset_index().sort_values("_date")

        # ── Row 1: Invest vs Conversions (full width) ──
        if "spend" in df_t.columns:
            fig1 = chart_spend_vs_conversions(df_t, sym)
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

        # ── Row 2: Clicks+CTR | ROAS+CPC ──
        col_a, col_b = st.columns(2)
        with col_a:
            if "clicks" in df_t.columns or "ctr" in df_t.columns:
                st.plotly_chart(
                    chart_clicks_ctr(df_t),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
        with col_b:
            if "roas" in df_t.columns or "cpc" in df_t.columns:
                st.plotly_chart(
                    chart_roas_cpc(df_t, sym),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
    else:
        st.info(
            "💡 Nenhuma coluna de data detectada. Adicione uma coluna `date` ao CSV "
            "para ver os gráficos de linha temporais.",
            icon="📅",
        )

    # ── Row 3: Spend by campaign | Funnel ──
    col_c, col_d = st.columns([3, 2])
    with col_c:
        fig_camp = chart_spend_by_campaign(df, sym)
        if fig_camp:
            st.plotly_chart(fig_camp, use_container_width=True, config={"displayModeBar": False})
    with col_d:
        fig_funnel = chart_funnel(df)
        if fig_funnel:
            st.plotly_chart(fig_funnel, use_container_width=True, config={"displayModeBar": False})

    # ── Analysis button ────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🤖 Análise com IA</div>', unsafe_allow_html=True)

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        run_analysis = st.button("✨ Analisar com Gemini", use_container_width=True)

    if run_analysis:
        if not api_key:
            st.warning("⚠️ Insira sua Gemini API Key na barra lateral.")
        else:
            summary = build_summary(df)
            goal    = user_goal or "Maximizar o desempenho geral das campanhas e reduzir custos."
            prompt  = build_prompt(summary, goal, currency, platform)

            with st.spinner("Gemini está analisando seus dados…"):
                try:
                    analysis = run_gemini_analysis(api_key, prompt, model_choice)

                    st.markdown("""
                    <div class="ai-box">
                        <span class="ai-tag">✦ Gemini AI · Análise de Performance</span>
                    """, unsafe_allow_html=True)
                    st.markdown(analysis)
                    st.markdown("</div>", unsafe_allow_html=True)

                    download_name = (
                        "meta_ads_analysis.txt"
                        if platform == "Meta Ads"
                        else "google_ads_analysis.txt"
                    )
                    st.download_button(
                        label="⬇️ Baixar análise (.txt)",
                        data=analysis.encode("utf-8"),
                        file_name=download_name,
                        mime="text/plain",
                    )
                except Exception as e:
                    st.error(f"Erro na API do Gemini: {e}")

else:

    if platform == "Meta Ads":
        hint_platform = "Meta Ads Manager"
        hint_path     = "Relatórios → Exportar → Formato CSV"
        hint_cols     = "Campanha · Impressões · Cliques · Investimento · CTR"
    else:
        hint_platform = "Google Ads"
        hint_path     = "Relatórios → Baixar ícone → CSV"
        hint_cols     = "Campaign · Impr. · Clicks · Cost · CTR · Conversions"

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 4rem 2rem;
        color: #6b6880;
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
        border: 1px dashed #2a2a3a;
        border-radius: 16px;
        margin-top: 2rem;
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📂</div>
        <div>Faça upload de um CSV exportado do</div>
        <div style="color: #7c6aff; font-weight: 700; margin-top: 0.3rem;">{hint_platform}</div>
        <div style="margin-top: 1rem; font-size: 0.72rem; line-height: 1.8; color: #4a4860">
            {hint_path}<br>
            Inclua: {hint_cols}
        </div>
    </div>
    """, unsafe_allow_html=True)
