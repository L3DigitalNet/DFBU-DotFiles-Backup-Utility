# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_dotfile_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QCheckBox,
    QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_AddDotfileDialog(object):
    def setupUi(self, AddDotfileDialog):
        if not AddDotfileDialog.objectName():
            AddDotfileDialog.setObjectName(u"AddDotfileDialog")
        AddDotfileDialog.resize(600, 500)
        AddDotfileDialog.setModal(True)
        self.mainLayout = QVBoxLayout(AddDotfileDialog)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(16, 16, 16, 16)
        self.infoLabel = QLabel(AddDotfileDialog)
        self.infoLabel.setObjectName(u"infoLabel")

        self.mainLayout.addWidget(self.infoLabel)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setVerticalSpacing(8)
        self.tagsLabel = QLabel(AddDotfileDialog)
        self.tagsLabel.setObjectName(u"tagsLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.tagsLabel)

        self.tagsEdit = QLineEdit(AddDotfileDialog)
        self.tagsEdit.setObjectName(u"tagsEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.tagsEdit)

        self.applicationLabel = QLabel(AddDotfileDialog)
        self.applicationLabel.setObjectName(u"applicationLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.applicationLabel)

        self.applicationEdit = QLineEdit(AddDotfileDialog)
        self.applicationEdit.setObjectName(u"applicationEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.applicationEdit)

        self.descriptionLabel = QLabel(AddDotfileDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.descriptionLabel)

        self.descriptionEdit = QLineEdit(AddDotfileDialog)
        self.descriptionEdit.setObjectName(u"descriptionEdit")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.descriptionEdit)


        self.mainLayout.addLayout(self.formLayout)

        self.pathsLabel = QLabel(AddDotfileDialog)
        self.pathsLabel.setObjectName(u"pathsLabel")

        self.mainLayout.addWidget(self.pathsLabel)

        self.pathsList = QListWidget(AddDotfileDialog)
        self.pathsList.setObjectName(u"pathsList")
        self.pathsList.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.mainLayout.addWidget(self.pathsList)

        self.pathInputLayout = QHBoxLayout()
        self.pathInputLayout.setObjectName(u"pathInputLayout")
        self.pathInputEdit = QLineEdit(AddDotfileDialog)
        self.pathInputEdit.setObjectName(u"pathInputEdit")

        self.pathInputLayout.addWidget(self.pathInputEdit)

        self.browseBtn = QPushButton(AddDotfileDialog)
        self.browseBtn.setObjectName(u"browseBtn")

        self.pathInputLayout.addWidget(self.browseBtn)

        self.addPathBtn = QPushButton(AddDotfileDialog)
        self.addPathBtn.setObjectName(u"addPathBtn")

        self.pathInputLayout.addWidget(self.addPathBtn)


        self.mainLayout.addLayout(self.pathInputLayout)

        self.removePathBtn = QPushButton(AddDotfileDialog)
        self.removePathBtn.setObjectName(u"removePathBtn")

        self.mainLayout.addWidget(self.removePathBtn)

        self.enabledCheckbox = QCheckBox(AddDotfileDialog)
        self.enabledCheckbox.setObjectName(u"enabledCheckbox")
        self.enabledCheckbox.setChecked(True)

        self.mainLayout.addWidget(self.enabledCheckbox)

        self.buttonTopSpacer = QSpacerItem(0, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.mainLayout.addItem(self.buttonTopSpacer)

        self.buttonBox = QDialogButtonBox(AddDotfileDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.mainLayout.addWidget(self.buttonBox)


        self.retranslateUi(AddDotfileDialog)
        self.buttonBox.accepted.connect(AddDotfileDialog.accept)
        self.buttonBox.rejected.connect(AddDotfileDialog.reject)

        QMetaObject.connectSlotsByName(AddDotfileDialog)
    # setupUi

    def retranslateUi(self, AddDotfileDialog):
        AddDotfileDialog.setWindowTitle(QCoreApplication.translate("AddDotfileDialog", u"Add Dotfile Entry", None))
        self.infoLabel.setText(QCoreApplication.translate("AddDotfileDialog", u"Add a new dotfile entry to the configuration:", None))
        self.tagsLabel.setText(QCoreApplication.translate("AddDotfileDialog", u"Tags:", None))
        self.tagsEdit.setPlaceholderText(QCoreApplication.translate("AddDotfileDialog", u"e.g., shell, terminal, config (comma-separated)", None))
        self.applicationLabel.setText(QCoreApplication.translate("AddDotfileDialog", u"Application:", None))
        self.applicationEdit.setPlaceholderText(QCoreApplication.translate("AddDotfileDialog", u"e.g., Firefox, Bash", None))
        self.descriptionLabel.setText(QCoreApplication.translate("AddDotfileDialog", u"Description:", None))
        self.descriptionEdit.setPlaceholderText(QCoreApplication.translate("AddDotfileDialog", u"Brief description of the configuration", None))
        self.pathsLabel.setText(QCoreApplication.translate("AddDotfileDialog", u"Paths (one or more):", None))
        self.pathInputEdit.setPlaceholderText(QCoreApplication.translate("AddDotfileDialog", u"Enter or browse for path...", None))
        self.browseBtn.setText(QCoreApplication.translate("AddDotfileDialog", u"Browse...", None))
        self.addPathBtn.setText(QCoreApplication.translate("AddDotfileDialog", u"Add Path", None))
        self.removePathBtn.setText(QCoreApplication.translate("AddDotfileDialog", u"Remove Selected Path(s)", None))
        self.enabledCheckbox.setText(QCoreApplication.translate("AddDotfileDialog", u"Enable for backup", None))
    # retranslateUi

