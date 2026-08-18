from pathlib import Path

import pandas as pd

from src.extract import extract_data
from src.validate import validate_data
from src.transform import transform_data

PROCESSED_FILE_PATH = Path(
    "data/processed/credit_risk_processed.csv"
)

AI_OUTPUT_FILE_PATH = Path(
    "data/output/credit_risk_ai_dataset.csv"
)

AI_EXCLUDED_COLUMNS = [
    "annual_income",
    "annual_expense"
]

def save_csv(
        dataframe: pd.DataFrame,
        output_path: Path,
) -> None:
    # Dataframe을 임시 파일에 저장 후 csv로 최종 교체

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = output_path.with_suffix(
        ".csv.tmp"
    )

    dataframe.to_csv(
        temporary_path,
        index=False,
        encoding="utf-8-sig",
    )

    temporary_path.replace(output_path)

def load_data(
    dataframe: pd.DataFrame,
    processed_path: Path = PROCESSED_FILE_PATH,
    ai_output_path: Path = AI_OUTPUT_FILE_PATH,
) -> tuple[Path, Path]:
    # 전체 가공 데이터, AI 전달용 데이터를 각각 csv 파일로 저장

    # 전체 가공 데이터
    processed_dataframe = dataframe.copy()

    # AI 전달 데이터
    ai_output_dataframe = dataframe.drop(
        columns=AI_EXCLUDED_COLUMNS
    ).copy()

    save_csv(
        processed_dataframe,
        processed_path,
    )

    save_csv(
        ai_output_dataframe,
        ai_output_path,
    )

    print()
    print("[LOAD] CSV 저장 완료")
    print(
        f"[LOAD] 전체 가공 데이터: "
        f"{processed_path}"
    )
    print(
        f"[LOAD] 전체 가공 데이터 크기: "
        f"{processed_path.stat().st_size / 1024 / 1024:.2f}MB"
    )
    print(
        f"[LOAD] AI 전달 데이터 행 수: "
        f"{len(ai_output_dataframe):,}개"
    )
    print(
        f"[LOAD] AI 전달 데이터 컬럼 수: "
        f"{len(ai_output_dataframe.columns)}개"
    )

    return processed_path, ai_output_path


if __name__ == "__main__":
    extracted_dataframe = extract_data()

    validate_data(extracted_dataframe)

    transformed_dataframe = transform_data(
        extracted_dataframe
    )

    load_data(transformed_dataframe)