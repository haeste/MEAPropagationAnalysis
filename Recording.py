import neo.io
import numpy
import matplotlib
import matplotlib.widgets
import matplotlib.pyplot as plt

from lowpass import lowpass


class RecordingData:
    # ui - user interface object
    # filename - name of datafile
    # widget - mplwidget used for plotting data
    def __init__(self, ui, filename, widget):
        self.filename = filename
        self.data = []
        self.signals = []
        self.t = []
        matplotlib.rc('xtick', labelsize=8)
        matplotlib.rc('ytick', labelsize=8)
        font = dict(family='normal', weight='normal', size=8)
        matplotlib.rc('font', **font)
        self.ui = ui
        self.widget = widget
        self.datalines = []
        self.fitlines = []
        self.fitpoints = []
        self.start = 0
        self.end = 0
        self.loadfile(filename)
        self.cursors = [None] * (len(self.signals) + 1)
        self.buttons = [None] * (len(self.signals) + 1)
        self.axes = [None] * (len(self.signals) + 1)
        self.markerlines = [None] * (len(self.signals) + 1)
        self.cid = 0
        textstr = "Time difference:" + str(self.get_speed())
        self.props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        self.speedtext = self.widget.fig.text(0.05, 0.95, textstr, fontsize=14,
                                                 verticalalignment='top', bbox=self.props)


    # Load datafile into memory using neo library
    def loadfile(self, fileName):
        print ("Loading " + fileName)
        #for axon binary file
        if fileName.endswith('.abf'):
            r = neo.io.AxonIO(fileName)
            bl = r.read_block(lazy=False, cascade=True)
            self.signals = bl.segments[0].analogsignals # read first block which contains all data for abf files
        #for spike 2 file
        elif fileName.endswith('smr'):
            r = neo.io.Spike2IO(fileName)
            self.signals = r.read_segment().analogsignals

        self.t = numpy.linspace(1, self.signals[0].sampling_rate.magnitude, len(self.signals[0])) # create an x axis for the data
        print ("Data loaded")
        # set info boxes in gui to start and end of datafile
        self.end = len(self.signals[0]) * (1 / self.signals[0].sampling_rate.magnitude)



    # method to add or remove axis from display
    def showAxis(self, ui, isChecked):
        for x in range(1, (len(self.signals) + 1)):
            if isChecked:
                self.axes[x].set_axis_on()
            else:
                self.axes[x].set_axis_off()
        self.widget.canvas.draw()

    # incomplete method -- does nothing
    def remove_data(self, ui):
        for x in range(1, (len(self.datalines))):
            print "removing: {0}".format(str(x))

        self.widget.canvas.draw()

    # show the markers used for manual measuring of propagation
    def show_markers(self, ui):
        for x in range(1, (len(self.signals) + 1)):
            print "axes: " + str(self.axes[x])
            self.markerlines[x] = self.axes[x].vlines(self.fitpoints[x - 1], self.axes[x].get_ylim()[0],
                                                      self.axes[x].get_ylim()[1],
                                                      colors='k', linestyles='solid', label="wave:" + str(x))
        self.widget.canvas.draw()

    # Called when the alter markers box has been ticked by the user indicating that they
    # wish to manually set the markers to measure propagation.
    # Adds the event lister method set_marker to the button pressed event so that
    # when the user clicks on the mplwidget a marker will be drawn at that location.
    def alter_markers(self, ui, alter):
        if alter:
            for x in range(1, (len(self.signals) + 1)):
                self.cursors[x] = matplotlib.widgets.Cursor(self.axes[x], horizOn=False, vertOn=True, useblit=False)
                #self.buttons[x] = matplotlib.widgets.Button(self.axes[x], label="", image=None, color='0.85',
                #hovercolor='0.95')
                #self.buttons[x].on_clicked(self.set_marker)
            self.cid = self.widget.fig.canvas.mpl_connect('button_press_event', self.set_marker)
        else:
            for x in range(1, (len(self.signals) + 1)):
                self.cursors[x] = None
                #self.buttons[x] = None
            self.widget.fig.canvas.mpl_disconnect(self.cid)

        self.widget.canvas.draw()

    # called by the button pressed event after alt
    def set_marker(self, event):
        print str(event)
        axes_index = 0
        for x in range(1, (len(self.signals) + 1)):
            if event.inaxes == self.axes[x]:
                print "axes is : " + str(x)
                axes_index = x
        self.fitpoints[axes_index - 1] = event.xdata
        print str(self.markerlines[axes_index])
        self.markerlines[axes_index].remove()
        print str(self.markerlines[axes_index])

        self.markerlines[axes_index] = self.axes[axes_index].vlines(self.fitpoints[axes_index - 1],
                                                                    self.axes[axes_index].get_ylim()[0],
                                                                    self.axes[axes_index].get_ylim()[1], colors='k',
                                                                    linestyles='solid',
                                                                    label="wave:" + str(axes_index))
        textstr = "Time difference: " + str(self.get_speed()) + " seconds"
        print textstr
        self.speedtext.set_text(textstr)
        self.widget.canvas.draw()

        print "setting maker"

    def get_speed(self):
        if len(self.fitpoints) <= 0:
            return []

        return (self.fitpoints[0]/self.signals[0].sampling_rate.magnitude - self.fitpoints[15]/self.signals[0].sampling_rate.magnitude)

    def drawplot(self, ui,  filterfrequency):
        start = float(self.start)
        stop = float(self.end)
        print "start: " + str(start)
        print "stop: " + str(self.end)
        left = start
        right = stop

        matplotlib.pyplot.autoscale(enable=True, axis='both', tight=True)
        xlabel = "Time (s)"
        print xlabel
        ui.progressBar.setMinimum(0)
        ui.progressBar.setMaximum(len(self.signals))
        mplwidget = self.widget
        mplwidget.fig.clear()

        # plot signal from each channel
        for x in range(1, (len(self.signals) + 1)):

            # add subplot and set axes and scale
            self.axes[x] = mplwidget.fig.add_subplot(len(self.signals), 1, x, sharex=self.axes[1])
            self.axes[x].set_xlim(left, right)
            self.axes[x].autoscale(enable=True, axis='y', tight=True)

            v = self.signals[x - 1][:].magnitude # signal to plot
            print "SAMPLING RATE: " + str(len(self.signals[x - 1])/self.signals[x-1].sampling_rate.magnitude)
            self.t = numpy.linspace(1, len(self.signals[x - 1])/self.signals[x-1].sampling_rate.magnitude, num=len(self.signals[x - 1]))
            self.t = self.t[:]
            print len(self.t)
            if self.ui.actionFilter.isChecked():
                v = lowpass(v, self.signals[x - 1].sampling_rate.magnitude, filterfrequency)

            if self.ui.actionAbsolute_Value_2.isChecked():
                v = numpy.absolute(v)
            matplotlib.pyplot.plot(self.t, v)
            self.datalines.append(self.axes[x].plot(self.t, v))
            self.fitpoints.insert(x, 1)

            #for all plots but the final plot
            if x < len(self.signals):
                matplotlib.artist.setp(self.axes[x].get_xticklabels(), visible=False)  #don't draw x ticks

            #for only the final plot
            if x >= len(self.signals):
                self.axes[x].set_xlabel(xlabel)

            if not ui.actionShow_Axes.isChecked():
                self.axes[x].set_axis_off()
            elif ui.actionShow_Axes.isChecked():
                self.axes[x].set_axis_on()

            self.axes[x].set_ylabel(str(self.signals[x - 1].name))

            max_yticks = 2
            yloc = plt.MaxNLocator(max_yticks)
            self.axes[x].yaxis.set_major_locator(yloc)
            ui.progressBar.setValue(x)


        self.show_markers(ui)
        matplotlib.pyplot.autoscale(enable=True, axis='both', tight=True)
        textstr = ""
        self.speedtext = self.widget.fig.text(0.05, 0.95, textstr, fontsize=14,
                                                 verticalalignment='top', bbox=self.props)
        mplwidget.canvas.draw()
        ui.progressBar.setValue(len(self.signals))