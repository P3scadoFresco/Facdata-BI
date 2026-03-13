import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import plotly.graph_objects as go
import pandas as pd
import os

# ── Path resolution ───────────────────────────────────────────────────────────
def find_data_dir():
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_data"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output_data"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "DASHBOARD"),
        "output_data",
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    raise FileNotFoundError("output_data/ não encontrado.")

BASE = find_data_dir()

def load(name):
    try:
        return pd.read_csv(os.path.join(BASE, name))
    except Exception as e:
        print(f"[warn] {name}: {e}")
        return pd.DataFrame()

# ── Substituição de nomes fictícios → nomes reais ─────────────────────────────
NAME_MAP = {
    "Ana":      "Rafael",
    "Carlos":   "Diego",
    "Fernanda": "Marcelo",
    "João":     "Juan",
    "Lucas":    "Gilberto",
    "Marina":   "Renato",
    "ana":      "Rafael",
    "carlos":   "Diego",
    "fernanda": "Marcelo",
    "joão":     "Juan",
    "lucas":    "Gilberto",
    "marina":   "Renato",
}

def remap_names(df, cols=None):
    if df.empty:
        return df
    df = df.copy()
    target_cols = cols if cols else [c for c in df.columns if df[c].dtype == object]
    for col in target_cols:
        if col in df.columns:
            df[col] = df[col].map(lambda v: NAME_MAP.get(str(v), v) if pd.notna(v) else v)
    return df

# ── Substituição de termos em Inglês → Português ─────────────────────────────
TERM_MAP = {
    "Bug Fix": "Correção de Erro",
    "Feature": "Nova Funcionalidade",
    "Research": "Pesquisa",
    "Data Engineering": "Eng. de Dados",
    "Data Analysis": "Análise de Dados",
    "Analytics": "Análises",
    "Dashboard": "Painel",
    "ETL": "Pipeline de Dados (ETL)",
    "Infra": "Infraestrutura",
    "Pipeline": "Automação",
    "High": "Alta",
    "Medium": "Média",
    "Low": "Baixa",
    "Critical": "Crítica",
    "Backlog": "Backlog",
    "To Do": "A Fazer",
    "In Progress": "Em Andamento",
    "Review": "Revisão",
    "QA": "Testes",
    "Done": "Concluído"
}

def translate_terms(df, cols=None):
    if df.empty:
        return df
    df = df.copy()
    target_cols = cols if cols else [c for c in df.columns if df[c].dtype == object]
    for col in target_cols:
        if col in df.columns:
            df[col] = df[col].map(lambda v: TERM_MAP.get(str(v), v) if pd.notna(v) else v)
    return df

# ── Load e remap ──────────────────────────────────────────────────────────────
kpis          = load("painel_1_kpis_kanban.csv")
horas_owner   = remap_names(load("painel_1_horas_owner.csv"), ["owner"])
live_cards    = translate_terms(remap_names(load("painel_1_kanban_live_cards.csv"), ["owner"]))
dev_est       = translate_terms(remap_names(load("painel_2_desvio_estimado_real.csv"), ["owner"]))
owner_act_hrs = translate_terms(remap_names(load("painel_2_owner_activity_hours.csv"), ["owner"]))
owner_month   = remap_names(load("painel_2_owner_monthly_hours.csv"), ["owner"])
alerts_sla    = load("painel_3_alerts_sla.csv")
blocked_cards = translate_terms(remap_names(load("painel_3_blocked_cards.csv"), ["owner"]))
block_reasons = load("painel_3_top_block_reasons.csv")
act_dist      = translate_terms(load("painel_4_activity_distribution.csv"))
avg_time_sub  = translate_terms(load("painel_4_avg_time_subcategory.csv"))
owner_act_stk = translate_terms(remap_names(load("painel_4_owner_activity_stack.csv"), ["owner"]))
weekly_act    = translate_terms(load("painel_4_weekly_activity_evolution.csv"))
perf          = remap_names(load("painel_5_owner_performance.csv"), ["owner"])
reopen        = remap_names(load("painel_5_reopen_analysis.csv"), ["owner"])
throughput    = load("painel_5_throughput_week.csv")
dem_sub       = translate_terms(load("painel_6_demand_subcategory.csv"))
dem_type      = translate_terms(load("painel_6_demand_type.csv"))
weekly_dem    = load("painel_6_weekly_demand.csv")
col_time      = translate_terms(load("painel_7_column_time.csv"))
waiting       = translate_terms(remap_names(load("painel_7_waiting_cards.csv"), ["owner"]))
fin_sub       = translate_terms(load("painel_8_financeiro_subcategoria.csv"))

# ── Tokens de design ──────────────────────────────────────────────────────────
C = {
    "bg":     "#0d1117",
    "card":   "#161b22",
    "border": "#21262d",
    "a1":     "#4493f8",
    "a2":     "#3fb950",
    "a3":     "#d29922",
    "a4":     "#f78166",
    "a5":     "#bc8cff",
    "a6":     "#39c5cf",
    "text":   "#e6edf3",
    "sub":    "#8b949e",
    "green":  "#3fb950",
    "red":    "#f78166",
    "yellow": "#d29922",
}
PAL = [C["a1"],C["a2"],C["a3"],C["a4"],C["a5"],C["a6"],"#ff7b72","#ffa657"]

LB = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C["text"], family="Inter, sans-serif", size=12),
    margin=dict(l=50, r=24, t=48, b=48),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    xaxis=dict(gridcolor=C["border"], linecolor=C["border"], tickfont=dict(size=11)),
    yaxis=dict(gridcolor=C["border"], linecolor=C["border"], tickfont=dict(size=11)),
)

def fl(fig, title="", h=330):
    fig.update_layout(**LB,
        title=dict(text=title, font=dict(size=13, color=C["text"])),
        height=h)
    return fig

# ── Helpers de UI ─────────────────────────────────────────────────────────────
def kcard(label, value, sub="", color=C["a2"], icon="📊"):
    return html.Div([
        html.Div(icon, style={"fontSize":"22px","marginBottom":"6px"}),
        html.Div(str(value), style={"fontSize":"28px","fontWeight":"700",
                                     "color":color,"lineHeight":"1.1"}),
        html.Div(label, style={"fontSize":"11px","color":C["sub"],"marginTop":"4px",
                                "fontWeight":"600","letterSpacing":"0.5px"}),
        html.Div(sub,   style={"fontSize":"10px","color":C["sub"],"marginTop":"2px"}),
    ], style={
        "background":   C["card"],
        "borderRadius": "12px",
        "border":       f"1px solid {C['border']}",
        "padding":      "18px 20px",
        "flex":         "1",
        "minWidth":     "150px",
        "textAlign":    "center",
        "boxShadow":    "0 2px 8px rgba(0,0,0,0.4)",
    })

def cc(fig, sx=None):
    s = {
        "background":   C["card"],
        "borderRadius": "12px",
        "border":       f"1px solid {C['border']}",
        "padding":      "8px",
        "flex":         "1",
        "minWidth":     "280px",
        "boxShadow":    "0 2px 8px rgba(0,0,0,0.4)",
    }
    if sx:
        s.update(sx)
    return html.Div(dcc.Graph(figure=fig, config={"displayModeBar": False}), style=s)

def row(*ch, gap="14px"):
    return html.Div(list(ch),
        style={"display":"flex","gap":gap,"flexWrap":"wrap","marginBottom":"14px"})

def insight_box(text, icon="💡"):
    """Caixa de insight para storytelling — aparece entre seções."""
    return html.Div([
        html.Span(icon, style={"fontSize":"16px","marginRight":"8px"}),
        html.Span(text, style={"fontSize":"12px","color":C["sub"],"lineHeight":"1.5"}),
    ], style={
        "background":   "rgba(68,147,248,0.06)",
        "border":       f"1px solid rgba(68,147,248,0.2)",
        "borderLeft":   f"3px solid {C['a1']}",
        "borderRadius": "8px",
        "padding":      "10px 14px",
        "marginBottom": "14px",
    })

def story_header(title, subtitle):
    """Cabeçalho narrativo da página."""
    return html.Div([
        html.Div(title,    style={"fontSize":"20px","fontWeight":"700",
                                   "color":C["text"],"marginBottom":"4px"}),
        html.Div(subtitle, style={"fontSize":"12px","color":C["sub"],"lineHeight":"1.6"}),
    ], style={
        "background":   "rgba(68,147,248,0.04)",
        "border":       f"1px solid {C['border']}",
        "borderRadius": "12px",
        "padding":      "16px 20px",
        "marginBottom": "16px",
        "borderLeft":   f"4px solid {C['a1']}",
    })

def conclusion_box(text):
    """Caixa de conclusão — sempre no canto inferior direito de cada página."""
    return html.Div([
        html.Div("📌 Conclusão da Página", style={
            "fontSize":"11px","fontWeight":"700","color":C["a3"],
            "letterSpacing":"1px","marginBottom":"6px","textTransform":"uppercase"
        }),
        html.Div(text, style={"fontSize":"12px","color":C["text"],"lineHeight":"1.7"}),
    ], style={
        "background":   "rgba(210,153,34,0.07)",
        "border":       f"1px solid rgba(210,153,34,0.25)",
        "borderLeft":   f"3px solid {C['a3']}",
        "borderRadius": "8px",
        "padding":      "14px 18px",
        "marginTop":    "4px",
        "flex":         "1",
        "minWidth":     "300px",
    })

# ── Helpers para tabelas com status emoji + filtro ────────────────────────────
def status_emoji(row_data, sla_col="status_sla", block_col="is_blocked",
                 blocked_days_col=None, cycle_col=None):
    """
    Retorna 🔴 Crítico / 🟡 Atenção / 🟢 Normal baseado nas colunas disponíveis.
    """
    sla    = str(row_data.get(sla_col, "")).lower()
    blocked= str(row_data.get(block_col, "False")).lower()
    days   = float(row_data.get(blocked_days_col, 0)) if blocked_days_col else 0

    if sla in ("atrasado",) or (blocked == "true" and days > 1):
        return "🔴 Crítico"
    elif sla in ("em risco",) or blocked == "true":
        return "🟡 Atenção"
    else:
        return "🟢 Normal"

def build_table_blocked(df):
    """Tabela de cards bloqueados com coluna de status emoji e colunas em PT."""
    if df.empty:
        return dash_table.DataTable()

    # Mapeia nomes de colunas para PT
    col_rename = {
        "card_id":              "ID",
        "card_title":           "Título do Card",
        "owner":                "Responsável",
        "priority":             "Prioridade",
        "block_reason":         "Motivo do Bloqueio",
        "tempo_bloqueado_dias": "Tempo Bloqueado (dias)",
        "status_sla":           "Status SLA",
        "horas_restantes_sla":  "Horas Restantes SLA",
    }
    display_cols = [c for c in col_rename if c in df.columns]
    df2 = df[display_cols].copy()
    df2.insert(0, "status_icon", df2.apply(
        lambda r: status_emoji(r, sla_col="status_sla",
                                block_col=None,
                                blocked_days_col="tempo_bloqueado_dias"), axis=1))

    renamed = {"status_icon": "Status", **{c: col_rename[c] for c in display_cols}}
    df2.rename(columns=renamed, inplace=True)

    columns = [{"name": v, "id": v} for v in df2.columns]

    return dash_table.DataTable(
        id="tbl-bloqueios",
        data=df2.to_dict("records"),
        columns=columns,
        page_size=12,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto", "borderRadius": "8px"},
        style_header={
            "backgroundColor": C["border"], "color": C["text"],
            "fontWeight": "700", "fontSize": "12px",
            "textAlign": "center", "padding": "10px",
            "borderBottom": f"2px solid {C['a1']}",
        },
        style_cell={
            "backgroundColor": C["card"], "color": C["text"],
            "fontSize": "12px", "padding": "9px 12px",
            "border": f"1px solid {C['border']}",
            "textAlign": "center",
            "maxWidth": "220px", "overflow": "hidden", "textOverflow": "ellipsis",
        },
        style_cell_conditional=[
            {"if": {"column_id": "Título do Card"}, "textAlign": "left"},
            {"if": {"column_id": "Motivo do Bloqueio"}, "textAlign": "left"},
            {"if": {"column_id": "Status"}, "width": "110px", "fontWeight": "600"},
        ],
        style_data_conditional=[
            {"if": {"filter_query": '{Status} = "🔴 Crítico"'},
             "borderLeft": f"3px solid {C['red']}"},
            {"if": {"filter_query": '{Status} = "🟡 Atenção"'},
             "borderLeft": f"3px solid {C['yellow']}"},
            {"if": {"filter_query": '{Status} = "🟢 Normal"'},
             "borderLeft": f"3px solid {C['green']}"},
        ],
    )

def build_table_fluxo(df):
    """Tabela de cards em espera com coluna de status emoji e colunas em PT."""
    if df.empty:
        return dash_table.DataTable()

    col_rename = {
        "card_id":              "ID",
        "card_title":           "Título do Card",
        "owner":                "Responsável",
        "historical_column":    "Coluna Atual",
        "priority":             "Prioridade",
        "status_sla":           "Status SLA",
        "block_reason":         "Motivo Bloqueio",
        "total_cycle_time":     "Cycle Time (h)",
    }
    display_cols = [c for c in col_rename if c in df.columns]
    df2 = df[display_cols].copy()
    df2.insert(0, "status_icon", df2.apply(
        lambda r: status_emoji(r, sla_col="status_sla"), axis=1))

    renamed = {"status_icon": "Status", **{c: col_rename[c] for c in display_cols}}
    df2.rename(columns=renamed, inplace=True)

    columns = [{"name": v, "id": v} for v in df2.columns]

    return dash_table.DataTable(
        id="tbl-fluxo",
        data=df2.to_dict("records"),
        columns=columns,
        page_size=12,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto", "borderRadius": "8px"},
        style_header={
            "backgroundColor": C["border"], "color": C["text"],
            "fontWeight": "700", "fontSize": "12px",
            "textAlign": "center", "padding": "10px",
            "borderBottom": f"2px solid {C['a1']}",
        },
        style_cell={
            "backgroundColor": C["card"], "color": C["text"],
            "fontSize": "12px", "padding": "9px 12px",
            "border": f"1px solid {C['border']}",
            "textAlign": "center",
            "maxWidth": "220px", "overflow": "hidden", "textOverflow": "ellipsis",
        },
        style_cell_conditional=[
            {"if": {"column_id": "Título do Card"}, "textAlign": "left"},
            {"if": {"column_id": "Motivo Bloqueio"}, "textAlign": "left"},
            {"if": {"column_id": "Status"}, "width": "110px", "fontWeight": "600"},
        ],
        style_data_conditional=[
            {"if": {"filter_query": '{Status} = "🔴 Crítico"'},
             "borderLeft": f"3px solid {C['red']}"},
            {"if": {"filter_query": '{Status} = "🟡 Atenção"'},
             "borderLeft": f"3px solid {C['yellow']}"},
            {"if": {"filter_query": '{Status} = "🟢 Normal"'},
             "borderLeft": f"3px solid {C['green']}"},
        ],
    )

def status_filter_bar(tbl_id):
    """Botões de filtro rápido de status (Todos / Crítico / Atenção / Normal)."""
    btn_base = {
        "border": f"1px solid {C['border']}",
        "borderRadius": "20px",
        "padding": "5px 14px",
        "fontSize": "12px",
        "cursor": "pointer",
        "fontWeight": "600",
        "background": C["card"],
        "color": C["sub"],
        "transition": "all .15s",
    }
    return html.Div([
        html.Span("Filtrar por status:", style={"fontSize":"12px","color":C["sub"],
                                                 "marginRight":"8px","alignSelf":"center"}),
        html.Button("Todos",       id=f"f-all-{tbl_id}",   n_clicks=0,
                    style={**btn_base,"color":C["text"],"borderColor":C["a1"]}),
        html.Button("🔴 Crítico",  id=f"f-crit-{tbl_id}",  n_clicks=0,
                    style={**btn_base,"color":C["red"],"borderColor":C["red"]}),
        html.Button("🟡 Atenção",  id=f"f-attn-{tbl_id}",  n_clicks=0,
                    style={**btn_base,"color":C["yellow"],"borderColor":C["yellow"]}),
        html.Button("🟢 Normal",   id=f"f-norm-{tbl_id}",  n_clicks=0,
                    style={**btn_base,"color":C["green"],"borderColor":C["green"]}),
    ], style={"display":"flex","gap":"8px","alignItems":"center",
              "marginBottom":"10px","flexWrap":"wrap"})

def table_card(title, tbl, filter_bar):
    return html.Div([
        html.Div([
            html.H3(title, style={"color":C["text"],"margin":"0","fontSize":"14px",
                                   "fontWeight":"600"}),
        ], style={"marginBottom":"12px","borderLeft":f"3px solid {C['a1']}",
                  "paddingLeft":"10px"}),
        filter_bar,
        tbl,
    ], style={"background":C["card"],"borderRadius":"12px",
              "border":f"1px solid {C['border']}","padding":"16px",
              "boxShadow":"0 2px 8px rgba(0,0,0,0.4)"})

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 1 — Visão Geral Kanban
# ══════════════════════════════════════════════════════════════════════════════
def p_kanban():
    total  = int(kpis["total_cards"].iloc[0])   if not kpis.empty else "—"
    risco  = int(kpis["cards_em_risco"].iloc[0]) if not kpis.empty else "—"
    fech   = int(kpis["cards_fechados_hoje"].iloc[0]) if not kpis.empty else "—"
    owners = len(horas_owner) if not horas_owner.empty else "—"

    # ① Horas investidas + Cards ativos (eixo duplo)
    f1 = go.Figure()
    if not horas_owner.empty:
        f1.add_trace(go.Bar(
            x=horas_owner["owner"], y=horas_owner["total_horas_investidas"],
            name="Horas Investidas", marker_color=C["a1"],
            hovertemplate="<b>%{x}</b><br>Horas: %{y}<extra></extra>"))
        f1.add_trace(go.Scatter(
            x=horas_owner["owner"], y=horas_owner["cards_ativos"],
            mode="lines+markers", yaxis="y2", name="Cards Ativos",
            marker=dict(color=C["a2"], size=9), line=dict(color=C["a2"], width=2),
            hovertemplate="<b>%{x}</b><br>Cards Ativos: %{y}<extra></extra>"))
        f1.update_layout(**LB,
            title=dict(text="① Carga de Trabalho por Membro", font=dict(size=13)),
            height=300,
            yaxis2=dict(overlaying="y", side="right", showgrid=False,
                        tickfont=dict(size=11),
                        title=dict(text="Cards", font=dict(size=11))))

    # ② Status SLA donut
    f2 = go.Figure()
    if not live_cards.empty and "status_sla" in live_cards.columns:
        vc = live_cards["status_sla"].value_counts()
        col_map = {"No prazo":C["green"],"Em risco":C["yellow"],"Atrasado":C["red"]}
        colors = [col_map.get(l, C["a1"]) for l in vc.index]
        f2.add_trace(go.Pie(
            labels=vc.index, values=vc.values, hole=0.58,
            marker_colors=colors,
            hovertemplate="<b>%{label}</b><br>%{value} cards — %{percent}<extra></extra>"))
        fl(f2, "② Distribuição de Status SLA", 300)
        f2.update_layout(showlegend=True, margin=dict(l=10, r=10, t=48, b=10))

    # ③ Scatter Cycle Time vs Desvio
    f3 = go.Figure()
    if not live_cards.empty:
        lc = live_cards.dropna(subset=["total_cycle_time","desvio_horas"])
        for i, col in enumerate(lc["historical_column"].unique()):
            d = lc[lc["historical_column"]==col]
            f3.add_trace(go.Scatter(
                x=d["total_cycle_time"], y=d["desvio_horas"],
                mode="markers", name=col,
                marker=dict(color=PAL[i%len(PAL)], size=7, opacity=.75),
                customdata=d[["card_title","owner","status_sla","priority"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Responsável: %{customdata[1]}<br>"
                    "Cycle Time: %{x}h | Desvio: %{y}h<br>"
                    "SLA: %{customdata[2]} | Prioridade: %{customdata[3]}"
                    "<extra></extra>")))
        fl(f3, "③ Cycle Time vs Desvio — onde estão as entregas problemáticas?", 300)

    # ④ Cards por Prioridade
    f4 = go.Figure()
    if not live_cards.empty and "priority" in live_cards.columns:
        vc = live_cards["priority"].value_counts().reset_index()
        vc.columns = ["priority","count"]
        prio_col = {"Alta":C["red"],"Média":C["yellow"],"Baixa":C["green"],"Crítica":C["a5"], 
                    "High":C["red"],"Medium":C["yellow"],"Low":C["green"],"Critical":C["a5"]}
        f4.add_trace(go.Bar(
            y=vc["priority"], x=vc["count"], orientation="h",
            marker_color=[prio_col.get(p, C["a1"]) for p in vc["priority"]],
            hovertemplate="<b>%{y}</b>: %{x} cards<extra></extra>"))
        fl(f4, "④ Distribuição por Prioridade — qual é o perfil de urgência?", 300)

    return html.Div([
        story_header(
            "Visão Geral do Kanban",
            "Comece pela carga de trabalho de cada membro (①) e veja quem está sobrecarregado. "
            "Avance para o painel de SLA (②) para entender a saúde das entregas. "
            "Desça para identificar os cards com maior desvio e cycle time (③) — são os gargalos do time. "
            "Conclua entendendo o perfil de prioridade dos itens em aberto (④)."
        ),
        row(
            kcard("Total de Cards", total, "ativos no kanban", C["a1"], "📋"),
            kcard("Cards em Risco", risco, "requerem atenção", C["red"], "⚠️"),
            kcard("Fechados Hoje",  fech,  "entregas do dia",  C["green"], "✅"),
            kcard("Membros Ativos", owners,"equipe",           C["a5"], "👥"),
        ),
        insight_box(
            "Membros com alto volume de horas E muitos cards ativos indicam risco de burnout e atrasos. "
            "Observe se o mesmo nome aparece com SLA 'Atrasado' no gráfico ao lado.",
            "👀"
        ),
        row(cc(f1, {"flex":"2","minWidth":"380px"}), cc(f2, {"flex":"1"})),
        insight_box(
            "No scatter abaixo, pontos no quadrante superior direito (alto cycle time E alto desvio) "
            "são os cards mais críticos — considere escalá-los imediatamente.",
            "🎯"
        ),
        row(
            cc(f3, {"flex":"2","minWidth":"380px"}),
            cc(f4, {"flex":"1"}),
        ),
        html.Div(style={"display":"flex","justifyContent":"flex-end"}, children=[
            conclusion_box(
                "A carga está distribuída entre os 6 membros, mas o desvio no scatter revela entregas "
                "acima do estimado em várias colunas do kanban. Cards de alta prioridade sem prazo definido "
                "tendem a ficar represados — priorize a revisão dos itens 'Atrasado' com maior cycle time."
            )
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 2 — Horas & Utilização
# ══════════════════════════════════════════════════════════════════════════════
def p_horas():
    # ① Estimado vs Investido
    f1 = go.Figure()
    if not owner_month.empty:
        f1.add_trace(go.Bar(x=owner_month["owner"], y=owner_month["total_horas_estimadas"],
            name="Estimadas", marker_color=C["a1"],
            hovertemplate="<b>%{x}</b><br>Estimadas: %{y}h<extra></extra>"))
        f1.add_trace(go.Bar(x=owner_month["owner"], y=owner_month["total_horas_investidas"],
            name="Investidas", marker_color=C["a2"],
            hovertemplate="<b>%{x}</b><br>Investidas: %{y}h<extra></extra>"))
        fl(f1, "① Horas Estimadas vs Investidas por Membro", 300)
        f1.update_layout(barmode="group")

    # ② Utilização %
    f2 = go.Figure()
    if not owner_month.empty and "utilizacao_pct" in owner_month.columns:
        bar_c = [C["red"] if v > 100 else C["green"] for v in owner_month["utilizacao_pct"]]
        f2.add_trace(go.Bar(
            x=owner_month["owner"], y=owner_month["utilizacao_pct"],
            marker_color=bar_c,
            hovertemplate="<b>%{x}</b><br>Utilização: %{y:.1f}%<extra></extra>"))
        f2.add_hline(y=100, line_dash="dash", line_color=C["yellow"], annotation_text="Limite 100%")
        fl(f2, "② Utilização (%) — quem está acima do limite?", 300)

    # ③ Stacked por atividade
    f3 = go.Figure()
    if not owner_act_hrs.empty:
        for i, act in enumerate(owner_act_hrs["activity_type"].unique()):
            d = owner_act_hrs[owner_act_hrs["activity_type"]==act]
            f3.add_trace(go.Bar(
                x=d["owner"], y=d["horas_investidas"],
                name=act, marker_color=PAL[i%len(PAL)],
                hovertemplate=f"<b>%{{x}}</b><br>{act}: %{{y}}h<extra></extra>"))
        fl(f3, "③ Composição de Horas por Tipo de Atividade", 300)
        f3.update_layout(barmode="stack")

    # ④ Desvio estimado vs real
    f4 = go.Figure()
    if not dev_est.empty:
        d = dev_est.dropna(subset=["total_cycle_time","desvio_horas_pct"])
        subs = d["subcategory"].unique() if "subcategory" in d.columns else ["—"]
        for i, sub in enumerate(subs):
            dd = d[d["subcategory"]==sub]
            f4.add_trace(go.Scatter(
                x=dd["total_cycle_time"], y=dd["desvio_horas_pct"],
                mode="markers", name=sub,
                marker=dict(color=PAL[i%len(PAL)], size=7, opacity=.7),
                hovertemplate=f"Sub: {sub}<br>Cycle: %{{x}}h | Desvio: %{{y:.1f}}%<extra></extra>"))
        fl(f4, "④ Desvio Estimado vs Real por Card", 300)

    return html.Div([
        story_header(
            "Horas & Utilização da Equipe",
            "Inicie comparando o que foi estimado com o que foi efetivamente investido por cada membro (①). "
            "Avance para a taxa de utilização (②) — vermelho significa sobrecarga. "
            "Entenda como as horas estão distribuídas entre tipos de atividade (③). "
            "Conclua identificando quais cards apresentam maior desvio entre estimativa e realidade (④)."
        ),
        insight_box(
            "Membros com barras 'Investidas' muito maiores que 'Estimadas' em (①) "
            "e percentual acima de 100% em (②) são candidatos a redistribuição de carga.",
            "👀"
        ),
        row(cc(f1, {"flex":"2"}), cc(f2, {"flex":"1"})),
        insight_box(
            "A composição em (③) revela se o time está gastando tempo onde agrega mais valor. "
            "Um volume excessivo de 'Bug Fix' pode indicar problemas de qualidade upstream.",
            "🔍"
        ),
        row(cc(f3, {"flex":"2"}), cc(f4, {"flex":"1"})),
        html.Div(style={"display":"flex","justifyContent":"flex-end"}, children=[
            conclusion_box(
                "A distribuição de horas mostra onde o time concentra esforço. "
                "Desvios positivos altos no scatter (④) indicam cards mal estimados — "
                "refinamentos de backlog com story points mais precisos podem reduzir este gap."
            )
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 3 — Bloqueios & SLA
# ══════════════════════════════════════════════════════════════════════════════
def p_bloqueios():
    # ① Top motivos
    f1 = go.Figure()
    if not block_reasons.empty:
        br = block_reasons.sort_values("num_bloqueios", ascending=True)
        f1.add_trace(go.Bar(
            y=br["block_reason"], x=br["num_bloqueios"], orientation="h",
            marker_color=C["a4"],
            customdata=br[["total_tempo_bloqueado","pct_bloqueios"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>Bloqueios: %{x}<br>"
                "Tempo total: %{customdata[0]:.1f}h | %{customdata[1]:.1f}% dos casos"
                "<extra></extra>")))
        fl(f1, "① Principais Causas de Bloqueio — onde atacar primeiro?", 300)

    # ② Bloqueados vs Livres
    f2 = go.Figure()
    if not live_cards.empty and "is_blocked" in live_cards.columns:
        vc = live_cards["is_blocked"].astype(str).value_counts()
        f2.add_trace(go.Pie(
            labels=["🔒 Bloqueado" if l=="True" else "🟢 Livre" for l in vc.index],
            values=vc.values, hole=0.6,
            marker_colors=[C["red"], C["green"]],
            hovertemplate="<b>%{label}</b>: %{value} cards (%{percent})<extra></extra>"))
        fl(f2, "② Proporção de Cards Bloqueados vs Livres", 300)
        f2.update_layout(margin=dict(l=10, r=10, t=48, b=10))

    # ③ Tempo bloqueado por membro
    f3 = go.Figure()
    if not blocked_cards.empty and "owner" in blocked_cards.columns:
        bo = blocked_cards.groupby("owner")["tempo_bloqueado_dias"].sum().reset_index()
        bo = bo.sort_values("tempo_bloqueado_dias", ascending=False)
        f3.add_trace(go.Bar(
            x=bo["owner"], y=bo["tempo_bloqueado_dias"],
            marker_color=C["a3"],
            hovertemplate="<b>%{x}</b><br>Tempo bloqueado: %{y:.1f} dias<extra></extra>"))
        fl(f3, "③ Quem está sendo mais impactado por bloqueios? (dias)", 260)

    tbl  = build_table_blocked(blocked_cards)
    fbar = status_filter_bar("bloqueios")

    return html.Div([
        story_header(
            "Bloqueios & Conformidade SLA",
            "Identifique primeiro quais causas geram mais bloqueios no time (①). "
            "Confira a proporção atual de cards travados vs fluindo (②). "
            "Veja quem na equipe acumula mais dias perdidos por bloqueio (③). "
            "Na tabela filtre por 🔴 Crítico para agir agora — são os casos mais urgentes."
        ),
        insight_box(
            "Causas com alta frequência E alto tempo acumulado em (①) são as mais danosas. "
            "Priorize resolver dependências externas e bugs de sistema — os dois maiores vilões.",
            "👀"
        ),
        row(cc(f1, {"flex":"2"}), cc(f2, {"flex":"1"})),
        insight_box(
            "Membros com muitos dias bloqueados em (③) não estão entregando por impedimentos, "
            "não por falta de capacidade. Acionar as remoções de bloqueio é responsabilidade do gestor.",
            "🚧"
        ),
        row(cc(f3)),
        table_card(
            "④ Detalhamento de Cards Bloqueados — filtre por status para priorizar ação",
            tbl, fbar
        ),
        html.Div(style={"display":"flex","justifyContent":"flex-end","marginTop":"14px"},
                 children=[
            conclusion_box(
                "Bloqueios concentrados em poucos motivos indicam problemas sistêmicos, não pontuais. "
                "Resolva a causa raiz (dependências externas, infraestrutura) e o tempo perdido cairá "
                "de forma significativa para toda a equipe. Filtre por 🔴 Crítico na tabela e "
                "inicie a remoção de impedimentos ainda hoje."
            )
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 4 — Atividades
# ══════════════════════════════════════════════════════════════════════════════
def p_atividades():
    # ① Donut de horas
    f1 = go.Figure()
    if not act_dist.empty:
        f1.add_trace(go.Pie(
            labels=act_dist["activity_type"], values=act_dist["total_horas"],
            hole=0.52, marker_colors=PAL,
            customdata=act_dist[["num_cards","pct_horas"]].values,
            hovertemplate="<b>%{label}</b><br>Horas: %{value}<br>Cards: %{customdata[0]} | %{customdata[1]:.1f}%<extra></extra>"))
        fl(f1, "① Onde o time gasta as horas?", 310)
        f1.update_layout(margin=dict(l=10, r=10, t=48, b=10))

    # ② Tempo médio por subcategoria
    f2 = go.Figure()
    if not avg_time_sub.empty:
        f2.add_trace(go.Bar(
            x=avg_time_sub["subcategory"], y=avg_time_sub["tempo_medio_dias"],
            marker_color=C["a2"],
            error_y=dict(type="data", array=avg_time_sub["desvio_padrao_dias"].tolist(),
                         color=C["sub"], thickness=1.5, width=4),
            customdata=avg_time_sub[["tempo_min_dias","tempo_max_dias"]].values,
            hovertemplate="<b>%{x}</b><br>Médio: %{y:.2f} dias<br>Min: %{customdata[0]:.2f} | Max: %{customdata[1]:.2f}<extra></extra>"))
        fl(f2, "② Tempo Médio por Subcategoria — qual demora mais?", 310)

    # ③ Evolução semanal stacked area
    f3 = go.Figure()
    if not weekly_act.empty:
        for i, act in enumerate(weekly_act["activity_type"].unique()):
            d = weekly_act[weekly_act["activity_type"]==act].sort_values("created_week")
            f3.add_trace(go.Scatter(
                x=d["created_week"], y=d["horas_investidas"],
                mode="lines", name=act, stackgroup="one",
                line=dict(color=PAL[i%len(PAL)], width=1.5),
                hovertemplate=f"Sem %{{x}}<br>{act}: %{{y}}h<extra></extra>"))
        fl(f3, "③ Evolução Semanal por Tipo de Atividade", 310)

    # ④ Heatmap
    f4 = go.Figure()
    if not owner_act_stk.empty:
        pivot = owner_act_stk.pivot_table(
            index="owner", columns="activity_type",
            values="horas_investidas", fill_value=0)
        f4.add_trace(go.Heatmap(
            z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
            colorscale="Blues",
            hovertemplate="<b>%{y}</b> → %{x}: %{z}h<extra></extra>"))
        fl(f4, "④ Heatmap: Membro × Tipo de Atividade — quem faz o quê?", 310)

    return html.Div([
        story_header(
            "Distribuição e Evolução das Atividades",
            "Entenda onde vai a energia do time: o donut (①) mostra o peso de cada atividade. "
            "Veja quais subcategorias demoram mais para fechar (②). "
            "Acompanhe se o perfil de trabalho mudou ao longo das semanas (③). "
            "Conclua identificando especialistas e gargalos individuais no heatmap (④)."
        ),
        insight_box(
            "Se 'Bug Fix' dominar o donut (①), o time está em modo reativo. "
            "Ciclos saudáveis têm maior proporção de 'Feature' e 'Data Analysis'.",
            "👀"
        ),
        row(cc(f1, {"flex":"1"}), cc(f2, {"flex":"2"})),
        insight_box(
            "Subcategorias com alto desvio padrão em (②) indicam imprevisibilidade — "
            "candidatas a refinamento de processos e estimativas.",
            "📐"
        ),
        row(cc(f3, {"flex":"2"}), cc(f4, {"flex":"1"})),
        html.Div(style={"display":"flex","justifyContent":"flex-end"}, children=[
            conclusion_box(
                "O heatmap (④) revela se há concentração de conhecimento em poucos membros — "
                "risco de bus factor. Subcategorias com tempo médio alto e alta variância "
                "precisam de processos mais definidos para reduzir incerteza."
            )
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 5 — Performance
# ══════════════════════════════════════════════════════════════════════════════
def p_performance():
    # ① Cards concluídos
    f1 = go.Figure()
    if not perf.empty:
        perf_s = perf.sort_values("cards_concluidos", ascending=False)
        f1.add_trace(go.Bar(
            x=perf_s["owner"], y=perf_s["cards_concluidos"],
            marker_color=C["a1"],
            hovertemplate="<b>%{x}</b><br>Concluídos: %{y}<extra></extra>"))
        fl(f1, "① Quem entregou mais? — Cards Concluídos", 300)

    # ② Lead Time
    f2 = go.Figure()
    if not perf.empty:
        f2.add_trace(go.Scatter(
            x=perf["owner"], y=perf["lead_time_medio"],
            mode="lines+markers", name="Lead Time Médio",
            marker=dict(color=C["a2"], size=10), line=dict(color=C["a2"], width=2),
            hovertemplate="<b>%{x}</b><br>Médio: %{y:.2f} dias<extra></extra>"))
        f2.add_trace(go.Scatter(
            x=perf["owner"], y=perf["lead_time_mediano"],
            mode="lines+markers", name="Lead Time Mediano",
            marker=dict(color=C["a3"], size=10), line=dict(color=C["a3"], width=2),
            hovertemplate="<b>%{x}</b><br>Mediano: %{y:.2f} dias<extra></extra>"))
        fl(f2, "② Lead Time por Membro — quanto tempo da criação à entrega?", 300)

    # ③ Taxa de reabertura
    f3 = go.Figure()
    if not reopen.empty:
        rop_s = reopen.sort_values("taxa_reabertura_pct", ascending=False)
        f3.add_trace(go.Bar(
            x=rop_s["owner"], y=rop_s["taxa_reabertura_pct"],
            marker_color=C["a4"],
            customdata=rop_s["total_reaberturas"].tolist(),
            hovertemplate="<b>%{x}</b><br>Taxa: %{y:.1f}%<br>Reaberturas: %{customdata}<extra></extra>"))
        f3.add_hline(y=100, line_dash="dash", line_color=C["yellow"], annotation_text="100%")
        fl(f3, "③ Taxa de Reabertura — indicador de qualidade das entregas", 300)

    # ④ Throughput semanal
    f4 = go.Figure()
    if not throughput.empty:
        f4.add_trace(go.Scatter(
            x=throughput["closed_at"], y=throughput["cards_entregues"],
            mode="lines+markers+text",
            marker=dict(color=C["a2"], size=8),
            line=dict(color=C["a2"], width=2.5),
            fill="tozeroy", fillcolor="rgba(63,185,80,0.1)",
            text=throughput["cards_entregues"], textposition="top center",
            hovertemplate="Semana: %{x}<br>Cards entregues: %{y}<extra></extra>"))
        fl(f4, "④ Throughput Semanal — o ritmo do time ao longo do tempo", 300)
        f4.update_layout(xaxis=dict(tickangle=-45))

    return html.Div([
        story_header(
            "Performance da Equipe",
            "Comece vendo quem entregou mais cards no período (①). "
            "Analise o lead time (②) — menor é melhor, mas diferença entre médio e mediano indica outliers. "
            "Cards reabertos (③) são um indicador de qualidade: alta taxa sinaliza entregas incompletas. "
            "Encerre observando o ritmo de entrega do time semana a semana (④)."
        ),
        insight_box(
            "Alta produtividade em (①) com alto lead time em (②) pode indicar cards muito grandes — "
            "considere quebrar as demandas em itens menores para aumentar o fluxo.",
            "👀"
        ),
        row(cc(f1), cc(f2)),
        insight_box(
            "Taxa de reabertura acima de 50% em (③) é um sinal claro: a definição de 'pronto' "
            "precisa ser revisada com a equipe. Acordos de DoD (Definition of Done) reduzem esse número.",
            "🔁"
        ),
        row(cc(f3), cc(f4)),
        html.Div(style={"display":"flex","justifyContent":"flex-end"}, children=[
            conclusion_box(
                "Performance não é só quantidade: um membro com menos cards concluídos mas "
                "lead time menor e taxa de reabertura baixa agrega mais valor. "
                "O throughput semanal (④) revela se o time está em tendência de melhora ou queda — "
                "use essa linha para planejar sprints e capacidade futura."
            )
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 6 — Demanda
# ══════════════════════════════════════════════════════════════════════════════
def p_demanda():
    # ① Tipo
    f1 = go.Figure()
    if not dem_type.empty:
        f1.add_trace(go.Pie(
            labels=dem_type["type"], values=dem_type["total_cards"],
            hole=0.52, marker_colors=PAL,
            customdata=dem_type["pct_total"].values,
            hovertemplate="<b>%{label}</b><br>Cards: %{value} | %{customdata:.1f}%<extra></extra>"))
        fl(f1, "① Mix de Demanda — o que chega para o time?", 310)
        f1.update_layout(margin=dict(l=10, r=10, t=48, b=10))

    # ② Subcategoria
    f2 = go.Figure()
    if not dem_sub.empty:
        ds = dem_sub.sort_values("total_cards", ascending=False)
        f2.add_trace(go.Bar(
            x=ds["subcategory"], y=ds["total_cards"],
            marker_color=C["a5"],
            hovertemplate="<b>%{x}</b><br>Cards: %{y}<extra></extra>"))
        fl(f2, "② Volume por Subcategoria — onde o time mais trabalha?", 310)

    # ③ Criação semanal
    f3 = go.Figure()
    if not weekly_dem.empty:
        f3.add_trace(go.Scatter(
            x=weekly_dem["created_at"], y=weekly_dem["cards_criados"],
            mode="lines+markers+text",
            marker=dict(color=C["a3"], size=8),
            line=dict(color=C["a3"], width=2.5),
            fill="tozeroy", fillcolor="rgba(210,153,34,0.1)",
            text=weekly_dem["cards_criados"], textposition="top center",
            hovertemplate="Semana: %{x}<br>Cards criados: %{y}<extra></extra>"))
        fl(f3, "③ Criação Semanal de Cards — a demanda está crescendo?", 310)
        f3.update_layout(xaxis=dict(tickangle=-45))

    return html.Div([
        story_header(
            "Análise de Demanda",
            "Entenda o perfil da demanda que chega ao time: o donut (①) mostra se Bug, Feature ou "
            "Data Request dominam. Veja quais subcategorias concentram mais volume (②). "
            "Acompanhe se a demanda está crescendo, estável ou caindo semana a semana (③) — "
            "isso é essencial para planejamento de capacidade."
        ),
        insight_box(
            "Se 'Bug' representar mais de 30% do donut (①), o time opera em modo apagador de incêndio. "
            "Isso compromete capacidade para features estratégicas.",
            "👀"
        ),
        row(cc(f1, {"flex":"1"}), cc(f2, {"flex":"2"})),
        insight_box(
            "Semanas com pico de criação em (③) sem aumento proporcional no throughput (veja Página 5) "
            "resultam em acúmulo de backlog — antecipe ajustando a capacidade do time.",
            "📈"
        ),
        row(cc(f3)),
        html.Div(style={"display":"flex","justifyContent":"flex-end"}, children=[
            conclusion_box(
                "O equilíbrio entre tipo de demanda e subcategoria revela o foco estratégico do time. "
                "Demanda crescente sem crescimento equivalente de throughput gera dívida de backlog. "
                "Use estas métricas para argumentar por aumento de headcount ou redução de escopo."
            )
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 7 — Fluxo & Gargalos
# ══════════════════════════════════════════════════════════════════════════════
def p_fluxo():
    # ① Tempo por coluna
    f1 = go.Figure()
    if not col_time.empty:
        ct = col_time.sort_values("tempo_medio", ascending=True)
        f1.add_trace(go.Bar(
            y=ct["historical_column"], x=ct["tempo_medio"], orientation="h",
            marker_color=C["a1"],
            customdata=ct[["num_cards","tempo_total"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>Tempo médio: %{x:.1f}h<br>"
                "Cards: %{customdata[0]} | Total acumulado: %{customdata[1]:.0f}h"
                "<extra></extra>")))
        fl(f1, "① Tempo Médio por Coluna — onde os cards ficam presos?", 310)

    # ② Funil
    f2 = go.Figure()
    if not col_time.empty:
        f2.add_trace(go.Funnel(
            y=col_time["historical_column"], x=col_time["num_cards"],
            textinfo="value+percent initial",
            marker=dict(color=PAL[:len(col_time)])))
        fl(f2, "② Funil de Cards por Coluna — há gargalo visível?", 310)

    tbl  = build_table_fluxo(waiting)
    fbar = status_filter_bar("fluxo")

    return html.Div([
        story_header(
            "Fluxo do Kanban & Gargalos",
            "Inicie identificando em qual coluna os cards demoram mais (①) — esta é a restrição do sistema. "
            "O funil (②) mostra se há acúmulo desproporcionado em alguma etapa. "
            "Na tabela abaixo, filtre por 🔴 Crítico para visualizar cards parados há mais tempo "
            "com SLA em risco — esses precisam de ação imediata."
        ),
        insight_box(
            "A coluna com maior tempo médio em (①) é o gargalo principal. "
            "Toda melhoria feita fora do gargalo é desperdício — concentre energia aqui primeiro.",
            "👀"
        ),
        row(cc(f1, {"flex":"2"}), cc(f2, {"flex":"1"})),
        insight_box(
            "Diferença grande entre o funil (②) e a coluna final indica que muitos cards "
            "estão presos no meio do processo. Revise critérios de entrada e saída de cada etapa.",
            "🔄"
        ),
        table_card(
            "③ Cards em Espera — filtre por status para priorizar desbloqueio",
            tbl, fbar
        ),
        html.Div(style={"display":"flex","justifyContent":"flex-end","marginTop":"14px"},
                 children=[
            conclusion_box(
                "Gargalos no fluxo são a principal causa de atrasos de entrega. "
                "Limitar o WIP (Work In Progress) na coluna gargalo e aumentar o foco "
                "nela — ao invés de abrir novos cards — é a receita do Kanban para aumentar "
                "throughput sem adicionar headcount. Atue nos 🔴 Críticos da tabela agora."
            )
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 8 — Financeiro
# ══════════════════════════════════════════════════════════════════════════════
def p_financeiro():
    # ① Barras agrupadas
    f1 = go.Figure()
    if not fin_sub.empty:
        for col, name, color in [
            ("receita_total","Receita",C["a2"]),
            ("custo_total",  "Custo",  C["a4"]),
            ("lucro",        "Lucro",  C["a1"]),
        ]:
            f1.add_trace(go.Bar(
                x=fin_sub["subcategory"], y=fin_sub[col],
                name=name, marker_color=color,
                hovertemplate=f"<b>%{{x}}</b><br>{name}: R$ %{{y:,.0f}}<extra></extra>"))
        fl(f1, "① Receita, Custo e Lucro por Subcategoria", 340)
        f1.update_layout(barmode="group")

    # ② Waterfall
    f2 = go.Figure()
    if not fin_sub.empty:
        total_r = fin_sub["receita_total"].sum()
        total_c = fin_sub["custo_total"].sum()
        total_l = fin_sub["lucro"].sum()
        f2.add_trace(go.Waterfall(
            x=["Receita Total","– Custos","= Lucro Líquido"],
            measure=["absolute","relative","total"],
            y=[total_r, -total_c, total_l],
            connector=dict(line=dict(color=C["border"])),
            increasing=dict(marker_color=C["a2"]),
            decreasing=dict(marker_color=C["a4"]),
            totals=dict(marker_color=C["a1"]),
            hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>"))
        fl(f2, "② Resultado Financeiro Consolidado", 340)

    kr  = f"R$ {fin_sub['receita_total'].sum():,.0f}" if not fin_sub.empty else "—"
    kcu = f"R$ {fin_sub['custo_total'].sum():,.0f}"   if not fin_sub.empty else "—"
    kl  = f"R$ {fin_sub['lucro'].sum():,.0f}"         if not fin_sub.empty else "—"
    mg  = (fin_sub["lucro"].sum()/fin_sub["receita_total"].sum()*100) if not fin_sub.empty else 0
    av  = (live_cards["valor_projeto"].dropna().mean()
           if not live_cards.empty and "valor_projeto" in live_cards.columns else 0)

    return html.Div([
        story_header(
            "Análise Financeira",
            "Inicie pelo resultado por subcategoria (①) — identifique quais linhas de serviço "
            "são mais e menos lucrativas. O waterfall (②) consolida o resultado: "
            "receita total menos custos resulta no lucro líquido do período. "
            "Os KPIs abaixo resumem a saúde financeira em números."
        ),
        row(
            kcard("Receita Total",     kr,              "", C["a2"], "💰"),
            kcard("Custo Total",       kcu,             "", C["red"],"📉"),
            kcard("Lucro Total",       kl,              "", C["a1"], "📈"),
            kcard("Margem (%)",        f"{mg:.1f}%",    "", C["a3"], "🎯"),
            kcard("Valor Médio/Card",  f"R$ {av:,.0f}", "", C["a5"], "🃏"),
        ),
        insight_box(
            "Subcategorias com receita alta mas margem baixa em (①) estão consumindo recursos "
            "desproporcional — considere renegociar escopo ou precificação dessas demandas.",
            "👀"
        ),
        row(cc(f1, {"flex":"2"}), cc(f2, {"flex":"1"})),
        html.Div(style={"display":"flex","justifyContent":"flex-end","marginTop":"14px"},
                 children=[
            conclusion_box(
                "A margem geral reflete a eficiência do time em converter horas investidas em receita. "
                "Cruzar esses números com o lead time (Página 5) e o perfil de atividades (Página 4) "
                "revela onde o time gera mais valor financeiro por hora trabalhada — "
                "o insumo mais importante para decisões de priorização estratégica."
            )
        ]),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  APP LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
PAGES = [
    ("📋 Kanban Geral",    "kanban"),
    ("⏱ Horas & Uso",     "horas"),
    ("🚫 Bloqueios & SLA","bloqueios"),
    ("⚙️ Atividades",      "atividades"),
    ("🏆 Performance",     "performance"),
    ("📥 Demanda",         "demanda"),
    ("🔄 Fluxo",           "fluxo"),
    ("💰 Financeiro",      "financeiro"),
]
PAGE_IDS = [pid for _, pid in PAGES]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "FacData BI"

# Injeta CSS global para remover qualquer borda/margin branca do Dash
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * { box-sizing: border-box; }
            html, body {
                margin: 0 !important;
                padding: 0 !important;
                background: #0d1117 !important;
                border: none !important;
                outline: none !important;
            }
            body > div {
                margin: 0 !important;
                padding: 0 !important;
            }
            /* Remove borda branca do container raiz do Dash */
            #react-entry-point, ._dash-loading {
                margin: 0 !important;
                padding: 0 !important;
                background: #0d1117 !important;
            }
            /* Scrollbar escura */
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: #0d1117; }
            ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: #484f58; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def nav_btn(label, pid):
    return html.Button(
        label,
        id=f"nav-{pid}",
        n_clicks=0,
        style={
            "background":    "transparent",
            "border":        "none",
            "borderBottom":  "3px solid transparent",
            "color":         C["sub"],
            "fontSize":      "12px",
            "fontWeight":    "500",
            "padding":       "10px 16px",
            "cursor":        "pointer",
            "transition":    "all .15s",
            "whiteSpace":    "nowrap",
        }
    )

app.layout = html.Div([
    # ── Header ──────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Span("◆ ", style={"color":C["a1"],"fontSize":"20px"}),
            html.Span("FacData", style={"fontSize":"20px","fontWeight":"800","color":C["text"]}),
            html.Span(" BI", style={"fontSize":"20px","fontWeight":"300","color":C["a1"]}),
        ], style={"display":"flex","alignItems":"center","gap":"2px"}),
        html.Div("Dashboard - Grupo Fácil",
                 style={"color":C["sub"],"fontSize":"11px"}),
    ], style={
        "display":         "flex",
        "justifyContent":  "space-between",
        "alignItems":      "center",
        "padding":         "12px 24px",
        "background":      C["card"],
        "borderBottom":    f"1px solid {C['border']}",
    }),

    # ── Nav ─────────────────────────────────────────────────────────────────
    html.Div(
        [nav_btn(lbl, pid) for lbl, pid in PAGES],
        id="nav-bar",
        style={
            "display":      "flex",
            "flexWrap":     "wrap",
            "padding":      "0 16px",
            "background":   C["card"],
            "borderBottom": f"2px solid {C['border']}",
            "gap":          "0px",
        }
    ),

    # ── Content ─────────────────────────────────────────────────────────────
    html.Div(
        id="page-content",
        style={"padding":"20px 24px","minHeight":"calc(100vh - 108px)"}
    ),

    dcc.Store(id="current-page", data="kanban"),

], style={
    "fontFamily": "Inter, system-ui, -apple-system, sans-serif",
    "background":  C["bg"],
    "minHeight":   "100vh",
    "color":       C["text"],
    "margin":      "0",
    "padding":     "0",
})

# ── Callbacks ─────────────────────────────────────────────────────────────────

# 1) Atualiza página
@app.callback(
    Output("current-page","data"),
    [Input(f"nav-{pid}","n_clicks") for pid in PAGE_IDS],
    prevent_initial_call=True,
)
def set_page(*_):
    ctx = callback_context
    if not ctx.triggered:
        return "kanban"
    return ctx.triggered[0]["prop_id"].split(".")[0].replace("nav-","")

# 2) Atualiza visual do botão ativo (highlight)
@app.callback(
    [Output(f"nav-{pid}","style") for pid in PAGE_IDS],
    Input("current-page","data"),
)
def highlight_nav(current):
    styles = []
    for pid in PAGE_IDS:
        if pid == current:
            styles.append({
                "background":    "transparent",
                "border":        "none",
                "borderBottom":  f"3px solid {C['a1']}",
                "color":         C["text"],
                "fontSize":      "12px",
                "fontWeight":    "700",
                "padding":       "10px 16px",
                "cursor":        "pointer",
                "whiteSpace":    "nowrap",
            })
        else:
            styles.append({
                "background":    "transparent",
                "border":        "none",
                "borderBottom":  "3px solid transparent",
                "color":         C["sub"],
                "fontSize":      "12px",
                "fontWeight":    "500",
                "padding":       "10px 16px",
                "cursor":        "pointer",
                "transition":    "all .15s",
                "whiteSpace":    "nowrap",
            })
    return styles

# 3) Renderiza conteúdo da página
@app.callback(
    Output("page-content","children"),
    Input("current-page","data"),
)
def render(page):
    m = {
        "kanban":      p_kanban,
        "horas":       p_horas,
        "bloqueios":   p_bloqueios,
        "atividades":  p_atividades,
        "performance": p_performance,
        "demanda":     p_demanda,
        "fluxo":       p_fluxo,
        "financeiro":  p_financeiro,
    }
    return m.get(page, p_kanban)()

# 4) Filtro de status — Tabela Bloqueios
@app.callback(
    Output("tbl-bloqueios","filter_query"),
    [Input("f-all-bloqueios","n_clicks"),
     Input("f-crit-bloqueios","n_clicks"),
     Input("f-attn-bloqueios","n_clicks"),
     Input("f-norm-bloqueios","n_clicks")],
    prevent_initial_call=True,
)
def filter_bloqueios(all_, crit, attn, norm):
    ctx = callback_context
    if not ctx.triggered:
        return ""
    btn = ctx.triggered[0]["prop_id"].split(".")[0]
    return {
        "f-all-bloqueios":  "",
        "f-crit-bloqueios": '{Status} = "🔴 Crítico"',
        "f-attn-bloqueios": '{Status} = "🟡 Atenção"',
        "f-norm-bloqueios": '{Status} = "🟢 Normal"',
    }.get(btn, "")

# 5) Filtro de status — Tabela Fluxo
@app.callback(
    Output("tbl-fluxo","filter_query"),
    [Input("f-all-fluxo","n_clicks"),
     Input("f-crit-fluxo","n_clicks"),
     Input("f-attn-fluxo","n_clicks"),
     Input("f-norm-fluxo","n_clicks")],
    prevent_initial_call=True,
)
def filter_fluxo(all_, crit, attn, norm):
    ctx = callback_context
    if not ctx.triggered:
        return ""
    btn = ctx.triggered[0]["prop_id"].split(".")[0]
    return {
        "f-all-fluxo":  "",
        "f-crit-fluxo": '{Status} = "🔴 Crítico"',
        "f-attn-fluxo": '{Status} = "🟡 Atenção"',
        "f-norm-fluxo": '{Status} = "🟢 Normal"',
    }.get(btn, "")

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)