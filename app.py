import streamlit as st
from openai import OpenAI
import pandas as pd
from io import BytesIO
import requests
from Bio.SeqUtils.ProtParam import ProteinAnalysis

# ==========================================
# UI 基礎配置與全域設定
# ==========================================
st.set_page_config(page_title="生技資訊 AI 工具箱", page_icon="🧬", layout="wide")

with st.sidebar:
    st.title("🧬 生技資訊 AI 工具箱")
    st.write("APCS 組專題實作：結合資訊技術與生物產業科學")
    st.markdown("---")
    
    st.subheader("🔑 API 密碼設定 (Groq 雙模型架構)")
    st.markdown("使用 Groq 雲端平台調度不同參數級別的開源大模型。")
    groq_api_key = st.text_input("請輸入 Groq API Key：", type="password").strip()
    st.markdown("---")
    
    app_mode = st.radio(
        "🖥️ 請選擇分析工具：", 
        ["📄 單篇文獻 AI 導讀 (Llama-3 8B)", 
         "📚 批次文獻處理與報表 (Llama-3 8B)", 
         "🔬 蛋白質特徵與資料庫比對 (Agentic AI 架構)"]
    )

# 共用 RNA 密碼子表 (已修復 Cysteine Bug)
CODON_TABLE = {
    'AUA':'I', 'AUC':'I', 'AUU':'I', 'AUG':'M', 'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACU':'T',
    'AAC':'N', 'AAU':'N', 'AAA':'K', 'AAG':'K', 'AGC':'S', 'AGU':'S', 'AGA':'R', 'AGG':'R',
    'CUA':'L', 'CUC':'L', 'CUG':'L', 'CUU':'L', 'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCU':'P',
    'CAC':'H', 'CAU':'H', 'CAA':'Q', 'CAG':'Q', 'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGU':'R',
    'GUA':'V', 'GUC':'V', 'GUG':'V', 'GUU':'V', 'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCU':'A',
    'GAC':'D', 'GAU':'D', 'GAA':'E', 'GAG':'E', 'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGU':'G',
    'UCA':'S', 'UCC':'S', 'UCG':'S', 'UCU':'S', 'UUC':'F', 'UUU':'F', 'UUA':'L', 'UUG':'L',
    'UAC':'Y', 'UAU':'Y', 'UAA':'_', 'UAG':'_', 'UGA':'_', 'UGG':'W', 'UGU':'C', 'UGC':'C'
}

def translate_rna_to_protein(rna_seq):
    protein = ""
    for i in range(0, len(rna_seq), 3):
        codon = rna_seq[i:i+3]
        if len(codon) == 3:
            amino_acid = CODON_TABLE.get(codon, '?')
            if amino_acid == '_': break
            protein += amino_acid
    return protein

def get_groq_client():
    return OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")

# ==========================================
# 模組一：單篇文獻 AI 導讀
# ==========================================
if app_mode == "📄 單篇文獻 AI 導讀 (Llama-3 8B)":
    st.header("📄 生技文獻 AI 導讀助手")
    st.write("調用極速 8B 模型，瞬間轉換結構化的中文導讀。")
    text_input = st.text_area("請貼上單篇生技英文文獻摘要：", height=200)
    
    if st.button("開始導讀"):
        if not groq_api_key: st.error("請先在左側輸入 Groq API Key！")
        elif not text_input: st.warning("請貼上文獻摘要！")
        else:
            try:
                client = get_groq_client()
                prompt = f"""你是一位專業的生物科技產業分析師。請將以下英文學術摘要轉換為高中生能理解的繁體中文。請固定以三個部分輸出：1. 研究目的、2. 核心技術、3. 產業應用價值。文獻摘要：\n{text_input}"""
                with st.spinner('Groq 正在極速解析文獻中...'):
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}]
                    )
                st.success("導讀完成！")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"發生錯誤：{e}")

# ==========================================
# 模組二：批次文獻處理與報表
# ==========================================
elif app_mode == "📚 批次文獻處理與報表 (Llama-3 8B)":
    st.header("📚 批次文獻處理與 Excel 匯出")
    st.info("上傳純文字檔 (.txt)，每篇摘要之間使用 `---` 隔開。")
    uploaded_file = st.file_uploader("選擇您的 TXT 檔案", type=['txt'])
    
    if st.button("啟動批次分析"):
        if not groq_api_key: st.error("請輸入 Groq API Key！")
        elif uploaded_file is None: st.warning("請先上傳檔案！")
        else:
            try:
                client = get_groq_client()
                content = uploaded_file.getvalue().decode("utf-8")
                abstracts = [abs.strip() for abs in content.split("---") if abs.strip()]
                results = []
                progress_bar = st.progress(0)
                for i, abstract in enumerate(abstracts):
                    prompt = f"""請分析此生物科技摘要，固定輸出：- 研究目的：(一句話)\n- 核心技術：(一句話)\n- 應用價值：(一句話)\n摘要：\n{abstract}"""
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    results.append({
                        "原文摘要 (前100字)": abstract[:100] + "...",
                        "AI 導讀報告": response.choices[0].message.content
                    })
                    progress_bar.progress((i + 1) / len(abstracts))
                st.success("批次處理完畢！")
                for idx, row in enumerate(results):
                    with st.expander(f"📄 文獻 {idx+1} 導讀結果", expanded=(idx==0)):
                        st.markdown(f"**原文摘要:**\n> {row['原文摘要 (前100字)']}")
                        st.markdown(f"**AI 分析:**\n{row['AI 導讀報告']}")
                df = pd.DataFrame(results)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='導讀報告')
                output.seek(0)
                st.download_button(label="📥 下載 Excel 報表 (.xlsx)", data=output.getvalue(), file_name="生技文獻導讀批次.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"發生錯誤：{e}")

# ==========================================
# 模組三：蛋白質特徵與 UniProt 檢索 (Agentic AI)
# ==========================================
elif app_mode == "🔬 蛋白質特徵與資料庫比對 (Agentic AI 架構)":
    st.header("🔬 序列解析與 Agentic AI 資料庫檢索")
    st.write("展示矽谷最新的 Agentic Workflow：讓 AI 預測特徵，再由系統自動調用真實資料庫驗證。")
    dna_input = st.text_area("請輸入 DNA 序列：", "ATGCGTGCTAAATGGCGTAAAAAACGTATGCGTCGTCTGAAACGTAAACGTCGTAAAATGCGTCAGCGTTCCAAACGTGCTCCTGCT")
    
    if st.button("執行生資管線分析"):
        if not groq_api_key: st.error("請在左側輸入 Groq API Key！")
        else:
            clean_dna = dna_input.upper().replace(" ", "").replace("\n", "")
            protein_seq = translate_rna_to_protein(clean_dna.replace("T", "U"))
            
            if len(protein_seq) < 5:
                st.warning("轉譯序列過短，請提供更長的 DNA 序列。")
            else:
                col1, col2 = st.columns(2)
                col1.code(f"mRNA: {clean_dna.replace('T', 'U')}", language="text")
                col2.code(f"Protein: {protein_seq}", language="text")
                
                st.subheader("⚙️ Biopython 物理化學特徵計算")
                try:
                    analysis = ProteinAnalysis(protein_seq)
                    mw = round(analysis.molecular_weight(), 2)
                    pi = round(analysis.isoelectric_point(), 2)
                    gravy = round(analysis.gravy(), 3)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("分子量 (MW)", f"{mw} Da")
                    c2.metric("等電點 (pI)", f"{pi}")
                    c3.metric("親疏水性 (GRAVY)", f"{gravy}")
                except Exception as e:
                    st.error(f"Biopython 運算錯誤：{e}")
                    mw, pi, gravy = "N/A", "N/A", "N/A"

                # 💡 核心亮點：Agentic Workflow 資料庫檢索
                st.subheader("🌐 Agentic AI 輔助資料庫檢索")
                uniprot_hit = "未找到完全匹配的已知蛋白質。"
                guessed_name = "Unknown"
                
                try:
                    with st.spinner("啟動 Agent 1：正在讓 70B AI 預測序列名稱..."):
                        client = get_groq_client()
                        # 稍微修改提示詞，拿掉退縮的 Unknown 條件，鼓勵它大膽輸出基因縮寫
                        guess_prompt = f"Identify the human gene symbol for this exact amino acid sequence: {protein_seq}. Respond with ONLY the official gene symbol (e.g. RPL41, GCG). Do not explain."
                        guess_res = client.chat.completions.create(
                            model="llama-3.3-70b-versatile", # 🎯 關鍵升級：換成 70B 頂級模型
                            messages=[{"role": "user", "content": guess_prompt}]
                        )
                        guessed_name = guess_res.choices[0].message.content.strip().replace('"', '').replace("'", "")
                    
                    st.write(f"💡 **AI 初步預測基因/蛋白名稱：** `{guessed_name}`")

                    if guessed_name.lower() != "unknown" and len(guessed_name) > 1:
                        with st.spinner(f"啟動 Agent 2：正在向 UniProt 驗證 {guessed_name}..."):
                            # 將 AI 猜出來的名字編碼後丟給資料庫搜尋
                            safe_name = requests.utils.quote(guessed_name)
                            url = f"https://rest.uniprot.org/uniprotkb/search?query={safe_name}&format=json&size=1"
                            res = requests.get(url)
                            data = res.json()
                            if data.get('results') and len(data['results']) > 0:
                                top_hit = data['results'][0]
                                protein_name = top_hit.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', 'Unknown')
                                organism = top_hit.get('organism', {}).get('scientificName', 'Unknown')
                                uniprot_hit = f"✅ **資料庫驗證成功！** 此序列與 **{organism}** 的 **{protein_name}** 相關。"
                            st.info(uniprot_hit)
                    else:
                        st.warning("AI 無法精準識別此短肽，請嘗試更長或具備特徵的序列。")

                except Exception as e:
                    st.error(f"連線失敗：{e}")

                st.markdown("---")
                st.subheader("🤖 AI 綜合生化報告")
                try:
                    client = get_groq_client()
                    prompt = f"""
                    請根據以下系統計算出的數據產生生化報告：
                    - 胺基酸序列：{protein_seq}
                    - 預測蛋白名稱：{guessed_name}
                    - 分子量：{mw} Da
                    - 等電點(pI)：{pi}
                    - GRAVY(親疏水性)：{gravy}
                    - UniProt 檢索結果：{uniprot_hit}
                    
                    請簡要分析：1. 根據 GRAVY 與 pI 預測此蛋白質在細胞內的環境。2. 綜合評估其潛在功能。請用高中生能理解的繁體中文回答。
                    """
                    with st.spinner('Llama-3 70B 正在進行深度生化推理...'):
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}]
                        )
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"AI 報告生成錯誤：{e}")
