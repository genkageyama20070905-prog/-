import streamlit as st
import pandas as pd
import datetime

# ページ設定
st.set_page_config(page_title="収支管理ツール", layout="centered")
st.title("収支管理")

DATA_FILE = 'shushi_data.csv'

# --- データの読み込みと項目修正 ---
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        # 項目の名前を「台数」に統一（古いデータがある場合への対応）
        if '台_数' in df.columns:
            df = df.rename(columns={'台_数': '台数'})
        if '台数' not in df.columns:
            # 3番目の位置に「台数」列を初期値1で追加
            df.insert(3, '台数', 1)
        df['日付'] = df['日付'].astype(str)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # 新規作成時の正しい列構成
        return pd.DataFrame(columns=['日付', '機種名', '稼働時間', '台数', '投資枚数', '回収枚数', '収支'])

df = load_data()

# --- 入力エリア ---
with st.expander("➕ 新規データ入力", expanded=True):
    with st.form("input_form", clear_on_submit=True):
        date = st.date_input("日付", datetime.date.today())
        
        # 機種名の選択
        existing_models = sorted(df['機種名'].unique().tolist()) if not df.empty else []
        selected_option = st.selectbox("機種名を選択", ["(新規入力)"] + existing_models)
        new_model_name = st.text_input("新しい機種名を入力", placeholder="機種名を入力")
        model_name = new_model_name if selected_option == "(新規入力)" else selected_option
        
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("稼働時間(h)", min_value=0.0, step=0.5, value=None, placeholder="3.5")
            unit_count = st.number_input("台数", min_value=1, step=1, value=None, placeholder="1")
        with col2:
            investment = st.number_input("投資(枚)", min_value=0, step=10, value=None, placeholder="500")
            recovery = st.number_input("回収(枚)", min_value=0, step=10, value=None, placeholder="1200")
        
        submit = st.form_submit_button("データを記録する")
        
        if submit:
            if not model_name or duration is None or unit_count is None or investment is None or recovery is None:
                st.error("入力漏れがあります")
            else:
                income = int(recovery) - int(investment)
                # 列の順番を確実に合わせる
                new_row = pd.DataFrame([[
                    date.strftime('%Y-%m-%d'), 
                    model_name, 
                    float(duration), 
                    int(unit_count), 
                    int(investment), 
                    int(recovery), 
                    int(income)
                ]], columns=['日付', '機種名', '稼働時間', '台数', '投資枚数', '回収枚数', '収支'])
                
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success(f"保存完了！")
                st.rerun()

# --- 表示・削除エリア ---
st.divider()

if not df.empty:
    # 数値列を確実に数値化（集計エラー防止）
    numeric_cols = ['稼働時間', '台数', '投資枚数', '回収枚数', '収支']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    tab1, tab2 = st.tabs(["📊 通算成績", "🗑️ 履歴・削除"])

    with tab1:
        st.subheader("機種ごとの収支")
        # グループ化して合計を表示
        stats = df.groupby('機種名')[numeric_cols].sum()
        st.dataframe(stats, use_container_width=True)

    with tab2:
        st.subheader("履歴の削除")
        # 削除用のリスト作成
        df_rev = df.copy().iloc[::-1] # 新しい順
        delete_options = {f"{i}: {row['日付']} | {row['機種名']} ({int(row['収支'])}枚)": i for i, row in df_rev.iterrows()}
        
        target_label = st.selectbox("削除するデータを選択", ["選択してください"] + list(delete_options.keys()))
        
        if st.button("選択したデータを削除する", type="primary"):
            if target_label != "選択してください":
                target_idx = delete_options[target_label]
                df = df.drop(target_idx)
                df.to_csv(DATA_FILE, index=False)
                st.warning("削除しました")
                st.rerun()
            else:
                st.error("削除するデータを選んでください")
        
        st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
else:
    st.info("データがありません")
