title tanglebox.ai
:start
C:\Users\Tangles\miniconda3\_conda run --name tanglebox
python server/main.py --model-name E:/models/vicuna-7b-v11 --temperature 0.5 --max-new-tokens 2048 --port 8080
pause
goto start