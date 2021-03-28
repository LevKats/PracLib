from matplotlib import pyplot as plt
from collections import namedtuple
from os.path import join
from multiprocessing import Pool

import numpy as np

from scipy.stats import pearsonr
from scipy.optimize import curve_fit


class Plotter:
    Line = namedtuple("Line", [
        'x_value',
        'y_value',
        'color',
        'marker',
        'draw_error',
        'fit',
        'legend',
        'func',
        'p0'
    ])

    FitParameters = namedtuple("FitParameters", [
        "legend",
        "a", "sigma_a",
        "b", "sigma_b",
        "r"
    ])
    FitParametersNonLinear = namedtuple("FitParametersNonLinear", [
        "legend",
        "params", "sigma_params",
    ])

    @staticmethod
    def get_new_line(**kwargs):
        return Plotter.Line(
            kwargs['x_value'],
            kwargs['y_value'],
            kwargs['color'],
            kwargs['marker'],
            kwargs['draw_error'],
            kwargs['fit'],
            kwargs['legend'],
            kwargs['func'] if 'func' in kwargs else None,
            kwargs['p0'] if 'p0' in kwargs else None
        )

    class Scale:
        LOG = "log"
        LINEAR = "linear"
        SYMLOG = "symlog"
        LOGIT = "logit"

    SIZE = 1.0
    NUMBER_OF_SIGMA = 1.0
    PLT_YSCALE = "linear"
    PLT_XSCALE = "linear"
    NUM_PROC = 5
    NUM_POINTS = 100

    def __init__(self, **kwargs):
        self.__lines = kwargs['lines'] if 'lines' in kwargs else []
        self.__draw_legend = kwargs['draw_legend'] if 'draw_legend' in kwargs else False
        self.__axis_x = kwargs['axis_x'] if 'axis_x' in kwargs else 'x'
        self.__axis_y = kwargs['axis_y'] if 'axis_y' in kwargs else 'y'
        self.__title = kwargs['title'] if 'title' in kwargs else '$y(x)$'
        self.__name = kwargs['name'] if 'name' in kwargs else "nonamefigure"

    def set_title(self, title):
        return Plotter(
            draw_legend=self.__draw_legend,
            axis_x=self.__axis_x,
            axis_y=self.__axis_y,
            title=title,
            lines=self.__lines,
            name=self.__name
        )

    def set_name(self, title):
        return Plotter(
            draw_legend=self.__draw_legend,
            axis_x=self.__axis_x,
            axis_y=self.__axis_y,
            title=self.__title,
            lines=self.__lines,
            name=title
        )

    def set_x_name(self, name):
        return Plotter(
            draw_legend=self.__draw_legend,
            axis_x=name,
            axis_y=self.__axis_y,
            title=self.__title,
            lines=self.__lines,
            name=self.__name
        )

    def set_y_name(self, name):
        return Plotter(
            draw_legend=self.__draw_legend,
            axis_x=self.__axis_x,
            axis_y=name,
            title=self.__title,
            lines=self.__lines,
            name=self.__name
        )

    def add_line(self, line):
        return Plotter(
            draw_legend=self.__draw_legend,
            axis_x=self.__axis_x,
            axis_y=self.__axis_y,
            title=self.__title,
            lines=self.__lines + [line],
            name=self.__name
        )

    def __create(self):
        plt.figure(num=1, figsize=(8, 6))
        plt.title(self.__title, size=14, loc='center')
        plt.xlabel(self.__axis_x, size=14)
        plt.ylabel(self.__axis_y, size=14)
        plt.yscale(Plotter.PLT_YSCALE)
        plt.xscale(Plotter.PLT_XSCALE)

    @staticmethod
    def get_tup(x):
        return x.get_value_error()

    @staticmethod
    def __line_fit(line, x_data, y_data, sigmay):
        (res_a, res_b), pcov = curve_fit(lambda x, a, b: x * a + b, x_data, y_data, sigma=sigmay)
        a_deviation, b_deviation = np.sqrt(np.diag(pcov))
        line_r = pearsonr(x_data, y_data)[0]
        ffit = np.polynomial.polynomial.Polynomial((res_b, res_a))
        y_fit = ffit(x_data)
        plt.plot(x_data, y_fit, color=line.color, linestyle='-', marker='', linewidth=2 * Plotter.SIZE)
        return Plotter.FitParameters(line.legend, res_a, a_deviation, res_b, b_deviation, line_r)

    @staticmethod
    def __nonlinear_fit(line, x_data, y_data, sigmay):
        if line.p0 is not None:
            res_params, pcov = curve_fit(line.func, x_data, y_data, p0=line.p0, sigma=sigmay)
        else:
            res_params, pcov = curve_fit(line.func, x_data, y_data, sigma=sigmay)
        x_fit = np.linspace(x_data.min(), x_data.max(), Plotter.NUM_POINTS)
        y_fit = line.func(x_fit, *res_params)
        plt.plot(x_fit, y_fit, color=line.color, linestyle='-', marker='', linewidth=2 * Plotter.SIZE)
        return Plotter.FitParametersNonLinear(line.legend, res_params, np.sqrt(np.diag(pcov)))

    def __draw_lines(self):
        fit_lines = []
        for line in self.__lines:
            with Pool(Plotter.NUM_PROC) as p:
                x_tup = p.map(Plotter.get_tup, line.x_value)
                y_tup = p.map(Plotter.get_tup, line.y_value)

            x_val_error = np.array(
                list(map(
                    lambda tup: [float(tup[0]), float(tup[1])],
                    x_tup
                ))
            )
            y_val_error = np.array(
                list(map(
                    lambda tup: [float(tup[0]), float(tup[1])],
                    y_tup
                ))
            )
            # x_data = [float(x.get_value_error()[0]) for x in line.x_value]
            # y_data = [float(y.get_value_error()[0]) for y in line.y_value]
            x_data = x_val_error[::, 0]
            y_data = y_val_error[::, 0]
            plt.scatter(
                x_data, y_data,
                color=line.color, marker=line.marker, s=4 * Plotter.SIZE, label=line.legend
            )
            # sigmax = [Plotter.NUMBER_OF_SIGMA * float(x.get_value_error()[1]) for x in line.x_value]
            # sigmay = [Plotter.NUMBER_OF_SIGMA * float(y.get_value_error()[1]) for y in line.y_value]
            sigmax = x_val_error[::, 1] * Plotter.NUMBER_OF_SIGMA
            sigmay = y_val_error[::, 1] * Plotter.NUMBER_OF_SIGMA

            if line.fit and line.func is None:
                fit_lines.append(Plotter.__line_fit(line, x_data, y_data, sigmay))
            elif line.fit and line.func is not None:
                fit_lines.append(Plotter.__nonlinear_fit(line, x_data, y_data, sigmay))
            if line.draw_error:
                plt.errorbar(x_data, y_data, ecolor=line.color,
                             yerr=sigmay, xerr=sigmax,
                             fmt='none', linewidth=Plotter.SIZE / 1.5)
        return fit_lines

    def plot(self, **kwargs):
        self.__create()
        res = self.__draw_lines()

        plt.grid(linewidth=Plotter.SIZE / 3.0, linestyle='--')
        plt.tick_params(axis='both', direction='in', which='both', width=Plotter.SIZE / 2.0)
        if 'ylim' in kwargs:
            ymin, ymax = kwargs['ylim']
            plt.ylim(ymin, ymax)

        if 'xlim' in kwargs:
            xmin, xmax = kwargs['xlim']
            plt.xlim(xmin, xmax)

        if self.__draw_legend:
            plt.legend(loc='upper left')

        if 'save' in kwargs and kwargs['save']:
            plt.savefig(join("images", self.__name + ".png"), format='png', dpi=300)
        if 'show' in kwargs and kwargs['show']:
            plt.show()
        return res
