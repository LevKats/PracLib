from sympy import sqrt, Symbol, diff, evaluate, latex, simplify
from decimal import Decimal


def rounding(value, error):
    value = Decimal(value)
    error = Decimal(error)
    if error == Decimal(0):
        return value, error
    e = error.as_tuple().exponent + len(error.as_tuple().digits) - 1
    n = -e + (1 if error.as_tuple().digits[0] == 1 else 0)
    return round(value, n), round(error, n)


def get_pair(**kwargs):
    return kwargs['value'], kwargs['deviation']


def print_with_deviation(f, dct, ignoreset=set(), notebook=True):
    dct3 = {}
    for name in ignoreset:
        dct3[name] = dct[name][0]
    f = simplify(f.subs(dct3))
    dev = get_deviation(f, dct, ignoreset)
    dct2 = dict((s, dct[s][0]) for s in dct)
    rnd = rounding(float(f.subs(dct2)), float(dev[2]))
    with evaluate(False):
        rnd = (rnd[0], f.subs(dct2), rnd[1])
    res = latex(dev[0]) + '=' + latex(dev[1]) + '={}'.format(dev[2]) + r'\\' +\
          latex(f) + '= {} = {} \\pm {}'.format(rnd[1], rnd[0], rnd[2])
    if notebook:
        return res
    print('$$' + res + '$$')


def get_deviation(f, dct, ignoreset=set()):
    # {sumbol:(value, deviation)}
    sdct = dict((s, Symbol('sigma_' + str(s))) for s in dct)
    sdct2 = dict((sdct[s], dct[s][1]) for s in dct)
    res = sqrt(sum([(diff(f, s) * sdct[s]) ** 2 for s in dct if s not in ignoreset]))
    res = simplify(res)
    vls = dict((s, dct[s][0]) for s in dct)
    vls.update(sdct2)
    with evaluate(False):
        step = res.subs(vls)
    return res, step, res.subs(vls)


def dict_adding(a, b):
    res = dict((i, a[i]) for i in a)
    res.update(b)
    return res


def cut_array(arr, how_to_cut):
    left = []
    right = []
    l = 0
    for i in how_to_cut:
        left.append(l)
        l += i
        right.append(l)
    return tuple(arr[left[i]:right[i]:] for i in range(len(left)))


if __name__ == "__main__":
    pass
