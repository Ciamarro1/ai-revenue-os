from typing import List, Dict, Any
from src.revenue_os.connectors.base_adapter import BaseMarketplaceAdapter
from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity

class HotmartAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "Hotmart"

    def fetch_raw_opportunities(self, niche: str) -> List[Dict[str, Any]]:
        return [
            {"product_id": "HOT-101", "name": "Formação Master em Produtividade", "comm_percent": 65, "comm_value_brl": 250.0, "temperature": 85, "epc_brl": 28.50},
            {"product_id": "HOT-102", "name": "Organização Pessoal com Notion", "comm_percent": 60, "comm_value_brl": 120.0, "temperature": 70, "epc_brl": 15.20}
        ]

    def normalize(self, raw_data: Dict[str, Any], niche: str) -> RevenueOpportunity:
        comm_usd = round(raw_data["comm_value_brl"] / 5.0, 2)
        epc_usd = round(raw_data["epc_brl"] / 5.0, 2)
        return RevenueOpportunity(
            id=raw_data["product_id"],
            marketplace="Hotmart",
            product_name=raw_data["name"],
            category=niche,
            commission_rate=raw_data["comm_percent"] / 100.0,
            avg_commission_usd=comm_usd,
            competition_index=round(raw_data["temperature"] / 100.0 * 0.5, 2),
            epc_usd=epc_usd,
            confidence_score=0.92,
            target_audience=niche
        )


class ClickBankAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "ClickBank"

    def fetch_raw_opportunities(self, niche: str) -> List[Dict[str, Any]]:
        return [
            {"item_code": "CB-909", "title": "AI Content Automation 2026", "gravity": 145.0, "initial_sale_usd": 68.0, "average_epc_usd": 5.80}
        ]

    def normalize(self, raw_data: Dict[str, Any], niche: str) -> RevenueOpportunity:
        return RevenueOpportunity(
            id=raw_data["item_code"],
            marketplace="ClickBank",
            product_name=raw_data["title"],
            category=niche,
            commission_rate=0.70,
            avg_commission_usd=raw_data["initial_sale_usd"],
            competition_index=min(0.9, round(raw_data["gravity"] / 200.0, 2)),
            epc_usd=raw_data["average_epc_usd"],
            confidence_score=0.88,
            target_audience=niche
        )


class AmazonAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "Amazon"

    def fetch_raw_opportunities(self, niche: str) -> List[Dict[str, Any]]:
        return [
            {"asin": "B08N5WRWNW", "item_name": "Ergonomic Office Chair Mesh", "commission_rate_pct": 10.0, "price_usd": 220.0, "estimated_epc": 3.10}
        ]

    def normalize(self, raw_data: Dict[str, Any], niche: str) -> RevenueOpportunity:
        comm_usd = round(raw_data["price_usd"] * (raw_data["commission_rate_pct"] / 100.0), 2)
        return RevenueOpportunity(
            id=raw_data["asin"],
            marketplace="Amazon",
            product_name=raw_data["item_name"],
            category=niche,
            commission_rate=raw_data["commission_rate_pct"] / 100.0,
            avg_commission_usd=comm_usd,
            competition_index=0.25,
            epc_usd=raw_data["estimated_epc"],
            confidence_score=0.96,
            target_audience=niche
        )


class DigistoreAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "Digistore24"

    def fetch_raw_opportunities(self, niche: str) -> List[Dict[str, Any]]:
        return [
            {"product_no": "DIGI-304", "name": "Digital Planner 2026 Edition", "commission_pct": 50.0, "net_payout_usd": 24.50, "epc": 3.90}
        ]

    def normalize(self, raw_data: Dict[str, Any], niche: str) -> RevenueOpportunity:
        return RevenueOpportunity(
            id=raw_data["product_no"],
            marketplace="Digistore24",
            product_name=raw_data["name"],
            category=niche,
            commission_rate=raw_data["commission_pct"] / 100.0,
            avg_commission_usd=raw_data["net_payout_usd"],
            competition_index=0.30,
            epc_usd=raw_data["epc"],
            confidence_score=0.90,
            target_audience=niche
        )


class GumroadAdapter(BaseMarketplaceAdapter):
    @property
    def marketplace_name(self) -> str:
        return "Gumroad"

    def fetch_raw_opportunities(self, niche: str) -> List[Dict[str, Any]]:
        return [
            {"product_permalink": "GUM-501", "name": "Ultimate Social Media Kit", "affiliate_fee_pct": 40.0, "price_usd": 39.0, "epc_usd": 2.90}
        ]

    def normalize(self, raw_data: Dict[str, Any], niche: str) -> RevenueOpportunity:
        comm_usd = round(raw_data["price_usd"] * (raw_data["affiliate_fee_pct"] / 100.0), 2)
        return RevenueOpportunity(
            id=raw_data["product_permalink"],
            marketplace="Gumroad",
            product_name=raw_data["name"],
            category=niche,
            commission_rate=raw_data["affiliate_fee_pct"] / 100.0,
            avg_commission_usd=comm_usd,
            competition_index=0.20,
            epc_usd=raw_data["epc_usd"],
            confidence_score=0.87,
            target_audience=niche
        )
