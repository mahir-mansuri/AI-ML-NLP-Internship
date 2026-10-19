
import streamlit as st
from pathlib import Path


st.set_page_config(
    page_title="Manual Summary Statistics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Manual Summary Statistics")
st.write("Statistics calculated using Python loops without Pandas or NumPy.")


# 1. Manually parse a CSV line
def parse_line(line, delimiter=","):
    fields = []
    current = ""
    inside_quotes = False
    i = 0

    while i < len(line):
        char = line[i]

        if char == '"':
            if (
                inside_quotes
                and i + 1 < len(line)
                and line[i + 1] == '"'
            ):
                current += '"'
                i += 1
            else:
                inside_quotes = not inside_quotes

        elif char == delimiter and not inside_quotes:
            fields.append(current.strip())
            current = ""

        else:
            current += char

        i += 1

    fields.append(current.strip())
    return fields


# 2. Read dataset manually
def load_dataset(file_path):
    with open(file_path, "r", encoding="utf-8-sig") as file:
        text = file.read()

    lines = [line for line in text.splitlines() if line.strip()]

    if not lines:
        return [], []

    headers = parse_line(lines[0])
    rows = []

    for line in lines[1:]:
        row = parse_line(line)

        if len(row) == len(headers):
            rows.append(row)

    return headers, rows


# 3. Convert valid values into numbers
def get_numeric_values(rows, column_index):
    values = []

    for row in rows:
        try:
            value = float(row[column_index])
            values.append(value)
        except ValueError:
            continue

    return values


# 4. Calculate mean manually
def calculate_mean(values):
    total = 0.0
    count = 0

    for value in values:
        total += value
        count += 1

    if count == 0:
        return None

    return total / count


# 5. Sort values manually using insertion sort
def manual_sort(values):
    result = []

    for value in values:
        position = 0

        while (
            position < len(result)
            and result[position] <= value
        ):
            position += 1

        result.insert(position, value)

    return result


# 6. Calculate median manually
def calculate_median(values):
    if len(values) == 0:
        return None

    ordered = manual_sort(values)
    n = len(ordered)
    middle = n // 2

    if n % 2 == 1:
        return ordered[middle]

    return (ordered[middle - 1] + ordered[middle]) / 2


# 7. Calculate mode manually
def calculate_mode(values):
    if len(values) == 0:
        return []

    frequencies = {}

    for value in values:
        if value in frequencies:
            frequencies[value] += 1
        else:
            frequencies[value] = 1

    highest_frequency = 0

    for value in frequencies:
        if frequencies[value] > highest_frequency:
            highest_frequency = frequencies[value]

    modes = []

    for value in frequencies:
        if frequencies[value] == highest_frequency:
            modes.append(value)

    return manual_sort(modes)


# 8. Calculate minimum manually
def calculate_min(values):
    if len(values) == 0:
        return None

    smallest = values[0]

    for value in values:
        if value < smallest:
            smallest = value

    return smallest


# 9. Calculate maximum manually
def calculate_max(values):
    if len(values) == 0:
        return None

    largest = values[0]

    for value in values:
        if value > largest:
            largest = value

    return largest


# 10. Calculate population standard deviation manually
def calculate_std(values):
    if len(values) == 0:
        return None

    mean = calculate_mean(values)
    squared_difference_total = 0.0

    for value in values:
        difference = value - mean
        squared_difference_total += difference * difference

    variance = squared_difference_total / len(values)

    # Square root using Newton's method
    if variance == 0:
        return 0.0

    estimate = variance if variance >= 1 else 1.0

    for _ in range(100):
        estimate = (estimate + variance / estimate) / 2

    return estimate


# 11. Locate dataset relative to this app
dataset_path = (
    Path(__file__).resolve().parent.parent
    / "01-heart-dataset-viewer"
    / "heart.csv"
)

if not dataset_path.exists():
    st.error(f"Dataset not found: {dataset_path}")
    st.info(
        "Keep heart.csv inside the "
        "01-heart-dataset-viewer folder."
    )

else:
    headers, rows = load_dataset(dataset_path)

    if not headers:
        st.error("Dataset is empty.")

    else:
        st.success("Dataset loaded successfully!")

        st.metric("Total Rows", len(rows))
        st.metric("Total Columns", len(headers))

        # Detect columns containing numeric values
        numeric_columns = []

        for index, header in enumerate(headers):
            values = get_numeric_values(rows, index)

            if values:
                numeric_columns.append(header)

        if not numeric_columns:
            st.warning("No numerical columns found.")

        else:
            selected_columns = st.multiselect(
                "Select numerical columns",
                numeric_columns,
                default=numeric_columns
            )

            statistics_rows = []

            for column in selected_columns:
                index = headers.index(column)
                values = get_numeric_values(rows, index)

                mean = calculate_mean(values)
                median = calculate_median(values)
                modes = calculate_mode(values)
                smallest = calculate_min(values)
                largest = calculate_max(values)
                std = calculate_std(values)

                statistics_rows.append({
                    "Column": column,
                    "Count": len(values),
                    "Mean": round(mean, 3),
                    "Median": round(median, 3),
                    "Mode": ", ".join(
                        str(round(value, 3))
                        for value in modes
                    ),
                    "Min": round(smallest, 3),
                    "Max": round(largest, 3),
                    "Std Dev (Population)": round(std, 3)
                })

            st.subheader("Summary Statistics")

            st.dataframe(
                statistics_rows,
                use_container_width=True,
                hide_index=True
            )
