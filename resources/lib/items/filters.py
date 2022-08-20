import operator
from resources.lib.addon.modimp import importmodule


def is_excluded(item, filter_key=None, filter_value=None, filter_operator=None, exclude_key=None, exclude_value=None, exclude_operator=None, is_listitem=False):
    """ Checks if item should be excluded based on filter/exclude values
    Values can optional be a dict which contains module, method, and kwargs
    """
    def is_filtered(d, k, v, exclude=False, operator_type=None):
        if isinstance(v, dict):
            v = importmodule(v['module'], v['method'])(**v['kwargs'])
        comp = getattr(operator, operator_type or 'contains')
        boolean = False if exclude else True  # Flip values if we want to exclude instead of include
        if k and v and k in d and comp(str(d[k]).lower(), str(v).lower()):
            boolean = exclude
        return boolean

    if not item:
        return

    if is_listitem:
        il, ip = item.infolabels, item.infoproperties
    else:
        il, ip = item.get('infolabels', {}), item.get('infoproperties', {})

    if filter_key and filter_value:
        if filter_value == 'is_empty':
            if il.get(filter_key) or ip.get(filter_key):
                return True
        if filter_key in il:
            if is_filtered(il, filter_key, filter_value, operator_type=filter_operator):
                return True
        if filter_key in ip:
            if is_filtered(ip, filter_key, filter_value, operator_type=filter_operator):
                return True

    if exclude_key and exclude_value:
        if exclude_value == 'is_empty':
            if not il.get(exclude_key) and not ip.get(exclude_key):
                return True
        if exclude_key in il:
            if is_filtered(il, exclude_key, exclude_value, True, operator_type=exclude_operator):
                return True
        if exclude_key in ip:
            if is_filtered(ip, exclude_key, exclude_value, True, operator_type=exclude_operator):
                return True
