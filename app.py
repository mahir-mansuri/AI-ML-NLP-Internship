
import streamlit as st


# 1. Streamlit page setup
st.set_page_config(
    page_title="Heart Dataset Viewer",
    page_icon="❤️",
    layout="wide"
)

st.title("❤️ Heart Dataset Viewer")
st.write("Manual CSV parsing without Pandas")


# 2. Manually parse one line
def parse_line(line, delimiter):
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


# 3. Automatically detect delimiter
def detect_delimiter(text):
    candidates = [",", ";", "\t", "|"]
    lines = [
        line for line in text.splitlines()
        if line.strip()
    ][:20]

    best_delimiter = ","
    best_score = (-1, -1)

    for delimiter in candidates:
        counts = [
            len(parse_line(line, delimiter))
            for line in lines
        ]

        if not counts:
            continue

        frequency = max(
            counts.count(n) for n in set(counts)
        )
        columns = max(counts)

        score = (
            frequency if columns > 1 else 0,
            columns
        )

        if score > best_score:
            best_score = score
            best_delimiter = delimiter

    return best_delimiter


# 4. Parse dataset into headers and rows
def parse_dataset(text, delimiter):
    lines = text.splitlines()
    rows = []

    for line in lines:
        if line.strip():
            rows.append(parse_line(line, delimiter))

    if not rows:
        return [], [], 0

    headers = rows[0]
    data = []
    skipped_rows = 0

    for row in rows[1:]:
        if len(row) == len(headers):
            data.append(row)
        else:
            skipped_rows += 1

    return headers, data, skipped_rows


# 5. Create sorting key
def get_sort_key(row, column_index):
    value = row[column_index].strip()

    try:
        return (0, float(value))
    except ValueError:
        return (1, value.casefold())


# 6. Load heart.csv
try:
    with open(
        "heart.csv",
        "r",
        encoding="utf-8-sig"
    ) as file:
        content = file.read()

    if not content.strip():
        st.error("The dataset file is empty.")

    else:
        delimiter = detect_delimiter(content)

        headers, data, skipped_rows = parse_dataset(
            content, delimiter
        )

        if not headers:
            st.error("No columns were found.")

        elif len(headers) != len(set(headers)):
            st.error("Duplicate column names detected.")

        else:
            st.success("Dataset loaded successfully!")

            st.caption(
                f"Detected delimiter: {repr(delimiter)}"
            )

            # 7. Display dataset information
            col1, col2, col3 = st.columns(3)

            col1.metric("Total Rows", len(data))
            col2.metric("Total Columns", len(headers))
            col3.metric("Skipped Rows", skipped_rows)

            st.write("Column names:", headers)

            # 8. Sorting options
            st.subheader("Sorting Options")

            col_a, col_b = st.columns(2)

            with col_a:
                sort_column = st.selectbox(
                    "Sort by column",
                    ["None"] + headers
                )

            with col_b:
                sort_order = st.selectbox(
                    "Sort order",
                    ["Ascending", "Descending"]
                )

            display_data = [row.copy() for row in data]

            if sort_column != "None":
                column_index = headers.index(sort_column)

                display_data.sort(
                    key=lambda row: get_sort_key(
                        row, column_index
                    ),
                    reverse=(sort_order == "Descending")
                )

            # 9. Pagination options
            st.subheader("Pagination")

            page_size = st.selectbox(
                "Rows per page",
                [5, 10, 20, 50, 100],
                index=1
            )

            total_rows = len(display_data)

            total_pages = max(
                1,
                (total_rows + page_size - 1) // page_size
            )

            page = st.number_input(
                "Select page",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1
            )

            start = (page - 1) * page_size
            end = min(start + page_size, total_rows)

            page_data = display_data[start:end]

            st.caption(
                f"Page {page} of {total_pages} | "
                f"Showing rows "
                f"{start + 1 if total_rows else 0}"
                f"–{end} of {total_rows}"
            )

            # 10. Display current page as a table
            table_data = [
                dict(zip(headers, row))
                for row in page_data
            ]

            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True
            )

except FileNotFoundError:
    st.error(
        "heart.csv not found. Keep it in the same "
        "folder as app.py."
    )

except UnicodeDecodeError:
    st.error("Please use a UTF-8 encoded text dataset.")
