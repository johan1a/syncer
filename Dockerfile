FROM python:3

WORKDIR /app

RUN mkdir -p /syncer/data

COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

EXPOSE 5000

ENTRYPOINT ["python"]
CMD [ "syncer.py" ]
