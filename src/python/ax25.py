#!/usr/bin/env python
# Originally from http://digilander.libero.it/iz2eeq/

#import threading
import gnuradio.gr.gr_threading as _threading

# FIXME: Make these local
mark=1
space=-1
out=[]
flag=False
fcs=False
stuff=0
fcslo=0
fcshi=0

def nrziencode(bitarr):
    outbit=1
    outarr=[]
    for bit in bitarr:
        if bit==0:
            outbit=(~outbit)&1
            outarr.append(outbit)
        else:
            outarr.append(outbit)
    return outarr

def nrzidecode(bitarr):
    prevbit=0
    outarr=[]
    for bit in bitarr:
        if bit==prevbit:
            outarr.append(1)
        else:
            outarr.append(0)
        prevbit=bit
    return outarr
    
def fcsbit(bit):
    global fcshi,fcslo
    b1=fcshi&0x01
    fcshi>>=1
    b2=fcslo&0x01
    fcslo>>=1
    fcslo|=(b1<<7)
    if b2 != bit:
        fcshi=fcshi^0x84
        fcslo=fcslo^0x08

def sendbyte(byte):
    global stuff
    for k in range(8): 
        bt=byte & 0x01
        if not fcs and not flag: fcsbit(bt)
        if bt==0:
            stuff=0
            out.append(0)
        else :
            stuff+=1
            out.append(1)
            if not flag and stuff==5:
                stuff=0
                out.append(0)
        byte>>=1
        
def pbits(number):
    bstring=''
    for i in range(8):
        bstring+=chr(((number>>(7-i)) & 1)+0x30)
    return bstring
        
def dumppacket(pkt):
    print "length: %d\n" % len(pkt)
    for byte in pkt:
        print "%02x %s %c" % (byte,pbits(byte),byte)

def printpacket(pkt):
    string=""
    idx=0
    v1=1
    lun=len(pkt)
    if lun<8:
        return "ERROR: Packet can't be shorter than 8 bytes (%u)" % len(pkt)
    if (ord(pkt[idx+1]) & 0x01):
        #flexnet header compression
        v1=0
        cmd=(ord(pkt[idx+1]) & 2)!=0
        string="fm ? to "
        i=(ord(pkt[idx+2])>>2) & 0x3f
        if i:
            string+=chr(i+0x20)
        i = ((ord(pkt[idx+2]) << 4) | ((ord(pkt[idx+3]) >> 4) & 0xf)) & 0x3f
        if i:
			string+=chr(i+0x20)
        i = ((ord(pkt[idx+3]) << 2) | ((ord(pkt[idx+4]) >> 6) & 3)) & 0x3f
        if i:
            string+=chr(i+0x20)
        i = ord(pkt[idx+4]) & 0x3f
        if i:
            string+=chr(i+0x20)
        i = (ord(pkt[idx+5]) >> 2) & 0x3f
        if i:
            string+=chr(i+0x20)
        i = ((ord(pkt[idx+5]) << 4) | ((ord(pkt[idx+6]) >> 4) & 0xf)) & 0x3f
        if i:
            string+=chr(i+0x20)
        string+="-%u QSO Nr %u" % (ord(pkt[idx+6]) & 0xf, (ord(pkt[idx+0]) << 6) | (ord(pkt[idx+1]) >> 2))
        idx+=7
        lun-=7
    else:
        #normal header
        if lun<15:
            return "ERROR: Packet can't be shorter than 15 bytes (%u)" % len(pkt)
        if ((ord(pkt[idx+6]) & 0x80) != (ord(pkt[idx+13]) & 0x80)):
            v1=0
            cmd=(ord(pkt[idx+6]) & 0x80)
        string+="fm "
        for i in range(7,13):
            if (ord(pkt[idx+i])&0xfe)!=0x40:
                string+=chr(ord(pkt[idx+i])>>1)
        string+="-%u to " % ((ord(pkt[idx+13])>>1) & 0x0f)
        for i in range(6):
            if (ord(pkt[idx+i])&0xfe)!=0x40:
                string+=chr(ord(pkt[idx+i])>>1)
        string+="-%u" % ((ord(pkt[idx+6])>>1) & 0x0f)
        idx+=14
        lun-=14
        if (not(ord(pkt[idx-1]) & 1)) and (lun >= 7):
            string+=" via "
        while (not(ord(pkt[idx-1]) & 1)) and (lun >= 7):
            for i in range(6):
                if ((ord(pkt[idx+i])&0xfe)!=0x40):
                    string+=chr(ord(pkt[idx+i])>>1)
            string+="-%u" % (ord(pkt[idx+6])>>1 & 0x0f)
            idx+=7
            lun-=7
            if (not(ord(pkt[idx-1]) & 1)) and (lun>=7):
                string+=","
    if (lun==0):
            return string
    i=ord(pkt[idx])
    idx+=1
    lun-=1
    if v1:
        if i & 0x10:
            j="!"
        else:
            j=" "
    else:
        if i & 0x10:
            if cmd:
                j="+"
            else:
                j="-" 
        else:
            if cmd:
                j="^"
            else:
                j="v"
    if (not(i & 1)):
		#Info frame
		string+=" I%u%u%c" % ((i >> 5) & 7, (i >> 1) & 7, j)
    elif (i & 2):
		#U frame
        ii=(i & (~0x10))
        if ii==0x03:
            string+=" UI%c" % j
        elif ii==0x2f:
            string+=" SABM%c" % j
        elif ii==0x43:
            string+=" DISC%c" % j
        elif ii==0x0f:
            string+=" DM%c" % j
        elif ii==0x63:
            string+=" UA%c" % j
        elif ii==0x87:
            string+=" FRMR%c" % j
        else:
            string+=" unknown U (0x%x)%c" % (i & (~0x10), j)
    else:
        #supervisory
        ii=(i & 0xf)
        if ii==0x1:
            string+=" RR%u%c" % ((i >> 5) & 7, j)
        elif ii==0x5:
            string+=" RNR%u%c" % ((i >> 5) & 7, j)
        elif ii==0x9:
            string+=" REJ%u%c" % ((i >> 5) & 7, j)
        else:
			string+=" unknown S (0x%x)%u%c" % (i & 0xf, (i >> 5) & 7, j)
    if (lun==0):
        string+="\n"
        return string
    string+=" pid=%02X\n" % ord(pkt[idx])
    idx+=1
    lun-=1
    j=0
    while lun:
        i=ord(pkt[idx])
        idx+=1
        if (i>=32) and (i<128):
			string+=chr(i)
        elif i==13:
            if j:
                string+="\n"
            j=0
        else:
            string+="."
        if i>=32: 
            j=1
        lun-=1
    if j:
        string+="\n"
    return string

def dumppackettofile(packet,filename):
    file=open(filename,"w")
    for byte in packet:
        file.write(chr(byte))
    file.close
        
def buildpacket(source,source_ssid,dest,dest_ssid,digi,digi_ssid,control,pid,payload):
    packet=[]
    for j in range(6):
        if j<len(dest):
            c=ord(dest[j])
            packet.append(c<<1)
        else:
            packet.append(0x40)
    packet.append(0x60|(dest_ssid<<1))
    for j in range(6):
        if j<len(source):
            c=ord(source[j])
            packet.append(c<<1)
        else:
            packet.append(0x40)
    packet.append(0x60|(source_ssid<<1))
    for j in range(6):
        if j<len(digi):
            c=ord(digi[j])
            packet.append(c<<1)
        else:
            packet.append(0x40)
    packet.append(0x60|(digi_ssid<<1)|0x01)
    packet.append(control)
    packet.append(pid)
    for j in range(len(payload)):
        packet.append(ord(payload[j]))
    return packet

def scrambler(bitarr):
    scrambled=[]
    tsr=0
    for bit in bitarr:
        tbit=bit ^ ((tsr>>11)&1) ^ ((tsr>>16)&1)
        tsr=(tsr<<1)|tbit
        scrambled.append(tbit)
    return scrambled

def descrambler(bitarr):
    descrambled=[]
    rsr=0
    for bit in bitarr:
        rbit=((rsr>>11)&1) ^ ((rsr>>16)&1) ^ bit
        rsr=(rsr<<1) | bit
        descrambled.append(rbit)
    return descrambled     

def bits2syms(bitarr):
    syms=[]
    for bit in bitarr:
	if bit==0:
		syms.append(space)
	else:
		syms.append(mark)
    return syms

def array2string(array):
    outstr=''
    for el in array:
        outstr+=chr(el+0x30)
    return outstr

def array2file(array,filename):
    file=open(filename,'w')
    for el in array:
        file.write(chr(el))
    file.close()

def hdlcpacket(pak,flaghead,flagtail):
    global out,flag,fcs,stuff,fcslo,fcshi
    out=[]
    fcslo=0xff
    fcshi=0xff
    stuff=0
    flag=True
    fcs=False
    #head flags
    for i in range(flaghead): sendbyte(0x7e)
    flag=False
    #print len(pak)
    for i in range(len(pak)): sendbyte(pak[i])
    fcs=True
    fcslo=fcslo^0xff
    fcshi=fcshi^0xff
    sendbyte(fcslo)
    sendbyte(fcshi)
    fcs=False
    flag=True
    #tail flags
    for i in range(flagtail): sendbyte(0x7e)
    return out

def loadpacket(filename):
    out=[]
    f=open(filename,'r')
    buffer=f.read()
    f.close()
    for i in range(len(buffer)):
        out.append(ord(buffer[i])&1)
    return out

class queue_watcher_thread(_threading.Thread):
    def __init__(self, rcvd_pktq, callback=None):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.rcvd_pktq = rcvd_pktq
        self.callback = callback
        self.keep_running = True
        self.start()
    def stop(self):
        print "Stopping..."
        self.keep_running = False
    def run(self):
        while self.keep_running:
            msg = self.rcvd_pktq.delete_head()
            msg_str = msg.to_string()
            if self.callback:
                self.callback(msg_str)
            else:
                print printpacket(msg_str)

def sendpacket(packet):
    global out,flag,fcs,stuff,fcslo,fcshi
    out=[]
    fcslo=0xff
    fcshi=0xff
    stuff=0
    flag=True
    fcs=False
    #head flags
    for i in range(40): sendbyte(0x7e)
    flag=False
#    print len(packet)
    for i in range(len(packet)): sendbyte(packet[i])
    fcs=True
    fcslo=fcslo^0xff
    fcshi=fcshi^0xff
    sendbyte(fcslo)
    sendbyte(fcshi)
    fcs=False
    flag=True
    #tail flags
    for i in range(8): sendbyte(0x7e)
    return out

def main():
    message=":ALL      :this is a test";
    packet=buildpacket("MYCALL",1,"CQ",0,"RELAY",0,0x03,0xf0,message)
    outstream=sendpacket(packet)
    print len(outstream)
    print outstream
    
if __name__ == '__main__':
    main()
