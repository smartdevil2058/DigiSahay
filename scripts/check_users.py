<<<<<<< HEAD
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FILE_PATH = ROOT / "data" / "DigiSahay_rulebook (1).xlsx"

for sheet in ["Applications", "Appointments"]:
    df = pd.read_excel(FILE_PATH, sheet_name=sheet)

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all")

    print(f"\n{sheet} user IDs:")
=======
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FILE_PATH = ROOT / "data" / "DigiSahay_rulebook (1).xlsx"

for sheet in ["Applications", "Appointments"]:
    df = pd.read_excel(FILE_PATH, sheet_name=sheet)

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all")

    print(f"\n{sheet} user IDs:")
>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c
    print(df["user_id"].dropna().unique())