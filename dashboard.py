import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

COLORS = {
    'bg_main': '#FFFFFF',      # Branco
    'bg_card': '#FFFFFF',      # Branco
    'text_main': '#000000',    # Preto
    'text_muted': '#666666',   # Cinza
    'border': '#E0E0E0',       # Cinza Claro
    'accent': '#000000',       # Preto para destaques
    'light_grey': '#F5F5F5'    # Cinza muito claro para fundos sutis
}

# Estilo para os Cards Minimalistas
CARD_STYLE = {
    'backgroundColor': COLORS['bg_card'],
    'border': f'1px solid {COLORS["border"]}',
    'borderRadius': '0px',     # Bordas retas para estilo minimalista
    'boxShadow': 'none',
    'padding': '24px'
}

# ======================================================
# CARREGAMENTO DOS DADOS
# ======================================================

csv_paths = [
    'dataframe final.csv',
    'data/dataframe final.csv',
    '/home/ubuntu/upload/dataframe final.csv'
]

df = None
for path in csv_paths:
    if os.path.exists(path):
        df = pd.read_csv(path)
        break

if df is None:
    import numpy as np
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    df = pd.DataFrame({
        'order_purchase_timestamp': np.random.choice(dates, 2000),
        'price': np.random.uniform(20, 800, 2000),
        'order_id': [f'ord_{i}' for i in range(2000)],
        'customer_state': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'BA', 'PR', 'SC', 'PE', 'CE'], 2000),
        'product_category_name': np.random.choice(['Tech', 'Games', 'Home Office', 'Áudio', 'Wearables'], 2000),
        'atrasou': np.random.choice([True, False], 2000, p=[0.12, 0.88]),
        'dias_atraso': np.random.randint(0, 20, 2000)
    })

# ======================================================
# TRATAMENTO DOS DADOS
# ======================================================

df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
df = df.dropna(subset=['order_purchase_timestamp'])
df['ano'] = df['order_purchase_timestamp'].dt.year
df['mes'] = df['order_purchase_timestamp'].dt.month
df['mes_nome'] = df['order_purchase_timestamp'].dt.strftime('%b')

# Garantir colunas
for col, val in [('product_category_name', 'Geral'), ('customer_state', 'N/A'), 
                ('price', 0), ('atrasou', False), ('dias_atraso', 0)]:
    if col not in df.columns: df[col] = val

anos_disponiveis = sorted(df['ano'].dropna().unique())
estados = sorted(df['customer_state'].dropna().unique())
categorias = sorted(df['product_category_name'].dropna().unique())

# ======================================================
# APP
# ======================================================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
app.title = 'Relatório de Vendas | Minimalista'

# ======================================================
# COMPONENTES
# ======================================================

def minimal_kpi(title, value_id):
    return html.Div([
        html.P(title, className='mb-1 small text-uppercase fw-bold', style={'color': COLORS['text_muted'], 'letterSpacing': '1px'}),
        html.H2(id=value_id, className='mb-0 fw-light', style={'color': COLORS['text_main']})
    ], style=CARD_STYLE)

# ======================================================
# LAYOUT
# ======================================================

app.layout = html.Div([
    dbc.Container([
        # Header Section
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1('RELATÓRIO DE VENDAS', className='fw-black mb-0', style={'letterSpacing': '2px', 'fontSize': '2.5rem'}),
                    html.P('VISÃO GERAL DE PERFORMANCE E-COMMERCE', className='small', style={'color': COLORS['text_muted'], 'letterSpacing': '1px'})
                ], className='pt-5 pb-4')
            ], md=8),
            dbc.Col([
                html.Div([
                    html.Label('ANO', className='small fw-bold mb-1', style={'color': COLORS['text_muted']}),
                    dcc.Dropdown(
                        id='ano-filter',
                        options=[{'label': str(a), 'value': a} for a in anos_disponiveis],
                        value=max(anos_disponiveis) if anos_disponiveis else None,
                        clearable=False,
                        style={'borderRadius': '0px', 'border': f'1px solid {COLORS["border"]}'}
                    )
                ], className='pt-5 pb-4 text-end')
            ], md=4)
        ], className='mb-4'),

        # KPI Row
        dbc.Row([
            dbc.Col(minimal_kpi('Receita Total', 'kpi-receita'), lg=3, md=6),
            dbc.Col(minimal_kpi('Pedidos', 'kpi-pedidos'), lg=3, md=6),
            dbc.Col(minimal_kpi('Ticket Médio', 'kpi-ticket'), lg=3, md=6),
            dbc.Col(minimal_kpi('Taxa de Atraso', 'kpi-atraso'), lg=3, md=6),
        ], className='g-4 mb-5'),

        # Secondary Filters
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='mes-filter', options=[{'label': m, 'value': i} for i, m in enumerate(['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'], 1)], 
                             value=list(range(1, 13)), multi=True, placeholder='MESES', className='mb-3')
            ], md=4),
            dbc.Col([
                dcc.Dropdown(id='estado-filter', options=[{'label': e, 'value': e} for e in estados], multi=True, placeholder='ESTADOS', className='mb-3')
            ], md=4),
            dbc.Col([
                dcc.Dropdown(id='categoria-filter', options=[{'label': c, 'value': c} for c in categorias], multi=True, placeholder='CATEGORIAS', className='mb-3')
            ], md=4),
        ], className='mb-5'),

        # Charts Section
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6('TENDÊNCIA DE RECEITA', className='mb-4 fw-bold', style={'color': COLORS['text_main'], 'letterSpacing': '1px'}),
                    dcc.Graph(id='grafico-receita', config={'displayModeBar': False})
                ], style=CARD_STYLE)
            ], lg=8, md=12),
            dbc.Col([
                html.Div([
                    html.H6('TOP REGIÕES', className='mb-4 fw-bold', style={'color': COLORS['text_main'], 'letterSpacing': '1px'}),
                    dcc.Graph(id='grafico-estados', config={'displayModeBar': False})
                ], style=CARD_STYLE)
            ], lg=4, md=12),
        ], className='g-4 mb-4'),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6('MIX DE PRODUTOS', className='mb-4 fw-bold', style={'color': COLORS['text_main'], 'letterSpacing': '1px'}),
                    dcc.Graph(id='grafico-categorias', config={'displayModeBar': False})
                ], style=CARD_STYLE)
            ], lg=6, md=12),
            dbc.Col([
                html.Div([
                    html.H6('ANÁLISE DE ENTREGAS', className='mb-4 fw-bold', style={'color': COLORS['text_main'], 'letterSpacing': '1px'}),
                    dcc.Graph(id='grafico-atrasos', config={'displayModeBar': False})
                ], style=CARD_STYLE)
            ], lg=6, md=12),
        ], className='g-4 mb-5'),

        # Table Section
        html.Div([
            html.H6('DETALHAMENTO OPERACIONAL', className='mb-4 fw-bold', style={'color': COLORS['text_main'], 'letterSpacing': '1px'}),
            dash_table.DataTable(
                id='tabela-resumo',
                style_table={'overflowX': 'auto', 'border': f'1px solid {COLORS["border"]}'},
                style_header={
                    'backgroundColor': COLORS['light_grey'],
                    'color': COLORS['text_main'],
                    'fontWeight': 'bold',
                    'border': f'1px solid {COLORS["border"]}',
                    'textTransform': 'uppercase',
                    'fontSize': '12px'
                },
                style_cell={
                    'backgroundColor': COLORS['bg_main'],
                    'color': COLORS['text_main'],
                    'padding': '15px',
                    'border': f'1px solid {COLORS["border"]}',
                    'fontSize': '14px',
                    'fontFamily': 'inherit'
                },
                style_data_conditional=[
                    {'if': {'column_id': 'Receita'}, 'fontWeight': 'bold'},
                ],
                page_size=8
            )
        ], className='mb-5 pb-5')

    ], fluid=True)
], style={'backgroundColor': COLORS['bg_main'], 'minHeight': '100vh', 'fontFamily': 'Helvetica, Arial, sans-serif', 'color': COLORS['text_main']})

# ======================================================
# CALLBACKS
# ======================================================

@app.callback(
    [
        Output('kpi-receita', 'children'),
        Output('kpi-pedidos', 'children'),
        Output('kpi-ticket', 'children'),
        Output('kpi-atraso', 'children'),
        Output('grafico-receita', 'figure'),
        Output('grafico-estados', 'figure'),
        Output('grafico-categorias', 'figure'),
        Output('grafico-atrasos', 'figure'),
        Output('tabela-resumo', 'data'),
        Output('tabela-resumo', 'columns')
    ],
    [
        Input('ano-filter', 'value'),
        Input('mes-filter', 'value'),
        Input('estado-filter', 'value'),
        Input('categoria-filter', 'value')
    ]
)
def update_dashboard(ano, meses, estados_sel, categorias_sel):
    filtered = df[df['ano'] == ano]
    if meses: filtered = filtered[filtered['mes'].isin(meses)]
    if estados_sel: filtered = filtered[filtered['customer_state'].isin(estados_sel)]
    if categorias_sel: filtered = filtered[filtered['product_category_name'].isin(categorias_sel)]

    receita = filtered['price'].sum()
    pedidos = filtered['order_id'].nunique()
    ticket = filtered['price'].mean() if not filtered.empty else 0
    atraso = (filtered['atrasou'].mean() * 100) if not filtered.empty else 0

    # Gráfico de Receita (Minimalista - Linha Preta)
    meses_map = {'Jan':'Jan','Feb':'Fev','Mar':'Mar','Apr':'Abr','May':'Mai','Jun':'Jun','Jul':'Jul','Aug':'Ago','Sep':'Set','Oct':'Out','Nov':'Nov','Dec':'Dez'}
    receita_tempo = filtered.groupby('mes_nome')['price'].sum().reindex(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']).reset_index()
    receita_tempo['mes_nome'] = receita_tempo['mes_nome'].map(meses_map)
    
    fig_receita = go.Figure()
    fig_receita.add_trace(go.Scatter(
        x=receita_tempo['mes_nome'], y=receita_tempo['price'],
        mode='lines', line=dict(color=COLORS['text_main'], width=2),
        fill='tozeroy', fillcolor='rgba(0, 0, 0, 0.02)'
    ))
    fig_receita.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_muted']), height=300, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=COLORS['light_grey'], showticklabels=False)
    )

    # Gráfico de Estados (Minimalista - Barras Cinza)
    pedidos_estado = filtered.groupby('customer_state')['order_id'].nunique().sort_values(ascending=True).tail(8).reset_index()
    fig_estados = px.bar(pedidos_estado, x='order_id', y='customer_state', orientation='h')
    fig_estados.update_traces(marker_color=COLORS['text_main'])
    fig_estados.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_muted']), height=300, margin=dict(l=0, r=0, t=0, b=0),
        xaxis_visible=False, yaxis=dict(showgrid=False)
    )

    # Gráfico de Categorias (Minimalista - Donut Cinza)
    cat_data = filtered.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(5).reset_index()
    fig_categorias = px.pie(cat_data, values='price', names='product_category_name', hole=0.8,
                           color_discrete_sequence=[COLORS['text_main'], COLORS['text_muted'], '#999', '#CCC', '#EEE'])
    fig_categorias.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_muted']), height=280, margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )

    # Gráfico de Atrasos (Minimalista - Histograma)
    fig_atrasos = px.histogram(filtered[filtered['atrasou']], x='dias_atraso')
    fig_atrasos.update_traces(marker_color=COLORS['text_muted'])
    fig_atrasos.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_muted']), height=280, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(title='Dias de Atraso', showgrid=False), yaxis=dict(showgrid=True, gridcolor=COLORS['light_grey'])
    )

    # Tabela
    resumo = filtered.groupby('customer_state').agg(
        Receita=('price', 'sum'),
        Pedidos=('order_id', 'nunique'),
        Atraso_Pct=('atrasou', 'mean')
    ).reset_index()
    resumo['Atraso_Pct'] = (resumo['Atraso_Pct'] * 100).round(1)
    resumo = resumo.sort_values('Receita', ascending=False)
    
    cols = [
        {'name': 'ESTADO', 'id': 'customer_state'},
        {'name': 'RECEITA (R$)', 'id': 'Receita', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
        {'name': 'PEDIDOS', 'id': 'Pedidos'},
        {'name': '% ATRASO', 'id': 'Atraso_Pct'}
    ]

    return (
        f'R$ {receita:,.2f}',
        f'{pedidos:,}',
        f'R$ {ticket:,.2f}',
        f'{atraso:.1f}%',
        fig_receita,
        fig_estados,
        fig_categorias,
        fig_atrasos,
        resumo.to_dict('records'),
        cols
    )

if __name__ == '__main__':
    app.run(debug=True, port=8050)
