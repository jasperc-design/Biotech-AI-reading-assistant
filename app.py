import streamlit as st
import google.generativeai as genai

st.title("生技文獻 AI 導讀助手 🧬")
st.write("這是一個幫助理解生物科技學術文獻的 AI 工具。")

# 讓使用者輸入 API Key (為了安全，不要把密碼寫死在公開的 GitHub 上)
api_key = st.text_input("請輸入您的 Gemini API Key：", type="password")

text_input = st.text_area("請貼上生技英文文獻摘要：", height=200)

if st.button("開始導讀"):
    if not api_key:
        st.warning("請先輸入 API Key！")
    elif not text_input:
        st.warning("請貼上文獻摘要！")
    else:
        try:
            # 設定 API Key 並呼叫模型
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 定義 AI 的靈魂指令 (Prompt)
            prompt = f"""
            你現在是一位專業的生物科技產業分析師與學術導讀員。請將以下英文學術摘要轉換為高中生能理解的繁體中文。
            請固定以三個部分輸出：
            1. 研究目的（一句話總結）
            2. 核心技術（列出使用的生技技術）
            3. 產業應用價值（這項技術能幫人類解決什麼真實問題）

            文獻摘要：
            {text_input}
            """
            
            with st.spinner('AI 正在分析文獻中...'):
                response = model.generate_content(prompt)
                
            st.success("導讀完成！")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"發生錯誤，請檢查 API Key 是否正確。錯誤訊息：{e}")
