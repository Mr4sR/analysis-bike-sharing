import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import os

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
    sum_rent_df = df.groupby("weathersit")["cnt"].sum().sort_values(ascending=False).reset_index()
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

def create_sum_rent_by_hour(df):
    sum_rent_hour_df = df.groupby("hr")["cnt"].mean()
    return sum_rent_hour_df

def create_sum_rent_by_hour_pattern(df):
    df['day_type'] = df['workingday'].map({1: 'Weekday', 0: 'Weekend'})
    sum_rent_hour_pattern_df = df.groupby(['hr', 'day_type'])['cnt'].mean().unstack()
    return sum_rent_hour_pattern_df

def create_sum_rent_by_category(df):
    def categorize_time(hour):
        if 6 <= hour < 10:
            return 'Pagi (06:00-10:00)'
        elif 10 <= hour < 15:
            return 'Siang (10:00-15:00)'
        elif 15 <= hour < 19:
            return 'Sore (15:00-19:00)'
        elif 19 <= hour < 23:
            return 'Malam (19:00-23:00)'
        else:
            return 'Dini Hari (23:00-06:00)'

    df['time_category'] = df['hr'].apply(categorize_time)
    return df

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

def load_csv(file_name):
    try:
        return pd.read_csv(file_name)
    except FileNotFoundError:
        alternative_path = os.path.join("dashboard", file_name)
        if os.path.exists(alternative_path):
            return pd.read_csv(alternative_path)
        else:
            raise FileNotFoundError(f"File '{file_name}' tidak ditemukan di lokasi utama maupun di 'dashboard/'")

bike_df = load_csv("day.csv")
bike_hour_df = load_csv("hour.csv")

datetime_columns = ["dteday"]

bike_df.sort_values(by="dteday", inplace=True)
bike_df.reset_index(drop=True, inplace=True)

bike_hour_df.sort_values(by="dteday", inplace=True)
bike_hour_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    bike_df[column] = pd.to_datetime(bike_df[column])
    bike_hour_df[column] = pd.to_datetime(bike_hour_df[column])

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

hour_df = bike_hour_df[(bike_hour_df["dteday"] >= str(start_date)) & 
                (bike_hour_df["dteday"] <= str(end_date))]

daily_rent_df = create_daily_rent_df(main_df)
sum_rent_df = create_sum_rent_df(main_df)
sum_rent_month_df = create_sum_rent_by_month(main_df)
sum_rent_year_df = create_sum_rent_by_year(main_df)
sum_rent_weekday_df = create_sum_rent_by_weekday(main_df)
sum_rent_hour_df = create_sum_rent_by_hour(hour_df)
sum_rent_hour_pattern_df = create_sum_rent_by_hour_pattern(hour_df)
sum_rent_hour_category_df = create_sum_rent_by_category(hour_df)
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

st.subheader("📅 Rentals by Weekday")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x="weekday", y="cnt", data=sum_rent_weekday_df, palette="muted", ax=ax)
ax.set_xticklabels(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
ax.set_ylabel("Total Rentals")
ax.set_title("Total Rentals by Weekday")

st.pyplot(fig)

st.subheader("⌚ Rentals by Hour")

fig, ax = plt.subplots(figsize=(10, 6))

sns.lineplot(x=sum_rent_hour_df.index, y=sum_rent_hour_df.values, marker='o', linestyle='-', ax=ax)

ax.set_xlabel("Hour")
ax.set_ylabel("Average Number of Rentals")
ax.set_title("Bike Rental Trend by Hour")
ax.set_xticks(range(24))
ax.grid()

st.pyplot(fig)

st.subheader("🌦 Rentals by Weather Conditions")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x="weathersit", y="cnt", data=main_df)
ax.set_xticklabels(["Clear, Partly cloudly", "Misty clouds", "Light snow, Light rain"])
ax.set_xlabel("Weather Conditions")
ax.set_ylabel("Total Rentals")
ax.set_title("Total Rentals by Weather Conditions")

st.pyplot(fig)

st.subheader("🕓 Bike Rental per Hour Patterns Weekdays vs Weekends")
fig, ax = plt.subplots(figsize=(12, 6))
sum_rent_hour_pattern_df.plot(kind='line', marker='o', ax=plt.gca())
ax.set_xlabel("Hour")
ax.set_ylabel("Average Number of Rentals")
ax.set_title("Bike Rental Patterns: Weekdays vs Weekends")
ax.legend(title='Day Type')
ax.grid()

st.pyplot(fig)

st.subheader("🕓 Rentals by Categorical Time")

rental_counts = sum_rent_hour_category_df.groupby('time_category').size().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
rental_counts.plot(kind='bar', color=['#FFDDC1', '#FFABAB', '#FFC3A0', '#D5AAFF'])
ax.set_title('Jumlah Penyewaan Sepeda Berdasarkan Waktu')
ax.set_xlabel('Kategori Waktu')
ax.set_ylabel('Jumlah Penyewaan')
plt.xticks(rotation=45)
ax.grid(axis='y', linestyle='--', alpha=0.7)

st.pyplot(fig)

st.caption("📌 Copyright (c) Ahmad S 2025")


