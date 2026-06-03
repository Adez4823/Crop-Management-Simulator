FROM python:3.14

WORKDIR /project

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv pip install --system .

COPY . .

CMD ["python", "src/src_backend/main.py"]