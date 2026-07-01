#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

def main():
    app = QApplication(sys.argv)
    view = QWebEngineView()
    view.setHtml('<h1 style="color:blue;">✅ WebEngine funciona correctamente</h1>')
    view.setWindowTitle("Test WebEngine")
    view.resize(600, 400)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()