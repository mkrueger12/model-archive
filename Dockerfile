FROM cgr.dev/chainguard/python:latest-dev AS builder

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/nonroot/venv/bin:$PATH"

WORKDIR /home/nonroot/app
RUN python -m venv /home/nonroot/venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM cgr.dev/chainguard/python:latest

WORKDIR /home/nonroot/app
ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/nonroot/venv/bin:$PATH"

# Expose the port Streamlit runs on
EXPOSE 8501

COPY --from=builder /home/nonroot/venv /home/nonroot/venv
COPY . /home/nonroot/app/

ENTRYPOINT [ "/home/nonroot/venv/bin/streamlit", "run", "/home/nonroot/app/main.py" ]
