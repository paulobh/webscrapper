"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r"data\dataframe\all_data.csv")

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