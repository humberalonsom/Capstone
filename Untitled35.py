import streamlit as st
import pandas as pd
import plotly.express as px
from googletrans import Translator

# Sttreamlit settings
st.set_page_config(page_title="Customer Insights Dashboard", layout="wide")

# Load CSV
@st.cache_data(show_spinner=True)
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"El archivo {file_path} no se encontró.")
        return pd.DataFrame()

df_customers = load_data("clustered_df.csv")
df_state = load_data("state.csv")
df_industry = load_data("industry.csv")

# Mapping for cluster labels
cluster_labels = {
    0: "Very Low",
    1: "Low",
    2: "Medium",
    3: "High",
    4: "Very High"
}

# Apply cluster labels to the dataframe
df_customers['cluster_label'] = df_customers['cluster'].map(cluster_labels)

# Replace "_" to " " 
def format_label(label):
    return label.replace('_', ' ').capitalize()

# CSS Styles
def inject_css():
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            background-color: #f0f8ff;  /* Fondo azul claro */
            font-family: 'Roboto', sans-serif;
        }
        .main-title {
            font-size: 3em;
            color: #0033cc;  /* Azul principal */
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .sub-title {
            font-size: 2em;
            color: #0033cc;  /* Azul principal */
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .section-header {
            font-size: 1.8em;
            color: #0033cc;  /* Azul principal */
            font-weight: bold;
            margin-top: 20px;
        }
        .uploaded-data, .search-results {
            margin-top: 20px;
        }
        .dataframe {
            border: 2px solid #0033cc;  /* Azul principal */
            border-radius: 10px;
            padding: 10px;
            margin-top: 10px;
            background: #ffffff;  /* Blanco */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;  /* Blanco */
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .stButton>button {
            background-color: #0033cc;  /* Azul principal */
            color: white;
            font-weight: bold;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #002699;  /* Azul más oscuro para hover */
        }
        .stTextInput>div>div>input {
            background-color: #ffffff;  /* Blanco */
            border: 2px solid #0033cc;  /* Azul principal */
            border-radius: 5px;
            padding: 5px;
            transition: all 0.3s ease;
        }
        .stTextInput>div>div>input:focus {
            border-color: #002699;  /* Azul más oscuro para focus */
        }
        .language-selector {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
            margin-top: 10px;
        }
        .flag-icon {
            width: 30px;
            height: 20px;
            cursor: pointer;
            margin: 0 5px;
            transition: transform 0.3s ease;
        }
        .flag-icon:hover {
            transform: scale(1.1);
        }
        </style>
    """, unsafe_allow_html=True)

inject_css()

# Show logo
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://raw.githubusercontent.com/humberalonsom/Capstone/main/olist_logo.png' width='200'>
    </div>
""", unsafe_allow_html=True)

# Selección de idioma con íconos de banderas en la parte superior de la página
languages = {
    "English": ("en", "https://upload.wikimedia.org/wikipedia/en/a/a4/Flag_of_the_United_States.svg"),
    "Español": ("es", "https://upload.wikimedia.org/wikipedia/commons/9/9a/Flag_of_Spain.svg"),
    "Français": ("fr", "https://upload.wikimedia.org/wikipedia/en/c/c3/Flag_of_France.svg"),
    "Deutsch": ("de", "https://upload.wikimedia.org/wikipedia/en/b/ba/Flag_of_Germany.svg"),
    "中文": ("zh-cn", "https://upload.wikimedia.org/wikipedia/commons/f/f3/Flag_of_the_People%27s_Republic_of_China.svg")
}
st.markdown("<div class='language-selector'>", unsafe_allow_html=True)
for lang, (code, flag_url) in languages.items():
    st.markdown(f"""
        <a href="?lang={code}">
            <img src="{flag_url}" class="flag-icon" title="{lang}" alt="{lang}">
        </a>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Title
st.markdown("<div class='main-title'>Customer Insights Dashboard</div>", unsafe_allow_html=True)

# Translator
translator = Translator()

@st.cache_data(show_spinner=True)
def translate_text(text, dest_language):
    try:
        return translator.translate(text, dest_language).text
    except Exception as e:
        return text

# Get lenguage
query_params = st.experimental_get_query_params()
dest_language = query_params.get("lang", ["en"])[0]

# Traduce
def t(text):
    return translate_text(text, dest_language)

# Save temporally results
df_customers_filtered = pd.DataFrame()

# Upload files
def handle_file_upload(uploaded_file):
    if uploaded_file:
        try:
            df_uploaded = pd.read_excel(uploaded_file)
            if 'customer_id' not in df_uploaded.columns:
                st.sidebar.error(t("The uploaded file must contain a 'customer_id' column."))
                return pd.DataFrame()
            customer_ids = df_uploaded['customer_id'].astype(str).tolist()
            df_filtered = df_customers[df_customers['customer_id'].astype(str).isin(customer_ids)]
            st.sidebar.write(t("### Uploaded Data"))
            st.sidebar.write(df_uploaded)
            return df_filtered
        except Exception as e:
            st.sidebar.error(t("Error processing the uploaded file. Please ensure it is an Excel file with a 'customer_id' column."))
    return pd.DataFrame()

# load excel
uploaded_file = st.sidebar.file_uploader(t("Upload an Excel file with Customer IDs"), type=["xlsx"])
df_customers_filtered = handle_file_upload(uploaded_file)

# Manual search
st.sidebar.markdown(f"<div class='section-header'>{t('Manual Search')}</div>", unsafe_allow_html=True)
customer_id = st.sidebar.text_input(t("Customer ID:"))
if st.sidebar.button(t("Search")):
    query = df_customers[df_customers['customer_id'].astype(str).str.strip() == customer_id.strip()]
    df_customers_filtered = pd.concat([df_customers_filtered, query]).drop_duplicates()

# Show uploded data
def display_search_results(df):
    if not df.empty:
        st.markdown(f"<div class='sub-title'>{t('Search Results')}</div>", unsafe_allow_html=True)
        df_display = df.copy()
        df_display.columns = [format_label(col) for col in df_display.columns]
        st.write(df_display)
    else:
        st.markdown(f"<div class='sub-title'>{t('No customer data to display. Upload an Excel file or use the search bar to find customers.')}</div>", unsafe_allow_html=True)

display_search_results(df_customers_filtered)

# Create windowa
tab = st.selectbox(t("Select a tab"), [t("Graphs"), t("State Data"), t("Industry Data"), t("Sales by State")])

def display_graphs(df):
    if not df.empty:
        st.markdown(f"<div class='section-header'>{t('Graphs')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-header'>{t('Cluster Distribution')}</div>", unsafe_allow_html=True)
        cluster_pie_chart = px.pie(df, names='cluster_label', title=t('Cluster Distribution'))
        cluster_pie_chart.update_layout(title_text=t('Cluster Distribution'), template='plotly_dark')
        st.plotly_chart(cluster_pie_chart)

        st.markdown(f"<div class='section-header'>{t('Average Price per Industry')}</div>", unsafe_allow_html=True)
        average_price_data = df.groupby('product_category_name')['average_price'].mean().reset_index()
        average_price_bar_chart = px.bar(average_price_data, x=average_price_data['product_category_name'].apply(format_label), y='average_price', title=t('Average Price per Industry'))
        average_price_bar_chart.update_layout(xaxis_title=t('Product Category Name'), yaxis_title=t('Average Price'), template='plotly_dark')
        st.plotly_chart(average_price_bar_chart)

        st.markdown(f"<div class='section-header'>{t('Customer Value per Industry')}</div>", unsafe_allow_html=True)
        customer_value_data = df.groupby('product_category_name')['customer_lifetime_value'].mean().reset_index()
        customer_value_bar_chart = px.bar(customer_value_data, x=customer_value_data['product_category_name'].apply(format_label), y='customer_lifetime_value', title=t('Customer Value per Industry'))
        customer_value_bar_chart.update_layout(xaxis_title=t('Product Category Name'), yaxis_title=t('Customer Lifetime Value'), template='plotly_dark')
        st.plotly_chart(customer_value_bar_chart)
    else:
        st.markdown(f"<div class='sub-title'>{t('No data to display in graphs. Upload an Excel file or use the search bar to find customers.')}</div>", unsafe_allow_html=True)

def display_state_data(df, state):
    st.markdown(f"<div class='section-header'>{t('State Data')}</div>", unsafe_allow_html=True)
    filtered_df = df[df['customer_state'] == state]
    
    st.markdown(f"<div class='section-header'>{t('Count of Industries in')} {state}</div>", unsafe_allow_html=True)
    count_industry_bar_chart = px.bar(filtered_df, x=filtered_df['product_category_name'].apply(format_label), y='Count_industry', title=t(f'Count of Industries in {state}'))
    count_industry_bar_chart.update_layout(xaxis_title=t('Product Category Name'), yaxis_title=t('Count Industry'), template='plotly_dark')
    st.plotly_chart(count_industry_bar_chart)
    
    st.markdown(f"<div class='section-header'>{t('Average Price in')} {state} {t('by Industry')}</div>", unsafe_allow_html=True)
    average_price_bar_chart = px.bar(filtered_df, x=filtered_df['product_category_name'].apply(format_label), y='Average Price per state', title=t(f'Average Price in {state} by Industry'))
    average_price_bar_chart.update_layout(xaxis_title=t('Product Category Name'), yaxis_title=t('Average Price'), template='plotly_dark')
    st.plotly_chart(average_price_bar_chart)

def display_industry_data(df, industry):
    st.markdown(f"<div class='section-header'>{t('Industry Data')}</div>", unsafe_allow_html=True)
    filtered_df = df[df['product_category_name'] == industry]
    
    if not filtered_df.empty:
        st.markdown(f"<div class='section-header'>{t('Sales Data for')} {industry}</div>", unsafe_allow_html=True)
        df_display = filtered_df.copy()
        df_display.columns = [format_label(col) for col in df_display.columns]
        st.write(df_display)

        # Calculate average price and lifetime value
        if 'price' in filtered_df.columns and 'order_id' in filtered_df.columns:
            average_price_industry = filtered_df['price'].mean()
            customer_lifetime_value_industry = filtered_df.groupby('customer_id')['price'].sum().mean()
            
            st.markdown(f"<div class='section-header'>{t('Average Price in')} {industry}</div>", unsafe_allow_html=True)
            st.metric(label=t('Average Price'), value=f"${average_price_industry:,.2f}")

            st.markdown(f"<div class='section-header'>{t('Customer Lifetime Value in')} {industry}</div>", unsafe_allow_html=True)
            st.metric(label=t('Customer Lifetime Value'), value=f"${customer_lifetime_value_industry:,.2f}")

            st.markdown(f"<div class='section-header'>{t('Graphs for')} {industry}</div>", unsafe_allow_html=True)
            
            fig1 = px.histogram(filtered_df, x='price', title=t('Distribution of Prices'))
            st.plotly_chart(fig1)
            
            fig2 = px.histogram(filtered_df.groupby('customer_id')['price'].sum().reset_index(), x='price', title=t('Distribution of Customer Lifetime Values'))
            st.plotly_chart(fig2)
        else:
            st.warning(f"{t('No price or order data available for')} {industry}.")
    else:
        st.markdown(f"<div class='sub-title'>{t('No data to display for')} {industry}.</div>", unsafe_allow_html=True)

def display_sales_by_state(df):
    st.markdown(f"<div class='section-header'>{t('Sales by State')}</div>", unsafe_allow_html=True)
    
    if not df.empty:
        orders_by_state = df.groupby('customer_state').size().reset_index(name='orders')
        
        fig = px.choropleth(orders_by_state, 
                            geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
                            locations='customer_state', 
                            featureidkey="properties.sigla", 
                            color='orders', 
                            color_continuous_scale="Viridis",
                            title=t('Orders by State in Brazil'))
        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig)
    else:
        st.markdown(f"<div class='sub-title'>{t('No order data to display.')}</div>", unsafe_allow_html=True)

if tab == t("Graphs"):
    display_graphs(df_customers_filtered)
elif tab == t("State Data"):
    state = st.selectbox(t("Select a state"), df_state['customer_state'].unique())
    display_state_data(df_state, state)
elif tab == t("Industry Data"):
    industry = st.selectbox(t("Select an industry"), df_industry['product_category_name'].unique())
    display_industry_data(df_industry, industry)
elif tab == t("Sales by State"):
    display_sales_by_state(df_customers_filtered)

