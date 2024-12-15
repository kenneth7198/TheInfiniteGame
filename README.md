![image](https://github.com/kenneth7198/TheInfiniteGame/blob/main/images/logo.png)

# The Infinite Show
此專案基於 Generative AgentsCN 並原始的作者為 Generative Agents 與 Wounderland 專案。
此專案為清華大學許素朱教授在清大電資學院資訊應用所開設的【網路藝術】課程期末作業，此作業探討AI與AI之間虛擬數位社群關係變化，試圖透過一個角色進行改良成具有【欺騙、竄改、造謠、鼓舞投資、以及散播數位謠言的AI人工代理角色】，經過這個AI代理人，在虛擬數位社群內模擬此AI角色是否能操弄整個虛擬村莊的AI之間的關係變化，最終期望在這個過程中產生出AI領袖的人格特質出來。

# 原始的研究論文如下：
### Generative Agents: Interactive Simulacra of Human Behavior : https://arxiv.org/abs/2304.03442

# 原始的github來源：
### https://github.com/joonspk-research/generative_agents
### https://github.com/x-glacier/GenerativeAgentsCN
### https://github.com/Archermmt/wounderland


# clone原始碼
1. git clone https://github.com/kenneth7198/TheInfiniteShow.git
2. cd TheInfiniteShow


# 基本安裝環境
1. 安裝Anaconda
2. 建立Anaconda虛擬環境，名為the_infinite_show，並選用python 3.11.11
3. 啟動the_infinite_show的虛擬環境，使用terminal開啟
4. cd到clone下來的資料夾，在TheInfiniteShow資料夾內，輸入：
```
pip install -r requirements.txt
```
5. 下載Ollama的本機運作的AI模型，到官網上下載 https://ollama.com/
6. 安裝後開一個新的命令提示字元視窗，輸入ollama指令看看有沒成功安裝或是否可以呼叫
7. 開啟系統內容的"編輯系統環境變數"，在進階頁籤點選"環境變數"，然後在系統變數中新增以下的變數與值:
```
OLLAMA_HOST   0.0.0.0
OLLAMA_KEEP_ALIVE 2h
OLLAMA_MODELS X:\OllamaModels
OLLAMA_ORIGINS  *
```
![image](https://github.com/kenneth7198/TheInfiniteGame/blob/main/images/ollama_env.png)

# 下載&運作LLM 大語言模型，重開機後仍需重新下載

1. 回到命令提示字元視窗中，透過指令方式下載以下的LLM大語言模型，這邊採用的是阿里巴巴的Qwen 2.5(通義千問) : https://github.com/QwenLM/Qwen
```
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull bge-m3:latest
```
2. 等待下載完畢之後，用以下的指令啟動Ollama大語言模型運作
```
ollama serve
```
  
# 運作虛擬小鎮

切換到原本的TheInfiniteShow的Anaconda虛擬環境下，切換到generative_agents資料夾，並用以下指令啟動虛擬小鎮的計算
```
cd generative_agents
python start.py --name infinite-test --start "20241214-08:00" --step 10 --stride 10
```
參數說明：
* name參數後面加的是一個用英文組合數字組成的虛擬小鎮名稱
* start參數後面是設置小鎮的起始時間點
* step參數是迭代幾次後停止運作，設置10預計要跑1小時多
* stride參數是設置每一次時間運作的累計方式，設置10等於9:00 9:10 9:20 ...

# 回放過程 
1. 在剛剛的虛擬環境下輸入以下指令，壓縮infinite-test的虛擬小鎮運算過後的數據
```
python compress.py --name infinite-test
```

2. 回放infinite-test虛擬小鎮的過程
```
python replay.py
```

3. 開啟網頁 http://127.0.0.1:5000/?name=infinite-test 看到虛擬小鎮內各個居民活動過程