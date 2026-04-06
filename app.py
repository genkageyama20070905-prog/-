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
    # 日付列を文字列として確実に扱う
    df['日付'] = df['日付'].astype(str)
except (FileNotFoundError, pd.errors.EmptyDataError):
    # ファイルがない、または空の場合は新規作成
    df = pd.DataFrame(columns=['日付', '機種名', '稼働時間', '投資枚数', '回収枚数', '収支'])

# --- 入力エリア ---
with st.form("input_form", clear_on_submit=True):
    st.subheader("📝 新規データ入力")
    date = st.date_input("日付", datetime.date.today())
    
    # 過去の機種名リストを取得（重複排除してソート）
    existing_models = sorted(df['機種名'].unique().tolist()) if not df.empty else []
    
    # 機種選択：初期状態は「新規入力」
    options = ["(新規入力)"] + existing_models
    selected_option = st.selectbox("機種名を選択", options)
    
    # 新規入力用のテキストボックス（placeholderで入力しやすく）
    new_model_name = st.text_input("新しい機種名を入力（新規の場合のみ）", placeholder="機種名を入力してください")
    
    # 最終的な機種名の決定（選択されたものか、新規入力されたものか）
    model_name = new_model_name if selected_option == "(新規入力)" else selected_option
    
    # 数値入力：value=None で初期値を空にし、iPhoneでの入力をスムーズに
    duration = st.number_input("1. 稼働時間 (h)", min_value=0.0, step=0.5, value=None, placeholder="例: 3.5")
    investment = st.number_input("3. 投資枚数 (枚)", min_value=0, step=10, value=None, placeholder="例: 500")
    recovery = st.number_input("4. 回収枚数 (枚)", min_value=0, step=10, value=None, placeholder="例: 1200")
    
    submit = st.form_submit_button("データを記録する")
    
    if submit:
        # 未入力チェック
        if not model_name:
            st.error("機種名を入力または選択してください！")
        elif duration is None or investment is None or recovery is None:
            st.error("全ての数値を入力してください！")
        else:
            # 収支計算
            income = int(recovery) - int(investment)
            # 新しい行を作成
            new_row = pd.DataFrame([[
                date.strftime('%Y-%m-%d'), 
                model_name, 
                float(duration), 
                int(investment), 
                int(recovery), 
                int(income)
            ]], columns=df.columns)
            
            # データを追加して保存
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"【{model_name}】のデータを保存しました！")
            st.rerun() # 画面を更新してリストに反映

# --- 集計・表示エリア ---
st.divider()

if not df.empty:
    # 数値列を確実に数値型に変換
    for col in ['稼働時間', '投資枚数', '回収枚数', '収支']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # タブで切り替え（見やすさ向上）
    tab1, tab2 = st.tabs(["📊 機種別通算", "📜 履歴一覧"])

    with tab1:
        st.subheader("機種ごとの通算成績")
        stats = df.groupby('機種名').agg({
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
