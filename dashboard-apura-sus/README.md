# Dashboard Apura SUS

Este projeto é um dashboard interativo desenvolvido com Dash, que permite visualizar e analisar dados relacionados aos gastos em saúde. O dashboard utiliza um arquivo Excel como fonte de dados e oferece funcionalidades para filtrar informações e gerar relatórios em PDF.

## Estrutura do Projeto

- **assets/logo_govmt_horizontal.jpg**: Imagem utilizada como logo no dashboard.
- **data/Base de Dados - Apura SUS.xlsx**: Planilha Excel contendo os dados utilizados pelo dashboard.
- **dashboard.py**: Arquivo principal da aplicação. Inicializa o aplicativo Dash, carrega os dados do arquivo Excel, configura o layout e define callbacks para interatividade. Inclui funções para gerar visualizações e um relatório em PDF.
- **requirements.txt**: Lista as dependências Python necessárias para o projeto, como Dash, Pandas, Plotly e FPDF.

## Instalação

1. Clone este repositório:
   ```
   git clone <URL_DO_REPOSITORIO>
   cd dashboard-apura-sus
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```
   python -m venv venv
   source venv/bin/activate  # Para Linux/Mac
   venv\Scripts\activate  # Para Windows
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Execução

Para executar o dashboard, utilize o seguinte comando:
```
python dashboard.py
```

O aplicativo estará disponível em `http://127.0.0.1:8050/` no seu navegador.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.