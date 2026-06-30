FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libnss3 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxi6 \
        libxtst6 \
        libcups2 \
        libxrandr2 \
        libasound2 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        libgbm1 && \
    rm -rf /var/lib/apt/lists/*


# Copy and install Python dependencies
COPY requirements/core.txt ./requirements/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=300 -r requirements/core.txt

COPY requirements/integrations.txt ./requirements/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=300 -r requirements/integrations.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "synthetix_os.asgi:application", "--host", "0.0.0.0", "--port", "8000"]