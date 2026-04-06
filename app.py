import streamlit as st
import pandas as pd
import datetime

# ページ設定
st.set_page_config(page_title="収支管理ツール", layout="centered")
st.title("🎰 収支管理ツール")

# データの読み込み（なければ新規作成）
if 'data' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv('shushi_data.csv')
    except FileNotFoundError:
        st.session_state.df = pd.DataFrame(columns=['日付', '機種名', '稼働時間', '投資枚数', '回収枚数', '収支'])

df = st.session_state.df

# --- 入力エリア ---
with st.form("input_form", clear_on_submit=True):
    st.subheader("新規データ入力")
    date = st.date_input("日付", datetime.date.today())
    
    # 2. 機種名の選択（過去の履歴から引用）
    existing_models = df['機種名'].unique().tolist()
    model_name = st.selectbox("機種を選択（または新規入力）", ["新規入力..."] + existing_models)
    
    if model_name == "新規入力...":
        model_name = st.text_input("新しい機種名を入力")
    
    # 1, 3, 4. 各項目の入力
    duration = st.number_input("1. 稼働時間 (h)", min_value=0.0, step=0.5)
    investment = st.number_input("3. 投資枚数 (枚)", min_value=0, step=50)
    recovery = st.number_input("4. 回収枚数 (枚)", min_value=0, step=50)
    
    submit = st.form_submit_button("記録する")
    
    if submit and model_name:
        income = recovery - investment
        new_row = pd.DataFrame([[date, model_name, duration, investment, recovery, income]], 
                               columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        st.session_state.df = df
        df.to_csv('shushi_data.csv', index=False)
        st.success(f"{model_name} のデータを保存しました！")

# --- 集計エリア ---
st.divider()
st.subheader("📊 機種別通算データ")
if not df.empty:
    # 機種ごとの合計を集計
    stats = df.groupby('機種名').agg({
        '稼働時間': 'sum',
        '投資枚数': 'sum',
        '回収枚数': 'sum',
        '収支': 'sum'
    })
    st.dataframe(stats)
    
    st.subheader("📝 履歴一覧")
    st.dataframe(df.sort_values('日付', ascending=False))
else:
    st.info("データがまだありません。")

