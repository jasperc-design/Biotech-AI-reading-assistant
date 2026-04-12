import streamlit as st
import google.generativeai as genai
import pandas as pd

# ==========================================
# UI 基礎配置與全域設定
# ==========================================
st.set_page_config(page_title="生技資訊 AI 工具箱", page_icon="🧬", layout="wide")

# --- 側邊欄導覽與設定 ---
with st.sidebar:
    st.title("🧬 生技資訊 AI 工具箱")
    st.write("APCS 組專題實作：結合資訊技術與生物產業科學")
    st.markdown("---")
    
    # 統一在這裡輸入密碼，全站通用
    api_key = st.text_input("🔑 請輸入 Gemini API Key：", type="password")
    st.markdown("---")
    
    # 建立系統導覽選單
    st.subheader("🖥️ 功能導覽模組")
    app_mode = st.radio(
        "請選擇您要使用的分析工具：", 
        ["📄 單篇文獻 AI 導讀", 
         "📚 批次文獻處理與報表", 
         "🔬 蛋白質預測 (中心法則)"]
    )

# ==========================================
# 共用資源區塊：RNA 密碼子對應胺基酸的字典
# ==========================================
CODON_TABLE = {
    'AUA':'I', 'AUC':'I', 'AUU':'I', 'AUG':'M',
    'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACU':'T',
    'AAC':'N', 'AAU':'N', 'AAA':'K', 'AAG':'K',
    'AGC':'S', 'AGU':'S', 'AGA':'R', 'AGG':'R',
    'CUA':'L', 'CUC':'L', 'CUG':'L', 'CUU':'L',
    'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCU':'P',
    'CAC':'H', 'CAU':'H', 'CAA':'Q', 'CAG':'Q',
    'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGU':'R',
    'GUA':'V', 'GUC':'V', 'GUG':'V', 'GUU':'V',
    'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCU':'A',
    'GAC':'D', 'GAU':'D', 'GAA':'E', 'GAG':'E',
    'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGU':'G',
    'UCA':'S', 'UCC':'S', 'UCG':'S', 'UCU':'S',
    'UUC':'F', 'UUU':'F', 'UUA':'L', 'UUG':'L',
    'UAC':'Y', 'UAU':'Y', 'UAA':'_', 'UAG':'_', 'UGA':'_', 'UGG':'W',
}

def translate_rna_to_protein(rna_seq):
    protein = ""
    for i in range(0, len(rna_seq), 3):
        codon = rna_seq[i:i+3]
        if len(codon) == 3:
            amino_acid = CODON_TABLE.get(codon, '?')
            if amino_acid == '_': # 終止密碼子
                break
            protein += amino_acid
    return protein

# ==========================================
# 模組一：單篇文獻 AI 導讀
# ==========================================
if app_mode == "📄 單篇文獻 AI 導讀":
    st.header("📄 生技文獻 AI 導讀助手")
    st.write("快速將生技領域的英文學術摘要，轉換為結構化的中文導讀。")
    
    text_input = st.text_area("請貼上單篇生技英文文獻摘要：", height=200)
    
    if st.button("開始單篇導讀"):
        if not api_key:
            st.error("請先在左側欄位輸入 API Key！")
        elif not text_input:
            st.warning("請貼上文獻摘要！")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = f"""
                你現在是一位專業的生物科技產業分析師與學術導讀員。請將以下英文學術摘要轉換為高中生能理解的繁體中文。
                請固定以三個部分輸出：1. 研究目的、2. 核心技術、3. 產業應用價值。
                文獻摘要：\n{text_input}
                """
                with st.spinner('AI 正在分析文獻中...'):
                    response = model.generate_content(prompt)
                st.success("導讀完成！")
                st.write(response.text)
            except Exception as e:
                st.error(f"發生錯誤：{e}")

# ==========================================
# 模組二：批次文獻處理與報表
# ==========================================
elif app_mode == "📚 批次文獻處理與報表":
    st.header("📚 批次文獻處理與 Excel 匯出")
    st.write("結合迴圈處理與 Pandas 數據清理技術，將大量非結構化文獻轉化為結構化報表。")
    st.info("上傳純文字檔 (.txt)。若有多篇摘要，請在每篇摘要之間使用三個減號 `---` 隔開。")
    
    uploaded_file = st.file_uploader("選擇您的 TXT 檔案", type=['txt'])
    
    if st.button("啟動批次自動化分析"):
        if not api_key:
            st.error("請先在左側欄位輸入 API Key！")
        elif uploaded_file is None:
            st.warning("請先上傳檔案！")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                content = uploaded_file.getvalue().decode("utf-8")
                abstracts = [abs.strip() for abs in content.split("---") if abs.strip()]
                
                st.write(f"✅ 成功讀取 **{len(abstracts)}** 篇文獻摘要，準備進入產線處理...")
                results = []
                progress_bar = st.progress(0)
                
                for i, abstract in enumerate(abstracts):
                    prompt = f"""
                    請簡要分析以下生物科技學術摘要。請固定輸出這三個項目：
                    - 研究目的：(一句話)
                    - 核心技術：(一句話)
                    - 應用價值：(一句話)
                    摘要：\n{abstract}
                    """
                    response = model.generate_content(prompt)
                    results.append({
                        "原文摘要 (前100字)": abstract[:100] + "...",
                        "AI 導讀報告": response.text
                    })
                    progress_bar.progress((i + 1) / len(abstracts))
                
                st.success("批次處理完畢！")
                
                # --- UI 優化：改用「折疊面板」漂亮呈現，不再使用難閱讀的 DataFrame ---
                st.subheader("📊 導讀結果預覽")
                for idx, row in enumerate(results):
                    # 預設展開第一筆，其他的折疊起來
                    with st.expander(f"📄 文獻 {idx+1} 導讀結果", expanded=(idx==0)):
                        st.markdown(f"**原文摘要 (前100字):**\n> {row['原文摘要 (前100字)']}")
                        st.markdown(f"**AI 分析:**\n{row['AI 導讀報告']}")
                
                # --- 匯出優化：產生真正的 Excel (.xlsx) 檔案 ---
                df = pd.DataFrame(results)
                
                from io import BytesIO
                output = BytesIO()
                # 引擎指定使用 openpyxl 寫入 Excel 格式
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='AI導讀報告')
                
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 下載完整 Excel 報表 (.xlsx)",
                    data=excel_data,
                    file_name="生技文獻導讀批次報表.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
# ==========================================
# 模組三：蛋白質預測 (中心法則)
# ==========================================
elif app_mode == "🔬 蛋白質預測 (中心法則)：":
    st.header("🔬 中心法則模擬與 AI 蛋白質預測")
    st.write("整合基礎生物資訊演算法與 LLM，展示從 DNA 序列解析到巨觀特性預測的自動化流程。")
    
    dna_input = st.text_area("請輸入 DNA 序列 (僅限 A, T, C, G)：", "ATGCGTACGGCCATTGACGAGTCCCTGAGGAAAAAAATGTAA")
    
    if st.button("執行演算法與 AI 預測"):
        if not api_key:
            st.error("請先在左側欄位輸入 API Key！")
        else:
            # 演算法執行
            clean_dna = dna_input.upper().replace(" ", "").replace("\n", "")
            rna_seq = clean_dna.replace("T", "U") 
            protein_seq = translate_rna_to_protein(rna_seq)

            col1, col2, col3 = st.columns(3)
            col1.metric("輸入 DNA 長度", f"{len(clean_dna)} bp")
            col2.metric("轉錄 mRNA", "成功")
            col3.metric("轉譯胺基酸", f"{len(protein_seq)} aa")

            st.code(f"mRNA 序列: {rna_seq}\n胺基酸序列: {protein_seq}", language="text")

            if len(protein_seq) > 0:
                st.markdown("---")
                st.subheader("🤖 AI 蛋白質特性預測報告")
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = f"""
                    你現在是一位頂尖的結構生物學家與生物資訊專家。
                    我有一段剛剛透過中心法則演算法轉譯出來的胺基酸序列：{protein_seq}

                    請根據這段序列，提供簡要的學術分析：
                    1. 胺基酸組成特徵 (例如：疏水/親水比例、帶電狀況)。
                    2. 二級結構預測 (傾向形成 Alpha-helix 還是 Beta-sheet？)。
                    3. 潛在功能推測 (如果這是一個真實蛋白質片段，可能具備什麼類型的功能？)。
                    
                    請用高中生能理解的繁體中文回答，語氣專業但易懂。
                    """
                    with st.spinner('正在將序列傳送至 AI 結構資料庫分析中...'):
                        response = model.generate_content(prompt)
                    
                    st.success("分析完成！")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"AI 連線發生錯誤：{e}")
            else:
                st.warning("轉譯出的胺基酸序列為空，請檢查輸入的 DNA。")
