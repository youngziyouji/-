import tkinter as tk
from tkinter import ttk, messagebox
import json
import numpy as np
from openai import OpenAI

# 配置 OpenAI 客户端
API_KEY = "ec74abae-967d-41ed-8903-30ba58aa415a"
MODEL_ID = "doubao-seed-1-6-250615"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

# 全局数据：10名学生信息（学号唯一标识）
students_data = [
    {"id": "2024001", "name": "张三", "pwd": "001", "comment": ""},
    {"id": "2024002", "name": "李四", "pwd": "002", "comment": ""},
    {"id": "2024003", "name": "王五", "pwd": "003", "comment": ""},
    {"id": "2024004", "name": "赵六", "pwd": "004", "comment": ""},
    {"id": "2024005", "name": "孙七", "pwd": "005", "comment": ""},
    {"id": "2024006", "name": "周八", "pwd": "006", "comment": ""},
    {"id": "2024007", "name": "吴九", "pwd": "007", "comment": ""},
    {"id": "2024008", "name": "郑十", "pwd": "008", "comment": ""},
    {"id": "2024009", "name": "钱十一", "pwd": "009", "comment": ""},
    {"id": "2024010", "name": "冯十二", "pwd": "010", "comment": ""}
]

# 为每个学生随机生成多维度学习数据
def generate_student_data():
    for student in students_data:
        student['homework_score'] = np.random.rand()
        student['submission_delay'] = np.random.randint(0, 5)
        student['modification_count'] = np.random.randint(0, 5)
        student['login_duration'] = np.random.randint(30, 120)
        student['video_watching_duration'] = np.random.randint(10, 60)
        student['class_participation'] = np.random.randint(0, 10)
        student['group_cooperation'] = np.random.randint(0, 10)
        student['quiz_score'] = np.random.rand()
        student['question_order'] = np.random.randint(1, 10)
        student['error_type'] = np.random.randint(0, 5)
        student['answer_time'] = np.random.randint(30, 300)
        student['discussion_post_count'] = np.random.randint(0, 20)
        student['sentiment_score'] = np.random.rand()
        student['keyword_density'] = np.random.rand()
        list = ["文科", "理科"]

        student['class'] = list[np.random.randint(0, 2)]

generate_student_data()

# 调用 AI 接口生成评语
def get_ai_response(student_data):
    try:
        user_input = json.dumps(student_data, ensure_ascii=False)
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "基于发给你的数据，给教师写学生评语:"},
                {"role": "user", "content": user_input}
            ],
            max_tokens=5000,
            temperature=0.7,
        )
        ai_response = response.choices[0].message.content
        return ai_response
    except Exception as e:
        print(f"请求失败: {e}")
        return "请求失败，请检查网络连接或网页链接的合法性，稍后再试。"

def show_teacher_window(prev_window):
    prev_window.destroy()

    teacher_win = tk.Tk()
    teacher_win.title("教师 - 学生评语管理")
    teacher_win.geometry("700x550")

    ttk.Button(
        teacher_win,
        text="返回主界面",
        command=lambda: show_main_window(teacher_win)
    ).pack(anchor=tk.W, padx=20, pady=10)

    ttk.Label(teacher_win, text="学生列表", font=("微软雅黑", 12)).pack(pady=5)
    student_tree = ttk.Treeview(
        teacher_win, columns=("id", "name"), show="headings", selectmode="browse"
    )
    student_tree.heading("id", text="学号")
    student_tree.heading("name", text="姓名")
    student_tree.column("id", width=150, anchor=tk.CENTER)
    student_tree.column("name", width=150, anchor=tk.CENTER)
    for idx, student in enumerate(students_data):
        student_tree.insert("", tk.END, iid=idx, values=(student["id"], student["name"]))
    student_tree.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=5)

    input_frame = ttk.Frame(teacher_win)
    input_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=5)

    ttk.Label(input_frame, text="评语编辑", font=("微软雅黑", 12)).pack(pady=10)
    comment_text = tk.Text(input_frame, width=40, height=15, wrap=tk.WORD)
    comment_text.pack(fill=tk.BOTH, expand=True, pady=10)

    def load_comment(event):
        selected_idx = student_tree.selection()
        if selected_idx:
            idx = int(selected_idx[0])
            comment_text.delete(1.0, tk.END)
            comment_text.insert(tk.END, students_data[idx]["comment"])

    student_tree.bind("<<TreeviewSelect>>", load_comment)

    def ai_generate_comment():
        selected_idx = student_tree.selection()
        if not selected_idx:
            messagebox.showwarning("提示", "请先选中一名学生！")
            return
        idx = int(selected_idx[0])
        student = students_data[idx]
        ai_response = get_ai_response(student)
        student["comment"] = ai_response
        comment_text.delete(1.0, tk.END)
        comment_text.insert(tk.END, student["comment"])

    ttk.Button(input_frame, text="AI生成评语", command=ai_generate_comment).pack(pady=10)

    teacher_win.mainloop()

def show_main_window(prev_window=None):
    if prev_window:
        prev_window.destroy()

    main_win = tk.Tk()
    main_win.title("师生评语系统")
    main_win.geometry("500x450")
    main_win.resizable(False, False)

    ttk.Label(main_win, text="师生评语系统", font=("微软雅黑", 16, "bold")).pack(pady=30)

    ttk.Button(
        main_win,
        text="教师入口（点击进入评语管理）",
        command=lambda: show_teacher_window(main_win),
        width=35
    ).pack(pady=20)

    ttk.Button(
        main_win,
        text="学生入口（点击登录查看评语）",
        command=lambda: show_student_login_window(main_win),
        width=35
    ).pack(pady=20)

    main_win.mainloop()

if __name__ == "__main__":
    show_main_window()