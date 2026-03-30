# Apache Access Log 分析工具

## 1. 環境準備 (Prerequisites)
執行前請先安裝必要的 Python 實作套件：
```bash
pip install geoip2
```

## 2. 下載 IP 地理位置資料庫 (Database)
前往 DB-IP 官網 下載 IP to Country Lite。

選擇 MMDB 格式 (例如：dbip-country-lite-2026-03.mmdb)。

下載後將檔案解壓縮，並放置於與 Python 程式碼 (trans.py) 相同的資料夾。

注意：請確認程式碼中的 DB_FILE 變數名稱與你下載的檔名完全一致。