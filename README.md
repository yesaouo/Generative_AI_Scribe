# Generative AI Scribe

## 簡介

**「生成式 AI 書僮」** 系統旨在以精準的回應協助用戶處理大規模文本，提升學習與工作效率。隨著 ChatGPT 等大型語言模型的普及，學生與專業人士在使用這些工具時，常因需求表達不清或答案不夠相關而感到困擾。「生成式 AI 書僮」解決了這些痛點，基於基因演算法與嵌入向量技術，提供高效的文本摘要、自動生成考題功能，並適配資源受限的環境。

核心功能包括：
- 關鍵內容提取
- 高質量文本生成
- 跨領域學習支持與個性化建議

未來計劃擴展學習工具整合與進一步提升用戶體驗，旨在成為智能文本處理的可靠解決方案。

---

## 目標

1. **準確擷取文本中的關鍵內容**  
   - 利用嵌入向量技術與基因演算法，提升文本摘要與關鍵字提取的精確度。
   
2. **改進文本生成**  
   - 模擬基因進化過程，提高生成內容的流暢度與語義準確性。
   
3. **提升學習與應用體驗**  
   - 提供靈活、高效的文本處理功能，適應多樣化場景需求。

---

## 方法

1. **關鍵字與句子提取**  
   - 利用語義分析與嵌入向量技術，自動識別文本中的核心內容。
   
2. **文本優化**  
   - 模擬基因突變與進化過程，逐代篩選最優文本結構與關鍵句組合。
   
3. **與 LLM 整合**  
   - 使用本地化 LLM（如 Llama3），實現輕量化、高準確度的文本處理與生成。

4. **功能擴展**  
   - 支持生成各類考題，並提供智能化的文本摘要與學習建議。

---

## 技術參考

1. **基因演算法的評估機制**  
   - 使用摘要與原文進行相似度對比，完整的算法參考：[Adaptive Semantic Similarity](https://github.com/yesaouo/adaptive-semantic-similarity)。

2. **關鍵字提取模型**  
   - 訓練於英語科學論文摘要的模型：[Keyphrase Extraction KBIR-InSpec](https://huggingface.co/ml6team/keyphrase-extraction-kbir-inspec)。

---

## 系統需求

- **Python**: 3.9  
- **建議環境**: PyTorch 2.4, CUDA 11.8, cuDNN 8  
- **安裝依賴**: `requirements.txt`

---

## 安裝與環境配置

1. 使用 Conda 建立虛擬環境：
   ```bash
   conda create --name Generative_AI_Scribe python=3.9
   conda activate Generative_AI_Scribe
   conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
   ```

2. 安裝相依套件：
   ```bash
   pip install -r requirements.txt
   ```

---

## 執行方式

1. 啟動應用程式：
   ```bash
   python app.py
   ```
2. 使用瀏覽器開啟 `index.html` 進行操作。

---

## 啟動參數

以下為可選參數及其效果：

| 參數                      | 描述                                         |
|---------------------------|--------------------------------------------|
| `--host`                  | 指定後端服務的 URL，預設為 `http://localhost:11434` |
| `--ignore-backend-check`  | 忽略 Ollama 後端的檢查                     |

範例：
```bash
python app.py --host http://example.com:12345 --ignore-backend-check
```

---

## 系統優勢

1. **精準摘要與生成**  
   克服傳統語言模型答非所問或過度生成的問題。
   
2. **資源友好**  
   採用時間換空間的策略，適合硬體受限環境。

3. **靈活應用**  
   支援多樣化學習與文本處理場景。

**「生成式 AI 書僮」助您輕鬆應對文本挑戰，快速提取重點，提升效率！**
