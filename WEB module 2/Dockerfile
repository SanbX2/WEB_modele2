FROM python:3.11

ENV ASSISTANT /app

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN pip install "poetry==1.8.3"

COPY . /app

CMD ["poetry", "run", "python", "task_2.py"]