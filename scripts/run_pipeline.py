import logging
import sys
import time

# Import ETL modules
from scripts import etl_bronze
from scripts import etl_silver
from scripts import etl_gold

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pipeline_orchestrator")

def main():
    start_time = time.time()
    logger.info("🚀 Starting IAR Data Pipeline (Medallion Architecture)...")
    
    try:
        # 1. Bronze Layer
        logger.info("\n--- STEP 1: BRONZE LAYER (Ingestion) ---")
        etl_bronze.run_bronze()
        
        # 2. Silver Layer
        logger.info("\n--- STEP 2: SILVER LAYER (Cleaning & Enrichment) ---")
        etl_silver.run_silver()
        
        # 3. Gold Layer
        logger.info("\n--- STEP 3: GOLD LAYER (Aggregation & Serving) ---")
        etl_gold.run_gold()
        
        elapsed = time.time() - start_time
        logger.info(f"\n✅ Pipeline Completed Successfully in {elapsed:.2f} seconds.")
        
    except Exception as e:
        logger.error(f"\n❌ Pipeline Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
