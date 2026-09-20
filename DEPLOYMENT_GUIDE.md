# 🚀 Free Cloud Deployment Guide: Gold Analytics & AI Forecasting Platform

This guide walks you through deploying your **Django + AI Gold Forecasting Platform** online completely **free of cost** using **Render.com** (Recommended), **PythonAnywhere**, or **Railway**.

---

## 🌟 Method 1: Render.com (Recommended — 100% Free Tier)

Render offers a free Python Web Service, free PostgreSQL database, automated Git deployments, and free automatic SSL/HTTPS certificates.

### Step 1: Push Your Code to GitHub
1. Open terminal/PowerShell in your project directory:
   ```bash
   git add .
   git commit -m "Configure production deployment for Render"
   git push origin main
   ```
   *(If you haven't initialized a repository yet: create a new GitHub repo at [github.com/new](https://github.com/new), then run `git init`, `git branch -M main`, `git remote add origin <your-repo-url>`, and `git push -u origin main`)*

---

### Step 2: Create Free Account on Render
1. Go to [https://render.com](https://render.com) and click **Sign Up** (use your GitHub account for instant 1-click authorization).

---

### Step 3: Deploy via Blueprint (Fastest — 1 Click)
1. On your Render dashboard, click **New +** and select **Blueprint**.
2. Select your GitHub repository (`Gold_analytics`).
3. Render will automatically detect [`render.yaml`](file:///d:/Hari_files/FirstMoneyGold/software_apps/Gold_analytics/render.yaml) and configure:
   - **Web Service**: Python environment running `gunicorn config.wsgi:application`
   - **PostgreSQL Database**: Free managed PostgreSQL instance
4. Click **Apply**.
5. Render will automatically run [`build.sh`](file:///d:/Hari_files/FirstMoneyGold/software_apps/Gold_analytics/build.sh), install dependencies, collect static files, run database migrations, and seed initial gold rates.

---

### Step 4 (Alternative): Manual Web Service Setup on Render
If you prefer creating the Web Service manually:
1. Click **New +** ➔ **Web Service**.
2. Connect your GitHub repository.
3. Fill in the configuration:
   - **Name**: `gold-analytics-ai`
   - **Runtime**: `Python 3`
   - **Branch**: `main`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application`
   - **Plan**: `Free`
4. Under **Advanced** ➔ **Environment Variables**, add:
   | Key | Value |
   | :--- | :--- |
   | `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
   | `PYTHON_VERSION` | `3.12.0` |
   | `DJANGO_SECRET_KEY` | *(Generate any random string or click generate)* |
   | `DEBUG` | `False` |
   | `DATABASE_URL` | *(Optional: Leave blank to use SQLite, or paste Render PostgreSQL Internal URL)* |
5. Click **Create Web Service**.

---

### Step 5: Create Production Admin / Superuser
Once the build completes on Render:
1. Go to your Web Service dashboard on Render.
2. Click on the **Shell** tab on the left menu.
3. Run:
   ```bash
   python manage.py createsuperuser --settings=config.settings.production
   ```
4. Enter your desired username, email, and password.
5. You can now log in at `https://<your-subdomain>.onrender.com/admin/` or access the main terminal at `https://<your-subdomain>.onrender.com/`.

---

## 🐍 Method 2: PythonAnywhere (Alternative Free Option)

PythonAnywhere provides free beginner hosting for Python/Django applications.

1. Sign up at [https://www.pythonanywhere.com](https://www.pythonanywhere.com).
2. Open a **Bash Console** on PythonAnywhere and clone your repo:
   ```bash
   git clone https://github.com/<your-username>/Gold_analytics.git
   cd Gold_analytics
   ```
3. Create a virtualenv & install dependencies:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 gold-venv
   pip install -r requirements.txt
   ```
4. Configure the **Web** tab:
   - Source code: `/home/<username>/Gold_analytics`
   - Virtualenv: `/home/<username>/.virtualenvs/gold-venv`
   - WSGI configuration file: Edit to point to `config.wsgi.application` and set `DJANGO_SETTINGS_MODULE = 'config.settings.production'`.
5. Run migrations & collectstatic in console:
   ```bash
   python manage.py migrate --settings=config.settings.production
   python manage.py collectstatic --no-input --settings=config.settings.production
   ```
6. Click **Reload <username>.pythonanywhere.com**.

---

## 🛠️ Included Production Files Overview

| File | Purpose |
| :--- | :--- |
| [`render.yaml`](file:///d:/Hari_files/FirstMoneyGold/software_apps/Gold_analytics/render.yaml) | Infrastructure-as-code for 1-click Render blueprint deployments. |
| [`build.sh`](file:///d:/Hari_files/FirstMoneyGold/software_apps/Gold_analytics/build.sh) | Automated build script that installs dependencies, compiles static WhiteNoise assets, migrates DB schema, and seeds default physical gold catalogues. |
| [`Procfile`](file:///d:/Hari_files/FirstMoneyGold/software_apps/Gold_analytics/Procfile) | Specifies the production Gunicorn web server process. |
| [`config/settings/production.py`](file:///d:/Hari_files/FirstMoneyGold/software_apps/Gold_analytics/config/settings/production.py) | Hardened production settings supporting dynamic hostnames (`*.onrender.com`), CSRF origins, HTTPS proxy headers, and resilient SQLite/PostgreSQL failovers. |
