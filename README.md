<img width="1445" height="915" alt="docker_running" src="https://github.com/user-attachments/assets/80edddbc-f607-4903-9b2e-c5629e245734" /># 🎵 Collaborative Playlist 
A realtime collaborative playlist system where users can add tracks, vote, reorder, and see updates instantly through Server-Sent Events (SSE). The backend is built using **Django REST Framework**, and the frontend uses **Streamlit** with a custom embedded HTML+JS interface for live syncing.

---

# ✅ Setup Instructions

### **1. Clone the repository**

```bash
git clone https://github.com/Fahimahmed123/colaborative_playlist.git
cd colaborative_playlist
```

---

### **2. Create environment file**

```bash
cp .env.example .env
```

---
---

If you want, I can now:

✅ merge all sections into a perfectly formatted **final README.md**
or
✅ generate **screenshots**, **tests**, or **Docker deployment notes**.

Just say: **"give final README"** or **"generate tests"**.

### **3. Install dependencies (non-Docker option)**

```bash
pip install -r requirements.txt
```

---

### **4. Run database migrations**

```bash
python manage.py migrate
```

---

### **5. Start Django backend**

```bash
python manage.py runserver
```

API will be available at:

* [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

### **6. Start Streamlit UI**

```bash
streamlit run streamlit_app.py
```

UI will open at:

* [http://localhost:8501/](http://localhost:8501/)

---

### **7. (Recommended) Run everything via Docker**

```bash
docker compose up --build
```

This runs:

| Service            | Port |
| ------------------ | ---- |
| Django backend     | 8000 |
| Streamlit frontend | 8501 |

---

# 🌱 Database Seeding Instructions

Your backend includes a built-in seeding system (`playlist/seeds.py`).

### **Option 1: Use the built-in endpoint**

Visit:

```
http://127.0.0.1:8000/admin/seed
```

This loads:

* Sample tracks
* A default playlist

---

### **Option 2: Management command**

```bash
python manage.py seed
```

---

### **Option 3: Docker version**

```bash
docker exec -it django_app python manage.py seed
```

---

# ⚙️ Technical Decisions and Trade-offs

### **1. Server-Sent Events (SSE) for realtime**

* **Why:** Very simple to implement, stable, built-in browser support.
* **Trade-off:** One-way communication only; WebSockets would support chat or voice rooms.

---

### **2. Streamlit for the UI**

* **Why:** Fast prototyping, easy deployment, integrated Python environment.
* **Trade-off:** Limited dynamic interactions compared to React/Vue.

---

### **3. Optimistic UI updates**

* **Why:** Playlist feels snappy; users see their additions instantly.
* **Trade-off:** Requires cleanup when backend sends correct state.
  (Handled in `ui.html` → `"track.added"` event logic.)

---

### **4. SQLite database**

* **Why:** Simple, portable, perfect for Docker and assignments.
* **Trade-off:** Not suitable for massive concurrency like 10k users.

---

### **5. Django REST Framework**

* **Why:** Clean serialization, strong authentication, easy testing.
* **Trade-off:** Slightly slower than lightweight FastAPI for realtime workloads.

---

# ⏳ If I Had 2 More Days…

* Add Redis or PostgreSQL for more reliable transactions
* Add WebSocket support instead of SSE
* Build a full React UI with drag-and-drop timeline visuals
* Implement user-uploaded tracks and audio preview
* Deploy the project to Render/Heroku with CI/CD
* Add more tests: concurrency tests, SSE tests, and playlist ordering tests
* Improve error handling and add rate limiting


Working screenshots are given:

<img width="1876" height="927" alt="login" src="https://github.com/user-attachments/assets/8c4640ee-f631-41e1-a504-61a554e099e0" />
<img width="1876" height="927" alt="realtime_sync2" src="https://github.com/user-attachments/assets/3d2d8f19-5d67-4cbf-b021-7e6988d5d39b" />
<img width="1876" height="927" alt="realtime_sync" src="https://github.com/user-attachments/assets/27a2eb40-9a9e-4f78-8fa1-bebf84135fbd" />
<img width="1876" height="927" alt="playlist_view" src="https://github.com/user-attachments/assets/3f3371fa-c12f-4bdb-881f-bedba327f8ca" />
<img width="1445" height="915" alt="docker_running" src="https://github.com/user-attachments/assets/69e1e6f7-cbf0-4eab-aca8-5230be26fb59" />


