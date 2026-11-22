from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FILE_PATH = ROOT / "data" / "DigiSahay_rulebook (1).xlsx"

for sheet in ["Applications", "Appointments"]:
    df = pd.read_excel(FILE_PATH, sheet_name=sheet)

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all")

    print(f"\n{sheet} user IDs:")
    print(df["user_id"].dropna().unique())