# ---------------------------------------------------------------
# -- UNote Main File --
#
# Main File for running the UNote
#
# Author: Melvin Strobl
# ---------------------------------------------------------------


# ----------------------------------------------------------
# Import region
# ----------------------------------------------------------
from fbs_runtime.application_context.PyQt5 import ApplicationContext

import argparse  # parsing cmdline arguments
import os  # launching external python script
import sys  # exit script, file parsing
import atexit

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import QTimer, Qt, QRect, QObject

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))


from core import GraphicsViewHandler
from unote_receivers import Receivers
from preferences import Preferences
from toolbox import ToolBoxWidget
from preferences_gui import PreferencesGUI

from unote_qt_export import Ui_MainWindow



class App(QObject):
    appctxt = ApplicationContext()

    ICONPATH = appctxt.get_resource('icon.png')

    DONATEURL = "https://www.paypal.me/vinstrobl/coffee"
    UPDATEURL = "http://www.foxbyrd.com/wp-content/uploads/2018/02/file-4.jpg"
    ABOUTURL = "http://www.foxbyrd.com/wp-content/uploads/2018/02/file-4.jpg"

    TOOLBOXWIDTH = 200
    TOOLBOXHEIGHT = 200
    TOOLBOXSTARTX = 200
    TOOLBOXSTARTY = 50

    # MAINWINDOWSTARTX = 0
    # MAINWINDOWSTARTY = 0
    # MAINWINDOWWIDTH = 1920
    # MAINWINDOWHEIGHT = 1080

class UNote(App):
    '''
    Main class for the UNote
    '''

    def __init__(self, args):
        super().__init__()


        self.initUI()

        t = QTimer()
        t.singleShot(0, self.onQApplicationStarted)



        self.preferencesGui = PreferencesGUI(self.PreferenceWindow)

        self.receiversInst = Receivers(self.ui)

        self.connectReceivers()

        self.ui.floatingToolBox.restoreDefaults()

        if args.open:
            self.receiversInst.loadPdf(os.path.abspath(args.open))

        elif args.new:
            self.receiversInst.newPdf(os.path.abspath(args.new))



    def initUI(self):
        '''
        Initialize mandatory ui components
        '''
        # Create an application context
        # self.app = QtWidgets.QApplication(sys.argv)
        self.appctxt = ApplicationContext()

        self.MainWindow = QMainWindow()

        self.ui = Ui_MainWindow()

        # Load the ui definitions generated by qt designer
        self.ui.setupUi(self.MainWindow)

        # Load the icon
        self.MainWindow.setWindowIcon(QIcon(self.ICONPATH))

        # Get the preferences window ready
        self.PreferenceWindow = QWidget(self.MainWindow)
        self.PreferenceWindow.move(self.MainWindow.width()/2 - 500, self.MainWindow.height()/2 - 250)

        # Initialize graphicviewhandler. This is a core component of unote
        self.ui.graphicsView = GraphicsViewHandler(self.ui.centralwidget)
        # Simply use the whole window
        self.ui.gridLayout.addWidget(self.ui.graphicsView, 0, 0, 1, 1)

        # Initialize a floating toolboxwidget. This is used for storing tools and editing texts
        self.ui.floatingToolBox = ToolBoxWidget(self.MainWindow)
        self.ui.floatingToolBox.setWindowFlags(Qt.WindowTitleHint | Qt.FramelessWindowHint)
        self.ui.floatingToolBox.setObjectName("floatingToolBox")
        self.ui.floatingToolBox.setGeometry(QRect(self.TOOLBOXSTARTX, self.TOOLBOXSTARTY, self.TOOLBOXWIDTH, self.TOOLBOXHEIGHT))
        self.ui.floatingToolBox.show()
        # self.ui.floatingToolBox.setStyleSheet("background-color:black")


    def run(self, args):
        '''
        Starts the UNote
        '''
        self.MainWindow.show()

        result = self.appctxt.app.exec_()

        self.onQApplicationQuit()

        sys.exit(result)

    def onQApplicationStarted(self):
        '''
        Executed immediately when Application started
        '''
        #Restore window pos
        try:
            self.MainWindow.restoreGeometry(bytearray(Preferences.data['geometry'],"utf-8"))
            self.MainWindow.restoreState(bytearray(Preferences.data['state'],"utf-8"))
        except Exception as identifier:
            print("Unable to restore window size: " + str(identifier))

        # Initialize auto saving
        # self.autoSaveReceiver()





    def autoSaveReceiver(self):
        if Preferences.data['comboBoxAutosave'] != 'never' and Preferences.data['comboBoxAutosave'] != '':
            self.autoSaveTimer = QTimer()
            interval = 600 * int(Preferences.data['comboBoxAutosave'])
            print(interval)
            self.autoSaveTimer.singleShot(interval, self.autoSaveReceiver())

            # self.ui.graphicsView.savePdf()

    def onQApplicationQuit(self):
        '''
        Executed immediately when Application stops
        '''
        Preferences.updateKeyValue('geometry', self.MainWindow.saveGeometry())
        Preferences.updateKeyValue('state', self.MainWindow.saveState())

        self.preferencesGui.storeSettings()



    def connectReceivers(self):
        '''
        Connects all the buttons to the right receivers
        '''
        # Add the exit method
        self.ui.actionExit.triggered.connect(self.appctxt.app.quit)

        # Open Preferences
        self.ui.actionPreferences.triggered.connect(lambda: self.receiversInst.openPreferencesReceiver(self.preferencesGui))

        # Create new PDF file
        self.ui.actionNew_PDF.triggered.connect(lambda: self.receiversInst.newPdf())

        # Load PDF File
        self.ui.actionLoad_PDF.triggered.connect(lambda: self.receiversInst.loadPdf())

        # Save PDF
        self.ui.actionSave_PDF.triggered.connect(lambda: self.receiversInst.savePdf())

        # Save PDF as
        self.ui.actionSave_PDF_as.triggered.connect(lambda: self.receiversInst.savePdfAs())

        # Insert PDF Page
        self.ui.actionPageInsertHere.triggered.connect(lambda: self.receiversInst.pageInsertHere())

        # Goto Page
        self.ui.actionPageGoto.triggered.connect(lambda: self.receiversInst.pageGoto())

        # Zoom In
        self.ui.actionZoomIn.triggered.connect(lambda: self.receiversInst.zoomIn())

        # Zoom Out
        self.ui.actionZoomOut.triggered.connect(lambda: self.receiversInst.zoomOut())


        self.ui.actionZoomToFit.triggered.connect(lambda: self.receiversInst.zoomToFit())

        # Delete Active PDF Page
        self.ui.actionPageInsertHere.triggered.connect(lambda: self.receiversInst.pageDeleteActive())

        # Toolbox Edit modes available
        self.ui.floatingToolBox.editModeChange.connect(self.ui.graphicsView.editModeChangeRequest)

        # Toolboxspecific events
        self.ui.floatingToolBox.textInputFinished.connect(self.ui.graphicsView.toolBoxTextInputEvent)
        self.ui.graphicsView.requestTextInput.connect(self.ui.floatingToolBox.handleTextInputRequest)

        self.ui.actionHelpDonate.triggered.connect(lambda: self.receiversInst.donateReceiver(self.DONATEURL))

        self.ui.actionHelpCheck_for_Updates.triggered.connect(lambda: self.receiversInst.checkForUpdatesReceiver(self.UPDATEURL))

        self.ui.actionHelpAbout.triggered.connect(lambda: self.receiversInst.aboutReceiver(self.ABOUTURL))
# ----------------------------------------------------------
# User Parameter region
# ----------------------------------------------------------


# ----------------------------------------------------------
# Variable region
# ----------------------------------------------------------


# ----------------------------------------------------------
# Helper Fct for handling input arguments
# ----------------------------------------------------------
def argumentHelper():
    '''
    Just a helper for processing the arguments
    '''

    # Define Help Te
    helpText = 'Register Converter Script'
    # Create ArgumentParser instance
    argparser = argparse.ArgumentParser(description=helpText)

    argparser.add_argument('-o', '--open',
                        help='Open existing pdf from path')
    argparser.add_argument('-n', '--new',
                        help='Create new pdf at path')

    return argparser.parse_args()


# ----------------------------------------------------------
# Called on script exit
# ----------------------------------------------------------
def exitMethod():
    '''
    Called for exiting the program
    '''

    sys.exit("\n\nExiting UNote\n")


# ----------------------------------------------------------
# Main Entry Point
# ----------------------------------------------------------
def main():
    '''
    Main method handling the flow
    '''

    # -----------------------------------------------------
    # -----------------At Exit Register------------------
    atexit.register(exitMethod)

    # -----------------------------------------------------
    # ---------------Argument processing------------------
    args = None
    try:
        args = argumentHelper()
    except ValueError as e:
        sys.exit("Unable to parse arguments:\n" + str(e))

    UNoteGUI = UNote(args)
    UNoteGUI.run(args)


# Standard python script entry handling
if __name__ == '__main__':
    main()
