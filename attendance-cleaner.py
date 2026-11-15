"""
Student Attendance Cleaner
==========================
Reads raw student names from ``attendance.txt`` (one name per line), cleans them,
removes duplicates and writes a tidy, alphabetically sorted list to
``attendance_clean.csv``.

Concepts demonstrated
---------------------
* File handling      : read a text file, write a CSV file.
* Exception handling : ``FileNotFoundError``, empty input, write errors.
* List comprehension : ``strip()`` + ``title()`` clean-up of every name.
* Sets               : ``set(cleaned)`` removes duplicates and gives the unique count.
"""

import csv

INPUT_FILE = "attendance.txt"
OUTPUT_FILE = "attendance_clean.csv"


def read_raw_lines(filename=INPUT_FILE):
    """Return every line of *filename* (or None if the file cannot be read)."""
    try:
        with open(filename, mode="r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"[error] '{filename}' was not found. Place it in the same folder as this script.")
    except PermissionError:
        print(f"[error] No permission to read '{filename}'.")
    except UnicodeDecodeError:
        print(f"[error] '{filename}' is not a valid UTF-8 text file.")
    return None


def clean_names(lines):
    """Clean the raw lines with a LIST COMPREHENSION.

    * ``strip()`` removes leading/trailing spaces and the newline character.
    * ``split()`` + ``" ".join()`` squeezes repeated spaces *inside* a name
      ("zainab   iqbal" -> "zainab iqbal") so one student is never counted twice.
    * ``title()`` fixes capitalisation  ("aLI rAZA" -> "Ali Raza").
    * The ``if line.strip()`` filter ignores completely blank lines.
    """
    return [" ".join(line.strip().split()).title() for line in lines if line.strip()]


def save_clean_list(names, filename=OUTPUT_FILE):
    """Write the cleaned names to a CSV file (header: student_name)."""
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["student_name"])
            writer.writerows([name] for name in names)
        return True
    except OSError as error:
        print(f"[error] Could not write '{filename}': {error}")
        return False


def main():
    lines = read_raw_lines()
    if lines is None:
        return

    cleaned = clean_names(lines)                 # list comprehension
    if not cleaned:
        print(f"[warning] '{INPUT_FILE}' contains no student names. Nothing to clean.")
        return

    unique_students = set(cleaned)               # set -> duplicates disappear
    final_list = sorted(unique_students)         # alphabetical order

    if not save_clean_list(final_list):
        return

    blank_lines = len(lines) - len(cleaned)
    print("=" * 46)
    print("        STUDENT ATTENDANCE CLEANER")
    print("=" * 46)
    print(f"Original number of records : {len(cleaned)}")
    if blank_lines:
        print(f"(blank lines ignored       : {blank_lines})")
    print(f"Unique students            : {len(unique_students)}")
    print(f"Duplicates removed         : {len(cleaned) - len(unique_students)}")
    print(f"Saved to                   : {OUTPUT_FILE}")
    print("-" * 46)
    print("Cleaned attendance list:")
    for number, name in enumerate(final_list, start=1):
        print(f"{number:>3}. {name}")


if __name__ == "__main__":
    main()
