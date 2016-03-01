__author__ = 'Santiago Salas'
import datetime as dt
import sys
from PySide import QtGui, QtCore

class MainForm(QtGui.QWidget):

    def __init__(self, parent=None):
        #QtGui.QWidget.__init__(self, parent)
        super(MainForm, self).__init__(parent)

        self.table1 = QtGui.QTableWidget(0, 5, self)
        self.table1.setHorizontalHeaderLabels(['0wk', '4wk', '8wk', '13wk', '15wk'])
        self.show_today = QtGui.QPushButton('Show Today', self)
        self.show_today.connect(self.show_today, QtCore.SIGNAL('clicked()'),
                                self.go_to_today)
        self.cal = QtGui.QCalendarWidget(self)
        self.cal.setGridVisible(True)
        self.cal.connect(self.cal, QtCore.SIGNAL('selectionChanged()'),
                         self.show_date)
        self.show_today.setGeometry(10, 10, 60, 35)
        table1_label1 = QtGui.QLabel('Stability dates')
        v_box = QtGui.QVBoxLayout()
        v_box.addStrut(5)
        v_box.addWidget(table1_label1)
        v_box.addWidget(self.cal)
        v_box.addWidget(self.show_today)
        v_box.addWidget(self.table1)
        self.setLayout(v_box)
        self.setGeometry(300, 100, 550, 500)
        self.setFixedWidth(550)
        self.setWindowTitle('Stability dates')
        self.setWindowIcon(QtGui.QIcon('./utils/gnome-clocks_ignorethis.png'))

    def show_date(self):
        year = self.cal.selectedDate().year()
        month = self.cal.selectedDate().month()
        day = self.cal.selectedDate().day()
        date = dt.datetime(year, month, day)
        self.table1.setRowCount(self.table1.rowCount()+1)
        row = self.table1.rowCount()-1
        wk0 = date
        wk4 = date+dt.timedelta(7*4*1)
        wk8 = date+dt.timedelta(7*4*2)
        wk13 = date+dt.timedelta(7*13)
        wk15 = date+dt.timedelta(7*15)
        self.table1.setItem(row, 0, QtGui.QTableWidgetItem(wk0.strftime('%d-%b-%Y')))
        self.table1.setItem(row, 1, QtGui.QTableWidgetItem(wk4.strftime('%d-%b-%Y')))
        self.table1.setItem(row, 2, QtGui.QTableWidgetItem(wk8.strftime('%d-%b-%Y')))
        self.table1.setItem(row, 3, QtGui.QTableWidgetItem(wk13.strftime('%d-%b-%Y')))
        self.table1.setItem(row, 4, QtGui.QTableWidgetItem(wk15.strftime('%d-%b-%Y')))
        self.table1.selectRow(row)

    def go_to_today(self):
        #today = dt.date.today()
        #self.cal.setSelectedDate(QtCore.QDate(today.year, today.month, today.day))
        self.cal.showToday()
app = QtGui.QApplication(sys.argv)
icon = MainForm()
icon.show()

#main loop


# TODO: cygstart -- 'C:\Users\Santiago Salas\Downloads\cygwin-setup-x86_64.exe'
# -K http://cygwinports.org/ports.gpg --no-admin
sys.exit(app.exec_())