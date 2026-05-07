# Truck Scheduling Knowledge

## Business Rules
- 9MT trucks are used for smaller loads
- 16MT trucks are used for higher loads
- Truck type should be consistent (no "9 mt", always "9MT")

## Logic
- cases_per_truck = total_cases / trips
- If trips = 0 → ignore row

## Data Rules
- truck column contains truck type
- cases column contains total units
- plant is source
- destination is target

## Code Examples
- Total cases for 9MT:
  df[df["truck"]=="9MT"]["cases"].sum()

- Group by truck:
  df.groupby("truck")["cases"].sum()

## Edge Cases
- Normalize truck values:
  df["truck"] = df["truck"].str.upper().str.replace(" ", "")

- If no matching rows → return 0