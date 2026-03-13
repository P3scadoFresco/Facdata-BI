import dash
from dash import dcc, html, Input, Output, dash_table, callback_context
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

# ── Mapeamento de nomes ───────────────────────────────────────────────────────
NAME_MAP = {
    "Ana":"Rafael","Carlos":"Diego","Fernanda":"Marcelo",
    "João":"Juan","Lucas":"Gilberto","Marina":"Renato",
    "ana":"Rafael","carlos":"Diego","fernanda":"Marcelo",
    "joão":"Juan","lucas":"Gilberto","marina":"Renato",
}

def remap_names(df, cols=None):
    if df.empty: return df
    df = df.copy()
    for col in (cols or [c for c in df.columns if df[c].dtype == object]):
        if col in df.columns:
            df[col] = df[col].map(lambda v: NAME_MAP.get(str(v), v) if pd.notna(v) else v)
    return df

# ── Tradução de termos ────────────────────────────────────────────────────────
TERM_MAP = {
    "Bug Fix":"Correção de Erro","Feature":"Nova Funcionalidade",
    "Research":"Pesquisa","Data Engineering":"Eng. de Dados",
    "Data Analysis":"Análise de Dados","Analytics":"Análises",
    "Dashboard":"Painel","ETL":"Pipeline de Dados (ETL)",
    "Infra":"Infraestrutura","Pipeline":"Automação",
    "High":"Alta","Medium":"Média","Low":"Baixa","Critical":"Crítica",
    "Backlog":"Backlog","To Do":"A Fazer","In Progress":"Em Andamento",
    "Review":"Revisão","QA":"Testes","Done":"Concluído",
}

def translate_terms(df, cols=None):
    if df.empty: return df
    df = df.copy()
    for col in (cols or [c for c in df.columns if df[c].dtype == object]):
        if col in df.columns:
            df[col] = df[col].map(lambda v: TERM_MAP.get(str(v), v) if pd.notna(v) else v)
    return df

# ── Load & remap ──────────────────────────────────────────────────────────────
kpis          = load("painel_1_kpis_kanban.csv")
horas_owner   = remap_names(load("painel_1_horas_owner.csv"), ["owner"])
live_cards    = translate_terms(remap_names(load("painel_1_kanban_live_cards.csv"), ["owner"]))
dev_est       = translate_terms(remap_names(load("painel_2_desvio_estimado_real.csv"), ["owner"]))
owner_act_hrs = translate_terms(remap_names(load("painel_2_owner_activity_hours.csv"), ["owner"]))
owner_month   = remap_names(load("painel_2_owner_monthly_hours.csv"), ["owner"])
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

# ── Design tokens ─────────────────────────────────────────────────────────────
C = {
    "bg":"#0d1117","card":"#161b22","border":"#21262d",
    "a1":"#4493f8","a2":"#3fb950","a3":"#d29922",
    "a4":"#f78166","a5":"#bc8cff","a6":"#39c5cf",
    "text":"#e6edf3","sub":"#8b949e",
    "green":"#3fb950","red":"#f78166","yellow":"#d29922",
}
PAL = [C["a1"],C["a2"],C["a3"],C["a4"],C["a5"],C["a6"],"#ff7b72","#ffa657"]

LB = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C["text"], family="Inter, sans-serif", size=12),
    margin=dict(l=50, r=24, t=48, b=48),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    xaxis=dict(gridcolor=C["border"], linecolor=C["border"], tickfont=dict(size=11)),
    yaxis=dict(gridcolor=C["border"], linecolor=C["border"], tickfont=dict(size=11)),
)

def fl(fig, title="", h=330):
    fig.update_layout(**LB,
        title=dict(text=title, font=dict(size=13, color=C["text"])), height=h)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  TOOLTIP SYSTEM
#  Cada gráfico e cada página têm um ícone ℹ️ que ao hover mostra o texto
#  explicativo / insight / conclusão. Nada aparece fixo na tela.
# ══════════════════════════════════════════════════════════════════════════════

def tooltip_icon(tip_id, text, position="right"):
    """
    Ícone ℹ️ com tooltip puro CSS — sem JS, sem callbacks.
    Ao passar o mouse aparece a caixa com o texto explicativo.
    position: 'right' | 'left' | 'bottom'
    """
    pos_style = {
        "right":  {"left":"28px","top":"50%","transform":"translateY(-50%)"},
        "left":   {"right":"28px","top":"50%","transform":"translateY(-50%)"},
        "bottom": {"left":"50%","top":"28px","transform":"translateX(-50%)"},
    }.get(position, {"left":"28px","top":"50%","transform":"translateY(-50%)"})

    return html.Div([
        # O ícone
        html.Span("ℹ", style={
            "fontSize":"13px","color":C["sub"],"cursor":"help",
            "fontWeight":"700","fontStyle":"italic","fontFamily":"serif",
            "display":"inline-block","width":"18px","height":"18px",
            "lineHeight":"18px","textAlign":"center",
            "border":f"1px solid {C['sub']}","borderRadius":"50%",
            "userSelect":"none",
        }),
        # A caixa de tooltip (hidden por padrão via CSS class)
        html.Div(text, className="tt-box", style={
            "position":"absolute",
            "zIndex":"9999",
            "background":"#1c2128",
            "border":f"1px solid {C['a1']}",
            "borderLeft":f"3px solid {C['a1']}",
            "borderRadius":"8px",
            "padding":"12px 14px",
            "fontSize":"12px",
            "color":C["text"],
            "lineHeight":"1.6",
            "width":"320px",
            "pointerEvents":"none",
            "boxShadow":"0 8px 24px rgba(0,0,0,0.6)",
            **pos_style,
        }),
    ], className="tt-wrap", style={
        "position":"relative","display":"inline-flex",
        "alignItems":"center","marginLeft":"8px","verticalAlign":"middle",
    })

def chart_title_with_tip(title, tip_id, tip_text, position="right"):
    """Título do gráfico inline com o ícone de tooltip ao lado."""
    return html.Div([
        html.Span(title, style={"fontSize":"13px","color":C["text"],"fontWeight":"600"}),
        tooltip_icon(tip_id, tip_text, position),
    ], style={"padding":"4px 8px 0 8px","marginBottom":"-8px","display":"flex","alignItems":"center"})

def page_header(page_title, tip_text):
    """Cabeçalho limpo da página com ícone de tooltip para o 'roteiro de leitura'."""
    return html.Div([
        html.Div([
            html.Div([
                html.Span("◈ ", style={"color":C["a1"],"fontSize":"16px"}),
                html.Span(page_title, style={
                    "fontSize":"16px","fontWeight":"700","color":C["text"]
                }),
            ], style={"display":"flex","alignItems":"center","gap":"2px"}),
            tooltip_icon(f"ph-{page_title}", tip_text, "bottom"),
        ], style={"display":"flex","alignItems":"center","gap":"4px"}),
    ], style={
        "padding":"10px 16px",
        "marginBottom":"14px",
        "background":C["card"],
        "borderRadius":"10px",
        "border":f"1px solid {C['border']}",
        "borderLeft":f"3px solid {C['a1']}",
    })

# ── CSS global (tooltip + reset de bordas) ────────────────────────────────────
TOOLTIP_CSS = """
    * { box-sizing: border-box; }
    html, body {
        margin: 0 !important; padding: 0 !important;
        background: #0d1117 !important;
        border: none !important; outline: none !important;
    }
    body > div { margin: 0 !important; padding: 0 !important; }
    #react-entry-point, ._dash-loading {
        margin: 0 !important; padding: 0 !important;
        background: #0d1117 !important;
    }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #484f58; }

    /* ── Tooltip ── */
    .tt-wrap .tt-box { opacity: 0; visibility: hidden; transition: opacity .18s ease; }
    .tt-wrap:hover .tt-box { opacity: 1; visibility: visible; }
"""

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
        "background":C["card"],"borderRadius":"12px","border":f"1px solid {C['border']}",
        "padding":"18px 20px","flex":"1","minWidth":"150px","textAlign":"center",
        "boxShadow":"0 2px 8px rgba(0,0,0,0.4)",
    })

def cc(content, sx=None):
    """Wrapper de card para gráfico OU conteúdo HTML (quando passado como Div)."""
    s = {
        "background":C["card"],"borderRadius":"12px","border":f"1px solid {C['border']}",
        "padding":"8px","flex":"1","minWidth":"280px",
        "boxShadow":"0 2px 8px rgba(0,0,0,0.4)",
    }
    if sx: s.update(sx)
    if isinstance(content, go.Figure):
        inner = dcc.Graph(figure=content, config={"displayModeBar":False})
    else:
        inner = content
    return html.Div(inner, style=s)

def cc_titled(title, tip_id, tip_text, fig, sx=None, tip_pos="right"):
    """Card com título+tooltip acima do gráfico."""
    s = {
        "background":C["card"],"borderRadius":"12px","border":f"1px solid {C['border']}",
        "padding":"10px 8px 8px 8px","flex":"1","minWidth":"280px",
        "boxShadow":"0 2px 8px rgba(0,0,0,0.4)",
    }
    if sx: s.update(sx)
    return html.Div([
        chart_title_with_tip(title, tip_id, tip_text, tip_pos),
        dcc.Graph(figure=fig, config={"displayModeBar":False}),
    ], style=s)

def row(*ch, gap="14px"):
    return html.Div(list(ch),
        style={"display":"flex","gap":gap,"flexWrap":"wrap","marginBottom":"14px"})

def table_card(title, tip_text, tbl, filter_bar):
    return html.Div([
        html.Div([
            html.Div([
                html.H3(title, style={"color":C["text"],"margin":"0","fontSize":"13px","fontWeight":"600"}),
                tooltip_icon(f"tbl-{title[:10]}", tip_text, "right"),
            ], style={"display":"flex","alignItems":"center","gap":"4px"}),
        ], style={"marginBottom":"10px","borderLeft":f"3px solid {C['a1']}","paddingLeft":"10px"}),
        filter_bar,
        tbl,
    ], style={"background":C["card"],"borderRadius":"12px",
              "border":f"1px solid {C['border']}","padding":"16px",
              "boxShadow":"0 2px 8px rgba(0,0,0,0.4)"})

# ── Status helpers ────────────────────────────────────────────────────────────
def status_emoji(r, sla_col="status_sla", blocked_days_col=None):
    sla  = str(r.get(sla_col,"")).lower()
    days = float(r.get(blocked_days_col,0)) if blocked_days_col else 0
    if sla == "atrasado" or days > 1: return "🔴 Crítico"
    if sla == "em risco"  or days > 0: return "🟡 Atenção"
    return "🟢 Normal"

_TBL_HEADER = {
    "backgroundColor":C["border"],"color":C["text"],"fontWeight":"700",
    "fontSize":"12px","textAlign":"center","padding":"10px",
    "borderBottom":f"2px solid {C['a1']}",
}
_TBL_CELL = {
    "backgroundColor":C["card"],"color":C["text"],"fontSize":"12px",
    "padding":"9px 12px","border":f"1px solid {C['border']}","textAlign":"center",
    "maxWidth":"220px","overflow":"hidden","textOverflow":"ellipsis",
}
_TBL_COND_STATUS = [
    {"if":{"filter_query":'{Status} = "🔴 Crítico"'},"borderLeft":f"3px solid {C['red']}"},
    {"if":{"filter_query":'{Status} = "🟡 Atenção"'},"borderLeft":f"3px solid {C['yellow']}"},
    {"if":{"filter_query":'{Status} = "🟢 Normal"'},"borderLeft":f"3px solid {C['green']}"},
]

def _base_table(tbl_id, df, col_rename, left_cols, sla_col="status_sla", days_col=None):
    if df.empty: return dash_table.DataTable()
    display = [c for c in col_rename if c in df.columns]
    df2 = df[display].copy()
    df2.insert(0,"status_icon", df2.apply(
        lambda r: status_emoji(r, sla_col=sla_col, blocked_days_col=days_col), axis=1))
    df2.rename(columns={"status_icon":"Status",**{c:col_rename[c] for c in display}}, inplace=True)
    return dash_table.DataTable(
        id=tbl_id,
        data=df2.to_dict("records"),
        columns=[{"name":v,"id":v} for v in df2.columns],
        page_size=12, filter_action="native", sort_action="native",
        style_table={"overflowX":"auto","borderRadius":"8px"},
        style_header=_TBL_HEADER, style_cell=_TBL_CELL,
        style_cell_conditional=[
            *[{"if":{"column_id":c},"textAlign":"left"} for c in left_cols],
            {"if":{"column_id":"Status"},"width":"110px","fontWeight":"600"},
        ],
        style_data_conditional=_TBL_COND_STATUS,
    )

def build_table_blocked(df):
    return _base_table("tbl-bloqueios", df, {
        "card_id":"ID","card_title":"Título do Card","owner":"Responsável",
        "priority":"Prioridade","block_reason":"Motivo do Bloqueio",
        "tempo_bloqueado_dias":"Bloqueado (dias)","status_sla":"Status SLA",
        "horas_restantes_sla":"Horas Restantes SLA",
    }, left_cols=["Título do Card","Motivo do Bloqueio"],
       sla_col="status_sla", days_col="tempo_bloqueado_dias")

def build_table_fluxo(df):
    return _base_table("tbl-fluxo", df, {
        "card_id":"ID","card_title":"Título do Card","owner":"Responsável",
        "historical_column":"Coluna Atual","priority":"Prioridade",
        "status_sla":"Status SLA","block_reason":"Motivo Bloqueio",
        "total_cycle_time":"Cycle Time (h)",
    }, left_cols=["Título do Card","Motivo Bloqueio"], sla_col="status_sla")

def status_filter_bar(tbl_id):
    btn = lambda label,bid,col: html.Button(label, id=bid, n_clicks=0, style={
        "border":f"1px solid {col}","borderRadius":"20px","padding":"5px 14px",
        "fontSize":"12px","cursor":"pointer","fontWeight":"600",
        "background":C["card"],"color":col,"transition":"all .15s",
    })
    return html.Div([
        html.Span("Filtrar:", style={"fontSize":"12px","color":C["sub"],"alignSelf":"center"}),
        btn("Todos",      f"f-all-{tbl_id}",  C["text"]),
        btn("🔴 Crítico", f"f-crit-{tbl_id}", C["red"]),
        btn("🟡 Atenção", f"f-attn-{tbl_id}", C["yellow"]),
        btn("🟢 Normal",  f"f-norm-{tbl_id}", C["green"]),
    ], style={"display":"flex","gap":"8px","alignItems":"center",
              "marginBottom":"10px","flexWrap":"wrap"})

# ══════════════════════════════════════════════════════════════════════════════
#  TEXTOS DOS TOOLTIPS (centralizados aqui para fácil edição)
# ══════════════════════════════════════════════════════════════════════════════
T = {
    # ── Página 1 ──
    "p1_header": (
        "📖 Roteiro desta página:\n"
        "① Carga por membro → veja quem acumula mais horas e cards.\n"
        "② Status SLA → entenda a saúde geral das entregas.\n"
        "③ Cycle Time vs Desvio → identifique cards problemáticos.\n"
        "④ Prioridade → conclua com o perfil de urgência do backlog."
    ),
    "p1_f1": (
        "Membros com horas altas E muitos cards ativos têm risco de burnout. "
        "Compare com o SLA ao lado: se o mesmo nome aparece 'Atrasado', redistribua carga."
    ),
    "p1_f2": (
        "Verde = no prazo | Amarelo = em risco | Vermelho = atrasado. "
        "Uma fatia vermelha grande exige ação imediata na fila de prioridades."
    ),
    "p1_f3": (
        "Quadrante superior direito (alto cycle time + alto desvio) = cards críticos. "
        "Passe o mouse em cada ponto para ver o card, responsável e SLA."
    ),
    "p1_f4": (
        "Alta proporção de 'Alta' ou 'Crítica' sem throughput equivalente "
        "indica promessas impossíveis — revise o backlog com o time."
    ),
    # ── Página 2 ──
    "p2_header": (
        "📖 Roteiro desta página:\n"
        "① Estimado vs Investido → detecte quem extrapolou o planejado.\n"
        "② Utilização % → barras vermelhas = sobrecarga, revise.\n"
        "③ Composição de atividades → o time está em modo reativo?\n"
        "④ Desvio por card → quais cards foram mal estimados?"
    ),
    "p2_f1": (
        "Barras 'Investidas' muito maiores que 'Estimadas' indicam "
        "sub-estimação crônica ou escopo crescente. Candidatos a redistribuição."
    ),
    "p2_f2": (
        "Acima de 100% = sobrecarga. Membros sobrecarregados entregam menos e "
        "com mais erros. A linha tracejada amarela é o limite saudável."
    ),
    "p2_f3": (
        "Alto volume de 'Correção de Erro' = time reativo. "
        "Ciclos saudáveis têm predominância de 'Nova Funcionalidade' e 'Análise de Dados'."
    ),
    "p2_f4": (
        "Pontos com desvio positivo alto = cards que tomaram muito mais tempo que o estimado. "
        "Use para melhorar as estimativas nos próximos refinamentos."
    ),
    # ── Página 3 ──
    "p3_header": (
        "📖 Roteiro desta página:\n"
        "① Causas de bloqueio → onde estão os maiores impedimentos.\n"
        "② Bloqueados vs Livres → qual a proporção atual.\n"
        "③ Impacto por membro → quem perde mais dias bloqueado.\n"
        "④ Tabela → filtre por 🔴 para agir nos casos mais urgentes."
    ),
    "p3_f1": (
        "Causas com alta frequência E alto tempo acumulado são as mais danosas. "
        "Priorize resolver as do topo — atacar a causa raiz libera o maior fluxo."
    ),
    "p3_f2": (
        "Se mais de 30% dos cards estiverem bloqueados, o fluxo está comprometido. "
        "Identifique as causas em (①) e acione as remoções imediatamente."
    ),
    "p3_f3": (
        "Membros com muitos dias bloqueados não entregam por impedimentos — "
        "não por falta de capacidade. Remoção de bloqueios é papel do gestor."
    ),
    "p3_tbl": (
        "Use os botões de filtro para focar nos casos críticos. "
        "Clique nos cabeçalhos para ordenar. A coluna 'Bloqueado (dias)' "
        "mostra quanto tempo já foi perdido por impedimento."
    ),
    # ── Página 4 ──
    "p4_header": (
        "📖 Roteiro desta página:\n"
        "① Distribuição de horas → onde vai a energia do time.\n"
        "② Tempo por subcategoria → qual tipo de demanda consome mais.\n"
        "③ Evolução semanal → o perfil de trabalho está mudando?\n"
        "④ Heatmap → especialistas e riscos de bus factor."
    ),
    "p4_f1": (
        "Se 'Correção de Erro' dominar o donut, o time opera em modo apagador de incêndio. "
        "Ciclos saudáveis têm maior proporção de 'Nova Funcionalidade' e 'Análise de Dados'."
    ),
    "p4_f2": (
        "As barras de erro mostram variância — alta variância significa imprevisibilidade. "
        "Subcategorias imprevisíveis precisam de processos mais definidos."
    ),
    "p4_f3": (
        "Semanas com aumento de 'Correção de Erro' geralmente seguem sprints com "
        "muitas entregas rápidas. O padrão revela ciclos de qualidade do time."
    ),
    "p4_f4": (
        "Células quentes concentradas em 1-2 membros = bus factor alto. "
        "Se esse membro sair, o conhecimento vai junto. Planeje pair programming."
    ),
    # ── Página 5 ──
    "p5_header": (
        "📖 Roteiro desta página:\n"
        "① Cards concluídos → quem entregou mais no período.\n"
        "② Lead Time → quanto tempo da criação à entrega por membro.\n"
        "③ Taxa de reabertura → indicador de qualidade individual.\n"
        "④ Throughput semanal → o ritmo geral do time."
    ),
    "p5_f1": (
        "Quantidade de entregas é só uma parte da performance. "
        "Combine com lead time e reabertura para ter o quadro completo."
    ),
    "p5_f2": (
        "Diferença grande entre Médio e Mediano indica outliers — "
        "cards que demoraram muito mais que o normal. Investigue o motivo."
    ),
    "p5_f3": (
        "Taxa acima de 100% significa que os cards foram reabertos mais vezes "
        "do que o total de cards do membro. Sinal de que 'pronto' precisa ser redefinido."
    ),
    "p5_f4": (
        "Tendência de queda no throughput semanal é um alerta antecipado. "
        "Correlacione com bloqueios (pág. 3) e sobrecarga (pág. 2) para encontrar a causa."
    ),
    # ── Página 6 ──
    "p6_header": (
        "📖 Roteiro desta página:\n"
        "① Mix de demanda → que tipo de trabalho chega ao time.\n"
        "② Volume por subcategoria → onde se concentra o esforço.\n"
        "③ Criação semanal → a demanda está crescendo ou caindo?"
    ),
    "p6_f1": (
        "Mais de 30% de 'Bug' = time em modo reativo. "
        "Mais de 50% de 'Data Request' = time virando suporte — avalie processos de autoatendimento."
    ),
    "p6_f2": (
        "Subcategorias com alto volume e alto tempo médio (ver pág. 4) "
        "são as que mais consomem capacidade — candidatas a otimização ou automação."
    ),
    "p6_f3": (
        "Picos de criação sem aumento proporcional de throughput (pág. 5) "
        "geram acúmulo de backlog. Use este gráfico para argumentar por mais headcount ou menos escopo."
    ),
    # ── Página 7 ──
    "p7_header": (
        "📖 Roteiro desta página:\n"
        "① Tempo por coluna → onde os cards ficam presos (gargalo).\n"
        "② Funil → há acúmulo desproporcional em alguma etapa?\n"
        "③ Tabela → filtre por 🔴 para agir nos cards parados mais tempo."
    ),
    "p7_f1": (
        "A coluna com maior tempo médio é o gargalo do sistema. "
        "Toda melhoria feita fora do gargalo é desperdício — foque aqui primeiro."
    ),
    "p7_f2": (
        "Funil com 'pescoço' em etapas intermediárias indica critérios de saída mal definidos. "
        "Revise a Definition of Done de cada coluna com o time."
    ),
    "p7_tbl": (
        "Filtre por 🔴 Crítico para ver cards com SLA vencido ou quase vencido. "
        "Ordene por 'Cycle Time (h)' para encontrar os mais antigos."
    ),
    # ── Página 8 ──
    "p8_header": (
        "📖 Roteiro desta página:\n"
        "① Financeiro por subcategoria → quais linhas são mais lucrativas.\n"
        "② Waterfall → resultado consolidado do período.\n"
        "KPIs no topo resumem a saúde financeira em números."
    ),
    "p8_f1": (
        "Subcategorias com alta receita mas baixo lucro estão consumindo recursos "
        "de forma desproporcional — renegocie escopo ou precificação."
    ),
    "p8_f2": (
        "O waterfall mostra o caminho da receita até o lucro líquido. "
        "Uma barra de custo maior que 60% da receita merece atenção."
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 1 — Visão Geral Kanban
# ══════════════════════════════════════════════════════════════════════════════
def p_kanban():
    total  = int(kpis["total_cards"].iloc[0])        if not kpis.empty else "—"
    risco  = int(kpis["cards_em_risco"].iloc[0])     if not kpis.empty else "—"
    fech   = int(kpis["cards_fechados_hoje"].iloc[0]) if not kpis.empty else "—"
    owners = len(horas_owner) if not horas_owner.empty else "—"

    f1 = go.Figure()
    if not horas_owner.empty:
        f1.add_trace(go.Bar(x=horas_owner["owner"],y=horas_owner["total_horas_investidas"],
            name="Horas Investidas",marker_color=C["a1"],
            hovertemplate="<b>%{x}</b><br>Horas: %{y}<extra></extra>"))
        f1.add_trace(go.Scatter(x=horas_owner["owner"],y=horas_owner["cards_ativos"],
            mode="lines+markers",yaxis="y2",name="Cards Ativos",
            marker=dict(color=C["a2"],size=9),line=dict(color=C["a2"],width=2),
            hovertemplate="<b>%{x}</b><br>Cards Ativos: %{y}<extra></extra>"))
        f1.update_layout(**LB,height=300,
            yaxis2=dict(overlaying="y",side="right",showgrid=False,
                        tickfont=dict(size=11),title=dict(text="Cards",font=dict(size=11))))

    f2 = go.Figure()
    if not live_cards.empty and "status_sla" in live_cards.columns:
        vc = live_cards["status_sla"].value_counts()
        col_map = {"No prazo":C["green"],"Em risco":C["yellow"],"Atrasado":C["red"]}
        f2.add_trace(go.Pie(labels=vc.index,values=vc.values,hole=0.58,
            marker_colors=[col_map.get(l,C["a1"]) for l in vc.index],
            hovertemplate="<b>%{label}</b><br>%{value} cards — %{percent}<extra></extra>"))
        fl(f2,"",300); f2.update_layout(showlegend=True,margin=dict(l=10,r=10,t=10,b=10))

    f3 = go.Figure()
    if not live_cards.empty:
        lc = live_cards.dropna(subset=["total_cycle_time","desvio_horas"])
        for i,col in enumerate(lc["historical_column"].unique()):
            d = lc[lc["historical_column"]==col]
            f3.add_trace(go.Scatter(x=d["total_cycle_time"],y=d["desvio_horas"],
                mode="markers",name=col,marker=dict(color=PAL[i%len(PAL)],size=7,opacity=.75),
                customdata=d[["card_title","owner","status_sla","priority"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>Responsável: %{customdata[1]}<br>"
                    "Cycle Time: %{x}h | Desvio: %{y}h<br>"
                    "SLA: %{customdata[2]} | Prioridade: %{customdata[3]}<extra></extra>"))
        fl(f3,"",300)

    f4 = go.Figure()
    if not live_cards.empty and "priority" in live_cards.columns:
        vc = live_cards["priority"].value_counts().reset_index()
        vc.columns = ["priority","count"]
        pc = {"Alta":C["red"],"Média":C["yellow"],"Baixa":C["green"],"Crítica":C["a5"],
              "High":C["red"],"Medium":C["yellow"],"Low":C["green"],"Critical":C["a5"]}
        f4.add_trace(go.Bar(y=vc["priority"],x=vc["count"],orientation="h",
            marker_color=[pc.get(p,C["a1"]) for p in vc["priority"]],
            hovertemplate="<b>%{y}</b>: %{x} cards<extra></extra>"))
        fl(f4,"",300)

    return html.Div([
        page_header("Visão Geral do Kanban", T["p1_header"]),
        row(kcard("Total de Cards",total,"ativos no kanban",C["a1"],"📋"),
            kcard("Cards em Risco",risco,"requerem atenção",C["red"],"⚠️"),
            kcard("Fechados Hoje",fech,"entregas do dia",C["green"],"✅"),
            kcard("Membros Ativos",owners,"equipe",C["a5"],"👥")),
        row(
            cc_titled("① Carga de Trabalho por Membro","p1f1",T["p1_f1"],f1,{"flex":"2","minWidth":"380px"}),
            cc_titled("② Distribuição de Status SLA","p1f2",T["p1_f2"],f2,{"flex":"1"}),
        ),
        row(
            cc_titled("③ Cycle Time vs Desvio","p1f3",T["p1_f3"],f3,{"flex":"2","minWidth":"380px"}),
            cc_titled("④ Cards por Prioridade","p1f4",T["p1_f4"],f4,{"flex":"1"}),
        ),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 2 — Horas & Utilização
# ══════════════════════════════════════════════════════════════════════════════
def p_horas():
    f1 = go.Figure()
    if not owner_month.empty:
        f1.add_trace(go.Bar(x=owner_month["owner"],y=owner_month["total_horas_estimadas"],
            name="Estimadas",marker_color=C["a1"],
            hovertemplate="<b>%{x}</b><br>Estimadas: %{y}h<extra></extra>"))
        f1.add_trace(go.Bar(x=owner_month["owner"],y=owner_month["total_horas_investidas"],
            name="Investidas",marker_color=C["a2"],
            hovertemplate="<b>%{x}</b><br>Investidas: %{y}h<extra></extra>"))
        fl(f1,"",300); f1.update_layout(barmode="group")

    f2 = go.Figure()
    if not owner_month.empty and "utilizacao_pct" in owner_month.columns:
        f2.add_trace(go.Bar(x=owner_month["owner"],y=owner_month["utilizacao_pct"],
            marker_color=[C["red"] if v>100 else C["green"] for v in owner_month["utilizacao_pct"]],
            hovertemplate="<b>%{x}</b><br>Utilização: %{y:.1f}%<extra></extra>"))
        f2.add_hline(y=100,line_dash="dash",line_color=C["yellow"],annotation_text="Limite 100%")
        fl(f2,"",300)

    f3 = go.Figure()
    if not owner_act_hrs.empty:
        for i,act in enumerate(owner_act_hrs["activity_type"].unique()):
            d = owner_act_hrs[owner_act_hrs["activity_type"]==act]
            f3.add_trace(go.Bar(x=d["owner"],y=d["horas_investidas"],
                name=act,marker_color=PAL[i%len(PAL)],
                hovertemplate=f"<b>%{{x}}</b><br>{act}: %{{y}}h<extra></extra>"))
        fl(f3,"",300); f3.update_layout(barmode="stack")

    f4 = go.Figure()
    if not dev_est.empty:
        d = dev_est.dropna(subset=["total_cycle_time","desvio_horas_pct"])
        for i,sub in enumerate(d["subcategory"].unique() if "subcategory" in d.columns else ["—"]):
            dd = d[d["subcategory"]==sub]
            f4.add_trace(go.Scatter(x=dd["total_cycle_time"],y=dd["desvio_horas_pct"],
                mode="markers",name=sub,marker=dict(color=PAL[i%len(PAL)],size=7,opacity=.7),
                hovertemplate=f"Sub: {sub}<br>Cycle: %{{x}}h | Desvio: %{{y:.1f}}%<extra></extra>"))
        fl(f4,"",300)

    return html.Div([
        page_header("Horas & Utilização", T["p2_header"]),
        row(cc_titled("① Horas Estimadas vs Investidas","p2f1",T["p2_f1"],f1,{"flex":"2"}),
            cc_titled("② Utilização (%) por Membro","p2f2",T["p2_f2"],f2,{"flex":"1"})),
        row(cc_titled("③ Composição de Horas por Atividade","p2f3",T["p2_f3"],f3,{"flex":"2"}),
            cc_titled("④ Desvio Estimado vs Real","p2f4",T["p2_f4"],f4,{"flex":"1"})),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 3 — Bloqueios & SLA
# ══════════════════════════════════════════════════════════════════════════════
def p_bloqueios():
    f1 = go.Figure()
    if not block_reasons.empty:
        br = block_reasons.sort_values("num_bloqueios",ascending=True)
        f1.add_trace(go.Bar(y=br["block_reason"],x=br["num_bloqueios"],orientation="h",
            marker_color=C["a4"],
            customdata=br[["total_tempo_bloqueado","pct_bloqueios"]].values,
            hovertemplate="<b>%{y}</b><br>Bloqueios: %{x}<br>Tempo: %{customdata[0]:.1f}h | %{customdata[1]:.1f}%<extra></extra>"))
        fl(f1,"",300)

    f2 = go.Figure()
    if not live_cards.empty and "is_blocked" in live_cards.columns:
        vc = live_cards["is_blocked"].astype(str).value_counts()
        f2.add_trace(go.Pie(
            labels=["🔒 Bloqueado" if l=="True" else "🟢 Livre" for l in vc.index],
            values=vc.values,hole=0.6,marker_colors=[C["red"],C["green"]],
            hovertemplate="<b>%{label}</b>: %{value} cards (%{percent})<extra></extra>"))
        fl(f2,"",300); f2.update_layout(margin=dict(l=10,r=10,t=10,b=10))

    f3 = go.Figure()
    if not blocked_cards.empty and "owner" in blocked_cards.columns:
        bo = blocked_cards.groupby("owner")["tempo_bloqueado_dias"].sum().reset_index()
        bo = bo.sort_values("tempo_bloqueado_dias",ascending=False)
        f3.add_trace(go.Bar(x=bo["owner"],y=bo["tempo_bloqueado_dias"],
            marker_color=C["a3"],
            hovertemplate="<b>%{x}</b><br>Tempo bloqueado: %{y:.1f} dias<extra></extra>"))
        fl(f3,"",260)

    return html.Div([
        page_header("Bloqueios & Conformidade SLA", T["p3_header"]),
        row(cc_titled("① Principais Causas de Bloqueio","p3f1",T["p3_f1"],f1,{"flex":"2"}),
            cc_titled("② Cards Bloqueados vs Livres","p3f2",T["p3_f2"],f2,{"flex":"1"})),
        row(cc_titled("③ Impacto por Membro (dias bloqueados)","p3f3",T["p3_f3"],f3)),
        table_card("④ Detalhamento de Cards Bloqueados",T["p3_tbl"],
                   build_table_blocked(blocked_cards), status_filter_bar("bloqueios")),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 4 — Atividades
# ══════════════════════════════════════════════════════════════════════════════
def p_atividades():
    f1 = go.Figure()
    if not act_dist.empty:
        f1.add_trace(go.Pie(labels=act_dist["activity_type"],values=act_dist["total_horas"],
            hole=0.52,marker_colors=PAL,
            customdata=act_dist[["num_cards","pct_horas"]].values,
            hovertemplate="<b>%{label}</b><br>Horas: %{value}<br>Cards: %{customdata[0]} | %{customdata[1]:.1f}%<extra></extra>"))
        fl(f1,"",310); f1.update_layout(margin=dict(l=10,r=10,t=10,b=10))

    f2 = go.Figure()
    if not avg_time_sub.empty:
        f2.add_trace(go.Bar(x=avg_time_sub["subcategory"],y=avg_time_sub["tempo_medio_dias"],
            marker_color=C["a2"],
            error_y=dict(type="data",array=avg_time_sub["desvio_padrao_dias"].tolist(),
                         color=C["sub"],thickness=1.5,width=4),
            customdata=avg_time_sub[["tempo_min_dias","tempo_max_dias"]].values,
            hovertemplate="<b>%{x}</b><br>Médio: %{y:.2f} dias<br>Min: %{customdata[0]:.2f} | Max: %{customdata[1]:.2f}<extra></extra>"))
        fl(f2,"",310)

    f3 = go.Figure()
    if not weekly_act.empty:
        for i,act in enumerate(weekly_act["activity_type"].unique()):
            d = weekly_act[weekly_act["activity_type"]==act].sort_values("created_week")
            f3.add_trace(go.Scatter(x=d["created_week"],y=d["horas_investidas"],
                mode="lines",name=act,stackgroup="one",
                line=dict(color=PAL[i%len(PAL)],width=1.5),
                hovertemplate=f"Sem %{{x}}<br>{act}: %{{y}}h<extra></extra>"))
        fl(f3,"",310)

    f4 = go.Figure()
    if not owner_act_stk.empty:
        pivot = owner_act_stk.pivot_table(index="owner",columns="activity_type",
                                           values="horas_investidas",fill_value=0)
        f4.add_trace(go.Heatmap(z=pivot.values,x=pivot.columns.tolist(),y=pivot.index.tolist(),
            colorscale="Blues",
            hovertemplate="<b>%{y}</b> → %{x}: %{z}h<extra></extra>"))
        fl(f4,"",310)

    return html.Div([
        page_header("Distribuição de Atividades", T["p4_header"]),
        row(cc_titled("① Distribuição de Horas","p4f1",T["p4_f1"],f1,{"flex":"1"}),
            cc_titled("② Tempo Médio por Subcategoria","p4f2",T["p4_f2"],f2,{"flex":"2"})),
        row(cc_titled("③ Evolução Semanal por Atividade","p4f3",T["p4_f3"],f3,{"flex":"2"}),
            cc_titled("④ Heatmap Membro × Atividade","p4f4",T["p4_f4"],f4,{"flex":"1"})),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 5 — Performance
# ══════════════════════════════════════════════════════════════════════════════
def p_performance():
    f1 = go.Figure()
    if not perf.empty:
        ps = perf.sort_values("cards_concluidos",ascending=False)
        f1.add_trace(go.Bar(x=ps["owner"],y=ps["cards_concluidos"],marker_color=C["a1"],
            hovertemplate="<b>%{x}</b><br>Concluídos: %{y}<extra></extra>"))
        fl(f1,"",300)

    f2 = go.Figure()
    if not perf.empty:
        f2.add_trace(go.Scatter(x=perf["owner"],y=perf["lead_time_medio"],
            mode="lines+markers",name="Lead Time Médio",
            marker=dict(color=C["a2"],size=10),line=dict(color=C["a2"],width=2),
            hovertemplate="<b>%{x}</b><br>Médio: %{y:.2f} dias<extra></extra>"))
        f2.add_trace(go.Scatter(x=perf["owner"],y=perf["lead_time_mediano"],
            mode="lines+markers",name="Lead Time Mediano",
            marker=dict(color=C["a3"],size=10),line=dict(color=C["a3"],width=2),
            hovertemplate="<b>%{x}</b><br>Mediano: %{y:.2f} dias<extra></extra>"))
        fl(f2,"",300)

    f3 = go.Figure()
    if not reopen.empty:
        rs = reopen.sort_values("taxa_reabertura_pct",ascending=False)
        f3.add_trace(go.Bar(x=rs["owner"],y=rs["taxa_reabertura_pct"],marker_color=C["a4"],
            customdata=rs["total_reaberturas"].tolist(),
            hovertemplate="<b>%{x}</b><br>Taxa: %{y:.1f}%<br>Reaberturas: %{customdata}<extra></extra>"))
        f3.add_hline(y=100,line_dash="dash",line_color=C["yellow"],annotation_text="100%")
        fl(f3,"",300)

    f4 = go.Figure()
    if not throughput.empty:
        f4.add_trace(go.Scatter(x=throughput["closed_at"],y=throughput["cards_entregues"],
            mode="lines+markers+text",
            marker=dict(color=C["a2"],size=8),line=dict(color=C["a2"],width=2.5),
            fill="tozeroy",fillcolor="rgba(63,185,80,0.1)",
            text=throughput["cards_entregues"],textposition="top center",
            hovertemplate="Semana: %{x}<br>Cards: %{y}<extra></extra>"))
        fl(f4,"",300); f4.update_layout(xaxis=dict(tickangle=-45))

    return html.Div([
        page_header("Performance da Equipe", T["p5_header"]),
        row(cc_titled("① Cards Concluídos por Membro","p5f1",T["p5_f1"],f1),
            cc_titled("② Lead Time (dias)","p5f2",T["p5_f2"],f2)),
        row(cc_titled("③ Taxa de Reabertura (%)","p5f3",T["p5_f3"],f3),
            cc_titled("④ Throughput Semanal","p5f4",T["p5_f4"],f4)),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 6 — Demanda
# ══════════════════════════════════════════════════════════════════════════════
def p_demanda():
    f1 = go.Figure()
    if not dem_type.empty:
        f1.add_trace(go.Pie(labels=dem_type["type"],values=dem_type["total_cards"],
            hole=0.52,marker_colors=PAL,customdata=dem_type["pct_total"].values,
            hovertemplate="<b>%{label}</b><br>Cards: %{value} | %{customdata:.1f}%<extra></extra>"))
        fl(f1,"",310); f1.update_layout(margin=dict(l=10,r=10,t=10,b=10))

    f2 = go.Figure()
    if not dem_sub.empty:
        ds = dem_sub.sort_values("total_cards",ascending=False)
        f2.add_trace(go.Bar(x=ds["subcategory"],y=ds["total_cards"],marker_color=C["a5"],
            hovertemplate="<b>%{x}</b><br>Cards: %{y}<extra></extra>"))
        fl(f2,"",310)

    f3 = go.Figure()
    if not weekly_dem.empty:
        f3.add_trace(go.Scatter(x=weekly_dem["created_at"],y=weekly_dem["cards_criados"],
            mode="lines+markers+text",
            marker=dict(color=C["a3"],size=8),line=dict(color=C["a3"],width=2.5),
            fill="tozeroy",fillcolor="rgba(210,153,34,0.1)",
            text=weekly_dem["cards_criados"],textposition="top center",
            hovertemplate="Semana: %{x}<br>Cards criados: %{y}<extra></extra>"))
        fl(f3,"",310); f3.update_layout(xaxis=dict(tickangle=-45))

    return html.Div([
        page_header("Análise de Demanda", T["p6_header"]),
        row(cc_titled("① Mix de Demanda","p6f1",T["p6_f1"],f1,{"flex":"1"}),
            cc_titled("② Volume por Subcategoria","p6f2",T["p6_f2"],f2,{"flex":"2"})),
        row(cc_titled("③ Criação Semanal de Cards","p6f3",T["p6_f3"],f3)),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 7 — Fluxo & Gargalos
# ══════════════════════════════════════════════════════════════════════════════
def p_fluxo():
    f1 = go.Figure()
    if not col_time.empty:
        ct = col_time.sort_values("tempo_medio",ascending=True)
        f1.add_trace(go.Bar(y=ct["historical_column"],x=ct["tempo_medio"],orientation="h",
            marker_color=C["a1"],customdata=ct[["num_cards","tempo_total"]].values,
            hovertemplate="<b>%{y}</b><br>Tempo médio: %{x:.1f}h<br>Cards: %{customdata[0]} | Total: %{customdata[1]:.0f}h<extra></extra>"))
        fl(f1,"",310)

    f2 = go.Figure()
    if not col_time.empty:
        f2.add_trace(go.Funnel(y=col_time["historical_column"],x=col_time["num_cards"],
            textinfo="value+percent initial",marker=dict(color=PAL[:len(col_time)])))
        fl(f2,"",310)

    return html.Div([
        page_header("Fluxo do Kanban & Gargalos", T["p7_header"]),
        row(cc_titled("① Tempo Médio por Coluna","p7f1",T["p7_f1"],f1,{"flex":"2"}),
            cc_titled("② Funil de Cards por Coluna","p7f2",T["p7_f2"],f2,{"flex":"1"})),
        table_card("③ Cards em Espera",T["p7_tbl"],
                   build_table_fluxo(waiting), status_filter_bar("fluxo")),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  PÁGINA 8 — Financeiro
# ══════════════════════════════════════════════════════════════════════════════
def p_financeiro():
    f1 = go.Figure()
    if not fin_sub.empty:
        for col,name,color in [("receita_total","Receita",C["a2"]),
                                ("custo_total","Custo",C["a4"]),("lucro","Lucro",C["a1"])]:
            f1.add_trace(go.Bar(x=fin_sub["subcategory"],y=fin_sub[col],
                name=name,marker_color=color,
                hovertemplate=f"<b>%{{x}}</b><br>{name}: R$ %{{y:,.0f}}<extra></extra>"))
        fl(f1,"",340); f1.update_layout(barmode="group")

    f2 = go.Figure()
    if not fin_sub.empty:
        total_r = fin_sub["receita_total"].sum()
        total_c = fin_sub["custo_total"].sum()
        total_l = fin_sub["lucro"].sum()
        f2.add_trace(go.Waterfall(
            x=["Receita Total","– Custos","= Lucro Líquido"],
            measure=["absolute","relative","total"],y=[total_r,-total_c,total_l],
            connector=dict(line=dict(color=C["border"])),
            increasing=dict(marker_color=C["a2"]),decreasing=dict(marker_color=C["a4"]),
            totals=dict(marker_color=C["a1"]),
            hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>"))
        fl(f2,"",340)

    kr  = f"R$ {fin_sub['receita_total'].sum():,.0f}" if not fin_sub.empty else "—"
    kcu = f"R$ {fin_sub['custo_total'].sum():,.0f}"   if not fin_sub.empty else "—"
    kl  = f"R$ {fin_sub['lucro'].sum():,.0f}"         if not fin_sub.empty else "—"
    mg  = (fin_sub["lucro"].sum()/fin_sub["receita_total"].sum()*100) if not fin_sub.empty else 0
    av  = (live_cards["valor_projeto"].dropna().mean()
           if not live_cards.empty and "valor_projeto" in live_cards.columns else 0)

    return html.Div([
        page_header("Análise Financeira", T["p8_header"]),
        row(kcard("Receita Total",kr,"",C["a2"],"💰"),
            kcard("Custo Total",kcu,"",C["red"],"📉"),
            kcard("Lucro Total",kl,"",C["a1"],"📈"),
            kcard("Margem (%)",f"{mg:.1f}%","",C["a3"],"🎯"),
            kcard("Valor Médio/Card",f"R$ {av:,.0f}","",C["a5"],"🃏")),
        row(cc_titled("① Financeiro por Subcategoria","p8f1",T["p8_f1"],f1,{"flex":"2"}),
            cc_titled("② Resultado Consolidado","p8f2",T["p8_f2"],f2,{"flex":"1"})),
    ])

# ══════════════════════════════════════════════════════════════════════════════
#  APP
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
PAGE_IDS = [pid for _,pid in PAGES]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "FacData BI"

app.index_string = (
    '<!DOCTYPE html>\n'
    '<html>\n'
    '    <head>\n'
    '        {%metas%}\n'
    '        <title>{%title%}</title>\n'
    '        {%favicon%}\n'
    '        {%css%}\n'
    '        <style>\n'
    + TOOLTIP_CSS +
    '        </style>\n'
    '    </head>\n'
    '    <body>\n'
    '        {%app_entry%}\n'
    '        <footer>\n'
    '            {%config%}\n'
    '            {%scripts%}\n'
    '            {%renderer%}\n'
    '        </footer>\n'
    '    </body>\n'
    '</html>\n'
)

def nav_btn(label, pid):
    return html.Button(label, id=f"nav-{pid}", n_clicks=0, style={
        "background":"transparent","border":"none","borderBottom":"3px solid transparent",
        "color":C["sub"],"fontSize":"12px","fontWeight":"500","padding":"10px 16px",
        "cursor":"pointer","transition":"all .15s","whiteSpace":"nowrap",
    })

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Span("◆ ", style={"color":C["a1"],"fontSize":"20px"}),
            html.Span("FacData", style={"fontSize":"20px","fontWeight":"800","color":C["text"]}),
            html.Span(" BI", style={"fontSize":"20px","fontWeight":"300","color":C["a1"]}),
        ], style={"display":"flex","alignItems":"center","gap":"2px"}),
        html.Div("Dashboard — Grupo Fácil",
                 style={"color":C["sub"],"fontSize":"11px"}),
    ], style={"display":"flex","justifyContent":"space-between","alignItems":"center",
              "padding":"12px 24px","background":C["card"],
              "borderBottom":f"1px solid {C['border']}"}),

    html.Div([nav_btn(lbl,pid) for lbl,pid in PAGES], id="nav-bar",
        style={"display":"flex","flexWrap":"wrap","padding":"0 16px",
               "background":C["card"],"borderBottom":f"2px solid {C['border']}","gap":"0px"}),

    html.Div(id="page-content",
        style={"padding":"20px 24px","minHeight":"calc(100vh - 108px)"}),

    dcc.Store(id="current-page", data="kanban"),
], style={"fontFamily":"Inter,system-ui,-apple-system,sans-serif",
          "background":C["bg"],"minHeight":"100vh","color":C["text"],"margin":"0","padding":"0"})

# ── Callbacks ─────────────────────────────────────────────────────────────────
@app.callback(
    Output("current-page","data"),
    [Input(f"nav-{pid}","n_clicks") for pid in PAGE_IDS],
    prevent_initial_call=True,
)
def set_page(*_):
    ctx = callback_context
    if not ctx.triggered: return "kanban"
    return ctx.triggered[0]["prop_id"].split(".")[0].replace("nav-","")

@app.callback(
    [Output(f"nav-{pid}","style") for pid in PAGE_IDS],
    Input("current-page","data"),
)
def highlight_nav(current):
    active = {"background":"transparent","border":"none","borderBottom":f"3px solid {C['a1']}",
               "color":C["text"],"fontSize":"12px","fontWeight":"700",
               "padding":"10px 16px","cursor":"pointer","whiteSpace":"nowrap"}
    inactive = {"background":"transparent","border":"none","borderBottom":"3px solid transparent",
                 "color":C["sub"],"fontSize":"12px","fontWeight":"500","padding":"10px 16px",
                 "cursor":"pointer","transition":"all .15s","whiteSpace":"nowrap"}
    return [active if pid==current else inactive for pid in PAGE_IDS]

@app.callback(Output("page-content","children"), Input("current-page","data"))
def render(page):
    return {"kanban":p_kanban,"horas":p_horas,"bloqueios":p_bloqueios,
            "atividades":p_atividades,"performance":p_performance,
            "demanda":p_demanda,"fluxo":p_fluxo,"financeiro":p_financeiro
            }.get(page, p_kanban)()

@app.callback(Output("tbl-bloqueios","filter_query"),
    [Input(f"f-{x}-bloqueios","n_clicks") for x in ["all","crit","attn","norm"]],
    prevent_initial_call=True)
def filter_bloqueios(*_):
    ctx = callback_context
    if not ctx.triggered: return ""
    return {"f-all-bloqueios":"","f-crit-bloqueios":'{Status} = "🔴 Crítico"',
            "f-attn-bloqueios":'{Status} = "🟡 Atenção"',"f-norm-bloqueios":'{Status} = "🟢 Normal"',
            }.get(ctx.triggered[0]["prop_id"].split(".")[0],"")

@app.callback(Output("tbl-fluxo","filter_query"),
    [Input(f"f-{x}-fluxo","n_clicks") for x in ["all","crit","attn","norm"]],
    prevent_initial_call=True)
def filter_fluxo(*_):
    ctx = callback_context
    if not ctx.triggered: return ""
    return {"f-all-fluxo":"","f-crit-fluxo":'{Status} = "🔴 Crítico"',
            "f-attn-fluxo":'{Status} = "🟡 Atenção"',"f-norm-fluxo":'{Status} = "🟢 Normal"',
            }.get(ctx.triggered[0]["prop_id"].split(".")[0],"")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)