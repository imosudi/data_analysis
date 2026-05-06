

"""
Austrian National Tourist Office - Winter Tourism Dashboard
Group B: Winter Season Promotion
Data: Statistics Austria OGD Tourism Dataset (2015-2024)
Stack: Dash · Plotly · Pandas
"""

import re
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

# ─────────────────────────────────────────────
# 1. DATA LOADING & PREPARATION
# ─────────────────────────────────────────────

def load_and_merge():
    """Load all CSV files, join lookups, classify seasons."""
    main         = pd.read_csv('dataset/4-OGD_touextsai_Tour_HKL_1.csv', sep=';')
    countries_df = pd.read_csv('dataset/2-OGD_touextsai_Tour_HKL_1_C-C93-2.csv', sep=';')
    regions_df   = pd.read_csv('dataset/3-OGD_touextsai_Tour_HKL_1_C-W96-0.csv', sep=';')

    # Decode year / month from YYYYMM season code
    main['year']  = main['C-SDB_TIT-0'].astype(str).str[:4].astype(int)
    main['month'] = main['C-SDB_TIT-0'].astype(str).str[4:].astype(int)

    # Season classification
    main['season'] = main['month'].apply(
        lambda m: 'Winter' if m in [11, 12, 1, 2, 3]
                  else ('Summer' if m in [6, 7, 8] else 'Shoulder')
    )

    # Build lookup maps (strip angle-bracket codes from names)
    def clean(name):
        return re.sub(r'\s*<[^>]+>', '', str(name)).strip()

    region_map  = {row['code']: clean(row['en_name']) for _, row in regions_df.iterrows()}
    country_map = {row['code']: clean(row['en_name']) for _, row in countries_df.iterrows()}

    # Further clean country labels - remove "(beg.XX/XX)" suffixes
    def short(name):
        return re.sub(r'\s*\((?:beg\.|till).*?\)', '', name).strip()

    country_map = {k: short(v) for k, v in country_map.items()}

    main['region']  = main['C-W96-0'].map(region_map)
    main['country'] = main['C-C93-2'].map(country_map)

    # Filter to 2015-2024 study window
    df = main[(main['year'] >= 2015) & (main['year'] <= 2024)].copy()
    return df


df = load_and_merge()

# ── Aggregate datasets used by charts ──

# Season KPIs
kpi = df.groupby('season')[['F-ANK', 'F-UEB']].sum()
w_nights   = kpi.loc['Winter', 'F-UEB']
s_nights   = kpi.loc['Summer', 'F-UEB']
w_arr      = kpi.loc['Winter', 'F-ANK']
s_arr      = kpi.loc['Summer', 'F-ANK']
w_los      = w_nights / w_arr   # avg length of stay
s_los      = s_nights / s_arr

# Monthly totals
monthly = (df.groupby('month')['F-UEB'].sum()
             .reset_index()
             .rename(columns={'month': 'Month', 'F-UEB': 'Nights'}))
MONTH_NAMES = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
               7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
monthly['MonthName'] = monthly['Month'].map(MONTH_NAMES)
monthly['Season'] = monthly['Month'].apply(
    lambda m: 'Winter' if m in [11,12,1,2,3] else ('Summer' if m in [6,7,8] else 'Shoulder'))

# Regional comparison
reg = (df[df['season'].isin(['Winter', 'Summer'])]
       .groupby(['region', 'season'])['F-UEB'].sum()
       .reset_index()
       .rename(columns={'region': 'Region', 'season': 'Season', 'F-UEB': 'Nights'}))

# Sort regions by total winter nights
winter_order = (reg[reg['Season'] == 'Winter']
                .sort_values('Nights')['Region'].tolist())

# Annual trend
trend = (df[df['season'].isin(['Winter', 'Summer'])]
         .groupby(['year', 'season'])['F-UEB'].sum()
         .reset_index()
         .rename(columns={'year': 'Year', 'season': 'Season', 'F-UEB': 'Nights'}))

# Top foreign markets (winter) - keep only real foreign / German state entries
# Exclude ambiguous domestic lumped codes (1-2, 53-55, 63-64, 70-77)
domestic_codes = {1, 2, 53, 54, 55, 63, 64, 70, 71, 72, 73, 74, 75, 76, 77}
foreign_winter = (df[(df['season'] == 'Winter') &
                     (~df['C-C93-2'].isin(domestic_codes))]
                  .groupby('country')['F-UEB'].sum()
                  .reset_index()
                  .rename(columns={'country': 'Country', 'F-UEB': 'Nights'})
                  .sort_values('Nights', ascending=False)
                  .head(12))

# ─────────────────────────────────────────────
# 2. DESIGN TOKENS
# ─────────────────────────────────────────────

C_INK      = '#f5f7fb'
C_CARD     = '#ffffff'
C_BORDER   = 'rgba(15,23,42,0.08)'
C_WINTER   = '#2e6da4'
C_WIN_LT   = '#5ba3d9'
C_SUMMER   = '#d97c3a'
C_SUM_LT   = '#e8a06a'
C_GOLD     = '#c9973a'
C_GOLD_LT  = '#e8c070'
C_TEXT     = '#0f172a'
C_MUTED    = '#475569'
C_GRID     = 'rgba(15,23,42,0.06)'
C_SHOULDER = 'rgba(15,23,42,0.12)'

FONT_MAIN  = 'DM Sans, Helvetica Neue, Arial, sans-serif'
FONT_SERIF = 'Cormorant Garamond, Georgia, serif'

PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family=FONT_MAIN, color=C_TEXT, size=12),
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(
        bgcolor='rgba(255,255,255,0.0)',
        font=dict(size=11, color=C_TEXT),
        orientation='h', x=0, y=1.08,
    ),
    hoverlabel=dict(
        bgcolor='#f8fafc',
        bordercolor=C_WIN_LT,
        font=dict(family=FONT_MAIN, size=12, color=C_TEXT),
    ),
)

def axis_style(show_grid=True, tickformat=None, title=None):
    return dict(
        title=title,
        showgrid=show_grid,
        gridcolor=C_GRID,
        gridwidth=1,
        zeroline=False,
        linecolor='rgba(15,23,42,0.12)',
        tickfont=dict(size=11, color=C_MUTED),
        tickformat=tickformat,
    )


# ─────────────────────────────────────────────
# 3. FIGURE BUILDERS
# ─────────────────────────────────────────────

def fig_monthly():
    """Bar chart: monthly overnight stays coloured by season."""
    colour_map = {'Winter': C_WINTER, 'Summer': C_SUMMER, 'Shoulder': C_SHOULDER}
    colours = monthly['Season'].map(colour_map)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly['MonthName'],
        y=monthly['Nights'],
        marker_color=colours,
        marker_line_width=0,
        hovertemplate='<b>%{x}</b><br>%{y:,.0f} nights<extra></extra>',
        name='',
    ))

    # Annotation: peak months
    for month, label, col in [(2, 'Feb Peak', C_WIN_LT), (8, 'Aug Peak', C_SUM_LT)]:
        row = monthly[monthly['Month'] == month].iloc[0]
        fig.add_annotation(
            x=row['MonthName'], y=row['Nights'],
            text=f"<b>{row['Nights']/1e6:.0f}M</b>",
            showarrow=False, yshift=14,
            font=dict(size=11, color=col, family=FONT_MAIN),
        )

    fig.update_layout(
        **PLOTLY_BASE,
        xaxis=axis_style(show_grid=False),
        yaxis=dict(**axis_style(tickformat='.2s', title='Overnight Stays'),
                   tickprefix='', showticklabels=True),
        bargap=0.18,
    )
    return fig


def fig_regional():
    """Grouped horizontal bar: regions by season."""
    fig = go.Figure()
    for season, colour, sym in [
        ('Winter', C_WINTER, 'circle'),
        ('Summer', C_SUMMER, 'circle'),
    ]:
        s = reg[reg['Season'] == season].set_index('Region').reindex(winter_order)
        fig.add_trace(go.Bar(
            y=s.index,
            x=s['Nights'],
            name=season,
            orientation='h',
            marker=dict(color=colour, line_width=0),
            hovertemplate=f'<b>%{{y}}</b> ({season})<br>%{{x:,.0f}} nights<extra></extra>',
        ))

    layout_kw = {**PLOTLY_BASE}
    layout_kw['margin'] = dict(l=100, r=10, t=30, b=10)
    fig.update_layout(
        **layout_kw,
        barmode='group',
        bargroupgap=0.12,
        xaxis=axis_style(tickformat='.2s', title='Overnight Stays'),
        yaxis=axis_style(show_grid=False),
    )
    return fig


def fig_trend():
    """Dual-line area chart: annual winter vs summer trend."""
    fig = go.Figure()
    styles = {
        'Winter': dict(color=C_WIN_LT,  fill_color='rgba(91,163,217,0.10)'),
        'Summer': dict(color=C_SUMMER,  fill_color='rgba(217,124,58,0.07)'),
    }
    for season, st in styles.items():
        s = trend[trend['Season'] == season].sort_values('Year')
        fig.add_trace(go.Scatter(
            x=s['Year'], y=s['Nights'],
            name=season,
            mode='lines+markers',
            line=dict(color=st['color'], width=2.5),
            marker=dict(size=6, color=st['color'],
                        line=dict(width=1.5, color=C_INK)),
            fill='tozeroy',
            fillcolor=st['fill_color'],
            hovertemplate=f'<b>%{{x}}</b> ({season})<br>%{{y:,.0f}} nights<extra></extra>',
        ))

    # COVID band annotation
    fig.add_vrect(x0=2019.5, x1=2021.5,
        fillcolor='rgba(255,80,80,0.06)',
        line_width=0,
        annotation_text='COVID', annotation_position='top left',
        annotation_font=dict(size=10, color='rgba(255,100,100,0.6)'),
    )

    fig.update_layout(
        **PLOTLY_BASE,
        xaxis=axis_style(show_grid=False, title='Year'),
        yaxis=axis_style(tickformat='.2s', title='Overnight Stays'),
        hovermode='x unified',
    )
    return fig


def fig_countries():
    """Ranked horizontal bar: top foreign winter markets."""
    # Colour Netherlands gold, German states blue, rest lighter
    def bar_colour(country):
        if 'Netherlands' in country:
            return C_GOLD
        german_keywords = ['Bavaria','Württemberg','Westfalen','Germany','German']
        if any(k in country for k in german_keywords):
            return C_WINTER
        return C_WIN_LT

    colours = foreign_winter['Country'].apply(bar_colour)
    df_plot  = foreign_winter.sort_values('Nights')

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_plot['Country'],
        x=df_plot['Nights'],
        orientation='h',
        marker=dict(color=df_plot['Country'].apply(bar_colour), line_width=0),
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} nights<extra></extra>',
        name='',
    ))

    layout_kw2 = {**PLOTLY_BASE}
    layout_kw2['margin'] = dict(l=170, r=20, t=10, b=10)
    fig.update_layout(
        **layout_kw2,
        xaxis=axis_style(tickformat='.2s'),
        yaxis=axis_style(show_grid=False),
    )
    return fig


# ─────────────────────────────────────────────
# 4. REUSABLE UI COMPONENTS
# ─────────────────────────────────────────────

def card(*children, style=None):
    base = dict(
        background=C_CARD,
        border=f'1px solid {C_BORDER}',
        borderRadius='14px',
        padding='24px',
        display='flex',
        flexDirection='column',
    )
    if style:
        base.update(style)
    return html.Div(children, style=base)


def kpi_card(label, value, unit, delta=None, delta_up=True, note=None):
    delta_el = None
    if delta:
        delta_el = html.Span(
            ('▲ ' if delta_up else '▼ ') + delta,
            style=dict(
                display='inline-block',
                marginTop='10px',
                padding='3px 12px',
                borderRadius='20px',
                fontSize='12px',
                fontWeight='600',
                background='rgba(109,217,138,0.10)' if delta_up else 'rgba(217,100,100,0.10)',
                color='#6dd98a' if delta_up else '#e07070',
            )
        )
    return card(
        html.Div(label, style=dict(fontSize='10px', letterSpacing='2.5px',
                                   textTransform='uppercase', color=C_MUTED,
                                   marginBottom='10px')),
        html.Div(value, style=dict(
            fontFamily=FONT_SERIF, fontSize='48px', fontWeight='700',
            lineHeight='1', color=C_TEXT, marginBottom='2px')),
        html.Div(unit, style=dict(fontSize='12px', color=C_WIN_LT,
                                  letterSpacing='1px', marginBottom='6px')),
        delta_el,
        html.Div(note, style=dict(fontSize='12px', color='rgba(15,23,42,0.7)',
                                   lineHeight='1.6', marginTop='10px')) if note else None,
        style=dict(textAlign='center', padding='28px 20px'),
    )


def chart_card(label, title, figure, legend_items=None, note=None, style=None):
    legend_el = None
    if legend_items:
        dots = []
        for colour, text in legend_items:
            dots.append(html.Div([
                html.Div(style=dict(width='10px', height='10px', borderRadius='2px',
                                    background=colour, flexShrink='0')),
                html.Span(text, style=dict(fontSize='11px', color='rgba(71,85,105,0.75)')),
            ], style=dict(display='flex', alignItems='center', gap='6px')))
        legend_el = html.Div(dots, style=dict(display='flex', gap='16px',
                                               flexWrap='wrap', marginBottom='12px'))
    note_el = html.Div(note, style=dict(fontSize='12px', color='rgba(71,85,105,0.75)',
                                         lineHeight='1.6', marginTop='10px')) if note else None
    return card(
        html.Div(label, style=dict(fontSize='10px', letterSpacing='2.5px',
                                    textTransform='uppercase', color=C_MUTED,
                                    marginBottom='8px')),
        html.Div(title, style=dict(fontFamily=FONT_SERIF, fontSize='17px',
                                    fontWeight='600', color=C_TEXT, marginBottom='12px')),
        legend_el,
        dcc.Graph(figure=figure, config={'displayModeBar': False, 'displaylogo': False},
                  style=dict(flex='1', minHeight='0')),
        note_el,
        style={**dict(flex='1'), **(style or {})},
    )


def text_card(label, quote, cite, bullets):
    return card(
        html.Div(label, style=dict(fontSize='10px', letterSpacing='2.5px',
                                    textTransform='uppercase', color=C_MUTED,
                                    marginBottom='16px')),
        # Pull-quote
        html.Div([
            html.Div(style=dict(width='3px', background=C_GOLD,
                                borderRadius='2px', flexShrink='0')),
            html.Div([
                html.P(f'"{quote}"', style=dict(
                    fontFamily=FONT_SERIF, fontSize='19px', fontWeight='300',
                    fontStyle='italic', color='rgba(15,23,42,0.88)',
                    lineHeight='1.55', margin='0 0 8px 0')),
                html.Cite(f'- {cite}', style=dict(fontSize='11px', color=C_MUTED,
                                                    letterSpacing='1px',
                                                    textTransform='uppercase')),
            ]),
        ], style=dict(display='flex', gap='16px', marginBottom='24px')),
        # Bullets
        html.Ul([
            html.Li(html.Span(b, style=dict(fontSize='13px', color='rgba(15,23,42,0.75)',
                                             lineHeight='1.65')),
                    style=dict(
                        display='flex', gap='10px', alignItems='flex-start',
                        paddingBottom='8px', marginBottom='8px',
                        borderBottom='1px solid rgba(15,23,42,0.08)',
                        listStyle='none', padding='6px 0',
                    ))
            for b in bullets
        ], style=dict(paddingLeft='0', margin='0')),
    )


# ─────────────────────────────────────────────
# 5. LAYOUT
# ─────────────────────────────────────────────

def layout():
    # ── figures ──
    f_monthly   = fig_monthly()
    f_regional  = fig_regional()
    f_trend     = fig_trend()
    f_countries = fig_countries()

    return html.Div([

        # Google Fonts injection
        html.Link(rel='stylesheet',
                  href='https://fonts.googleapis.com/css2?'
                       'family=Cormorant+Garamond:ital,wght@0,300;0,600;0,700;1,300'
                       '&family=DM+Sans:wght@300;400;500;600&display=swap'),
        # ── HERO ──────────────────────────────
        html.Div([
            html.Div([

                # LEFT: Text Content
                html.Div([
                    html.Div('AUSTRIAN NATIONAL TOURIST OFFICE · MARKET INTELLIGENCE 2015-2024',
                            style=dict(fontSize='11px', letterSpacing='3px',
                                        color=C_WIN_LT, marginBottom='12px', fontWeight='500')),

                    html.H1([
                        "The Winning Season in Austria is ",
                        html.Em("Winter", style=dict(color=C_GOLD_LT, fontStyle='italic')),
                    ], style=dict(
                        fontFamily=FONT_SERIF, fontSize='clamp(36px,4.5vw,60px)',
                        fontWeight='300', color=C_TEXT, margin='0 0 10px 0', lineHeight='1.1',
                    )),

                    html.P(
                        'A data-driven case for Group B: overnight stay analysis across nine federal '
                        'provinces reveals winter consistently outperforms summer - by 15% in total '
                        'volume with stronger year-on-year growth heading into 2024.',
                        style=dict(fontSize='14px', color='rgba(15,23,42,0.75)',
                                fontWeight='300', maxWidth='560px', lineHeight='1.75',
                                marginBottom='22px'),
                    ),

                    html.Div([
                        html.Span('Source: Statistics Austria - OGD Tourism HKL Dataset',
                                style=dict(padding='5px 14px', borderRadius='20px',
                                            fontSize='11px', fontWeight='500',
                                            background='rgba(91,163,217,0.10)',
                                            border='1px solid rgba(91,163,217,0.28)',
                                            color=C_WIN_LT)),
                        html.Span('Period: 2015 - 2024',
                                style=dict(padding='5px 14px', borderRadius='20px',
                                            fontSize='11px', fontWeight='500',
                                            background='rgba(201,151,58,0.10)',
                                            border='1px solid rgba(201,151,58,0.28)',
                                            color=C_GOLD_LT)),
                        html.Span('9 Provinces · 80+ Origin Markets',
                                style=dict(padding='5px 14px', borderRadius='20px',
                                            fontSize='11px', fontWeight='500',
                                            background='rgba(91,163,217,0.08)',
                                            border='1px solid rgba(91,163,217,0.18)',
                                            color=C_WIN_LT)),
                    ], style=dict(display='flex', gap='10px', flexWrap='wrap')),

                ], style=dict(flex='1', zIndex='1')),

                # RIGHT: Logo Graphic
                html.Div([
                    html.Div([
                        html.Img(src='/assets/fhtw-logo.png',
                                 style=dict(width='100%', maxWidth='420px', opacity='0.95'))
                    ], style=dict(
                        width='100%',
                        maxWidth='420px',
                    ))
                ], style=dict(
                    flex='1',
                    display='flex',
                    justifyContent='center',
                    alignItems='center'
                )),

            ], style=dict(
                display='flex',
                gap='40px',
                alignItems='center',
                justifyContent='space-between',
                flexWrap='wrap'
            )),

        ], style=dict(
            background='linear-gradient(145deg,#f8fafc 0%,#e2e8f0 45%,#dbeafe 100%)',
            padding='48px 48px 40px',
            borderBottom=f'1px solid {C_BORDER}',
        )),

        # ── MAIN GRID ─────────────────────────
        html.Div([

            # Row 1: KPI cards
            html.Div([
                kpi_card('Winter Overnight Stays', f'{w_nights/1e6:.0f}M',
                         'Total Nights · 2015-2024',
                         delta='+15% vs. Summer',
                         note='Winter (Nov-Mar) drives the largest share of annual tourism volume.'),
                kpi_card('Record Winter', '66.1M',
                         'Overnight Nights in 2024',
                         delta='All-time high',
                         note='2024 surpassed the pre-pandemic peak of 65.8M set in 2018.'),
                kpi_card('Star Region', 'Tyrol',
                         '213M Winter Nights',
                         delta='39% of all winter stays',
                         delta_up=True,
                         note='Tyrol alone accounts for nearly 4 in 10 winter overnight stays.'),
                kpi_card('Avg. Length of Stay', f'{w_los:.2f}',
                         'Nights per Arrival - Winter',
                         delta=f'{w_los - s_los:+.2f} vs. Summer',
                         note=f'Summer LOS: {s_los:.2f} nights. Winter guests stay longer.'),
            ], style=dict(
                display='grid',
                gridTemplateColumns='repeat(4, 1fr)',
                gap='18px', marginBottom='18px',
            )),

            # Row 2: Monthly chart + Regional chart
            html.Div([
                chart_card(
                    label='Seasonal Rhythm',
                    title='Monthly Overnight Stays - Austria, 2015-2024 Total',
                    figure=f_monthly,
                    legend_items=[
                        (C_WINTER, 'Winter Season (Nov-Mar)'),
                        (C_SUMMER, 'Summer Season (Jun-Aug)'),
                        (C_SHOULDER, 'Shoulder Season'),
                    ],
                    note=(
                        'Feb (158M) and Aug (200M) are absolute peaks. '
                        'Winter\'s 5-month season accumulates far more nights than Summer\'s 3-month window.'
                    ),
                    style=dict(flex='7'),
                ),
                chart_card(
                    label='Regional Powerhouses',
                    title='Overnight Stays by Province',
                    figure=f_regional,
                    legend_items=[
                        (C_WINTER, 'Winter'),
                        (C_SUMMER, 'Summer'),
                    ],
                    note='Tyrol + Salzburg hold 61% of all winter overnight stays.',
                    style=dict(flex='5'),
                ),
            ], style=dict(display='flex', gap='18px', marginBottom='18px',
                          alignItems='stretch')),

            # Row 3: Text callout + Trend + Countries
            html.Div([
                text_card(
                    label='Key Insights',
                    quote=(
                        'Winter is not a season in Austria - '
                        'it is the season.'
                    ),
                    cite='ANTO Market Intelligence Briefing',
                    bullets=[
                        'Winter outperformed summer in 7 of the last 9 pre/post-COVID years',
                        'Tyrol + Salzburg account for 61% of all winter overnight stays',
                        'Dutch guests show the highest nights-per-arrival ratio of any foreign market',
                        'Vorarlberg: 40M winter nights from Austria\'s smallest alpine province - +55% vs. summer',
                        'Winter 2024 hit an all-time record; summer is still catching up to 2019 levels',
                    ],
                ),
                chart_card(
                    label='Year-over-Year Performance',
                    title='Winter vs. Summer: Annual Overnight Stays 2015-2024',
                    figure=f_trend,
                    legend_items=[
                        (C_WIN_LT, 'Winter Season'),
                        (C_SUMMER, 'Summer Season'),
                    ],
                    note=(
                        'Winter staged a 6× faster post-COVID rebound than summer. '
                        '2021 winter collapse due to nationwide ski resort closures.'
                    ),
                    style=dict(flex='6'),
                ),
                chart_card(
                    label='Top Origin Markets - Winter',
                    title='Foreign Overnight Stays (Millions)',
                    figure=f_countries,
                    note='🟡 Netherlands #1 foreign market. 🔵 German Bundesländer dominate in aggregate.',
                    style=dict(flex='4'),
                ),
            ], style=dict(display='flex', gap='18px', alignItems='stretch')),

        ], style=dict(padding='28px 44px 40px', background=C_INK)),

        # ── FOOTER ────────────────────────────
        html.Div(
            'FT Technikum Wien · Data Analysis · Winter Tourism Dashboard · 2015-2024',
            style=dict(
                padding='0 44px 32px',
                background=C_INK,
                fontSize='11px',
                color='rgba(15,23,42,0.6)',
                letterSpacing='0.3px',
                textAlign='center',
            ),
        ),

    ], style=dict(
        background=C_INK,
        minHeight='100vh',
        fontFamily=FONT_MAIN,
        color=C_TEXT,
    ))


# ─────────────────────────────────────────────
# 6. APP INIT
# ─────────────────────────────────────────────

app = Dash(
    __name__,
    title='Austria Winter Tourism Dashboard',
    suppress_callback_exceptions=True,
)
app.layout = layout()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
