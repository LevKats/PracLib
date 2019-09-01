from plotter import Plotter
from value import Value
import numpy as np


def main():
    x = np.random.uniform(0., 100., 100)
    y = 3. * x + 2. + np.random.normal(0., 10., 100)
    err = Value(values=[0.0], syst=10)
    x = np.vectorize(Value)(x)
    y = np.vectorize(Value)(y) + err
    fit = Plotter().add_line(Plotter.Line(x, y * y, "black", "v", True, True, "lol")).plot(show=True)
    print(fit)


if __name__ == '__main__':
    main()
