import streamlit as st
import pandas as pd
import plotly.express as px
from googletrans import Translator

# Cargar los datos del archivo CSV
df_customers = pd.read_csv("clustered_df.csv")
df_state = pd.read_csv("state.csv")
df_industry = pd.read_csv("industry.csv")

# Función para reemplazar guiones bajos con espacios y capitalizar
def format_label(label):
    return label.replace('_', ' ').capitalize()

# Configurar la página de Streamlit
st.set_page_config(page_title="Customer Insights Dashboard", layout="wide")

# Añadir estilos CSS personalizados directamente en el código
st.markdown("""
    <style>
    body {
        background-color: #f0f8ff;
        font-family: 'Arial', sans-serif;
    }
    .main-title {
        font-size: 2.5em;
        color: #4CAF50;
        text-align: center;
        font-weight: bold;
    }
    .sub-title {
        font-size: 2em;
        color: #2E7D32;
        text-align: center;
        font-weight: bold;
    }
    .section-header {
        font-size: 1.5em;
        color: #1B5E20;
        font-weight: bold;
        margin-top: 20px;
    }
    .uploaded-data, .search-results {
        margin-top: 20px;
    }
    .dataframe {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 10px;
        margin-top: 10px;
    }
    .sidebar .sidebar-content {
        background-color: #E8F5E9;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #E8F5E9;
        border: 2px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("<div class='main-title'>Customer Insights Dashboard</div>", unsafe_allow_html=True)

# Función para traducir texto
translator = Translator()

def translate_text(text, dest_language):
    try:
        return translator.translate(text, dest=dest_language).text
    except Exception as e:
        return text

# Selección de idioma
language = st.sidebar.selectbox("Select Language", ["en", "es", "fr", "de", "zh-cn"])

# Traducir texto de la interfaz
def t(text):
    return translate_text(text, language)

# Variables para almacenamiento temporal de resultados
df_customers_filtered = pd.DataFrame()

# Cargar archivo Excel
uploaded_file = st.sidebar.file_uploader(t("Upload an Excel file with Customer IDs"), type=["xlsx"])
if uploaded_file:
    df_uploaded = pd.read_excel(uploaded_file)
    customer_ids = df_uploaded['customer_id'].astype(str).tolist()
    df_customers_filtered = df_customers[df_customers['customer_id'].astype(str).isin(customer_ids)]
    st.sidebar.write(t("### Uploaded Data"))
    st.sidebar.write(df_uploaded)

# Interfaz para la búsqueda manual
st.sidebar.markdown(f"<div class='section-header'>{t('Manual Search')}</div>", unsafe_allow_html=True)
customer_id = st.sidebar.text_input(t("Customer ID:"))
if st.sidebar.button(t("Search")):
    query = df_customers[df_customers['customer_id'].astype(str).str.strip() == customer_id.strip()]
    df_customers_filtered = pd.concat([df_customers_filtered, query]).drop_duplicates()

# Mostrar los datos cargados o buscados manualmente si existen
if not df_customers_filtered.empty:
    st.markdown(f"<div class='sub-title'>{t('Search Results')}</div>", unsafe_allow_html=True)
    st.write(df_customers_filtered)
else:
    st.markdown(f"<div class='sub-title'>{t('No customer data to display. Upload an Excel file or use the search bar to find customers.')}</div>", unsafe_allow_html=True)

# Crear pestañas
tab = st.selectbox(t("Select a tab"), [t("Graphs"), t("State Data"), t("Industry Data")])

if tab == t("Graphs"):
    if not df_customers_filtered.empty:
        st.markdown(f"<div class='section-header'>{t('Graphs')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-header'>{t('Cluster Distribution')}</div>", unsafe_allow_html=True)
        cluster_pie_chart = px.pie(df_customers_filtered, names='cluster', title=t('Cluster Distribution'))
        cluster_pie_chart.update_layout(title_text=t('Cluster Distribution'))
        st.plotly_chart(cluster_pie_chart)

        st.markdown(f"<div class='section-header'>{t('Average Price per Industry')}</div>", unsafe_allow_html=True)
        average_price_data = df_customers_filtered.groupby('product_category_name')['average_price'].mean().reset_index()
        average_price_bar_chart = px.bar(average_price_data, x='product_category_name', y='average_price', title=t('Average Price per Industry'))
        average_price_bar_chart.update_layout(xaxis_title=t('Product Category Name'), yaxis_title=t('Average Price'))
        st.plotly_chart(average_price_bar_chart)

        st.markdown(f"<div class='section-header'>{t('Customer Value per Industry')}</div>", unsafe_allow_html=True)
        customer_value_data = df_customers_filtered.groupby('product_category_name')['customer_lifetime_value'].mean().reset_index()
        customer_value_bar_chart = px.bar(customer_value_data, x='product_category_name', y='customer_lifetime_value', title=t('Customer Value per Industry'))
        customer_value_bar_chart.update_layout(xaxis_title=t('Product Category Name'), yaxis_title=t('Customer Lifetime Value'))
        st.plotly_chart(customer_value_bar_chart)
    else:
        st.markdown(f"<div class='sub-title'>{t('No data to display in graphs. Upload an Excel file or use the search bar to find customers.')}</div>", unsafe_allow_html=True)

elif tab == t("State Data"):
    st.markdown(f"<div class='section-header'>{t('State Data')}</div>", unsafe_allow_html=True)
    state = st.selectbox(t("Select a state"), df_state['customer_state'].unique())
    filtered_df = df_state[df_state['customer_state'] == state]
    
    st.markdown(f"<div class='section-header'>{t('Count of Industries in')} {state}</div>", unsafe_allow_html=True)
    count_industry_bar_chart = px.bar(filtered_df, x='product_category_name', y='Count_industry', title=t(f'Count of Industries in {state}'))
    count_industry_bar_chart.update_layout(xaxis_title=t('Product Category Name'), yaxis_title=t('Count Industry'))
    st.plotly_chart(count_industry_bar_chart)
    
    st.markdown(f"<div class='section-header'>{t('Average Price in')} {state} {t('by Industry')}</div>", unsafe_allow_html=True)
    average_price_bar_chart = px.bar(filtered_df, x='product_category_name', y='Average Price per state', title=t(f'Average Price in {state} by Industry'))
    average_price_bar_chart.update_layout(xaxis_title=t('Product Category Name'), yaxis_title=t('Average Price'))
    st.plotly_chart(average_price_bar_chart)

elif tab == t("Industry Data"):
    st.markdown(f"<div class='section-header'>{t('Industry Data')}</div>", unsafe_allow_html=True)
    industry = st.selectbox(t("Select an industry"), df_industry['product_category_name'].unique())
    filtered_df = df_industry[df_industry['product_category_name'] == industry]
    
    st.markdown(f"<div class='section-header'>{t('Count of States for')} {format_label(industry)}</div>", unsafe_allow_html=True)
    count_state_bar_chart = px.bar(filtered_df, x='customer_state', y='Count_state', title=t(f'Count of States for {format_label(industry)}'))
    count_state_bar_chart.update_layout(xaxis_title=t('Customer State'), yaxis_title=t('Count State'))
    st.plotly_chart(count_state_bar_chart)
    
    st.markdown(f"<div class='section-header'>{t('Average Price for')} {format_label(industry)} {t('by State')}</div>", unsafe_allow_html=True)
    average_price_bar_chart = px.bar(filtered_df, x='customer_state', y='Average Price per state', title=t(f'Average Price for {format_label(industry)} by State'))
    average_price_bar_chart.update_layout(xaxis_title=t('Customer State'), yaxis_title=t('Average Price'))
    st.plotly_chart(average_price_bar_chart)
