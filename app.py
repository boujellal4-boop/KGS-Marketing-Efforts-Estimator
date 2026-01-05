
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from pathlib import Path

# --- Logo & Title (byte-safe) ---
logo_bytes = None
for p in [
    Path("KID-22300_KGS-Logo_Full Color.png"),
    Path("assets/KID-22300_KGS-Logo_Full Color.png"),
    Path("assets/logo.png"),
    Path("logo.png"),
]:
    if p.exists():
        try:
            logo_bytes = p.read_bytes()
            break
        except Exception:
            logo_bytes = None

if logo_bytes:
    try:
        st.image(logo_bytes, width=220)
    except Exception:
        pass

st.markdown("<h1 style='text-align:center; margin-top:0;'>KGS Marketing Efforts Estimation</h1>", unsafe_allow_html=True)

pricing = {'Poster Design': 150, 'Brochure Design': 400, 'Catalogue Design': 800, 'Leaflet Design': 100, 'Presentation Design': 300, 'Whitepaper Creation': 500, 'Infographic Design': 250, 'Office Wall Design': 1200, 'Website Banner Design': 250, 'Social Media Graphics': 200, 'Translation (<5 pages)': 100, 'Translation (5–10 pages)': 180, 'Translation (10–20 pages)': 350, 'Translation (20–50 pages)': 800, 'Translation (>50 pages)': 1500, 'Website Event Registration Webpage': 600, 'Event Registration Handling': 400, 'Webpage Link for Campaign': 300, 'Video Production (<1 minute)': 800, 'Video Production (>1 minute)': 1500, 'Cost of One Lead Generated': 50, 'Specific PR Need': 1000, 'Market Research Report': 2000, 'Brand Guidelines Creation': 1500, 'VR Experience (1-day)': 2000, 'Event Support (on-site branding)': 1200, 'Event Support (digital assets)': 800, 'Webinar Setup & Promotion': 1000, 'Trade Show Booth Design': 2500}
service_to_task = {'Poster Design': 'Collaterals', 'Brochure Design': 'Collaterals', 'Catalogue Design': 'Collaterals', 'Leaflet Design': 'Collaterals', 'Presentation Design': 'Collaterals', 'Whitepaper Creation': 'Collaterals', 'Infographic Design': 'Collaterals', 'Office Wall Design': 'Office Design', 'Website Banner Design': 'Digital', 'Social Media Graphics': 'Digital', 'Translation (<5 pages)': 'Translations', 'Translation (5–10 pages)': 'Translations', 'Translation (10–20 pages)': 'Translations', 'Translation (20–50 pages)': 'Translations', 'Translation (>50 pages)': 'Translations', 'Website Event Registration Webpage': 'Digital', 'Event Registration Handling': 'Events', 'Webpage Link for Campaign': 'Digital', 'Video Production (<1 minute)': 'Video Production', 'Video Production (>1 minute)': 'Video Production', 'Cost of One Lead Generated': 'Lead Generation', 'Specific PR Need': 'Campaigns and PR', 'Market Research Report': 'Market Research', 'Brand Guidelines Creation': 'Collaterals', 'VR Experience (1-day)': 'VR', 'Event Support (on-site branding)': 'Events', 'Event Support (digital assets)': 'Events', 'Webinar Setup & Promotion': 'Events', 'Trade Show Booth Design': 'Events'}

departments = ["General", "Sales", "Customer Service", "HR", "Finance", "IT", "Operations", "Legal"]
countries = ["GENERAL", "BE", "NL", "UK", "IE", "FR", "IT", "ES", "PT", "DE", "DK", "SE", "FI", "NO", "PL", "TR", "ZA", "ME", "OUT-OF-EMEA"]
services = list(pricing.keys())
general_tasks = ["Campaigns and PR", "Collaterals", "Digital", "Events", "Lead Generation", "Market Research", "Office Design", "Photography", "Training", "Translations", "Video Production", "VR"]

if 'services_list' not in st.session_state:
    st.session_state.services_list = []
if 'entry_choice' not in st.session_state:
    st.session_state.entry_choice = 'Predefined Service'

st.subheader("Add an item")
st.session_state.entry_choice = st.radio("Item type", ["Predefined Service", "Custom Service"], horizontal=True, index=0 if st.session_state.entry_choice=='Predefined Service' else 1)

with st.form("add_item_form"):
    col1, col2 = st.columns(2)
    with col1:
        department = st.selectbox("Department", departments, key="dept")
        country = st.selectbox("Country", countries, key="country")
        if st.session_state.entry_choice == "Predefined Service":
            service = st.selectbox("Service", services, key="svc_pre")
        else:
            service = st.text_input("Service name", key="svc_custom", placeholder="e.g., Photography Day Rate")
            task_c = st.selectbox("General Task", general_tasks, key="task_custom")
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=1, key="qty")
        if st.session_state.entry_choice == "Predefined Service":
            pass
        else:
            unit_price_c = st.number_input("Unit Price (EUR)", min_value=0.0, value=0.0, step=10.0, key="price_custom")

    add_btn = st.form_submit_button("Add Item")
    if add_btn:
        if st.session_state.entry_choice == "Predefined Service":
            st.session_state.services_list.append({
                "Department": department,
                "Country": country,
                "Service": service,
                "Quantity": quantity,
                "General Task": service_to_task.get(service, "N/A"),
                "Unit Price (€)": pricing.get(service, 0)
            })
        else:
            name = service.strip()
            if name:
                if name in pricing and unit_price_c == 0.0:
                    final_price = pricing[name]
                    final_task = service_to_task.get(name, task_c)
                else:
                    if unit_price_c <= 0.0:
                        st.error("Please enter a Unit Price (EUR) for custom services.")
                        final_price = None
                    else:
                        final_price = unit_price_c
                    final_task = task_c
                if final_price is not None:
                    st.session_state.services_list.append({
                        "Department": department,
                        "Country": country,
                        "Service": name,
                        "Quantity": quantity,
                        "General Task": final_task,
                        "Unit Price (€)": final_price
                    })
            else:
                st.error("Please enter a service name.")

if st.session_state.services_list:
    st.write("### The list of services (TABLE)")
    df_preview = pd.DataFrame(st.session_state.services_list)
    st.table(df_preview[["Department", "Country", "General Task", "Service", "Quantity", "Unit Price (€)"]])

# Estimate guard & export
if st.button("Estimate"):
    if not st.session_state.services_list:
        st.warning("Please add at least one service to the list, then click Estimate.")
    else:
        df = pd.DataFrame(st.session_state.services_list)
        if "Unit Price (€)" not in df.columns:
            df["Unit Price (€)"] = df["Service"].map(pricing)
        df["Total (€)"] = df["Quantity"] * df["Unit Price (€)"]

        if "General Task" not in df.columns:
            df["General Task"] = df["Service"].map(service_to_task).fillna("Custom")
        else:
            df["General Task"] = df.apply(lambda r: r["General Task"] if pd.notnull(r["General Task"]) and r["General Task"] != "" else service_to_task.get(r["Service"], "Custom"), axis=1)

        total_savings = float(df["Total (€)"].sum())
        st.subheader(f"Total Estimated Savings: EUR {total_savings:,.2f}")
        st.markdown("""
        **This amount represents the money saved by leveraging internal marketing resources instead of external agencies.**  
        Remember: *Saved money is earned money*.
        """)

        task_totals = df.groupby("General Task", as_index=False)["Total (€)"].sum().sort_values("Total (€)", ascending=False)
        fig_pie = px.pie(task_totals, names="General Task", values="Total (€)", title="Savings by General Task (Pie Chart)")
        st.plotly_chart(fig_pie, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            cols = ["Department", "Country", "General Task", "Service", "Quantity", "Unit Price (€)", "Total (€)"]
            for c in cols:
                if c not in df.columns:
                    df[c] = ""
            df[cols].to_excel(writer, index=False, sheet_name="Estimate")
            task_totals.to_excel(writer, index=False, sheet_name="By Task")
        st.download_button(label="Download Excel", data=output.getvalue(), file_name="estimate.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
