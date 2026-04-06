import streamlit as st
import pandas as pd
import datetime

# ページ設定
st.set_page_config(page_title="収支管理ツール", layout="centered")
st.title("🎰 収支管理ツール")

# データの保存先ファイル
DATA_FILE = 'shushi_data.csv'

# データの読み込み
try:
    df = pd.read_csv(DATA_FILE)
    df['日付'] = df['日付'].astype(str)
except (FileNotFoundError, pd.errors.EmptyDataError):
    df = pd.DataFrame(columns=['日付', '機種名', '稼働時間', '台数', '投資枚数', '回収枚数', '収支'])

# --- 入力エリア ---
with st.form("input_form", clear_on_submit=True):
    st.subheader("📝 新規データ入力")
    date = st.date_input("日付", datetime.date.today())
    
    existing_models = sorted(df['機種名'].unique().tolist()) if not df.empty else []
    options = ["(新規入力)"] + existing_models
    selected_option = st.selectbox("機種名を選択", options)
    
    new_model_name = st.text_input("新しい機種名を入力（新規の場合のみ）", placeholder="機種名を入力してください")
    model_name = new_model_name if selected_option == "(新規入力)" else selected_option
    
    # 項目追加：稼働時間と投資枚数の間に「台数」を配置
    duration = st.number_input("1. 稼働時間 (h)", min_value=0.0, step=0.5, value=None, placeholder="例: 3.5")
    unit_count = st.number_input("2. 台数", min_value=1, step=1, value=None, placeholder="例: 1")
    investment = st.number_input("3. 投資枚数 (枚)", min_value=0, step=10, value=None, placeholder="例: 500")
    recovery = st.number_input("4. 回収枚数 (枚)", min_value=0, step=10, value=None, placeholder="例: 1200")
    
    submit = st.form_submit_button("データを記録する")
    
    if submit:
        if not model_name:
            st.error("機種名を入力または選択してください！")
        elif duration is None or unit_count is None or investment is None or recovery is None:
            st.error("全ての数値を入力してください！")
        else:
            income = int(recovery) - int(investment)
            new_row = pd.DataFrame([[
                date.strftime('%Y-%m-%d'), 
                model_name, 
                float(duration),
                int(unit_count),
                int(investment), 
                int(recovery), 
                int(income)
            ]], columns=df.columns)
            
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"【{model_name}】のデータを保存しました！")
            st.rerun()

# --- 集計・表示エリア ---
st.divider()

if not df.empty:
    # 数値列の変換（台数も含める）
    for col in ['稼働時間', '台数', '投資枚数', '回収枚数', '収支']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    tab1, tab2 = st.tabs(["📊 機種別通算", "📜 履歴一覧"])

    with tab1:
        st.subheader("機種ごとの通算成績")
        # 台数も合計（sum）で集計
        stats = df.groupby('機種名').agg({
            '台数': 'sum',
            '稼働時間': 'sum',
            '投資枚数': 'sum',
            '回収枚数': 'sum',
            '収支': 'sum'
        })
        st.dataframe(stats, use_container_width=True)

    with tab2:
        st.subheader("全履歴（新しい順）")
        st.dataframe(df.sort_values('日付', ascending=False), use_container_width=True, hide_index=True)
else:
    st.info("まだデータがありません。上のフォームから入力してください。")
