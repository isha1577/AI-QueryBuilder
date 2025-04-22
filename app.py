import streamlit as st
import plotly.express as px
import json
import pandas as pd
import streamlit_authenticator as stauth

# 1. Define user credentials
names = ['Alice', 'Bob']
usernames = ['alice', 'bob']
passwords = ['123', '456']  # In production, use environment variables or hashed passwords directly

# 2. Hash the passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# 3. Create the authenticator object
authenticator = stauth.Authenticate(
    credentials={
        "usernames": {
            usernames[0]: {
                "name": names[0],
                "password": hashed_passwords[0],
            },
            usernames[1]: {
                "name": names[1],
                "password": hashed_passwords[1],
            },
        }
    },
    cookie_name='some_cookie_name',
    key='some_signature_key',
    cookie_expiry_days=1
)


# 4. Login
name, authentication_status, username = authenticator.login('Login', 'main')

# 5. Display login status
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Welcome {name}!")

    # Title
    st.title("🗺️ Region-Based Sales Distribution (India Map)")

    # Sample sales data
    df = pd.DataFrame({
        'state': [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
            'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
            'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
            'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
            'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi', 'Jammu and Kashmir',
            'Ladakh'
        ],
        'sales': [
            82000, 0, 45000, 72000, 38000, 99000, 58000, 100, 9100,
            65000, 34000, 31000, 2900, 36000, 8700, 80000, 92000, 22000,
            90, 31000, 600, 0, 0, 0, 0, 0, 0, 0, 23, 100, 0
        ]
    })

    # Load India GeoJSON
    try:
        with open("india.geojson", "r") as f:
            india_geojson = json.load(f)
    except Exception as e:
        st.error(f"Error loading GeoJSON: {e}")
        st.stop()

    # Normalize state names
    state_id_map = {
        feature["properties"]["st_nm"].strip().lower(): feature["properties"]["st_nm"]
        for feature in india_geojson["features"]
    }

    df["state_lower"] = df["state"].str.strip().str.lower()
    df["state_corrected"] = df["state_lower"].map(state_id_map)

    df_valid = df.dropna(subset=["state_corrected"])

    # Plot Choropleth Mapbox
    fig = px.choropleth_mapbox(
        df_valid,
        geojson=india_geojson,
        featureidkey="properties.st_nm",
        locations="state_corrected",
        color="sales",
        color_continuous_scale="Inferno",
        mapbox_style="carto-darkmatter",
        zoom=2.5,
        center={"lat": 22.9734, "lon": 78.6569},
        opacity=0.8,
        title="📊 Sales Distribution by State"
    )

    fig.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_valid[["state", "sales"]])

elif authentication_status is False:
    st.error("❌ Username/password is incorrect.")
elif authentication_status is None:
    st.warning("🔐 Please enter your username and password.")
