@echo off
start cmd /k "npm run dev"
timeout /t 2
start cmd /k "cd server && python app.py"
timeout /t 2
start cmd /k "cd server && cd groq_hr && python app_similiar_copy.py"
