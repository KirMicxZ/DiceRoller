import random
import re

def solve_expression(expression):
    # จัด Format: ตัวเล็ก, ลบช่องว่าง
    expression = expression.lower().replace(" ", "")
    # แปลงสัญลักษณ์คูณรูปแบบ '2x3' หรือ '2x(3+1)' ให้เป็น '*' แต่ไม่แตะคำว่า 'max'/'min'
    expression = re.sub(r'(?<=[0-9)])x(?=[0-9(])', '*', expression)

    # แปลง / เป็น // (หารปัดเศษทิ้งเสมอ)
    expression = expression.replace("/", "//")

    # ก่อนแทนค่า dice: ถ้าใช้ max(...) หรือ min(...) แบบใส่ arg เดียว
    # เช่น max(2d6) หรือ min(1d8+2) ให้ขยายเป็น max(expr, expr)
    # เพื่อให้การเขียนแบบ "max(2d6)+2" หมายถึง ทอย 2d6 สองครั้งแล้วเอาค่าสูงสุด
    # รองรับรูปแบบสั้น ๆ ที่มีตัวคูณนำหน้าฟังก์ชัน เช่น `3max(...)` หรือ `2min(...)`
    # ความหมาย: ทอย/คำนวณภายในวงเล็บ N ครั้ง แล้วเอา max/min ของผลลัพธ์ทั้งหมด
    def _expand_repeats(expr, limit=50):
        pattern = re.compile(r'(?<!\w)(\d+)(max|min)\(')
        i = 0
        while True:
            m = pattern.search(expr, i)
            if not m:
                break
            count = int(m.group(1))
            func = m.group(2)
            if count < 1:
                count = 1
            if count > limit:
                count = limit
            start = m.end() - 1  # index of '('
            # find matching closing parenthesis
            depth = 0
            j = start
            while j < len(expr):
                if expr[j] == '(':
                    depth += 1
                elif expr[j] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if depth != 0:
                # ไม่พบวงเล็บปิดที่ตรงกัน — ข้ามไป
                i = m.end()
                continue
            inner = expr[start+1:j]
            replacement = f"{func}({','.join([inner]*count)})"
            expr = expr[:m.start()] + replacement + expr[j+1:]
            i = m.start() + len(replacement)
        return expr

    expression = _expand_repeats(expression)

    # ขยายกรณี max(expr) หรือ min(expr) ที่มี arg เดียว ให้เป็นสอง arg
    expression = re.sub(r'\bmax\(\s*([^,()]+?)\s*\)', r'max(\1,\1)', expression)
    expression = re.sub(r'\bmin\(\s*([^,()]+?)\s*\)', r'min(\1,\1)', expression)

    roll_log = []

    # ฟังก์ชัน Callback เมื่อเจอ Dice (เช่น 2d6)
    def roll_replacer(match):
        text = match.group(0)
        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))

        rolls = [random.randint(1, sides) for _ in range(count)]
        total_sub = sum(rolls)

        roll_log.append(f"{text}{rolls}") # เก็บ Log เช่น 2d6[3, 5]
        return str(total_sub)

    try:
        # 1. Regex หา pattern ลูกเต๋า (XdY) แล้วแทนค่าด้วยผลรวมตัวเลข
        processed_expr = re.sub(r'(\d*)d(\d+)', roll_replacer, expression)

        # 2. ความปลอดภัย: อนุญาตเฉพาะตัวเลข, Math, และฟังก์ชัน max/min
        allowed_chars = set("0123456789+-*/()maxin,")
        if not set(processed_expr).issubset(allowed_chars):
             return None, "Error: พบตัวอักษรที่ไม่รองรับ", None

        # 3. คำนวณผลลัพธ์ (รองรับ max(a,b) และ min(a,b) ได้เลยเพราะเป็น built-in python)
        final_result = int(eval(processed_expr))

        return final_result, processed_expr, " | ".join(roll_log)

    except Exception as e:
        # ส่งข้อความ error กลับเพื่อช่วย debug ถ้าจำเป็น
        return None, f"Error: {e} | Expr: {processed_expr}", None
