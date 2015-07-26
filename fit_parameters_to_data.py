__author__ = 'Santiago Salas'
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize, stats
import csv
import os
import sys
import inspect
from string import ascii_lowercase
from functools import partial
from PySide import QtGui, QtCore
# define gui app and widget
app = QtGui.QApplication(sys.argv)
# Widget class with changed icon


def f(x, *params):
    return params[0] * np.exp(params[1] * x) + \
           params[2] * np.exp(params[3] * x)


def fit_from_csv(file_name, conf_level=0.95):
    param_letters = ascii_lowercase
    ext = os.path.splitext(os.path.split(file_name)[-1])[-1]
    single_name = os.path.splitext(os.path.split(file_name)[-1])[0]
    # expected columns: [category, X, Y]
    data_table = np.genfromtxt(file_name, dtype=['S25', 'float', 'float'],
                               delimiter=',', skip_header=0,
                               usecols=range(3), names=True)
    output_file_name = single_name + '_with_fits' + ext
    var_names = data_table.dtype.names
    categories = np.unique(data_table[var_names[0]])
    params_list = dict()
    with open(output_file_name, 'w') as outfile:
        writer = csv.writer(outfile, lineterminator='\n')
        writer.writerow([y for y in var_names]
                        + [param_letters[y] for y in
                           range(len(inspect.getargspec(f)))]
                        + ['R^2', 'Calc(y=a*exp(b*x)+c*exp(d*x))',
                           'y-LCL:'+format(conf_level, '0.0%'),
                           'y-UCL:'+format(conf_level, '0.0%')])
        for k in categories:
            # y (x) = a*exp(b*x) + c*exp(d*x)
            # y'(x) = a*b*exp(b*x) + c*d*exp(d*x)
            # Initial estimates to be taken at initial (2) and final (1)
            # Points assuming sufficiently far, ex. for a, b
            # P1    a*exp(b*x[0]) = y[0]
            # P2    a*exp(b*x[1]) = y[1]
            #       a = y[0]/exp(b*x[0]) , b = ln(y[1]/a)/x[1]
            #       a = y[0]/exp(x[0]/x[1]*ln(y[1]/a))
            #       a = y[0]/y[1]^(x[0]/x[1])*a^(x[0]/x[1])
            #       a^(1-x[0]/x[1]) = y[0]/y[1]^(x[0]/x[1])
            #       a = (y[0]/y[1]^(x[0]/x[1]))^(1/(1-x[0]/x[1]))
            # P2    c*exp(d*x[1]) = y[1]
            # P4    c*exp(d*x[-1]) = y[-1]
            x = data_table[data_table[var_names[0]] == k][var_names[1]]
            y = data_table[data_table[var_names[0]] == k][var_names[2]]
            a0 = (y[0] / y[1] ** (x[0] / x[1])) ** (1 / (1 - x[0] / x[1]))
            b0 = np.log(y[1] / a0) / x[1]
            c0 = (y[1] / y[-1] ** (x[1] / x[-1])) ** (1 / (1 - x[1] / x[-1]))
            d0 = np.log(y[-1] / c0) / x[-1]
            p0 = [a0, b0, c0, d0]
            # Curve fitting
            popt, pcov, infodict, mesg, ier = \
                optimize.curve_fit(f, x, y, p0, full_output=True,
                                   ftol=1.0e-6, xtol=1.0e-6)
            params_list[k] = popt
            # Standard deviation errors on the parameters
            perr = np.sqrt(np.diag(pcov))
            # Correlation Coefficient
            # Confidence intervals (95%, 97.5% percentile, P(X>1.96)=2.5%)
            n_stdev_plus_minus = \
                stats.norm.ppf(conf_level + (1.0 - conf_level)/2.0)
            popt_high = popt + n_stdev_plus_minus * perr
            popt_low = popt - n_stdev_plus_minus * perr
            # Sum of Squares Due to Error SSE, Sum of squares of residuals SSR
            sse = sum((y - f(x, *popt))**2)
            ssr = sum((f(x, *popt) - np.mean(y))**2)
            r_squared = 1 - sse/ssr
            for j in data_table[data_table[var_names[0]] == k]:
                j_list = list(j)
                x = j_list[1]
                y = f(x, *popt)
                y_LCL = f(x, *popt_low)
                y_UCL = f(x, *popt_high)
                if np.isinf(pcov).any():
                    writer.writerow(j_list
                                    + popt.tolist()
                                    + [r_squared]
                                    + [y, y_LCL, y_UCL])
                else:
                    writer.writerow(j_list
                                    + popt.tolist()
                                    + [r_squared]
                                    + [y, y_LCL, y_UCL])
        del y, k, j
    return params_list, output_file_name

class MainForm(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.group = QtGui.QGroupBox('Fit Data to model', parent=self)
        self.setWindowTitle('Fit')
        self.setToolTip('Fit Data to model')
        self.setWindowIcon(QtGui.QIcon(
            os.path.join(sys.path[0], *['utils', 'graph-4x.png'])))
        self.open = QtGui.QPushButton(QtGui.QIcon(
            os.path.join(sys.path[0], *['utils', 'folder-4x.png'])), '')
        self.open.clicked.connect(partial(operate_on_file, self))
        self.label1 = QtGui.QLabel('1 - alpha = ')
        self.conf_level = QtGui.QLineEdit()
        self.conf_level.setPlaceholderText(str(0.95))
        self.open.setToolTip('Open')
        h_box = QtGui.QHBoxLayout()
        h_box.addWidget(self.open)
        h_box.addWidget(self.label1)
        h_box.addWidget(self.conf_level)
        self.group.setLayout(h_box)

def operate_on_file(form):

    (filename, _) = \
        QtGui.QFileDialog.getOpenFileName(None,
                                          caption='Open file',
                                          dir=os.path.splitdrive(sys.path[0])[0],
                                          filter='*.csv')

    if filename != '':
        try:
            conf_level = float(form.findChild(QtGui.QLineEdit).text())
        except ValueError:
            conf_level = 0.95
        return_value, out_file_name = fit_from_csv(filename, conf_level)
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Saved file.')
        msgBox.setStandardButtons(QtGui.QMessageBox.Close)
        msgBox.setText('Saved: ' + os.path.dirname(filename) + '/' + out_file_name)
        msgBox.setWindowModality(QtCore.Qt.WindowModal)
        msgBox.exec_()

main_form = MainForm()
main_form.show()
width = main_form.childrenRect().width()
height = main_form.childrenRect().height()
main_form.setFixedSize(width, height)
# show the main widget, enter 'main loop'

# exit 'main loop'
sys.exit(app.exec_())