import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar los datos del archivo CSV
df_customers = pd.read_csv("clustered_df.csv")
df_state = pd.read_csv("state.csv")
df_industry = pd.read_csv("industry.csv")

# Función para reemplazar guiones bajos con espacios
def format_label(label):
    return label.replace('_', ' ').capitalize()

# Configurar la página de Streamlit
st.set_page_config(page_title="Customer Dashboard", layout="wide")

# Crear pestañas usando selectbox
tab = st.sidebar.selectbox("Select a tab", ["Customer Database", "Graphs", "State Data", "Industry Data"])

uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx"])
if uploaded_file:
    df_uploaded = pd.read_excel(uploaded_file)
    customer_ids = df_uploaded['customer_id'].astype(str).tolist()
    df_customers = df_customers[df_customers['customer_id'].astype(str).isin(customer_ids)]

if tab == "Customer Database":
    st.title("Customer Database")
    customer_id = st.text_input("Customer ID:")
    if st.button("Search"):
        query = df_customers[df_customers['customer_id'].astype(str).str.strip() == customer_id.strip()]
        st.write(query)
    if st.button("Clear"):
        st.write(df_customers)

elif tab == "Graphs":
    st.title("Graphs")
    cluster_pie_chart = px.pie(df_customers, names='cluster', title='Cluster Distribution')
    st.plotly_chart(cluster_pie_chart)

    average_price_data = df_customers.groupby('product_category_name')['average_price'].mean().reset_index()
    average_price_bar_chart = px.bar(average_price_data, x='product_category_name', y='average_price', title='Average Price per Industry')
    st.plotly_chart(average_price_bar_chart)

    customer_value_data = df_customers.groupby('product_category_name')['customer_lifetime_value'].mean().reset_index()
    customer_value_bar_chart = px.bar(customer_value_data, x='product_category_name', y='customer_lifetime_value', title='Customer Value per Industry')
    st.plotly_chart(customer_value_bar_chart)

elif tab == "State Data":
    st.title("State Data")
    state = st.selectbox("Select a state", df_state['customer_state'].unique())
    filtered_df = df_state[df_state['customer_state'] == state]
    
    count_industry_bar_chart = px.bar(filtered_df, x='product_category_name', y='Count_industry', title=f'Count of Industries in {state}')
    st.plotly_chart(count_industry_bar_chart)
    
    average_price_bar_chart = px.bar(filtered_df, x='product_category_name', y='Average Price per state', title=f'Average Price in {state} by Industry')
    st.plotly_chart(average_price_bar_chart)

elif tab == "Industry Data":
    st.title("Industry Data")
    industry = st.selectbox("Select an industry", df_industry['product_category_name'].unique())
    filtered_df = df_industry[df_industry['product_category_name'] == industry]
    
    count_state_bar_chart = px.bar(filtered_df, x='customer_state', y='Count_state', title=f'Count of States for {format_label(industry)}')
    st.plotly_chart(count_state_bar_chart)
    
    average_price_bar_chart = px.bar(filtered_df, x='customer_state', y='Average Price per state', title=f'Average Price for {format_label(industry)} by State')
    st.plotly_chart(average_price_bar_chart)



