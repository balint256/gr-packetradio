/* -*- c++ -*- */
/*
 * Copyright 2004 Free Software Foundation, Inc.
 * 
 * This file is part of GNU Radio
 * 
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 * 
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_hdlc_framer.h>
#include <gr_io_signature.h>
#include <assert.h>
#include <stdexcept>
#include <stdio.h>

//#define VERBOSE

gr_hdlc_framer_sptr gr_make_hdlc_framer (gr_msg_queue_sptr target_queue, bool mode) {
  return gr_hdlc_framer_sptr (new gr_hdlc_framer (target_queue, mode));
}

gr_hdlc_framer::gr_hdlc_framer (gr_msg_queue_sptr target_queue, bool mode)
  : gr_sync_block ("hdlc_framer",
	gr_make_io_signature (1, 1, sizeof (unsigned char)),
	gr_make_io_signature (0,0,0)) {
		gr_hdlc_framer::mode=mode;
		gr_hdlc_framer::target_queue=target_queue;
		state=STARTFLAG;
		pktbuf=new unsigned char [MAX_PACKET_LEN];
		sr=0;
		prevbit=0;
		descr=0;
}

static unsigned short checkfcs(unsigned char *pktbuf, int bytecount) {
    unsigned short fcs=0xFFFF;
    for (int i=0; i<bytecount-2; i++) {
        fcs = fcs ^ *pktbuf++;
        for (int k=0;k<8;k++) {
            if (fcs & 0x01) fcs = (fcs >> 1) ^ 0x8408;
            else fcs>>=1;
        }
    }
    return(fcs^0xFFFF);
}

static char* int2bin(int a) {
    static char str[64];
    int cnt=15;
    while (cnt > -1) {
        str[cnt--]=(a & 0x01)?'1':'0';
        a>>=1;
    } 
    return str;
} 

static char* char2bin(char a) {
    static char str[64];
    int cnt=7;
    while (cnt > -1) {
        str[cnt--]=(a & 0x01)?'1':'0';
        a>>=1;
    } 
    return str;
} 

int gr_hdlc_framer::work (int noutput_items,
				    gr_vector_const_void_star &input_items,
				    gr_vector_void_star &output_items) {
  const unsigned char *in = (const unsigned char *) input_items[0];
  
  int n=0;
  while (n < noutput_items){
  	bit=*in;
  	if (mode) {
  		rbit=((descr>>11) & 1) ^ ((descr>>16) & 1) ^ bit;		//LFSR descrambling
  		descr<<=1;
  		descr|=bit;
  		bit=rbit;
  	}

  	if (prevbit==bit) rbit=1;									//NRZI decoding
  	else rbit=0;
  	prevbit=bit;

#ifdef VERBOSE
//printf("Got %d (%d)\n",rbit,bit);
#endif 
  	
	switch (state) {
		case STARTFLAG:			//looking for start of head flags
			sr>>=1;
			if (rbit==1) sr|=0x80;
			if (sr==FLAG) {
				state=PACKET;
				bitctr=0;
				flagctr=1;
#ifdef VERBOSE
//printf("Start of Head Flags Found\n");
#endif 				
			}
			break;
		case PACKET:			//looking for packet start (end of head flags)
			sr>>=1;
			if (rbit==1) sr|=0x80;
			bitctr++;
			if (bitctr==8) {
				bitctr=0;
				if (sr!=FLAG) {
					state=ENDFLAG;
					pktptr=pktbuf;
					*pktptr=sr;
					pktptr++;
					bytectr=1;
					ones=0;
#ifdef VERBOSE
printf("Start of Packet Found %02X after %d FLAGS\n",sr,flagctr);
#endif					
				}
				else {
					flagctr++;
#ifdef VERBOSE
printf("Got FLAG\n");
#endif						
				}
			}
			break;
		case ENDFLAG:					//looking for start of tail flags
			if (ones==5) {
				if (rbit==0) {	//destuffing
#ifdef VERBOSE					
printf ("DESTUFFING!!!\n");
#endif
				}
				else {					//6 bits in a row - FLAG!
					state=LASTFLAGBIT;	//we need to consume one more bit (last 0 of the flag)
#ifdef VERBOSE
printf("End of Packet Found (%d bytes)\n",bytectr);
#endif
					if (bytectr>=MIN_PACKET_LEN) {					//check CRC and if OK send to out queue
						unsigned short gfcs = pktbuf[bytectr-1];
                        gfcs=(gfcs<<8)|pktbuf[bytectr-2];
                        unsigned short cfcs = checkfcs(pktbuf,bytectr);
                        if (gfcs==cfcs/*true*/) {
                        	//printf("\nCRC %X %X\n",gfcs,cfcs);
                            bytectr-=2;
                            gr_message_sptr msg=gr_make_message(0,0,0,bytectr);  	    
                            memcpy(msg->msg(),pktbuf,bytectr);
                            target_queue->insert_tail(msg);
                            msg.reset();
                        }
                        else {
                        	printf("X");
                        	fflush(stdout);
                        }
					}
				}
			}
			else {
				*pktptr>>=1;
				if (rbit==1) *pktptr|=0x80;
				bitctr++;
				if (bitctr==8) {
					bitctr=0;
#ifdef VERBOSE
printf("Got BYTE %02X %s (%d)\n",*pktptr,char2bin(*pktptr),bytectr);
#endif						
					pktptr++;
					bytectr++;
				}
			}	
			if (rbit==1) ones++;
			else ones=0;
			break;
		case LASTFLAGBIT:		//just consume a bit
			state=END;
			sr=0;
			bitctr=0;
			break;
		case END:				//looking for end of tail flags
			sr>>=1;
			if (rbit==1) sr|=0x80;
			bitctr++;
			if (bitctr==8) {
				bitctr=0;
				if (sr!=FLAG) {
					state=STARTFLAG;
					sr=0;			
#ifdef VERBOSE
printf("End of Tail Flags Found\n");
#endif					
				}
				else {
#ifdef VERBOSE
//printf("Got FLAG\n");
#endif						
				}
			}
			break;
	}
	in++;
    n++;
  }
  return n;
}
