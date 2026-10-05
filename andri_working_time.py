import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path


PERSONS_FILE = Path(__file__).resolve().parent / "Persons.csv"
RESULTS_FILE = Path(__file__).resolve().parent / "results.csv"

CSV_COLUMNS = [
    "Eesnimi",
    "Perenimi",
    "Sünniaeg",
    "Sugu",
    "Isikukood",
]
RESULTS_HEADER = CSV_COLUMNS + ["Kuupäev", "Algus", "Lõpp", "Tööaeg"]


def read_persons():
    try:
        with PERSONS_FILE.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file, delimiter=";")
            if reader.fieldnames != CSV_COLUMNS:
                raise ValueError("Persons.csv päis ei vasta nõutud kujule.")
            persons = [person for person in reader if person.get("Eesnimi")]
    except FileNotFoundError:
        raise FileNotFoundError(
            "Persons.csv ei leitud. Lisa see skriptiga samasse kausta."
        )

    if not persons:
        raise ValueError("Persons.csv failis ei ole ühtegi isikut.")

    return persons


def parse_time(value):
    parsed_time = datetime.strptime(value.strip(), "%H:%M").time()
    if parsed_time.strftime("%H:%M") != value.strip():
        raise ValueError
    return parsed_time


def main():
    try:
        persons = read_persons()
    except (OSError, ValueError) as error:
        print(f"Viga: {error}")
        return

    person = random.choice(persons)

    today = date.today()
    first_day_of_year = date(today.year, 1, 1)
    days_since_new_year = (today - first_day_of_year).days
    work_date = first_day_of_year + timedelta(
        days=random.randint(0, days_since_new_year)
    )

    print(f"Isik: {person['Eesnimi']} {person['Perenimi']}")
    print(f"Kuupäev: {work_date.strftime('%d.%m.%Y')}")

    start_input = input("Sisesta töö algusaeg (HH:mm): ")
    end_input = input("Sisesta töö lõpuaeg (HH:mm): ")

    parsed_times = []
    has_invalid_time = False
    for label, value in (("algusaeg", start_input), ("lõpuaeg", end_input)):
        try:
            parsed_times.append(parse_time(value))
        except ValueError:
            print(f"Viga: töö {label} ei ole korrektne kellaaeg kujul HH:mm.")
            parsed_times.append(None)
            has_invalid_time = True

    if has_invalid_time:
        return

    start_time, end_time = parsed_times

    if start_time > end_time:
        start_time, end_time = end_time, start_time
        print("Algusaeg on hilisem kui lõpuaeg. Ajad vahetati.")
    elif start_time == end_time:
        print("Töö algus- ja lõpuaeg on samad.")

    duration_minutes = (
        end_time.hour * 60
        + end_time.minute
        - start_time.hour * 60
        - start_time.minute
    )
    hours, minutes = divmod(duration_minutes, 60)

    start_text = start_time.strftime("%H:%M")
    end_text = end_time.strftime("%H:%M")
    duration_text = f"{hours:02d}:{minutes:02d}"

    print(f"Tööpäeva kestus: {duration_text}")

    write_header = not RESULTS_FILE.exists() or RESULTS_FILE.stat().st_size == 0
    with RESULTS_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";", lineterminator="\n")
        if write_header:
            writer.writerow(RESULTS_HEADER)
        writer.writerow(
            [
                *(person[column] for column in CSV_COLUMNS),
                work_date.strftime("%d.%m.%Y"),
                start_text,
                end_text,
                duration_text,
            ]
        )


if __name__ == "__main__":
    main()
