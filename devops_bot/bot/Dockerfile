FROM python:latest

COPY . /bot
WORKDIR /bot
RUN mkdir -p logs
RUN python3 -m pip install -r requirements.txt --no-cache-dir

CMD ["python", "bot.py"]
