FROM python:3.12-slim

WORKDIR /app

# System deps for scipy/numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer cache)
COPY web/requirements.txt /app/web/requirements.txt
RUN pip install --no-cache-dir -r web/requirements.txt

# Copy project (excluding heavy local-model artifacts)
COPY agents/       /app/agents/
COPY web/          /app/web/
COPY IG_inquiry.py        /app/
COPY IG_catalog.json      /app/
COPY IG_promotions.json   /app/
COPY IG_primitive_map.py  /app/
COPY framework/           /app/framework/

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "web.api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
