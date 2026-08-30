import re
from typing import Dict, Optional

from src.time_parser import extract_time_info

PLATFORMS = ("学习通", "雨课堂", "钉钉", "腾讯会议", "微信群", "邮箱", "教务系统", "网站", "QQ群")
ACTIONS = ("提交", "上传", "参加", "报名", "签到", "填写", "下载", "到场", "完成", "修改", "考试", "开会", "上课", "答辩", "领取")


class InformationExtractor:
    """可替换的混合抽取接口；第一版以语义分类结果为入口、规则完成槽位抽取。"""

    def extract(self, text: str) -> Dict[str, Optional[str]]:
        time_info = extract_time_info(text)
        location_match = re.search(r"(?:综合楼|研教楼|机械馆|教学楼|实验楼)[A-Za-z]?\d{2,4}|[A-Za-z]区\d{2,4}|图书馆|体育馆|实验室|线上|腾讯会议", text)
        platform = next((word for word in PLATFORMS if word in text), None)
        action = next((word for word in ACTIONS if word in text), None)
        person_match = re.search(r"(?:请|通知)([\u4e00-\u9fa5]{2,12}(?:同学|老师|人员))", text)
        return {"event": self._event(text, action), "time": time_info["time"],
                "deadline": time_info["deadline"],
                "location": location_match.group(0) if location_match else None,
                "person": person_match.group(1) if person_match else None,
                "platform": platform, "action": action,
                "requirement": self._requirement(text)}

    @staticmethod
    def _event(text: str, action: Optional[str]) -> str:
        patterns = [r"([\u4e00-\u9fa5A-Za-z0-9]{2,12}(?:实验报告|报告))", r"([\u4e00-\u9fa5A-Za-z0-9]{2,12}报名)",
                    r"([\u4e00-\u9fa5A-Za-z0-9]{2,12}(?:答疑|培训|答辩|考试|实验|会议|组会|课程))"]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).lstrip("将在于请需各位同学")
                if "报告" in name and action in ("提交", "上传"):
                    return name + "提交"
                return name
        core = re.sub(r"今天|明天|后天|本周|下周|上午|下午|晚上|\d{1,2}:\d{2}|[，。]", "", text)
        return core[:16] or "重要事项"

    @staticmethod
    def _requirement(text: str) -> Optional[str]:
        match = re.search(r"(?:请|需|须|务必|必须)(.+)", text)
        return match.group(1).strip("。") if match else None

