import re
from typing import Dict, List, Optional

DATE = r"(?:今天(?:下午|晚上)?|今晚|明天(?:上午|下午|晚上)?|后天|(?:本周|下周|周|星期)[一二三四五六日天]|(?:\d{4}年)?\d{1,2}月\d{1,2}日)"
CLOCK = r"(?:上午|下午|晚上)?(?:\d{1,2}:\d{2}|[一二两三四五六七八九十\d]{1,3}点(?:半|\d{1,2}分)?)"


def extract_time_info(text: str) -> Dict[str, Optional[str]]:
    expressions: List[str] = []
    pattern = rf"{DATE}(?:{CLOCK})?|{CLOCK}"
    for match in re.finditer(pattern, text):
        value = match.group(0)
        if value not in expressions:
            expressions.append(value)
    deadline: Optional[str] = None
    for value in expressions:
        tail = text[text.find(value) + len(value): text.find(value) + len(value) + 6]
        if re.search(r"之前|以前|前|截止|截至|最晚", tail) or re.search(r"截止|截至|最晚", text[:text.find(value) + 1]):
            deadline = value
            break
    if not deadline and expressions and re.search(r"提交|上传|报名截止|截止|截至|最晚", text):
        deadline = expressions[0]
    normal = next((x for x in expressions if x != deadline), None)
    return {"time": normal, "deadline": deadline, "time_expressions": expressions}

