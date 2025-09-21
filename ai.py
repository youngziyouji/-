# ai.py
from openai import OpenAI
import json
import sys

API_KEY = "ec74abae-967d-41ed-8903-30ba58aa415a"
MODEL_ID = "doubao-seed-1-6-250615"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

def get_ai_response(user_input):
    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "基于发给你的数据，给教师写学生评语,不要出现英文:"},
                {"role": "user", "content": user_input}
            ],
            max_tokens=5000,
            temperature=0.7,
        )
        ai_response = response.choices[0].message.content
        return ai_response
    except Exception as e:
        print(f"请求失败: {e}", file=sys.stderr)
        return "请求失败，请检查网络连接或网页链接的合法性，稍后再试。"

if __name__ == "__main__":
    # 从命令行参数中获取学生数据
    student_data = json.loads(sys.argv[1])
    # 将学生数据转换为字符串
    user_input = json.dumps(student_data, ensure_ascii=False)
    # 调用 AI 接口生成评语
    ai_response = get_ai_response(user_input)
    # 输出 AI 生成的评语，确保使用 UTF-8 编码
    print(ai_response, file=sys.stdout)