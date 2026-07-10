# -*- coding: utf-8 -*-
"""
build_data.py — แปลงฐานข้อมูล Excel ของทีม content เป็น data.json ให้เว็บใช้
ติดตั้งก่อนใช้:  pip install pandas openpyxl
รัน:            py build_data.py [path ไฟล์ .xlsx]
ถ้าไม่ระบุ path จะใช้ codecoin_database.xlsx ในโฟลเดอร์เดียวกัน

โครงสร้าง Excel (หัวตารางจริงอยู่แถวที่ 2 — แถวแรกเป็นหมายเหตุ):
  spaces:    space_id, zone, name_th, price, rent_L0..rent_L3, upgrade_cost, content_th
  questions: question_id, space_id, level, question_th, choice_a..d, answer(a-d), time_limit
  events:    event_id, zone, mechanic, title_th, description_th, effect, weight
  bugjam:    bug_id, code_snippet, question_th, choice_a..c, answer(a-c), time_limit
"""
import json
import math
import sys

import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")

XLSX_FILE = sys.argv[1] if len(sys.argv) > 1 else "codecoin_database.xlsx"
OUT_FILE = "data.json"
ANSWER_INDEX = {"a": 0, "b": 1, "c": 2, "d": 3}


def cell(v, default=""):
    """NaN → ค่า default"""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return default
    return v


def as_int(v, default=0):
    v = cell(v, default)
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def choices_of(row, letters):
    """รวม choice_a..d เฉพาะช่องที่มีข้อมูล คืน (รายการตัวเลือก, ตำแหน่งใหม่ของแต่ละตัวอักษร)
    ตัวอย่าง: choice_b ว่าง → letter_index ของ 'c' จะเลื่อนมาเป็น 1 ให้เฉลยไม่เพี้ยน"""
    out, letter_index = [], {}
    for c in letters:
        v = str(cell(row.get(f"choice_{c}"))).strip()
        if v and v.lower() != "nan":
            letter_index[c] = len(out)
            out.append(v)
    return out, letter_index


def fix_newlines(s):
    """Excel บางเครื่องพิมพ์ \\n เป็นตัวอักษร — แปลงเป็นขึ้นบรรทัดจริง"""
    return str(s).replace("\\n", "\n")


def main():
    xl = pd.ExcelFile(XLSX_FILE)
    warns = []

    # ---------- spaces ----------
    df = xl.parse("spaces", header=1)
    spaces = {}
    for _, r in df.iterrows():
        sid = str(cell(r["space_id"])).strip()
        if not sid:
            continue
        spaces[sid] = {
            "zone": str(cell(r["zone"])).strip(),
            "name_th": str(cell(r["name_th"])).strip(),
            "price": as_int(r["price"]),
            "rent": [as_int(r[f"rent_L{i}"]) for i in range(4)],
            "upgrade_cost": as_int(r["upgrade_cost"]),
            "content_th": str(cell(r["content_th"])).strip(),
        }

    # ---------- questions ----------
    df = xl.parse("questions", header=1)
    questions = []
    for _, r in df.iterrows():
        qth = str(cell(r["question_th"])).strip()
        if not qth:
            continue
        ans = str(cell(r["answer"])).strip().lower()
        is_draft = qth.startswith("DRAFT") or str(cell(r["question_id"])).startswith("DRAFT")
        if not is_draft and ans not in ANSWER_INDEX:
            warns.append(f"questions: {cell(r['question_id'])} answer '{ans}' ไม่ใช่ a-d — ข้ามแถวนี้")
            continue
        sid = str(cell(r["space_id"])).strip()
        if not is_draft and sid not in spaces:
            warns.append(f"questions: {cell(r['question_id'])} อ้าง space_id '{sid}' ที่ไม่มีในชีต spaces")
        choices, letter_index = choices_of(r, "abcd")
        if not is_draft and ans not in letter_index:
            warns.append(f"questions: {cell(r['question_id'])} เฉลย '{ans}' ชี้ตัวเลือกที่ว่าง — ข้ามแถวนี้ "
                         f"(เช็คว่าเซลล์นั้นโดน Excel ตีความเป็นสูตรหรือไม่)")
            continue
        questions.append({
            "question_id": str(cell(r["question_id"])).strip(),
            "space_id": sid,
            "level": as_int(r["level"], 1),
            "question_th": qth,
            "choices": choices,
            "answer": letter_index.get(ans, 0),
            "time_limit": as_int(r["time_limit"]),
        })

    # ---------- events ----------
    df = xl.parse("events", header=1)
    events = []
    for _, r in df.iterrows():
        title = str(cell(r["title_th"])).strip()
        if not title:
            continue
        events.append({
            "event_id": str(cell(r["event_id"])).strip(),
            "zone": str(cell(r["zone"])).strip(),
            "mechanic": str(cell(r["mechanic"])).strip(),
            "weight": as_int(r["weight"], 1),
            "title_th": title,
            "description_th": str(cell(r["description_th"])).strip(),
            "effect": str(cell(r["effect"])).strip(),
        })

    # ---------- bugjam ----------
    df = xl.parse("bugjam", header=1)
    bugjam = []
    for _, r in df.iterrows():
        qth = str(cell(r["question_th"])).strip()
        if not qth:
            continue
        ans = str(cell(r["answer"])).strip().lower()
        choices, letter_index = choices_of(r, "abc")
        if ans not in letter_index:
            warns.append(f"bugjam: {cell(r['bug_id'])} เฉลย '{ans}' ชี้ตัวเลือกที่ว่าง — ข้ามแถวนี้")
            continue
        bugjam.append({
            "bug_id": str(cell(r["bug_id"])).strip(),
            "code": fix_newlines(cell(r["code_snippet"])),
            "question_th": qth,
            "choices": choices,
            "answer": letter_index[ans],
            "time_limit": as_int(r["time_limit"]),
        })

    data = {"spaces": spaces, "questions": questions, "events": events, "bugjam": bugjam}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] {OUT_FILE}: spaces {len(spaces)} | questions {len(questions)} "
          f"| events {len(events)} | bugjam {len(bugjam)}")
    zones = {}
    for e in events:
        zones[e["zone"]] = zones.get(e["zone"], 0) + 1
    print("     events ต่อโซน:", ", ".join(f"{z}={n}" for z, n in zones.items()))
    for w in warns:
        print("[!]", w)


if __name__ == "__main__":
    main()
