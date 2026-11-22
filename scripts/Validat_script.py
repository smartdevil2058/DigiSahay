import pandas as pd

FILE_PATH = "data\DigiSahay_rulebook (1).xlsx"
excel = pd.ExcelFile(FILE_PATH)

# for sheet in excel.sheet_names:
#     df = pd.read_excel(FILE_PATH,sheet_name=sheet)
#     print(f"\nSheet:{sheet}")
#     print(f"Total Records:{len(df)}")
#     print(f"Columns:{df.columns}")



excel = pd.ExcelFile(FILE_PATH)

sheets_to_import = [
    "Services",
    "Eligibility Rules",
    "Requirement Groups",
    "Document Types",
    "Requirements",
    "Submission Routes",
    "Sources",
    "Requirement Sources",
    "Service Centers",
    "Center Services",
    "Appointments",
    "Service Routes",
    "Applications"
]

data = {}

def load_sheet(name):

    df = pd.read_excel(
        FILE_PATH,
        sheet_name=name
    )

    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(how="all").copy()

    df.columns = df.columns.astype(str).str.strip()

    if name == "Submission Routes":
        df = df.rename(columns={"": "route_id"})
    return df

services = load_sheet("Services")
eligibility = load_sheet("Eligibility Rules")
groups = load_sheet("Requirement Groups")
documents = load_sheet("Document Types")
requirements = load_sheet("Requirements")
sources = load_sheet("Sources")
centers = load_sheet("Service Centers")
center_services = load_sheet("Center Services")
applications = load_sheet("Applications")
appointments = load_sheet("Appointments")
print("\nWorkbook cleaning completed.")

def check_foreign_key(child_df, child_column, parent_df, parent_column, name):
    parent_ids = set(parent_df[parent_column].dropna())
    child_ids = set(child_df[child_column])

    invalid_ids = child_ids - parent_ids

    if invalid_ids:
        print(f"Failed:{name}")
        print(f"Invalid IDs are {invalid_ids}")
    else:
        print("PASSED, there is not a single missing or invalid ids")

print("\n========== FOREIGN KEY VALIDATION ==========")

check_foreign_key(
    eligibility, "service_id",
    services, "service_id",
    "Eligibility Rules -> Services"
)

check_foreign_key(
    groups, "service_id",
    services, "service_id", 
    "Requirement Groups -> Services"
)

check_foreign_key(
    documents, "document_type_id",
    documents, "document_type_id",
    "Document Types primary IDs (basic check)"
)

check_foreign_key(
    requirements, "group_id",
    groups, "group_id",
    "Requirements -> Requirement Groups"
)

check_foreign_key(
    requirements, "document_type_id",
    documents, "document_type_id",
    "Requirements -> Document Types"
)

check_foreign_key(
    requirements, "source_id",
    sources, "source_id",
    "Requirements -> Sources"
)

check_foreign_key(
    center_services, "center_id",
    centers, "center_id",
    "Center Services -> Service Centers"
)

check_foreign_key(
    center_services, "service_id",
    services, "service_id",
    "Center Services -> Services"
)

check_foreign_key(
    applications, "service_id",
    services, "service_id",
    "Applications -> Services"
)

check_foreign_key(
    appointments, "center_id",
    centers, "center_id",
    "Appointments -> Service Centers"
)

check_foreign_key(
    appointments, "service_id",
    services, "service_id",
    "Appointments -> Services"
)

print("\n========== VALIDATION COMPLETE ==========")
