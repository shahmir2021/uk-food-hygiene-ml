import csv


# ============================================================
# 1. FILE LOCATIONS
# ============================================================

INPUT_FILE = (
    "/Users/shahmirayub/Downloads/"
    "BasicCompanyDataAsOneFile-2026-09-01.csv"
)

OUTPUT_FILE = (
    "/Users/shahmirayub/Downloads/"
    "companies_house_selected_2026_09.csv"
)


# ============================================================
# 2. COLUMNS WE ACTUALLY NEED
# ============================================================

KEEP_COLUMNS = [
    "CompanyName",
    "CompanyNumber",
    "RegAddress.PostCode",
    "CompanyStatus",
    "CompanyCategory",
    "CountryOfOrigin",
    "IncorporationDate",
    "DissolutionDate",
    "Accounts.AccountCategory",
    "Accounts.LastMadeUpDate",
    "Accounts.NextDueDate",
    "Mortgages.NumMortCharges",
    "Mortgages.NumMortOutstanding",
    "Mortgages.NumMortPartSatisfied",
    "Mortgages.NumMortSatisfied",
    "SICCode.SicText_1",
    "SICCode.SicText_2",
    "SICCode.SicText_3",
    "SICCode.SicText_4",
]


# ============================================================
# 3. FUNCTION TO CLEAN HEADER NAMES
# ============================================================

def clean_header(value):
    """
    Removes spaces and invisible Unicode characters
    that can cause column-name matching problems.
    """

    if value is None:
        return ""

    return (
        value
        .strip()
        .replace("\ufeff", "")   # BOM
        .replace("\u200b", "")   # zero-width space
        .replace("\xa0", " ")    # non-breaking space
        .strip()
    )


# ============================================================
# 4. STREAM THROUGH THE LARGE CSV
#
# The source file is around 2.8 GB.
# We process one row at a time rather than loading
# the whole dataset into RAM.
# ============================================================

row_count = 0

print("Opening Companies House dataset...")

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8-sig",
    newline=""
) as infile:

    reader = csv.DictReader(infile)

    if reader.fieldnames is None:
        raise ValueError("No CSV header was found.")

    # --------------------------------------------------------
    # Build a mapping:
    #
    # cleaned column name -> actual column name in source CSV
    #
    # Example:
    # CompanyNumber -> CompanyNumber
    # --------------------------------------------------------

    header_map = {}

    for original_header in reader.fieldnames:

        cleaned_header = clean_header(original_header)

        header_map[cleaned_header] = original_header


    # --------------------------------------------------------
    # Check required columns
    # --------------------------------------------------------

    missing_columns = []

    for required_column in KEEP_COLUMNS:

        cleaned_required_column = clean_header(required_column)

        if cleaned_required_column not in header_map:
            missing_columns.append(required_column)


    if missing_columns:

        print()
        print("=" * 60)
        print("MISSING REQUIRED COLUMNS")
        print("=" * 60)

        for column in missing_columns:
            print(column)

        print()
        print("Available source columns:")
        print()

        for column in reader.fieldnames:
            print(repr(column))

        raise ValueError(
            f"Missing columns: {missing_columns}"
        )


    print("All required columns found.")
    print()
    print("Starting reduction...")


    # ========================================================
    # 5. CREATE REDUCED OUTPUT FILE
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=KEEP_COLUMNS
        )

        # Write standardized output column names
        writer.writeheader()


        # ====================================================
        # 6. PROCESS COMPANIES ONE ROW AT A TIME
        # ====================================================

        for row in reader:

            selected_row = {}

            for required_column in KEEP_COLUMNS:

                cleaned_required_column = clean_header(
                    required_column
                )

                # Find the real source column
                source_column = header_map[
                    cleaned_required_column
                ]

                # Copy its value into our standardized column
                selected_row[required_column] = row.get(
                    source_column,
                    ""
                )

            writer.writerow(selected_row)

            row_count += 1


            # ------------------------------------------------
            # Progress update every 500,000 companies
            # ------------------------------------------------

            if row_count % 500_000 == 0:
                print(
                    f"Processed {row_count:,} companies..."
                )


# ============================================================
# 7. FINISHED
# ============================================================

print()
print("=" * 60)
print("COMPANIES HOUSE REDUCTION COMPLETE")
print("=" * 60)

print(f"Rows written: {row_count:,}")
print(f"Columns kept: {len(KEEP_COLUMNS)}")
print(f"Output file: {OUTPUT_FILE}")