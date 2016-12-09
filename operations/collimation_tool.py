import PyIndi
import time
import threading
from astropy.io import fits
from astropy.visualization import SqrtStretch, HistEqStretch
from astropy.visualization.mpl_normalize import ImageNormalize
import matplotlib.pyplot as plt
'''
Hacked together tool to help with collimation. Takes continuous exposures and plots the 4 corners of the image in a single plot full size. Star distortions are visible in the corners aiding collimation
'''

class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        global blobEvent
        print("new BLOB ", bp.name)
        blobEvent.set()
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass


# Constants
normalise_upper = 20000
normalise = False
exposure_time = 3
ccd="Atik 383L+ CCD"
section_size = 200

# connect the server
indiclient=IndiClient()
indiclient.setServer("localhost",7624)

if (not(indiclient.connectServer())):
    raise RuntimeError('No indiserver running')

device_ccd=indiclient.getDevice(ccd)
while not(device_ccd):
    time.sleep(0.5)
    device_ccd=indiclient.getDevice(ccd)

ccd_connect=device_ccd.getSwitch("CONNECTION")
while not(ccd_connect):
    time.sleep(0.5)
    ccd_connect=device_ccd.getSwitch("CONNECTION")

if not(device_ccd.isConnected()):
    ccd_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
    ccd_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
    indiclient.sendNewSwitch(ccd_connect)

ccd_exposure=device_ccd.getNumber("CCD_EXPOSURE")
while not(ccd_exposure):
    time.sleep(0.5)
    ccd_exposure=device_ccd.getNumber("CCD_EXPOSURE")

# we should inform the indi server that we want to receive the
# "CCD1" blob from this device
indiclient.setBLOBMode(PyIndi.B_ALSO, ccd, "CCD1")
ccd_ccd1=device_ccd.getBLOB("CCD1")
while not(ccd_ccd1):
    time.sleep(0.5)
    ccd_ccd1=device_ccd.getBLOB("CCD1")

blobEvent=threading.Event()
blobEvent.clear()
i=0
ccd_exposure[0].value=exposure_time
indiclient.sendNewNumber(ccd_exposure)
while (True):
    # wait for the ith exposure
    blobEvent.wait()
    ccd_exposure[0].value=exposure_time
    blobEvent.clear()
    indiclient.sendNewNumber(ccd_exposure)
    # and meanwhile process the received one
    for blob in ccd_ccd1:
        print("name: ", blob.name," size: ", blob.size," format: ", blob.format)
        fitsbytes=blob.getblobdata()
        print("fits data type: ", type(fitsbytes))
        with open('/tmp/tmp.fits', 'wb') as f:
            f.write(fitsbytes)
        hdulist = fits.open('/tmp/tmp.fits')
        # hdulist = fits.open('/home/dokeeffe/Desktop/2016-11-30-22-37-25Light_002.fits')
        header = hdulist[0].header
        data = hdulist[0].data
        norm = ImageNormalize(100,normalise_upper, stretch=SqrtStretch())
        nax1 = header['NAXIS1']
        nax2 = header['NAXIS2']
        # now generate a corner snippet the same size as the scaled image
        bl = data[0:section_size,0:section_size]
        tl = data[nax2-section_size:nax2,0:section_size]
        br = data[0:section_size,nax1-section_size:nax1]
        tr = data[nax2-section_size:nax2,nax1-section_size:nax1]

        # generate plot
        ax = plt.subplot(221)
        if normalise:
            plt.imshow(tl, origin='lower', norm=norm)
            plt.subplot(222)
            plt.imshow(tr, origin='lower', norm=norm)
            plt.subplot(223)
            plt.imshow(bl, origin='lower', norm=norm)
            plt.subplot(224)
            plt.imshow(br, origin='lower', norm=norm)
            plt.pause(0.05)
        else:
            plt.imshow(tl, origin='lower')
            plt.subplot(222)
            plt.imshow(tr, origin='lower')
            plt.subplot(223)
            plt.imshow(bl, origin='lower')
            plt.subplot(224)
            plt.imshow(br, origin='lower')
            plt.pause(0.05)
