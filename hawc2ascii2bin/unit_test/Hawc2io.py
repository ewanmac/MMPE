# -*- coding: utf-8 -*-
"""
Author:     
    Bjarne S. Kallesoee
    bska@risoe.dtu.dk

Description: 
    Reads all HAWC2 output data formats, HAWC2 ascii, HAWC2 binary and FLEX
    
call ex.:   
    # creat data file object, call without extension, but with parth 
    file = ReadHawc2("HAWC2ex/test")
    # if called with ReadOnly = 1 as
    file = ReadHawc2("HAWC2ex/test",ReadOnly=1)
    # no channels a stored in memory, otherwise read channels are stored for reuse    

    # channels are called by a list
    file([0,2,1,1])  => channels 1,3,2,2
    # if empty all channels are returned
    file()  => all channels as 1,2,3,... 
    file.t => time vector
    
1. version: 19/4-2011

Need to be done:
    * add error handling for allmost every thing

"""
import numpy as np
import os
################################################################################    
################################################################################    
################################################################################    
## Read HAWC2 class
################################################################################    
class ReadHawc2:
    """
    Class title
    ===========
    
    Class documentation docstring
    
    class subtitle
    --------------
    and more...
    
    """
################################################################################    
# read *.sel file
    def _ReadSelFile(self):
        """
        Some title
        ==========
        
        Using docstrings formatted according to the reStructuredText specs
        can be used for automated documentation generation with for instance
        Sphinx: http://sphinx.pocoo.org/. 
        
        Parameters
        ----------
        signal : ndarray
            some description
        
        Returns
        -------
        output : int
            describe variable
        """
        
        # read *.sel hawc2 output file for result info
        fid = open(self.FileName + '.sel', 'r')
        Lines = fid.readlines()
        fid.close()
        # findes general result info (number of scans, number of channels, 
        # simulation time and file format)
        temp = Lines[8].split()
        self.NrSc = int(temp[0]); self.NrCh = int(temp[1])
        self.Time = float(temp[2]); self.Freq = self.NrSc/self.Time;
        self.t = np.linspace(0,self.Time,self.NrSc); 
        Format = temp[3]
        # reads channel info (name, unit and description)
        Name = []; Unit = []; Description = [];
        for i in range(0,self.NrCh):
            temp = str(Lines[i+12][12:43]); Name.append(temp.strip())  
            temp = str(Lines[i+12][12:43]); Unit.append(temp.strip())
            temp = str(Lines[i+12][12:43]); Description.append(temp.strip())
        self.ChInfo = [Name,Unit,Description]
        # if binary file format, scaling factors are read
        if Format.lower() == 'binary':
            self.ScaleFactor = np.zeros(self.NrCh)
            self.FileFormat = 'HAWC2_BINARY'
            for i in range(0,self.NrCh):
                self.ScaleFactor[i] = float(Lines[i+12+self.NrCh+2])
        else:
            self.FileFormat = 'HAWC2_ASCII'
################################################################################    
# read sensor file for FLEX format
    def _ReadSensorFile(self):
        # read sensor file used if results are saved in FLEX format
        DirName = os.path.dirname(self.FileName + ".int")
        try:
            fid = open(DirName + "\sensor ", 'r')
        except IOError:
            print "can't finde sensor file for FLEX format"
            return
        Lines = fid.readlines()
        fid.close()
        # reads channel info (name, unit and description)
        self.NrCh = 0
        Name = []; Unit = []; Description = [];
        for i in range(2,len(Lines)):
            temp = Lines[i]
            if not temp.strip():
                break
            self.NrCh += 1
            temp = str(Lines[i][38:45]); Unit.append(temp.strip())
            temp = str(Lines[i][45:53]); Name.append(temp.strip())  
            temp = str(Lines[i][53:]); Description.append(temp.strip())
        self.ChInfo = [Name,Unit,Description]
        # read general info from *.int file
        fid = open(self.FileName + ".int", 'rb')
        fid.seek(4*19)
        if not np.fromfile(fid,'int32',1) == self.NrCh:
            print "number of sensors in sensor file and data file are not consisten"
        fid.seek(4*(self.NrCh)+8,1)
        temp = np.fromfile(fid,'f',2)
        self.Freq = 1/temp[1];   
        self.ScaleFactor = np.fromfile(fid,'f',self.NrCh)
        fid.seek(2*4*self.NrCh+48*2)
        self.NrSc = len(np.fromfile(fid,'int16'))/self.NrCh
        self.Time = self.NrSc*temp[1]
        self.t = np.arange(0,self.Time,temp[1])
        fid.close()        
################################################################################    
# init function, load channel and other general result file info
    def __init__(self,FileName,ReadOnly=0):
        self.FileName = FileName
        self.ReadOnly = ReadOnly
        self.Iknown = [] # to keep track of what has been read all ready
        self.Data = np.zeros(0)
        if os.path.isfile(FileName + ".sel"):
             self._ReadSelFile()
        elif os.path.isfile(self.FileName + ".int"):
             self.FileFormat = 'FLEX'
             self._ReadSensorFile()
        else:
            print "unknown file: "+FileName
################################################################################    
# Read results in binary format
    def ReadBinary(self,ChVec=[]):
        if not ChVec:
            ChVec = range(0,self.NrCh)
        fid = open(self.FileName + '.dat', 'rb')
        data = np.zeros((self.NrSc,len(ChVec))); j=0
        for i in ChVec:
            fid.seek(i*self.NrSc*2,0)
            data[:,j] = np.fromfile(fid,'int16',self.NrSc)*self.ScaleFactor[i]
            j += 1
        return data
################################################################################    
# Read results in ASCII format
    def ReadAscii(self,ChVec=[]):
        if not ChVec:  
            ChVec = range(0,self.NrCh)
        temp = np.loadtxt(self.FileName + '.dat',usecols=ChVec)
        return temp.reshape((self.NrSc,len(ChVec)))
################################################################################    
# Read results in FLEX format
    def ReadFLEX(self,ChVec=[]):
        if not ChVec:
            ChVec = range(1,self.NrCh)
        fid = open(self.FileName + ".int", 'rb')
        fid.seek(2*4*self.NrCh+48*2)
        temp = np.fromfile(fid,'int16')
        temp = temp.reshape(self.NrSc,self.NrCh)
        fid.close()        
        return np.dot(temp[:,ChVec],np.diag(self.ScaleFactor[ChVec]))
################################################################################    
# One stop call for reading all data formats
    def ReadAll(self,ChVec=[]):
        if not ChVec:
            ChVec = range(0,self.NrCh)
        if self.FileFormat == 'HAWC2_BINARY':
            return self.ReadBinary(ChVec)
        elif self.FileFormat == 'HAWC2_ASCII':
            return self.ReadAscii(ChVec)
        else:
            return self.ReadFLEX(ChVec)
################################################################################    
# Main read data call, read, save and sort data
    def __call__(self,ChVec=[]):
        if not ChVec:
            ChVec = range(0,self.NrCh)
        elif max(ChVec) >= self.NrCh:
            print "to high channel number"
            return
        # if ReadOnly, read data but no storeing in memory    
        if self.ReadOnly:
            return self.ReadAll(ChVec)
        # if not ReadOnly, sort in known and new channels, read new channels 
        # and return all requested channels 
        else:
            # sort into known channels and channels to be read
            I1=[];I2=[] # I1=Channel mapping, I2=Channels to be read
            for i in ChVec:
                try:
                    I1.append(self.Iknown.index(i))
                except:
                    self.Iknown.append(i)
                    I2.append(i)
                    I1.append(len(I1))
            # read new channels
            if I2:
                temp = self.ReadAll(I2)
                # add new channels to Data
                if self.Data.any():
                    self.Data = np.append(self.Data,temp,axis=1)
                # if first call, so Daata is empty
                else:                    
                    self.Data = temp
            return self.Data[:,tuple(I1)]
 

################################################################################    
################################################################################    
################################################################################    
## write HAWC2 class, to be implemented
################################################################################    

if __name__ == '__main__':
    res_file = Hawc2io.ReadHawc2('structure_wind')
    results = res_file.ReadAscii()
    channelinfo = res_file.ChInfo
