"""
competitor-price-monitor-skill: Client SDK
Analyze competitor pricing, detect gaps, and generate repricing recommendations.
"""
from __future__ import annotations
from typing import Literal, Optional
from collections import defaultdict

Strategy = Literal["beat", "match", "premium", "value"]

STRATEGY_CONFIG = {
    "beat":    {"target_position": "lowest",  "offset_pct": -0.02, "label": "Beat Lowest Price"},
    "match":   {"target_position": "match",   "offset_pct":  0.00, "label": "Match Lowest Price"},
    "premium": {"target_position": "premium", "offset_pct":  0.10, "label": "Premium Positioning"},
    "value":   {"target_position": "value",   "offset_pct": -0.05, "label": "Value Pricing"},
}


class CompetitorPriceClient:
    """
    SDK for competitor price monitoring and dynamic repricing recommendations.
    """

    def analyze(
        self,
        our_products: list[dict],
        competitor_data: list[dict],
        strategy: Strategy = "match",
    ) -> dict:
        """
        Run competitive price analysis.

        Args:
            our_products:    Our products: [{id, name, price, cost, min_price}].
            competitor_data: Competitor prices: [{competitor, product_id, price, in_stock}].
            strategy:        Pricing strategy.

        Returns:
            dict with analysis, repricing_actions, market_summary
        """
        cfg = STRATEGY_CONFIG.get(strategy, STRATEGY_CONFIG["match"])

        # Group competitor data by product_id
        comp_by_product = defaultdict(list)
        for entry in competitor_data:
            comp_by_product[str(entry.get("product_id", ""))].append(entry)

        analysis = []
        repricing_actions = []

        for product in our_products:
            pid = str(product.get("id", ""))
            our_price = float(product.get("price", 0))
            cost = float(product.get("cost", our_price * 0.5))
            min_price = float(product.get("min_price", cost * 1.05))
            name = product.get("name", pid)

            comp_entries = comp_by_product.get(pid, [])
            in_stock_comps = [e for e in comp_entries if e.get("in_stock", True)]
            comp_prices = [float(e["price"]) for e in in_stock_comps if e.get("price")]

            if not comp_prices:
                analysis.append({
                    "product_id": pid, "name": name, "our_price": our_price,
                    "competitors": 0, "status": "no_data",
                    "market_avg": None, "lowest_comp": None,
                    "price_gap_pct": None, "position": "unknown",
                })
                continue

            market_avg = round(sum(comp_prices) / len(comp_prices), 2)
            lowest_comp = round(min(comp_prices), 2)
            highest_comp = round(max(comp_prices), 2)
            gap_pct = round((our_price - lowest_comp) / lowest_comp * 100, 1)

            # Position
            if our_price <= lowest_comp * 1.01:
                position = "price_leader"
            elif our_price <= market_avg * 1.05:
                position = "competitive"
            elif our_price <= highest_comp:
                position = "above_average"
            else:
                position = "premium"

            # Target price based on strategy
            if strategy == "beat":
                target = max(min_price, lowest_comp * (1 + cfg["offset_pct"]))
            elif strategy == "match":
                target = max(min_price, lowest_comp)
            elif strategy == "premium":
                target = our_price * (1 + abs(cfg["offset_pct"]))
            else:  # value
                target = max(min_price, market_avg * (1 + cfg["offset_pct"]))

            target = round(target, 2)
            price_change = round(target - our_price, 2)
            margin_at_target = round((target - cost) / max(target, 1) * 100, 1)

            analysis.append({
                "product_id": pid, "name": name, "our_price": our_price,
                "competitors": len(comp_entries), "in_stock_competitors": len(in_stock_comps),
                "lowest_competitor_price": lowest_comp,
                "highest_competitor_price": highest_comp,
                "market_avg_price": market_avg,
                "price_gap_pct": gap_pct,
                "position": position,
                "target_price": target,
                "price_change": price_change,
                "margin_at_target_pct": margin_at_target,
                "status": "ok" if abs(price_change) < 0.50 else "action_needed",
            })

            if abs(price_change) >= 0.50:
                direction = "decrease" if price_change < 0 else "increase"
                repricing_actions.append({
                    "product_id": pid, "name": name,
                    "current_price": our_price, "recommended_price": target,
                    "change_usd": price_change, "change_pct": round(price_change / our_price * 100, 1),
                    "direction": direction,
                    "reason": f"{cfg['label']} vs lowest competitor at ${lowest_comp}",
                    "urgency": "high" if abs(gap_pct) > 15 else "medium",
                })

        repricing_actions.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

        market_summary = self._market_summary(analysis, strategy, cfg["label"])

        return {
            "strategy": strategy,
            "strategy_label": cfg["label"],
            "analysis": analysis,
            "repricing_actions": repricing_actions,
            "market_summary": market_summary,
        }

    @staticmethod
    def _market_summary(analysis: list[dict], strategy: str, label: str) -> dict:
        valid = [a for a in analysis if a.get("price_gap_pct") is not None]
        if not valid:
            return {"products_analyzed": len(analysis), "actions_needed": 0}
        price_leaders = sum(1 for a in valid if a["position"] == "price_leader")
        above_avg = sum(1 for a in valid if a["position"] in ("above_average", "premium"))
        avg_gap = round(sum(a["price_gap_pct"] for a in valid) / len(valid), 1)
        return {
            "products_analyzed": len(analysis),
            "products_with_data": len(valid),
            "price_leaders": price_leaders,
            "competitive": sum(1 for a in valid if a["position"] == "competitive"),
            "above_market": above_avg,
            "avg_price_gap_pct": avg_gap,
            "actions_needed": sum(1 for a in analysis if a.get("status") == "action_needed"),
            "strategy": label,
        }
