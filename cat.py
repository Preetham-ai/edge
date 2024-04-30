def parse_expr(s: str, idx: int):
    idx = skip_space(s, idx)
    if s[idx] == '(':
        # a list
        idx += 1
        l = []
        while True:
            idx = skip_space(s, idx)
            if idx >= len(s):
                raise Exception('unbalanced parenthesis')
            if s[idx] == ')':
                idx += 1
                break
            idx, v = parse_expr(s, idx)
            l.append(v)

        return idx, l
    elif s[idx] == ')':
        raise Exception('bad parenthesis')
    else:
        # an atom
        start = idx
        while idx < len(s) and (not s[idx].isspace()) and s[idx] not in '()':
            idx += 1
        if start == idx:
            raise Exception('empty program')
        return idx, parse_atom(s[start:idx])


def skip_space(s, idx):
    while 1:
        save = idx
        while idx < len(s) and s[idx].isspace():
            idx += 1
        if idx < len(s) and s[idx] == ';':
            idx += 1
            while idx < len(s) and s[idx] != '\n':
                idx += 1
        if idx == save:
            break
    return idx

def parse_atom(s):
    import json
    try:
        return ['val', json.loads(s)]
    except json.JSONDecodeError:
        return s
    
def pl_parse(s):
    idx, node = parse_expr(s, 0)
    idx = skip_space(s, idx)
    if idx < len(s):
        raise ValueError('trailing garbage')
    return node

def name_loopup(env, key):
    while env:
        current, env = env
        if key in current:
            return current
    raise ValueError('undefined name')

def pl_eval(env,node):
    if not isinstance(node, list):
        assert isinstance(node, str)
        return name_loopup(env, node)[node]
    
    if len(node) == 0:
        raise ValueError('empty list')

    # bool, number, string and etc
    if len(node) == 2 and node[0] == 'val':
        return node[1]
    
    # binary operators
    import operator

    binops = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '=': operator.eq,
    '!=': operator.ne,
    '>=': operator.ge,
    '>': operator.gt,
    '<=': operator.le,
    '<': operator.lt,
    'and': operator.and_,
    'or': operator.or_,
    'xor': operator.xor,
    }

    if len(node) == 3 and node[0] in binops:
        op = binops[node[0]]
        return op(pl_eval(node[1]), pl_eval(node[2]))
    
    # unary operators
    unops = {
    '-': operator.neg,
    'not': operator.not_,
    '~': operator.not_,
    }

    if len(node) == 2 and node[0] in unops:
        op = unops[node[0]]
        return op(pl_eval(node[1]))

    if len(node) == 4 and node[0] == '?':
        _, cond, yes, no = node
        if pl_eval(cond):
            return pl_eval(yes)
        else:
            return pl_eval(no)
    
    #If-Else
    #do, then, else
    if node[0] in ('pounce', 'watch', 'purr') and len(node) > 1:
        new_env = (dict(), env)
        for val in node[1:]:
            val = pl_eval(new_env, val)
            return val

    # Print statement
    if node[0] == 'meow':
        return print(*(pl_eval(val) for val in node[1:]))
    raise ValueError('unknown expression')


def evaluate(s):
    return pl_eval(pl_parse(s))

string = str(input())
print(evaluate(string))

    