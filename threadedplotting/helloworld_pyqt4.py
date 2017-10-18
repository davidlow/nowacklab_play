import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QPushButton
app = QApplication(sys.argv)
button = QPushButton("Hello World", None)
button.show()
app.exec_()
