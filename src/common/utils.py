"""
Utility Functions for Data Processing
"""
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, trim, upper, regexp_replace, when
from typing import Tuple


def clean_string_column(df: DataFrame, column_name: str) -> DataFrame:
    """
    Clean string column: trim whitespace and convert to uppercase
    
    Args:
        df: Input DataFrame
        column_name: Name of column to clean
        
    Returns:
        DataFrame with cleaned column
    """
    return df.withColumn(column_name, upper(trim(col(column_name))))


def normalize_code_commune(df: DataFrame, source_column: str = 'code_commune') -> DataFrame:
    """
    Normalize code commune to 5 characters with leading zeros
    
    Args:
        df: Input DataFrame
        source_column: Name of source column
        
    Returns:
        DataFrame with normalized code_commune
    """
    from pyspark.sql.functions import lpad
    
    df = df.withColumn(
        'code_commune',
        lpad(trim(col(source_column)), 5, '0')
    )
    return df


def remove_outliers_iqr(df: DataFrame, column_name: str, k: float = 1.5) -> DataFrame:
    """
    Remove outliers using IQR (Interquartile Range) method
    
    Args:
        df: Input DataFrame
        column_name: Name of column to check for outliers
        k: IQR multiplier (default: 1.5)
        
    Returns:
        DataFrame with outliers removed
    """
    # Calculate Q1, Q3
    quantiles = df.approxQuantile(column_name, [0.25, 0.75], 0.01)
    q1 = quantiles[0]
    q3 = quantiles[1]
    iqr = q3 - q1
    
    # Calculate bounds
    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr
    
    # Filter outliers
    df_filtered = df.filter(
        (col(column_name) >= lower_bound) & 
        (col(column_name) <= upper_bound)
    )
    
    return df_filtered


def remove_outliers_percentile(df: DataFrame, 
                               column_name: str, 
                               lower_percentile: float = 0.01,
                               upper_percentile: float = 0.99) -> Tuple[DataFrame, float, float]:
    """
    Remove outliers using percentile method
    
    Args:
        df: Input DataFrame
        column_name: Name of column to check for outliers
        lower_percentile: Lower percentile threshold (default: 1%)
        upper_percentile: Upper percentile threshold (default: 99%)
        
    Returns:
        Tuple of (filtered DataFrame, lower_bound, upper_bound)
    """
    # Calculate percentiles
    percentiles = df.approxQuantile(column_name, [lower_percentile, upper_percentile], 0.01)
    lower_bound = percentiles[0]
    upper_bound = percentiles[1]
    
    # Filter outliers
    df_filtered = df.filter(
        (col(column_name) >= lower_bound) & 
        (col(column_name) <= upper_bound)
    )
    
    return df_filtered, lower_bound, upper_bound


def normalize_min_max(df: DataFrame, column_name: str, new_column_name: str = None) -> DataFrame:
    """
    Normalize column to [0, 1] using min-max scaling
    
    Args:
        df: Input DataFrame
        column_name: Name of column to normalize
        new_column_name: Name for normalized column (default: column_name + '_norm')
        
    Returns:
        DataFrame with normalized column
    """
    if new_column_name is None:
        new_column_name = f"{column_name}_norm"
    
    # Calculate min and max
    stats = df.agg({column_name: 'min', column_name: 'max'}).collect()[0]
    min_val = stats[f'min({column_name})']
    max_val = stats[f'max({column_name})']
    
    # Avoid division by zero
    if max_val == min_val:
        df = df.withColumn(new_column_name, when(col(column_name).isNotNull(), 0.5).otherwise(None))
    else:
        df = df.withColumn(
            new_column_name,
            (col(column_name) - min_val) / (max_val - min_val)
        )
    
    return df


def calculate_iar_index(df: DataFrame, 
                        services_column: str = 'score_services_norm',
                        prix_column: str = 'prix_m2_norm',
                        services_weight: float = 0.7,
                        prix_weight: float = 0.3) -> DataFrame:
    """
    Calculate IAR (Indice d'Attractivité Rationnelle)
    
    Formula: IAR = services_weight × services_norm + prix_weight × (1 - prix_norm)
    
    Args:
        df: Input DataFrame with normalized columns
        services_column: Name of normalized services column
        prix_column: Name of normalized prix column
        services_weight: Weight for services (default: 0.7)
        prix_weight: Weight for prix (default: 0.3)
        
    Returns:
        DataFrame with IAR column
    """
    df = df.withColumn(
        'IAR',
        services_weight * col(services_column) + prix_weight * (1 - col(prix_column))
    )
    
    return df


def safe_divide(numerator_col: str, denominator_col: str, default_value: float = 0.0):
    """
    Safely divide two columns, handling division by zero
    
    Args:
        numerator_col: Name of numerator column
        denominator_col: Name of denominator column
        default_value: Value to use when denominator is 0 or null
        
    Returns:
        Column expression for safe division
    """
    return when(
        (col(denominator_col).isNull()) | (col(denominator_col) == 0),
        default_value
    ).otherwise(col(numerator_col) / col(denominator_col))


def cast_columns_to_types(df: DataFrame, column_types: dict) -> DataFrame:
    """
    Cast multiple columns to specified types
    
    Args:
        df: Input DataFrame
        column_types: Dictionary mapping column names to types
                     Example: {'col1': 'int', 'col2': 'double'}
        
    Returns:
        DataFrame with casted columns
    """
    for col_name, col_type in column_types.items():
        if col_name in df.columns:
            df = df.withColumn(col_name, col(col_name).cast(col_type))
    
    return df


def fill_null_values(df: DataFrame, fill_values: dict) -> DataFrame:
    """
    Fill null values in specified columns
    
    Args:
        df: Input DataFrame
        fill_values: Dictionary mapping column names to fill values
                    Example: {'col1': 0, 'col2': 'UNKNOWN'}
        
    Returns:
        DataFrame with filled values
    """
    return df.fillna(fill_values)
