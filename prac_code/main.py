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
    fit = Plotter().add_line(Plotter.Line(x, y * y, "black", "v", True, True, "lol")).plot(show=True)
    print(fit)


if __name__ == '__main__':
    main()
