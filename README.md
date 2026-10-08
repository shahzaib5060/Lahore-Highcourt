# Punjab Lawyers Dashboard (Streamlit + Supabase)

A Python dashboard of the Lahore High Court Bar Association voter roll 2022–23:
17,859 lawyers across 38 bar stations, with login, filters, charts, a station
scorecard and a photo directory.

## Files

| File | What it is |
|---|---|
| `streamlit_app.py` | The dashboard. Main file path for Streamlit. |
| `requirements.txt` | Python packages Streamlit Cloud installs. |
| `lawyers.csv` | The lawyer records, ready to import into Supabase. |
| `sheet_0.jpg` … `sheet_8.jpg` | Member photos (40 per row, 72×72 px). |
| `supabase_schema.sql` | Creates the `lawyers` table and its read rule. |
| `.streamlit/config.toml` | Optional. The theme is also set inside the app. |

## Login

The dashboard always asks for a login. Put one of these in Streamlit Cloud:
**Manage app → Settings → Secrets**.

**Option A: simple passwords (works straight away, data from lawyers.csv)**

```toml
[passwords]
shahzaib = "choose-a-strong-password"
```

Add one line per person.

**Option B: Supabase (login with email + data from Supabase)**

```toml
[supabase]
url = "https://YOUR-PROJECT-ID.supabase.co"
anon_key = "YOUR-ANON-OR-PUBLISHABLE-KEY"
```

When `[supabase]` is present the app uses it, and `[passwords]` is ignored.

## Connect Supabase, step by step

1. **Create a project** at supabase.com. Note the database password somewhere safe.
2. **Create the table.** Open **SQL Editor → New query**, paste all of
   `supabase_schema.sql`, click **Run**.
3. **Import the data.** Open **Table Editor → lawyers → Insert → Import data from CSV**,
   choose `lawyers.csv`, check the columns match, and import. You should see 17,859 rows.
4. **Create logins.** Open **Authentication → Users → Add user → Create new user**.
   Enter the email and a password and tick **Auto Confirm User**. Repeat for each person.
5. **Stop strangers signing up.** In **Authentication → Sign In / Providers**, turn off
   **Allow new users to sign up**. Only the users you add can then log in.
6. **Copy the keys.** In **Project Settings → API Keys**, copy the **Project URL** and the
   **anon** (or **publishable**) key. Do not use the service_role / secret key.
7. **Add the secrets** in Streamlit (Option B above) and click **Save**. The app restarts.
8. **Sign in** with a user from step 4. The sidebar shows "Data source: Supabase".

Why this is safe: the anon key alone can't read anything. The table's rule only lets
signed-in users read rows, and only the users you create can sign in.

## After Supabase is working

* Delete `lawyers.csv` from the GitHub repo. The data now lives in Supabase.
* Make the GitHub repo private (Settings → General → Danger Zone → Change visibility).
  The app keeps working; the photo sheets are read by the app on the server.
* Edits you make in the Supabase Table Editor show up in the dashboard within 10 minutes.

## Run on your computer

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Put the same secrets in `.streamlit/secrets.toml` next to the app (never commit that file).
