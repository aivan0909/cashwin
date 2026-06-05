# Cloud Function 部署指南

## 需要的檔案
- `main.py`（Cloud Function 主程式）
- `requirements.txt`（相依套件）

---

## 部署步驟

### Step 1：進入 Google Cloud Console
前往 https://console.cloud.google.com

### Step 2：開啟 Cloud Functions
左側選單 → Cloud Functions → 點擊「建立函式」

### Step 3：基本設定
- **函式名稱**：`get-institutional-investors`
- **地區**：`asia-east1`（台灣最近）
- **觸發條件**：HTTP
- **驗證**：允許未經驗證的叫用（Allow unauthenticated）✅
- 點擊「儲存」

### Step 4：程式碼設定
- **執行階段**：Python 3.11
- **進入點**：`get_institutional_investors`
- 將 `main.py` 內容貼到編輯器
- 將 `requirements.txt` 內容貼到對應欄位

### Step 5：部署
點擊「部署」，等待約 2 分鐘

### Step 6：取得網址
部署完成後，複製「觸發條件」的 URL，格式為：
```
https://asia-east1-YOUR_PROJECT.cloudfunctions.net/get-institutional-investors
```

### Step 7：測試 API
在瀏覽器輸入：
```
https://YOUR_URL?stock=2330
```
應該會看到台積電的三大法人資料

---

## 回傳資料格式
```json
{
  "stock_id": "2330",
  "count": 30,
  "data": [
    {
      "date": "2026/06/04",
      "foreign": -2940,
      "investment_trust": 0,
      "dealer_self": -19,
      "dealer_hedge": -15,
      "total": -2974
    }
  ]
}
```

---

## 將 URL 填入 HTML
部署完成後，把你的 Cloud Function URL 填入 HTML 功能四的設定欄位即可。

---

## 免費額度（完全夠用）
- 每月 200 萬次呼叫免費
- 每月 400,000 GB 秒免費
- 個人使用完全不需付費
