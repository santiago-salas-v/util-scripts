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
    data_table = np.genfromtxt(file_name, dtype=['S6', 'float', 'float'],
                               delimiter=',', skip_header=0, usecols=range(3),
                               names=True)
    out_file_name = single_name + '_with_fits' + ext
    if data_table.dtype.names != ('sample', 'days', 'penetrability_mm'):
        return "Invalid file. File must have columns: " \
               "('sample', 'days', 'penetrability_mm')"
    else:
        categories = np.unique(data_table['sample'])
        params_list = dict()
        with open(out_file_name, 'w') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow(['sample', 'days', 'penetrability_mm']
                            + [param_letters[y] for y in range(len(inspect.getargspec(f)))]
                            + ['R^2', 'Calc(penetrability_mm)'])
            for k in categories:
                # Initial estimates to be taken at initial and final 2
                # Points, ex. for a, b
                # P1    a*exp(b*x[0]) = y[0]
                # P2    a*exp(b*x[1]) = y[1]
                #       a = y[0]/exp(b*x[0]) , b = ln(y[1]/a)/x[1]
                #       a = y[0]/exp(x[0]/x[1]*ln(y[1]/a))
                #       a = y[0]/y[1]^(x[0]/x[1])*a^(x[0]/x[1])
                #       a^(1-x[0]/x[1]) = y[0]/y[1]^(x[0]/x[1])
                #       a = (y[0]/y[1]^(x[0]/x[1]))^(1/(1-x[0]/x[1]))
                # P3    c*exp(d*x[-2]) = y[-2]
                # P4    c*exp(d*x[-1]) = y[-1]
                x = data_table[data_table['sample'] == k]['days']
                y = data_table[data_table['sample'] == k]['penetrability_mm']
                a0 = (y[0]/y[1]**(x[0]/x[1]))**(1/(1-x[0]/x[1]))
                b0 = np.log(y[1]/a0)/x[1]
                c0 = (y[-2]/y[-1]**(x[-2]/x[-1]))**(1/(1-x[-2]/x[-1]))
                d0 = np.log(y[-1]/c0)/x[-1]
                popt1, pcov1 = optimize.curve_fit(f, x, y, [a0*1000, b0, c0, d0])
                params_list[k] = popt1
                for j in data_table[data_table['sample'] == k]:
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

if filename != '':
    return_value, out_file_name = fit_from_csv(filename)

msgBox = QtGui.QMessageBox()
msgBox.setText('Saved: ' + os.path.dirname(filename) + out_file_name)
msgBox.setWindowTitle('Saved file.')
msgBox.setStandardButtons(QtGui.QMessageBox.Close)
QtCore.QObject.connect(msgBox.button(QtGui.QMessageBox.Close),
                       QtCore.SIGNAL('clicked()'), msgBox.close)

# exit 'main loop'
sys.exit(msgBox.exec_())
#sys.exit(app.exec_())