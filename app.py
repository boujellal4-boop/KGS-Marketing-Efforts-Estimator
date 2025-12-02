
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# App title and logo
st.image("KID-22300_KGS-Logo_Full Color.png", width=300)
st.title("KGS Marketing Efforts Estimator")

# Dropdown options
departments = ["Sales", "Customer Service", "HR", "Finance", "IT", "Operations", "Legal"]
countries = ["BE", "NL", "UK", "IE", "FR", "IT", "ES", "PT", "DE", "DK", "SE", "FI", "NO", "PL", "TR", "ZA", "ME", "OUT-OF-EMEA"]
services = [
    "Poster", "Whitepaper", "Presentation", "Catalogue", "Brochure", "Lead", "VR Experience", "Leaflet", "Website Banner", "Office Wall Design",
    "Translation (10 pages)", "Translation (20 pages)", "Game Preparation", "Social Media Campaign", "Video Production", "Event Support"
]

# Pricing model (average prices in EUR)
pricing = {
    "Poster": 150,
    "Whitepaper": 500,
    "Presentation": 300,
    "Catalogue": 800,
    "Brochure": 400,
    "Lead": 50,
    "VR Experience": 2000,
    "Leaflet": 100,
    "Website Banner": 250,
    "Office Wall Design": 1200,
    "Translation (10 pages)": 200,
    "Translation (20 pages)": 400,
    "Game Preparation": 1500,
    "Social Media Campaign": 1000,
    "Video Production": 2500,
    "Event Support": 3000
}

# Initialize session state
if 'services_list' not in st.session_state:
    st.session_state.services_list = []

# Function to add a service
with st.form("add_service_form"):
    department = st.selectbox("Select Department", departments)
    country = st.selectbox("Select Country", countries)
    service = st.selectbox("Select Service", services)
    quantity = st.number_input("Quantity", min_value=1, value=1)
    add_btn = st.form_submit_button("Add Another Service")
    if add_btn:
        st.session_state.services_list.append({"Department": department, "Country": country, "Service": service, "Quantity": quantity})

# Display added services
if st.session_state.services_list:
    st.write("### Added Services")
    st.table(pd.DataFrame(st.session_state.services_list))

# Estimate button
if st.button("Estimate"):
    df = pd.DataFrame(st.session_state.services_list)
    df['Unit Price (€)'] = df['Service'].map(pricing)
    df['Total (€)'] = df['Quantity'] * df['Unit Price (€)']
    total_savings = df['Total (€)'].sum()

    st.subheader(f"Total Estimated Savings: €{total_savings:,.2f}")

    # Bar chart
    fig = px.bar(df, x='Service', y='Total (€)', color='Service', title='Breakdown of Services')
    st.plotly_chart(fig)

    # Excel download
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estimate')
    st.download_button(label="Download Excel", data=output.getvalue(), file_name="estimate.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
