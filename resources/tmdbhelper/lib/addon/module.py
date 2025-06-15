def get_all_module_class_objects(module_name):  # module_name = __name__
    import sys
    import inspect
    return [
        class_object
        for _, class_object
        in inspect.getmembers(
            sys.modules[module_name],
            lambda member: inspect.isclass(member) and member.__module__ == module_name
        )
    ]


def get_all_module_class_objects_by_priority(module_name, condition_func=None):
    return [
        j for j, _ in sorted([
            (i, i.priority)
            for i in get_all_module_class_objects(module_name)
        ], key=lambda x: x[1]) if not condition_func or condition_func(j)
    ]
