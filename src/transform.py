import pandas as pd

from src.extract import extract_data
from src.validate import validate_data

RATIO_COLUMNS = [
    "expense_to_income_ratio",
    "debt_to_annual_income_ratio",
    "loan_to_annual_income_ratio",
    "payment_to_income_ratio",
    "debt_to_asset_ratio",
]

DERIVED_COLUMNS = [
    *RATIO_COLUMNS,
    "monthly_disposable_income",
]

def transform_data(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    # 원천데이터를 AI 학습에 필요한 파생 변수로 변환

    transformed_dataframe = dataframe.copy()

    # 1. 소득 대비 지출 비율 
    transformed_dataframe[
        "expense_to_income_ratio"
    ] = (
        transformed_dataframe["monthly_expense"] 
        / transformed_dataframe["monthly_income"]
    ).round(6)

    # 2. 연소득 대비 총부채 비율
    transformed_dataframe[
        "debt_to_annual_income_ratio"
    ] = (
        transformed_dataframe["total_debt"]
        / transformed_dataframe["annual_income"]
    ).round(6)

    # 3. 연소득 대비 대출잔액 비율
    transformed_dataframe[
        "loan_to_annual_income_ratio"
    ] = (
        transformed_dataframe["loan_balance"]
        / transformed_dataframe["annual_income"]
    ).round(6)

    # 4. 월소득 대비 월상환액 비율
    transformed_dataframe[
        "payment_to_income_ratio"
    ] = (
        transformed_dataframe["monthly_loan_payment"]
        / transformed_dataframe["monthly_income"]
    ).round(6)

    # 5. 총자산 대비 총부채 비율
    transformed_dataframe[
        "debt_to_asset_ratio"
    ] = (
        transformed_dataframe["total_debt"]
        / transformed_dataframe["total_assets"]
    ).round(6)

    # 6. 월 가처분소득
    transformed_dataframe[
        "monthly_disposable_income"
    ] = (
        transformed_dataframe["monthly_income"]
        - transformed_dataframe["monthly_expense"]
        - transformed_dataframe["monthly_loan_payment"]
    )

    # 7. 파생변수 결측치 검사
    derived_null_counts = (
        transformed_dataframe[DERIVED_COLUMNS]
        .isna()
        .sum()
    )

    invalid_derived_columns = derived_null_counts[
        derived_null_counts > 0
    ]

    if not invalid_derived_columns.empty:
        raise ValueError(
            f"[TRANSFORM] 파생변수 결측치 발생: "
            f"{invalid_derived_columns.to_dict()}"
        )

    # target 컬럼을 마지막 위치로
    ordered_columns = [
        column
        for column in transformed_dataframe.columns
        if column != "target"
    ]

    ordered_columns.append("target")

    transformed_dataframe = (
        transformed_dataframe[ordered_columns]
    )

    print()
    print("[TRANSFORM] 파생변수 생성 완료")
    print(
        f"[TRANSFORM] 생성한 파생변수: "
        f"{len(DERIVED_COLUMNS):,}개"
    )
    print(
        f"[TRANSFORM] 전체 행 수: "
        f"{len(transformed_dataframe):,}개"
    )
    print(
        f"[TRANSFORM] 전체 컬럼 수: "
        f"{len(transformed_dataframe.columns):,}개"
    )

    return transformed_dataframe

if __name__ == "__main__":
    extracted_dataframe = extract_data()

    validate_data(extracted_dataframe)

    transformed_dataframe = transform_data(
        extracted_dataframe
    )

    print()
    print(
        transformed_dataframe[
            DERIVED_COLUMNS + ["target"]
        ].head()
    )