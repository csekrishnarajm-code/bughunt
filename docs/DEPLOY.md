# Deploy BugHunt for free (Render + Neon)

BugHunt is one Docker service (the API also serves the React app), plus a PostgreSQL database.

## 1. Database (Neon)

You can reuse the Neon connection string from your JobTrack or ResumeFit project. The tables do not conflict
(BugHunt only creates `games` and `answers`). For a clean database, create a new Neon project instead.

The string looks like `postgresql://USER:PASSWORD@ep-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`.

## 2. Push the code to GitHub

Create a public repo named `bughunt`, then from the project folder (the one that contains `backend`, `frontend` and `Dockerfile`):

```powershell
git init
git add .
git commit -m "BugHunt: spot-the-bug game with React and FastAPI"
git branch -M main
git remote add origin https://github.com/csekrishnarajm-code/bughunt.git
git push -u origin main
```

Check on GitHub that the first page shows `backend`, `frontend`, `docs` and `Dockerfile`.

## 3. Render

1. Render dashboard, **New +**, **Web Service**, choose the `bughunt` repo.
2. Fill in:
   - **Name:** `bughunt`
   - **Language:** Docker
   - **Branch:** `main`
   - **Root Directory:** leave empty
   - **Dockerfile Path:** `./Dockerfile`
   - **Docker Build Context Directory:** `.`
   - **Instance Type:** Free
3. Environment variable: `DATABASE_URL` = your Neon connection string.
4. Click **Create Web Service**. The first build takes a few minutes.
5. When it says **Live**, open the URL.

## 4. Check it

- Click **Start hunting**, play a few bugs, and check the explanation and fix appear after each answer.
- Finish a game, submit your name, and check you appear on the leaderboard.
- Refresh the page in the middle of a game. You should land back on the same bug.
- Open `/docs` for the API docs.

## Notes

- Free Render services sleep after about 15 minutes without traffic, so the first request can take up to a minute.
- The leaderboard keeps the names players type. There is no moderation, so delete rows from the `games` table if you need to.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Dockerfile not found" | Dockerfile Path must be `./Dockerfile` and the build context `.`, with Root Directory empty |
| Game does not start (500 error) | Check `DATABASE_URL` is the full Neon string including `?sslmode=require` |
| Page loads but is blank | Check the Render build log for `npm run build` errors |
