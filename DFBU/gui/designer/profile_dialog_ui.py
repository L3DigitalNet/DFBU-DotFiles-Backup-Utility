# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'profile_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_ProfileDialog(object):
    def setupUi(self, ProfileDialog):
        if not ProfileDialog.objectName():
            ProfileDialog.setObjectName(u"ProfileDialog")
        ProfileDialog.resize(500, 400)
        ProfileDialog.setModal(True)
        self.mainLayout = QVBoxLayout(ProfileDialog)
        self.mainLayout.setObjectName(u"mainLayout")
        self.profileList = QListWidget(ProfileDialog)
        self.profileList.setObjectName(u"profileList")

        self.mainLayout.addWidget(self.profileList)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.btnNewProfile = QPushButton(ProfileDialog)
        self.btnNewProfile.setObjectName(u"btnNewProfile")

        self.buttonLayout.addWidget(self.btnNewProfile)

        self.btnEditProfile = QPushButton(ProfileDialog)
        self.btnEditProfile.setObjectName(u"btnEditProfile")
        self.btnEditProfile.setEnabled(False)

        self.buttonLayout.addWidget(self.btnEditProfile)

        self.btnDeleteProfile = QPushButton(ProfileDialog)
        self.btnDeleteProfile.setObjectName(u"btnDeleteProfile")
        self.btnDeleteProfile.setEnabled(False)

        self.buttonLayout.addWidget(self.btnDeleteProfile)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.horizontalSpacer)


        self.mainLayout.addLayout(self.buttonLayout)

        self.buttonBox = QDialogButtonBox(ProfileDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(ProfileDialog)

        QMetaObject.connectSlotsByName(ProfileDialog)
    # setupUi

    def retranslateUi(self, ProfileDialog):
        ProfileDialog.setWindowTitle(QCoreApplication.translate("ProfileDialog", u"Manage Backup Profiles", None))
        self.btnNewProfile.setText(QCoreApplication.translate("ProfileDialog", u"New Profile", None))
        self.btnEditProfile.setText(QCoreApplication.translate("ProfileDialog", u"Edit", None))
        self.btnDeleteProfile.setText(QCoreApplication.translate("ProfileDialog", u"Delete", None))
    # retranslateUi

