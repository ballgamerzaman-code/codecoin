# CodeCoin — QR System

ระบบ QR ประกอบบอร์ดเกมเพื่อการศึกษา CodeCoin (base จาก Monopoly) — Static ทั้งหมด host บน GitHub Pages

**🌐 เว็บจริง:** https://ballgamerzaman-code.github.io/codecoin/
**📦 Repo:** https://github.com/ballgamerzaman-code/codecoin (push ขึ้น main แล้วเว็บอัปเดตเองใน ~1 นาที)

## ไฟล์ในโปรเจค

| ไฟล์ | หน้าที่ |
|---|---|
| `index.html` | ตัวแอป (SPA ไฟล์เดียว) — โหลดข้อมูลจาก `data.json` ตอนเปิดหน้า |
| `codecoin_database.xlsx` | **ต้นทางข้อมูลของทีม content** (4 ชีต: spaces/questions/events/bugjam) |
| `build_data.py` | แปลง Excel → `data.json` (รันทุกครั้งหลังทีม content แก้ Excel) |
| `data.json` | ฐานข้อมูลที่เว็บใช้จริง — **อย่าแก้มือ ให้แก้ Excel แล้วรัน build_data.py** |
| `gen_qr.py` | สคริปต์ gen QR ทั้งชุดเป็น PNG (โฟลเดอร์ `qr_output/`) |

## Routing

| URL | หน้า |
|---|---|
| ไม่มี `?space=` | เมนูทดสอบ (คลิกดูทุกช่องโดยไม่ต้องสแกน) |
| `?space=coding_02` | ช่องทรัพย์สิน: เนื้อหา → คำถาม L1 → ตอบถูกลด 20% |
| `?space=coding_02&upgrade=2` | อัปเกรดระดับชำนาญ (คำถาม L2) — `upgrade=3` = ผู้เชี่ยวชาญ |
| `?space=event_coding` | สุ่มเหตุการณ์โซน (coding/design/office/hardware) |
| `?space=bugjam` | โจทย์ debug จับเวลา ออกจาก "คุก" ฟรีเมื่อตอบถูก |

## การแก้ไขข้อมูล

- ทีม content แก้ `codecoin_database.xlsx` (หัวตารางจริงอยู่แถวที่ 2 — แถวแรกเป็นหมายเหตุ ห้ามลบ) แล้วรัน:

```bash
py build_data.py            # ได้ data.json ใหม่
py gen_qr.py                # ถ้าเพิ่ม/ลบช่อง ให้ gen QR ใหม่ด้วย
```

- ในชีต questions กรอก `answer` เป็นตัวอักษร a/b/c/d — สคริปต์แปลงเป็น index ให้เอง `time_limit` เว้นว่าง = ไม่จับเวลา
- แถวคำถามที่ `question_th` หรือ `question_id` ขึ้นต้นด้วย `DRAFT` จะถูกซ่อนอัตโนมัติ
- สคริปต์เตือนถ้า answer ไม่ใช่ a-d หรือ space_id อ้างถึงช่องที่ไม่มีจริง
- ถ้าโหลด `data.json` ไม่สำเร็จ แอปจะใช้ข้อมูลสำรองที่ฝังใน `index.html` และแสดงแถบเตือน
- จะย้ายไป Google Sheet ภายหลังได้โดยเปลี่ยน `CONFIG.data_url` ใน `index.html` ให้ชี้ URL Apps Script (doGet คืน JSON) หรือ opensheet.elk.sh — โครงสร้าง JSON ต้องมี key ครบ 4 ก้อนเหมือน `data.json`
- เก็บสถิติการตอบ (optional): ใส่ URL Apps Script ใน `CONFIG.log_url` — แอปจะ POST `{kind, space_id, level, correct, ts}` ทุกครั้งที่ตอบ

## สร้าง QR

```bash
pip install "qrcode[pil]"
# แก้ BASE_URL บนหัวไฟล์ gen_qr.py เป็น URL จริงก่อน
python gen_qr.py
```

ได้ PNG error correction ระดับ H ตั้งชื่อตาม space_id ขนาดพิมพ์คมชัดที่ ~3×3 ซม. (300 DPI)

## ทดสอบในเครื่อง

เปิดผ่าน local server (เพราะ `fetch` data.json ไม่ทำงานบน `file://`):

```bash
python -m http.server 8000
# แล้วเปิด http://localhost:8000
```

## กติกาที่ห้ามเปลี่ยน

- Naming: space_id = `{zone}_{ลำดับ 2 หลัก}` (ตัวพิมพ์เล็ก + underscore), question_id = `{space_id}_L{ระดับ}_{ลำดับ}`
- รูปแบบ effect: `+1500` / `-800` / `skip:1` / `all:-500` / `collect:200` / `bet:1000:x3|safe:+300` / `quiz:{question_id}:+500`
- UI ภาษาไทย + ธีมสี PCB เดิม
