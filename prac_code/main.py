from prac_code.plotter import Plotter
from prac_code.value import Value, create_error
import numpy as np


def main():
    x = np.random.uniform(0., 100., 100)
    y = 3. * x + 2. + np.random.normal(0., 10., 100)
    err = create_error(10)
    x = np.vectorize(Value)(x) + err/2
    y = np.vectorize(Value)(y) + err
    (x[0]**2 + x[1]**2).print_value_error(notebook=False)
    fit = Plotter().add_line(Plotter.Line(x, y * y, "black", "v", True, True, "lol", None, None))\
        .add_line(Plotter.Line(x, y * y, "gray", "v", True, True, "lol2", (lambda _x, a, b, c: a * _x**2 + b * _x + c), None))\
        .plot(show=True)
    print(fit)
    print(Value(1.0, 2.0))


if __name__ == '__main__':
    main()
