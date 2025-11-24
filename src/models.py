from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
import time
import random

class MarketRiskSnapshot(BaseModel):
    symbol: str
    timestamp: int
    price: Decimal
    volume: Decimal

    dailyPnl: Optional[Decimal] = None
    monthlyPnl: Optional[Decimal] = None
    var1at95: Optional[Decimal] = None
    var1at99: Optional[Decimal] = None
    var10at95: Optional[Decimal] = None
    var10at99: Optional[Decimal] = None
    volatility30: Optional[Decimal] = None
    alpha: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    riskScore: Optional[int] = None

    aiSentiment: Optional[str] = None
    aiSummary: Optional[str] = None
    aiConfidenceScore: Optional[float] = None

default_MarketRiskSnapshot = MarketRiskSnapshot(
    symbol="TD",
    timestamp=int(time.time() * 1000),
    price=Decimal(str(round(random.uniform(78.0, 82.0), 2))),  # TD stock price range
    volume=Decimal(str(random.randint(50000, 200000))),  # intraday traded volume

    dailyPnl=Decimal(str(round(random.uniform(-2_000_000, 2_000_000), 2))),
    monthlyPnl=Decimal(str(round(random.uniform(-10_000_000, 20_000_000), 2))),

    var1at95=Decimal(str(round(random.uniform(500_000, 2_500_000), 2))),
    var1at99=Decimal(str(round(random.uniform(700_000, 3_500_000), 2))),
    var10at95=Decimal(str(round(random.uniform(1_000_000, 4_000_000), 2))),
    var10at99=Decimal(str(round(random.uniform(1_500_000, 6_000_000), 2))),

    volatility30=Decimal(str(round(random.uniform(0.12, 0.28), 4))),  # 12–28%
    alpha=Decimal(str(round(random.uniform(-0.5, 0.5), 4))),
    beta=Decimal(str(round(random.uniform(0.8, 1.3), 4))),

    riskScore=random.randint(1, 100)
)
