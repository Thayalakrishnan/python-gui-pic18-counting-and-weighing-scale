from PyQt5.QtGui import QColor, QPalette


""" Provides the Dark Theme """


def ApplicationTheme() -> QPalette:
    palette = QPalette()

    # base
    palette.setColor(QPalette.WindowText, QColor(180, 180, 180))
    palette.setColor(QPalette.Window, QColor(53, 53, 53))

    palette.setColor(QPalette.Light, QColor(180, 180, 180))
    palette.setColor(QPalette.Midlight, QColor(90, 90, 90))
    palette.setColor(QPalette.Dark, QColor(35, 35, 35))

    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(180, 180, 180))

    palette.setColor(QPalette.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))

    palette.setColor(QPalette.Text, QColor(180, 180, 180))
    palette.setColor(QPalette.BrightText, QColor(180, 180, 180))
    palette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))

    palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))

    palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))

    palette.setColor(QPalette.Link, QColor(56, 252, 196))
    palette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))

    # disabled
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

    # app.setPalette(palette)
    return palette


""" Provides the Dark Theme """


def ScatterGraphTheme() -> QPalette:
    palette = QPalette()

    # base
    palette.setColor(QPalette.WindowText, QColor(180, 180, 180))
    palette.setColor(QPalette.Window, QColor(53, 53, 53))

    palette.setColor(QPalette.Light, QColor(180, 180, 180))
    palette.setColor(QPalette.Midlight, QColor(90, 90, 90))
    palette.setColor(QPalette.Dark, QColor(35, 35, 35))

    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(180, 180, 180))

    palette.setColor(QPalette.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))

    palette.setColor(QPalette.Text, QColor(180, 180, 180))
    palette.setColor(QPalette.BrightText, QColor(180, 180, 180))
    palette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))

    palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))

    palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))

    palette.setColor(QPalette.Link, QColor(56, 252, 196))
    palette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))

    # disabled
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

    theme = Q3DTheme()
    theme.setAmbientLightStrength(0.3)
    theme.setBackgroundColor(QColor(QRgb(0x99CA53)))
    theme.setBackgroundEnabled(True)
    theme.setBaseColor(QColor(QRgb(0x209FDF)))
    theme.setColorStyle(Q3DTheme.ColorStyleUniform)
    theme.setFont(QFont("Impact"), 35)
    theme.setGridEnabled(True)
    theme.setGridLineColor(QColor(QRgb(0x99CA53)))
    theme.setHighlightLightStrength(7.0)
    theme.setLabelBackgroundColor(QColor(0xF6, 0xA6, 0x25, 0xA0))
    theme.setLabelBackgroundEnabled(True)
    theme.setLabelBorderEnabled(True)
    theme.setLabelTextColor(QColor(QRgb(0x404044)))
    theme.setLightColor(QColor(QColorConstants.White))
    theme.setLightStrength(6.0)
    theme.setMultiHighlightColor(QColor(QRgb(0x6D5FD5)))
    theme.setSingleHighlightColor(QColor(QRgb(0xF6A625)))
    theme.setWindowColor(QColor(QRgb(0xFFFFFF)))

    # app.setPalette(darkPalette)
    return theme
