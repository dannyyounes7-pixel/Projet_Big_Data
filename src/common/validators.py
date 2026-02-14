"""
Data Validation Rules for DVF and BPE
"""
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, length, lpad, trim
from typing import Tuple


class DVFValidator:
    """Validation rules for DVF (Demandes de Valeurs Foncières) data"""
    
    @staticmethod
    def validate_valeur_fonciere(df: DataFrame, min_value: float = 0) -> DataFrame:
        """
        Validation Rule 1: valeur_fonciere must be > 0
        
        Args:
            df: Input DataFrame
            min_value: Minimum acceptable value
            
        Returns:
            Filtered DataFrame
        """
        return df.filter(col('valeur_fonciere') > min_value)
    
    @staticmethod
    def validate_surface_bati(df: DataFrame, min_surface: float = 0) -> DataFrame:
        """
        Validation Rule 2: surface_reelle_bati must be > 0
        
        Args:
            df: Input DataFrame
            min_surface: Minimum acceptable surface
            
        Returns:
            Filtered DataFrame
        """
        return df.filter(col('surface_reelle_bati') > min_surface)
    
    @staticmethod
    def validate_date_mutation(df: DataFrame) -> DataFrame:
        """
        Validation Rule 3: date_mutation must be valid and not null
        
        Args:
            df: Input DataFrame
            
        Returns:
            Filtered DataFrame
        """
        return df.filter(col('date_mutation').isNotNull())
    
    @staticmethod
    def validate_code_commune(df: DataFrame) -> DataFrame:
        """
        Validation Rule 4: code_commune must not be null and normalized to 5 chars
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with validated and normalized code_commune
        """
        df = df.filter(col('code_commune').isNotNull())
        # Normalize to 5 characters with leading zeros
        df = df.withColumn('code_commune', lpad(trim(col('code_commune')), 5, '0'))
        return df
    
    @staticmethod
    def validate_prix_m2_range(df: DataFrame, 
                               lower_percentile: float = 0.01, 
                               upper_percentile: float = 0.99) -> Tuple[DataFrame, float, float]:
        """
        Validation Rule 5: prix_m2 within realistic range (remove outliers)
        
        Args:
            df: Input DataFrame with prix_m2 column
            lower_percentile: Lower percentile for outlier removal (default: 1%)
            upper_percentile: Upper percentile for outlier removal (default: 99%)
            
        Returns:
            Tuple of (filtered DataFrame, lower_bound, upper_bound)
        """
        # Calculate percentiles
        percentiles = df.approxQuantile('prix_m2', [lower_percentile, upper_percentile], 0.01)
        lower_bound = percentiles[0]
        upper_bound = percentiles[1]
        
        # Filter outliers
        df_filtered = df.filter(
            (col('prix_m2') >= lower_bound) & 
            (col('prix_m2') <= upper_bound)
        )
        
        return df_filtered, lower_bound, upper_bound
    
    @staticmethod
    def validate_type_local(df: DataFrame, valid_types: list = None) -> DataFrame:
        """
        Additional Validation Rule 6: type_local must be in valid list
        
        Args:
            df: Input DataFrame
            valid_types: List of valid type_local values
            
        Returns:
            Filtered DataFrame
        """
        if valid_types is None:
            # Default valid types for residential properties
            valid_types = ['Maison', 'Appartement', 'Local industriel. commercial ou assimilé']
        
        return df.filter(col('type_local').isin(valid_types))
    
    @staticmethod
    def validate_nb_pieces(df: DataFrame, min_pieces: int = 0) -> DataFrame:
        """
        Additional Validation Rule 7: nombre_pieces_principales must be > 0
        
        Args:
            df: Input DataFrame
            min_pieces: Minimum number of pieces
            
        Returns:
            Filtered DataFrame
        """
        return df.filter(col('nombre_pieces_principales') > min_pieces)
    
    @staticmethod
    def apply_all_validations(df: DataFrame, 
                             min_valeur: float = 0,
                             min_surface: float = 0,
                             prix_percentiles: Tuple[float, float] = (0.01, 0.99)) -> DataFrame:
        """
        Apply all DVF validation rules
        
        Args:
            df: Input DataFrame
            min_valeur: Minimum valeur_fonciere
            min_surface: Minimum surface_reelle_bati
            prix_percentiles: Tuple of (lower, upper) percentiles for prix_m2
            
        Returns:
            Validated DataFrame
        """
        # Rule 1: valeur_fonciere > 0
        df = DVFValidator.validate_valeur_fonciere(df, min_valeur)
        
        # Rule 2: surface_reelle_bati > 0
        df = DVFValidator.validate_surface_bati(df, min_surface)
        
        # Rule 3: date_mutation not null
        df = DVFValidator.validate_date_mutation(df)
        
        # Rule 4: code_commune normalized
        df = DVFValidator.validate_code_commune(df)
        
        # Calculate prix_m2 before Rule 5
        df = df.withColumn('prix_m2', col('valeur_fonciere') / col('surface_reelle_bati'))
        
        # Rule 5: prix_m2 outlier removal
        df, lower, upper = DVFValidator.validate_prix_m2_range(
            df, prix_percentiles[0], prix_percentiles[1]
        )
        
        return df


class BPEValidator:
    """Validation rules for BPE (Base Permanente des Équipements) data"""
    
    @staticmethod
    def validate_depcom(df: DataFrame) -> DataFrame:
        """
        Validate and normalize DEPCOM (code commune)
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with validated and normalized code_commune
        """
        df = df.filter(col('DEPCOM').isNotNull())
        # Normalize to 5 characters with leading zeros
        df = df.withColumn('code_commune', lpad(trim(col('DEPCOM')), 5, '0'))
        return df
    
    @staticmethod
    def validate_typequ(df: DataFrame) -> DataFrame:
        """
        Validate TYPEQU (type d'équipement) is not null
        
        Args:
            df: Input DataFrame
            
        Returns:
            Filtered DataFrame
        """
        return df.filter(col('TYPEQU').isNotNull())
    
    @staticmethod
    def apply_all_validations(df: DataFrame) -> DataFrame:
        """
        Apply all BPE validation rules
        
        Args:
            df: Input DataFrame
            
        Returns:
            Validated DataFrame
        """
        df = BPEValidator.validate_depcom(df)
        df = BPEValidator.validate_typequ(df)
        return df
