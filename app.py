import streamlit as st
import google.generativeai as genai
import pandas as pd

st.title("生技文獻 AI 導讀助手 🧬 (進階批次版)")
st.write("這是一個幫助理解生物科技學術文獻的 AI 工具，展示跨領域資訊應用與批次資料處理能力。")

# 使用側邊欄讓介面更專業
with st.sidebar:
    st.header("⚙️ 系統設定")
    api_key = st.text_input("請輸入您的 Gemini API Key：", type="password")
    st.markdown("---")
    st.write("💡 **開發亮點**：")
    st.write("結合迴圈處理與 Pandas 數據清理技術，將大量非結構化文獻轉化為結構化報表，大幅提升文獻回顧效率。")

# 建立兩個分頁，保留原本的單篇功能，加入新的批次功能
tab1, tab2 = st.tabs(["📄 單篇導讀", "📚 批次處理與匯出 (新功能!)"])

# --- 第一個分頁：單篇導讀 ---
with tab1:
    text_input = st.text_area("請貼上單篇生技英文文獻摘要：", height=200)
    if st.button("開始單篇導讀"):
        if not api_key:
            st.error("請先在左側輸入 API Key！")
        elif not text_input:
            st.warning("請貼上文獻摘要！")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = f"""
                你現在是一位專業的生物科技產業分析師與學術導讀員。請將以下英文學術摘要轉換為高中生能理解的繁體中文。
                請固定以三個部分輸出：1. 研究目的、2. 核心技術、3. 產業應用價值。

                文獻摘要：
                {text_input}
                """
                with st.spinner('AI 正在分析文獻中...'):
                    response = model.generate_content(prompt)
                st.success("導讀完成！")
                st.write(response.text)
            except Exception as e:
                st.error(f"發生錯誤：{e}")

# --- 第二個分頁：批次處理與表格匯出 ---
with tab2:
    st.info("上傳純文字檔 (.txt)。若有多篇摘要，請在每篇摘要之間使用三個減號 `---` 隔開。")
    uploaded_file = st.file_uploader("選擇您的 TXT 檔案", type=['txt'])
    
    if st.button("啟動批次自動化分析"):
        if not api_key:
            st.error("請先在左側輸入 API Key！")
        elif uploaded_file is None:
            st.warning("請先上傳檔案！")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 讀取檔案並切割摘要
                content = uploaded_file.getvalue().decode("utf-8")
                # 以 --- 為界線切割文章，並去除空白
                abstracts = [abs.strip() for abs in content.split("---") if abs.strip()]
                
                st.write(f"✅ 成功讀取 **{len(abstracts)}** 篇文獻摘要，準備進入產線處理...")
                
                results = []
                progress_bar = st.progress(0) # 酷炫的進度條
                
                for i, abstract in enumerate(abstracts):
                    prompt = f"""
                    請簡要分析以下生物科技學術摘要。
                    請固定輸出這三個項目，不要多餘的問候語：
                    - 研究目的：(一句話)
                    - 核心技術：(一句話)
                    - 應用價值：(一句話)

                    摘要：
                    {abstract}
                    """
                    
                    response = model.generate_content(prompt)
                    # 將結果存入字典，準備轉為表格
                    results.append({
                        "原文摘要 (前100字)": abstract[:100] + "...",
                        "AI 導讀報告": response.text
                    })
                    
                    # 更新進度條
                    progress_bar.progress((i + 1) / len(abstracts))
                
                st.success("批次處理完畢！")
                
                # 使用 Pandas 將結果轉換為美觀的表格
                df = pd.DataFrame(results)
                st.dataframe(df)
                
                # 準備 CSV 下載檔案 (加上 utf-8-sig 讓 Excel 開啟不會亂碼)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                
                st.download_button(
                    label="📥 下載 Excel (CSV) 報表",
                    data=csv,
                    file_name="生技文獻導讀批次報表.csv",
                    mime="text/csv",
                )
                
            except Exception as e:
                st.error(f"發生錯誤：{e}")
