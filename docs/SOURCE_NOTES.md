# Source Notes

이 저장소는 KT AIVLE School 발표자료의 내용에 근거해 재구현했습니다.

## 확인된 원본 구조
발표자료에는 다음 구조가 명시되어 있습니다.

- `app/main.py`
- `app/models.py`
- `app/schemas.py`
- `app/database.py`
- `app/price_engine.py`
- `app/routes/seafoods.py`
- `app/routes/orders.py`

또한 FastAPI, SQLAlchemy ORM, Swagger 검증, EC2 + ALB + RDS(PostgreSQL) 구조가 제시됩니다.

## 가격 계산 예시의 불일치
발표자료의 코드 예시는 조정률을 순차 곱셈합니다.

- 20,000 × 1.20 × 0.95 × 0.90 = 20,520

하지만 같은 발표자료의 응답 예시는 다음을 제시합니다.

- 기본가 20,000
- 신선도 +20%
- 어획량 -5%
- 재고 -10%
- 최종가 21,000

이 재구현은 **발표자료의 API 응답 예시(21,000원)**를 재현하기 위해 조정률을 기준가 대비 합산하는 방식을 선택했습니다.

## Deadline Discount
`apply_deadline_discount` 필드는 발표자료에 존재하지만 구체적인 할인 규칙은 제시되지 않습니다.  
따라서 이 재구현에서는 값을 보존하되 실제 할인율을 임의로 만들지 않았습니다.
