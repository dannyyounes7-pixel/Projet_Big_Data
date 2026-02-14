"""
Path Utilities for Data Lake Partitioning
"""
from datetime import datetime
from pathlib import Path


def get_partition_path(base_path: str, run_date: str = None) -> str:
    """
    Generate partition path with year/month/day structure
    
    Args:
        base_path: Base path for the data
        run_date: Date string in format YYYY-MM-DD (default: today)
        
    Returns:
        Full path with partitions: base_path/year=YYYY/month=MM/day=DD
    """
    if run_date is None:
        date_obj = datetime.now()
    else:
        date_obj = datetime.strptime(run_date, '%Y-%m-%d')
    
    year = date_obj.year
    month = f"{date_obj.month:02d}"
    day = f"{date_obj.day:02d}"
    
    partition_path = f"{base_path}/year={year}/month={month}/day={day}"
    return partition_path


def create_partition_directories(base_path: str, run_date: str = None):
    """
    Create partition directories if they don't exist
    
    Args:
        base_path: Base path for the data
        run_date: Date string in format YYYY-MM-DD (default: today)
    """
    partition_path = get_partition_path(base_path, run_date)
    Path(partition_path).mkdir(parents=True, exist_ok=True)
    return partition_path


def get_latest_partition(base_path: str) -> str:
    """
    Get the latest partition path based on year/month/day
    
    Args:
        base_path: Base path to search for partitions
        
    Returns:
        Path to the latest partition or None if no partitions exist
    """
    base = Path(base_path)
    
    if not base.exists():
        return None
    
    # Find all year directories
    year_dirs = sorted([d for d in base.glob('year=*') if d.is_dir()], reverse=True)
    
    if not year_dirs:
        return None
    
    # For the latest year, find latest month
    for year_dir in year_dirs:
        month_dirs = sorted([d for d in year_dir.glob('month=*') if d.is_dir()], reverse=True)
        
        if not month_dirs:
            continue
        
        # For the latest month, find latest day
        for month_dir in month_dirs:
            day_dirs = sorted([d for d in month_dir.glob('day=*') if d.is_dir()], reverse=True)
            
            if day_dirs:
                return str(day_dirs[0])
    
    return None


def parse_partition_date(partition_path: str) -> datetime:
    """
    Extract date from partition path
    
    Args:
        partition_path: Path with year/month/day partitions
        
    Returns:
        datetime object
    """
    path = Path(partition_path)
    
    # Extract year, month, day from path
    parts = str(path).split('/')
    
    year = None
    month = None
    day = None
    
    for part in parts:
        if part.startswith('year='):
            year = int(part.split('=')[1])
        elif part.startswith('month='):
            month = int(part.split('=')[1])
        elif part.startswith('day='):
            day = int(part.split('=')[1])
    
    if year and month and day:
        return datetime(year, month, day)
    
    return None
