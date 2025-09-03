import sys
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QIcon
from BlurWindow.blurWindow import GlobalBlur
from qfluentwidgets import SystemTrayMenu, isDarkThemeMode, Action, MessageBoxBase, SubtitleLabel, LineEdit, CaptionLabel, QColor

class InputMessageBox(MessageBoxBase):
    """ Input message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('新的窗口标题', self)
        self.urlLineEdit = LineEdit(self)

        self.urlLineEdit.setPlaceholderText('留空可隐藏窗口标题')
        self.urlLineEdit.setClearButtonEnabled(True)

        self.warningLabel = CaptionLabel("窗口标题不规范")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # change the text of button
        self.yesButton.setText('确认')
        self.cancelButton.setText('取消')

        self.widget.setMinimumWidth(350)

        # self.hideYesButton()

    # def validate(self):
    #     """ Rewrite the virtual method """
    #     isValid = self.urlLineEdit.text().lower().startswith("http://")
    #     self.warningLabel.setHidden(isValid)
    #     self.urlLineEdit.setError(not isValid)
    #     return isValid

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(500, 400)
        self.setWindowIcon(QIcon("None.ico"))
        self.setWindowTitle("")
        GlobalBlur(self.winId(),Dark=isDarkThemeMode(),QWidget=self)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        self.init_context_menu()
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda: self.tray_menu.exec(QCursor.pos()))
        
    def init_context_menu(self):
        self.tray_menu = SystemTrayMenu("一块模糊", parent=self)
        self.top_action = Action("置顶", self)
        self.top_action.triggered.connect(self.showInTop)
        
        self.title_action = Action("自定义窗口标题", self)
        self.title_action.triggered.connect(self.show_input_dialog)
        
        self.tray_menu.addAction(self.top_action)
        self.tray_menu.addAction(self.title_action)
        
    def show_input_dialog(self):
        w = InputMessageBox(self)
        if w.exec():
            self.setWindowTitle(w.urlLineEdit.text())
        
    def showInTop(self):
        flags = self.windowFlags()
        if flags & Qt.WindowStaysOnTopHint:
            flags &= ~Qt.WindowStaysOnTopHint
            self.top_action.setText("置顶")
            print("取消置顶")
        else:
            flags |= Qt.WindowStaysOnTopHint
            self.top_action.setText("取消置顶")
            print("置顶")
        self.setWindowFlags(flags)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.setWindowTitle("")
    mw.show()
    sys.exit(app.exec_())