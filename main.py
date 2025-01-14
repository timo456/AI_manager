import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import re

# 確保從 Streamlit Secrets 中讀取 API 金鑰
api_key = st.secrets["openai"]["api_key"]

if not api_key:
    st.error("API 金鑰未設置，請檢查 s11230017.env 文件。")
else:
    # 設置 OpenAI API 客戶端
    client = OpenAI(api_key=api_key)

    st.title("AI 行程助理")
    
    # 用戶輸入需求
    user_input = st.text_input("請輸入你的行程需求：", placeholder="例如：幫我規劃一個五天的學習計劃，涵蓋數學、語言學、科學和一些休閒活動，每天學習不超過6小時，並確保每天下午有1小時的自由時間。")

    # 當按下“生成行程”按鈕時，開始處理請求
    if st.button("生成行程"):
        if user_input:
            try:
                # 在請求之前添加延遲（例如：2秒）
                time.sleep(2)

                # 提供給 AI 的提示，要求返回計劃格式
                prompt = f"{user_input}\n請以以下格式返回計劃：\n1. 數學 - 代數：2025-01-15，9:00AM - 12:00PM\n2. 語言學 - 英文：2025-01-15，1:00PM - 3:00PM\n3. 科學 - 物理：2025-01-16，9:00AM - 12:00PM\n4. 休閒活動：2025-01-16，3:00PM - 4:00PM"

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # 使用你想要的模型
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # 使用正確的方式訪問生成的內容
                plan = response.choices[0].message.content.strip()  # 獲取生成的行程計畫
                
                # 顯示生成的計劃
                st.success("生成的行程如下：")
                st.markdown(plan)

                # 根據 AI 回應繼續添加更多的事件
                plan_lines = plan.split('\n')
                events = []

                # 定义一个函数将 AM/PM 时间格式转换为 24 小时制
                def convert_to_24hr_format(time_str):
                    return datetime.strptime(time_str, '%I:%M%p').strftime('%H:%M')

                for line in plan_lines:
                    # 使用正则表达式解析格式化的计划，匹配活动标题、日期和时间
                    match = re.match(r'(.*?)：(\d{4}-\d{2}-\d{2})，(\d{1,2}:\d{2}[APM]{2}) - (\d{1,2}:\d{2}[APM]{2})', line)
                    if match:
                        title = match.group(1)  # 活动标题
                        start_date = match.group(2)  # 日期
                        start_time = match.group(3)  # 开始时间
                        end_time = match.group(4)  # 结束时间

                        # 将 AM/PM 时间格式转换为 24 小时制
                        start_time_24hr = convert_to_24hr_format(start_time)
                        end_time_24hr = convert_to_24hr_format(end_time)

                        # 拼接完整的时间字符串，确保符合 ISO 8601 格式
                        start_datetime = f"{start_date}T{start_time_24hr}"
                        end_datetime = f"{start_date}T{end_time_24hr}"

                        # 将解析后的活动加入事件列表
                        events.append({
                            "title": title,
                            "start": start_datetime,
                            "end": end_datetime
                        })

                # 输出事件列表，检查解析结果
                for event in events:
                    print(f"Title: {event['title']}")
                    print(f"Start datetime: {event['start']}")
                    print(f"End datetime: {event['end']}")
                    print()        

                # 構建日曆 HTML 代碼
                calendar_html = f"""
                <div id="calendar"></div>
                <script src="https://cdn.jsdelivr.net/npm/fullcalendar@5.10.1/main.min.js"></script>
                <link href="https://cdn.jsdelivr.net/npm/fullcalendar@5.10.1/main.min.css" rel="stylesheet" />
                <script>
                    document.addEventListener('DOMContentLoaded', function() {{
                        var calendarEl = document.getElementById('calendar');
                        var calendar = new FullCalendar.Calendar(calendarEl, {{
                            initialView: 'dayGridMonth',
                            events: {events},  // 傳遞事件數據
                        }});
                        calendar.render();
                    }});
                </script>
                """

                # 使用 Streamlit 的 st.components.v1.html 方法嵌入 FullCalendar
                st.components.v1.html(calendar_html, height=600)

            except Exception as e:
                st.error(f"發生錯誤：{str(e)}")
        else:
            st.error("請輸入有效的需求！")
