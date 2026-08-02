FROM python:3.9

RUN mkdir -p home/chat_app/

COPY . home/chat_app/

WORKDIR /home/chat_app

RUN pip install -r requirements.txt

EXPOSE 8000
EXPOSE 8001

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]