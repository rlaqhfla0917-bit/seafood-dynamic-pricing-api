def calculate_price(seafood, rules):
    """
    발표자료의 조정률(+20%, -5%, -10%)과 응답 예시(20,000 -> 21,000)를
    함께 만족시키기 위해 '기준가 대비 조정률 합산' 방식으로 재구현했습니다.

    자세한 근거는 docs/SOURCE_NOTES.md 참고.
    """
    base = seafood.base_price
    adjustment_rate = 0.0
    adjustments = {}

    if rules.apply_freshness_rule:
        if seafood.freshness_grade == "A":
            adjustment_rate += 0.20
            adjustments["freshness"] = "+20%"
        elif seafood.freshness_grade == "C":
            adjustment_rate -= 0.15
            adjustments["freshness"] = "-15%"
        else:
            adjustments["freshness"] = "0%"

    if rules.apply_catch_rule:
        if seafood.catch_amount > 100:
            adjustment_rate -= 0.05
            adjustments["catch"] = "-5%"
        elif seafood.catch_amount < 30:
            adjustment_rate += 0.05
            adjustments["catch"] = "+5%"
        else:
            adjustments["catch"] = "0%"

    if rules.apply_stock_rule:
        if seafood.stock_quantity > 50:
            adjustment_rate -= 0.10
            adjustments["stock"] = "-10%"
        elif seafood.stock_quantity < 10:
            adjustment_rate += 0.10
            adjustments["stock"] = "+10%"
        else:
            adjustments["stock"] = "0%"

    # 발표자료에는 deadline discount의 구체 규칙이 없어 플래그만 보존합니다.
    if rules.apply_deadline_discount:
        adjustments["deadline"] = "NOT_DEFINED_IN_SOURCE"

    final_price = int(round(base * (1 + adjustment_rate)))
    return final_price, adjustments
