# Python Web Picture Scrapper Script

> ### 注意，這檔案只是範例，不可用作非法用途
> 

這是一個使用 Selenium 和 Requests library 的 Python script，可以自動從指定網站上下載圖片。目前此 script 設定為爬 Uvex Safety 和 Gloria Eyewear（Oakley）上面的圖片，但可以依需求修改程式碼來爬其他網站。

## 環境需求

- **Operating System：** Ubuntu 或 Windows 上的 WSL2（Windows Subsystem for Linux 2）
- **Python：** 建議使用 version 3.8 以上
- **Conda：** 用於管理 Python environment 和相依套件
- **Google Chrome / Chromium：** Selenium 需要 browser 來執行自動化操作

## 環境設定（使用 Conda）

以下步驟適用於 **Ubuntu** 和 **WSL2**：

1. **開啟 Terminal**
2. **建立一個新的 Conda 環境** (您可以將 `scraper_env` 替換為您喜歡的環境名稱):
    
    ```bash
    conda create --name scraper_env python=3.9 -y
    
    ```
    
    *(我們選擇 Python 3.9，您可以根據需要調整版本)*
    
3. **啟動 Conda 環境:**
    
    ```bash
    conda activate scraper_env
    ```
    
    *您應該會看到終端機提示符前面出現 `(scraper_env)`。*
    
4. **安裝必要的 Python 套件:**
    - 確保您的專案目錄中有一個 `requirements.txt` 文件，內容如下：
        
        ```
        selenium
        webdriver-manager
        requests
        ```
        
    - 在已啟動的 `scraper_env` 環境中，執行以下指令安裝套件：
        
        ```bash
        pip install -r requirements.txt
        ```
        
5. **安裝 Google Chrome / Chromium:**
    - **Ubuntu:***或者，如果您偏好 Chromium:*
        
        ```bash
        sudo apt update
        sudo apt install -y google-chrome-stable
        ```
        
        ```bash
        sudo apt update
        sudo apt install -y chromium-browser
        ```
        
    - **WSL2:**
        - 在 WSL2 環境中，通常**不需要**直接安裝 Chrome。Selenium（透過 `webdriver-manager`）會主動使用您的 **Windows 主機**上所安裝的 Chrome browser。請確認您的 Windows system 已安裝最新版本的 Google Chrome，`webdriver-manager` 便會自動下載對應版本的 ChromeDriver。

## 如何執行 Script

1. **確認您是否處於已啟動的 Conda 環境中（請輸入 `conda activate scraper_env`）**
2. **切換到含有 `app.py` 的目錄（若您的 script 檔名不同，請用實際檔名取代）**
3. **執行 Python 腳本:**
    
    ```bash
    python app.py
    ```
    
    *(如果您的腳本檔名不同，請替換 `app.py`)*
    
4. 腳本將會啟動 Chrome browser（除非您啟用了 headless mode，否則您會看到 browser 視窗彈出），接著開始訪問目標網站並下載圖片。執行進度和任何 error message 都會顯示在 terminal 中。

## 自訂腳本

如果要爬取不同的網站或修改設定：

1. **編輯腳本檔案（`app.py`）**
2. 找到標示為 `### EDIT HERE ###` 的註解。這些註解標示了您最可能需要修改的部分：
    - **`UVEX_URL`、`GLORIA_OAKLEY_URL`：** 修改為您想爬取的目標 URL。
    - **`OUTPUT_DIR_UVEX`、`OUTPUT_DIR_GLORIA`：** 修改圖片儲存的資料夾名稱或路徑。
    - **`scrape_uvex` 和 `scrape_gloria_oakley` function 內部：**
        - 修改 **CSS selector**（`By.CSS_SELECTOR, '...'`）以匹配新網站的 HTML 結構，用於定位圖片元素、「載入更多」按鈕或分頁元素。您可以使用 browser 的開發者工具（按 F12）來檢查元素並找到正確的 selector。
        - 調整**取得圖片 URL 的屬性**（例如 `img_tag.get_attribute('src')` 可能需要改成 `'data-src'` 或其他屬性）。
        - 修改**頁面載入邏輯**（例如，處理不同的分頁方式或無限滾動）。
        - 調整**檔案命名邏輯**。
    - **主要執行區塊（`if __name__ == "__main__":`）：** 修改要呼叫的爬蟲 function。

## 輸出

- 腳本會在執行目錄下建立一個 `scraped_images` 資料夾（或者您在 `OUTPUT_DIR_...` 變數中指定的其他名稱）。
- `scraped_images` 內部會有對應網站的子資料夾（例如 `uvex_safety`、`gloria_oakley`）。
- 下載的圖片將會儲存在對應的子資料夾中。
