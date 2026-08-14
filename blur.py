import sys
import os
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QMetaObject, Slot
from PySide6.QtGui import QCursor, QIcon, QColor
from BlurWindow.blurWindow import GlobalBlur
from qfluentwidgets import (FluentIcon, RoundMenu, isDarkTheme, Action, MessageBoxBase, Theme, setTheme, ColorDialog,
                            SubtitleLabel, LineEdit, CaptionLabel, AvatarWidget, HyperlinkButton, BodyLabel, setFont)
import pystray
from PIL import Image
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayItem
import keyboard
import win32gui
import win32con


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


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
        self.setWindowIcon(QIcon(resource_path("blur_ico.ico")))
        self.setWindowTitle("\0")

        self.is_acrylic = False
        GlobalBlur(self.winId(),Dark=isDarkTheme(),Acrylic=self.is_acrylic,QWidget=self)

        self.color_overlay = QWidget(self)
        self.color_overlay.setGeometry(self.rect())
        self.color_overlay.setStyleSheet("background-color: transparent")
        self.color_overlay.lower()

        self.init_context_menu()
        self.init_tray()
        self.init_hotkey()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda: self.tray_menu.exec(QCursor.pos()))

    def init_context_menu(self):
        self.tray_menu = RoundMenu("一块模糊", parent=self)
        card = ProfileCard(resource_path('blur_ico.png'), '一块模糊', 'A-Blur v0.3', self.tray_menu)

        self.mode_action = Action("当前模式：亚克力", self)
        self.mode_action.triggered.connect(self.change_blur_mode)

        self.top_action = Action(FluentIcon.PIN, "置顶")
        self.top_action.triggered.connect(self.showInTop)

        self.win_action = Action(FluentIcon.MORE, "隐藏窗口按钮")
        self.win_action.triggered.connect(self.change_window_buttons_hint)

        self.title_action = Action(FluentIcon.FONT, "自定义窗口标题")
        self.title_action.triggered.connect(self.show_input_dialog)

        self.color_action = Action(FluentIcon.PALETTE, "调色盘")
        self.color_action.triggered.connect(self.show_color_dialog)

        self.reset_color_action = Action(FluentIcon.SYNC, "恢复默认颜色")
        self.reset_color_action.triggered.connect(self.reset_color)

        self.quit_action = Action(FluentIcon.CLOSE, "退出")
        self.quit_action.triggered.connect(self.quit_app)

        # self.tray_menu.addSeparator()
        self.tray_menu.addWidget(card, selectable=False)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.top_action)
        self.tray_menu.addAction(self.win_action)
        self.tray_menu.addAction(self.title_action)
        self.tray_menu.addAction(self.color_action)
        self.tray_menu.addAction(self.reset_color_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)

        self.tray_menu.actions()[1].setCheckable(True)

    def init_tray(self):
        try:
            image = Image.open(resource_path("blur_ico.png"))
        except Exception:
            image = Image.new("RGB", (64, 64), (0, 0, 0))
        menu = TrayMenu(
            TrayItem("显示窗口", lambda: self._invoke("show_normal"), default=True),
            TrayItem("我找不到玻璃啦！", lambda: self._invoke("find_blur")),
            TrayItem("隐藏窗口", lambda: self._invoke("hide")),
            TrayMenu.SEPARATOR,
            TrayItem("退出", lambda: self._invoke("quit_app")),
        )
        self.tray = TrayIcon("A-Blur", image, "一块模糊", menu)
        self.tray.run_detached()

    def _invoke(self, method):
        QMetaObject.invokeMethod(self, method, Qt.QueuedConnection)

    @Slot()
    def show_normal(self):
        self.show()
        self.raise_()
        self.activateWindow()

    @Slot()
    def find_blur(self):
        self.show()
        self.showMaximized()
        self.raise_()
        self.activateWindow()

    @Slot()
    def quit_app(self):
        try:
            self.tray.stop()
        except Exception:
            pass
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def show_input_dialog(self):
        w = InputMessageBox(self)
        if w.exec():
            new_title = w.urlLineEdit.text().strip()
            if len(new_title.strip()) == 0:
                self.setWindowTitle("\0")
            else:
                self.setWindowTitle(new_title)

    def show_color_dialog(self):
        dlg = ColorDialog(QColor(255, 255, 255, 90), "选个玻璃色调", self, enableAlpha=True)
        if dlg.exec():
            color = dlg.color
            self.color_overlay.setStyleSheet(
                f"background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"
            )
            self.color_overlay.update()

    def reset_color(self):
        self.color_overlay.setStyleSheet("background-color: transparent")
        self.color_overlay.update()

    def init_hotkey(self):
        keyboard.on_press_key("f9", lambda _e: self._invoke("enable_click_through"))
        keyboard.on_release_key("f9", lambda _e: self._invoke("disable_click_through"))

    @Slot()
    def enable_click_through(self):
        self._prev_topmost = bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
        self.set_click_through(True)
        hwnd = int(self.winId())
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    @Slot()
    def disable_click_through(self):
        self.set_click_through(False)
        if not self._prev_topmost:
            hwnd = int(self.winId())
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def set_click_through(self, on):
        hwnd = int(self.winId())
        ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if on:
            ex |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
        else:
            ex &= ~win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex)
        win32gui.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'color_overlay'):
            self.color_overlay.setGeometry(self.rect())

    def showInTop(self):
        flags = self.windowFlags()
        if flags & Qt.WindowType.WindowStaysOnTopHint:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
            # flags |= Qt.WindowType.WindowCloseButtonHint
            self.top_action.setText("置顶")
        else:
            flags |= Qt.WindowType.WindowStaysOnTopHint
            # flags |= Qt.WindowType.WindowCloseButtonHint
            self.top_action.setText("取消置顶")
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
        else:
            flags |= Qt.WindowType.WindowCloseButtonHint
            flags |= Qt.WindowType.WindowMinimizeButtonHint
            flags |= Qt.WindowType.WindowMinMaxButtonsHint
            self.win_action.setText("隐藏窗口按钮")
        self.setWindowFlags(flags)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    setTheme(Theme.DARK)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
