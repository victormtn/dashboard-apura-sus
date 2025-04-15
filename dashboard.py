import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
from fpdf import FPDF
import io
import base64
from flask import send_file, Flask
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Inicializa o servidor Flask
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Configurar o acesso ao Google Sheets
def load_data_from_sheets(sheet_url):
    # Escopo da API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Credenciais da conta de serviço
    credentials = ServiceAccountCredentials.from_json_keyfile_name("C:\Users\victornadim\Desktop\dashboard-apura-sus.git\luminous-empire-456918-d2-bce5145c696b.json", scope)

    # Autenticar e acessar o Google Sheets
    client = gspread.authorize(credentials)

    # Abrir a planilha pelo URL
    sheet = client.open_by_url(sheet_url)

    # Selecionar a primeira aba da planilha
    worksheet = sheet.get_worksheet(0)

    # Obter os dados como uma lista de listas
    data = worksheet.get_all_records()

    # Converter para um DataFrame do Pandas
    df = pd.DataFrame(data)

    return df

# URL da planilha no Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/1xpIBGZibAYcOjrs5yR0lBggW8OBziMzPnJb-5Vfef38/edit?usp=sharing"

# Substitua a função de carregamento de dados local
df = load_data_from_sheets(sheet_url)

# Formatar a coluna de Data para exibir apenas mês/ano
df['Data'] = pd.to_datetime(df['Data']).dt.to_period('M').astype(str)

# Converter a coluna 'Valor' para numérica
df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

# Verificar as colunas do DataFrame
print("Colunas do DataFrame:", df.columns)

# Layout do Dashboard
app.layout = html.Div(
    children=[

        html.Img(
            src="/assets/logoses.png",  # Caminho para a logo
            className="logo",  # Classe CSS para posicionar a logo
            style={"width": "100px", "height": "auto", "position": "absolute", "top": "10px", "left": "10px"}
        ),
        
        # Botão para Modo Daltonismo
        html.Button(
            "Modo Daltonismo", 
            id="color-mode-button",  # ID do botão
            n_clicks=0,  # Contador de cliques
            style={
                'position': 'absolute',
                'top': '10px',
                'right': '10px',
                'padding': '10px 20px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontSize': '14px'
            }
        ),

        html.Button(
            "Gerar Relatório (PDF)", 
            id="generate-pdf-button",  # ID do botão
            n_clicks=0,  # Contador de cliques
            style={
                'position': 'absolute',
                'top': '10px',
                'right': '10px',
                'padding': '10px 20px',
                'backgroundColor': '#28a745',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontSize': '14px'
            }
        ),
        dcc.Download(id="download-pdf"),  # Componente para gerenciar o download
        
        html.H1(
            "Apura-SUS",
            className="custom-title"  # Classe CSS para o título
        ),
        
        # Filtros
        html.Div([
            html.Label("Filtrar por Data (Mês/Ano):"),
            dcc.Dropdown(
                id="date-filter",
                options=[{"label": date, "value": date} for date in df['Data'].unique()],
                value=[df['Data'].unique()[0]],  # Valor inicial como lista
                multi=True  # Permitir múltiplas seleções
            ),
            html.Label("Filtrar por Hospital:"),
            dcc.Dropdown(
                id="hospital-filter",
                options=[{"label": hospital, "value": hospital} for hospital in df['Hospital'].unique()],
                value=[df['Hospital'].unique()[0]],  # Valor inicial como lista
                multi=True  # Permitir múltiplas seleções
            ),
            html.Label("Filtrar por Centro de Custo:"),
            html.Div([
                dcc.Dropdown(
                    id="cost-center-filter",
                    options=[{"label": cost_center, "value": cost_center} for cost_center in df['Centro de Custo'].unique()],
                    value=[df['Centro de Custo'].unique()[0]],  # Apenas o primeiro valor selecionado inicialmente
                    multi=True  # Permitir múltiplas seleções
                ),
                html.Button(
                    "Selecionar Todos", 
                    id="select-all-cost-centers",  # ID do botão
                    n_clicks=0,  # Contador de cliques
                    style={
                        'marginTop': '10px',
                        'padding': '10px 20px',
                        'backgroundColor': '#007bff',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontSize': '14px'
                    }
                )
            ]),
            html.Label("Filtrar por Categoria:"),
            dcc.Dropdown(
                id="category-filter",
                options=[{"label": category, "value": category} for category in df['Categoria'].unique()],
                value=[df['Categoria'].unique()[0]],  # Valor inicial como lista
                multi=True  # Permitir múltiplas seleções
            ),
            # Valor Total logo abaixo dos filtros
            html.H3(
                id="total-value",
                className="total-value",  # Classe CSS para o valor total
                style={
                    'marginTop': '20px',  # Espaçamento superior
                    'color': 'white',  # Cor branca para o texto
                    'textAlign': 'center'  # Centralizar o texto
                }
            ),
        ], className="custom-card"),  # Classe CSS para o card dos filtros
        
        # Informações sobre os gastos por hospital, categorias e centro de custo
        html.Div([
            html.H3(
                "Informações sobre os Gastos por Hospital, Categorias e Centro de Custo",
                style={
                    'textAlign': 'center',
                    'color': 'white',
                    'marginBottom': '20px'
                }
            ),
            # Informações por Categoria
            html.Div([
                html.H4("Gastos por Categoria:", style={'color': 'white'}),
                html.Div(id="category-info", style={'color': 'white', 'fontSize': '16px'})
            ], className="custom-card"),
            # Informações por Subcategoria
            html.Div([
                html.H4("Gastos por Subcategoria:", style={'color': 'white'}),
                html.Div(id="subcategory-info", style={'color': 'white', 'fontSize': '16px'})
            ], className="custom-card"),
            # Informações por Hospital
            html.Div([
                html.H4("Gastos por Hospital:", style={'color': 'white'}),
                html.Div(id="hospital-info", style={'color': 'white', 'fontSize': '16px'})
            ], className="custom-card"),
        ], className="custom-card"),
        
        # Gráficos
        html.Div([
            dcc.Graph(id="category-bar-chart"),  # Gráfico de barras para categorias
            dcc.Graph(id="subcategory-bar-chart"),  # Gráfico de barras para subcategorias
            dcc.Graph(id="hospital-bar-chart"),  # Gráfico de barras para hospitais
            dcc.Graph(id="cost-center-bar-chart"),  # Gráfico de barras para centro de custo
        ], className="custom-card"),  # Classe CSS para o card dos gráficos
    ]
)

# Callback para atualizar os gráficos e o valor total com base nos filtros
@app.callback(
    [Output("category-bar-chart", "figure"),
     Output("subcategory-bar-chart", "figure"),
     Output("hospital-bar-chart", "figure"),
     Output("cost-center-bar-chart", "figure"),
     Output("total-value", "children"),
     Output("category-info", "children"),  # Informações por Categoria
     Output("subcategory-info", "children"),  # Informações por Subcategoria
     Output("hospital-info", "children"),  # Informações por Hospital
     Output("color-mode-button", "children")],  # Atualiza o texto do botão
    [Input("date-filter", "value"),
     Input("hospital-filter", "value"),
     Input("cost-center-filter", "value"),
     Input("category-filter", "value"),
     Input("color-mode-button", "n_clicks")]  # Número de cliques no botão
)
def update_dashboard(dates, hospitals, cost_centers, categories, n_clicks):
    # Determinar o modo com base no número de cliques
    is_daltonic_mode = n_clicks % 2 == 1  # Alterna entre True e False
    
    # Cores para o modo normal e daltônico
    normal_colors = px.colors.qualitative.Plotly
    daltonic_colors = px.colors.qualitative.Safe  # Paleta amigável para Deuteranopia
    
    # Escolher as cores com base no modo
    colors = daltonic_colors if is_daltonic_mode else normal_colors
    
    # Filtrar os dados com base nos filtros selecionados
    filtered_df = df[
        (df['Data'].isin(dates)) &
        (df['Hospital'].isin(hospitals)) &
        (df['Centro de Custo'].isin(cost_centers)) &
        (df['Categoria'].isin(categories))
    ]
    
    # Verificar se há dados filtrados
    if filtered_df.empty:
        return {}, {}, {}, {}, "Nenhum dado encontrado para os filtros selecionados.", "Nenhum dado encontrado para os filtros selecionados.", "Nenhum dado encontrado para os filtros selecionados.", "Nenhum dado encontrado para os filtros selecionados.", "Modo Daltonismo" if is_daltonic_mode else "Modo Normal"
    
    # Calcular o valor total
    total_value = f"Valor Total: R$ {filtered_df['Valor'].sum():,.2f}"
    
    # Gráfico de barras para categorias
    category_totals = filtered_df.groupby("Categoria")["Valor"].sum().reset_index()
    category_totals["Percentual"] = (category_totals["Valor"] / category_totals["Valor"].sum()) * 100
    category_bar_chart = px.bar(
        category_totals,
        x="Categoria",
        y="Valor",
        text="Percentual",  # Adiciona os percentuais como rótulos
        title="Gastos por Categoria",
        color="Categoria",
        color_discrete_sequence=colors
    )
    category_bar_chart.update_traces(texttemplate='%{text:.2f}%', textposition='outside')  # Formata os rótulos
    category_bar_chart.update_layout(
        plot_bgcolor='#C0C0C0',
        paper_bgcolor='#C0C0C0',
        font=dict(color='#333'),
        xaxis_title="Categoria",
        yaxis_title="Valor (R$)",
        title_font=dict(size=18, color='#333'),
        legend_title=dict(font=dict(size=12))
    )
    
    # Gráfico de barras para subcategorias
    subcategory_totals = filtered_df.groupby("Subcategoria")["Valor"].sum().reset_index()
    subcategory_totals["Percentual"] = (subcategory_totals["Valor"] / subcategory_totals["Valor"].sum()) * 100
    subcategory_bar_chart = px.bar(
        subcategory_totals,
        x="Subcategoria",
        y="Valor",
        text="Percentual",  # Adiciona os percentuais como rótulos
        title="Gastos por Subcategoria",
        color="Subcategoria",
        color_discrete_sequence=colors
    )
    subcategory_bar_chart.update_traces(texttemplate='%{text:.2f}%', textposition='outside')  # Formata os rótulos
    subcategory_bar_chart.update_layout(
        plot_bgcolor='#C0C0C0',
        paper_bgcolor='#C0C0C0',
        font=dict(color='#333'),
        xaxis_title="Subcategoria",
        yaxis_title="Valor (R$)",
        title_font=dict(size=18, color='#333'),
        legend_title=dict(font=dict(size=12))
    )
    
    # Gráfico de barras para hospitais
    hospital_totals = filtered_df.groupby("Hospital")["Valor"].sum().reset_index()
    hospital_totals["Percentual"] = (hospital_totals["Valor"] / hospital_totals["Valor"].sum()) * 100
    hospital_bar_chart = px.bar(
        hospital_totals,
        x="Hospital",
        y="Valor",
        text="Percentual",  # Adiciona os percentuais como rótulos
        title="Gastos por Hospital",
        color="Hospital",
        color_discrete_sequence=colors
    )
    hospital_bar_chart.update_traces(texttemplate='%{text:.2f}%', textposition='outside')  # Formata os rótulos
    hospital_bar_chart.update_layout(
        plot_bgcolor='#C0C0C0',
        paper_bgcolor='#C0C0C0',
        font=dict(color='#333'),
        xaxis_title="Hospital",
        yaxis_title="Valor (R$)",
        title_font=dict(size=18, color='#333'),
        legend_title=dict(font=dict(size=12))
    )
    
    # Gráfico de barras para centro de custo
    cost_center_totals = filtered_df.groupby("Centro de Custo")["Valor"].sum().reset_index()
    cost_center_totals["Percentual"] = (cost_center_totals["Valor"] / cost_center_totals["Valor"].sum()) * 100
    cost_center_bar_chart = px.bar(
        cost_center_totals,
        x="Centro de Custo",
        y="Valor",
        text="Percentual",  # Adiciona os percentuais como rótulos
        title="Gastos por Centro de Custo",
        color="Centro de Custo",
        color_discrete_sequence=colors
    )
    cost_center_bar_chart.update_traces(texttemplate='%{text:.2f}%', textposition='outside')  # Formata os rótulos
    cost_center_bar_chart.update_layout(
        plot_bgcolor='#C0C0C0',
        paper_bgcolor='#C0C0C0',
        font=dict(color='#333'),
        xaxis_title="Centro de Custo",
        yaxis_title="Valor (R$)",
        title_font=dict(size=18, color='#333'),
        legend_title=dict(font=dict(size=12))
    )
    
    # Informações sobre os gastos por categoria
    category_info = [
        html.Div(f"{row['Categoria']}: R$ {row['Valor']:,.2f} ({row['Percentual']:.2f}%)")
        for _, row in category_totals.iterrows()
    ]
    
    # Informações sobre os gastos por subcategoria
    subcategory_info = [
        html.Div(f"{row['Subcategoria']}: R$ {row['Valor']:,.2f} ({row['Percentual']:.2f}%)")
        for _, row in subcategory_totals.iterrows()
    ]
    
    # Informações sobre os gastos por hospital
    hospital_info = [
        html.Div(f"{row['Hospital']}: R$ {row['Valor']:,.2f} ({row['Percentual']:.2f}%)")
        for _, row in hospital_totals.iterrows()
    ]
    
    # Atualizar o texto do botão
    button_text = "Modo Normal" if is_daltonic_mode else "Modo Daltonismo"
    
    return category_bar_chart, subcategory_bar_chart, hospital_bar_chart, cost_center_bar_chart, total_value, category_info, subcategory_info, hospital_info, button_text

@app.callback(
    Output("cost-center-filter", "value"),  # Atualiza o valor do dropdown
    Input("select-all-cost-centers", "n_clicks")  # Entrada do botão
)
def select_all_cost_centers(n_clicks):
    if n_clicks > 0:  # Se o botão for clicado
        return [cost_center for cost_center in df['Centro de Custo'].unique()]  # Seleciona todas as opções
    return dash.no_update  # Não atualiza se o botão não for clicado

@app.callback(
    Output("download-pdf", "data"),  # Vincula o download ao componente dcc.Download
    [Input("generate-pdf-button", "n_clicks")],  # Dispara o download ao clicar no botão
    [State("date-filter", "value"),  # Filtros aplicados no dashboard
     State("hospital-filter", "value"),
     State("cost-center-filter", "value"),
     State("category-filter", "value")],
    prevent_initial_call=True  # Evita que o callback seja executado ao carregar a página
)
def generate_pdf(n_clicks, dates, hospitals, cost_centers, categories):
    # Filtrar os dados com base nos filtros selecionados
    filtered_df = df[
        (df['Data'].isin(dates)) &
        (df['Hospital'].isin(hospitals)) &
        (df['Centro de Custo'].isin(cost_centers)) &
        (df['Categoria'].isin(categories))
    ]

    # Criar o PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Adicionar a logo
    pdf.image("assets/logoses.png", x=10, y=8, w=30)  # Ajuste o tamanho conforme necessário
    pdf.ln(20)  # Espaçamento após a imagem

    # Adicionar título principal
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Relatório de Gastos - Apura SUS", ln=True, align='C')
    pdf.ln(10)

    # Adicionar informações filtradas
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Datas Selecionadas: {', '.join(dates)}", ln=True)
    pdf.cell(200, 10, txt=f"Hospitais Selecionados: {', '.join(hospitals)}", ln=True)
    pdf.cell(200, 10, txt=f"Centros de Custo Selecionados: {', '.join(cost_centers)}", ln=True)
    pdf.cell(200, 10, txt=f"Categorias Selecionadas: {', '.join(categories)}", ln=True)
    pdf.ln(10)

    # Adicionar tabela de gastos por categoria
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Gastos por Categoria:", ln=True)
    pdf.set_font("Arial", size=12)
    category_totals = filtered_df.groupby("Categoria")["Valor"].sum().reset_index()
    for _, row in category_totals.iterrows():
        pdf.cell(200, 10, txt=f"- {row['Categoria']}: R$ {row['Valor']:,.2f}", ln=True)
    pdf.ln(10)

    # Adicionar tabela de gastos por hospital
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Gastos por Hospital:", ln=True)
    pdf.set_font("Arial", size=12)
    hospital_totals = filtered_df.groupby("Hospital")["Valor"].sum().reset_index()
    for _, row in hospital_totals.iterrows():
        pdf.cell(200, 10, txt=f"- {row['Hospital']}: R$ {row['Valor']:,.2f}", ln=True)
    pdf.ln(10)

    # Adicionar tabela de gastos por centro de custo
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Gastos por Centro de Custo:", ln=True)
    pdf.set_font("Arial", size=12)
    cost_center_totals = filtered_df.groupby("Centro de Custo")["Valor"].sum().reset_index()
    for _, row in cost_center_totals.iterrows():
        pdf.cell(200, 10, txt=f"- {row['Centro de Custo']}: R$ {row['Valor']:,.2f}", ln=True)
    pdf.ln(10)

    # Salvar o PDF em memória
    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)

    # Retornar o PDF para download
    return dcc.send_bytes(
        pdf_output.getvalue(),  # Conteúdo do PDF
        filename="relatorio.pdf"  # Nome do arquivo para download
    )

# Rodar o App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))  # Use a porta fornecida pelo Render ou 8050 como padrão
    app.run(host="0.0.0.0", port=port, debug=True)