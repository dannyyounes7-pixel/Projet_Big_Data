"""
Spark Session Factory and Configuration Loader
"""
import yaml
from pyspark.sql import SparkSession
from pathlib import Path


def load_config(config_path: str) -> dict:
    """
    Load YAML configuration file
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Dictionary with configuration
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_spark_session(app_name: str = None, spark_config_path: str = "config/spark.yaml") -> SparkSession:
    """
    Create and configure Spark Session
    
    Args:
        app_name: Application name (optional, will use config if not provided)
        spark_config_path: Path to Spark configuration file
        
    Returns:
        Configured SparkSession
    """
    # Load Spark configuration
    config = load_config(spark_config_path)
    spark_conf = config.get('spark', {})
    
    # Use provided app_name or get from config
    app_name = app_name or spark_conf.get('app_name', 'IAR-BigData-Platform')
    
    # Create Spark Session Builder
    builder = SparkSession.builder.appName(app_name)
    
    # Set master
    master = spark_conf.get('master', 'local[*]')
    builder = builder.master(master)
    
    # Driver configuration
    driver_conf = spark_conf.get('driver', {})
    if 'memory' in driver_conf:
        builder = builder.config('spark.driver.memory', driver_conf['memory'])
    if 'maxResultSize' in driver_conf:
        builder = builder.config('spark.driver.maxResultSize', driver_conf['maxResultSize'])
    
    # Executor configuration
    executor_conf = spark_conf.get('executor', {})
    if 'memory' in executor_conf:
        builder = builder.config('spark.executor.memory', executor_conf['memory'])
    if 'cores' in executor_conf:
        builder = builder.config('spark.executor.cores', executor_conf['cores'])
    if 'instances' in executor_conf:
        builder = builder.config('spark.executor.instances', executor_conf['instances'])
    
    # SQL configuration
    sql_conf = spark_conf.get('sql', {})
    if 'shuffle' in sql_conf:
        shuffle_conf = sql_conf['shuffle']
        if 'partitions' in shuffle_conf:
            builder = builder.config('spark.sql.shuffle.partitions', shuffle_conf['partitions'])
    
    if 'adaptive' in sql_conf:
        adaptive_conf = sql_conf['adaptive']
        if 'enabled' in adaptive_conf:
            builder = builder.config('spark.sql.adaptive.enabled', adaptive_conf['enabled'])
        if 'coalescePartitions' in adaptive_conf:
            coalesce_conf = adaptive_conf['coalescePartitions']
            if 'enabled' in coalesce_conf:
                builder = builder.config('spark.sql.adaptive.coalescePartitions.enabled', 
                                       coalesce_conf['enabled'])
    
    # Serialization
    if 'serializer' in spark_conf:
        builder = builder.config('spark.serializer', spark_conf['serializer'])
    
    kryo_conf = spark_conf.get('kryoserializer', {})
    if 'buffer' in kryo_conf and 'max' in kryo_conf['buffer']:
        builder = builder.config('spark.kryoserializer.buffer.max', kryo_conf['buffer']['max'])
    
    # Default parallelism
    default_conf = spark_conf.get('default', {})
    if 'parallelism' in default_conf:
        builder = builder.config('spark.default.parallelism', default_conf['parallelism'])
    
    # UI configuration
    ui_conf = spark_conf.get('ui', {})
    if 'enabled' in ui_conf:
        builder = builder.config('spark.ui.enabled', ui_conf['enabled'])
    if 'port' in ui_conf:
        builder = builder.config('spark.ui.port', ui_conf['port'])
    
    # Compression
    io_conf = spark_conf.get('io', {})
    if 'compression' in io_conf and 'codec' in io_conf['compression']:
        builder = builder.config('spark.io.compression.codec', io_conf['compression']['codec'])
    
    # Dynamic allocation
    dynamic_conf = spark_conf.get('dynamicAllocation', {})
    if 'enabled' in dynamic_conf:
        builder = builder.config('spark.dynamicAllocation.enabled', dynamic_conf['enabled'])
    if 'minExecutors' in dynamic_conf:
        builder = builder.config('spark.dynamicAllocation.minExecutors', dynamic_conf['minExecutors'])
    if 'maxExecutors' in dynamic_conf:
        builder = builder.config('spark.dynamicAllocation.maxExecutors', dynamic_conf['maxExecutors'])
    
    # Create session
    spark = builder.getOrCreate()
    
    # Set log level
    log_conf = spark_conf.get('log', {})
    log_level = log_conf.get('level', 'WARN')
    spark.sparkContext.setLogLevel(log_level)
    
    return spark


def stop_spark_session(spark: SparkSession):
    """
    Stop Spark Session
    
    Args:
        spark: SparkSession to stop
    """
    if spark:
        spark.stop()
