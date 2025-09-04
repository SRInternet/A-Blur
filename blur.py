import sys
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QIcon, QColor
from BlurWindow.blurWindow import GlobalBlur
from qfluentwidgets import (FluentIcon, RoundMenu, isDarkTheme, Action, MessageBoxBase, Theme, setTheme,
                            SubtitleLabel, LineEdit, CaptionLabel, AvatarWidget, HyperlinkButton, BodyLabel, setFont)

class ProfileCard(QWidget):
    """ Profile card """

    def __init__(self, avatarPath: str, name: str, email: str, parent=None):
        super().__init__(parent=parent)
        self.avatar = AvatarWidget(avatarPath, self)
        self.nameLabel = BodyLabel(name, self)
        self.emailLabel = CaptionLabel(email, self)
        self.logoutButton = HyperlinkButton(
            'https://github.com/SRInternet/A-Blur', '仓库', self)

        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        self.emailLabel.setStyleSheet('QLabel{color: '+color.name()+'}')

        color = QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)
        self.nameLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(self.logoutButton, 13)

        self.setFixedSize(307, 82)
        self.avatar.setRadius(24)
        self.avatar.move(2, 6)
        self.nameLabel.move(64, 13)
        self.emailLabel.move(64, 32)
        self.logoutButton.move(52, 48)


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
        self.setWindowIcon(QIcon("blur.ico"))
        self.setWindowTitle("\0")
        
        self.is_acrylic = False
        GlobalBlur(self.winId(),Dark=isDarkTheme(),Acrylic=self.is_acrylic,QWidget=self)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        self.init_context_menu()
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda: self.tray_menu.exec(QCursor.pos()))
        
    def init_context_menu(self):
        self.tray_menu = RoundMenu("一块模糊", parent=self)
        card = ProfileCard('blur_ico.png', '一块模糊', 'A-Blur v0.2', self.tray_menu)
        
        self.mode_action = Action("当前模式：亚克力", self)
        self.mode_action.triggered.connect(self.change_blur_mode)
        
        self.top_action = Action(FluentIcon.PIN, "置顶")
        self.top_action.triggered.connect(self.showInTop)
        
        self.win_action = Action(FluentIcon.MORE, "隐藏窗口按钮")
        self.win_action.triggered.connect(self.change_window_buttons_hint)
        
        self.title_action = Action(FluentIcon.FONT, "自定义窗口标题")
        self.title_action.triggered.connect(self.show_input_dialog)
        
        self.quit_action = Action(FluentIcon.CLOSE, "退出")
        self.quit_action.triggered.connect(self.close)
        
        # self.tray_menu.addAction(self.mode_action) 暂时还未完善
        # self.tray_menu.addSeparator()
        self.tray_menu.addWidget(card, selectable=False)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.top_action)
        self.tray_menu.addAction(self.win_action)
        self.tray_menu.addAction(self.title_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)
        
        self.tray_menu.actions()[1].setCheckable(True)
        
    def show_input_dialog(self):
        w = InputMessageBox(self)
        if w.exec():
            new_title = w.urlLineEdit.text().strip()
            if len(new_title.strip()) == 0:
                self.setWindowTitle("\0")
            else:
                self.setWindowTitle(new_title)
        
    def showInTop(self):
        flags = self.windowFlags()
        if flags & Qt.WindowType.WindowStaysOnTopHint:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            # flags |= Qt.WindowType.WindowCloseButtonHint
            self.top_action.setText("置顶")
            print("取消置顶")
        else:
            flags |= Qt.WindowType.WindowStaysOnTopHint
            # flags |= Qt.WindowType.WindowCloseButtonHint
            self.top_action.setText("取消置顶")
            print("置顶")
        self.setWindowFlags(flags)
        self.show()
        
    def change_blur_mode(self):
        if self.is_acrylic:
            self.is_acrylic = False
            self.mode_action.setText("当前模式：亚克力")
        else:
            self.is_acrylic = True
            self.mode_action.setText("当前模式：云母")
            
        GlobalBlur(self.winId(),Dark=isDarkTheme(),Acrylic=self.is_acrylic,QWidget=self)
        
    def change_window_buttons_hint(self):
        flags = self.windowFlags()
        if flags & Qt.WindowType.WindowMinimizeButtonHint:
            flags &= ~Qt.WindowType.WindowCloseButtonHint
            flags &= ~Qt.WindowType.WindowMinimizeButtonHint
            flags &= ~Qt.WindowType.WindowMinMaxButtonsHint
            self.win_action.setText("显示窗口按钮")
            print("隐藏窗口按钮")
        else:  
            flags |= Qt.WindowType.WindowCloseButtonHint
            flags |= Qt.WindowType.WindowMinimizeButtonHint
            flags |= Qt.WindowType.WindowMinMaxButtonsHint
            self.win_action.setText("隐藏窗口按钮")
            print("显示窗口按钮")
        self.setWindowFlags(flags)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    setTheme(Theme.DARK)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())