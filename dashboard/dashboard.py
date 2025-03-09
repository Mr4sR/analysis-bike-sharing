import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

def create_daily_rent_df(df):
    daily_rent_df = df.resample(rule='D', on='dteday').agg({
        "season": "first",
        "yr": "first",
        "mnth": "first",
        "holiday": "first",
        "weekday": "first",
        "workingday": "first",
        "weathersit": "first",
        "temp": "mean",
        "atemp": "mean",
        "hum": "mean",
        "windspeed": "mean",
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    
    daily_rent_df = daily_rent_df.reset_index()
    
    return daily_rent_df

def create_sum_rent_df(df):
    sum_rent_df = df.groupby("season")["cnt"].sum().sort_values(ascending=False).reset_index()
    return sum_rent_df

def create_sum_rent_by_month(df):
    sum_rent_month_df = df.groupby("mnth")["cnt"].sum().sort_values(ascending=False).reset_index()
    return sum_rent_month_df

def create_sum_rent_by_year(df):
    sum_rent_year_df = df.groupby("yr")["cnt"].sum().sort_values(ascending=False).reset_index()
    return sum_rent_year_df

def create_sum_rent_by_weekday(df):
    sum_rent_weekday_df = df.groupby("weekday")["cnt"].sum().sort_values(ascending=False).reset_index()
    return sum_rent_weekday_df

import pandas as pd

def create_rfm_df(df):
    df["dteday"] = pd.to_datetime(df["dteday"])

    df["weekday"] = df["dteday"].dt.day_name()

    last_order_date = df["dteday"].max()
    recency_df = df.groupby("weekday")["dteday"].max().reset_index()
    recency_df["recency"] = (last_order_date - recency_df["dteday"]).dt.days
    recency_df = recency_df[["weekday", "recency"]]

    frequency_df = df.groupby("weekday").size().reset_index(name="frequency")

    rental_df = df.groupby("weekday")[["casual", "registered"]].sum().reset_index()
    rental_df.rename(columns={"casual": "total_casual", "registered": "total_registered"}, inplace=True)

    rfm_idf = recency_df.merge(frequency_df, on="weekday").merge(rental_df, on="weekday")

    return rfm_idf

bike_df = pd.read_csv("day.csv")

bike_df['dteday'] = pd.to_datetime(bike_df['dteday'])

datetime_columns = ["dteday"]

bike_df.sort_values(by="dteday", inplace=True)
bike_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    bike_df[column] = pd.to_datetime(bike_df[column])

min_date = bike_df["dteday"].min()
max_date = bike_df["dteday"].max()

with st.sidebar:
    st.image("https://cdn01.bcycle.com/libraries/images/librariesprovider68/default-album/clemsonbikeshare.png?sfvrsn=9e5e5cc5_4")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = bike_df[(bike_df["dteday"] >= str(start_date)) & 
                (bike_df["dteday"] <= str(end_date))]

daily_rent_df = create_daily_rent_df(main_df)
sum_rent_df = create_sum_rent_df(main_df)
sum_rent_month_df = create_sum_rent_by_month(main_df)
sum_rent_year_df = create_sum_rent_by_year(main_df)
sum_rent_weekday_df = create_sum_rent_by_weekday(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Dicoding Collection Dashboard :sparkles:')

st.subheader('🚲 Daily Bike Rentals')

col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = daily_rent_df["cnt"].sum()
    st.metric("Total Rentals", value=total_rentals)

with col2:
    total_registered = daily_rent_df["casual"].sum()
    st.metric("Total Casual Users", value=total_registered)

with col3:
    total_registered = daily_rent_df["registered"].sum()
    st.metric("Total Registered Users", value=total_registered)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rent_df["dteday"],
    daily_rent_df["cnt"],
    marker='o', 
    linewidth=2,
    color="#90CAF9",
    label="Total Rentals"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xlabel("Date", fontsize=18)
ax.set_ylabel("Total Rentals", fontsize=18)
ax.legend(fontsize=14)

st.pyplot(fig)

st.subheader("🌦 Rentals by Season")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x="season", y="cnt", data=sum_rent_df, palette="coolwarm", ax=ax)
ax.set_xticklabels(["Spring", "Summer", "Fall", "Winter"])
ax.set_ylabel("Total Rentals")
ax.set_title("Total Rentals by Season")

st.pyplot(fig)

st.subheader("📆 Monthly Rentals")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x="mnth", y="cnt", data=sum_rent_month_df, palette="Blues", ax=ax)
ax.set_xticklabels(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
)
ax.set_ylabel("Total Rentals")
ax.set_title("Total Rentals by Month")

st.pyplot(fig)

st.subheader("📊 Yearly Rentals")

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="yr", y="cnt", data=sum_rent_year_df, palette="viridis", ax=ax)
ax.set_xticklabels(["2011", "2012"])
ax.set_ylabel("Total Rentals")
ax.set_title("Total Rentals by Year")

st.pyplot(fig)

st.subheader("📅 Rentals by Weekday")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x="weekday", y="cnt", data=sum_rent_weekday_df, palette="muted", ax=ax)
ax.set_xticklabels(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
ax.set_ylabel("Total Rentals")
ax.set_title("Total Rentals by Weekday")

st.pyplot(fig)

st.subheader("🚲 Best Rental Days Based on RFM Parameters")

fig, ax = plt.subplots(1, 2, figsize=(14, 5))

sns.barplot(x="weekday", y="recency", data=rfm_df, palette="coolwarm", ax=ax[0])
ax[0].set_title("Recency (Hari Sejak Transaksi Terakhir)", fontsize=12)
ax[0].set_xlabel("Weekday")
ax[0].set_ylabel("Recency (Hari)")

sns.barplot(x="weekday", y="frequency", data=rfm_df, palette="viridis", ax=ax[1])
ax[1].set_title("Frequency (Jumlah Transaksi per Hari)", fontsize=12)
ax[1].set_xlabel("Weekday")
ax[1].set_ylabel("Frequency")

st.pyplot(fig)

df_melted = rfm_df.melt(id_vars="weekday", value_vars=["total_casual", "total_registered"], 
                                     var_name="customer_type", value_name="total_rentals")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x="weekday", y="total_rentals", hue="customer_type", data=df_melted, palette="Set2", ax=ax)
ax.set_title("Perbandingan Penyewaan: Casual vs Registered", fontsize=14)
ax.set_xlabel("Weekday")
ax.set_ylabel("Total Rentals")
ax.legend(title="Customer Type")

st.pyplot(fig)

st.caption("📌 Copyright (c) Ahmad S 2025")


