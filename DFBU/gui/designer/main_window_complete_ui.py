# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window_complete.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QFormLayout,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QProgressBar, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QStackedWidget, QStatusBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1475, 1100)
        MainWindow.setMinimumSize(QSize(1000, 700))
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionStartBackup = QAction(MainWindow)
        self.actionStartBackup.setObjectName(u"actionStartBackup")
        self.actionStartRestore = QAction(MainWindow)
        self.actionStartRestore.setObjectName(u"actionStartRestore")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionVerifyBackup = QAction(MainWindow)
        self.actionVerifyBackup.setObjectName(u"actionVerifyBackup")
        self.actionUserGuide = QAction(MainWindow)
        self.actionUserGuide.setObjectName(u"actionUserGuide")
        self.central_widget = QWidget(MainWindow)
        self.central_widget.setObjectName(u"central_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.central_widget.sizePolicy().hasHeightForWidth())
        self.central_widget.setSizePolicy(sizePolicy)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_widget = QTabWidget(self.central_widget)
        self.tab_widget.setObjectName(u"tab_widget")
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.backupTab = QWidget()
        self.backupTab.setObjectName(u"backupTab")
        sizePolicy.setHeightForWidth(self.backupTab.sizePolicy().hasHeightForWidth())
        self.backupTab.setSizePolicy(sizePolicy)
        self.backupTabLayout = QVBoxLayout(self.backupTab)
        self.backupTabLayout.setSpacing(8)
        self.backupTabLayout.setContentsMargins(0, 0, 0, 0)
        self.backupTabLayout.setObjectName(u"backupTabLayout")
        self.backupTabLayout.setContentsMargins(12, 12, 12, 12)
        self.backupStackedWidget = QStackedWidget(self.backupTab)
        self.backupStackedWidget.setObjectName(u"backupStackedWidget")
        self.backupEmptyPage = QWidget()
        self.backupEmptyPage.setObjectName(u"backupEmptyPage")
        self.emptyStateLayout = QVBoxLayout(self.backupEmptyPage)
        self.emptyStateLayout.setSpacing(0)
        self.emptyStateLayout.setContentsMargins(0, 0, 0, 0)
        self.emptyStateLayout.setObjectName(u"emptyStateLayout")
        self.emptyTopSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.emptyStateLayout.addItem(self.emptyTopSpacer)

        self.emptyStateIcon = QLabel(self.backupEmptyPage)
        self.emptyStateIcon.setObjectName(u"emptyStateIcon")
        self.emptyStateIcon.setPixmap(QPixmap(u"../resources/icons/dfbu.svg"))
        self.emptyStateIcon.setScaledContents(False)
        self.emptyStateIcon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emptyStateIcon.setMaximumSize(QSize(64, 64))

        self.emptyStateLayout.addWidget(self.emptyStateIcon, 0, Qt.AlignmentFlag.AlignHCenter)

        self.emptyStateTitle = QLabel(self.backupEmptyPage)
        self.emptyStateTitle.setObjectName(u"emptyStateTitle")
        self.emptyStateTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.emptyStateLayout.addWidget(self.emptyStateTitle, 0, Qt.AlignmentFlag.AlignHCenter)

        self.emptyStateDescription = QLabel(self.backupEmptyPage)
        self.emptyStateDescription.setObjectName(u"emptyStateDescription")
        self.emptyStateDescription.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.emptyStateLayout.addWidget(self.emptyStateDescription, 0, Qt.AlignmentFlag.AlignHCenter)

        self.emptyStateAddButton = QPushButton(self.backupEmptyPage)
        self.emptyStateAddButton.setObjectName(u"emptyStateAddButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.emptyStateAddButton.sizePolicy().hasHeightForWidth())
        self.emptyStateAddButton.setSizePolicy(sizePolicy1)

        self.emptyStateLayout.addWidget(self.emptyStateAddButton, 0, Qt.AlignmentFlag.AlignHCenter)

        self.emptyBottomSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.emptyStateLayout.addItem(self.emptyBottomSpacer)

        self.backupStackedWidget.addWidget(self.backupEmptyPage)
        self.backupContentPage = QWidget()
        self.backupContentPage.setObjectName(u"backupContentPage")
        self.backupContentLayout = QVBoxLayout(self.backupContentPage)
        self.backupContentLayout.setSpacing(8)
        self.backupContentLayout.setContentsMargins(0, 0, 0, 0)
        self.backupContentLayout.setObjectName(u"backupContentLayout")
        self.backupContentLayout.setContentsMargins(0, 0, 0, 0)
        self.backupToolbarLayout = QHBoxLayout()
        self.backupToolbarLayout.setSpacing(8)
        self.backupToolbarLayout.setObjectName(u"backupToolbarLayout")
        self.filterLineEdit = QLineEdit(self.backupContentPage)
        self.filterLineEdit.setObjectName(u"filterLineEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.filterLineEdit.sizePolicy().hasHeightForWidth())
        self.filterLineEdit.setSizePolicy(sizePolicy2)
        self.filterLineEdit.setClearButtonEnabled(True)

        self.backupToolbarLayout.addWidget(self.filterLineEdit)

        self.fileGroupAddFileButton = QPushButton(self.backupContentPage)
        self.fileGroupAddFileButton.setObjectName(u"fileGroupAddFileButton")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.fileGroupAddFileButton.sizePolicy().hasHeightForWidth())
        self.fileGroupAddFileButton.setSizePolicy(sizePolicy3)

        self.backupToolbarLayout.addWidget(self.fileGroupAddFileButton)


        self.backupContentLayout.addLayout(self.backupToolbarLayout)

        self.fileGroupFileTable = QTableWidget(self.backupContentPage)
        if (self.fileGroupFileTable.columnCount() < 6):
            self.fileGroupFileTable.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.fileGroupFileTable.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.fileGroupFileTable.setObjectName(u"fileGroupFileTable")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.fileGroupFileTable.sizePolicy().hasHeightForWidth())
        self.fileGroupFileTable.setSizePolicy(sizePolicy4)
        self.fileGroupFileTable.setDragEnabled(True)
        self.fileGroupFileTable.setAlternatingRowColors(True)
        self.fileGroupFileTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.fileGroupFileTable.setSortingEnabled(True)

        self.backupContentLayout.addWidget(self.fileGroupFileTable)

        self.backupActionBarLayout = QHBoxLayout()
        self.backupActionBarLayout.setSpacing(8)
        self.backupActionBarLayout.setObjectName(u"backupActionBarLayout")
        self.fileGroupUpdateFileButton = QPushButton(self.backupContentPage)
        self.fileGroupUpdateFileButton.setObjectName(u"fileGroupUpdateFileButton")
        self.fileGroupUpdateFileButton.setEnabled(False)

        self.backupActionBarLayout.addWidget(self.fileGroupUpdateFileButton)

        self.fileGroupRemoveFileButton = QPushButton(self.backupContentPage)
        self.fileGroupRemoveFileButton.setObjectName(u"fileGroupRemoveFileButton")
        self.fileGroupRemoveFileButton.setEnabled(False)

        self.backupActionBarLayout.addWidget(self.fileGroupRemoveFileButton)

        self.fileGroupToggleEnabledButton = QPushButton(self.backupContentPage)
        self.fileGroupToggleEnabledButton.setObjectName(u"fileGroupToggleEnabledButton")
        self.fileGroupToggleEnabledButton.setEnabled(False)

        self.backupActionBarLayout.addWidget(self.fileGroupToggleEnabledButton)

        self.fileGroupSaveFilesButton = QPushButton(self.backupContentPage)
        self.fileGroupSaveFilesButton.setObjectName(u"fileGroupSaveFilesButton")
        self.fileGroupSaveFilesButton.setEnabled(False)

        self.backupActionBarLayout.addWidget(self.fileGroupSaveFilesButton)

        self.actionBarSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.backupActionBarLayout.addItem(self.actionBarSpacer)

        self.fileGroupTotalSizeLabel = QLabel(self.backupContentPage)
        self.fileGroupTotalSizeLabel.setObjectName(u"fileGroupTotalSizeLabel")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.fileGroupTotalSizeLabel.sizePolicy().hasHeightForWidth())
        self.fileGroupTotalSizeLabel.setSizePolicy(sizePolicy5)

        self.backupActionBarLayout.addWidget(self.fileGroupTotalSizeLabel)


        self.backupContentLayout.addLayout(self.backupActionBarLayout)

        self.backupStackedWidget.addWidget(self.backupContentPage)

        self.backupTabLayout.addWidget(self.backupStackedWidget)

        self.backupOptionsStripLayout = QHBoxLayout()
        self.backupOptionsStripLayout.setSpacing(12)
        self.backupOptionsStripLayout.setObjectName(u"backupOptionsStripLayout")
        self.backupOptionsLabel = QLabel(self.backupTab)
        self.backupOptionsLabel.setObjectName(u"backupOptionsLabel")
        sizePolicy1.setHeightForWidth(self.backupOptionsLabel.sizePolicy().hasHeightForWidth())
        self.backupOptionsLabel.setSizePolicy(sizePolicy1)

        self.backupOptionsStripLayout.addWidget(self.backupOptionsLabel)

        self.mirrorCheckbox = QCheckBox(self.backupTab)
        self.mirrorCheckbox.setObjectName(u"mirrorCheckbox")
        sizePolicy1.setHeightForWidth(self.mirrorCheckbox.sizePolicy().hasHeightForWidth())
        self.mirrorCheckbox.setSizePolicy(sizePolicy1)
        self.mirrorCheckbox.setChecked(True)

        self.backupOptionsStripLayout.addWidget(self.mirrorCheckbox)

        self.archiveCheckbox = QCheckBox(self.backupTab)
        self.archiveCheckbox.setObjectName(u"archiveCheckbox")
        sizePolicy1.setHeightForWidth(self.archiveCheckbox.sizePolicy().hasHeightForWidth())
        self.archiveCheckbox.setSizePolicy(sizePolicy1)

        self.backupOptionsStripLayout.addWidget(self.archiveCheckbox)

        self.forceBackupCheckbox = QCheckBox(self.backupTab)
        self.forceBackupCheckbox.setObjectName(u"forceBackupCheckbox")
        sizePolicy1.setHeightForWidth(self.forceBackupCheckbox.sizePolicy().hasHeightForWidth())
        self.forceBackupCheckbox.setSizePolicy(sizePolicy1)
        self.forceBackupCheckbox.setChecked(False)

        self.backupOptionsStripLayout.addWidget(self.forceBackupCheckbox)

        self.optionsStripSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.backupOptionsStripLayout.addItem(self.optionsStripSpacer)

        self.startBackupButton = QPushButton(self.backupTab)
        self.startBackupButton.setObjectName(u"startBackupButton")
        self.startBackupButton.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.startBackupButton.sizePolicy().hasHeightForWidth())
        self.startBackupButton.setSizePolicy(sizePolicy1)

        self.backupOptionsStripLayout.addWidget(self.startBackupButton)


        self.backupTabLayout.addLayout(self.backupOptionsStripLayout)

        self.tab_widget.addTab(self.backupTab, "")
        self.restoreTab = QWidget()
        self.restoreTab.setObjectName(u"restoreTab")
        sizePolicy.setHeightForWidth(self.restoreTab.sizePolicy().hasHeightForWidth())
        self.restoreTab.setSizePolicy(sizePolicy)
        self.restore_layout = QVBoxLayout(self.restoreTab)
        self.restore_layout.setSpacing(0)
        self.restore_layout.setContentsMargins(0, 0, 0, 0)
        self.restore_layout.setObjectName(u"restore_layout")
        self.restore_layout.setContentsMargins(12, 12, 12, 12)
        self.restoreSourceGroup = QWidget(self.restoreTab)
        self.restoreSourceGroup.setObjectName(u"restoreSourceGroup")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.restoreSourceGroup.sizePolicy().hasHeightForWidth())
        self.restoreSourceGroup.setSizePolicy(sizePolicy6)
        self.restore_source_layout = QVBoxLayout(self.restoreSourceGroup)
        self.restore_source_layout.setSpacing(6)
        self.restore_source_layout.setContentsMargins(0, 0, 0, 0)
        self.restore_source_layout.setObjectName(u"restore_source_layout")
        self.restore_source_layout.setContentsMargins(6, 0, 6, 6)
        self.restoreSourceLabelContainer = QWidget(self.restoreSourceGroup)
        self.restoreSourceLabelContainer.setObjectName(u"restoreSourceLabelContainer")
        sizePolicy6.setHeightForWidth(self.restoreSourceLabelContainer.sizePolicy().hasHeightForWidth())
        self.restoreSourceLabelContainer.setSizePolicy(sizePolicy6)
        self.restoreSourceLabelLayout = QHBoxLayout(self.restoreSourceLabelContainer)
        self.restoreSourceLabelLayout.setSpacing(0)
        self.restoreSourceLabelLayout.setContentsMargins(0, 0, 0, 0)
        self.restoreSourceLabelLayout.setObjectName(u"restoreSourceLabelLayout")
        self.restoreSourceLabelLayout.setContentsMargins(-1, -1, -1, 0)
        self.restoreSourceLabel = QLabel(self.restoreSourceLabelContainer)
        self.restoreSourceLabel.setObjectName(u"restoreSourceLabel")
        sizePolicy6.setHeightForWidth(self.restoreSourceLabel.sizePolicy().hasHeightForWidth())
        self.restoreSourceLabel.setSizePolicy(sizePolicy6)
        self.restoreSourceLabel.setMargin(6)

        self.restoreSourceLabelLayout.addWidget(self.restoreSourceLabel)


        self.restore_source_layout.addWidget(self.restoreSourceLabelContainer)

        self.restoreSourceLine = QFrame(self.restoreSourceGroup)
        self.restoreSourceLine.setObjectName(u"restoreSourceLine")
        sizePolicy6.setHeightForWidth(self.restoreSourceLine.sizePolicy().hasHeightForWidth())
        self.restoreSourceLine.setSizePolicy(sizePolicy6)
        self.restoreSourceLine.setFrameShape(QFrame.Shape.HLine)
        self.restoreSourceLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.restore_source_layout.addWidget(self.restoreSourceLine)

        self.restoreSourceInfoButtonContainer = QWidget(self.restoreSourceGroup)
        self.restoreSourceInfoButtonContainer.setObjectName(u"restoreSourceInfoButtonContainer")
        sizePolicy6.setHeightForWidth(self.restoreSourceInfoButtonContainer.sizePolicy().hasHeightForWidth())
        self.restoreSourceInfoButtonContainer.setSizePolicy(sizePolicy6)
        self.restoreSourceInfoButtonLayout = QHBoxLayout(self.restoreSourceInfoButtonContainer)
        self.restoreSourceInfoButtonLayout.setSpacing(6)
        self.restoreSourceInfoButtonLayout.setContentsMargins(0, 0, 0, 0)
        self.restoreSourceInfoButtonLayout.setObjectName(u"restoreSourceInfoButtonLayout")
        self.restoreSourceInfoButtonLayout.setContentsMargins(6, 0, 0, 0)
        self.restoreSourceInfoLabel = QLabel(self.restoreSourceInfoButtonContainer)
        self.restoreSourceInfoLabel.setObjectName(u"restoreSourceInfoLabel")
        sizePolicy6.setHeightForWidth(self.restoreSourceInfoLabel.sizePolicy().hasHeightForWidth())
        self.restoreSourceInfoLabel.setSizePolicy(sizePolicy6)
        self.restoreSourceInfoLabel.setWordWrap(True)
        self.restoreSourceInfoLabel.setMargin(5)

        self.restoreSourceInfoButtonLayout.addWidget(self.restoreSourceInfoLabel)

        self.restoreSourceInfoButtonLine = QFrame(self.restoreSourceInfoButtonContainer)
        self.restoreSourceInfoButtonLine.setObjectName(u"restoreSourceInfoButtonLine")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.restoreSourceInfoButtonLine.sizePolicy().hasHeightForWidth())
        self.restoreSourceInfoButtonLine.setSizePolicy(sizePolicy7)
        self.restoreSourceInfoButtonLine.setMinimumSize(QSize(0, 50))
        self.restoreSourceInfoButtonLine.setFrameShape(QFrame.Shape.VLine)
        self.restoreSourceInfoButtonLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.restoreSourceInfoButtonLayout.addWidget(self.restoreSourceInfoButtonLine, 0, Qt.AlignmentFlag.AlignHCenter)

        self.restoreSourceButton = QPushButton(self.restoreSourceInfoButtonContainer)
        self.restoreSourceButton.setObjectName(u"restoreSourceButton")
        self.restoreSourceButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.restoreSourceButton.sizePolicy().hasHeightForWidth())
        self.restoreSourceButton.setSizePolicy(sizePolicy6)
        self.restoreSourceButton.setMinimumSize(QSize(0, 0))

        self.restoreSourceInfoButtonLayout.addWidget(self.restoreSourceButton, 0, Qt.AlignmentFlag.AlignLeft)

        self.restoreSourceInfoButtonLayout.setStretch(0, 20)
        self.restoreSourceInfoButtonLayout.setStretch(1, 1)
        self.restoreSourceInfoButtonLayout.setStretch(2, 20)

        self.restore_source_layout.addWidget(self.restoreSourceInfoButtonContainer)

        self.restorePathLayout = QHBoxLayout()
        self.restorePathLayout.setSpacing(0)
        self.restorePathLayout.setObjectName(u"restorePathLayout")
        self.restoreSourceEdit = QLineEdit(self.restoreSourceGroup)
        self.restoreSourceEdit.setObjectName(u"restoreSourceEdit")
        sizePolicy6.setHeightForWidth(self.restoreSourceEdit.sizePolicy().hasHeightForWidth())
        self.restoreSourceEdit.setSizePolicy(sizePolicy6)
        self.restoreSourceEdit.setFrame(True)
        self.restoreSourceEdit.setReadOnly(True)
        self.restoreSourceEdit.setClearButtonEnabled(False)

        self.restorePathLayout.addWidget(self.restoreSourceEdit)

        self.restoreSourceBrowseButton = QPushButton(self.restoreSourceGroup)
        self.restoreSourceBrowseButton.setObjectName(u"restoreSourceBrowseButton")
        sizePolicy1.setHeightForWidth(self.restoreSourceBrowseButton.sizePolicy().hasHeightForWidth())
        self.restoreSourceBrowseButton.setSizePolicy(sizePolicy1)

        self.restorePathLayout.addWidget(self.restoreSourceBrowseButton)


        self.restore_source_layout.addLayout(self.restorePathLayout)

        self.restoreSourceButtonLayout = QHBoxLayout()
        self.restoreSourceButtonLayout.setSpacing(0)
        self.restoreSourceButtonLayout.setObjectName(u"restoreSourceButtonLayout")

        self.restore_source_layout.addLayout(self.restoreSourceButtonLayout)


        self.restore_layout.addWidget(self.restoreSourceGroup)

        self.restorePreviewGroup = QGroupBox(self.restoreTab)
        self.restorePreviewGroup.setObjectName(u"restorePreviewGroup")
        self.restorePreviewGroup.setVisible(False)
        self.restorePreviewLayout = QVBoxLayout(self.restorePreviewGroup)
        self.restorePreviewLayout.setSpacing(0)
        self.restorePreviewLayout.setContentsMargins(0, 0, 0, 0)
        self.restorePreviewLayout.setObjectName(u"restorePreviewLayout")
        self.restorePreviewLayout.setContentsMargins(12, 12, 12, 12)
        self.restorePreviewSummaryLayout = QHBoxLayout()
        self.restorePreviewSummaryLayout.setSpacing(0)
        self.restorePreviewSummaryLayout.setObjectName(u"restorePreviewSummaryLayout")
        self.restorePreviewHostLabel = QLabel(self.restorePreviewGroup)
        self.restorePreviewHostLabel.setObjectName(u"restorePreviewHostLabel")

        self.restorePreviewSummaryLayout.addWidget(self.restorePreviewHostLabel)

        self.restorePreviewCountLabel = QLabel(self.restorePreviewGroup)
        self.restorePreviewCountLabel.setObjectName(u"restorePreviewCountLabel")

        self.restorePreviewSummaryLayout.addWidget(self.restorePreviewCountLabel)

        self.restorePreviewSizeLabel = QLabel(self.restorePreviewGroup)
        self.restorePreviewSizeLabel.setObjectName(u"restorePreviewSizeLabel")

        self.restorePreviewSummaryLayout.addWidget(self.restorePreviewSizeLabel)

        self.restorePreviewSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.restorePreviewSummaryLayout.addItem(self.restorePreviewSpacer)


        self.restorePreviewLayout.addLayout(self.restorePreviewSummaryLayout)

        self.restorePreviewTree = QTreeWidget(self.restorePreviewGroup)
        self.restorePreviewTree.setObjectName(u"restorePreviewTree")
        self.restorePreviewTree.setMinimumSize(QSize(0, 150))
        self.restorePreviewTree.setAlternatingRowColors(True)
        self.restorePreviewTree.setRootIsDecorated(True)

        self.restorePreviewLayout.addWidget(self.restorePreviewTree)


        self.restore_layout.addWidget(self.restorePreviewGroup)

        self.restoreInfoGroup = QWidget(self.restoreTab)
        self.restoreInfoGroup.setObjectName(u"restoreInfoGroup")
        sizePolicy.setHeightForWidth(self.restoreInfoGroup.sizePolicy().hasHeightForWidth())
        self.restoreInfoGroup.setSizePolicy(sizePolicy)
        self.restore_info_layout = QVBoxLayout(self.restoreInfoGroup)
        self.restore_info_layout.setSpacing(6)
        self.restore_info_layout.setContentsMargins(0, 0, 0, 0)
        self.restore_info_layout.setObjectName(u"restore_info_layout")
        self.restore_info_layout.setContentsMargins(-1, -1, 0, 0)
        self.restoreInfoLabel = QLabel(self.restoreInfoGroup)
        self.restoreInfoLabel.setObjectName(u"restoreInfoLabel")
        sizePolicy6.setHeightForWidth(self.restoreInfoLabel.sizePolicy().hasHeightForWidth())
        self.restoreInfoLabel.setSizePolicy(sizePolicy6)
        font = QFont()
        font.setBold(False)
        self.restoreInfoLabel.setFont(font)
        self.restoreInfoLabel.setMargin(6)

        self.restore_info_layout.addWidget(self.restoreInfoLabel)

        self.restoreInfoLine = QFrame(self.restoreInfoGroup)
        self.restoreInfoLine.setObjectName(u"restoreInfoLine")
        sizePolicy6.setHeightForWidth(self.restoreInfoLine.sizePolicy().hasHeightForWidth())
        self.restoreInfoLine.setSizePolicy(sizePolicy6)
        self.restoreInfoLine.setFrameShape(QFrame.Shape.HLine)
        self.restoreInfoLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.restore_info_layout.addWidget(self.restoreInfoLine)

        self.restoreInfoText = QLabel(self.restoreInfoGroup)
        self.restoreInfoText.setObjectName(u"restoreInfoText")
        sizePolicy1.setHeightForWidth(self.restoreInfoText.sizePolicy().hasHeightForWidth())
        self.restoreInfoText.setSizePolicy(sizePolicy1)
        self.restoreInfoText.setWordWrap(True)
        self.restoreInfoText.setMargin(10)
        self.restoreInfoText.setIndent(-1)

        self.restore_info_layout.addWidget(self.restoreInfoText, 0, Qt.AlignmentFlag.AlignTop)


        self.restore_layout.addWidget(self.restoreInfoGroup)

        self.tab_widget.addTab(self.restoreTab, "")
        self.configTab = QWidget()
        self.configTab.setObjectName(u"configTab")
        sizePolicy.setHeightForWidth(self.configTab.sizePolicy().hasHeightForWidth())
        self.configTab.setSizePolicy(sizePolicy)
        self.config_tab_layout = QVBoxLayout(self.configTab)
        self.config_tab_layout.setSpacing(8)
        self.config_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.config_tab_layout.setObjectName(u"config_tab_layout")
        self.config_tab_layout.setContentsMargins(12, 12, 12, 12)
        self.configScrollArea = QScrollArea(self.configTab)
        self.configScrollArea.setObjectName(u"configScrollArea")
        self.configScrollArea.setWidgetResizable(True)
        self.configScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.configScrollContent = QWidget()
        self.configScrollContent.setObjectName(u"configScrollContent")
        self.configScrollLayout = QVBoxLayout(self.configScrollContent)
        self.configScrollLayout.setSpacing(12)
        self.configScrollLayout.setContentsMargins(0, 0, 0, 0)
        self.configScrollLayout.setObjectName(u"configScrollLayout")
        self.backupPathsGroup = QGroupBox(self.configScrollContent)
        self.backupPathsGroup.setObjectName(u"backupPathsGroup")
        self.backupPathsLayout = QFormLayout(self.backupPathsGroup)
        self.backupPathsLayout.setSpacing(0)
        self.backupPathsLayout.setContentsMargins(0, 0, 0, 0)
        self.backupPathsLayout.setObjectName(u"backupPathsLayout")
        self.backupPathsLayout.setHorizontalSpacing(8)
        self.backupPathsLayout.setVerticalSpacing(8)
        self.mirror_path_label = QLabel(self.backupPathsGroup)
        self.mirror_path_label.setObjectName(u"mirror_path_label")

        self.backupPathsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.mirror_path_label)

        self.mirror_path_layout = QHBoxLayout()
        self.mirror_path_layout.setSpacing(0)
        self.mirror_path_layout.setObjectName(u"mirror_path_layout")
        self.config_mirror_path_edit = QLineEdit(self.backupPathsGroup)
        self.config_mirror_path_edit.setObjectName(u"config_mirror_path_edit")

        self.mirror_path_layout.addWidget(self.config_mirror_path_edit)

        self.browse_mirror_btn = QPushButton(self.backupPathsGroup)
        self.browse_mirror_btn.setObjectName(u"browse_mirror_btn")
        sizePolicy1.setHeightForWidth(self.browse_mirror_btn.sizePolicy().hasHeightForWidth())
        self.browse_mirror_btn.setSizePolicy(sizePolicy1)

        self.mirror_path_layout.addWidget(self.browse_mirror_btn)


        self.backupPathsLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.mirror_path_layout)

        self.archivePathLabel = QLabel(self.backupPathsGroup)
        self.archivePathLabel.setObjectName(u"archivePathLabel")

        self.backupPathsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.archivePathLabel)

        self.archivePathLayout = QHBoxLayout()
        self.archivePathLayout.setSpacing(0)
        self.archivePathLayout.setObjectName(u"archivePathLayout")
        self.configArchivePathEdit = QLineEdit(self.backupPathsGroup)
        self.configArchivePathEdit.setObjectName(u"configArchivePathEdit")

        self.archivePathLayout.addWidget(self.configArchivePathEdit)

        self.browseArchiveButton = QPushButton(self.backupPathsGroup)
        self.browseArchiveButton.setObjectName(u"browseArchiveButton")
        sizePolicy1.setHeightForWidth(self.browseArchiveButton.sizePolicy().hasHeightForWidth())
        self.browseArchiveButton.setSizePolicy(sizePolicy1)

        self.archivePathLayout.addWidget(self.browseArchiveButton)


        self.backupPathsLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.archivePathLayout)


        self.configScrollLayout.addWidget(self.backupPathsGroup)

        self.backupModesGroup = QGroupBox(self.configScrollContent)
        self.backupModesGroup.setObjectName(u"backupModesGroup")
        self.backupModesLayout = QGridLayout(self.backupModesGroup)
        self.backupModesLayout.setSpacing(0)
        self.backupModesLayout.setContentsMargins(0, 0, 0, 0)
        self.backupModesLayout.setObjectName(u"backupModesLayout")
        self.backupModesLayout.setHorizontalSpacing(16)
        self.backupModesLayout.setVerticalSpacing(8)
        self.config_mirror_checkbox = QCheckBox(self.backupModesGroup)
        self.config_mirror_checkbox.setObjectName(u"config_mirror_checkbox")

        self.backupModesLayout.addWidget(self.config_mirror_checkbox, 0, 0, 1, 1)

        self.config_archive_checkbox = QCheckBox(self.backupModesGroup)
        self.config_archive_checkbox.setObjectName(u"config_archive_checkbox")

        self.backupModesLayout.addWidget(self.config_archive_checkbox, 0, 1, 1, 1)

        self.config_hostname_checkbox = QCheckBox(self.backupModesGroup)
        self.config_hostname_checkbox.setObjectName(u"config_hostname_checkbox")

        self.backupModesLayout.addWidget(self.config_hostname_checkbox, 1, 0, 1, 1)

        self.config_date_checkbox = QCheckBox(self.backupModesGroup)
        self.config_date_checkbox.setObjectName(u"config_date_checkbox")

        self.backupModesLayout.addWidget(self.config_date_checkbox, 1, 1, 1, 1)


        self.configScrollLayout.addWidget(self.backupModesGroup)

        self.archiveOptionsGroup = QGroupBox(self.configScrollContent)
        self.archiveOptionsGroup.setObjectName(u"archiveOptionsGroup")
        self.archiveOptionsLayout = QFormLayout(self.archiveOptionsGroup)
        self.archiveOptionsLayout.setSpacing(0)
        self.archiveOptionsLayout.setContentsMargins(0, 0, 0, 0)
        self.archiveOptionsLayout.setObjectName(u"archiveOptionsLayout")
        self.archiveOptionsLayout.setHorizontalSpacing(8)
        self.archiveOptionsLayout.setVerticalSpacing(8)
        self.compressionLabel = QLabel(self.archiveOptionsGroup)
        self.compressionLabel.setObjectName(u"compressionLabel")

        self.archiveOptionsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.compressionLabel)

        self.config_compression_spinbox = QSpinBox(self.archiveOptionsGroup)
        self.config_compression_spinbox.setObjectName(u"config_compression_spinbox")
        sizePolicy1.setHeightForWidth(self.config_compression_spinbox.sizePolicy().hasHeightForWidth())
        self.config_compression_spinbox.setSizePolicy(sizePolicy1)
        self.config_compression_spinbox.setMinimum(0)
        self.config_compression_spinbox.setMaximum(9)

        self.archiveOptionsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.config_compression_spinbox)

        self.rotate_label = QLabel(self.archiveOptionsGroup)
        self.rotate_label.setObjectName(u"rotate_label")

        self.archiveOptionsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.rotate_label)

        self.config_rotate_checkbox = QCheckBox(self.archiveOptionsGroup)
        self.config_rotate_checkbox.setObjectName(u"config_rotate_checkbox")

        self.archiveOptionsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.config_rotate_checkbox)

        self.max_archives_label = QLabel(self.archiveOptionsGroup)
        self.max_archives_label.setObjectName(u"max_archives_label")

        self.archiveOptionsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.max_archives_label)

        self.config_max_archives_spinbox = QSpinBox(self.archiveOptionsGroup)
        self.config_max_archives_spinbox.setObjectName(u"config_max_archives_spinbox")
        sizePolicy1.setHeightForWidth(self.config_max_archives_spinbox.sizePolicy().hasHeightForWidth())
        self.config_max_archives_spinbox.setSizePolicy(sizePolicy1)
        self.config_max_archives_spinbox.setMinimum(1)
        self.config_max_archives_spinbox.setMaximum(100)

        self.archiveOptionsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.config_max_archives_spinbox)


        self.configScrollLayout.addWidget(self.archiveOptionsGroup)

        self.preRestoreSafetyGroup = QGroupBox(self.configScrollContent)
        self.preRestoreSafetyGroup.setObjectName(u"preRestoreSafetyGroup")
        self.preRestoreSafetyLayout = QFormLayout(self.preRestoreSafetyGroup)
        self.preRestoreSafetyLayout.setSpacing(0)
        self.preRestoreSafetyLayout.setContentsMargins(0, 0, 0, 0)
        self.preRestoreSafetyLayout.setObjectName(u"preRestoreSafetyLayout")
        self.preRestoreSafetyLayout.setHorizontalSpacing(8)
        self.preRestoreSafetyLayout.setVerticalSpacing(8)
        self.config_pre_restore_checkbox = QCheckBox(self.preRestoreSafetyGroup)
        self.config_pre_restore_checkbox.setObjectName(u"config_pre_restore_checkbox")

        self.preRestoreSafetyLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.config_pre_restore_checkbox)

        self.maxRestoreBackupsLabel = QLabel(self.preRestoreSafetyGroup)
        self.maxRestoreBackupsLabel.setObjectName(u"maxRestoreBackupsLabel")

        self.preRestoreSafetyLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.maxRestoreBackupsLabel)

        self.config_max_restore_spinbox = QSpinBox(self.preRestoreSafetyGroup)
        self.config_max_restore_spinbox.setObjectName(u"config_max_restore_spinbox")
        sizePolicy1.setHeightForWidth(self.config_max_restore_spinbox.sizePolicy().hasHeightForWidth())
        self.config_max_restore_spinbox.setSizePolicy(sizePolicy1)
        self.config_max_restore_spinbox.setMinimum(1)
        self.config_max_restore_spinbox.setMaximum(100)
        self.config_max_restore_spinbox.setValue(5)

        self.preRestoreSafetyLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.config_max_restore_spinbox)

        self.restoreBackupDirLabel = QLabel(self.preRestoreSafetyGroup)
        self.restoreBackupDirLabel.setObjectName(u"restoreBackupDirLabel")

        self.preRestoreSafetyLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.restoreBackupDirLabel)

        self.restoreBackupDirLayout = QHBoxLayout()
        self.restoreBackupDirLayout.setSpacing(0)
        self.restoreBackupDirLayout.setObjectName(u"restoreBackupDirLayout")
        self.config_restore_path_edit = QLineEdit(self.preRestoreSafetyGroup)
        self.config_restore_path_edit.setObjectName(u"config_restore_path_edit")

        self.restoreBackupDirLayout.addWidget(self.config_restore_path_edit)

        self.browse_restore_btn = QPushButton(self.preRestoreSafetyGroup)
        self.browse_restore_btn.setObjectName(u"browse_restore_btn")
        sizePolicy1.setHeightForWidth(self.browse_restore_btn.sizePolicy().hasHeightForWidth())
        self.browse_restore_btn.setSizePolicy(sizePolicy1)

        self.restoreBackupDirLayout.addWidget(self.browse_restore_btn)


        self.preRestoreSafetyLayout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.restoreBackupDirLayout)


        self.configScrollLayout.addWidget(self.preRestoreSafetyGroup)

        self.verificationGroup = QGroupBox(self.configScrollContent)
        self.verificationGroup.setObjectName(u"verificationGroup")
        self.verificationLayout = QVBoxLayout(self.verificationGroup)
        self.verificationLayout.setSpacing(8)
        self.verificationLayout.setContentsMargins(0, 0, 0, 0)
        self.verificationLayout.setObjectName(u"verificationLayout")
        self.config_verify_checkbox = QCheckBox(self.verificationGroup)
        self.config_verify_checkbox.setObjectName(u"config_verify_checkbox")

        self.verificationLayout.addWidget(self.config_verify_checkbox)

        self.config_hash_checkbox = QCheckBox(self.verificationGroup)
        self.config_hash_checkbox.setObjectName(u"config_hash_checkbox")

        self.verificationLayout.addWidget(self.config_hash_checkbox)


        self.configScrollLayout.addWidget(self.verificationGroup)

        self.sizeManagementGroup = QGroupBox(self.configScrollContent)
        self.sizeManagementGroup.setObjectName(u"sizeManagementGroup")
        self.sizeManagementLayout = QFormLayout(self.sizeManagementGroup)
        self.sizeManagementLayout.setSpacing(0)
        self.sizeManagementLayout.setContentsMargins(0, 0, 0, 0)
        self.sizeManagementLayout.setObjectName(u"sizeManagementLayout")
        self.sizeManagementLayout.setHorizontalSpacing(8)
        self.sizeManagementLayout.setVerticalSpacing(8)
        self.config_size_check_checkbox = QCheckBox(self.sizeManagementGroup)
        self.config_size_check_checkbox.setObjectName(u"config_size_check_checkbox")

        self.sizeManagementLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.config_size_check_checkbox)

        self.sizeWarningLabel = QLabel(self.sizeManagementGroup)
        self.sizeWarningLabel.setObjectName(u"sizeWarningLabel")

        self.sizeManagementLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.sizeWarningLabel)

        self.config_size_warning_spinbox = QSpinBox(self.sizeManagementGroup)
        self.config_size_warning_spinbox.setObjectName(u"config_size_warning_spinbox")
        sizePolicy1.setHeightForWidth(self.config_size_warning_spinbox.sizePolicy().hasHeightForWidth())
        self.config_size_warning_spinbox.setSizePolicy(sizePolicy1)
        self.config_size_warning_spinbox.setMinimum(1)
        self.config_size_warning_spinbox.setMaximum(10000)
        self.config_size_warning_spinbox.setValue(10)

        self.sizeManagementLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.config_size_warning_spinbox)

        self.sizeAlertLabel = QLabel(self.sizeManagementGroup)
        self.sizeAlertLabel.setObjectName(u"sizeAlertLabel")

        self.sizeManagementLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.sizeAlertLabel)

        self.config_size_alert_spinbox = QSpinBox(self.sizeManagementGroup)
        self.config_size_alert_spinbox.setObjectName(u"config_size_alert_spinbox")
        sizePolicy1.setHeightForWidth(self.config_size_alert_spinbox.sizePolicy().hasHeightForWidth())
        self.config_size_alert_spinbox.setSizePolicy(sizePolicy1)
        self.config_size_alert_spinbox.setMinimum(1)
        self.config_size_alert_spinbox.setMaximum(10000)
        self.config_size_alert_spinbox.setValue(100)

        self.sizeManagementLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.config_size_alert_spinbox)

        self.sizeCriticalLabel = QLabel(self.sizeManagementGroup)
        self.sizeCriticalLabel.setObjectName(u"sizeCriticalLabel")

        self.sizeManagementLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.sizeCriticalLabel)

        self.config_size_critical_spinbox = QSpinBox(self.sizeManagementGroup)
        self.config_size_critical_spinbox.setObjectName(u"config_size_critical_spinbox")
        sizePolicy1.setHeightForWidth(self.config_size_critical_spinbox.sizePolicy().hasHeightForWidth())
        self.config_size_critical_spinbox.setSizePolicy(sizePolicy1)
        self.config_size_critical_spinbox.setMinimum(1)
        self.config_size_critical_spinbox.setMaximum(100000)
        self.config_size_critical_spinbox.setValue(1024)

        self.sizeManagementLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.config_size_critical_spinbox)


        self.configScrollLayout.addWidget(self.sizeManagementGroup)

        self.configScrollArea.setWidget(self.configScrollContent)

        self.config_tab_layout.addWidget(self.configScrollArea)

        self.configButtonLayout = QHBoxLayout()
        self.configButtonLayout.setSpacing(8)
        self.configButtonLayout.setObjectName(u"configButtonLayout")
        self.configButtonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.configButtonLayout.addItem(self.configButtonSpacer)

        self.saveConfigButton = QPushButton(self.configTab)
        self.saveConfigButton.setObjectName(u"saveConfigButton")
        self.saveConfigButton.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.saveConfigButton.sizePolicy().hasHeightForWidth())
        self.saveConfigButton.setSizePolicy(sizePolicy1)

        self.configButtonLayout.addWidget(self.saveConfigButton)


        self.config_tab_layout.addLayout(self.configButtonLayout)

        self.tab_widget.addTab(self.configTab, "")
        self.logTab = QWidget()
        self.logTab.setObjectName(u"logTab")
        sizePolicy.setHeightForWidth(self.logTab.sizePolicy().hasHeightForWidth())
        self.logTab.setSizePolicy(sizePolicy)
        self.logLayout = QVBoxLayout(self.logTab)
        self.logLayout.setSpacing(8)
        self.logLayout.setContentsMargins(0, 0, 0, 0)
        self.logLayout.setObjectName(u"logLayout")
        self.logLayout.setContentsMargins(12, 12, 12, 12)
        self.logToolbarLayout = QHBoxLayout()
        self.logToolbarLayout.setSpacing(4)
        self.logToolbarLayout.setObjectName(u"logToolbarLayout")
        self.logFilterAllButton = QPushButton(self.logTab)
        self.logFilterAllButton.setObjectName(u"logFilterAllButton")
        self.logFilterAllButton.setCheckable(True)
        self.logFilterAllButton.setChecked(True)
        sizePolicy1.setHeightForWidth(self.logFilterAllButton.sizePolicy().hasHeightForWidth())
        self.logFilterAllButton.setSizePolicy(sizePolicy1)

        self.logToolbarLayout.addWidget(self.logFilterAllButton)

        self.logFilterInfoButton = QPushButton(self.logTab)
        self.logFilterInfoButton.setObjectName(u"logFilterInfoButton")
        self.logFilterInfoButton.setCheckable(True)
        self.logFilterInfoButton.setChecked(True)
        sizePolicy1.setHeightForWidth(self.logFilterInfoButton.sizePolicy().hasHeightForWidth())
        self.logFilterInfoButton.setSizePolicy(sizePolicy1)

        self.logToolbarLayout.addWidget(self.logFilterInfoButton)

        self.logFilterWarningButton = QPushButton(self.logTab)
        self.logFilterWarningButton.setObjectName(u"logFilterWarningButton")
        self.logFilterWarningButton.setCheckable(True)
        self.logFilterWarningButton.setChecked(True)
        sizePolicy1.setHeightForWidth(self.logFilterWarningButton.sizePolicy().hasHeightForWidth())
        self.logFilterWarningButton.setSizePolicy(sizePolicy1)

        self.logToolbarLayout.addWidget(self.logFilterWarningButton)

        self.logFilterErrorButton = QPushButton(self.logTab)
        self.logFilterErrorButton.setObjectName(u"logFilterErrorButton")
        self.logFilterErrorButton.setCheckable(True)
        self.logFilterErrorButton.setChecked(True)
        sizePolicy1.setHeightForWidth(self.logFilterErrorButton.sizePolicy().hasHeightForWidth())
        self.logFilterErrorButton.setSizePolicy(sizePolicy1)

        self.logToolbarLayout.addWidget(self.logFilterErrorButton)

        self.logToolbarSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.logToolbarLayout.addItem(self.logToolbarSpacer)

        self.logClearButton = QPushButton(self.logTab)
        self.logClearButton.setObjectName(u"logClearButton")
        sizePolicy1.setHeightForWidth(self.logClearButton.sizePolicy().hasHeightForWidth())
        self.logClearButton.setSizePolicy(sizePolicy1)

        self.logToolbarLayout.addWidget(self.logClearButton)

        self.pushButton = QPushButton(self.logTab)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy1.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy1)

        self.logToolbarLayout.addWidget(self.pushButton)

        self.verifyBackupButton = QPushButton(self.logTab)
        self.verifyBackupButton.setObjectName(u"verifyBackupButton")
        sizePolicy1.setHeightForWidth(self.verifyBackupButton.sizePolicy().hasHeightForWidth())
        self.verifyBackupButton.setSizePolicy(sizePolicy1)

        self.logToolbarLayout.addWidget(self.verifyBackupButton)


        self.logLayout.addLayout(self.logToolbarLayout)

        self.logBox = QTextEdit(self.logTab)
        self.logBox.setObjectName(u"logBox")
        sizePolicy.setHeightForWidth(self.logBox.sizePolicy().hasHeightForWidth())
        self.logBox.setSizePolicy(sizePolicy)
        self.logBox.setReadOnly(True)

        self.logLayout.addWidget(self.logBox)

        self.tab_widget.addTab(self.logTab, "")

        self.main_layout.addWidget(self.tab_widget)

        MainWindow.setCentralWidget(self.central_widget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1475, 30))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOperations = QMenu(self.menubar)
        self.menuOperations.setObjectName(u"menuOperations")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.status_bar = QStatusBar(MainWindow)
        self.status_bar.setObjectName(u"status_bar")
        self.progress_bar = QProgressBar(self.status_bar)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setGeometry(QRect(0, 0, 100, 30))
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        MainWindow.setStatusBar(self.status_bar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOperations.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuOperations.addAction(self.actionStartBackup)
        self.menuOperations.addAction(self.actionStartRestore)
        self.menuOperations.addSeparator()
        self.menuOperations.addAction(self.actionVerifyBackup)
        self.menuHelp.addAction(self.actionUserGuide)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        self.tab_widget.setCurrentIndex(0)
        self.backupStackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"DFBU GUI", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"E&xit", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionStartBackup.setText(QCoreApplication.translate("MainWindow", u"Start &Backup", None))
#if QT_CONFIG(shortcut)
        self.actionStartBackup.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+B", None))
#endif // QT_CONFIG(shortcut)
        self.actionStartRestore.setText(QCoreApplication.translate("MainWindow", u"Start &Restore", None))
#if QT_CONFIG(shortcut)
        self.actionStartRestore.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+R", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"&About", None))
        self.actionVerifyBackup.setText(QCoreApplication.translate("MainWindow", u"&Verify Backup", None))
#if QT_CONFIG(shortcut)
        self.actionVerifyBackup.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+V", None))
#endif // QT_CONFIG(shortcut)
        self.actionUserGuide.setText(QCoreApplication.translate("MainWindow", u"&User Guide", None))
#if QT_CONFIG(shortcut)
        self.actionUserGuide.setShortcut(QCoreApplication.translate("MainWindow", u"F1", None))
#endif // QT_CONFIG(shortcut)
        self.emptyStateIcon.setText("")
        self.emptyStateTitle.setText(QCoreApplication.translate("MainWindow", u"No dotfiles configured yet", None))
        self.emptyStateTitle.setStyleSheet(QCoreApplication.translate("MainWindow", u"font-size: 16px; font-weight: bold; color: #1E293B;", None))
        self.emptyStateDescription.setText(QCoreApplication.translate("MainWindow", u"Click \"Add\" to create your first dotfile entry,\n"
"or load an existing configuration.", None))
        self.emptyStateDescription.setStyleSheet(QCoreApplication.translate("MainWindow", u"color: #64748B;", None))
        self.emptyStateAddButton.setText(QCoreApplication.translate("MainWindow", u"+ Add Dotfile", None))
        self.filterLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Filter by name, tags, or path...", None))
        self.fileGroupAddFileButton.setText(QCoreApplication.translate("MainWindow", u"New", None))
        ___qtablewidgetitem = self.fileGroupFileTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Included", None));
        ___qtablewidgetitem1 = self.fileGroupFileTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Status", None));
        ___qtablewidgetitem2 = self.fileGroupFileTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Application", None));
        ___qtablewidgetitem3 = self.fileGroupFileTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Tags", None));
        ___qtablewidgetitem4 = self.fileGroupFileTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Size", None));
        ___qtablewidgetitem5 = self.fileGroupFileTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Path", None));
        self.fileGroupUpdateFileButton.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.fileGroupRemoveFileButton.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.fileGroupToggleEnabledButton.setText(QCoreApplication.translate("MainWindow", u"Toggle Active", None))
#if QT_CONFIG(tooltip)
        self.fileGroupSaveFilesButton.setToolTip(QCoreApplication.translate("MainWindow", u"Save enable/disable changes to the configuration file (not the backup itself)", None))
#endif // QT_CONFIG(tooltip)
        self.fileGroupSaveFilesButton.setText(QCoreApplication.translate("MainWindow", u"Save Config", None))
        self.fileGroupTotalSizeLabel.setStyleSheet(QCoreApplication.translate("MainWindow", u"font-weight: bold; padding: 5px;", None))
        self.fileGroupTotalSizeLabel.setText(QCoreApplication.translate("MainWindow", u"Total Size (enabled): Calculating...", None))
        self.backupOptionsLabel.setStyleSheet(QCoreApplication.translate("MainWindow", u"font-weight: bold;", None))
        self.backupOptionsLabel.setText(QCoreApplication.translate("MainWindow", u"Backup Options:", None))
        self.mirrorCheckbox.setText(QCoreApplication.translate("MainWindow", u"Mirror", None))
        self.archiveCheckbox.setText(QCoreApplication.translate("MainWindow", u"Archive", None))
#if QT_CONFIG(tooltip)
        self.forceBackupCheckbox.setToolTip(QCoreApplication.translate("MainWindow", u"When checked, all files will be copied even if unchanged (slower but ensures complete backup)", None))
#endif // QT_CONFIG(tooltip)
        self.forceBackupCheckbox.setText(QCoreApplication.translate("MainWindow", u"Force Full Backup", None))
#if QT_CONFIG(tooltip)
        self.startBackupButton.setToolTip(QCoreApplication.translate("MainWindow", u"Start backup operation to copy enabled dotfiles to backup locations", None))
#endif // QT_CONFIG(tooltip)
        self.startBackupButton.setText(QCoreApplication.translate("MainWindow", u"Start Backup", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.backupTab), QCoreApplication.translate("MainWindow", u"Backup", None))
        self.restoreSourceLabel.setText(QCoreApplication.translate("MainWindow", u"Restore Source Path", None))
        self.restoreSourceInfoLabel.setText(QCoreApplication.translate("MainWindow", u"Select the backup directory containing the hostname folder.\n"
"Example: ~/GitHub/dotfiles/ (containing hostname subdirectory)", None))
        self.restoreSourceButton.setText(QCoreApplication.translate("MainWindow", u"Start Restore", None))
        self.restoreSourceEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Path to backup directory with hostname", None))
        self.restoreSourceBrowseButton.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.restorePreviewGroup.setTitle(QCoreApplication.translate("MainWindow", u"Backup Preview", None))
        self.restorePreviewHostLabel.setText(QCoreApplication.translate("MainWindow", u"Hostname: \u2014", None))
        self.restorePreviewCountLabel.setText(QCoreApplication.translate("MainWindow", u"Files: \u2014", None))
        self.restorePreviewSizeLabel.setText(QCoreApplication.translate("MainWindow", u"Size: \u2014", None))
        ___qtreewidgetitem = self.restorePreviewTree.headerItem()
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("MainWindow", u"Size", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Files", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Application", None));
        self.restoreInfoLabel.setText(QCoreApplication.translate("MainWindow", u"Restore Information", None))
        self.restoreInfoText.setText(QCoreApplication.translate("MainWindow", u"Restore will:\n"
"\u2022 Discover all files in the selected backup directory\n"
"\u2022 Reconstruct original file paths based on backup structure\n"
"\u2022 Copy files back to their original locations\n"
"\u2022 Create necessary parent directories\n"
"\u2022 Preserve file metadata and permissions\n"
"\n"
"WARNING: This will overwrite existing files at destination paths.", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.restoreTab), QCoreApplication.translate("MainWindow", u"Restore", None))
        self.backupPathsGroup.setTitle(QCoreApplication.translate("MainWindow", u"Backup Paths", None))
        self.mirror_path_label.setText(QCoreApplication.translate("MainWindow", u"Mirror Directory:", None))
        self.config_mirror_path_edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Mirror backup directory", None))
        self.browse_mirror_btn.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.archivePathLabel.setText(QCoreApplication.translate("MainWindow", u"Archive Directory:", None))
        self.configArchivePathEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Archive backup directory", None))
        self.browseArchiveButton.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.backupModesGroup.setTitle(QCoreApplication.translate("MainWindow", u"Backup Modes", None))
        self.config_mirror_checkbox.setText(QCoreApplication.translate("MainWindow", u"Enable mirror backup (uncompressed)", None))
        self.config_archive_checkbox.setText(QCoreApplication.translate("MainWindow", u"Enable archive backup (compressed)", None))
        self.config_hostname_checkbox.setText(QCoreApplication.translate("MainWindow", u"Include hostname in backup path", None))
        self.config_date_checkbox.setText(QCoreApplication.translate("MainWindow", u"Include date in backup path", None))
        self.archiveOptionsGroup.setTitle(QCoreApplication.translate("MainWindow", u"Archive Options", None))
        self.compressionLabel.setText(QCoreApplication.translate("MainWindow", u"Compression Level:", None))
#if QT_CONFIG(tooltip)
        self.config_compression_spinbox.setToolTip(QCoreApplication.translate("MainWindow", u"0 = no compression, 9 = maximum compression", None))
#endif // QT_CONFIG(tooltip)
        self.rotate_label.setText(QCoreApplication.translate("MainWindow", u"Rotate Archives:", None))
        self.config_rotate_checkbox.setText(QCoreApplication.translate("MainWindow", u"Enable archive rotation", None))
        self.max_archives_label.setText(QCoreApplication.translate("MainWindow", u"Max Archives:", None))
#if QT_CONFIG(tooltip)
        self.config_max_archives_spinbox.setToolTip(QCoreApplication.translate("MainWindow", u"Maximum number of archives to keep", None))
#endif // QT_CONFIG(tooltip)
        self.preRestoreSafetyGroup.setTitle(QCoreApplication.translate("MainWindow", u"Pre-Restore Safety", None))
#if QT_CONFIG(tooltip)
        self.config_pre_restore_checkbox.setToolTip(QCoreApplication.translate("MainWindow", u"Backup existing files before restore operations", None))
#endif // QT_CONFIG(tooltip)
        self.config_pre_restore_checkbox.setText(QCoreApplication.translate("MainWindow", u"Backup files before overwriting", None))
        self.maxRestoreBackupsLabel.setText(QCoreApplication.translate("MainWindow", u"Max Restore Backups:", None))
#if QT_CONFIG(tooltip)
        self.config_max_restore_spinbox.setToolTip(QCoreApplication.translate("MainWindow", u"Maximum number of pre-restore backups to keep", None))
#endif // QT_CONFIG(tooltip)
        self.restoreBackupDirLabel.setText(QCoreApplication.translate("MainWindow", u"Restore Backup Dir:", None))
#if QT_CONFIG(tooltip)
        self.config_restore_path_edit.setToolTip(QCoreApplication.translate("MainWindow", u"Directory to store pre-restore backups", None))
#endif // QT_CONFIG(tooltip)
        self.config_restore_path_edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"~/.local/share/dfbu/restore-backups", None))
        self.browse_restore_btn.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.verificationGroup.setTitle(QCoreApplication.translate("MainWindow", u"Verification", None))
#if QT_CONFIG(tooltip)
        self.config_verify_checkbox.setToolTip(QCoreApplication.translate("MainWindow", u"Run verification after each backup operation", None))
#endif // QT_CONFIG(tooltip)
        self.config_verify_checkbox.setText(QCoreApplication.translate("MainWindow", u"Automatically verify backup integrity", None))
#if QT_CONFIG(tooltip)
        self.config_hash_checkbox.setToolTip(QCoreApplication.translate("MainWindow", u"Compare file contents using cryptographic hash instead of size only", None))
#endif // QT_CONFIG(tooltip)
        self.config_hash_checkbox.setText(QCoreApplication.translate("MainWindow", u"Use SHA-256 hash comparison (slower)", None))
        self.sizeManagementGroup.setTitle(QCoreApplication.translate("MainWindow", u"Size Management", None))
#if QT_CONFIG(tooltip)
        self.config_size_check_checkbox.setToolTip(QCoreApplication.translate("MainWindow", u"Show warnings for large files before starting backup", None))
#endif // QT_CONFIG(tooltip)
        self.config_size_check_checkbox.setText(QCoreApplication.translate("MainWindow", u"Analyze file sizes before backup", None))
        self.sizeWarningLabel.setText(QCoreApplication.translate("MainWindow", u"Warning Threshold (MB):", None))
#if QT_CONFIG(tooltip)
        self.config_size_warning_spinbox.setToolTip(QCoreApplication.translate("MainWindow", u"Files larger than this show a warning (yellow)", None))
#endif // QT_CONFIG(tooltip)
        self.sizeAlertLabel.setText(QCoreApplication.translate("MainWindow", u"Alert Threshold (MB):", None))
#if QT_CONFIG(tooltip)
        self.config_size_alert_spinbox.setToolTip(QCoreApplication.translate("MainWindow", u"Files larger than this show an alert (orange)", None))
#endif // QT_CONFIG(tooltip)
        self.sizeCriticalLabel.setText(QCoreApplication.translate("MainWindow", u"Critical Threshold (MB):", None))
#if QT_CONFIG(tooltip)
        self.config_size_critical_spinbox.setToolTip(QCoreApplication.translate("MainWindow", u"Files larger than this show critical warning (red)", None))
#endif // QT_CONFIG(tooltip)
        self.saveConfigButton.setText(QCoreApplication.translate("MainWindow", u"Save Configuration", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.configTab), QCoreApplication.translate("MainWindow", u"Configuration", None))
        self.logFilterAllButton.setText(QCoreApplication.translate("MainWindow", u"All", None))
        self.logFilterInfoButton.setText(QCoreApplication.translate("MainWindow", u"Info", None))
        self.logFilterWarningButton.setText(QCoreApplication.translate("MainWindow", u"Warnings", None))
        self.logFilterErrorButton.setText(QCoreApplication.translate("MainWindow", u"Errors", None))
        self.logClearButton.setText(QCoreApplication.translate("MainWindow", u"Clear Log", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Save Log", None))
        self.verifyBackupButton.setText(QCoreApplication.translate("MainWindow", u"Verify Backup", None))
#if QT_CONFIG(tooltip)
        self.verifyBackupButton.setToolTip(QCoreApplication.translate("MainWindow", u"Verify integrity of the last backup operation", None))
#endif // QT_CONFIG(tooltip)
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.logTab), QCoreApplication.translate("MainWindow", u"Logs", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuOperations.setTitle(QCoreApplication.translate("MainWindow", u"&Operations", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
    # retranslateUi

