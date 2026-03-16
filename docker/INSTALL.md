# CyFun® 2025 CyberFundamentals Dashboard — Installation Guide

## Prerequisite

Install **Docker Desktop** for your operating system:
- Windows / macOS: https://www.docker.com/products/docker-desktop
- Linux: https://docs.docker.com/engine/install/

Make sure Docker Desktop is running before proceeding.

---

## First-time setup

1. Place the following files in the same folder on your computer:
   - `cyfundash.tar.gz`
   - `scores.json`

2. Open a terminal in that folder and load the image:

   ```
   docker load < cyfundash.tar.gz
   ```

3. Start the dashboard:

   ```
   docker run -d -p 8088:8088 -v ./scores.json:/app/scores.json --name cyfundash cyfundash-cyfundash
   ```

4. Open your browser and go to:

   **http://localhost:8088**

---

## Daily use

Start the dashboard:
```
docker start cyfundash
```

Stop the dashboard:
```
docker stop cyfundash
```

---

## Your assessment data

Your scores are saved automatically to `scores.json` in the same folder.
Back up this file regularly to preserve your assessment progress.

---

## Troubleshooting

**Page does not load** — make sure Docker Desktop is running, then retry `docker start cyfundash`.

**Port 8088 already in use** — change the port in the start command, e.g. `-p 9000:8088`, then open http://localhost:9000 instead.
