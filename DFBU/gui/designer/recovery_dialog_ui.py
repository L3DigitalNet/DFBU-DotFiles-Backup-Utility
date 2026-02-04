# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'recovery_dialog.ui'
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

class Ui_RecoveryDialog(object):
    def setupUi(self, RecoveryDialog):
        if not RecoveryDialog.objectName():
            RecoveryDialog.setObjectName(u"RecoveryDialog")
        RecoveryDialog.resize(650, 450)
        RecoveryDialog.setModal(True)
        self.mainLayout = QVBoxLayout(RecoveryDialog)
        self.mainLayout.setSpacing(12)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.titleLabel = QLabel(RecoveryDialog)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.titleLabel.setFont(font)

        self.mainLayout.addWidget(self.titleLabel)

        self.summaryFrame = QFrame(RecoveryDialog)
        self.summaryFrame.setObjectName(u"summaryFrame")
        self.summaryFrame.setFrameShape(QFrame.StyledPanel)
        self.summaryFrame.setFrameShadow(QFrame.Raised)
        self.summaryLayout = QHBoxLayout(self.summaryFrame)
        self.summaryLayout.setObjectName(u"summaryLayout")
        self.successIcon = QLabel(self.summaryFrame)
        self.successIcon.setObjectName(u"successIcon")
        font1 = QFont()
        font1.setPointSize(14)
        self.successIcon.setFont(font1)

        self.summaryLayout.addWidget(self.successIcon)

        self.successCountLabel = QLabel(self.summaryFrame)
        self.successCountLabel.setObjectName(u"successCountLabel")

        self.summaryLayout.addWidget(self.successCountLabel)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.summaryLayout.addItem(self.horizontalSpacer)

        self.failedIcon = QLabel(self.summaryFrame)
        self.failedIcon.setObjectName(u"failedIcon")
        self.failedIcon.setFont(font1)

        self.summaryLayout.addWidget(self.failedIcon)

        self.failedCountLabel = QLabel(self.summaryFrame)
        self.failedCountLabel.setObjectName(u"failedCountLabel")

        self.summaryLayout.addWidget(self.failedCountLabel)

        self.horizontalSpacer2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.summaryLayout.addItem(self.horizontalSpacer2)


        self.mainLayout.addWidget(self.summaryFrame)

        self.failedLabel = QLabel(RecoveryDialog)
        self.failedLabel.setObjectName(u"failedLabel")
        font2 = QFont()
        font2.setBold(True)
        self.failedLabel.setFont(font2)

        self.mainLayout.addWidget(self.failedLabel)

        self.failedItemsTree = QTreeWidget(RecoveryDialog)
        self.failedItemsTree.setObjectName(u"failedItemsTree")
        self.failedItemsTree.setAlternatingRowColors(True)
        self.failedItemsTree.setRootIsDecorated(False)
        self.failedItemsTree.setUniformRowHeights(True)
        self.failedItemsTree.setColumnCount(3)
        self.failedItemsTree.header().setStretchLastSection(True)

        self.mainLayout.addWidget(self.failedItemsTree)

        self.retryInfoLabel = QLabel(RecoveryDialog)
        self.retryInfoLabel.setObjectName(u"retryInfoLabel")
        self.retryInfoLabel.setWordWrap(True)

        self.mainLayout.addWidget(self.retryInfoLabel)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.retryFailedBtn = QPushButton(RecoveryDialog)
        self.retryFailedBtn.setObjectName(u"retryFailedBtn")

        self.buttonLayout.addWidget(self.retryFailedBtn)

        self.continueBtn = QPushButton(RecoveryDialog)
        self.continueBtn.setObjectName(u"continueBtn")

        self.buttonLayout.addWidget(self.continueBtn)

        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.buttonSpacer)

        self.abortBtn = QPushButton(RecoveryDialog)
        self.abortBtn.setObjectName(u"abortBtn")

        self.buttonLayout.addWidget(self.abortBtn)


        self.mainLayout.addLayout(self.buttonLayout)


        self.retranslateUi(RecoveryDialog)

        QMetaObject.connectSlotsByName(RecoveryDialog)
    # setupUi

    def retranslateUi(self, RecoveryDialog):
        RecoveryDialog.setWindowTitle(QCoreApplication.translate("RecoveryDialog", u"Operation Interrupted", None))
        self.titleLabel.setText(QCoreApplication.translate("RecoveryDialog", u"Some files could not be processed", None))
        self.successIcon.setText(QCoreApplication.translate("RecoveryDialog", u"\u2713", None))
        self.successIcon.setStyleSheet(QCoreApplication.translate("RecoveryDialog", u"color: green;", None))
        self.successCountLabel.setText(QCoreApplication.translate("RecoveryDialog", u"0 files backed up successfully", None))
        self.failedIcon.setText(QCoreApplication.translate("RecoveryDialog", u"\u2717", None))
        self.failedIcon.setStyleSheet(QCoreApplication.translate("RecoveryDialog", u"color: red;", None))
        self.failedCountLabel.setText(QCoreApplication.translate("RecoveryDialog", u"0 files failed", None))
        self.failedLabel.setText(QCoreApplication.translate("RecoveryDialog", u"Failed items:", None))
        ___qtreewidgetitem = self.failedItemsTree.headerItem()
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("RecoveryDialog", u"Retry?", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("RecoveryDialog", u"Error", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("RecoveryDialog", u"File", None));
        self.retryInfoLabel.setText(QCoreApplication.translate("RecoveryDialog", u"Items marked \"Yes\" in the Retry column may succeed if you retry.", None))
        self.retryInfoLabel.setStyleSheet(QCoreApplication.translate("RecoveryDialog", u"color: gray; font-style: italic;", None))
        self.retryFailedBtn.setText(QCoreApplication.translate("RecoveryDialog", u"Retry Failed", None))
#if QT_CONFIG(tooltip)
        self.retryFailedBtn.setToolTip(QCoreApplication.translate("RecoveryDialog", u"Retry all items that might succeed on retry", None))
#endif // QT_CONFIG(tooltip)
        self.continueBtn.setText(QCoreApplication.translate("RecoveryDialog", u"Skip & Continue", None))
#if QT_CONFIG(tooltip)
        self.continueBtn.setToolTip(QCoreApplication.translate("RecoveryDialog", u"Skip failed items and continue with the operation", None))
#endif // QT_CONFIG(tooltip)
        self.abortBtn.setText(QCoreApplication.translate("RecoveryDialog", u"Abort", None))
#if QT_CONFIG(tooltip)
        self.abortBtn.setToolTip(QCoreApplication.translate("RecoveryDialog", u"Stop the operation and discard any remaining items", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

