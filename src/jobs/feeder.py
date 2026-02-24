"""
RAW Layer Data Ingestion (Feeder)
Ingests DVF, BPE, and commune reference data into the data lake
"""
import argparse
import logging
import logging.config
import yaml
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pyspark.sql import SparkSession
from src.common.spark_session import create_spark_session, load_config
from src.common.paths import get_partition_path, create_partition_directories


def setup_logging(log_config_path: str, run_date: str):
    """Setup logging configuration"""
    with open(log_config_path, 'r') as f:
        log_config = yaml.safe_load(f)
    
    # Update log file path with date
    date_str = run_date.replace('-', '')
    log_file = f"logs/feeder_{date_str}.txt"
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Update file handler
    if 'handlers' in log_config and 'file_feeder' in log_config['handlers']:
        log_config['handlers']['file_feeder']['filename'] = log_file
    
    logging.config.dictConfig(log_config)
    return logging.getLogger('feeder')


def ingest_dvf(spark: SparkSession, config: dict, run_date: str, logger: logging.Logger):
    """
    Ingest DVF data into RAW layer
    
    Args:
        spark: SparkSession
        config: Application configuration
        run_date: Run date string (YYYY-MM-DD)
        logger: Logger instance
    """
    logger.info("=" * 80)
    logger.info("Starting DVF ingestion")
    logger.info("=" * 80)
    
    # Get source file path
    dvf_file = config['source_data']['dvf_file']
    logger.info(f"Reading DVF data from: {dvf_file}")
    
    try:
        # Check file extension
        if dvf_file.endswith('.csv.gz'):
            logger.info("Reading compressed CSV file (gzip) with pandas...")
            import pandas as pd
            import time
            
            start_read = time.time()
            # Read in chunks to show progress and avoid seeming hung
            chunk_size = 500000
            chunks = []
            total_rows = 0
            
            with pd.read_csv(dvf_file, compression='gzip', sep=',', chunksize=chunk_size, low_memory=False, dtype=str) as reader:
                for i, chunk in enumerate(reader):
                    total_rows += len(chunk)
                    chunks.append(chunk)
                    if i % 2 == 0:
                        logger.info(f"Read {total_rows:,} rows so far...")
            
            logger.info(f"Finished reading {total_rows:,} rows in {time.time() - start_read:.2f} seconds")
            pdf_dvf = pd.concat(chunks, ignore_index=True)
            
            # Convert NaN to None for Spark compatibility
            pdf_dvf = pdf_dvf.where(pd.notnull(pdf_dvf), None)
            
            df_dvf = spark.createDataFrame(pdf_dvf)
            
        elif dvf_file.endswith('.xlsx'):
            # Existing Excel logic
            import pandas as pd
            logger.info("Reading Excel file with pandas...")
            pdf_dvf = pd.read_excel(dvf_file)
            # Ensure columns are strings to avoid schema issues if mixed types
            for col in pdf_dvf.columns:
                if pdf_dvf[col].dtype == 'object':
                    pdf_dvf[col] = pdf_dvf[col].astype(str)
            df_dvf = spark.createDataFrame(pdf_dvf)
        else:
            raise ValueError(f"Unsupported file format: {dvf_file}")
        
        initial_count = df_dvf.count()
        logger.info(f"DVF records read: {initial_count:,}")
        
        # Get output path with partitioning
        raw_dvf_base = config['data_lake']['raw']['dvf']
        output_path = get_partition_path(raw_dvf_base, run_date)
        
        logger.info(f"Writing DVF data to: {output_path}")
        
        # Write to Parquet with Snappy compression
        df_dvf.write \
            .mode('overwrite') \
            .parquet(output_path, compression='snappy')
        
        logger.info(f"DVF ingestion completed successfully")
        logger.info(f"Records written: {initial_count:,}")
        
    except Exception as e:
        logger.error(f"Error during DVF ingestion: {str(e)}", exc_info=True)
        raise


def ingest_bpe(spark: SparkSession, config: dict, run_date: str, logger: logging.Logger):
    """
    Ingest BPE data into RAW layer
    
    Args:
        spark: SparkSession
        config: Application configuration
        run_date: Run date string (YYYY-MM-DD)
        logger: Logger instance
    """
    logger.info("=" * 80)
    logger.info("Starting BPE ingestion")
    logger.info("=" * 80)
    
    # Get source file path
    bpe_file = config['source_data']['bpe_file']
    logger.info(f"Reading BPE data from: {bpe_file}")
    
    try:
        # Check file extension
        if bpe_file.endswith('.zip'):
            logger.info("Handling ZIP file containing CSV...")
            import zipfile
            import os
            import pandas as pd
            
            # Extract first
            with zipfile.ZipFile(bpe_file, 'r') as z:
                csv_filename = z.namelist()[0]
                logger.info(f"Extracting {csv_filename} from zip...")
                z.extract(csv_filename, path='.')
                extracted_path = csv_filename
            
            logger.info(f"Reading extracted CSV {extracted_path} with pandas...")
            # Use chunks for BPE as well
            chunk_size = 100000
            chunks = []
            total_rows = 0
            
            # BPE has semicolon separator usually
            with pd.read_csv(extracted_path, sep=';', chunksize=chunk_size, low_memory=False, dtype=str) as reader:
                for i, chunk in enumerate(reader):
                    total_rows += len(chunk)
                    chunks.append(chunk)
                    if i % 5 == 0:
                        logger.info(f"Read {total_rows:,} rows so far...")
                        
            pdf_bpe = pd.concat(chunks, ignore_index=True)
            pdf_bpe = pdf_bpe.where(pd.notnull(pdf_bpe), None)
            
            df_bpe = spark.createDataFrame(pdf_bpe)
            
            # Clean up extracted file to save space? Keeping it for now.
            try:
                os.remove(extracted_path)
            except:
                pass
            
        elif bpe_file.endswith('.xlsx'):
            # Read Excel file with pandas (more reliable for large files)
            import pandas as pd
            logger.info("Reading Excel file with pandas...")
            pdf_bpe = pd.read_excel(bpe_file)
             # Ensure columns are strings
            for col in pdf_bpe.columns:
                if pdf_bpe[col].dtype == 'object':
                    pdf_bpe[col] = pdf_bpe[col].astype(str)
            df_bpe = spark.createDataFrame(pdf_bpe)
        else:
            raise ValueError(f"Unsupported file format: {bpe_file}")
        
        initial_count = df_bpe.count()
        logger.info(f"BPE records read: {initial_count:,}")
        
        # Get output path with partitioning
        raw_bpe_base = config['data_lake']['raw']['bpe']
        output_path = get_partition_path(raw_bpe_base, run_date)
        
        logger.info(f"Writing BPE data to: {output_path}")
        
        # Write to Parquet with Snappy compression
        df_bpe.write \
            .mode('overwrite') \
            .parquet(output_path, compression='snappy')
        
        logger.info(f"BPE ingestion completed successfully")
        logger.info(f"Records written: {initial_count:,}")
        
    except Exception as e:
        logger.error(f"Error during BPE ingestion: {str(e)}", exc_info=True)
        raise


def ingest_communes(spark: SparkSession, config: dict, run_date: str, logger: logging.Logger):
    """
    Ingest commune reference data into RAW layer
    
    Args:
        spark: SparkSession
        config: Application configuration
        run_date: Run date string (YYYY-MM-DD)
        logger: Logger instance
    """
    logger.info("=" * 80)
    logger.info("Starting Communes reference ingestion")
    logger.info("=" * 80)
    
    # Get source file path
    communes_file = config['source_data']['communes_file']
    logger.info(f"Reading Communes data from: {communes_file}")
    
    try:
        # Read CSV file
        df_communes = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .option("encoding", "UTF-8") \
            .csv(communes_file)
        
        initial_count = df_communes.count()
        logger.info(f"Communes records read: {initial_count:,}")
        logger.info(f"Communes columns: {df_communes.columns}")
        
        # Get output path with partitioning
        raw_communes_base = config['data_lake']['raw']['ref_communes']
        output_path = get_partition_path(raw_communes_base, run_date)
        
        logger.info(f"Writing Communes data to: {output_path}")
        
        # Write to Parquet with Snappy compression
        df_communes.write \
            .mode('overwrite') \
            .parquet(output_path, compression='snappy')
        
        logger.info(f"Communes ingestion completed successfully")
        logger.info(f"Records written: {initial_count:,}")
        
    except Exception as e:
        logger.error(f"Error during Communes ingestion: {str(e)}", exc_info=True)
        raise


def main():
    """Main execution function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='RAW Layer Data Ingestion (Feeder)')
    parser.add_argument('--config', required=True, help='Path to app.yaml configuration file')
    parser.add_argument('--run_date', required=True, help='Run date in YYYY-MM-DD format')
    args = parser.parse_args()
    
    # Validate date format
    try:
        datetime.strptime(args.run_date, '%Y-%m-%d')
    except ValueError:
        print(f"Error: Invalid date format. Expected YYYY-MM-DD, got {args.run_date}")
        sys.exit(1)
    
    # Setup logging
    logger = setup_logging('config/logging.yaml', args.run_date)
    
    logger.info("=" * 80)
    logger.info("RAW LAYER DATA INGESTION - FEEDER JOB")
    logger.info("=" * 80)
    logger.info(f"Run date: {args.run_date}")
    logger.info(f"Config file: {args.config}")
    
    # Load application configuration
    config = load_config(args.config)
    logger.info("Application configuration loaded")
    
    # Create Spark session
    logger.info("Creating Spark session...")
    spark = create_spark_session(app_name="IAR-Feeder")
    logger.info(f"Spark session created: {spark.version}")
    
    start_time = datetime.now()
    logger.info(f"Job started at: {start_time}")
    
    try:
        # Ingest DVF data
        ingest_dvf(spark, config, args.run_date, logger)
        
        # Ingest BPE data
        ingest_bpe(spark, config, args.run_date, logger)
        
        # Ingest Communes reference data
        ingest_communes(spark, config, args.run_date, logger)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("FEEDER JOB COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Job ended at: {end_time}")
        logger.info(f"Total duration: {duration:.2f} seconds")
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error("FEEDER JOB FAILED")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)
    
    finally:
        # Stop Spark session
        logger.info("Stopping Spark session...")
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
