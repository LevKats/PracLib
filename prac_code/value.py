"""
Value module

Contains Value class that can be used to calculate errors and value_operator_decorator to write methods
"""
from prac_code.praclib import get_pair
from prac_code.praclib import get_deviation
from prac_code.praclib import print_with_deviation
from prac_code.praclib import rounding
from prac_code.praclib import dict_adding

from sympy import Symbol
from copy import deepcopy

from scipy.stats import tstd
import numpy as np


def value_operator_decorator(operator):
    def custom_operator(first, second):
        if type(second) is float or type(second) is int:
            return operator(first, Value(const=second))
        return operator(first, second)

    return custom_operator


class Value:
    """
    Value class

    Use it for calculations with values that has errors
    """

    __count = 0

    NumberOfDigit = 10

    def __init__(self, *args, **kwargs):
        """
        :param kwargs:
        dict -- dict {symbol: (value, error)}
        symbol -- symbol
        ignorest -- set of symbols that are not used to calculate error
        """
        if len(args) == 1:
            val = deepcopy(args[0])
            self.__symbol = Symbol("const{}".format(Value.__count))
            Value.__count += 1
            self.__dct = {self.__symbol: get_pair(value=val, deviation=0.0)}
            self.__ignoreset = {self.__symbol}
        elif "dict" in kwargs and "symbol" in kwargs and "ignoreset" in kwargs:
            self.__create_from_formula(kwargs["dict"], kwargs["symbol"], kwargs["ignoreset"])
        elif "values" in kwargs and "syst" in kwargs:
            if "name" in kwargs:
                name = kwargs["name"]
            else:
                name = "c{}".format(Value.__count)
                Value.__count += 1
            self.__create_new_symbol(name, kwargs["values"], kwargs["syst"])
        elif "const" in kwargs:
            val = deepcopy(kwargs["const"])
            self.__symbol = Symbol("const{}".format(Value.__count))
            Value.__count += 1
            self.__dct = {self.__symbol: get_pair(value=val, deviation=0.0)}
            self.__ignoreset = {self.__symbol}
        elif len(args) == 2:
            name = "c{}".format(Value.__count)
            Value.__count += 1
            self.__create_new_symbol(name, [args[0]], args[1])
        else:
            raise ValueError(
                "incorrect **args: there must be dict, symbol and ignoreset or values and syst or const"
            )

    def __create_from_formula(self, dct, symb, ignore):
        self.__dct = dct
        self.__symbol = symb
        self.__ignoreset = ignore

    def __create_new_symbol(self, name, values, syst):
        try:
            self.__symbol = Symbol(name)
            self.__ignoreset = set()
            if len(values) >= 3:
                val, er = np.array(values).mean(), tstd(values)
            else:
                val, er = values[0], 0.0
            er = (er ** 2 + syst ** 2) ** 0.5
            self.__dct = {self.__symbol: get_pair(value=val, deviation=er)}  # added systematic(?) deviation
        except Exception:
            raise ValueError("incorrect name or values or error")

    def print_value_error(self, **kwargs):
        """:return string with Tex code"""
        notebook = True
        ignore = set()
        if "notebook" in kwargs:
            notebook = kwargs["notebook"]
        if "ignore" in kwargs:
            ignore = {v.__symbol for v in kwargs["ignore"]}

        return print_with_deviation(self.__symbol, self.__dct, self.__ignoreset | ignore, notebook)

    def get_value_error(self):
        """:return (value, error) tuple that are rounded by praclib.rounding"""
        er = get_deviation(self.__symbol, self.__dct, self.__ignoreset)[2]
        vls = dict((s, self.__dct[s][0]) for s in self.__dct)
        return rounding(float(self.__symbol.subs(vls)), float(er))

    @value_operator_decorator
    def __add__(self, other):
        return Value(
            symbol=self.__symbol + other.__symbol, dict=dict_adding(self.__dct, other.__dct),
            ignoreset=self.__ignoreset | other.__ignoreset
        )

    def __radd__(self, other):
        return Value(const=other) + self

    @value_operator_decorator
    def __sub__(self, other):
        return Value(
            symbol=self.__symbol - other.__symbol, dict=dict_adding(self.__dct, other.__dct),
            ignoreset=self.__ignoreset | other.__ignoreset
        )

    def __rsub__(self, other):
        return Value(const=other) - self

    @value_operator_decorator
    def __mul__(self, other):
        return Value(
            symbol=self.__symbol * other.__symbol, dict=dict_adding(self.__dct, other.__dct),
            ignoreset=self.__ignoreset | other.__ignoreset
        )

    def __rmul__(self, other):
        return Value(const=other) * self

    @value_operator_decorator
    def __truediv__(self, other):
        return Value(
            symbol=self.__symbol / other.__symbol, dict=dict_adding(self.__dct, other.__dct),
            ignoreset=self.__ignoreset | other.__ignoreset
        )

    def __rtruediv__(self, other):
        return Value(const=other) / self

    def __neg__(self):
        return Value(symbol=-self.__symbol, dict=self.__dct, ignoreset=self.__ignoreset)

    def __pos__(self):
        return Value(symbol=self.__symbol, dict=self.__dct, ignoreset=self.__ignoreset)

    def __str__(self):
        val, er = self.get_value_error()
        format_string = "{:." + str(Value.NumberOfDigit) + "g} {} {:." + str(Value.NumberOfDigit) + "g}"
        return format_string.format(val, chr(177), er)

    @value_operator_decorator
    def __pow__(self, other):
        return Value(
            symbol=self.__symbol ** other.__symbol, dict=dict_adding(self.__dct, other.__dct),
            ignoreset=self.__ignoreset | other.__ignoreset
        )

    def __rpow__(self, other):
        return Value(const=other) ** self

    @value_operator_decorator
    def __eq__(self, other):
        a, er_a = self.get_value_error()
        b, er_b = other.get_value_error()
        if a == b:
            return True
        elif a < b:
            return a + er_a <= b - er_b
        else:
            return b + er_b <= a - er_a

    @value_operator_decorator
    def __lt__(self, other):
        a, er_a = self.get_value_error()
        b, er_b = other.get_value_error()
        return a + er_a < b + er_b

    @value_operator_decorator
    def __le__(self, other):
        return self < other or self == other

    @value_operator_decorator
    def __gt__(self, other):
        return other < self

    @value_operator_decorator
    def __ge__(self, other):
        return other <= self

    def use_func(self, func):
        """:return Value object with symbol equal to func(self.__symbol)"""
        return Value(symbol=func(self.__symbol), dict=self.__dct, ignoreset=self.__ignoreset)


def create_error(errorsize):
    return Value(0, errorsize)
