# 🚀 StudyBuddy AI Project Context

## 📌 Proje Amacı
AI destekli çalışma planı oluşturan ve task list ile entegre çalışan web uygulaması.

## 🧠 Backend
- FastAPI
- CrewAI kullanılıyor
- 2 agent var:
  - planner
  - breakdown

## 🔥 Özellikler
- AI study planner
- JSON format output
- Gün bazlı plan
- Task list sistemi (frontend)
- LocalStorage kullanılıyor

## 🌍 Dil Sistemi
- AI kullanıcı dilini otomatik algılar
- Aynı dilde cevap verir
- Dil mix edilmez

## ⚠️ Kritik Kurallar
- AI sadece JSON döner
- Frontend JSON parse eder
- Backend OpenAI API kullanır (.env gerekir)

## 🔧 Endpoint
POST /plan-study

## 🚧 Yapılacaklar
- AI plan → task list entegrasyonu
- kullanıcıya "listeye ekle" butonu
- belki auth sistemi

## 💡 Not
Backend çalışmazsa:
→ %90 API key sorunu