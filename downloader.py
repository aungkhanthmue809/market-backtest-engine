import zipfile
import csv
import os
import shutil
from pathlib import Path
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dateutil.relativedelta import relativedelta

def download_data(symbol="BTC"):
    SYMBOL = f"{symbol.upper()}USDT"
    INTERVALS = ["15m", "1h"]
    FOLDER_NAMES = {"15m": "ltf", "1h": "htf"}

    DOWNLOAD_DIR = Path("data_shelf")

    WORKERS = 8

    if DOWNLOAD_DIR.exists():
        print(f"Clearing {DOWNLOAD_DIR}...")
        shutil.rmtree(DOWNLOAD_DIR)

    DOWNLOAD_DIR.mkdir(exist_ok=True)


    today = date.today()

    last_month = today.replace(day=1) - relativedelta(months=1)

    start_month = (
        last_month
        - relativedelta(years=7)
        + relativedelta(months=1)
    )

    months = []

    current = start_month

    while current <= last_month:
        months.append(current)
        current += relativedelta(months=1)


    print(
        f"Downloading from {start_month} "
        f"to {last_month}"
    )

    print(f"Total months: {len(months)}")


    def fix_timestamp(csv_path):

        temp_path = csv_path.with_suffix(".tmp")

        try:

            with open(
                csv_path,
                "r",
                newline="",
                encoding="utf-8"
            ) as input_file:

                reader = csv.reader(input_file)

                with open(
                    temp_path,
                    "w",
                    newline="",
                    encoding="utf-8"
                ) as output_file:

                    writer = csv.writer(output_file)

                    for row in reader:

                        if row:
                            row[0] = row[0][:13]

                        writer.writerow(row)

            os.replace(temp_path, csv_path)

            print(
                f"[TIMESTAMP FIXED] "
                f"{csv_path.name}"
            )

        except Exception as e:

            print(
                f"[ERROR TIMESTAMP] "
                f"{csv_path.name}: {e}"
            )

            if temp_path.exists():
                temp_path.unlink()


    def download_and_extract(interval, month):

        year_month = month.strftime("%Y-%m")

        zip_filename = (
            f"{SYMBOL}-{interval}-{year_month}.zip"
        )

        url = (
            f"https://data.binance.vision/"
            f"data/spot/monthly/klines/"
            f"{SYMBOL}/{interval}/{zip_filename}"
        )

        output_dir = DOWNLOAD_DIR / FOLDER_NAMES[interval]
        output_dir.mkdir(exist_ok=True)

        zip_path = output_dir / zip_filename

        if zip_path.exists():

            print(f"[ZIP EXISTS] {zip_filename}")

        else:

            try:

                response = requests.get(
                    url,
                    timeout=60
                )

                if response.status_code == 404:

                    print(
                        f"[MISSING] {zip_filename}"
                    )

                    return

                response.raise_for_status()

                zip_path.write_bytes(
                    response.content
                )

                print(
                    f"[DOWNLOADED] {zip_filename}"
                )

            except Exception as e:

                print(
                    f"[ERROR DOWNLOAD] "
                    f"{zip_filename}: {e}"
                )

                return

        extracted_path = None

        try:

            with zipfile.ZipFile(
                zip_path,
                "r"
            ) as z:

                csv_files = [
                    name
                    for name in z.namelist()
                    if name.endswith(".csv")
                ]

                if not csv_files:

                    print(
                        f"[NO CSV] {zip_filename}"
                    )

                    return

                csv_name = csv_files[0]

                extracted_path = (
                    output_dir /
                    Path(csv_name).name
                )

                if extracted_path.exists():

                    print(
                        f"[SKIP EXTRACT] "
                        f"{extracted_path.name}"
                    )

                else:

                    with z.open(csv_name) as source:

                        with open(
                            extracted_path,
                            "wb"
                        ) as target:

                            target.write(
                                source.read()
                            )

                    print(
                        f"[EXTRACTED] "
                        f"{extracted_path.name}"
                    )

        except Exception as e:

            print(
                f"[ERROR EXTRACT] "
                f"{zip_filename}: {e}"
            )

            return


        if extracted_path is not None:

            fix_timestamp(extracted_path)


        if extracted_path is not None and extracted_path.exists():

            try:

                zip_path.unlink()

                print(
                    f"[DELETED ZIP] "
                    f"{zip_filename}"
                )

            except Exception as e:

                print(
                    f"[ERROR DELETE] "
                    f"{zip_filename}: {e}"
                )


    for interval in INTERVALS:

        print("\n" + "=" * 50)
        print(f"PROCESSING {interval}")
        print("=" * 50)

        with ThreadPoolExecutor(
            max_workers=WORKERS
        ) as executor:

            futures = [
                executor.submit(
                    download_and_extract,
                    interval,
                    month
                )
                for month in months
            ]

            for future in as_completed(futures):

                try:

                    future.result()

                except Exception as e:

                    print(
                        f"[THREAD ERROR] {e}"
                    )
    print("\nAll downloads and extractions finished.")
if __name__ == "__main__":
    download_data()

