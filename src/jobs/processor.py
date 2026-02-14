"""
SILVER Layer Data Processing (Processor)
Cleans, validates, enriches, and joins DVF and BPE data
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
    col, sum as spark_sum, count, avg, median, min as spark_min, max as spark_max,
    when, lit, coalesce, rank, dense_rank, row_number, lpad, trim, upper
)

from src.common.spark_session import create_spark_session, load_config
from src.common.paths import get_partition_path
from src.common.validators import DVFValidator, BPEValidator
from src.common.bpe_mapping import get_category, get_category_weight, get_all_categories
from src.common.utils import normalize_code_commune


def setup_logging(log_config_path: str, run_date: str):
    """Setup logging configuration"""
    with open(log_config_path, 'r') as f:
        log_config = yaml.safe_load(f)
    
    date_str = run_date.replace('-', '')
    log_file = f"logs/processor_{date_str}.txt"
    
    Path("logs").mkdir(exist_ok=True)
    
    if 'handlers' in log_config and 'file_processor' in log_config['handlers']:
        log_config['handlers']['file_processor']['filename'] = log_file
    
    logging.config.dictConfig(log_config)
    return logging.getLogger('processor')


def process_dvf_silver(spark: SparkSession, config: dict, run_date: str, logger: logging.Logger):
    """
    Process DVF data to SILVER layer
    
    Args:
        spark: SparkSession
        config: Application configuration
        run_date: Run date string
        logger: Logger instance
        
    Returns:
        Processed DVF DataFrame
    """
    logger.info("=" * 80)
    logger.info("Processing DVF to SILVER layer")
    logger.info("=" * 80)
    
    # Read RAW DVF data
    raw_dvf_path = get_partition_path(config['data_lake']['raw']['dvf'], run_date)
    logger.info(f"Reading RAW DVF from: {raw_dvf_path}")
    
    df_dvf = spark.read.parquet(raw_dvf_path)
    initial_count = df_dvf.count()
    logger.info(f"Initial DVF records: {initial_count:,}")
    
    # Apply all validations
    logger.info("Applying validation rules...")
    
    # Get processing options
    proc_opts = config['processing']
    
    # Apply all DVF validations
    df_dvf = DVFValidator.apply_all_validations(
        df_dvf,
        min_valeur=proc_opts['min_valeur_fonciere'],
        min_surface=proc_opts['min_surface_bati'],
        prix_percentiles=(proc_opts['prix_m2_min_percentile'] / 100, 
                         proc_opts['prix_m2_max_percentile'] / 100)
    )
    
    validated_count = df_dvf.count()
    logger.info(f"Records after validation: {validated_count:,}")
    logger.info(f"Records filtered out: {initial_count - validated_count:,} ({100 * (initial_count - validated_count) / initial_count:.2f}%)")
    
    # Cache the cleaned DVF data (performance optimization)
    logger.info("Caching cleaned DVF DataFrame...")
    df_dvf.cache()
    df_dvf.count()  # Trigger cache
    logger.info("DVF DataFrame cached successfully")
    
    # Aggregate by commune
    logger.info("Aggregating DVF by commune...")
    df_dvf_agg = df_dvf.groupBy('code_commune').agg(
        avg('prix_m2').alias('prix_m2_moyen'),
        spark_sum('prix_m2').alias('prix_m2_sum'),  # For median calculation
        count('*').alias('nb_ventes'),
        spark_min('prix_m2').alias('prix_m2_min'),
        spark_max('prix_m2').alias('prix_m2_max'),
        avg('valeur_fonciere').alias('valeur_fonciere_moyenne'),
        avg('surface_reelle_bati').alias('surface_moyenne')
    )
    
    commune_count = df_dvf_agg.count()
    logger.info(f"Unique communes in DVF: {commune_count:,}")
    
    # Write to SILVER
    silver_dvf_path = get_partition_path(config['data_lake']['silver']['dvf'], run_date)
    logger.info(f"Writing SILVER DVF to: {silver_dvf_path}")
    
    df_dvf_agg.write.mode('overwrite').parquet(silver_dvf_path, compression='snappy')
    logger.info("DVF SILVER processing completed")
    
    return df_dvf_agg


def process_bpe_silver(spark: SparkSession, config: dict, run_date: str, logger: logging.Logger):
    """
    Process BPE data to SILVER layer
    
    Args:
        spark: SparkSession
        config: Application configuration
        run_date: Run date string
        logger: Logger instance
        
    Returns:
        Processed BPE DataFrame
    """
    logger.info("=" * 80)
    logger.info("Processing BPE to SILVER layer")
    logger.info("=" * 80)
    
    # Read RAW BPE data
    raw_bpe_path = get_partition_path(config['data_lake']['raw']['bpe'], run_date)
    logger.info(f"Reading RAW BPE from: {raw_bpe_path}")
    
    df_bpe = spark.read.parquet(raw_bpe_path)
    initial_count = df_bpe.count()
    logger.info(f"Initial BPE records: {initial_count:,}")
    
    # Apply validations
    logger.info("Applying BPE validation rules...")
    df_bpe = BPEValidator.apply_all_validations(df_bpe)
    
    validated_count = df_bpe.count()
    logger.info(f"Records after validation: {validated_count:,}")
    
    # Map TYPEQU to categories using UDF
    from pyspark.sql.functions import udf
    from pyspark.sql.types import StringType, DoubleType
    
    get_category_udf = udf(get_category, StringType())
    get_weight_udf = udf(get_category_weight, DoubleType())
    
    df_bpe = df_bpe.withColumn('categorie', get_category_udf(col('TYPEQU')))
    df_bpe = df_bpe.withColumn('poids', get_weight_udf(col('categorie')))
    
    logger.info("TYPEQU mapped to categories")
    
    # Aggregate by commune and category
    logger.info("Aggregating BPE by commune and category...")
    df_bpe_by_cat = df_bpe.groupBy('code_commune', 'categorie').agg(
        count('*').alias('nb_equipements'),
        spark_sum('poids').alias('score_categorie')
    )
    
    # Pivot to get one column per category
    categories = get_all_categories()
    df_bpe_pivot = df_bpe_by_cat.groupBy('code_commune').pivot('categorie', categories).agg(
        coalesce(spark_sum('score_categorie'), lit(0)).alias('score')
    )
    
    # Rename columns
    for cat in categories:
        if cat in df_bpe_pivot.columns:
            df_bpe_pivot = df_bpe_pivot.withColumnRenamed(cat, f'score_{cat}')
    
    # Calculate total score
    score_columns = [f'score_{cat}' for cat in categories]
    df_bpe_pivot = df_bpe_pivot.withColumn(
        'score_services_total',
        sum([coalesce(col(sc), lit(0)) for sc in score_columns])
    )
    
    # Also get total equipment count
    df_bpe_total = df_bpe.groupBy('code_commune').agg(
        count('*').alias('nb_equipements_total')
    )
    
    # Join pivot with total
    df_bpe_final = df_bpe_pivot.join(df_bpe_total, 'code_commune', 'left')
    
    commune_count = df_bpe_final.count()
    logger.info(f"Unique communes in BPE: {commune_count:,}")
    
    # Write to SILVER
    silver_bpe_path = get_partition_path(config['data_lake']['silver']['bpe'], run_date)
    logger.info(f"Writing SILVER BPE to: {silver_bpe_path}")
    
    df_bpe_final.write.mode('overwrite').parquet(silver_bpe_path, compression='snappy')
    logger.info("BPE SILVER processing completed")
    
    return df_bpe_final


def join_and_enrich(spark: SparkSession, config: dict, run_date: str, 
                   df_dvf: any, df_bpe: any, logger: logging.Logger):
    """
    Join DVF and BPE data and enrich with commune reference
    
    Args:
        spark: SparkSession
        config: Application configuration
        run_date: Run date string
        df_dvf: DVF SILVER DataFrame
        df_bpe: BPE SILVER DataFrame
        logger: Logger instance
        
    Returns:
        Joined and enriched DataFrame
    """
    logger.info("=" * 80)
    logger.info("Joining DVF and BPE data")
    logger.info("=" * 80)
    
    # Read commune reference
    raw_communes_path = get_partition_path(config['data_lake']['raw']['ref_communes'], run_date)
    logger.info(f"Reading commune reference from: {raw_communes_path}")
    
    df_communes = spark.read.parquet(raw_communes_path)
    
    # Normalize commune codes if needed
    # Assuming the reference has columns: COM (code), LIBELLE (name), DEP, REG
    # Adjust column names based on actual v_commune_2024.csv structure
    
    # Join DVF with BPE
    logger.info("Joining DVF with BPE on code_commune...")
    df_joined = df_dvf.join(df_bpe, 'code_commune', 'inner')
    
    joined_count = df_joined.count()
    logger.info(f"Records after DVF-BPE join: {joined_count:,}")
    
    # Enrich with commune reference
    # Note: Adjust column names based on actual commune reference structure
    logger.info("Enriching with commune reference data...")
    
    # Try to identify the correct columns from commune reference
    commune_cols = df_communes.columns
    logger.info(f"Commune reference columns: {commune_cols}")
    
    # Common column name patterns
    code_col = next((c for c in commune_cols if c.upper() in ['COM', 'CODE_COMMUNE', 'CODGEO']), None)
    name_col = next((c for c in commune_cols if c.upper() in ['LIBELLE', 'NOM', 'LIBGEO']), None)
    dep_col = next((c for c in commune_cols if c.upper() in ['DEP', 'DEPARTEMENT']), None)
    reg_col = next((c for c in commune_cols if c.upper() in ['REG', 'REGION']), None)
    
    if code_col:
        # Normalize commune code in reference
        df_communes = df_communes.withColumn('code_commune_ref', lpad(trim(col(code_col)), 5, '0'))
        
        # Select relevant columns
        select_cols = ['code_commune_ref']
        if name_col:
            select_cols.append(name_col)
            df_communes = df_communes.withColumnRenamed(name_col, 'nom_commune')
        if dep_col:
            select_cols.append(dep_col)
            df_communes = df_communes.withColumnRenamed(dep_col, 'dep')
        if reg_col:
            select_cols.append(reg_col)
            df_communes = df_communes.withColumnRenamed(reg_col, 'reg')
        
        df_communes_clean = df_communes.select(*[c for c in select_cols if c != 'code_commune_ref'] + ['code_commune_ref'])
        
        # Join with main dataset
        df_enriched = df_joined.join(
            df_communes_clean,
            df_joined.code_commune == df_communes_clean.code_commune_ref,
            'left'
        ).drop('code_commune_ref')
    else:
        logger.warning("Could not identify code commune column in reference data")
        df_enriched = df_joined
    
    enriched_count = df_enriched.count()
    logger.info(f"Records after enrichment: {enriched_count:,}")
    
    # Apply window functions for ranking
    logger.info("Applying window functions for ranking...")
    
    # Rank by département (if dep column exists)
    if 'dep' in df_enriched.columns:
        window_dep = Window.partitionBy('dep').orderBy(col('prix_m2_moyen').asc())
        df_enriched = df_enriched.withColumn('rang_prix_dep', rank().over(window_dep))
        logger.info("Added departmental ranking by prix_m2")
    
    # Rank by région (if reg column exists)
    if 'reg' in df_enriched.columns:
        window_reg = Window.partitionBy('reg').orderBy(col('prix_m2_moyen').asc())
        df_enriched = df_enriched.withColumn('rang_prix_reg', rank().over(window_reg))
        logger.info("Added regional ranking by prix_m2")
    
    # National ranking
    window_national = Window.orderBy(col('prix_m2_moyen').asc())
    df_enriched = df_enriched.withColumn('rang_prix_national', rank().over(window_national))
    logger.info("Added national ranking by prix_m2")
    
    # Persist the enriched data for performance
    logger.info("Persisting enriched DataFrame...")
    df_enriched.persist()
    df_enriched.count()  # Trigger persist
    logger.info("Enriched DataFrame persisted successfully")
    
    # Write to SILVER joined
    silver_joined_path = get_partition_path(config['data_lake']['silver']['joined'], run_date)
    logger.info(f"Writing SILVER joined data to: {silver_joined_path}")
    
    df_enriched.write.mode('overwrite').parquet(silver_joined_path, compression='snappy')
    logger.info("Joined data written to SILVER")
    
    return df_enriched


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='SILVER Layer Data Processing (Processor)')
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
    logger.info("SILVER LAYER DATA PROCESSING - PROCESSOR JOB")
    logger.info("=" * 80)
    logger.info(f"Run date: {args.run_date}")
    logger.info(f"Config file: {args.config}")
    
    # Load configuration
    config = load_config(args.config)
    logger.info("Application configuration loaded")
    
    # Create Spark session
    logger.info("Creating Spark session...")
    spark = create_spark_session(app_name="IAR-Processor")
    logger.info(f"Spark session created: {spark.version}")
    logger.info(f"Spark UI available at: http://localhost:4040")
    
    start_time = datetime.now()
    logger.info(f"Job started at: {start_time}")
    
    try:
        # Process DVF to SILVER
        df_dvf_silver = process_dvf_silver(spark, config, args.run_date, logger)
        
        # Process BPE to SILVER
        df_bpe_silver = process_bpe_silver(spark, config, args.run_date, logger)
        
        # Join and enrich
        df_joined = join_and_enrich(spark, config, args.run_date, df_dvf_silver, df_bpe_silver, logger)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("PROCESSOR JOB COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Job ended at: {end_time}")
        logger.info(f"Total duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        logger.info(f"Final dataset size: {df_joined.count():,} communes")
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error("PROCESSOR JOB FAILED")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}", exc_info=True)
        sys.exit(1)
    
    finally:
        logger.info("Stopping Spark session...")
        spark.stop()
        logger.info("Spark session stopped")


if __name__ == "__main__":
    main()
