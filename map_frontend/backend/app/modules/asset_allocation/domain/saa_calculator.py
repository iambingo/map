"""
modules/asset_allocation/domain/saa_calculator.py
纯 Python 战略资产配置规则引擎（零外部依赖，极易单元测试）。
"""
from dataclasses import dataclass


@dataclass
class AllocationInput:
    risk_level: int  # 1-5
    total_amount: float
    constraints: dict  # 上下限约束


@dataclass
class AllocationResult:
    weights: dict[str, float]  # asset_class -> weight
    expected_return: float
    expected_volatility: float


def calculate_saa(input_data: AllocationInput) -> AllocationResult:
    """
    战略资产配置权重计算主入口。
    输入输出均为纯 Python 对象，不依赖 DB Session / HTTP Request。
    """
    raise NotImplementedError
