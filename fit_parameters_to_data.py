import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
import csv
import os
import sys
import inspect
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
    # expected columns: [category, X, Y]
    data_table = np.genfromtxt(file_name, dtype=['S6', 'float', 'float'],
                               delimiter=',', skip_header=0, usecols=range(3),
                               names=True)
    out_file_name = single_name + '_with_fits' + ext
    var_names = data_table.dtype.names
    categories = np.unique(data_table[var_names[0]])
    params_list = dict()
    with open(out_file_name, 'w') as outfile:
        writer = csv.writer(outfile, lineterminator='\n')
        writer.writerow([y for y in var_names]
                        + [param_letters[y] for y in
                           range(len(inspect.getargspec(f)))]
                        + ['R^2', 'Calc(Y)'])
        for k in categories:
            # y (x) = a*exp(b*x) + c*exp(d*x)
            # y'(x) = a*b*exp(b*x) + c*d*exp(d*x)
            # Initial estimates to be taken at initial and final 2
            # Points assuming sufficiently far, ex. for a, b
            # P1    a*exp(b*x[0]) = y[0]
            # P2    a*exp(b*x[1]) = y[1]
            #       a = y[0]/exp(b*x[0]) , b = ln(y[1]/a)/x[1]
            #       a = y[0]/exp(x[0]/x[1]*ln(y[1]/a))
            #       a = y[0]/y[1]^(x[0]/x[1])*a^(x[0]/x[1])
            #       a^(1-x[0]/x[1]) = y[0]/y[1]^(x[0]/x[1])
            #       a = (y[0]/y[1]^(x[0]/x[1]))^(1/(1-x[0]/x[1]))
            # P3    c*exp(d*x[-2]) = y[-2]
            # P4    c*exp(d*x[-1]) = y[-1]
            x = data_table[data_table[var_names[0]] == k][var_names[1]]
            y = data_table[data_table[var_names[0]] == k][var_names[2]]
            a0 = (y[0] / y[1] ** (x[0] / x[1])) ** (1 / (1 - x[0] / x[1]))
            b0 = np.log(y[1] / a0) / x[1]
            c0 = (y[1] / y[-1] ** (x[1] / x[-1])) ** (1 / (1 - x[1] / x[-1]))
            d0 = np.log(y[-1] / c0) / x[-1]
            p0 = [a0, b0, c0, d0]
            popt1, pcov1, infodict, mesg, ier = \
                optimize.curve_fit(f, x, y, p0, full_output=True,
                                   ftol=1.0e-6, xtol=1.0e-6)
            params_list[k] = popt1
            for j in data_table[data_table[var_names[0]] == k]:
                j_list = list(j)
                if np.isinf(pcov1).any():
                    writer.writerow(j_list
                                    + popt1.tolist()
                                    + [np.inf])
                else:
                    writer.writerow(j_list
                                    + popt1.tolist()
                                    + np.sqrt(np.diag(pcov1)).tolist())
        del y, k, j
    return params_list, out_file_name


(filename, _) = \
    QtGui.QFileDialog.getOpenFileName(None,
                                      caption='Open file',
                                      dir=os.path.splitdrive(sys.path[0])[0],
                                      filter='*.csv')

msgBox = QtGui.QMessageBox()
msgBox.setWindowTitle('Saved file.')
msgBox.setStandardButtons(QtGui.QMessageBox.Close)
QtCore.QObject.connect(msgBox.button(QtGui.QMessageBox.Close),
                       QtCore.SIGNAL('clicked()'), msgBox.close)

if filename != '':
    return_value, out_file_name = fit_from_csv(filename)

    msgBox.setText('Saved: ' + os.path.dirname(filename) + out_file_name)

# exit 'main loop'
#sys.exit()
sys.exit(msgBox.exec_())