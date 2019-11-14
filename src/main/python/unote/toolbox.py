from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QPolygon, QIcon
from PyQt5.QtCore import pyqtSignal, QFile, QTextStream, pyqtSlot, QObject, QPoint, Qt, QRect, QSize
from PyQt5.QtWidgets import QDialog, QGraphicsView, QGraphicsScene, QWidget, QPushButton, QVBoxLayout, QTextEdit, QGridLayout, QSlider

from indexed import IndexedOrderedDict


from math import sin, cos

import assets

from editHelper import editModes
from preferences import Preferences

OUTEROFFSETTOP = 25
OUTEROFFSETBOTTOM = 14

TEXTBOXOFFSETTOP = 5
TEXTBOXOFFSETBOTTOM = 30

OUTERLINEWIDTH = OUTEROFFSETBOTTOM
INNERLINEWIDTH = 4

BUTTONOFFSETTOP = 17
BUTTONOFFSETBOTTOM = 15

CIRCLE = 5760


class ToolBoxWidget(QWidget):
    '''
    Class which creates a toolbox storing all available tools and handles text input
    '''
    numberOfButtons = 4

    textButtonName = 'textButton'
    markerButtonName = 'markerButton'
    okButtonName = 'okButton'
    cancelButtonName = 'cancelButton'

    items = IndexedOrderedDict()

    textInputFinished = pyqtSignal(int, int, int, bool, str)
    currentPageNumber = -1
    currentX = -1
    currentY = -1

    editMode = editModes.none

    editModeChange = pyqtSignal(str)

    editTextBox = False

    buttons = IndexedOrderedDict()

    def __init__(self, parent):
        '''
        Creates the toolboxwidget as child of the window widget

        :param parent: Parent window widget.
        '''
        QWidget.__init__(self, parent)
        self.initUI()

    def initUI(self):
        '''
        Sets up major UI components
        '''

        # Create a rectengle from teh given outer dimensions
        textBoxRect = self.rect()
        # Shrink it for matiching textBox size
        textBoxRect.adjust(+30,+30,-12,-12)

        buttonRect = self.rect()
        buttonRect.adjust(+35,+30,5,-20)

        self.row1Left = buttonRect.topLeft()
        self.row1Right = buttonRect.topRight()
        self.row2Left = QPoint(self.row1Left.x(), self.row1Left.y()+35)
        self.row2Right = QPoint(self.row1Right.x(), self.row1Right.y()+35)
        self.row3Left = QPoint(self.row2Left.x(), self.row2Left.y()+35)
        self.row3Right = QPoint(self.row2Right.x(), self.row2Right.y()+35)
        self.bottomLeft = QPoint(buttonRect.topLeft().x(), buttonRect.topLeft().y()+130)
        self.bottomRight = QPoint(self.row1Right.x(), self.row1Right.y()+130)
        self.bottomMiddle = QPoint(self.row1Left.x()+(self.row1Right.x()-self.row1Left.x()), self.row1Right.y()+130)

        # We use a textEdit for making text boxes editable for user
        self.pTextEdit = QTextEdit(self)
        # Always enable line wrapping
        self.pTextEdit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.pTextEdit.setAutoFormatting(QTextEdit.AutoAll)
        self.pTextEdit.setAcceptRichText(True)
        self.pTextEdit.setFontPointSize(10)
        self.pTextEdit.setPlaceholderText("Text Box Content")

        # Forward keypressevents from the textEdit to the parent toolBoxWidget
        self.keyPressEvent = self.pTextEdit.keyPressEvent
        self.keyReleaseEvent = self.pTextEdit.keyReleaseEvent

        # We need a layout to add the textBox to the toolBoxWidget
        widgetLayout = QGridLayout(self)
        widgetLayout.addWidget(self.pTextEdit)
        self.pTextEdit.setGeometry(textBoxRect)

        buttonSize = QSize(60,30)

        # -----------------------------
        # Toolbuttons
        # -----------------------------

        self.textButton = QPushButton(self)
        self.textButton.setFixedSize(buttonSize)
        self.textButton.move(self.row1Right)
        self.textButton.setIcon(QIcon(":/assets/text.png"))
        self.textButton.setCheckable(True)
        self.buttons['textButton'] = self.textButton

        self.markerButton = QPushButton(self)
        self.markerButton.setFixedSize(buttonSize)
        self.markerButton.move(self.row1Left)
        self.markerButton.setIcon(QIcon(":/assets/marker.png"))
        self.markerButton.setCheckable(True)
        self.buttons['markerButton'] = self.markerButton

        self.freehandButton = QPushButton(self)
        self.freehandButton.setFixedSize(buttonSize)
        self.freehandButton.move(self.row2Left)
        self.freehandButton.setIcon(QIcon(":/assets/freehand.png"))
        self.freehandButton.setCheckable(True)
        self.buttons['freehandButton'] = self.freehandButton

        self.markdownButton = QPushButton(self)
        self.markdownButton.setFixedSize(buttonSize)
        self.markdownButton.move(self.row2Right)
        self.markdownButton.setIcon(QIcon(":/assets/markdown.png"))
        self.markdownButton.setCheckable(True)
        self.buttons['markdownButton'] = self.markdownButton

        self.formsButton = QPushButton(self)
        self.formsButton.setFixedSize(buttonSize)
        self.formsButton.move(self.row3Left)
        self.formsButton.setIcon(QIcon(":/assets/forms.png"))
        self.formsButton.setCheckable(True)
        self.buttons['formsButton'] = self.formsButton

        self.clipboardButton = QPushButton(self)
        self.clipboardButton.setFixedSize(buttonSize)
        self.clipboardButton.move(self.row3Right)
        self.clipboardButton.setIcon(QIcon(":/assets/clipboard.png"))
        self.clipboardButton.setCheckable(True)
        self.buttons['clipboardButton'] = self.clipboardButton

        self.okButton = QPushButton(self)
        self.okButton.setFixedSize(buttonSize)
        self.okButton.move(self.bottomLeft)
        self.okButton.setIcon(QIcon(":/assets/ok.png"))
        self.buttons['okButton'] = self.okButton

        self.cancelButton = QPushButton(self)
        self.cancelButton.setFixedSize(buttonSize)
        self.cancelButton.move(self.bottomRight)
        self.cancelButton.setIcon(QIcon(":/assets/cancel.png"))
        self.buttons['cancelButton'] = self.cancelButton

        self.deleteButton = QPushButton(self)
        self.deleteButton.setFixedSize(buttonSize)
        self.deleteButton.move(self.bottomRight)
        self.deleteButton.setIcon(QIcon(":/assets/delete.png"))
        self.buttons['deleteButton'] = self.deleteButton

        # Set Shortcuts for the buttons
        self.textButton.setShortcut("Ctrl+T")
        self.markerButton.setShortcut("Ctrl+M")
        self.freehandButton.setShortcut("Ctrl+D")
        self.okButton.setShortcut("Ctrl+Return")
        self.cancelButton.setShortcut("Esc")
        self.deleteButton.setShortcut("Ctrl+Del")

        # Connect Events for the buttons
        self.okButton.clicked.connect(self.handleOkButton)
        self.markerButton.clicked.connect(self.handleMarkerButton)
        self.textButton.clicked.connect(self.handleTextButton)
        self.formsButton.clicked.connect(self.handleFormsButton)
        self.freehandButton.clicked.connect(self.handleFreehandButton)
        self.clipboardButton.clicked.connect(self.handleClipboardButton)
        self.markdownButton.clicked.connect(self.handleMarkdownButton)
        self.cancelButton.clicked.connect(self.handleCancelButton)
        self.deleteButton.clicked.connect(self.handleDeleteButton)


        # -----------------------------
        # Preference Buttons
        # -----------------------------

        self.sizeButton = QPushButton(self)
        self.sizeButton.setFixedSize(buttonSize)
        self.sizeButton.setIcon(QIcon(":/assets/size.png"))
        self.sizeButton.setCheckable(True)
        self.buttons['sizeButton'] = self.sizeButton



        self.setButtonState()


        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(10)
        self.slider.setMaximum(30)
        self.slider.setValue(20)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(5)
        self.slider.move(self.bottomMiddle)

    def paintEvent(self, event):
        '''
        Overrides the default paint event to either draw a textBox or a toolBox
        '''
        if self.editTextBox:
            # Draw the toolBoxShape
            self.drawRectShape(event)
        else:
            self.drawToolBoxShape(event)

        # Run the parent paint Event
        QWidget.paintEvent(self, event)

    def drawToolBoxShape(self, paintEvent):
        '''
        Draws the circular toolBox shape
        '''
        outerCircleRect = self.rect()
        outerCircleRect.adjust(+OUTEROFFSETBOTTOM,+OUTEROFFSETTOP,-OUTEROFFSETBOTTOM,-OUTEROFFSETBOTTOM)

        topMiddle = (outerCircleRect.topRight() - outerCircleRect.topLeft()) / 2 + outerCircleRect.topLeft()
        bottomMiddle = (outerCircleRect.bottomRight() - outerCircleRect.bottomLeft()) / 2 + outerCircleRect.bottomLeft()

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        # shapePainter.setPen(QPen(QColor(14,125,145),  OUTERLINEWIDTH, Qt.SolidLine))
        # shapePainter.drawArc(outerCircleRect, CIRCLE/2, CIRCLE/2)

        shapePainter.setPen(QPen(QColor(14,125,145),  5, Qt.SolidLine))
        shapePainter.drawLine(topMiddle, bottomMiddle)

        shapePainter.setPen(QPen(QColor(14,125,145),  2, Qt.SolidLine))
        arcRect = QRect(bottomMiddle.x() - 6, bottomMiddle.y()+1, 12, 12)
        shapePainter.drawArc(arcRect, 0, CIRCLE)

        self.pTextEdit.setEnabled(False)
        self.pTextEdit.setVisible(False)

    def drawRectShape(self, event):
        '''
        Draws a rectangle for the textEdit box
        '''
        textBoxRect = self.rect()
        outerCircleRect = self.rect()
        textBoxRect.adjust(+30,+30,-12,-12)
        outerCircleRect.adjust(+8,+8,-8,-15)

        moveRect = QRect(0,0, 11,11)

        shapePainter = QPainter(self)
        shapePainter.setRenderHint(shapePainter.Antialiasing)
        # shapePainter.setPen(QPen(QColor(14,125,145),  5, Qt.SolidLine))
        # shapePainter.drawRect(textBoxRect)

        shapePainter.setPen(QPen(QColor(14,125,145),  5, Qt.SolidLine))
        shapePainter.drawLine(outerCircleRect.topLeft(), outerCircleRect.bottomLeft())

        # shapePainter.setPen(QPen(QColor(14,125,145),  2, Qt.SolidLine))
        # arcRect = QRect(outerCircleRect.bottomLeft().x() - 6, outerCircleRect.bottomLeft().y()+1, 12, 12)
        # shapePainter.drawArc(arcRect, 0, CIRCLE)

        self.pTextEdit.setEnabled(True)
        self.pTextEdit.setVisible(True)

        self.pTextEdit.ensureCursorVisible()
        self.pTextEdit.setFocus()



    def setButtonState(self):
        '''
        Sets the button state depending on the current edit mode
        '''
        if self.editTextBox and self.editMode == editModes.newTextBox:
            self.setEnableOnAllButtonsButThose(['okButton', 'cancelButton'])
            self.setVisibleOnAllButtonsButThose(['okButton', 'cancelButton'])

        elif self.editTextBox and self.editMode == editModes.editTextBox:
            self.setEnableOnAllButtonsButThose(['okButton', 'deleteButton'])
            self.setVisibleOnAllButtonsButThose(['okButton', 'deleteButton'])

        elif self.editMode == editModes.newTextBox:
            self.setEnableOnAllButtonsButThose(['textButton', 'sizeButton'])
            self.setVisibleOnAllButtonsButThose(['textButton', 'sizeButton'])

            self.buttons['sizeButton'].move(self.row1Left)

        elif self.editMode == editModes.marker:
            self.setEnableOnAllButtonsButThose(['markerButton', 'sizeButton'])

            self.buttons['sizeButton'].move(self.row1Right)

        elif self.editMode == editModes.freehand:
            self.setEnableOnAllButtonsButThose(['freehandButton'])

            self.buttons['sizeButton'].move(self.row1Right)

        elif self.editMode == editModes.clipboard:
            self.setEnableOnAllButtonsButThose(['clipboardButton'])

        elif self.editMode == editModes.forms:
            self.setEnableOnAllButtonsButThose(['formsButton'])

        elif self.editMode == editModes.markdown:
            self.setEnableOnAllButtonsButThose(['markdownButton'])

        elif self.editMode == editModes.none:
            self.setVisibleOnAllButtonsButThose(['textButton', 'clipboardButton', 'formsButton', 'freehandButton', 'markerButton', 'markdownButton'])

            self.setEnableOnAllButtonsButThose(['textButton', 'clipboardButton', 'formsButton', 'freehandButton', 'markerButton', 'markdownButton'])

            self.setCheckedOnAllButtonsButThose([])

    def setEnableOnAllButtonsButThose(self, names, value=False):
        for buttonName, buttonInst in self.buttons.items():
            if not buttonName in names:
                buttonInst.setEnabled(value)
            else:
                buttonInst.setEnabled(not value)


    def setVisibleOnAllButtonsButThose(self, names, value=False):
        for buttonName, buttonInst in self.buttons.items():
            if not buttonName in names:
                buttonInst.setVisible(value)
            else:
                buttonInst.setVisible(not value)

    def setCheckedOnAllButtonsButThose(self, names, value=False):
        for buttonName, buttonInst in self.buttons.items():
            if not buttonName in names:
                buttonInst.setChecked(value)
            else:
                buttonInst.setChecked(not value)

    def insertCurrentContent(self, content):
        '''
        Used to append the provided content to the textEdit box

        :param content: Text which should be displayed in the textEdit
        '''
        if content != "":
            self.pTextEdit.setText(content)
            return True
        else:
            self.pTextEdit.setText("")
            return False

    def mousePressEvent(self, event):
        '''
        Overrides the default event
        '''
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        '''
        Overrides the default event
        '''
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        QWidget.mouseMoveEvent(self, event)

    # def mouseReleaseEvent(self, event):
    #     '''
    #     Overrides the default event
    #     '''
    #     if self.__mousePressPos is not None:
    #         moved = event.globalPos() - self.__mousePressPos
    #         if moved.manhattanLength() > 3:
    #             event.ignore()
    #             return

    #     QWidget.mouseReleaseEvent(self, event)

    @pyqtSlot(int, int, int, str)
    def handleTextInputRequest(self, x, y, pageNumber, currentContent):
        '''
        Slot when toolBox receives a textInput request. This is the case, when the user wants to insert a new or edit an existing textBox
        '''
        # Switch in to text box mode and redraw Widget
        self.currentPageNumber = pageNumber
        self.currentContent = currentContent

        if self.insertCurrentContent(currentContent):
            self.editMode = editModes.editTextBox
        else:
            self.editMode = editModes.newTextBox

        self.editTextBox = True
        self.setButtonState()

        self.currentX = x
        self.currentY = y
        self.repaint()

    def handleTextButton(self):
        if self.textButton.isChecked():
            self.editMode = editModes.newTextBox
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleMarkerButton(self):
        if self.markerButton.isChecked():
            self.editMode = editModes.marker
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleClipboardButton(self):
        if self.clipboardButton.isChecked():
            self.editMode = editModes.clipboard
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleFormsButton(self):
        if self.formsButton.isChecked():
            self.editMode = editModes.forms
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleFreehandButton(self):
        if self.freehandButton.isChecked():
            self.editMode = editModes.freehand
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleMarkdownButton(self):
        if self.markdownButton.isChecked():
            self.editMode = editModes.markdown
        else:
            self.editMode = editModes.none

        self.editModeChange.emit(self.editMode)
        self.setButtonState()

    def handleOkButton(self):
        '''
        This method handles all the stuff that needs to be done, when the user successfully finished textEditing
        '''
        if self.editMode == editModes.newTextBox or self.editMode == editModes.editTextBox:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, True, self.pTextEdit.toPlainText())
            self.editMode = editModes.none
            self.editTextBox = False
            self.setButtonState()

            self.repaint()
            self.currentPageNumber = -1
            self.currentX = -1
            self.currentY = -1

    def handleCancelButton(self):
        '''
        This method handles all the stuff that needs to be done, when the user canceled textEditing
        '''
        if self.editMode == editModes.newTextBox or self.editMode == editModes.editTextBox:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, False, self.currentContent)
            self.editMode = editModes.none
            self.editTextBox = False
            self.setButtonState()

            self.repaint()
            self.currentPageNumber = -1
            self.currentX = -1
            self.currentY = -1


    def handleDeleteButton(self):
        '''
        This method handles all the stuff that needs to be done, when the user canceled textEditing
        '''
        if self.editMode == editModes.newTextBox or self.editMode == editModes.editTextBox:
            self.textInputFinished.emit(self.currentX, self.currentY, self.currentPageNumber, False, "")
            self.editMode = editModes.none
            self.editTextBox = False
            self.setButtonState()

            self.repaint()
            self.currentPageNumber = -1
            self.currentX = -1
            self.currentY = -1
