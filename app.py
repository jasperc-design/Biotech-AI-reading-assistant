import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Bio-IT 蛋白質預測系統", page_icon="🧬")

st.title("中心法則模擬與 AI 蛋白質預測系統 🧬")
st.write("這是一個整合基礎生物資訊演算法與 LLM 的跨領域工具，展示從序列解析到宏觀特性預測的自動化流程。")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 系統設定")
    api_key = st.text_input("請輸入您的 Gemini API Key：", type="password")
    st.markdown("---")
    st.write("💡 **核心技術亮點**：")
    st.write("1. **演算法實作**：以 Python 實作 RNA 密碼子字典，精確模擬轉譯過程。")
    st.write("2. **AI 輔助分析**：串接 Gemini 2.5 分析胺基酸序列的潛在生化特性。")

# --- 生物資訊演算法區塊 ---
# 定義 RNA 密碼子對應胺基酸的字典 (Codon Table)
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
    # 每 3 個鹼基為一個密碼子進行讀取
    for i in range(0, len(rna_seq), 3):
        codon = rna_seq[i:i+3]
        if len(codon) == 3:
            amino_acid = CODON_TABLE.get(codon, '?')
            if amino_acid == '_': # 遇到終止密碼子
                break
            protein += amino_acid
    return protein

# --- 主介面 ---
st.subheader("第一階段：序列輸入與轉譯演算")
dna_input = st.text_area("請輸入 DNA 序列 (僅限 A, T, C, G)：", "ATGCGTACGGCCATTTAA")

if st.button("執行演算法與 AI 預測"):
    if not api_key:
        st.error("請先在左側輸入 API Key！")
    else:
        # 資料清理與轉錄演算法
        clean_dna = dna_input.upper().replace(" ", "").replace("\n", "")
        # 模擬轉錄：DNA coding strand -> mRNA (將 T 換成 U)
        rna_seq = clean_dna.replace("T", "U") 
        # 執行轉譯
        protein_seq = translate_rna_to_protein(rna_seq)

        # 顯示演算法執行結果
        col1, col2, col3 = st.columns(3)
        col1.metric("輸入的 DNA 長度", f"{len(clean_dna)} bp")
        col2.metric("轉錄 mRNA", "成功")
        col3.metric("轉譯胺基酸", f"{len(protein_seq)} aa")

        st.code(f"mRNA 序列: {rna_seq}\n胺基酸序列: {protein_seq}", language="text")

        if len(protein_seq) > 0:
            st.markdown("---")
            st.subheader("第二階段：AI 蛋白質特性預測")
            try:
                # 串接 LLM 進行特性分析
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = f"""
                你現在是一位頂尖的結構生物學家與生物資訊專家。
                我有一段剛剛透過中心法則演算法轉譯出來的胺基酸序列：{protein_seq}

                請根據這段序列，提供簡要的學術分析：
                1. 胺基酸組成特徵 (例如：疏水性/親水性比例、帶電狀況)。
                2. 二級結構預測 (這段序列傾向形成 Alpha-helix 還是 Beta-sheet？)。
                3. 潛在功能推測 (如果這是一個真實蛋白質的片段，它可能具備什麼類型的功能？)。
                
                請用高中生能理解的繁體中文回答，語氣專業但易懂。
                """
                with st.spinner('正在將序列傳送至 AI 結構資料庫分析中...'):
                    response = model.generate_content(prompt)
                
                st.success("分析完成！")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"AI 連線發生錯誤：{e}")
        else:
            st.warning("轉譯出的胺基酸序列為空，請檢查輸入的 DNA 是否正確 (需以起始密碼子對應的 ATG 開始較佳)。")
