"""Utilities for normalizing and validating pandas DataFrame values before SQL insertion.

This module provides a function `normalize_df_for_sql` which coerces column values
to appropriate Python types (or None) according to inferred target SQL types.
It is designed to be safe (non-strict) by default: invalid values are converted to
None and reported in the returned errors list. If strict=True, it raises on errors.

The function is intentionally generic so it can be reused by other SQL processes.
"""
from typing import Tuple, List, Dict
import pandas as pd
import numpy as np


def _is_empty_string_like(x):
    try:
        return isinstance(x, str) and x.strip() == ''
    except Exception:
        return False


def normalize_df_for_sql(df: pd.DataFrame, strict: bool = False) -> Tuple[pd.DataFrame, List[Dict]]:
    """Return a normalized copy of `df` suitable for insertion into SQL and a list of
    normalization issues.

    Rules implemented:
    - Tries to infer numeric columns from object dtype and coerce with pd.to_numeric
    - Tries to infer datetime columns and coerce with pd.to_datetime
    - Boolean columns: map common truthy/falsey strings and values
    - String/object columns: strip whitespace; empty strings -> None
    - All invalid values -> None (SQL NULL)

    Parameters:
        df: pandas DataFrame to normalize (not modified in-place)
        strict: if True, raises ValueError when any invalid value is found

    Returns:
        (df_normalized, errors)
        df_normalized: pandas DataFrame with normalized values (None used for SQL NULL)
        errors: list of dicts {column, count, example}
    """
    df_norm = df.copy()
    errors = []

    for col in df_norm.columns:
        series = df_norm[col]
        original_non_na = series.notna()
        
        # 1. Try datetime conversion first (before numeric, since dates might look numeric)
        if pd.api.types.is_datetime64_any_dtype(series):
            # Already datetime, just ensure valid
            coerced = pd.to_datetime(series, errors='coerce')
            invalid_mask = coerced.isna() & original_non_na
            if invalid_mask.any():
                errors.append({'column': col, 'count': int(invalid_mask.sum()), 'example': str(series[invalid_mask].iloc[0])})
            df_norm[col] = coerced
            continue
        
        # 2. Try numeric conversion FIRST for object columns (before datetime)
        # Numeric is more specific than datetime (dates can look like numbers)
        if pd.api.types.is_numeric_dtype(series):
            # Already numeric, just standardize None
            df_norm[col] = series.where(series.notna(), None)
            continue
        
        # Try coercing object columns to numeric
        if series.dtype == 'object':
            try:
                test_numeric = pd.to_numeric(series, errors='coerce')
                # Count non-empty original values (exclude empty strings and 'None' strings)
                non_empty_mask = original_non_na & ~series.apply(_is_empty_string_like) & (series.astype(str).str.lower() != 'none')
                
                # If more than 50% of non-empty values convert successfully, treat as numeric
                valid_nums = test_numeric.notna() & non_empty_mask
                if non_empty_mask.sum() > 0 and valid_nums.sum() / non_empty_mask.sum() > 0.5:
                    invalid_mask = test_numeric.isna() & non_empty_mask
                    if invalid_mask.any():
                        errors.append({'column': col, 'count': int(invalid_mask.sum()), 'example': str(series[invalid_mask].iloc[0])})
                    df_norm[col] = test_numeric
                    continue
            except Exception:
                pass
        
        # Try coercing object columns to datetime (after numeric)
        if series.dtype == 'object':
            try:
                test_datetime = pd.to_datetime(series, errors='coerce', format='mixed')
                # If more than 50% of non-null values convert successfully, treat as datetime
                # AND check if values don't look like pure numbers
                valid_dates = test_datetime.notna() & original_non_na
                if valid_dates.sum() > 0.5 * original_non_na.sum():
                    # Double check: if column has patterns like YYYY-MM-DD, treat as datetime
                    sample_valid = series[original_non_na].head(3).astype(str)
                    looks_like_date = any('-' in str(v) or '/' in str(v) for v in sample_valid if v)
                    
                    if looks_like_date:
                        invalid_mask = test_datetime.isna() & original_non_na & ~series.apply(_is_empty_string_like)
                        if invalid_mask.any():
                            errors.append({'column': col, 'count': int(invalid_mask.sum()), 'example': str(series[invalid_mask].iloc[0])})
                        df_norm[col] = test_datetime
                        continue
            except Exception:
                pass
        
        # 3. Try boolean conversion
        if pd.api.types.is_bool_dtype(series):
            df_norm[col] = series.where(series.notna(), None)
            continue
        
        # Try coercing object columns to boolean
        if series.dtype == 'object':
            def _to_bool(v):
                if pd.isna(v) or _is_empty_string_like(v):
                    return None
                s = str(v).strip().lower()
                if s in ('1', 'true', 't', 'yes', 'y', 'si', 'sí'):
                    return True
                if s in ('0', 'false', 'f', 'no', 'n'):
                    return False
                return None
            
            # Check if column looks boolean
            try:
                test_bool = series.map(_to_bool)
                valid_bools = test_bool.notna()
                if valid_bools.sum() > 0.5 * original_non_na.sum():
                    invalid_mask = test_bool.isna() & original_non_na
                    if invalid_mask.any():
                        errors.append({'column': col, 'count': int(invalid_mask.sum()), 'example': str(series[invalid_mask].iloc[0])})
                    df_norm[col] = test_bool
                    continue
            except Exception:
                pass
        
        # 4. Fallback: treat as string -> strip whitespace, empty -> None
        try:
            def _clean_string(v):
                if pd.isna(v):
                    return None
                s = str(v).strip()
                return None if s == '' or s.lower() == 'none' or s.lower() == 'nan' else s
            
            df_norm[col] = series.map(_clean_string)
        except Exception as e:
            errors.append({'column': col, 'count': int(original_non_na.sum()), 'example': str(e)})

    if errors and strict:
        raise ValueError(f"Normalization errors detected: {errors}")

    return df_norm, errors
