from importlib import import_module


def lazyimport_module(global_dict, module_name, import_as=None, import_attr=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            global_name = import_as or module_name
            if not global_dict[global_name]:
                module = import_module(module_name)
                global_dict[global_name] = getattr(module, import_attr) if import_attr else module
            return func(*args, **kwargs)
        return wrapper
    return decorator
