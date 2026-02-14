"""
GOLD Layer Datamart Creation
Calculates IAR and loads data into PostgreSQL
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

from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, lit, coalesce, rank, dense_rank, row_number,
    min as spark_min, max as spark_max, avg, count, sum as spark_sum
)

from src.common.spark_session import create_spark_session, load_config
from src.common.paths import get_partition_path
from src.common.utils import normalize_min_max, calculate_iar_index


def setup_logging(log_config_path: str, run_date: str):
    """Setup logging configuration"""
    with open(log_config_path, 'r') as f:
        log_config = yaml.safe_load(f)
    
    date_str = run_date.replace('-', '')
    log_file = f"logs/datamart_{date_str}.txt"
    
    Path("logs").mkdir(exist_ok=True)
    
    if 'handlers' in log_config and 'file_datamart' in log_config['handlers']:
        log_config['handlers']['file_datamart']['filename'] = log_file
    
    logging.config.dictConfig(log_config)
    return logging.getLogger('datamart')


def create_dm_commune_iar(spark: SparkSession, config: dict, run_date: str, logger: logging.Logger):
    """
    Create dm_commune_iar datamart with IAR calculation
    
    Args:
        spark: SparkSession
        config: Application configuration
        run_date: Run date string
        logger: Logger instance
        
    Returns:
        DataFrame with commune IAR data
    """
    logger.info("=" * 80)
    logger.info("Creating dm_commune_iar datamart")
    logger.info("=" * 80)
    
    # Read SILVER joined data
    silver_joined_path = get_partition_path(config['data_lake']['silver']['joined'], run_date)
    logger.info(f"Reading SILVER joined data from: {silver_joined_path}")
    
    df = spark.read.parquet(silver_joined_path)
    initial_count = df.count()
    logger.info(f"Initial records: {initial_count:,}")
    
    # Fill null service scores with 0
    service_cols = ['score_sante', 'score_education', 'score_transport', 
                   'score_commerce', 'score_services_publics', 'score_loisirs']
    
    for col_name in service_cols:
        if col_name in df.columns:
            df = df.withColumn(col_name, coalesce(col(col_name), lit(0)))
    
    # Fill null score_services_total
    df = df.withColumn('score_services_total', coalesce(col('score_services_total'), lit(0)))
    
    # Normalize prix_m2 to [0, 1]
    logger.info("Normalizing prix_m2...")
    df = normalize_min_max(df, 'prix_m2_moyen', 'prix_m2_norm')
    
    # Normalize score_services_total to [0, 1]
    logger.info("Normalizing score_services_total...")
    df = normalize_min_max(df, 'score_services_total', 'score_services_norm')
    
    # Calculate IAR
    logger.info("Calculating IAR index...")
    proc_opts = config['processing']
    services_weight = proc_opts.get('iar_services_weight', 0.7)
    prix_weight = proc_opts.get('iar_price_weight', 0.3)
    
    logger.info(f"IAR formula: {services_weight} × services_norm + {prix_weight} × (1 - prix_norm)")
    
    df = calculate_iar_index(
        df,
        services_column='score_services_norm',
        prix_column='prix_m2_norm',
        services_weight=services_weight,
        prix_weight=prix_weight
    )
    
    # Calculate rankings by IAR
    logger.info("Calculating IAR rankings...")
    
    # Departmental ranking
    if 'dep' in df.columns:
        window_dep = Window.partitionBy('dep').orderBy(col('IAR').desc())
        df = df.withColumn('rang_dep', rank().over(window_dep))
    
    # Regional ranking
    if 'reg' in df.columns:
        window_reg = Window.partitionBy('reg').orderBy(col('IAR').desc())
        df = df.withColumn('rang_reg', rank().over(window_reg))
    
    # National ranking
    window_national = Window.orderBy(col('IAR').desc())
    df = df.withColumn('rang_national', rank().over(window_national))
    
    logger.info("Rankings calculated")
    
    # Select and rename columns for datamart
    select_cols = [
        'code_commune',
        coalesce(col('nom_commune'), lit('UNKNOWN')).alias('nom_commune'),
        coalesce(col('dep'), lit('00')).alias('dep'),
        coalesce(col('reg'), lit('00')).alias('reg'),
        col('prix_m2_moyen').alias('prix_m2'),
        col('nb_ventes'),
        coalesce(col('prix_m2_min'), lit(0)).alias('prix_m2_min'),
        coalesce(col('prix_m2_max'), lit(0)).alias('prix_m2_max'),
        col('score_services_total'),
    ]
    
    # Add service category scores
    for col_name in service_cols:
        if col_name in df.columns:
            select_cols.append(col(col_name))
    
    # Add equipment count
    if 'nb_equipements_total' in df.columns:
        select_cols.append(col('nb_equipements_total'))
    
    # Add normalized values and IAR
    select_cols.extend([
        col('prix_m2_norm'),
        col('score_services_norm'),
        col('IAR').alias('iar'),
        coalesce(col('rang_dep'), lit(0)).alias('rang_dep'),
        coalesce(col('rang_reg'), lit(0)).alias('rang_reg'),
        col('rang_national')
    ])
    
    df_commune_iar = df.select(*select_cols)
    
    # Show sample
    logger.info("Sample of dm_commune_iar:")
    df_commune_iar.show(5, truncate=False)
    
    # Statistics
    iar_stats = df_commune_iar.select(
        spark_min('iar').alias('iar_min'),
        spark_max('iar').alias('iar_max'),
        avg('iar').alias('iar_moyen')
    ).collect()[0]
    
    logger.info(f"IAR statistics: min={iar_stats['iar_min']:.4f}, max={iar_stats['iar_max']:.4f}, avg={iar_stats['iar_moyen']:.4f}")
    
    return df_commune_iar


def create_dm_dep_stats(df_commune_iar, logger: logging.Logger):
    """
    Create dm_dep_stats datamart with departmental statistics
    
    Args:
        df_commune_iar: Commune IAR DataFrame
        logger: Logger instance
        
    Returns:
        DataFrame with departmental statistics
    """
    logger.info("=" * 80)
    logger.info("Creating dm_dep_stats datamart")
    logger.info("=" * 80)
    
    # Aggregate by department
    df_dep_agg = df_commune_iar.groupBy('dep').agg(
        avg('prix_m2').alias('prix_m2_moyen'),
        avg('score_services_total').alias('score_services_moyen'),
        avg('iar').alias('iar_moyen'),
        count('*').alias('nb_communes'),
        spark_sum('nb_ventes').alias('nb_ventes_total'),
        spark_sum('nb_equipements_total').alias('nb_equipements_total')
    )
    
    # Get top commune per department
    window_top = Window.partitionBy('dep').orderBy(col('iar').desc())
    df_with_rank = df_commune_iar.withColumn('rank_in_dep', rank().over(window_top))
    
    df_top_communes = df_with_rank.filter(col('rank_in_dep') == 1).select(
        col('dep'),
        col('code_commune').alias('top_commune_code'),
        col('nom_commune').alias('top_commune_name'),
        col('iar').alias('top_commune_iar')
    )
    
    # Join aggregates with top communes
    df_dep_stats = df_dep_agg.join(df_top_communes, 'dep', 'left')
    
    # Add median calculation (approximate)
    # Note: For exact median, would need percentile_approx
    df_dep_stats = df_dep_stats.withColumn('prix_m2_median', col('prix_m2_moyen'))  # Simplified
    
    logger.info(f"Departmental statistics created for {df_dep_stats.count()} departments")
    
    # Show sample
    logger.info("Sample of dm_dep_stats:")
    df_dep_stats.show(5, truncate=False)
    
    return df_dep_stats


def load_to_postgres(df, table_name: str, db_config: dict, logger: logging.Logger):
    """
    Load DataFrame to PostgreSQL table
    
    Args:
        df: DataFrame to load
        table_name: Target table name
        db_config: Database configuration
        logger: Logger instance
    """
    logger.info(f"Loading data to PostgreSQL table: {table_name}")
    
    jdbc_url = db_config['connection_string'].replace('postgresql://', 'jdbc:postgresql://')
    
    properties = {
        "user": db_config['user'],
        "password": db_config['password'],
        "driver": "org.postgresql.Driver"
    }
    
    try:
        df.write \
            .jdbc(url=jdbc_url, table=table_name, mode='overwrite', properties=properties)
        
        logger.info(f"Successfully loaded {df.count():,} records to {table_name}")
        
    except Exception as e:
        logger.error(f"Error loading to PostgreSQL: {str(e)}", exc_info=True)
        
        # Fallback: save as CSV for manual import
        csv_path = f"data_lake/gold/{table_name}.csv"
        logger.info(f"Saving to CSV as fallback: {csv_path}")
        df.coalesce(1).write.mode('overwrite').option('header', 'true').csv(csv_path)
        logger.info(f"CSV saved successfully. You can manually import it to PostgreSQL.")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='GOLD Layer Datamart Creation')
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
    logger.info("GOLD LAYER DATAMART CREATION - DATAMART JOB")
    logger.info("=" * 80)
    logger.info(f"Run date: {args.run_date}")
    logger.info(f"Config file: {args.config}")
    
    # Load configuration
    config = load_config(args.config)
    logger.info("Application configuration loaded")
    
    # Create Spark session
    logger.info("Creating Spark session...")
    spark = create_spark_session(app_name="IAR-Datamart")
    logger.info(f"Spark session created: {spark.version}")
    
    start_time = datetime.now()
    logger.info(f"Job started at: {start_time}")
    
    try:
        # Create dm_commune_iar
        df_commune_iar = create_dm_commune_iar(spark, config, args.run_date, logger)
        
        # Create dm_dep_stats
        df_dep_stats = create_dm_dep_stats(df_commune_iar, logger)
        
        # Save to Parquet (GOLD backup)
        gold_path = config['data_lake']['gold']['path']
        logger.info(f"Saving GOLD datamarts to Parquet: {gold_path}")
        
        df_commune_iar.write.mode('overwrite').parquet(f"{gold_path}/dm_commune_iar", compression='snappy')
        df_dep_stats.write.mode('overwrite').parquet(f"{gold_path}/dm_dep_stats", compression='snappy')
        
        logger.info("Parquet files saved successfully")
        
        # Load to PostgreSQL
        db_config = config['database']
        logger.info("Loading datamarts to PostgreSQL...")
        
        load_to_postgres(df_commune_iar, 'dm_commune_iar', db_config, logger)
        load_to_postgres(df_dep_stats, 'dm_dep_stats', db_config, logger)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("DATAMART JOB COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Job ended at: {end_time}")
        logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info(f"Communes processed: {df_commune_iar.count():,}")
        logger.info(f"Departments processed: {df_dep_stats.count():,}")
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error("DATAMART JOB FAILED")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)
    
    finally:
        logger.info("Stopping Spark session...")
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
