# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'size_warning_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_SizeWarningDialog(object):
    def setupUi(self, SizeWarningDialog):
        if not SizeWarningDialog.objectName():
            SizeWarningDialog.setObjectName(u"SizeWarningDialog")
        SizeWarningDialog.resize(700, 500)
        SizeWarningDialog.setModal(True)
        self.mainLayout = QVBoxLayout(SizeWarningDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.titleLabel = QLabel(SizeWarningDialog)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.titleLabel.setFont(font)

        self.mainLayout.addWidget(self.titleLabel)

        self.summaryFrame = QFrame(SizeWarningDialog)
        self.summaryFrame.setObjectName(u"summaryFrame")
        self.summaryFrame.setFrameShape(QFrame.StyledPanel)
        self.summaryFrame.setFrameShadow(QFrame.Raised)
        self.summaryLayout = QHBoxLayout(self.summaryFrame)
        self.summaryLayout.setObjectName(u"summaryLayout")
        self.totalSizeIcon = QLabel(self.summaryFrame)
        self.totalSizeIcon.setObjectName(u"totalSizeIcon")
        font1 = QFont()
        font1.setPointSize(14)
        self.totalSizeIcon.setFont(font1)

        self.summaryLayout.addWidget(self.totalSizeIcon)

        self.totalSizeLabel = QLabel(self.summaryFrame)
        self.totalSizeLabel.setObjectName(u"totalSizeLabel")
        font2 = QFont()
        font2.setBold(True)
        self.totalSizeLabel.setFont(font2)

        self.summaryLayout.addWidget(self.totalSizeLabel)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.summaryLayout.addItem(self.horizontalSpacer)

        self.fileCountLabel = QLabel(self.summaryFrame)
        self.fileCountLabel.setObjectName(u"fileCountLabel")

        self.summaryLayout.addWidget(self.fileCountLabel)

        self.horizontalSpacer2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.summaryLayout.addItem(self.horizontalSpacer2)


        self.mainLayout.addWidget(self.summaryFrame)

        self.largeItemsLabel = QLabel(SizeWarningDialog)
        self.largeItemsLabel.setObjectName(u"largeItemsLabel")
        self.largeItemsLabel.setFont(font2)

        self.mainLayout.addWidget(self.largeItemsLabel)

        self.largeItemsTree = QTreeWidget(SizeWarningDialog)
        self.largeItemsTree.setObjectName(u"largeItemsTree")
        self.largeItemsTree.setAlternatingRowColors(True)
        self.largeItemsTree.setRootIsDecorated(False)
        self.largeItemsTree.setUniformRowHeights(True)
        self.largeItemsTree.setColumnCount(4)
        self.largeItemsTree.header().setStretchLastSection(True)

        self.mainLayout.addWidget(self.largeItemsTree)

        self.recommendationLabel = QLabel(SizeWarningDialog)
        self.recommendationLabel.setObjectName(u"recommendationLabel")
        self.recommendationLabel.setWordWrap(True)

        self.mainLayout.addWidget(self.recommendationLabel)

        self.criticalWarningLabel = QLabel(SizeWarningDialog)
        self.criticalWarningLabel.setObjectName(u"criticalWarningLabel")
        self.criticalWarningLabel.setWordWrap(True)

        self.mainLayout.addWidget(self.criticalWarningLabel)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.continueBtn = QPushButton(SizeWarningDialog)
        self.continueBtn.setObjectName(u"continueBtn")

        self.buttonLayout.addWidget(self.continueBtn)

        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.cancelBtn = QPushButton(SizeWarningDialog)
        self.cancelBtn.setObjectName(u"cancelBtn")

        self.buttonLayout.addWidget(self.cancelBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(SizeWarningDialog)

        QMetaObject.connectSlotsByName(SizeWarningDialog)
    # setupUi

    def retranslateUi(self, SizeWarningDialog):
        SizeWarningDialog.setWindowTitle(QCoreApplication.translate("SizeWarningDialog", u"Large Files Detected", None))
        self.titleLabel.setText(QCoreApplication.translate("SizeWarningDialog", u"Your backup contains large files", None))
        self.totalSizeIcon.setText(QCoreApplication.translate("SizeWarningDialog", u"\ud83d\udcca", None))
        self.totalSizeLabel.setText(QCoreApplication.translate("SizeWarningDialog", u"Total backup size: 0 MB", None))
        self.fileCountLabel.setText(QCoreApplication.translate("SizeWarningDialog", u"0 files analyzed", None))
        self.largeItemsLabel.setText(QCoreApplication.translate("SizeWarningDialog", u"Large items (above warning threshold):", None))
        ___qtreewidgetitem = self.largeItemsTree.headerItem()
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("SizeWarningDialog", u"Application", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("SizeWarningDialog", u"Path", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("SizeWarningDialog", u"Size", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("SizeWarningDialog", u"Level", None));
        self.recommendationLabel.setText(QCoreApplication.translate("SizeWarningDialog", u"Recommendation: Large files may exceed Git repository size limits. Consider adding exclusion patterns to .dfbuignore.", None))
        self.recommendationLabel.setStyleSheet(QCoreApplication.translate("SizeWarningDialog", u"color: gray; font-style: italic;", None))
        self.criticalWarningLabel.setText("")
        self.criticalWarningLabel.setStyleSheet(QCoreApplication.translate("SizeWarningDialog", u"color: red; font-weight: bold;", None))
        self.continueBtn.setText(QCoreApplication.translate("SizeWarningDialog", u"Continue Anyway", None))
#if QT_CONFIG(tooltip)
        self.continueBtn.setToolTip(QCoreApplication.translate("SizeWarningDialog", u"Proceed with backup including large files", None))
#endif // QT_CONFIG(tooltip)
        self.cancelBtn.setText(QCoreApplication.translate("SizeWarningDialog", u"Cancel", None))
#if QT_CONFIG(tooltip)
        self.cancelBtn.setToolTip(QCoreApplication.translate("SizeWarningDialog", u"Cancel backup and return to main window", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

