################################################################################
## Form generated from reading UI file 'profile_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_ProfileDialog:
    def setupUi(self, ProfileDialog):
        if not ProfileDialog.objectName():
            ProfileDialog.setObjectName("ProfileDialog")
        ProfileDialog.resize(500, 400)
        ProfileDialog.setModal(True)
        self.mainLayout = QVBoxLayout(ProfileDialog)
        self.mainLayout.setObjectName("mainLayout")
        self.profileList = QListWidget(ProfileDialog)
        self.profileList.setObjectName("profileList")

        self.mainLayout.addWidget(self.profileList)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.btnNewProfile = QPushButton(ProfileDialog)
        self.btnNewProfile.setObjectName("btnNewProfile")

        self.buttonLayout.addWidget(self.btnNewProfile)

        self.btnEditProfile = QPushButton(ProfileDialog)
        self.btnEditProfile.setObjectName("btnEditProfile")
        self.btnEditProfile.setEnabled(False)

        self.buttonLayout.addWidget(self.btnEditProfile)

        self.btnDeleteProfile = QPushButton(ProfileDialog)
        self.btnDeleteProfile.setObjectName("btnDeleteProfile")
        self.btnDeleteProfile.setEnabled(False)

        self.buttonLayout.addWidget(self.btnDeleteProfile)

        self.horizontalSpacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.buttonLayout.addItem(self.horizontalSpacer)

        self.mainLayout.addLayout(self.buttonLayout)

        self.buttonBox = QDialogButtonBox(ProfileDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.mainLayout.addWidget(self.buttonBox)

        self.retranslateUi(ProfileDialog)

        QMetaObject.connectSlotsByName(ProfileDialog)

    # setupUi

    def retranslateUi(self, ProfileDialog):
        ProfileDialog.setWindowTitle(
            QCoreApplication.translate("ProfileDialog", "Manage Backup Profiles", None)
        )
        self.btnNewProfile.setText(
            QCoreApplication.translate("ProfileDialog", "New Profile", None)
        )
        self.btnEditProfile.setText(
            QCoreApplication.translate("ProfileDialog", "Edit", None)
        )
        self.btnDeleteProfile.setText(
            QCoreApplication.translate("ProfileDialog", "Delete", None)
        )

    # retranslateUi
