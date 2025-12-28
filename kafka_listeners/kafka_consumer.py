"""
Unified Kafka Consumer for StocksAgent.

Consumes from two topics:
1. trade_signals - from indicators pipeline (technical analysis triggers)
2. summarized_news - from news pipeline (high-impact news triggers)

Runs LangGraph analysis and publishes results to stock_analysis topic.

Features:
- Concurrent message processing (non-blocking)
- Backpressure via semaphore (respects API rate limits)
- Per-ticker locking (prevents race conditions)
- Graceful shutdown (waits for active tasks)
"""

import os
import sys
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from asyncio import Semaphore, Lock
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import config first to ensure .env is loaded
import config  

from stocks_agent.graph import get_compiled_graph
from stocks_agent.services.kafka_service import (
    KafkaProducerService, 
    KafkaConsumerService,
    KAFKA_TOPIC_TRADE_SIGNALS,
    KAFKA_TOPIC_SUMMARIZED_NEWS,
    KAFKA_TOPIC_STOCK_ANALYSIS
)

# High-impact liquidity values that trigger processing
HIGH_IMPACT_LIQUIDITY = ["HIGH_NEGATIVE", "HIGH_POSITIVE"]

# ============================================================
# CONCURRENCY CONFIGURATION
# ============================================================
# Thread pool for running synchronous graph.invoke() without blocking async loop
THREAD_POOL_SIZE = 5
EXECUTOR = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)

# Maximum concurrent graph executions (respects OpenAI rate limits)
# OpenAI GPT-4o: ~500 RPM, each graph invocation makes 3-5 API calls
# Safe limit: 3 concurrent = ~15 API calls at once
MAX_CONCURRENT = 3
# ============================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StocksAgentKafkaConsumer:
    """
    Production-ready Kafka consumer with concurrent message processing.
    
    Features:
    - Concurrent processing: Multiple messages processed in parallel
    - Thread pool: graph.invoke() runs in threads to avoid blocking async loop
    - Backpressure: Semaphore limits concurrent executions (API rate limit safety)
    - Per-ticker locks: Prevents race conditions when same ticker has multiple messages
    - Graceful shutdown: Waits for all active tasks to complete
    
    Flow for trade_signals:
    1. Consume trade signal from 'trade_signals' topic
    2. If action is BUY or SELL, run through LangGraph (concurrent)
    3. Publish to 'stock_analysis' topic
    
    Flow for summarized_news:
    1. Consume news from 'summarized_news' topic
    2. Filter: only process if liquidity_impact is HIGH_NEGATIVE or HIGH_POSITIVE
    3. Extract relevant fields and run through LangGraph (concurrent)
    4. Publish to 'stock_analysis' topic
    """
    
    def __init__(self):
        self.graph = None
        self.producer = KafkaProducerService()
        self.consumer = KafkaConsumerService(
            topics=[KAFKA_TOPIC_TRADE_SIGNALS, KAFKA_TOPIC_SUMMARIZED_NEWS],
            group_id="stocksagent-consumers"
        )
        self._running = False
        
        # Concurrency controls
        self._semaphore = Semaphore(MAX_CONCURRENT)  # Global concurrency limit
        self._ticker_locks: Dict[str, Lock] = defaultdict(Lock)  # Per-ticker locks
        self._active_tasks: set = set()  # Track running tasks for graceful shutdown
    
    def _init_graph(self):
        """Lazy-load the graph to avoid import issues."""
        if self.graph is None:
            logger.info("Initializing LangGraph...")
            self.graph = get_compiled_graph()
            logger.info("LangGraph initialized successfully")
    
    async def _run_graph_in_thread(self, initial_state: dict) -> dict:
        """
        Run synchronous graph.invoke() in a thread pool to avoid blocking the async event loop.
        
        This is critical because:
        - graph.invoke() is synchronous and can take 20-60 seconds
        - Without this, the async event loop would be blocked
        - Other Kafka messages couldn't be consumed during that time
        
        Args:
            initial_state: Initial state dict for the LangGraph
            
        Returns:
            Result dict from graph.invoke()
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(EXECUTOR, self.graph.invoke, initial_state)
    
    def _extract_news_fields(self, news_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant fields from summarized_news message.
        
        Returns dict with: title, url, sentiment, financial_metrics, impact_assessment,
        liquidity_impact, summary, key_points, article_id, publisher details
        """
        return {
            "article_id": news_message.get("article_id") or news_message.get("_id"),
            "title": news_message.get("title"),
            "url": news_message.get("url"),
            "ticker": news_message.get("company"),  # company field is the ticker
            "sentiment": {
                "label": news_message.get("sentiment_label"),
                "score": news_message.get("sentiment_score"),
                "confidence": news_message.get("sentiment_confidence")
            },
            "financial_metrics": news_message.get("financial_metrics"),
            "impact_assessment": news_message.get("impact_assessment"),
            "liquidity_impact": news_message.get("liquidity_impact"),
            "summary": news_message.get("summary"),
            "key_points": news_message.get("key_points"),
            "publisher": {
                "name": news_message.get("publisher_name"),
                "icon": news_message.get("publisher_icon"),
                "author": news_message.get("author")
            },
            "published_at": news_message.get("published_at"),
            "decisions": news_message.get("decisions")
        }
    
    def _should_process_news(self, news_message: Dict[str, Any]) -> bool:
        """Check if news message should be processed based on liquidity_impact."""
        liquidity_impact = news_message.get("liquidity_impact", "")
        return liquidity_impact in HIGH_IMPACT_LIQUIDITY
    
    async def process_trade_signal(self, signal: Dict[str, Any], task_id: str):
        """
        Process a trade signal from the indicators pipeline.
        
        Runs news, twitter, montecarlo agents to check for conflicts.
        Only publishes if there's no conflict with sentiment.
        
        Concurrency features:
        - Semaphore: Limits total concurrent executions
        - Per-ticker lock: Prevents same ticker processing simultaneously
        - Thread pool: graph.invoke() runs without blocking
        
        Args:
            signal: Trade signal message from Kafka
            task_id: Unique task ID for logging/debugging
        """
        ticker = signal.get("ticker", "UNKNOWN")
        action = signal.get("action", "HOLD")
        
        logger.info(f"[{task_id}] Received trade signal: {ticker} - {action}")
        
        # Only process BUY or SELL signals (skip HOLD)
        if action == "HOLD":
            logger.info(f"[{task_id}] Skipping HOLD signal for {ticker}")
            return
        
        # Initialize graph if needed
        self._init_graph()
        
        # Acquire semaphore (global concurrency limit) and per-ticker lock
        async with self._semaphore:
            async with self._ticker_locks[ticker]:
                try:
                    # Build initial state for LangGraph
                    initial_state = {
                        "query": f"Analyze {ticker} based on technical {action} signal",
                        "message_type": "technical_kafka",
                        "trigger_signal": signal,
                        "ticker": [ticker],
                        "parsed_intent": {},
                        "agent_contributions": [],
                        "errors": []
                    }
                    
                    logger.info(f"[{task_id}] Running LangGraph analysis for {ticker}...")
                    
                    # Run in thread pool to avoid blocking async event loop
                    result = await self._run_graph_in_thread(initial_state)
                    
                    # Check for conflict with news/twitter sentiment
                    should_publish = result.get("should_publish", True)
                    
                    if should_publish:
                        # Build output message (raw state)
                        output_message = {
                            "message_type": "technical_kafka",
                            "ticker": ticker,
                            "task_id": task_id,
                            "trigger_signal": signal,
                            "news_output": result.get("news_output"),
                            "twitter_output": result.get("twitter_output"),
                            "montecarlo_output": result.get("montecarlo_output"),
                            "agent_contributions": result.get("agent_contributions", []),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Publish to stock_analysis topic
                        await self.producer.send(
                            KAFKA_TOPIC_STOCK_ANALYSIS,
                            output_message,
                            key=ticker
                        )
                        
                        logger.info(f"[{task_id}] Published analysis for {ticker} to {KAFKA_TOPIC_STOCK_ANALYSIS}")
                        
                        # Log the output
                        print("\n" + "=" * 60)
                        print(f"[{task_id}] Technical Kafka Analysis: {ticker}")
                        print(f"News Output: {result.get('news_output')}")
                        print(f"Twitter Output: {result.get('twitter_output')}")
                        print(f"Monte Carlo Output: {result.get('montecarlo_output')}")
                        print("=" * 60 + "\n")
                    else:
                        conflict_reason = result.get("conflict_reason", "Unknown conflict")
                        logger.warning(f"[{task_id}] NOT publishing {ticker}: {conflict_reason}")
                        print(f"\n[{task_id}] Conflict detected for {ticker}: {conflict_reason}\n")
                        
                except Exception as e:
                    logger.error(f"[{task_id}] Error processing signal for {ticker}: {e}", exc_info=True)
    
    async def process_news(self, news_message: Dict[str, Any], task_id: str):
        """
        Process a news message from the summarized_news topic.
        
        Runs technical and montecarlo agents for analysis.
        Always publishes (no conflict check for news-triggered analysis).
        
        Args:
            news_message: News message from Kafka
            task_id: Unique task ID for logging/debugging
        """
        # Check if we should process this news
        if not self._should_process_news(news_message):
            liquidity = news_message.get("liquidity_impact", "UNKNOWN")
            logger.info(f"[{task_id}] Skipping news with liquidity_impact: {liquidity}")
            return
        
        # Extract relevant fields
        news_input = self._extract_news_fields(news_message)
        ticker = news_input.get("ticker", "UNKNOWN")
        
        logger.info(f"[{task_id}] Received high-impact news for {ticker}: {news_input.get('title', '')[:50]}...")
        
        # Initialize graph if needed
        self._init_graph()
        
        # Acquire semaphore (global concurrency limit) and per-ticker lock
        async with self._semaphore:
            async with self._ticker_locks[ticker]:
                try:
                    # Build initial state for LangGraph
                    initial_state = {
                        "query": f"Analyze {ticker} based on high-impact news",
                        "message_type": "news_kafka",
                        "news_kafka_input": news_input,
                        "ticker": [ticker],
                        "parsed_intent": {},
                        "agent_contributions": [],
                        "errors": []
                    }
                    
                    logger.info(f"[{task_id}] Running LangGraph analysis for {ticker} (news-triggered)...")
                    
                    # Run in thread pool to avoid blocking async event loop
                    result = await self._run_graph_in_thread(initial_state)
                    
                    # Build output message (raw state)
                    output_message = {
                        "message_type": "news_kafka",
                        "ticker": ticker,
                        "task_id": task_id,
                        "news_kafka_input": news_input,
                        "technical_output": result.get("technical_output"),
                        "montecarlo_output": result.get("montecarlo_output"),
                        "agent_contributions": result.get("agent_contributions", []),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Publish to stock_analysis topic
                    await self.producer.send(
                        KAFKA_TOPIC_STOCK_ANALYSIS,
                        output_message,
                        key=ticker
                    )
                    
                    logger.info(f"[{task_id}] Published news-triggered analysis for {ticker} to {KAFKA_TOPIC_STOCK_ANALYSIS}")
                    
                    # Log the output
                    print("\n" + "=" * 60)
                    print(f"[{task_id}] News Kafka Analysis: {ticker}")
                    print(f"News: {news_input.get('title')}")
                    print(f"Liquidity Impact: {news_input.get('liquidity_impact')}")
                    print(f"Technical Output: {result.get('technical_output')}")
                    print(f"Monte Carlo Output: {result.get('montecarlo_output')}")
                    print("=" * 60 + "\n")
                        
                except Exception as e:
                    logger.error(f"[{task_id}] Error processing news for {ticker}: {e}", exc_info=True)
    
    def _handle_task_exception(self, task: asyncio.Task):
        """
        Callback to handle exceptions from completed tasks.
        This ensures errors in background tasks are logged and visible.
        """
        try:
            # This will raise if task had an exception
            task.result()
        except asyncio.CancelledError:
            pass  # Task was cancelled, not an error
        except Exception as e:
            logger.error(f"Background task failed with exception: {e}", exc_info=True)
    
    async def process_message(self, topic: str, message: Dict[str, Any]):
        """
        Route message to appropriate handler based on topic.
        
        CONCURRENT PROCESSING:
        - Uses asyncio.create_task() for fire-and-forget execution
        - Multiple messages can be processed simultaneously
        - Does NOT wait for processing to complete before receiving next message
        
        Args:
            topic: Kafka topic the message came from
            message: Message payload
        """
        # Generate unique task ID for logging/debugging
        task_id = str(uuid.uuid4())[:8]
        
        if topic == KAFKA_TOPIC_TRADE_SIGNALS:
            # Fire-and-forget: create task and don't await
            task = asyncio.create_task(
                self.process_trade_signal(message, task_id),
                name=f"trade_signal_{task_id}"
            )
        elif topic == KAFKA_TOPIC_SUMMARIZED_NEWS:
            task = asyncio.create_task(
                self.process_news(message, task_id),
                name=f"news_{task_id}"
            )
        else:
            logger.warning(f"[{task_id}] Unknown topic: {topic}")
            return
        
        # Track task for graceful shutdown
        self._active_tasks.add(task)
        
        # Remove from set when done, and handle any exceptions
        task.add_done_callback(self._active_tasks.discard)
        task.add_done_callback(self._handle_task_exception)
        
        logger.debug(f"[{task_id}] Created task for {topic}, active tasks: {len(self._active_tasks)}")
    
    async def run(self):
        """Start the Kafka consumer loop with concurrent processing."""
        logger.info("=" * 60)
        logger.info("Starting StocksAgent Kafka Consumer (CONCURRENT MODE)")
        logger.info(f"  Thread pool size: {THREAD_POOL_SIZE}")
        logger.info(f"  Max concurrent tasks: {MAX_CONCURRENT}")
        logger.info(f"  Consuming from: {KAFKA_TOPIC_TRADE_SIGNALS}, {KAFKA_TOPIC_SUMMARIZED_NEWS}")
        logger.info(f"  Publishing to: {KAFKA_TOPIC_STOCK_ANALYSIS}")
        logger.info(f"  News filter: liquidity_impact in {HIGH_IMPACT_LIQUIDITY}")
        logger.info("=" * 60)
        
        self._running = True
        
        try:
            # Connect producer
            await self.producer.connect()
            
            # Start consuming with topic-aware handler
            # This will call process_message() for each message, which creates concurrent tasks
            await self.consumer.consume_with_topic(self.process_message)
            
        except KeyboardInterrupt:
            logger.info("Received interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """
        Clean shutdown - waits for all active tasks to complete.
        
        This ensures:
        - No in-flight messages are lost
        - All graph executions complete
        - Producer flushes all pending messages
        """
        logger.info("Shutting down...")
        self._running = False
        
        # Wait for all active tasks to complete (with timeout)
        if self._active_tasks:
            logger.info(f"Waiting for {len(self._active_tasks)} active tasks to complete...")
            try:
                # Wait up to 60 seconds for tasks to complete
                await asyncio.wait_for(
                    asyncio.gather(*self._active_tasks, return_exceptions=True),
                    timeout=60.0
                )
                logger.info("All active tasks completed")
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for tasks, some may be cancelled")
                # Cancel remaining tasks
                for task in self._active_tasks:
                    task.cancel()
        
        # Close Kafka connections
        self.consumer.stop()
        await self.consumer.close()
        await self.producer.close()
        
        # Shutdown thread pool
        EXECUTOR.shutdown(wait=True)
        
        logger.info("Shutdown complete")


async def main():
    """Main entry point."""
    consumer = StocksAgentKafkaConsumer()
    await consumer.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
