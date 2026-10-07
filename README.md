# Seafood Dynamic Pricing API
### 신선도 · 어획량 · 재고량 기반 수산물 실시간 가격 조정 서비스

KT AIVLE School 팀 프로젝트 발표자료에 포함된 **API 명세·프로젝트 구조·가격 규칙·Swagger 검증 내용**을 바탕으로 GitHub 포트폴리오용으로 재구현한 버전입니다.

> 수산물 가격을 전화·메신저·엑셀로 수동 관리하던 흐름을  
> **데이터 입력 → 가격 자동 계산 → 주문/재고 반영 → API 응답**으로 연결하는 것이 핵심입니다.

## 주요 기능

- 수산물 상품 등록·조회
- 당일 어획량 / 입고량 및 재고 변경
- 신선도 등급 변경
- 신선도·어획량·재고량 기반 판매가 자동 계산
- 주문 생성 및 재고 자동 차감
- 재고 부족 시 `409 Conflict`
- 주문 상태 관리
- Swagger UI 자동 문서화
- SQLite 로컬 실행 / PostgreSQL(RDS) 전환 가능

## API

| Method | Endpoint | 설명 |
|---|---|---|
| GET | `/health` | 서버 상태 확인 |
| POST | `/api/v1/seafoods` | 상품 등록 |
| GET | `/api/v1/seafoods` | 상품 목록 조회 |
| GET | `/api/v1/seafoods/{seafood_id}` | 상품 상세 조회 |
| PATCH | `/api/v1/seafoods/{seafood_id}/catch` | 어획량/입고량 및 재고 변경 |
| PATCH | `/api/v1/seafoods/{seafood_id}/freshness` | 신선도 등급 변경 |
| POST | `/api/v1/seafoods/{seafood_id}/price-calculate` | 판매가 자동 계산 |
| POST | `/api/v1/orders` | 주문 생성 |
| GET | `/api/v1/orders` | 주문 목록 조회 |
| PATCH | `/api/v1/orders/{order_id}/status` | 주문 상태 변경 |

## 가격 조정 규칙

- 신선도 A: `+20%`
- 신선도 C: `-15%`
- 어획량 > 100: `-5%`
- 어획량 < 30: `+5%`
- 재고 > 50: `-10%`
- 재고 < 10: `+10%`

발표자료의 응답 예시인 **기본가 20,000원 → 최종가 21,000원**을 재현하도록 기준가 대비 조정률을 합산합니다.

## Project Structure

```text
seafood-dynamic-pricing-api/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── price_engine.py
│   └── routes/
│       ├── seafoods.py
│       └── orders.py
├── tests/
│   └── test_api.py
├── docs/
│   └── SOURCE_NOTES.md
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Run

```bash
git clone https://github.com/<YOUR_ID>/seafood-dynamic-pricing-api.git
cd seafood-dynamic-pricing-api

python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install & run:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Test:

```bash
pytest -q
```

## Cloud Architecture from Project

발표 프로젝트에서는 다음 구조를 설계했습니다.

```text
Internet
  ↓
ALB
  ↓
EC2 (nginx + uvicorn/FastAPI)
  ↓
PostgreSQL RDS
  ↓
CloudWatch
```

Public / Private Subnet을 분리하고 DB는 EC2를 통해서만 접근하도록 설계했습니다.

## Source Fidelity

이 저장소는 발표자료를 그대로 복사한 원본 저장소가 아니라, **발표자료에 기록된 구조와 동작을 기준으로 포트폴리오용으로 재구현한 코드**입니다.  
자료 안에서 서로 다르게 표현된 부분은 `docs/SOURCE_NOTES.md`에 별도로 기록했습니다.
