# competitor-price-monitor-skill

> **GenPark AI Agent Skill** -- Analyze competitor pricing, detect price gaps, and generate dynamic repricing recommendations.

## Features

- Four pricing strategies: beat / match / premium / value
- Per-product price gap analysis vs lowest and average competitor
- Market position classification: price_leader / competitive / above_average / premium
- Urgency-ranked repricing action list
- Minimum price floor enforcement (cost-based)
- Out-of-stock competitor filtering
- Market summary dashboard

## Quick Start

```python
from client import CompetitorPriceClient

client = CompetitorPriceClient()
result = client.analyze(
    our_products=[{"id":"P1","name":"Serum","price":35,"cost":7,"min_price":18}],
    competitor_data=[{"competitor":"RivalStore","product_id":"P1","price":31.50,"in_stock":True}],
    strategy="match",
)
for action in result["repricing_actions"]:
    print(f"{action['name']}: ${action['current_price']} -> ${action['recommended_price']}")
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
