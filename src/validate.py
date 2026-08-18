import pandas as pd
from pandas.api.types import is_numeric_dtype

from src.extract import extract_data

EXPECTED_COLUMNS = [
    "customer_id",
    "monthly_income",
    "annual_income",
    "monthly_expense",
    "annual_expense",
    "total_assets",
    "total_debt",
    "loan_balance",
    "monthly_loan_payment",
    "credit_score",
    "past_overdue_count",
    "target",
]

NUMERIC_COLUMNS = [
    "monthly_income",
    "annual_income",
    "monthly_expense",
    "annual_expense",
    "total_assets",
    "total_debt",
    "loan_balance",
    "monthly_loan_payment",
    "credit_score",
    "past_overdue_count",
    "target",
]

POSITIVE_COLUMNS = [
    "monthly_income",
    "annual_income",
    "monthly_expense",
    "annual_expense",
    "total_assets",
    "total_debt",
    "loan_balance",
    "monthly_loan_payment",
]

def validate_data(dataframe: pd.DataFrame) -> None:
    
    # EXTRACT 단계에서 생성된 DataFrame 품질 검사
    

    errors = []

    # 1. 빈데이터 검사
    if dataframe.empty:
        raise ValueError(
            "[VALIDATE] 데이터가 비어있습니다."
        )

    # 2. 컬럼 구조 검사
    actual_columns = dataframe.columns.to_list()

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in EXPECTED_COLUMNS
    ]

    if missing_columns:
        errors.append(
            f"필수 컬럼 누락: {missing_columns}"
        )

    if unexpected_columns:
        errors.append(
            f"예상하지 않은 컬럼 존재: {unexpected_columns}"
        )

    if errors:
        error_message = "\n- ".join(errors)

        raise ValueError(
            f"[VALIDATE] 컬럼 구조 검증 실패 \n- "
            f"{error_message}"
        )

    # 3. 컬럼 순서 검사
    if actual_columns != EXPECTED_COLUMNS:
        errors.append(
            "컬럼 순서가 데이터 명세와 일치하지 않습니다."
        )

    # 4. 결측치 검사
    null_counts = dataframe.isna().sum()
    columns_with_null = null_counts[
        null_counts > 0
    ]

    if not columns_with_null.empty:
        errors.append(
            f"결측치 발견: "
            f"{columns_with_null.to_dict()}"
        )

    # 5. 고객 ID 중복 검사
    duplicate_count = dataframe[
        "customer_id"
    ].duplicated().sum()

    if duplicate_count > 0:
        errors.append(
            f"고객 ID 중복: {duplicate_count:,}건"
        )

    # 6. 고객 ID 형식 검사
    invalid_customer_id_count = (
        ~dataframe["customer_id"]
        .astype(str)
        .str.fullmatch(r"C\d{6}")
    ).sum()

    if invalid_customer_id_count > 0:
        errors.append(
            f"고객 ID 형식 오류:"
            f"{invalid_customer_id_count:,}건"
        )

    # 7. 숫자형 컬럼 자료형 검사
    invalid_numeric_columns = [
        column
        for column in NUMERIC_COLUMNS
        if not is_numeric_dtype(dataframe[column])
    ]

    if invalid_numeric_columns:
        errors.append(
            f"숫자형이 아닌 컬럼: "
            f"{invalid_numeric_columns}"
        )

        error_message = "\n- ".join(errors)

        raise ValueError(
            f"[VALIDATE] 자료형 검증 실패\n- "
            f"{error_message}"
        )

    # 8. 양수 컬럼 검사
    for column in POSITIVE_COLUMNS:
        invalid_count = (
            dataframe[column] <= 0
        ).sum()

        if invalid_count > 0:
            errors.append(
                f"{column}이 0 이하: "
                f"{invalid_count:,}건"
            )

    # 9. 연소득 계산 관계 검사
    annual_income_mismatch = (
        dataframe["annual_income"]
        != dataframe["monthly_income"] * 12
    ).sum()

    if annual_income_mismatch > 0:
        errors.append(
            f"연소득 계산 불일치: "
            f"{annual_income_mismatch:,}건"
        )

    # 10. 연지출 계산 관계 검사
    annual_expense_mismatch = (
        dataframe["annual_expense"]
        != dataframe["monthly_expense"] * 12
    ).sum()

    if annual_expense_mismatch > 0:
        errors.append(
            f"연지출 계산 불일치: "
            f"{annual_expense_mismatch:,}건"
        )

    # 11. 총 부채와 대출잔액 관계 검사
    debt_mismatch = (
        dataframe["total_debt"]
        < dataframe["loan_balance"]
    ).sum()

    if debt_mismatch > 0:
        errors.append(
            f"대출 잔액이 총부채보다 큰 데이터: "
            f"{debt_mismatch:,}건"
        )

    # 12. 신용점수 범위 검사
    invalid_credit_score_count = (
        ~dataframe["credit_score"]
        .between(450, 950)
    ).sum()

    if invalid_credit_score_count > 0:
        errors.append(
            f"신용점수 범위 오류: "
            f"{invalid_credit_score_count:,}건"
        )

    # 13. 과거 연체 횟수 범위 검사
    invalid_overdue_count = (
        ~dataframe["past_overdue_count"]
        .between(0, 9)
    ).sum()

    if invalid_overdue_count > 0:
        errors.append(
            f"과거 연체 횟수 범위 오류: "
            f"{invalid_overdue_count:,}건"
        )

    # 14. target 값 검사
    invalid_target_count = (
        ~dataframe["target"].isin([0, 1])
    ).sum()

    if invalid_target_count > 0:
        errors.append(
            f"target 값 오류: "
            f"{invalid_target_count:,}건"
        )

    # 15. target에 0과 1이 모두 존재하는지 검사
    target_values = set(
        dataframe["target"].unique()
    )

    if target_values != {0, 1}:
        errors.append(
            f"target 클래스 부족: "
            f"{sorted(target_values)}"
        )

    # 오류가 하나라도 발생하면 중단
    if errors:
        error_message = "\n- ".join(errors)

        raise ValueError(
            f"[VALIDATE] 데이터 품질 검증 실패\n- "
            f"{error_message}" 
        )

    target_counts = (
        dataframe["target"]
        .value_counts()
        .sort_index()
    )

    target_rate = (
        dataframe["target"].mean() * 100
    )

    print()
    print("[VALIDATE] 데이터 품질 검증 완료")
    print(
        f"[VALIDATE] 전체 데이터: "
        f"{len(dataframe):,}건"
    )
    print(
        f"[VALIDATE] 비연체 고객: "
        f"{target_counts.get(0, 0):,}건"
    )
    print(
        f"[VALIDATE] 연체 고객: "
        f"{target_counts.get(1, 0):,}건"
    )
    print(
        f"[VALIDATE] 연체 비율: "
        f"{target_rate:.2f}%"
    )

if __name__ == "__main__":
    extract_dataframe = extract_data()
    validate_data(extract_dataframe)

