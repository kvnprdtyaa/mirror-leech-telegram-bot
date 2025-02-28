FROM arakurumi/mltb:latest

WORKDIR /app

RUN chmod -R 777 /app

COPY . .

RUN pip install --break-system-packages --no-cache-dir --requirement requirements.txt

CMD ["bash", "start.sh"]