import json
from datetime import datetime

line_size = 100


def format_timestamp(timestamp: int) -> str:
    dt = datetime.utcfromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


class MichelsonFormatterError(ValueError):
    pass


def is_framed(node):
    if node['prim'] in {'Pair', 'Left', 'Right', 'Some',
                        'pair', 'or', 'option', 'map', 'big_map', 'list', 'set', 'contract', 'lambda'}:
        return True
    elif node['prim'] in {'key', 'unit', 'signature', 'operation',
                          'int', 'nat', 'string', 'bytes', 'mutez', 'bool', 'key_hash', 'timestamp', 'address'}:
        return 'annots' in node
    return False


def is_complex(node):
    return node['prim'] == 'LAMBDA' \
           or node['prim'].startswith('IF')


def is_inline(node):
    return node['prim'] == 'PUSH'


def is_script(node):
    return all(map(
        lambda x: isinstance(x, dict) and x.get('prim') in ['parameter', 'storage', 'code'],
        node))


def format_node(node, indent='', inline=False, is_root=False, wrapped=False):
    if isinstance(node, list):
        is_script_root = is_root and is_script(node)
        seq_indent = indent if is_script_root else indent + ' ' * 2
        items = list(map(lambda x: format_node(x, seq_indent, inline, wrapped=True), node))
        if items:
            length = len(indent) + sum(map(len, items)) + 4
            space = '' if is_script_root else ' '
            if inline or length < line_size:
                seq = f'{space}; '.join(items)
            else:
                seq = f'{space};\n{seq_indent}'.join(items)
            return seq if is_script_root else f'{{ {seq} }}'
        else:
            return '{}'

    elif isinstance(node, dict):
        if node.get('prim'):
            expr = ' '.join([node['prim']] + node.get('annots', []))
            args = node.get('args', [])

            if is_complex(node):
                arg_indent = indent + ' ' * 2
                items = list(map(lambda x: format_node(x, arg_indent, inline), args))
                length = len(indent) + len(expr) + sum(map(len, items)) + len(items) + 1
                if inline or length < line_size:
                    expr = f'{expr} {" ".join(items)}'
                else:
                    expr = f'\n{arg_indent}'.join([expr] + items)

            elif len(args) == 1:
                arg_indent = indent + ' ' * (len(expr) + 1)
                expr = f'{expr} {format_node(args[0], arg_indent, inline)}'

            elif len(args) > 1:
                arg_indent = indent + ' ' * 2
                alt_indent = indent + ' ' * (len(expr) + 2)
                for arg in args:
                    item = format_node(arg, arg_indent, inline)
                    length = len(indent) + len(expr) + len(item) + 1
                    if inline or is_inline(node) or length < line_size:
                        arg_indent = alt_indent
                        expr = f'{expr} {item}'
                    else:
                        expr = f'{expr}\n{arg_indent}{item}'

            if is_framed(node) and not is_root and not wrapped:
                return f'({expr})'
            else:
                return expr
        else:
            assert len(node) == 1
            core_type, value = next(iter(node.items()))
            if core_type == 'int':
                return value
            elif core_type == 'bytes':
                return f'0x{value}'
            elif core_type == 'string':
                return json.dumps(value)
            else:
                assert False
    else:
        assert False, node


def micheline_to_michelson(data, inline=False):
    """
    Converts micheline expression into formatted Michelson source
    :param data: Micheline expression
    :param inline: produce single line, used for tezos-client arguments (False by default)
    :return: string
    """
    try:
        return format_node(data, inline=inline, is_root=True)
    except (KeyError, IndexError, TypeError):
        raise MichelsonFormatterError('Failed to format Micheline expression')
