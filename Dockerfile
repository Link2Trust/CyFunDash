# CyFun® 2025 Dashboard
FROM python:3.12-slim

WORKDIR /app

# Copy runtime files only (no Excel source, no dev tooling)
COPY server.py index.html summary.html disclaimer.html utils.js data.json scores.json link2trust.svg ./

EXPOSE 8088

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8088')"

CMD ["python3", "server.py"]
