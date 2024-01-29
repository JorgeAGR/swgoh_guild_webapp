FROM python:3.11
WORKDIR /src
COPY ./requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
COPY ./swgoh_comlink_fetcher/ /src/swgoh_comlink_fetcher
EXPOSE 3201
CMD ["uvicorn", "swgoh_comlink_fetcher.main:app", "--host", "0.0.0.0", "--port", "3201"]