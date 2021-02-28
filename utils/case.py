import re


SNAKE_CASE_REGEX = re.compile(r'(.)([A-Z][a-z]+)')
SNAKE_CASE_2_REGEX = re.compile(r'([a-z0-9])([A-Z])')


def snake_case(s):
    s = SNAKE_CASE_REGEX.sub(r'\1_\2', s)
    return SNAKE_CASE_2_REGEX.sub(r'\1_\2', s).lower()


def camel_case(s):
    components = s.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])