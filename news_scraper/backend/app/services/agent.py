from typing import Dict, List, Any
import random

class CanvasAgent:
    """
    Mock AI Agent - Returns components in new schema format
    
    This simulates what your real Python AI agent will do:
    1. Analyze user prompt
    2. Determine which components to show
    3. Generate appropriate data for each component
    4. Return in the new dict format: { "comp-1": {...}, "comp-2": {...} }
    """

    def generate_canvas(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate canvas components based on prompt
        
        Args:
            prompt: User's input
            context: Previous conversation history, etc.
            
        Returns:
            Dict with 'response' (text) and 'components' (dict of components)
        """
        prompt_lower = prompt.lower()
        components = {}
        comp_counter = 1
        
        # Risk/Alert keywords
        if any(word in prompt_lower for word in ['risk', 'alert', 'var', 'breach', 'warning']):
            components[f"comp-{comp_counter}"] = {
                "type": "AlertInsights",
                "data": [
                    {
                        "id": "1",
                        "title": "VaR limit breached on Desk A",
                        "timestamp": "10:42 AM",
                        "severity": "critical",
                        "icon": "alert-triangle"
                    },
                    {
                        "id": "2",
                        "title": "Counterparty credit rating under review",
                        "timestamp": "Yesterday",
                        "severity": "warning",
                        "icon": "exclamation"
                    }
                ]
            }
            comp_counter += 1
        
        # Timeline/Event keywords
        if any(word in prompt_lower for word in ['timeline', 'event', 'history', 'impact']):
            components[f"comp-{comp_counter}"] = {
                "type": "EventImpactTimeline",
                "data": {
                    "dates": [
                        "Jan 1", "Jan 5", "Jan 10", "Jan 15", "Jan 20", "Jan 25", "Jan 30"
                    ],
                    "prices": [
                        13600, 13650, 13700, 13800, 13850, 13900, 14000
                    ],
                    "events": [
                        {
                            "name": "Fed Meeting",
                            "date": "Jan 15",
                            "price": 13800,
                            "priceChange": -100,
                            "priceChangePercent": -0.7,
                            "volumeSpike": "High",
                            "sentimentUp": False
                        }
                    ]
                }
            }
            comp_counter += 1
        
        # Holdings/Portfolio keywords
        if any(word in prompt_lower for word in ['holding', 'portfolio', 'position', 'asset']):
            components[f"comp-{comp_counter}"] = {
                "type": "HoldingsDashboard",
                "data": {
                    "holdings": [
                        {
                            "ticker": "AAPL",
                            "name": "Apple Inc.",
                            "quantity": 150,
                            "price": 172.25,
                            "plPercent": 1.45,
                            "weight": 15,
                            "var": "$5k",
                            "greeks": 0.5,
                            "liquidity": "High"
                        },
                        {
                            "ticker": "GOOGL",
                            "name": "Alphabet Inc.",
                            "quantity": 50,
                            "price": 140.76,
                            "plPercent": -0.21,
                            "weight": 12,
                            "var": "$4k",
                            "greeks": 0.4,
                            "liquidity": "High"
                        }
                    ]
                }
            }
            comp_counter += 1
        
        # Correlation keywords
        if any(word in prompt_lower for word in ['correlation', 'matrix', 'relationship']):
            components[f"comp-{comp_counter}"] = {
                "type": "CorrelationMatrix",
                "data": {
                    "categories": ["Equity", "Rates", "Credit", "Cmdty", "FX"],
                    "correlationData": [
                        {"row": "Equity", "col": "Equity", "value": 1.0},
                        {"row": "Equity", "col": "Rates", "value": 0.12},
                        {"row": "Equity", "col": "Credit", "value": 0.35},
                        {"row": "Rates", "col": "Rates", "value": 1.0},
                        # ... more correlation data
                    ]
                }
            }
            comp_counter += 1
        
        # News/Sentiment keywords
        if any(word in prompt_lower for word in ['news', 'sentiment', 'headline']):
            components[f"comp-{comp_counter}"] = {
                "type": "NewsSentimentStream",
                "data": {
                    "newsItems": [
                        {
                            "headline": "US CPI beats expectations, raising odds of earlier Fed hike",
                            "source": "Reuters",
                            "timestamp": "2025-11-27T13:45:00Z",
                            "currencyPair": "EUR/USD",
                            "sentimentScore": -0.6,
                            "matchPercentage": 82
                        }
                    ]
                }
            }
            comp_counter += 1
        
        # Stress test keywords
        if any(word in prompt_lower for word in ['stress', 'scenario', 'test', 'shock']):
            components[f"comp-{comp_counter}"] = {
                "type": "StressTestResults",
                "data": {
                    "capitalHitScenarios": [
                        {"name": "Base Case", "percentage": 0},
                        {"name": "Mild Recession", "percentage": -5},
                        {"name": "Severe Crash", "percentage": -12}
                    ],
                    "stressScenarios": [
                        {
                            "scenario": "FX Shock +20%",
                            "lossPercent": -2.4,
                            "capitalHit": -15000000
                        },
                        {
                            "scenario": "Interest Rate Hike",
                            "lossPercent": -3.1,
                            "capitalHit": -22000000
                        }
                    ]
                }
            }
            comp_counter += 1
        
        # Trade log keywords
        if any(word in prompt_lower for word in ['trade', 'transaction', 'log', 'history']):
            components[f"comp-{comp_counter}"] = {
                "type": "TradeLogPage",
                "data": {
                    "trades": [
                        {
                            "id": "1",
                            "time": "14:30:05",
                            "symbol": "TSLA",
                            "action": "BUY",
                            "qty": 500,
                            "price": 240.5,
                            "profitLoss": 450.0
                        },
                        {
                            "id": "2",
                            "time": "14:28:15",
                            "symbol": "US10Y",
                            "action": "SELL",
                            "qty": 100,
                            "price": 98.12,
                            "profitLoss": -120.0
                        }
                    ]
                }
            }
            comp_counter += 1
        
        # Liquidity keywords
        if any(word in prompt_lower for word in ['liquidity', 'buffer', 'cash flow']):
            components[f"comp-{comp_counter}"] = {
                "type": "LiquidityBufferGauge",
                "data": {
                    "currentPercent": 115,
                    "targetPercent": 100,
                    "maxPercent": 150
                }
            }
            comp_counter += 1
        
        # Default: If no matches, show a generic dashboard
        if not components:
            components = {
                "comp-1": {
                    "type": "AlertInsights",
                    "data": [
                        {
                            "id": "1",
                            "title": "Welcome to Canvas Playground",
                            "timestamp": "Now",
                            "severity": "info",
                            "icon": "info"
                        }
                    ]
                },
                "comp-2": {
                    "type": "TopMovers",
                    "data": {
                        "gainers": [
                            {
                                "ticker": "US10Y",
                                "name": "US 10 Year Treasury",
                                "changePercent": 0.45,
                                "price": 101.25
                            }
                        ],
                        "losers": [
                            {
                                "ticker": "US30Y",
                                "name": "US 30 Year Treasury",
                                "changePercent": -0.50,
                                "price": 99.80
                            }
                        ]
                    }
                }
            }
        
        # Generate response text
        component_types = [comp["type"] for comp in components.values()]
        response_text = f"I've created a dashboard with {len(components)} component(s): {', '.join(component_types)}."
        
        return {
            "components": components  # Dict format: { "comp-1": {...}, "comp-2": {...} }
        }