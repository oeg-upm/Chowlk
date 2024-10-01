FROM python:3.12.6

RUN mkdir -p /home/app/

COPY . /home/app

#WORKDIR /app

RUN pip install --no-cache-dir -r /home/app/requirements.txt

EXPOSE 5000

CMD ["python", "/home/app/entrypoint.py"]



