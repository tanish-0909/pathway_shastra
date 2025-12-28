"""
Pathway Trading Signal Pipeline - Main Entry Point

This module orchestrates the complete trading signal generation pipeline using Pathway.
It handles data ingestion, indicator computation, signal generation, and output writing.
"""

import pathway as pw
import csv
import time
import os
import logging
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import pymongo
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError


# --- Imports from your project structure ---
from accumulators import (
    MACDAccumulator, RSIAccumulator, ADLAccumulator,
    SMA20Accumulator, SMA50Accumulator, Std20Accumulator,
    BollingerBand20Accumulator, VWAPAccumulator, ATR14Accumulator,
    OBVAccumulator, CMOAccumulator, CRSIAccumulator,
    KlingerAccumulator, KeltnerMidAccumulator, DayChangeAccumulator
)
from signal_generator import (
    enhanced_signal_generator, build_keltner_tuple,
    get_action, get_stop_loss, get_take_profit, get_signal_strength,
    get_current_price, get_rsi, get_macd, get_macd_signal, get_macd_hist,
    get_limit_order, get_sma, get_vwap, get_bb, get_crsi,
    get_klinger, get_keltner, get_cmo, get_reason, is_not_hold
)


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from stocks_agent.services.zerodha_service import ZerodhaDataManager
except ImportError as e:
    logging.warning("zerodha_services module not found. Live Mode will fail if enabled.")


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RELATIVE_UNIVERSE_PATH = "data/UNIVERSE.json"
default_universe_path = PROJECT_ROOT / RELATIVE_UNIVERSE_PATH
default_hist_path = PROJECT_ROOT / "data" / "RELIANCE_5minute.csv"

PRICE_CSV_PATH = os.getenv("PRICE_CSV_PATH", str(default_hist_path))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "history")
UNIVERSE_PATH = os.getenv("UNIVERSE_PATH", str(default_universe_path))

# Database Config
ATLAS_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
UNIVERSE_DB_NAME = "universe"
UNIVERSE_COL_NAME = "universe_collection"

# Kafka Config
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9093')
KAFKA_SECURITY_PROTOCOL = os.getenv("KAFKA_SECURITY_PROTOCOL", None)
KAFKA_SASL_USERNAME = os.getenv("KAFKA_SASL_USERNAME", None)
KAFKA_SASL_PASSWORD = os.getenv("KAFKA_SASL_PASSWORD", None)

# Persistence Config
PERSISTENCE_STATE_DIR = Path(os.getenv("PATHWAY_STATE_DIR", str(PROJECT_ROOT / "pathway_state")))

# Toggle for Live vs Backtest mode
LIVE_MODE = os.getenv("LIVE_MODE", "true").lower() in ('true', '1', 't')


# Create output directory
try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
except Exception as e:
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger(__name__).error(f"Failed to create output directory: {e}")
    raise


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(OUTPUT_DIR, 'trading_pipeline.log'))
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Persistence state directory: {PERSISTENCE_STATE_DIR}")


# =============================================================================
# Persistence Management
# =============================================================================

def clear_persistence_state():
    """Clear persistence state directory."""
    if PERSISTENCE_STATE_DIR.exists():
        try:
            shutil.rmtree(PERSISTENCE_STATE_DIR)
            logger.info(f"Cleared persistence state: {PERSISTENCE_STATE_DIR}")
        except Exception as e:
            logger.error(f"Failed to clear state: {e}")
            raise


def create_persistence_config() -> pw.persistence.Config:
    """
    Create persistence configuration.
    
    Returns:
        Pathway persistence config
    """
    # Create state directory
    PERSISTENCE_STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create backend and config
    persistence_backend = pw.persistence.Backend.filesystem(str(PERSISTENCE_STATE_DIR))
    persistence_config = pw.persistence.Config(
        persistence_backend,
        snapshot_interval_ms=60000,  # Snapshot every 60 seconds
    )
    
    logger.info(f"Persistence configured: {PERSISTENCE_STATE_DIR}")
    logger.info(f"   Snapshot interval: 60 seconds")
    return persistence_config


# =============================================================================
# MongoDB Setup & Custom Handlers
# =============================================================================

def setup_mongodb_indexes(uri, db_name, universe_db_name="universe", universe_col_name="universe_collection"):
    """
    Creates indexes for all collections used in the pipeline, 
    including a unique index for the universe collection.
    """
    try:
        client = MongoClient(uri)
        
        # 1. Indexes for Indicator Database
        db_indicators = client[db_name]
        target_collections = ["indicators", "sensex_indicators"]
        
        for col_name in target_collections:
            col = db_indicators[col_name]
            col.create_index([("ticker", pymongo.ASCENDING)], background=True)
            logger.info(f"Index created: {db_name}.{col_name}")
            
        # 2. Index for Universe Database (Unique Upsert Target)
        db_universe = client[universe_db_name]
        col_universe = db_universe[universe_col_name]
        
        # Create a unique index on 'ticker'
        col_universe.create_index(
            [("ticker", pymongo.ASCENDING)], 
            unique=True, 
            background=True
        )
        logger.info(f"Unique index created: {universe_db_name}.{universe_col_name}")
            
        client.close()
    except Exception as e:
        logger.error(f"⚠️ Could not create indexes: {e}")


# Run setup immediately
setup_mongodb_indexes(ATLAS_URI, "indicator_signals", UNIVERSE_DB_NAME, UNIVERSE_COL_NAME)


class MongoDBUpsertHandler:
    """
    Custom handler for upserting data to MongoDB via pymongo.
    Handles unique key constraints properly to avoid E11000 errors.
    """
    def __init__(self, connection_string: str, database: str, collection: str, 
                 unique_key: str = "ticker", batch_size: int = 50):
        self.client = MongoClient(connection_string)
        self.db = self.client[database]
        self.collection = self.db[collection]
        self.unique_key = unique_key
        self.buffer = []
        self.max_buffer_size = batch_size
        logger.info(f"MongoDB Upsert Handler initialized: {database}.{collection}")
    
    def add_record(self, record: dict):
        """Add a record to the buffer and flush if needed."""
        self.buffer.append(record)
        if len(self.buffer) >= self.max_buffer_size:
            self.flush()
    
    def flush(self):
        """Flush buffered records using bulk upsert."""
        if not self.buffer:
            return
        
        try:
            operations = []
            for record in self.buffer:
                # Prepare Filter
                unique_val = record.get(self.unique_key)
                if not unique_val:
                    continue

                # Create Upsert Operation
                op = UpdateOne(
                    {self.unique_key: unique_val},
                    {
                        '$set': record,
                        '$currentDate': {'lastModified': True}
                    },
                    upsert=True
                )
                operations.append(op)
            
            if operations:
                result = self.collection.bulk_write(operations, ordered=False)
                logger.debug(f"Upserted: {result.upserted_count}, Modified: {result.modified_count}")
            
            self.buffer.clear()
            
        except BulkWriteError as bwe:
            logger.error(f"MongoDB Bulk Write Error: {bwe.details}")
            self.buffer.clear()
        except Exception as e:
            logger.error(f"MongoDB General Upsert Error: {e}")
            self.buffer.clear()

    def close(self):
        """Flush remaining data and close connection."""
        self.flush()
        self.client.close()
        logger.info("MongoDB handler closed")


# Global handler instance
universe_handler = None


def init_mongodb_handlers():
    """Initialize the global MongoDB upsert handler."""
    global universe_handler
    universe_handler = MongoDBUpsertHandler(
        connection_string=ATLAS_URI,
        database=UNIVERSE_DB_NAME,
        collection=UNIVERSE_COL_NAME,
        unique_key="ticker"
    )


def upsert_to_universe(row):
    """Callback for pw.io.subscribe to push data to the custom handler."""
    if universe_handler is None:
        return

    try:
        # Explicit type conversion to ensure safety
        record = {
            'ticker': str(row['ticker']),
            'date': str(row['date']),
            'close_price': float(row['close_price']),
            'open_price': float(row['open_price']),
            'volume': float(row['volume']),
            'high_price': float(row['high_price']),
            'low_price': float(row['low_price']),
            'abs_change': float(row['abs_change']),
            'pct_change': float(row['pct_change'])
        }
        universe_handler.add_record(record)
    except Exception as e:
        logger.error(f"Error processing row for upsert: {e}")


# =============================================================================
# Kafka Configuration
# =============================================================================

def get_rdkafka_settings() -> dict:
    """Get rdkafka settings for Pathway Kafka connector."""
    settings = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "pathway-pipeline",
    }
    
    if KAFKA_SECURITY_PROTOCOL == "SASL_SSL":
        settings.update({
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.username": KAFKA_SASL_USERNAME,
            "sasl.password": KAFKA_SASL_PASSWORD,
        })
    
    return settings


# =============================================================================
# Pathway Components
# =============================================================================

class ZerodhaSchema(pw.Schema):
    """Schema for Zerodha-like broker interface."""
    close: float
    open: float
    high: float
    low: float
    date: str
    raw_date: str
    volume: float
    ticker: str


class ZerodhaStreamSubject(pw.io.python.ConnectorSubject):
    """Custom connector for CSV or Live Zerodha data."""
    
    def __init__(self, csv_path: str, universe_path: str, is_live: bool, delay_seconds: float = 0.5):
        super().__init__()
        self.csv_path = csv_path
        self.universe_path = universe_path
        self.is_live = is_live
        self.delay_seconds = delay_seconds

    def _parse_datetime(self, dt_str: str) -> str:
        """Parse datetime string to ISO format."""
        if not dt_str:
            return datetime.now(timezone.utc).isoformat()
            
        dt_str = str(dt_str).strip()
        try:
            if 'T' in dt_str:
                return dt_str  # Already ISO
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S%z')
            return dt.isoformat()
        except Exception:
            try:
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                return dt.isoformat()
            except Exception as e:
                logger.error(f"Error parsing date '{dt_str}': {e}")
                return datetime.now(timezone.utc).isoformat()

    def _is_market_open(self) -> bool:
        """
        Checks if the current time is within trading hours (NSE/BSE).
        Market Hours: 09:15 to 15:30 IST.
        Returns False on Weekends.
        """
        now = datetime.now()
        
        # Check Weekend
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False

        # Check Time (09:00 to 15:45)
        current_time = now.time()
        start_time = datetime.strptime("09:00:00", "%H:%M:%S").time()
        end_time = datetime.strptime("15:45:00", "%H:%M:%S").time()

        return start_time <= current_time <= end_time

    def run(self):
        """Execute the data stream loop."""
        if not self.is_live:
            # BACKTEST / CSV MODE
            logger.info(f"Starting CSV Stream from {self.csv_path}")
            if not Path(self.csv_path).exists():
                logger.error(f"Input CSV file not found: {self.csv_path}")
                return

            with open(self.csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        data = {
                            'date': self._parse_datetime(row.get('date', '')),
                            'raw_date': row.get('date', ''),
                            'open': float(row.get('Open', row.get('open', 0.0))),
                            'high': float(row.get('High', row.get('high', 0.0))),
                            'low': float(row.get('Low', row.get('low', 0.0))),
                            'close': float(row.get('Close', row.get('close', 0.0))),
                            'volume': float(row.get('Volume', row.get('volume', 0.0))),
                            'ticker': "ADANIPORTS"
                        }
                        self.next(**data)
                        time.sleep(self.delay_seconds)
                    except Exception as e:
                        logger.warning(f"Skipping row error: {e}")
            logger.info("CSV Stream finished.")
            
        else:
            # LIVE MODE
            logger.info("Starting Live Zerodha Stream...")
            dm = ZerodhaDataManager(universe_path=self.universe_path)
            
            # Load universe once
            try:
                with open(self.universe_path, 'r') as f:
                    universe = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load universe: {e}")
                return
            
            logger.info("Live Stream Active. Waiting for Market Hours...")

            while True:
                # Check Market Status
                if self._is_market_open():
                    # Market is OPEN: Poll API
                    for ticker in universe.keys():
                        try:
                            live_data = dm.get_recent_data(ticker, duration_minutes=5)
                            
                            if live_data and len(live_data) > 0:
                                latest_candle = live_data[-1]
                                data = {
                                    'date': self._parse_datetime(latest_candle.get('date')),
                                    'raw_date': str(latest_candle.get('date')),
                                    'open': float(latest_candle.get('open', 0.0)),
                                    'high': float(latest_candle.get('high', 0.0)),
                                    'close': float(latest_candle.get('close', 0.0)),
                                    'low': float(latest_candle.get('low', 0.0)),
                                    'volume': float(latest_candle.get('volume', 0.0)),
                                    'ticker': ticker
                                }
                                self.next(**data)
                        except Exception as inner_e:
                            logger.error(f"Error fetching data for {ticker}: {inner_e}")
                        
                        time.sleep(self.delay_seconds)  # Rate limit per ticker
                
                else:
                    # Market is CLOSED: Sleep
                    if datetime.now().minute == 0:
                        logger.info("Market closed. Pipeline sleeping...")
                    time.sleep(60)


def build_pipeline():
    """Build the complete trading signal pipeline."""
    logger.info("Building trading signal pipeline...")
    
    # Initialize Custom Upsert Handler
    init_mongodb_handlers()

    # 1. Define Reducers
    reduce_obv = pw.reducers.udf_reducer(OBVAccumulator)
    reduce_atr14 = pw.reducers.udf_reducer(ATR14Accumulator)
    reduce_vwap = pw.reducers.udf_reducer(VWAPAccumulator)
    reduce_bollinger20 = pw.reducers.udf_reducer(BollingerBand20Accumulator)
    reduce_std20 = pw.reducers.udf_reducer(Std20Accumulator)
    reduce_sma50 = pw.reducers.udf_reducer(SMA50Accumulator)
    reduce_sma20 = pw.reducers.udf_reducer(SMA20Accumulator)
    reduce_adl = pw.reducers.udf_reducer(ADLAccumulator)
    reduce_rsi = pw.reducers.udf_reducer(RSIAccumulator)
    reduce_macd = pw.reducers.udf_reducer(MACDAccumulator)
    reduce_cmo = pw.reducers.udf_reducer(CMOAccumulator)
    reduce_crsi = pw.reducers.udf_reducer(CRSIAccumulator)
    reduce_klinger = pw.reducers.udf_reducer(KlingerAccumulator)
    reduce_keltner_mid = pw.reducers.udf_reducer(KeltnerMidAccumulator)
    reduce_day_change = pw.reducers.udf_reducer(DayChangeAccumulator)

    # 2. Input Stream
    price_stream = pw.io.python.read(
        ZerodhaStreamSubject(
            csv_path=PRICE_CSV_PATH, 
            universe_path=UNIVERSE_PATH,
            is_live=LIVE_MODE,
            delay_seconds=3.0 if not LIVE_MODE else 3.0
        ),
        schema=ZerodhaSchema,
    )

    price_stream = price_stream.select(
        *pw.this,
        tstamp = pw.this.date.dt.strptime("%Y-%m-%dT%H:%M:%S%z")
    )
    
    def is_valid_date(ts) -> bool:
        try:
            if ts is None:
                return False
            return 2000 <= ts.year <= 2100
        except Exception:
            return False

    # 3. Apply Filters
    price_stream = price_stream.filter(pw.apply(is_valid_date, pw.this.tstamp))

    # 4. Windowing & Reduction
    combined_tmp = price_stream.windowby(
        pw.this.tstamp,
        window=pw.temporal.sliding(duration=timedelta(minutes=5*180), hop=timedelta(minutes=5)),
        instance=price_stream.ticker,
        behavior=pw.temporal.exactly_once_behavior()
    ).reduce(
        ticker=pw.this._pw_instance,
        window_end=pw.this._pw_window_end,
        date=pw.reducers.max(pw.this.date),
        
        # Tuple reductions (Date, Value)
        close=pw.reducers.max((pw.this.date, pw.this.close)),
        open=pw.reducers.max((pw.this.date, pw.this.open)),
        volume=pw.reducers.max((pw.this.date, pw.this.volume)),
        low=pw.reducers.max((pw.this.date, pw.this.low)),
        high=pw.reducers.max((pw.this.date, pw.this.high)),
        
        # Simple reductions
        max_high=pw.reducers.max(pw.this.high),
        min_low=pw.reducers.min(pw.this.low),
        
        # UDF Reducers
        macd_tuple=reduce_macd(pw.this.close),
        rsi_val=reduce_rsi(pw.this.close, pw.this.date),
        adl=reduce_adl(pw.this.date, pw.this.high, pw.this.low, pw.this.close, pw.this.volume),
        sma_20=reduce_sma20(pw.this.close),
        sma_50=reduce_sma50(pw.this.close),
        std_20=reduce_std20(pw.this.close),
        bb_tuple=reduce_bollinger20(pw.this.close),
        vwap=reduce_vwap(pw.this.date, pw.this.high, pw.this.low, pw.this.close, pw.this.volume),
        atr_14=reduce_atr14(pw.this.date, pw.this.high, pw.this.low, pw.this.close),
        cmo=reduce_cmo(pw.this.close, pw.this.date),
        crsi=reduce_crsi(pw.this.close, pw.this.date),
        klinger_tuple=reduce_klinger(pw.this.date, pw.this.high, pw.this.low, pw.this.close, pw.this.volume),
        keltner_mid=reduce_keltner_mid(pw.this.close, pw.this.date),
        day_change=reduce_day_change((pw.this.date, pw.this.close)),
    )

    # 5. Post-processing for Keltner Bands
    combined = combined_tmp.select(
        **combined_tmp,
        keltner=build_keltner_tuple(pw.this.keltner_mid, pw.this.atr_14),
    )

    logger.info("Indicators computed. Generating signals...")

    # 6. Signal Generation
    signals = combined.select(
        ticker=pw.this.ticker,
        date=pw.this.date,
        close_price=pw.this.close[1], 
        open_price=pw.this.open[1],
        volume_val=pw.this.volume[1],
        high_price=pw.this.high[1],
        low_price=pw.this.low[1],
        signal=enhanced_signal_generator(
            close=pw.this.close,
            macd_tuple=pw.this.macd_tuple,
            rsi=pw.this.rsi_val,
            atr=pw.this.atr_14,
            min_low=pw.this.min_low,
            max_high=pw.this.max_high,
            sma_20=pw.this.sma_20,
            sma_50=pw.this.sma_50,
            volume=pw.this.volume,
            vwap=pw.this.vwap,
            bb_tuple=pw.this.bb_tuple,
            crsi=pw.this.crsi,
            klinger_tuple=pw.this.klinger_tuple,
            keltner=pw.this.keltner,
            cmo=pw.this.cmo,
            buy_threshold = 5.0,
            sell_threshold = 5.0
        ),
        abs_change = pw.this.day_change[0],
        pct_change = pw.this.day_change[1]
    )

    # 7. Flattening
    signals_flat = signals.select(
        ticker=pw.this.ticker,
        date=pw.apply(str, pw.this.date),
        close_price=pw.this.close_price,
        open_price=pw.this.open_price,
        volume=pw.this.volume_val,
        high_price=pw.this.high_price,
        low_price=pw.this.low_price,
        abs_change=pw.this.abs_change,
        pct_change=pw.this.pct_change,
        action=get_action(pw.this.signal),
        stop_loss=get_stop_loss(pw.this.signal),
        take_profit=get_take_profit(pw.this.signal),
        signal_strength=get_signal_strength(pw.this.signal),
        limit_order=get_limit_order(pw.this.signal),
        current_price=get_current_price(pw.this.signal),
        rsi=get_rsi(pw.this.signal),
        macd=get_macd(pw.this.signal),
        macd_signal=get_macd_signal(pw.this.signal),
        macd_hist=get_macd_hist(pw.this.signal),
        vwap=get_vwap(pw.this.signal),
        bol_bands=get_bb(pw.this.signal),
        sma=get_sma(pw.this.signal),
        crsi=get_crsi(pw.this.signal),
        klinger=get_klinger(pw.this.signal),
        keltner=get_keltner(pw.this.signal),
        cmo=get_cmo(pw.this.signal),
        reason=get_reason(pw.this.signal),
    )

    # 8. Outputs
    logger.info(f"Writing outputs...")
    
    # Valid Data Filter
    signal_filtered = signals_flat.filter(
        (pw.this.date != "NaT") & 
        (pw.this.date != "") &
        (pw.this.date != None)
    )
    
    # 8a. Historical Indicators (Standard MongoDB Insert)
    no_sensex_filtered = signal_filtered.filter(pw.this.ticker != "SENSEX")
    
    pw.io.mongodb.write(
        no_sensex_filtered, 
        connection_string=ATLAS_URI, 
        database="indicator_signals", 
        collection="indicators"
    )
    pw.io.csv.write(
        no_sensex_filtered,
        os.path.join(OUTPUT_DIR, "trading_signals_history.csv"),
    )
    signal_filtered = signal_filtered.filter(is_not_hold(pw.this.action))

    # 8c. Universe Collection (Custom Upsert via subscribe)
    universe_table = no_sensex_filtered.select(
        ticker=pw.this.ticker,
        date=pw.apply(str, pw.this.date),
        close_price=pw.this.close_price,
        open_price=pw.this.open_price,
        volume=pw.this.volume,
        high_price=pw.this.high_price,
        low_price=pw.this.low_price,
        abs_change=pw.this.abs_change,
        pct_change=pw.this.pct_change
    )
    
    # Hook into Pathway stream for custom upserts
    pw.io.subscribe(
        universe_table,
        on_change=lambda key, row, time, is_addition: upsert_to_universe(row) if is_addition else None
    )
    

    rdkafka_settings = get_rdkafka_settings()
    pw.io.kafka.write(no_sensex_filtered, rdkafka_settings, topic_name="trade_signals_dev", format="json")
    
    logger.info("Pipeline construction complete.")


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    try:
        logger.info("="*80)
        logger.info(f"Starting Pathway Trading Signal Pipeline")
        logger.info(f"Mode: {'LIVE' if LIVE_MODE else 'BACKTEST'}")
        logger.info(f"Universe: {UNIVERSE_PATH}")
        logger.info(f"Output: {OUTPUT_DIR}")
        logger.info("="*80)
        
        # Check if state reset is requested
        if os.getenv("RESET_STATE", "false").lower() in ('true', '1', 't'):
            logger.info("State reset requested...")
            clear_persistence_state()
        
        # Create persistence config
        persistence_config = create_persistence_config()
        
        # Build and run pipeline with error recovery
        try:
            build_pipeline()
            pw.run(persistence_config=persistence_config)
            
        except pw.engine.EngineError as e:
            # Auto-recover from state corruption
            if "byte index" in str(e) and "out of bounds" in str(e):
                logger.error("Persistence state corrupted!")
                logger.info("Clearing state and retrying...")
                clear_persistence_state()
                
                # Recreate config and retry
                persistence_config = create_persistence_config()
                build_pipeline()
                pw.run(persistence_config=persistence_config)
            else:
                raise
                
    except KeyboardInterrupt:
        logger.info("\nPipeline stopped by user")
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise
        
    finally:
        # Cleanup MongoDB handlers
        logger.info("Cleaning up...")
        if universe_handler:
            universe_handler.close()
        
        logger.info("="*80)
        logger.info("Pipeline shutdown complete")
        logger.info("="*80)
