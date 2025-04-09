"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from src import config


# cols = st.columns(2)
##############################################################################
# with cols[0]:
"NIV Issuances by Post and Visa Class"

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

##############################################################################
# with cols[1]:
"NIV Issuances by Nationality and Visa Class"

df = pd.read_csv(r"data\dataframe\all_data_NIV Issuances by Nationality and Visa Class.csv")
df["Visa Class root"] = df["Visa Class"].str[0]
df_visa_mapping = df[["Visa Class root", "Visa Class"]].drop_duplicates().reset_index(drop=True)
df_visa_mapping = df_visa_mapping.groupby(["Visa Class root"], as_index=False)["Visa Class"].apply(list)
visa_mapping = df_visa_mapping.set_index("Visa Class root").to_dict()["Visa Class"]

cols = st.columns(2)
with cols[0]:
    nationalities = list(df["Nationality"].unique())
    country_default = nationalities.index("Brazil")
    nationality = st.selectbox("Country", nationalities, index=country_default)
    # nationality = "Brazil"

filter_nationality = df["Nationality"] == nationality
df = df[filter_nationality]

with cols[1]:
    visa_types = list(df["Visa Class"].unique())
    visa_types_root = list(df["Visa Class root"].unique())
    top_visa_types_root = df["Visa Class root"].value_counts()[:10]
    top_visa_types_root_values = list(df["Visa Class root"].value_counts()[:10].index) 
    visa_root = st.multiselect("Select Visa types root:", visa_types_root, default=top_visa_types_root_values, label_visibility="collapsed")

filter_visa_root = df["Visa Class root"].isin(top_visa_types_root_values)
df = df[filter_visa_root]

visa_types = []
# [visa_types.extend(visa_mapping[v_root]) for v_root in visa_root]
for v_root in visa_root:
    visa_types.extend(visa_mapping[v_root])
visa = st.multiselect("Select Visa types:", visa_types, default=visa_types, label_visibility="collapsed")

filter_visa = df["Visa Class"].isin(visa)
df_filter = df[filter_visa]

df_pivot = df_filter.pivot_table(index='Datetime', columns='Visa Class', values='Issuances', aggfunc='sum')
st.line_chart(df_pivot)


##############################################################################
f"ref: {config.TARGET_URL}"
