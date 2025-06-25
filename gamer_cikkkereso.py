import streamlit as st
import requests
import csv
import io
from datetime import datetime

USER_API = "https://gamer.hu/wp-json/wp/v2/users?per_page=100"
POST_API_BASE = "https://gamer.hu/wp-json/wp/v2/posts"

def get_authors():
    response = requests.get(USER_API)
    authors = response.json()
    return {f"{a['name']} ({a['slug']})": a['id'] for a in authors}

def get_month_list():
    now = datetime.now()
    months = []
    for i in range(12):
        year = now.year
        month = now.month - i
        if month <= 0:
            month += 12
            year -= 1
        months.append(f"{year}-{month:02}")
    return months

def get_articles(author_id, month):
    results = []
    for page in range(1, 150):
        url = f"{POST_API_BASE}?author={author_id}&page={page}&per_page=10&_embed"
        resp = requests.get(url)
        if resp.status_code == 400 or not resp.json():
            break
        posts = resp.json()
        for post in posts:
            date = post["date"][:7]
            if date == month:
                results.append({
                    "title": post["title"]["rendered"].strip(),
                    "link": post["link"]
                })
    return results

def create_csv(data):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Cím", "URL"])
    for item in data:
        writer.writerow([item["title"], item["link"]])
    return buffer.getvalue().encode("utf-8")

def create_txt(data):
    buffer = io.StringIO()
    for item in data:
        buffer.write(f"{item['title']}\n{item['link']}\n\n")
    return buffer.getvalue().encode("utf-8")

st.set_page_config(page_title="Gamer.hu lekérő", layout="centered")
st.markdown("""
    <style>
        body { background-color: #f5f7fa; }
        .css-18e3th9 { background-color: white; border-radius: 12px; padding: 2rem; box-shadow: 0 0 20px rgba(0,0,0,0.05); }
        h1 { text-align: center; color: #2c3e50; }
    </style>
""", unsafe_allow_html=True)

st.title("📰 Gamer.hu Cikkkereső")

with st.form("kereso_form"):
    author_map = get_authors()
    author_name = st.selectbox("Szerző kiválasztása", list(author_map.keys()))
    month = st.selectbox("Hónap kiválasztása", get_month_list())
    submitted = st.form_submit_button("Cikkek lekérése")

if submitted:
    with st.spinner("Cikkek lekérése folyamatban..."):
        articles = get_articles(author_map[author_name], month)

    st.success(f"{len(articles)} cikk található {month} hónapból.")

    if articles:
        csv_data = create_csv(articles)
        txt_data = create_txt(articles)

        st.download_button(
            label="📂 Letöltés CSV formátumban",
            data=csv_data,
            file_name=f"{author_name.split()[0]}_{month}_cikkek.csv",
            mime="text/csv"
        )

        st.download_button(
            label="🔖 Letöltés TXT formátumban",
            data=txt_data,
            file_name=f"{author_name.split()[0]}_{month}_cikkek.txt",
            mime="text/plain"
        )
