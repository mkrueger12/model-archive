FROM cgr.dev/chainguard/wolfi-base

ARG version=3.12

WORKDIR /app

COPY requirements.txt .

RUN apk upgrade --no-cache
RUN apk add --no-cache python-${version} py${version}-pip && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apk del py${version}-pip && \
    chown -R nonroot:nonroot /app

COPY . .

USER nonroot

EXPOSE 8501

# Use exec form of ENTRYPOINT for proper signal handling
ENTRYPOINT ["streamlit", "run", "main.py", "--browser.gatherUsageStats=false", "--server.port=8501", "--server.address=0.0.0.0"]


