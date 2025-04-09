import streamlit as st
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_by_city(city):
    safe_city = quote_plus(city)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={safe_city}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def get_weather_by_coords(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def get_forecast(city):
    safe_city = quote_plus(city)
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={safe_city}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()
    forecast_data = {}

    if res.get("cod") == "200":
        for item in res["list"]:
            date = item["dt_txt"].split(" ")[0]
            time = item["dt_txt"].split(" ")[1]
            if time == "12:00:00":  # get daily data at noon
                forecast_data[date] = {
                    "temp": item["main"]["temp"],
                    "desc": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"]
                }
    return forecast_data

def get_location_by_ip():
    try:
        ip_info = requests.get("http://ip-api.com/json").json()
        return ip_info.get("lat"), ip_info.get("lon"), ip_info.get("city")
    except:
        return None, None, None

# STREAMLIT UI
st.set_page_config(page_title="Weather App", page_icon="⛅", layout="wide")
st.title("🌤 Weather App")

st.markdown("**Created by Anoushka Anand**")

with st.expander("ℹ️ About PM Accelerator"):
    st.markdown("""
    **Product Manager Accelerator (PMA)** is an elite training program designed to help you launch and accelerate your product management career.

    🚀 We provide hands-on experience building real AI products, mentorship from experienced PMs, and opportunities to showcase your work.

    🔗 [Visit our LinkedIn page](https://www.linkedin.com/school/pmaccelerator/)
    """)

weather = None 
forecast = {}

# Location input
col1, col2 = st.columns([3, 1])
with col1:
    location = st.text_input("Enter a location (city or zip):")
with col2:
    use_current = st.button("📍 Use My Current Location")

# Determine location source
lat = lon = city = None

if use_current:
    lat, lon, city = get_location_by_ip()
    if city:
        st.success(f"Detected location: {city}")
        weather = get_weather_by_coords(lat, lon)
        forecast = get_forecast(city)
    else:
        st.error("Unable to detect location.")
        weather = None
        forecast = {}
elif location:
    weather = get_weather_by_city(location)
    if weather.get("cod") == 200:
        city = weather["name"]
        forecast = get_forecast(city)
    else:
        st.warning(f"⚠️ {weather.get('message', 'Location not found.')}")
        weather = None
        forecast = {}

# Show weather
if weather:
    st.subheader(f"Current Weather in {city}")
    col1, col2 = st.columns([1, 2])

    with col1:
        icon = weather['weather'][0]['icon']
        st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png")

    with col2:
        st.metric("🌡 Temperature", f"{weather['main']['temp']}°C")
        st.metric("💨 Wind Speed", f"{weather['wind']['speed']} m/s")
        st.metric("🌥 Condition", weather['weather'][0]['description'].title())

# Show 5-day forecast
if forecast:
    st.subheader("📅 5-Day Forecast")
    cols = st.columns(len(forecast))
    for i, (day, data) in enumerate(forecast.items()):
        with cols[i]:
            st.markdown(f"**{day}**")
            st.image(f"http://openweathermap.org/img/wn/{data['icon']}@2x.png")
            st.metric("Temp", f"{data['temp']}°C")
            st.caption(data["desc"].title())
