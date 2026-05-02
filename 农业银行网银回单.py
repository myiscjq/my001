import os
import re
import pdfplumber
import PyPDF2

os.chdir(os.path.dirname(__file__))
回单dict = {}
路径 = "农业银行回单.pdf"
with pdfplumber.open(路径) as pdf:
    for 页码, page in enumerate(pdf.pages):
        text = page.extract_tables()
        for outer in text:
            # 取出：最里层第一个值 → outer[0][0]
            first_value = outer[0][0]
            # 判断：如果这个值 不是空、不是None → 保留
            if first_value is not None and first_value.strip() != "":
                付款公司名称 = re.sub(r"\s+", "", outer[2][2])  # 删除所有空白
                收款公司名称 = re.sub(r"\s+", "", outer[2][5])
                付款公司账号 = re.sub(r"\s+", "", outer[1][2])
                收款公司账号 = re.sub(r"\s+", "", outer[1][5])
                # print(outer)
                # ===================== 过滤无效关键词 =====================
                过滤关键词 = [
                    "收入",
                    "支出",
                    "摘要",
                    "金额",
                    "应付",
                    "应收",
                    "税务",
                    "社保",
                    "手续费",
                ]
                if any(key in 付款公司名称 for key in 过滤关键词):
                    付款公司名称 = ""
                    付款公司账号 = ""
                if any(key in 收款公司名称 for key in 过滤关键词):
                    收款公司名称 = ""
                    收款公司账号 = ""
                # print("付款公司名称:", 付款公司名称, "收款公司名称:", 收款公司名称 ,'付款公司账号:', 付款公司账号, '收款公司账号:', 收款公司账号)
                # ===================== 提取金额（安全提取）=====================
                金额文本 = outer[4][2]
                金额匹配 = re.search(r"[\d,]+\.?\d*", 金额文本)
                if not 金额匹配:
                    continue  # 没取到金额，跳过
                金额 = float(金额匹配.group(0).replace(",", ""))
                # print("金额:", 金额)
                # ===================== 统计收入/支出凭证 =====================
                我方公司 = "吉安市钢铁有限责任公司"
                if 付款公司名称 == 我方公司 and 收款公司名称 == 我方公司:
                    key = "转户凭证-" + 收款公司名称
                elif 付款公司名称 == 我方公司:
                    key = "支出凭证-" + 收款公司名称
                elif 收款公司名称 == 我方公司:
                    key = "收入凭证-" + 付款公司名称
                else:
                    continue  # 不是我方收支，跳过
                # 存入字典统计
                if key not in 回单dict:
                    回单dict[key] = [[页码], 1, 金额]  # [页码列表, 张数, 累计金额]
                else:
                    回单dict[key][0].append(页码)
                    回单dict[key][1] += 1
                    回单dict[key][2] += 金额
print("统计结果：")
# print(回单dict)
