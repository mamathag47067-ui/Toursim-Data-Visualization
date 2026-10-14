# Indian Tourism Analytics Dashboard

An interactive Streamlit dashboard for the **Top Indian Places to Visit** dataset. The sidebar filters update all KPI cards, charts, and the destination table together.

## Features
- Sidebar filters for tourism zone, state, destination type, significance, best time to visit, airport access, DSLR permission, entrance-fee range, and Google rating range
- KPI cards for destination count, average rating, average entrance fee, and average visit duration
- Interactive bar, pie, line, scatter, and histogram charts
- Filtered destination table and CSV download
- Responsive layout with Plotly charts

## Files
- `app.py` — Streamlit dashboard
- `Top Indian Places to Visit.csv` — dataset
- `requirements.txt` — Python dependencies

## Run locally

1. Install Python 3.10 or newer.
2. Put all three files in the same folder.
3. Open a terminal in that folder and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Upload to GitHub

Create a new repository on GitHub, then upload `app.py`, `requirements.txt`, `README.md`, and `Top Indian Places to Visit.csv`.

Or use Git from the project folder:

```bash
git init
git add app.py requirements.txt README.md "Top Indian Places to Visit.csv"
git commit -m "Add interactive tourism dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace `YOUR-USERNAME` and `YOUR-REPOSITORY` with your own GitHub details.

## Deploy with Streamlit Community Cloud

1. Visit https://share.streamlit.io/
2. Sign in with GitHub and grant access to the repository.
3. Select your repository and branch (`main`).
4. Set the main file path to `app.py`.
5. Click **Deploy**.

Keep `Top Indian Places to Visit.csv` in the repository root next to `app.py`, otherwise the app will not find the dataset.

## Dataset note
The dashboard expects these columns in the CSV: Zone, State, City, Name, Type, Establishment Year, time needed to visit in hrs, Google review rating, Entrance Fee in INR, Airport with 50km Radius, Weekly Off, Significance, DSLR Allowed, Number of google review in lakhs, and Best Time to visit.
