# ./tests/Dockerfile

FROM python:3.11
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 libpangocairo-1.0-0 libgtk-3-0 \
    libffi-dev wget curl unzip
WORKDIR /app/tests
COPY tests/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["pytest", "--junitxml=tests/reports/junit_report.xml", "--html=tests/reports/test_report.html", "--self-contained-html"]
