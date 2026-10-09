# CyFun® 2025 Dashboard
FROM python:3.12-slim

WORKDIR /app

# Copy runtime files only (no Excel source, no dev tooling)
COPY server.py index.html summary.html disclaimer.html utils.js data.json scores.json link2trust.svg ./

# Listen on all interfaces inside the container (server.py defaults to 127.0.0.1)
ENV HOST=0.0.0.0 PORT=8088

EXPOSE 8088

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8088')"

CMD ["python3", "server.py"]
