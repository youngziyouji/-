import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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
    {"id": "2024001", "name": "张三", "pwd": "001", "comment": "", "group_id": None},
    {"id": "2024002", "name": "李四", "pwd": "002", "comment": "", "group_id": None},
    {"id": "2024003", "name": "王五", "pwd": "003", "comment": "", "group_id": None},
    {"id": "2024004", "name": "赵六", "pwd": "004", "comment": "", "group_id": None},
    {"id": "2024005", "name": "孙七", "pwd": "005", "comment": "", "group_id": None},
    {"id": "2024006", "name": "周八", "pwd": "006", "comment": "", "group_id": None},
    {"id": "2024007", "name": "吴九", "pwd": "007", "comment": "", "group_id": None},
    {"id": "2024008", "name": "郑十", "pwd": "008", "comment": "", "group_id": None},
    {"id": "2024009", "name": "钱十一", "pwd": "009", "comment": "", "group_id": None},
    {"id": "2024010", "name": "冯十二", "pwd": "010", "comment": "", "group_id": None}
]

# 学习小组数据
groups_data = []

# 为每个学生随机生成多维度学习数据，包括学科成绩
def generate_student_data():
    subjects = ["语文", "数学", "英语"]
    for student in students_data:
        # 学科成绩 (0-100分)
        student['chinese'] = np.random.randint(60, 100)
        student['math'] = np.random.randint(60, 100)
        student['english'] = np.random.randint(60, 100)
        
        # 找出优势学科
        scores = {
            "语文": student['chinese'],
            "数学": student['math'],
            "英语": student['english']
        }
        student['strong_subject'] = max(scores, key=scores.get)
        student['weak_subject'] = min(scores, key=scores.get)
        
        # 原有数据
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
        class_list = ["文科", "理科"]
        student['class'] = class_list[np.random.randint(0, 2)]

# 自动分组函数：根据学科优势互补原则
def auto_group_students(group_size=3):
    # 清空现有分组
    global groups_data
    groups_data = []
    for student in students_data:
        student['group_id'] = None
    
    # 复制学生列表用于分组
    remaining_students = students_data.copy()
    group_id = 1
    
    # 按学科优势互补原则分组
    while remaining_students:
        group = []
        subject_covered = set()
        
        # 尝试为每组添加不同优势学科的学生
        while len(group) < group_size and remaining_students:
            # 寻找能补充新学科的学生
            found = False
            for i, student in enumerate(remaining_students):
                if student['strong_subject'] not in subject_covered:
                    group.append(student)
                    subject_covered.add(student['strong_subject'])
                    del remaining_students[i]
                    found = True
                    break
            
            # 如果找不到新学科的学生，就添加任意剩余学生
            if not found:
                student = remaining_students.pop(0)
                group.append(student)
        
        # 为组内学生分配组ID
        for student in group:
            student['group_id'] = group_id
        
        # 添加组信息
        groups_data.append({
            "group_id": group_id,
            "members": [{"id": s["id"], "name": s["name"], "strong_subject": s["strong_subject"]} for s in group]
        })
        
        group_id += 1
    
    return groups_data

# 手动调整学生分组
def adjust_group(student_id, new_group_id):
    for student in students_data:
        if student["id"] == student_id:
            student["group_id"] = new_group_id
            break
    
    # 更新组数据
    update_groups_data()

# 更新组数据
def update_groups_data():
    global groups_data
    groups_data = []
    group_dict = {}
    
    # 按group_id分组
    for student in students_data:
        gid = student["group_id"]
        if gid not in group_dict:
            group_dict[gid] = []
        group_dict[gid].append(student)
    
    # 转换为组列表
    for gid, members in group_dict.items():
        if gid is not None:
            groups_data.append({
                "group_id": gid,
                "members": [{"id": s["id"], "name": s["name"], "strong_subject": s["strong_subject"]} for s in members]
            })
    
    # 按组ID排序
    groups_data.sort(key=lambda x: x["group_id"])

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

# 显示学习小组管理窗口
def show_group_management_window(prev_window):
    prev_window.destroy()
    
    group_win = tk.Tk()
    group_win.title("学习小组管理")
    group_win.geometry("800x600")
    
    # 返回按钮
    ttk.Button(
        group_win,
        text="返回教师界面",
        command=lambda: show_teacher_window(group_win)
    ).pack(anchor=tk.W, padx=20, pady=10)
    
    # 分组控制区
    control_frame = ttk.Frame(group_win)
    control_frame.pack(fill=tk.X, padx=20, pady=10)
    
    ttk.Button(
        control_frame,
        text="自动分组",
        command=lambda: [auto_group_students(), refresh_group_display()]
    ).pack(side=tk.LEFT, padx=5)
    
    ttk.Label(control_frame, text="组大小:").pack(side=tk.LEFT, padx=5)
    group_size_var = tk.StringVar(value="3")
    ttk.Combobox(control_frame, textvariable=group_size_var, values=["2", "3", "4", "5"]).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(
        control_frame,
        text="按当前组大小分组",
        command=lambda: [auto_group_students(int(group_size_var.get())), refresh_group_display()]
    ).pack(side=tk.LEFT, padx=5)
    
    # 分组显示区
    groups_frame = ttk.Frame(group_win)
    groups_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # 创建一个Canvas用于滚动
    canvas = tk.Canvas(groups_frame)
    scrollbar = ttk.Scrollbar(groups_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # 刷新分组显示
    def refresh_group_display():
        # 清除现有内容
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        # 如果没有分组，提示用户
        if not groups_data:
            ttk.Label(scrollable_frame, text="暂无分组，请点击自动分组按钮创建分组", font=("微软雅黑", 10)).pack(pady=20)
            return
        
        # 显示每个组
        for group in groups_data:
            group_frame = ttk.LabelFrame(scrollable_frame, text=f"学习小组 {group['group_id']}")
            group_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # 显示组内成员
            for member in group['members']:
                # 查找完整的学生信息
                student_info = next(s for s in students_data if s['id'] == member['id'])
                
                member_frame = ttk.Frame(group_frame)
                member_frame.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(member_frame, text=f"{member['name']} ({member['id']})", width=20).pack(side=tk.LEFT)
                ttk.Label(member_frame, text=f"优势学科: {member['strong_subject']}", width=15).pack(side=tk.LEFT)
                ttk.Label(member_frame, text=f"弱势学科: {student_info['weak_subject']}", width=15).pack(side=tk.LEFT)
                
                ttk.Button(
                    member_frame,
                    text="调整分组",
                    command=lambda sid=member['id']: adjust_student_group(sid)
                ).pack(side=tk.RIGHT, padx=5)
            
            # 显示组内互助关系
            ttk.Label(group_frame, text="组内互助建议:", font=("微软雅黑", 9, "bold")).pack(anchor=tk.W, padx=10, pady=5)
            suggestions = get_group_cooperation_suggestions(group)
            ttk.Label(group_frame, text=suggestions, wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=5)
    
    # 调整学生分组
    def adjust_student_group(student_id):
        student = next(s for s in students_data if s['id'] == student_id)
        current_group = student['group_id']
        
        new_group = simpledialog.askinteger(
            "调整分组",
            f"请输入{student['name']}的新组号 (当前: {current_group})",
            minvalue=1,
            maxvalue=len(groups_data) + 1
        )
        
        if new_group is not None:
            adjust_group(student_id, new_group)
            refresh_group_display()
    
    # 获取组内合作建议
    def get_group_cooperation_suggestions(group):
        suggestions = []
        members = group['members']
        
        # 为每个成员找到可以帮助他的人
        for member in members:
            student = next(s for s in students_data if s['id'] == member['id'])
            weak_subj = student['weak_subject']
            
            # 寻找擅长该弱势学科的组内成员
            helpers = [m for m in members if m['id'] != member['id'] and m['strong_subject'] == weak_subj]
            
            if helpers:
                helper_names = ", ".join([h['name'] for h in helpers])
                suggestions.append(f"{member['name']}在{weak_subj}方面可以向{helper_names}请教")
        
        if not suggestions:
            return "组内成员可以互相交流学习经验，共同进步。"
        
        return "; ".join(suggestions) + "。"
    
    # 初始刷新显示
    refresh_group_display()
    
    group_win.mainloop()

def show_teacher_window(prev_window):
    prev_window.destroy()

    teacher_win = tk.Tk()
    teacher_win.title("教师 - 学生评语管理")
    teacher_win.geometry("900x600")

    # 顶部按钮区
    top_frame = ttk.Frame(teacher_win)
    top_frame.pack(fill=tk.X, padx=20, pady=10)
    
    ttk.Button(
        top_frame,
        text="返回主界面",
        command=lambda: show_main_window(teacher_win)
    ).pack(anchor=tk.W, side=tk.LEFT)
    
    ttk.Button(
        top_frame,
        text="学习小组管理",
        command=lambda: show_group_management_window(teacher_win)
    ).pack(anchor=tk.W, side=tk.LEFT, padx=10)

    ttk.Label(teacher_win, text="学生列表", font=("微软雅黑", 12)).pack(pady=5)
    student_tree = ttk.Treeview(
        teacher_win, columns=("id", "name", "class", "strong_subject", "group"), show="headings", selectmode="browse"
    )
    student_tree.heading("id", text="学号")
    student_tree.heading("name", text="姓名")
    student_tree.heading("class", text="班级")
    student_tree.heading("strong_subject", text="优势学科")
    student_tree.heading("group", text="所属小组")
    
    student_tree.column("id", width=100, anchor=tk.CENTER)
    student_tree.column("name", width=80, anchor=tk.CENTER)
    student_tree.column("class", width=80, anchor=tk.CENTER)
    student_tree.column("strong_subject", width=100, anchor=tk.CENTER)
    student_tree.column("group", width=80, anchor=tk.CENTER)
    
    for idx, student in enumerate(students_data):
        group_id = student["group_id"] if student["group_id"] is not None else "未分组"
        student_tree.insert("", tk.END, iid=idx, values=(
            student["id"], 
            student["name"],
            student["class"],
            student["strong_subject"],
            group_id
        ))
    
    student_tree.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=5)

    input_frame = ttk.Frame(teacher_win)
    input_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=5)

    ttk.Label(input_frame, text="评语编辑", font=("微软雅黑", 12)).pack(pady=10)
    comment_text = tk.Text(input_frame, width=50, height=20, wrap=tk.WORD)
    comment_text.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # 学生详细信息
    details_frame = ttk.LabelFrame(input_frame, text="学生学科信息")
    details_frame.pack(fill=tk.X, pady=10)
    
    chinese_var = tk.StringVar()
    math_var = tk.StringVar()
    english_var = tk.StringVar()
    strong_subj_var = tk.StringVar()
    weak_subj_var = tk.StringVar()
    
    ttk.Label(details_frame, text="语文:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Label(details_frame, textvariable=chinese_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
    
    ttk.Label(details_frame, text="数学:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
    ttk.Label(details_frame, textvariable=math_var).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
    
    ttk.Label(details_frame, text="英语:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Label(details_frame, textvariable=english_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
    
    ttk.Label(details_frame, text="优势学科:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
    ttk.Label(details_frame, textvariable=strong_subj_var).grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
    
    ttk.Label(details_frame, text="弱势学科:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Label(details_frame, textvariable=weak_subj_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    def load_comment(event):
        selected_idx = student_tree.selection()
        if selected_idx:
            idx = int(selected_idx[0])
            student = students_data[idx]
            
            # 加载评语
            comment_text.delete(1.0, tk.END)
            comment_text.insert(tk.END, student["comment"])
            
            # 加载学科信息
            chinese_var.set(f"{student['chinese']}分")
            math_var.set(f"{student['math']}分")
            english_var.set(f"{student['english']}分")
            strong_subj_var.set(student['strong_subject'])
            weak_subj_var.set(student['weak_subject'])

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
    
    def save_comment():
        selected_idx = student_tree.selection()
        if not selected_idx:
            messagebox.showwarning("提示", "请先选中一名学生！")
            return
        idx = int(selected_idx[0])
        students_data[idx]["comment"] = comment_text.get(1.0, tk.END).strip()
        messagebox.showinfo("提示", "评语已保存！")

    button_frame = ttk.Frame(input_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(button_frame, text="AI生成评语", command=ai_generate_comment).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="保存评语", command=save_comment).pack(side=tk.LEFT, padx=5)

    teacher_win.mainloop()

def show_student_login_window(prev_window):
    prev_window.destroy()
    
    login_win = tk.Tk()
    login_win.title("学生登录")
    login_win.geometry("400x300")
    
    ttk.Label(login_win, text="学生登录", font=("微软雅黑", 16)).pack(pady=30)
    
    frame = ttk.Frame(login_win)
    frame.pack(pady=20)
    
    ttk.Label(frame, text="学号:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)
    id_entry = ttk.Entry(frame, width=20)
    id_entry.grid(row=0, column=1, padx=10, pady=10)
    
    ttk.Label(frame, text="密码:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
    pwd_entry = ttk.Entry(frame, width=20, show="*")
    pwd_entry.grid(row=1, column=1, padx=10, pady=10)
    
    def login():
        student_id = id_entry.get()
        password = pwd_entry.get()
        
        # 查找学生
        for student in students_data:
            if student["id"] == student_id and student["pwd"] == password:
                show_student_window(login_win, student)
                return
        
        messagebox.showerror("错误", "学号或密码不正确！")
    
    ttk.Button(login_win, text="登录", command=login).pack(pady=10)
    ttk.Button(login_win, text="返回主界面", command=lambda: show_main_window(login_win)).pack(pady=10)
    
    login_win.mainloop()

def show_student_window(prev_window, student):
    prev_window.destroy()
    
    student_win = tk.Tk()
    student_win.title(f"{student['name']} - 学生界面")
    student_win.geometry("600x500")
    
    ttk.Button(
        student_win,
        text="退出登录",
        command=lambda: show_main_window(student_win)
    ).pack(anchor=tk.W, padx=20, pady=10)
    
    # 学生信息
    info_frame = ttk.LabelFrame(student_win, text="个人信息")
    info_frame.pack(fill=tk.X, padx=20, pady=10)
    
    ttk.Label(info_frame, text=f"学号: {student['id']}", width=20).grid(row=0, column=0, padx=10, pady=5)
    ttk.Label(info_frame, text=f"姓名: {student['name']}", width=20).grid(row=0, column=1, padx=10, pady=5)
    ttk.Label(info_frame, text=f"班级: {student['class']}", width=20).grid(row=0, column=2, padx=10, pady=5)
    
    # 学科信息
    subject_frame = ttk.LabelFrame(student_win, text="学科情况")
    subject_frame.pack(fill=tk.X, padx=20, pady=10)
    
    ttk.Label(subject_frame, text=f"语文: {student['chinese']}分", width=15).grid(row=0, column=0, padx=10, pady=5)
    ttk.Label(subject_frame, text=f"数学: {student['math']}分", width=15).grid(row=0, column=1, padx=10, pady=5)
    ttk.Label(subject_frame, text=f"英语: {student['english']}分", width=15).grid(row=0, column=2, padx=10, pady=5)
    ttk.Label(subject_frame, text=f"优势学科: {student['strong_subject']}", width=20).grid(row=0, column=3, padx=10, pady=5)
    
    # 学习小组信息
    group_frame = ttk.LabelFrame(student_win, text="学习小组信息")
    group_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    if student['group_id'] is not None and groups_data:
        group = next((g for g in groups_data if g['group_id'] == student['group_id']), None)
        
        if group:
            ttk.Label(group_frame, text=f"你属于 学习小组 {group['group_id']}", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, padx=10, pady=5)
            
            ttk.Label(group_frame, text="组内成员:", font=("微软雅黑", 10)).pack(anchor=tk.W, padx=10, pady=5)
            for member in group['members']:
                if member['id'] == student['id']:
                    ttk.Label(group_frame, text=f"- {member['name']} (你) - 优势学科: {member['strong_subject']}").pack(anchor=tk.W, padx=20)
                else:
                    ttk.Label(group_frame, text=f"- {member['name']} - 优势学科: {member['strong_subject']}").pack(anchor=tk.W, padx=20)
            
            # 互助建议
            ttk.Label(group_frame, text="学习互助建议:", font=("微软雅黑", 10)).pack(anchor=tk.W, padx=10, pady=10)
            suggestions = []
            # 找到可以帮助我的人
            helpers = [m for m in group['members'] if m['id'] != student['id'] and m['strong_subject'] == student['weak_subject']]
            if helpers:
                helper_names = ", ".join([h['name'] for h in helpers])
                suggestions.append(f"你可以向{helper_names}请教{student['weak_subject']}方面的问题")
            
            # 找到我可以帮助的人
            for member in group['members']:
                if member['id'] != student['id'] and member['strong_subject'] != student['strong_subject'] and student['strong_subject'] == next(s for s in students_data if s['id'] == member['id'])['weak_subject']:
                    suggestions.append(f"你可以帮助{member['name']}学习{student['strong_subject']}")
            
            if not suggestions:
                ttk.Label(group_frame, text="组内成员可以互相交流学习经验，共同进步。", wraplength=500).pack(anchor=tk.W, padx=20)
            else:
                for s in suggestions:
                    ttk.Label(group_frame, text=f"- {s}", wraplength=500).pack(anchor=tk.W, padx=20)
        else:
            ttk.Label(group_frame, text="暂无小组信息").pack(pady=10)
    else:
        ttk.Label(group_frame, text="尚未分配学习小组").pack(pady=10)
    
    # 教师评语
    comment_frame = ttk.LabelFrame(student_win, text="教师评语")
    comment_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    if student['comment']:
        comment_text = tk.Text(comment_frame, wrap=tk.WORD, state=tk.DISABLED)
        comment_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        comment_text.config(state=tk.NORMAL)
        comment_text.insert(tk.END, student['comment'])
        comment_text.config(state=tk.DISABLED)
    else:
        ttk.Label(comment_frame, text="教师尚未添加评语").pack(pady=20)
    
    student_win.mainloop()

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
    generate_student_data()
    show_main_window()
