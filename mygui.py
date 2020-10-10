from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import *
from sys import argv, exit
from autoanalysis import Autoanalysis
from PropagationCalculator import Ui_PropagationCalculator
from Recording import RecordingData
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from os import listdir
from os.path import isfile, join
from os.path import splitext
import neo.io
import gc

class Main(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_PropagationCalculator()
        self.ui.setupUi(self)
        QObject.connect(self.ui.pushButton, SIGNAL("clicked()"), self.importData)
        QObject.connect(self.ui.auto_analysis, SIGNAL("clicked()"), self.autoanalysis)
        #QObject.connect(self.ui.comboBox, SIGNAL("activated(QString)"), self.comboChosen)
        #QObject.connect(self.ui.checkBox, SIGNAL("stateChanged(int)"), self.showDataChecked)
        #QObject.connect(self.ui.lineEdit, SIGNAL("returnPressed()"), self.dataLengthChanged)
        #QObject.connect(self.ui.lineEdit_2, SIGNAL("returnPressed()"), self.dataLengthChanged)
        #validator = QDoubleValidator()
        #self.ui.lineEdit.setValidator(validator)
        #self.ui.lineEdit_2.setValidator(validator)
        self.ui.actionShow_Axes.triggered.connect(self.showAxis)
        self.ui.actionAlter_Markers.triggered.connect(self.alter_markers)
        self.ui.actionOpen_Data.triggered.connect(self.importData)
        self.ui.actionFilter_Config.triggered.connect(self.get_filter_config)
        self.ui.actionAnalyse_waveform_currently_loaded.triggered.connect(self.autoanalysis)
        self.ui.actionAnalyse_multiple_additional_files.triggered.connect(self.multianalysis)
        self.ui.actionSet_threshold.triggered.connect(self.set_threshold)
        self.ui.actionSet_width.triggered.connect(self.set_spikewindow)
        self.tabs = []
        self.recordings = []
        self.filterfrequency = (49, True)
        self.threshold = (30, True)
        self.spikewindow = (100, True)
        self.ui.actionAlter_Markers.setEnabled(True)
        self.ui.tabWidgetPage1.close()

    #self.setCentralWidget(self.ui.widget)

    def set_spikewindow(self):
        self.spikewindow = QInputDialog.getInt(self, "Analysis Configuration", "Select window over which to sum spikes. ", self.spikewindow[0])

    def set_threshold(self):
        self.threshold = QInputDialog.getInt(self, "Analysis Configuration", "Select threshold amplitude for spike detection.", self.threshold[0])


    def get_filter_config(self):
        self.filterfrequency = QInputDialog.getInt(self, "Filter Configuration", "Select the low pass filter frequency", self.filterfrequency[0])
        print "filter frequency: " + str(self.filterfrequency)

    def alter_markers(self):
        print "Alter markers"
        self.recording.alter_markers(self.ui, self.ui.actionAlter_Markers.isChecked())

    def show_markers(self):
        print "Show Markers"


    def showAxis(self):
        print ("Setting show axis to: " + str(self.ui.actionShow_Axes.isChecked()))
        self.recording.showAxis(self.ui, self.ui.actionShow_Axes.isChecked())

    def autoanalysis(self):
        signals = [self.recording.signals[0], self.recording.signals[len(self.recording.signals)-1]]
        print "Doing automatic analysis using spike counting..."
        widget = QWidget(self.ui.tabWidget)

        widget.fig = Figure((5.0, 4.0), dpi=100)
        widget.canvas = FigureCanvas(widget.fig)
        widget.canvas.setParent(widget)
        widget.canvas.setFocusPolicy(Qt.StrongFocus)
        widget.canvas.setFocus()
        widget.mpl_toolbar = NavigationToolbar(widget.canvas, widget)
        widget.canvas.mpl_connect('key_press_event', self.on_key_press)

        vbox = QVBoxLayout()
        vbox.addWidget(widget.canvas)  # the matplotlib canvas
        vbox.addWidget(widget.mpl_toolbar)
        widget.setLayout(vbox)
        filestring = QString(self.recording.filename)
        self.ui.tabWidget.addTab(widget, filestring)
        self.prop_times = Autoanalysis(signals)
        self.prop_times.analyse(self.threshold[0], self.spikewindow[0])
        self.prop_times.plot(widget)

    def multianalysis(self):
        print "analysing multiple files, outputing to csv file."
        folderName = QFileDialog.getExistingDirectory(self, "", 'Select directory containing data' )
        print folderName
        onlyfiles = [f for f in listdir(str(folderName)) if isfile(join(str(folderName), f)) and splitext(str(folderName) + f )[1] == ".abf"]
        onlyfiles = sorted(onlyfiles)
        print onlyfiles
        proptimes = []
        method, ok = QInputDialog.getText(self, 'Input Dialog',
            'What was the preparation method?')
        output = "Slice\t Time\t propagation_time\t condition\t abs_prop\t Method\n"

        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(len(onlyfiles))
        x = 0
        self.ui.progressBar.setValue(x)
        for filename in onlyfiles:
            x = x + 1
            recording = neo.io.AxonIO(str(folderName) + "/" + filename)
            bl = recording.read_block(lazy=False, cascade=True)
            signals = [None] * 2
            signals[0] = bl.segments[0].analogsignals[0]
            signals[1] = bl.segments[0].analogsignals[15]
            propanalysis = Autoanalysis(signals)
            proptimes.append(propanalysis.analyse(self.threshold[0], self.spikewindow[0]))
            day = filename[0:2]
            month = filename[2:4]
            year = filename[4:6]
            date = day + "-" + month + "-" + year
            output = output + propanalysis.get_results(filename[8], filename[10], date, method)
            self.ui.progressBar.setValue(x)
            del signals
            del propanalysis
            gc.collect()
        f = open(str(folderName)+".csv", 'w')
        f.write(output)
        f.close()
        print "Written \n" + output + " to " + str(folderName)+".csv"
        del output

    def importData(self):
        print "Import pushed"
        fileName = QFileDialog.getOpenFileName(self, 'Open data file', "", "Axon Binary Files (*.abf);; Spike 2 files(*.smr)")
        print ("Opened file" + fileName)
        widget = QWidget(self.ui.tabWidget)
        widget.fig = Figure((5.0, 4.0), dpi=100)
        widget.canvas = FigureCanvas(widget.fig)
        widget.canvas.setParent(widget)
        widget.canvas.setFocusPolicy(Qt.StrongFocus)
        widget.canvas.setFocus()
        widget.mpl_toolbar = NavigationToolbar(widget.canvas, widget)
        widget.canvas.mpl_connect('key_press_event', self.on_key_press)
        vbox = QVBoxLayout()
        vbox.addWidget(widget.canvas)  # the matplotlib canvas
        vbox.addWidget(widget.mpl_toolbar)
        widget.setLayout(vbox)
        filestring = QString(fileName)
        self.ui.tabWidget.addTab(widget, filestring)
        self.ui.tabWidget.removeTab(0)
        self.recording = None
        gc.collect()
        self.recording = RecordingData(self.ui, str(fileName), widget)
        self.recording.drawplot(self.ui, self.filterfrequency[0])


    def on_key_press(self, event):
        print('you pressed', event.key)

    # implement the default mpl key press events described at
    # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts


if __name__ == "__main__":
    app = QApplication(argv)
    window = Main()
    window.show()
    app.exec_()
    exit()
