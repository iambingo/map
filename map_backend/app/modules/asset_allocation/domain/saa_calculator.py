"""
modules/asset_allocation/domain/saa_calculator.py
纯 Python SAA 规则引擎（零外部依赖，极易单元测试）。

算法：基于风险等级的预设权重矩阵 + 约束裁剪 + 归一化。
生产环境可替换为均值-方差优化（scipy.optimize）而无需改动上层接口。
"""
from dataclasses import dataclass, field


# 预设权重矩阵（风险等级 1-5）
# 资产类别：equity_domestic / equity_overseas / fixed_income / alternatives / cash
_BASE_WEIGHTS: dict[int, dict[str, float]] = {
    1: {"equity_domestic": 0.05, "equity_overseas": 0.05, "fixed_income": 0.60, "alternatives": 0.05, "cash": 0.25},
    2: {"equity_domestic": 0.10, "equity_overseas": 0.10, "fixed_income": 0.55, "alternatives": 0.10, "cash": 0.15},
    3: {"equity_domestic": 0.20, "equity_overseas": 0.15, "fixed_income": 0.40, "alternatives": 0.15, "cash": 0.10},
    4: {"equity_domestic": 0.30, "equity_overseas": 0.25, "fixed_income": 0.25, "alternatives": 0.15, "cash": 0.05},
    5: {"equity_domestic": 0.40, "equity_overseas": 0.30, "fixed_income": 0.15, "alternatives": 0.12, "cash": 0.03},
}

# 各资产类别预期参数（年化）
_ASSET_PARAMS: dict[str, dict[str, float]] = {
    "equity_domestic":  {"return": 0.08, "volatility": 0.22},
    "equity_overseas":  {"return": 0.07, "volatility": 0.18},
    "fixed_income":     {"return": 0.04, "volatility": 0.05},
    "alternatives":     {"return": 0.06, "volatility": 0.12},
    "cash":             {"return": 0.02, "volatility": 0.01},
}


@dataclass(frozen=True)
class AllocationInput:
    risk_level: int          # 1-5
    total_amount: float      # 万元
    constraints: dict = field(default_factory=dict)  # {asset_class: {"min": float, "max": float}}


@dataclass(frozen=True)
class AllocationResult:
    weights: dict[str, float]           # asset_class -> weight (sum=1)
    expected_return: float              # 组合预期年化收益率
    expected_volatility: float          # 组合预期年化波动率（简化：加权平均）
    amount_breakdown: dict[str, float]  # asset_class -> 金额（万元）


def calculate_saa(input_data: AllocationInput) -> AllocationResult:
    """
    SAA 权重计算主入口。
    1. 取预设基础权重
    2. 应用约束裁剪（min/max）
    3. 归一化使权重之和为 1
    4. 计算组合预期收益率与波动率
    """
    if input_data.risk_level not in _BASE_WEIGHTS:
        raise ValueError(f"risk_level 必须在 1-5 之间，收到: {input_data.risk_level}")
    if input_data.total_amount <= 0:
        raise ValueError("total_amount 必须大于 0")

    raw = dict(_BASE_WEIGHTS[input_data.risk_level])

    # 应用约束裁剪
    for asset, w in raw.items():
        c = input_data.constraints.get(asset, {})
        lo = float(c.get("min", 0.0))
        hi = float(c.get("max", 1.0))
        raw[asset] = max(lo, min(hi, w))

    # 归一化
    total = sum(raw.values())
    if total <= 0:
        raise ValueError("约束条件导致所有权重为 0，无法归一化")
    weights = {k: round(v / total, 6) for k, v in raw.items()}

    # 组合预期指标（简化加权平均，忽略相关性）
    exp_return = sum(
        weights[a] * _ASSET_PARAMS.get(a, {}).get("return", 0.0)
        for a in weights
    )
    exp_vol = sum(
        weights[a] * _ASSET_PARAMS.get(a, {}).get("volatility", 0.0)
        for a in weights
    )

    amount_breakdown = {a: round(w * input_data.total_amount, 2) for a, w in weights.items()}

    return AllocationResult(
        weights=weights,
        expected_return=round(exp_return, 6),
        expected_volatility=round(exp_vol, 6),
        amount_breakdown=amount_breakdown,
    )
