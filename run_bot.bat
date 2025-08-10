@echo off
cd /d "c:\Users\Serg\Documents\python\my_ai_teacher 3"
set DATABASE_URL=sqlite+aiosqlite:///local_test.db
.\venv\Scripts\python.exe main.py
