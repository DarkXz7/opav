# Template filter para acceder a elementos de un diccionario por clave

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un elemento de un diccionario por su clave"""
    return dictionary.get(key, None)
