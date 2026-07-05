"""
example_usage.py -- Demonstrates the CompetitorPriceClient SDK.
"""
from client import CompetitorPriceClient

def main():
    client = CompetitorPriceClient()

    our_products = [
        {"id":"P001","name":"Vitamin C Serum 30ml","price":34.99,"cost":7.00,"min_price":18.00},
        {"id":"P002","name":"Hyaluronic Moisturizer","price":28.99,"cost":6.50,"min_price":15.00},
        {"id":"P003","name":"SPF 50 Sunscreen","price":19.99,"cost":5.00,"min_price":12.00},
        {"id":"P004","name":"Retinol Night Cream","price":44.99,"cost":11.00,"min_price":22.00},
    ]

    competitor_data = [
        {"competitor":"BeautyMart","product_id":"P001","price":32.99,"in_stock":True},
        {"competitor":"GlowShop","product_id":"P001","price":31.50,"in_stock":True},
        {"competitor":"SkincareHub","product_id":"P001","price":35.99,"in_stock":False},
        {"competitor":"BeautyMart","product_id":"P002","price":26.99,"in_stock":True},
        {"competitor":"GlowShop","product_id":"P002","price":29.50,"in_stock":True},
        {"competitor":"BeautyMart","product_id":"P003","price":17.99,"in_stock":True},
        {"competitor":"SkincareHub","product_id":"P003","price":21.99,"in_stock":True},
        {"competitor":"GlowShop","product_id":"P004","price":49.99,"in_stock":True},
        {"competitor":"BeautyMart","product_id":"P004","price":46.50,"in_stock":True},
    ]

    print("[Competitor Price Monitor -- Match Strategy]")
    result = client.analyze(our_products, competitor_data, strategy="match")

    ms = result["market_summary"]
    print(f"Products Analyzed: {ms['products_analyzed']} | Actions Needed: {ms['actions_needed']} | Avg Gap: {ms['avg_price_gap_pct']}%")
    print(f"Price Leaders: {ms['price_leaders']} | Competitive: {ms['competitive']} | Above Market: {ms['above_market']}")

    print(f"\nProduct Analysis:")
    for a in result["analysis"]:
        print(f"  {a['name']}")
        print(f"    Our Price: ${a['our_price']} | Lowest Comp: ${a.get('lowest_competitor_price','N/A')} | Market Avg: ${a.get('market_avg_price','N/A')}")
        print(f"    Gap: {a.get('price_gap_pct',0):+.1f}% | Position: {a['position']} | Target: ${a.get('target_price','N/A')}")

    if result["repricing_actions"]:
        print(f"\nRepricing Actions:")
        for action in result["repricing_actions"]:
            print(f"  [{action['urgency'].upper()}] {action['name']}: ${action['current_price']} -> ${action['recommended_price']} ({action['change_pct']:+.1f}%)")
            print(f"    Reason: {action['reason']}")

if __name__ == "__main__":
    main()
