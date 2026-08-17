from pathlib import Path

import pandas as pd

DEFAULT_RAW_DIR = Path("data/raw")
FILE_PATTERN = "credit_risk_raw_part_*.csv"

# data/raw에 있는 csv 파일을 읽고 DataFrame 생성 
def extract_data(
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> pd.DataFrame: 

    raw_path = Path(raw_dir)

    if not raw_path.exists():
        raise FileNotFoundError(
            f"원천데이터 폴더를 찾을 수 없습니다.: {raw_path}"
        )

    csv_files = sorted(
        raw_path.glob(FILE_PATTERN)
    )

    if not csv_files:
        raise ValueError(
            f"CSV 파일을 찾을 수 없습니다: "
            f"{raw_path / FILE_PATTERN}"
        )   

    print(f"[EXTRACT] 발견한 CSV 파일 수 : {len(csv_files)}")

    dataframes = []

    for csv_file in csv_files:
        print(f"[EXTRACT] 파일 읽는 중 : {csv_file.name}")

        dataframe = pd.read_csv(
            csv_file,
            encoding="utf-8-sig",
        )

        dataframes.append(dataframe)

    combined_dataframe = pd.concat(
        dataframes,
        ignore_index=True
    )

    return combined_dataframe

if __name__ == "__main__":
    extracted_dataframe = extract_data()

    row_count, column_count = extracted_dataframe.shape

    print()
    print("[EXTRACT] 완료")
    print(f"[EXTRACT] 전체 행 수: {row_count}")
    print(f"[EXTRACT] 전체 컬럼 수: {column_count}")
    print()
    print(extracted_dataframe.head())

