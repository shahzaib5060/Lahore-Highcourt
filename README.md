# Punjab Lawyers Dashboard (Streamlit)

A Python dashboard of the Lahore High Court Bar Association voter roll 2022–23:
17,859 lawyers across 38 bar stations, with filters, charts, a station
scorecard and a photo directory.

## Files

| File | What it is |
|---|---|
| `streamlit_app.py` | The dashboard (Python). Main file path for Streamlit. |
| `requirements.txt` | Python packages Streamlit Cloud installs. |
| `lawyers.csv` | The lawyer records. Used until Supabase is connected. |
| `sheet_0.jpg` … `sheet_8.jpg` | Member photos, 40 per row, 72×72 px each. |
| `.streamlit/config.toml` | Navy and gold theme, including the dark sidebar. |
| `supabase_schema.sql` | Creates the `lawyers` table in Supabase. |

## Run on your computer

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Connect Supabase

1. In Supabase, open **SQL Editor**, paste `supabase_schema.sql` and click **Run**.
2. Open **Table Editor → lawyers → Insert → Import data from CSV** and upload `lawyers.csv`.
3. In Supabase **Project Settings → API**, copy the **Project URL** and the **service_role** key.
4. In Streamlit Cloud, open **Manage app → Settings → Secrets** and paste:

   ```toml
   [supabase]
   url = "https://YOUR-PROJECT.supabase.co"
   key = "YOUR-SERVICE-ROLE-KEY"
   ```

5. Save. The app restarts and the sidebar shows "Data source: Supabase".

Never put the key in a file in this repository. Secrets keep it on the server.
The app re-reads Supabase every 10 minutes, so new or edited rows appear without
a redeploy.

## Adding more stations

Add rows to `lawyers.csv` (or the Supabase table) with the same columns. New
stations appear in the filters and charts automatically.
