# Template filter para acceder a elementos de un diccionario por clave o lista por índice

from django import template

register = template.Library()

@register.filter
def get_item(dictionary_or_list, key):
    """
    Obtiene un elemento de un diccionario por su clave o de una lista por índice
    Funciona tanto con dict.get(key) como con list[index]
    """
    if isinstance(dictionary_or_list, dict):
        return dictionary_or_list.get(key, None)
    elif isinstance(dictionary_or_list, (list, tuple)):
        try:
            # Convertir key a int si es posible (para índices de lista)
            index = int(key) if isinstance(key, str) and key.isdigit() else key
            return dictionary_or_list[index]
        except (IndexError, ValueError, TypeError):
            return None
    else:
        return None

@register.filter
def apply_column_mapping(columns, args):
    """
    Aplica mapeos de nombres a una lista de columnas.
    Args debe ser una cadena "table_name,column_mappings_json"
    Retorna lista de nombres mapeados o los originales si no hay mapeo.
    
    Uso: {{ columns|apply_column_mapping:"table_name,process.column_mappings" }}
    """
    if not columns or not isinstance(columns, list):
        return columns
    
    if not args:
        return columns
    
    # Separar argumentos
    parts = args.split(',', 1)
    if len(parts) != 2:
        return columns
    
    table_name = parts[0]
    column_mappings = parts[1]
    
    # Si column_mappings es un string, intentar evaluar como dict
    if isinstance(column_mappings, str):
        try:
            import json
            column_mappings = json.loads(column_mappings)
        except:
            return columns
    
    # Si no hay mapeos o no es un dict, retornar columnas originales
    if not column_mappings or not isinstance(column_mappings, dict):
        return columns
    
    # Si no hay mapeo para esta tabla, retornar columnas originales
    if table_name not in column_mappings:
        return columns
    
    # Aplicar mapeos
    table_mappings = column_mappings[table_name]
    mapped_columns = [table_mappings.get(col, col) for col in columns]
    
    return mapped_columns

@register.simple_tag
def get_mapped_columns(columns, table_name, column_mappings):
    """
    Template tag para obtener columnas con nombres mapeados.
    Retorna la lista de columnas con sus nombres personalizados si existen.
    
    Uso: {% get_mapped_columns columns table_name process.column_mappings as mapped_cols %}
    """
    if not columns or not isinstance(columns, list):
        return columns
    
    # Si no hay mapeos, retornar originales
    if not column_mappings or not isinstance(column_mappings, dict):
        return columns
    
    # Si no hay mapeo para esta tabla, retornar originales
    if table_name not in column_mappings:
        return columns
    
    # Aplicar mapeos
    table_mappings = column_mappings[table_name]
    mapped_columns = [table_mappings.get(col, col) for col in columns]
    
    return mapped_columns
