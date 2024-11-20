# Generative AI Scribe

## 簡介

**「生成式 AI 書僮」** 系統專為處理大規模文本而設計，利用基因演算法與嵌入向量技術，提供精準的文本摘要與自動生成考題功能。它能適配資源受限的環境，並克服傳統大型語言模型的答非所問與過度生成問題，旨在成為智能文本處理的可靠解決方案。

---

## 目標

1. **準確擷取文本中的關鍵內容**  
   - 利用嵌入向量技術與基因演算法，提升文本摘要與關鍵字提取的精確度。

2. **改進文本生成**  
   - 模擬基因進化過程，增強生成內容的流暢度與語義準確性。

3. **提升學習與應用體驗**  
   - 提供靈活、高效的文本處理功能，滿足多樣化場景需求。

---

## 方法

1. **關鍵字與句子提取**  
   - 利用語義分析與嵌入向量技術，自動識別文本核心內容。

2. **文本優化**  
   - 模擬基因突變與進化過程，逐代篩選最佳文本結構與關鍵句組合。

3. **與 LLM 整合**  
   - 使用本地化 LLM（如 Llama3），實現輕量化、高準確度的文本處理與生成。

4. **功能擴展**  
   - 支援生成考題及提供個性化學習建議。

---

## 技術參考

1. **基因演算法評估機制**  
   - 使用摘要與原文進行相似度對比，詳見：[Adaptive Semantic Similarity](https://github.com/yesaouo/adaptive-semantic-similarity)。

2. **關鍵字提取模型**  
   - 訓練於英語科學論文摘要的模型：[Keyphrase Extraction KBIR-InSpec](https://huggingface.co/ml6team/keyphrase-extraction-kbir-inspec)。

---

## 系統需求

- **Python**: 3.9  
- **建議環境**: PyTorch 2.4, CUDA 11.8, cuDNN 8  
- **安裝依賴**: `requirements.txt`

---

## 安裝與環境配置

### 1. Conda 建立虛擬環境

```bash
conda create --name Generative_AI_Scribe python=3.9
conda activate Generative_AI_Scribe
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

### 2. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 3. 安裝 Ollama 並配置模型

#### **Linux**
執行以下指令安裝 Ollama：
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### **Windows / macOS**
至 [Ollama 官網](https://ollama.com/download) 下載並安裝。

#### **選擇並安裝模型**
安裝 Hugging Face 工具：
```bash
pip install huggingface-hub
huggingface-cli login  # 登錄 Hugging Face 帳戶（如需要）
```

下載模型（示例：Ministral 8B 量化模型）：
```bash
huggingface-cli download bartowski/Ministral-8B-Instruct-2410-GGUF \
    Ministral-8B-Instruct-2410-Q4_K_L.gguf \
    --local-dir downloads \
    --local-dir-use-symlinks False
```

配置模型：
1. 使用 `vim` 編輯下載資料夾內的 `Modelfile.txt`：
   ```plaintext
   FROM Ministral-8B-Instruct-2410-Q4_K_L.gguf
   PARAMETER temperature 0
   PARAMETER num_ctx 4096
   ```
2. 建立模型：
   ```bash
   ollama create Ministral-8B -f Modelfile.txt
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
