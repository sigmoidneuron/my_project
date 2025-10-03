# Phonebook Backend

A minimal, production-ready Django backend for a phone number search experience. It ships:

* **Public REST APIs** for area-code discovery and related-number search
* **Password-protected dashboard** for CRUD, CSV upsert, bulk delete, and password management
* **SQLite storage** with a reusable seed dataset

Only backend code is included—pair it with any frontend hosted on `www.example.com`.

---

## 1. Prerequisites (Explain-like-I'm-Five)

1. **Install Python 3.11 or newer**
   * **Windows:** download from [python.org](https://www.python.org/downloads/) and tick “Add Python to PATH”.
   * **macOS:** use the official installer or run `brew install python@3.11` if you already use Homebrew.
   * **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install python3.11 python3.11-venv python3.11-dev`.
2. **Open a terminal** (Command Prompt on Windows, Terminal app on macOS, any shell on Linux).
3. **Change into this project folder** (replace the path with wherever you cloned it):
   ```bash
   cd /path/to/my_project
   ```

---

## 2. Create and Activate a Virtual Environment

Keeping dependencies isolated avoids breaking your global Python setup.

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS / Linux
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Your prompt should now start with `(.venv)` to show the environment is active. Any time you return to this project, re-run the activation command above.

To leave the virtual environment later, run `deactivate`.

---

## 3. Install Dependencies

With the virtual environment active:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs Django 5, Django REST Framework, and django-cors-headers—nothing else.

---

## 4. Apply Database Migrations

```bash
python manage.py migrate
```

This creates the SQLite database (`db.sqlite3`) with the `PhoneNumber` table, uniqueness constraints, and indexes.

---

## 5. Create the Default Dashboard User (admin / 12345)

```bash
python manage.py ensure_admin
```

* If the `admin` user is missing, it will be created with password `12345`.
* If the user already exists (maybe you changed the password earlier), **nothing is overwritten**.

You can run this command as many times as you like—it is safe and idempotent.

---

## 6. Load Sample Data (Optional but Helpful)

```bash
python manage.py loaddata fixtures/sample_numbers.json
```

This seeds a few phone numbers so the APIs and dashboard have data to display.

---

## 7. Run the Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Keep this command running. The app will now be reachable on port 8000.

---

## 8. Simulate Subdomains Locally (Hosts File)

We conceptually host three subdomains on the same machine:

* Frontend SPA (not part of this repo): `https://www.example.com`
* Public APIs: `https://api.example.com`
* Dashboard: `https://dashboard.example.com`

To mimic this locally, point all three to `127.0.0.1` (your computer) while `runserver` is running.

### Windows
1. Run Notepad as Administrator.
2. Open `C:\\Windows\\System32\\drivers\\etc\\hosts`.
3. Add this line at the end:
   ```
   127.0.0.1    www.example.com api.example.com dashboard.example.com
   ```
4. Save and close Notepad.

### macOS / Linux
```bash
sudo sh -c 'echo "127.0.0.1 www.example.com api.example.com dashboard.example.com" >> /etc/hosts'
```

> **Tip:** if you ever want to undo this mapping, remove that line from your hosts file.

Now visiting `http://dashboard.example.com:8000/` in your browser will open the dashboard, and `http://api.example.com:8000/` will serve the APIs. (Use `https://` later in production with a reverse proxy—see section 12.)

---

## 9. Call the Public APIs (cURL Examples)

With the server running and hosts file updated, try:

```bash
curl http://api.example.com:8000/api/area-codes/
```

Expected response (sample):
```json
{"area_codes": ["212", "415", "646"]}
```

Search for related numbers (defaults to top 50 results, limit 100):

```bash
curl "http://api.example.com:8000/api/search/?area_code=212&digits=5550005&top=5"
```

Example response:
```json
[
  {"area_code": "212", "local_number": "5550002", "full_number": "2125550002", "cost": "12.50"},
  {"area_code": "212", "local_number": "5550001", "full_number": "2125550001", "cost": "10.00"}
]
```

Validation rules:

* `area_code` must be exactly 3 digits.
* `digits` must be exactly 7 digits.
* `top` is optional (defaults to 50) but must be an integer between 1 and 100 when provided.
* Invalid inputs return `400 Bad Request` with clear JSON error messages.

---

## 10. Use the Dashboard (Step-by-Step)

Open `http://dashboard.example.com:8000/` in your browser.

1. **Sign In**
   * Username: `admin`
   * Password: `12345`
   * Click **“Sign In”**.
2. **Browse Numbers**
   * You land on the “Phone Numbers” table with pagination (25 rows per page) and sortable columns.
   * Links:
     * **“Add Number”** → create a new entry.
     * **“Upload CSV”** → import/update data in bulk.
     * **“Delete All”** → wipe every row (after a confirmation screen).
3. **Add a Number**
   * Click **“Add Number”**, fill the form (3-digit area code, 7-digit number, cost), click **“Save”**.
4. **Edit / Delete a Number**
   * In the table, use **“Edit”** or **“Delete”** on any row. Deletes require a quick confirmation pop-up.
5. **Bulk Delete**
   * Click **“Delete All”**, then confirm with **“Yes, delete everything”** to remove all entries.
6. **CSV Upload (Upsert)**
   * Click **“Upload CSV”** and select a `.csv` file with the exact header row:
     ```csv
     area code,phone number,cost
     212,5550003,9.99
     212,5550001,11.00
     ```
   * Result: rows are inserted or updated by `(area_code, local_number)` and a summary appears.
   * Any skipped rows list the reason (bad digits, wrong column count, invalid cost, etc.).
7. **Update Password**
   * Click **“Update Password”** in the navbar.
   * Enter your current password, choose a new password (at least 5 characters), confirm it, then submit.
   * You will be logged out with a success banner: “Password updated. Please sign in with your new password.”
   * Sign back in with the new password. Re-running `python manage.py ensure_admin` later will **not** overwrite it.
8. **Sign Out**
   * Click **“Sign Out”** in the navbar.

> Screenshot placeholders (replace with your own once deployed):
> * Login page: `![Login screenshot](docs/login.png)`
> * Dashboard table: `![Dashboard table screenshot](docs/dashboard.png)`
> * CSV summary: `![CSV summary screenshot](docs/csv.png)`

---

## 11. Understanding CORS (Why django-cors-headers?)

* The frontend will live on `www.example.com`.
* APIs live on `api.example.com`.
* Browsers treat different subdomains as different origins, so cross-origin requests must be explicitly allowed.
* `django-cors-headers` is configured to allow the frontend origin (`http://www.example.com:8000` during dev, `https://www.example.com` in production).
* Adjust `CORS_ALLOWED_ORIGINS` inside `phonebook/settings.py` if your frontend domain changes.

---

## 12. Production Reverse Proxy (Nginx Example)

Use host-based routing to expose the three subdomains over HTTPS while pointing them to the same Django backend. Below is a minimal Nginx snippet assuming Gunicorn (or Daphne) listens on `127.0.0.1:8000`.

```nginx
# /etc/nginx/sites-available/phonebook.conf
upstream phonebook_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;
    location / {
        proxy_pass http://phonebook_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name dashboard.example.com;
    location / {
        proxy_pass http://phonebook_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend would likely be served separately (static hosting or another service)
# but you can proxy-pass it to a React/Vue dev server if needed.
```

Once ready for HTTPS, obtain TLS certificates (e.g., via Let’s Encrypt) and update the `listen 443 ssl;` blocks accordingly.

*Prefer Caddy?* A similar host-based setup works:
```caddyfile
api.example.com, dashboard.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

---

## 13. Stopping the Server and Cleaning Up

* Stop `runserver` with **Ctrl+C** in the terminal where it is running.
* Deactivate the virtual environment with `deactivate`.
* Optionally remove the hosts file entry if you no longer need the subdomain mappings.

---

## 14. Project Structure Reference

```
.
├── catalog/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── dashboard/
│   ├── management/commands/ensure_admin.py
│   ├── templates/dashboard/
│   ├── apps.py
│   ├── forms.py
│   ├── urls.py
│   └── views.py
├── fixtures/sample_numbers.json
├── manage.py
├── phonebook/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── requirements.txt
└── README.md
```

No automated tests are included to keep the scope focused on the functional requirements above.

---

Happy hacking!
