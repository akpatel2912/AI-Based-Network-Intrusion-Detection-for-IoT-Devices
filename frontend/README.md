# Frontend (HTML, CSS, JS)

Plain files, no build step. Open `index.html` in a browser, or serve the folder:

    python -m http.server 5500

- Demo mode (default) uses mock data so the UI works without a backend. Turn it off to call the API.
- Set the API address at the top of `app.js` (`API_BASE_URL`, default http://localhost:8000).
- Expected endpoints: `POST /predict`, `GET /predictions`, `GET /metrics`.
- The backend must allow CORS for the origin that serves this page.
