FROM python:3.12-slim

WORKDIR /api
COPY . .

ENV TZ=America/Sao_Paulo

RUN python -m pip install -r requirements.txt
EXPOSE 3199

CMD [ "gunicorn", "gallery_server.asgi:application", "-k", "uvicorn_worker.UvicornWorker", "-b", "0.0.0.0:3199" ]
# CMD [ "gunicorn", "gallery_server.asgi:application", "-k", "uvicorn_worker.UvicornWorker", "-b", "unix:/api/sockets/gallery_server.sock" ]