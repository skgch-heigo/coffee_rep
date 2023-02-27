import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlRelationalTableModel, QSqlRelation, QSqlQuery
from PyQt5.QtWidgets import QApplication, QInputDialog, QDialog, QStatusBar, QTableWidget
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

import addEditCoffeeForm
import main


class Dial(QDialog, addEditCoffeeForm.Ui_Dialog):
    def __init__(self, *args):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.run)
        if args:
            for i in range(len(args)):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(args[i])))

    def run(self):
        self.answers = []
        for i in range(6):
            self.answers.append(self.tableWidget.item(i, 0).text())
        self.accept()


class Example(QMainWindow, main.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(self.add)
        self.pushButton_2.clicked.connect(self.change)
        self.con = sqlite3.connect("data/coffee.db")
        self.cur = self.con.cursor()
        self.upd()

    def upd(self):
        self.tableWidget.clear()
        res = self.con.cursor().execute("""SELECT * FROM coffee""").fetchall()
        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "name", "roast", "type", "flavour", "cost", "volume"])
        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def add(self):
        dial = Dial(*[""] * 6)
        if dial.exec_():
            self.con.cursor().execute(f"""INSERT INTO coffee(name, roast, type, flavour, cost, volume) VALUES({
            ", ".join(["'" + str(x) + "'" for x in dial.answers])
            })""")
            self.con.commit()
            self.upd()

    def change(self):
        if self.tableWidget.selectedItems():
            first = self.tableWidget.selectedItems()[0].row()
            data = []
            ind = self.tableWidget.item(first, 0).text()
            for i in range(1, 7):
                data.append(self.tableWidget.item(first, i).text())
            dial = Dial(*data)
            if dial.exec_():
                self.con.cursor().execute(f"""UPDATE coffee
SET name = '{dial.answers[0]}',
roast = "{dial.answers[1]}",
type = "{dial.answers[2]}", 
flavour = "{dial.answers[3]}", 
cost = "{dial.answers[4]}", 
volume = "{dial.answers[5]}"
WHERE ID = {ind}""")
                self.con.commit()
                self.upd()

    def closeEvent(self, event):
        self.con.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
