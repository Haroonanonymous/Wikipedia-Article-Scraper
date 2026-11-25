
import pandas as pd

# Read CSV file
df = pd.read_csv("wikipedia_articles.csv")

# Create Excel file
with pd.ExcelWriter(
    "wikipedia_articles.xlsx",
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Wikipedia Data",
        index=False
    )

    # Access worksheet
    worksheet = writer.sheets["Wikipedia Data"]

    # Freeze header row
    worksheet.freeze_panes = "A2"

    # Enable filters
    worksheet.auto_filter.ref = worksheet.dimensions

    # Automatically adjust column widths
    for column in worksheet.columns:

        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:

            if cell.value is not None:
                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        worksheet.column_dimensions[
            column_letter
        ].width = min(max_length + 2, 50)

print("Excel file created successfully!")
print("File: wikipedia_articles.xlsx")
print("Total records:", len(df))
