import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
import csv
import os
import sys
from PySide import QtGui, QtCore
# define gui app and widget
app = QtGui.QApplication(sys.argv)
# Widget class with changed icon


def f(x, a, b, c, d):
    return a * np.exp(b * x) + c * np.exp(d * x)


def fit_from_csv(file_name):
    param_letters = 'abcdefghijklmnopqrstuvwxyz'
    ext = os.path.splitext(os.path.split(file_name)[-1])[-1]
    single_name = os.path.splitext(os.path.split(file_name)[-1])[0]
    data_table = np.genfromtxt(file_name, dtype=['S6', 'float', 'float'],
                               delimiter=',', skip_header=1, usecols=range(3),
                               names=['sample', 'days', 'penetrability_mm'])
    categories = np.unique(data_table['sample'])
    params_list = dict()
    with open(single_name + '_with_fits' + ext, 'w') as outfile:
        writer = csv.writer(outfile, lineterminator='\n')
        writer.writerow(['sample', 'days', 'penetrability_mm']
                        + [param_letters[y] for y in range(4)]
                        + ['R^2', 'Calc(penetrability_mm)'])
        for k in categories:
            popt1, pcov1 = optimize.curve_fit(f,
                                              data_table[data_table['sample'] == k]['days'],
                                              data_table[data_table['sample'] == k]['penetrability_mm'])
            params_list[k] = popt1
            for j in data_table[data_table['sample'] == k]:
                j_list = list(j)
                if ~ np.isinf(np.inf):
                    writer.writerow(j_list
                                    + popt1.tolist()
                                    + np.sqrt(np.diag(pcov1)).tolist())
                else:
                    writer.writerow(j_list
                                    + popt1.tolist()
                                    + [np.inf])
        del y, k, j
    return params_list


(filename, _) = \
    QtGui.QFileDialog.getOpenFileName(None,
                                      caption='Open file',
                                      dir=os.path.splitdrive(sys.path[0])[0],
                                      filter='*.csv')

fit_from_csv(filename)