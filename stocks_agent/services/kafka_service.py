"""
Kafka Service for StocksAgent.

Handles producing and consuming messages from Kafka topics.
"""

import os
import sys
import ssl
import json
import logging
from typing import Dict, Any, Optional, Callable, List

# Add parent directory to path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config

logger = logging.getLogger(__name__)

# Kafka settings from environment
# Default port 9093 for external access (9092 is internal Docker network)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9093")
KAFKA_TOPIC_TRADE_SIGNALS = os.getenv("KAFKA_TOPIC_TRADE_SIGNALS", "trade_signals")
KAFKA_TOPIC_SUMMARIZED_NEWS = os.getenv("KAFKA_TOPIC_SUMMARIZED_NEWS", "summarized_news")
KAFKA_TOPIC_STOCK_ANALYSIS = os.getenv("KAFKA_TOPIC_STOCK_ANALYSIS", "stock_analysis")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "stocksagent-consumers")

KAFKA_SECURITY_PROTOCOL = os.getenv("KAFKA_SECURITY_PROTOCOL", None)  # "SASL_SSL" for Confluent Cloud
KAFKA_SASL_MECHANISM = os.getenv("KAFKA_SASL_MECHANISM", None)  # "PLAIN" for Confluent Cloud
KAFKA_SASL_USERNAME = os.getenv("KAFKA_SASL_USERNAME", None)  # API Key
KAFKA_SASL_PASSWORD = os.getenv("KAFKA_SASL_PASSWORD", None)  # API Secret


def get_kafka_config() -> Dict[str, Any]:
    """
    Build Kafka configuration dict with optional Confluent Cloud auth.
    """
    config = {
        "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
    }
    
    # Add Confluent Cloud authentication if configured
    if KAFKA_SECURITY_PROTOCOL == "SASL_SSL":
        ssl_context = ssl.create_default_context()
        config.update({
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": KAFKA_SASL_MECHANISM or "PLAIN",
            "sasl_plain_username": KAFKA_SASL_USERNAME,
            "sasl_plain_password": KAFKA_SASL_PASSWORD,
            "ssl_context": ssl_context,
        })
        logger.info("Kafka configured for Confluent Cloud (SASL_SSL)")
    else:
        logger.info("Kafka configured for local/plaintext connection")
    
    return config

class KafkaProducerService:
    """
    Async Kafka producer for publishing agent outputs.
    """
    
    def __init__(self, bootstrap_servers: str = None):
        self.bootstrap_servers = bootstrap_servers or KAFKA_BOOTSTRAP_SERVERS
        self._producer = None
    
    async def connect(self):
        """Initialize the Kafka producer."""
        try:
            from aiokafka import AIOKafkaProducer
            
            kafka_config = get_kafka_config()
            if bootstrap_servers := kafka_config.pop("bootstrap_servers", None):
                pass  # Already set in self.bootstrap_servers if not overridden
            
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                **{k: v for k, v in kafka_config.items() if v is not None}
            )
            await self._producer.start()
            logger.info(f"Kafka producer connected to {self.bootstrap_servers}")
        except ImportError:
            logger.error("aiokafka not installed. Install with: pip install aiokafka")
            raise
        except Exception as e:
            logger.error(f"Failed to connect Kafka producer: {e}")
            raise
    
    async def send(self, topic: str, message: Dict[str, Any], key: str = None):
        """
        Send a message to a Kafka topic.
        
        Args:
            topic: Kafka topic name
            message: Message payload (dict)
            key: Optional message key for partitioning
        """
        if not self._producer:
            await self.connect()
        
        try:
            key_bytes = key.encode('utf-8') if key else None
            await self._producer.send_and_wait(topic, value=message, key=key_bytes)
            logger.info(f"Sent message to {topic}: ticker={message.get('ticker', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to send to Kafka: {e}")
            raise
    
    async def close(self):
        """Close the producer connection."""
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer closed")


class KafkaConsumerService:
    """
    Async Kafka consumer for receiving messages.
    """
    
    def __init__(
        self, 
        topics: List[str],
        group_id: str = None,
        bootstrap_servers: str = None
    ):
        self.topics = topics
        self.group_id = group_id or KAFKA_GROUP_ID
        self.bootstrap_servers = bootstrap_servers or KAFKA_BOOTSTRAP_SERVERS
        self._consumer = None
        self._running = False
    
    async def connect(self):
        """Initialize the Kafka consumer."""
        try:
            from aiokafka import AIOKafkaConsumer
            
            kafka_config = get_kafka_config()
            kafka_config.pop("bootstrap_servers", None)  # We set this explicitly
            
            self._consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                **{k: v for k, v in kafka_config.items() if v is not None}
            )
            await self._consumer.start()
            # Seek to end of all partitions
            await self._consumer.seek_to_end()
            logger.info("Seeked to end of all partitions (latest)")
            logger.info(f"Kafka consumer connected to topics: {self.topics}")
        except ImportError:
            logger.error("aiokafka not installed. Install with: pip install aiokafka")
            raise
        except Exception as e:
            logger.error(f"Failed to connect Kafka consumer: {e}")
            raise
    
    async def consume(self, handler: Callable[[Dict], Any]):
        """
        Start consuming messages and pass to handler.
        
        Args:
            handler: Async function to process each message
        """
        if not self._consumer:
            await self.connect()
        
        self._running = True
        logger.info("Starting message consumption loop...")
        
        try:
            async for msg in self._consumer:
                if not self._running:
                    break
                try:
                    logger.debug(f"Received message from {msg.topic}: {msg.value.get('ticker', 'unknown')}")
                    await handler(msg.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise
    
    async def consume_with_topic(self, handler: Callable[[str, Dict], Any]):
        """
        Start consuming messages and pass topic + message to handler.
        
        Args:
            handler: Async function that takes (topic, message) as arguments
        """
        if not self._consumer:
            await self.connect()
        
        self._running = True
        logger.info("Starting message consumption loop (with topic routing)...")
        
        try:
            async for msg in self._consumer:
                if not self._running:
                    break
                try:
                    logger.debug(f"Received message from {msg.topic}")
                    await handler(msg.topic, msg.value)
                except Exception as e:
                    logger.error(f"Error processing message from {msg.topic}: {e}")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise
    
    def stop(self):
        """Signal the consumer to stop."""
        self._running = False
    
    async def close(self):
        """Close the consumer connection."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka consumer closed")

