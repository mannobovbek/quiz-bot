# BOT: Backendga ulash rejasi (kategoriya -> quiz -> submit -> ball)

## Hozirgi holat

- `bot/main.py` faqat /start va `quiz` so‘zi kelganda hardcoded poll yuboradi.

## Kerakli funksiya

1. Channel’dan o‘tgan userlarni tekshirish (`check_sub`)
2. Userni `Student` ga ro‘yxatdan o‘tkazish (name/email bo‘lsa)
3. Kategoriya ro‘yxatini olish: GET `${API_BASE}/categories`
4. Kategoriya tanlash: GET `${API_BASE}/quizzes?category_id=...`
5. Quiz bo‘yicha ketma-ket savollar (yoki bitta poll)
6. Javobni olish -> score hisoblash -> POST/PUT -> Student.score ga yozish

## Backendda etishmayotgan endpointlar

- quiz submit + student score yozish (hozir backend faqat quiz CRUD va analytics bor)

> Keyingi qadam: botni ulash uchun backendga `POST /quiz-attempt` yoki shunga o‘xshash endpoint qo‘shiladi.
