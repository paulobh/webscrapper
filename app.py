"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt

df = pd.read_csv(r"data\dataframe\all_data_NIV Issuances by Post and Visa Class.csv")

with open("data\dataframe\post_country.json") as f:
    mapping_post_country = json.load(f)
df["Country"] = df["Post"].map(mapping_post_country)

visa_types = list(df["Visa Class"].unique())
visa_default = visa_types.index("L1")
visa = st.selectbox("Visa type:", visa_types, index=visa_default)

countries = list(df["Country"].unique())
country_default = countries.index("Brazil")
country = st.selectbox("Country", countries, index=country_default)

filter_visa = df["Visa Class"] == visa
filter_country = df["Country"] == country
df_filter = df[filter_visa & filter_country]

df_pivot = df_filter.pivot_table(index='Datetime', columns='Post', values='Issuances', aggfunc='sum')
st.line_chart(df_pivot)