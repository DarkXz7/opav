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
