import re
import csv
from datetime import datetime
import geoip2.database
from collections import Counter

# --- 設定區 ---
LOG_FILE = 'avalue.com-ssl_log-Mar-2026' 
DB_FILE = 'dbip-country-lite-2026-03.mmdb'
LOG_PATTERN = r'^(?P<ip>\S+) - - \[(?P<time>.*?)\] "(?P<request>.*?)" (?P<status>\d{3}) (?P<size>\S+) "(?P<referer>.*?)" "(?P<user_agent>.*?)"'

def analyze_and_rank():
    print("📊 Log 分析工具 (Top 10 排名)")
    print("格式: 年/月/日 (例如 2026/02/28)")
    start_input = input("開始日期: ").strip()
    end_input = input("結束日期: ").strip()

    try:
        # 1. 時間格式解析
        start_dt = datetime.strptime(start_input, '%Y/%m/%d')
        end_dt = datetime.strptime(end_input, '%Y/%m/%d').replace(hour=23, minute=59, second=59)
        
        # 2. 自動生成檔名
        fn_start = start_dt.strftime('%Y%m%d')
        fn_end = end_dt.strftime('%Y%m%d')
        output_csv = f"analysis_{fn_start}_to_{fn_end}.csv"
        
        ip_to_country = {}
        country_counter = Counter()
        ip_counter = Counter()  # 新增：用來統計個別 IP 次數
        processed_count = 0
        exported_count = 0

        print(f"\n🚀 正在分析: {start_input} ~ {end_input}")

        with geoip2.database.Reader(DB_FILE) as reader:
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f_in:
                with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f_out:
                    
                    keys = ["ip", "country", "time", "request", "status", "size", "referer", "user_agent"]
                    writer = csv.DictWriter(f_out, fieldnames=keys)
                    writer.writeheader()

                    for line in f_in:
                        processed_count += 1
                        match = re.search(LOG_PATTERN, line)
                        
                        if match:
                            log_time_str = match.group('time').split(' ')[0]
                            try:
                                log_dt = datetime.strptime(log_time_str, '%d/%b/%Y:%H:%M:%S')
                                
                                if start_dt <= log_dt <= end_dt:
                                    data = match.groupdict()
                                    ip = data['ip']
                                    
                                    # 統計 IP 請求次數
                                    ip_counter[ip] += 1
                                    
                                    # 查詢國家
                                    if ip not in ip_to_country:
                                        try:
                                            res = reader.country(ip)
                                            ip_to_country[ip] = res.country.name or "Unknown"
                                        except:
                                            ip_to_country[ip] = "Unknown"
                                    
                                    data['country'] = ip_to_country[ip]
                                    country_counter[data['country']] += 1
                                    
                                    writer.writerow(data)
                                    exported_count += 1
                            except:
                                continue

                        if processed_count % 200000 == 0:
                            print(f"已掃描 {processed_count} 行...")

        # --- 輸出結果總結 ---
        print("\n" + "="*50)
        print(f"✅ 處理完成！結果已存至: {output_csv}")
        print(f"總計掃描: {processed_count} 行 | 符合區間: {exported_count} 行")
        print("="*50)

        if exported_count > 0:
            # 1. 輸出 Top 10 國家
            print("\n🌍 [Top 10 流量來源國家]")
            print(f"{'國家':<23} | {'請求次數':<10}")
            print("-" * 40)
            for country, count in country_counter.most_common(10):
                print(f"{country:<25} | {count:<10,}")

            # 2. 輸出 Top 10 IP
            print("\n💻 [Top 10 請求來源 IP]")
            print(f"{'IP 位址':<16} | {'國家':<13} | {'請求次數':<10}")
            print("-" * 50)
            for ip, count in ip_counter.most_common(10):
                country = ip_to_country.get(ip, "Unknown")
                print(f"{ip:<18} | {country:<15} | {count:<10,}")
        else:
            print("\n⚠️ 該區間內沒有資料。")

    except ValueError:
        print("❌ 日期格式錯誤，請使用 2026/02/28")
    except FileNotFoundError:
        print("❌ 找不到檔案，請確認 Log 與 MMDB 是否在同資料夾。")

if __name__ == "__main__":
    analyze_and_rank()