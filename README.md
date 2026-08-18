# AI 신용대출 연체 위험 예측 데이터 파이프라인

신용대출 고객의 연체 위험 예측 모델에 전달할 학습데이터를 생성하는 ETL 파이프라인입니다.

10개의 합성 원천 CSV를 수집·병합하고 데이터 품질을 검증한 뒤, 연체 위험 분석에 필요한 파생변수를 생성하여 AI 학습용 CSV로 저장합니다.

> 본 프로젝트의 데이터는 실제 고객정보가 아닌 합성데이터이며, 실제 금융 의사결정에 사용할 수 없습니다.

## 데이터 처리 흐름

```text
원천 CSV 10개
    ↓
Extract
    ↓
Validate
    ↓
Transform
    ↓
Load
    ├── 전체 가공데이터
    └── AI 학습용 데이터
```

### Extract

* `data/raw`의 CSV 파일을 패턴 기반으로 탐색
* 여러 CSV를 하나의 pandas DataFrame으로 병합
* 현재 기준 총 100,000건 처리

### Validate

* 필수 컬럼 누락 및 예상하지 않은 컬럼 검사
* 컬럼 순서 및 자료형 검사
* 결측치 검사
* 고객 ID 형식 및 중복 검사
* 금액 컬럼의 양수 여부 검사
* 연소득·연지출 계산 관계 검사
* 총부채와 대출잔액 관계 검사
* 신용점수 및 과거 연체 횟수 범위 검사
* target 값과 클래스 구성 검사

### Transform

다음 파생변수를 생성합니다.

| 파생변수                          | 계산식              |
| ----------------------------- | ---------------- |
| `expense_to_income_ratio`     | 월지출 ÷ 월소득        |
| `debt_to_annual_income_ratio` | 총부채 ÷ 연소득        |
| `loan_to_annual_income_ratio` | 대출잔액 ÷ 연소득       |
| `payment_to_income_ratio`     | 월상환액 ÷ 월소득       |
| `debt_to_asset_ratio`         | 총부채 ÷ 총자산        |
| `monthly_disposable_income`   | 월소득 − 월지출 − 월상환액 |

### Load

두 종류의 CSV를 저장합니다.

* `data/processed/credit_risk_processed.csv`

  * 원천 컬럼과 파생변수를 모두 포함한 내부 가공데이터
* `data/output/credit_risk_ai_dataset.csv`

  * 중복 정보를 제거한 AI 담당자 전달용 데이터

AI 전달 데이터에서는 월 단위 값과 완전히 중복되는 `annual_income`, `annual_expense`를 제외합니다.

## 원천데이터 컬럼

| 컬럼                     | 의미                |
| ---------------------- | ----------------- |
| `customer_id`          | 가상 고객 식별자         |
| `monthly_income`       | 월소득               |
| `annual_income`        | 연소득               |
| `monthly_expense`      | 월지출               |
| `annual_expense`       | 연지출               |
| `total_assets`         | 총자산               |
| `total_debt`           | 총부채               |
| `loan_balance`         | 현재 대출잔액           |
| `monthly_loan_payment` | 월 대출상환액           |
| `credit_score`         | 신용점수              |
| `past_overdue_count`   | 기준 시점 이전 과거 연체 횟수 |
| `target`               | 향후 연체 발생 여부       |

`target`은 다음과 같이 정의합니다.

```text
0: 향후 90일 이내 30일 이상 연체가 발생하지 않음
1: 향후 90일 이내 30일 이상 연체 발생
```

현재 데이터 분포:

```text
전체 데이터: 100,000건
비연체 고객: 91,576건
연체 고객: 8,424건
연체 비율: 8.42%
```

## 프로젝트 구조

```text
ai-credit-risk-pipeline/
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
├── logs/
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── validate.py
│   ├── transform.py
│   └── load.py
├── tests/
├── pipeline.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 개발환경

* Windows 11
* WSL2 Ubuntu
* Python 3.12
* pandas 3.0
* Git/GitHub

## 실행 방법

### 가상환경 생성 및 활성화

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 라이브러리 설치

```bash
python -m pip install -r requirements.txt
```

### 전체 ETL 실행

현재는 Load 모듈을 실행하면 Extract부터 Load까지 순차적으로 실행됩니다.

```bash
python -m src.load
```

단계별 실행도 가능합니다.

```bash
python -m src.extract
python -m src.validate
python -m src.transform
python -m src.load
```

## AI 모델 사용 시 주의사항

* `customer_id`는 고객 식별용이므로 모델 입력에서 제외합니다.
* `target`은 모델이 예측해야 하는 정답 컬럼이므로 입력 피처에서 제외합니다.
* 연체 비율이 8.42%로 불균형하므로 데이터 분할 시 층화 분할을 권장합니다.
* 정확도뿐 아니라 Precision, Recall, F1, ROC-AUC, PR-AUC 등을 함께 평가해야 합니다.
* 합성데이터의 모델 성능은 실제 금융데이터의 성능을 보장하지 않습니다.

## 향후 확장 계획

* `pipeline.py`를 통한 전체 ETL 실행 구조 통합
* pytest 기반 데이터 품질 테스트
* MySQL 운영 원천데이터 연동
* PostgreSQL AI 피처 및 예측 결과 적재
* Airflow 기반 정기 배치 실행
* 고객별 연체 위험도 이력 관리
* 모델 버전 및 배치 실행 이력 관리
