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

#include <gr_hdlc_correlator.h>
#include <gr_io_signature.h>
#include <assert.h>
#include <stdexcept>
#include <gr_count_bits.h>
#include <stdio.h>

gr_hdlc_correlator_sptr gr_make_hdlc_correlator (gr_msg_queue_sptr target_queue, bool descramble /*= true*/) {
  return gr_hdlc_correlator_sptr (new gr_hdlc_correlator (target_queue, descramble));
}

gr_hdlc_correlator::gr_hdlc_correlator (gr_msg_queue_sptr target_queue, bool descramble /*= true*/)
  : gr_sync_block ("hdlc_correlator",
    gr_make_io_signature (1,1,sizeof (float)),
    gr_make_io_signature (0,0,0)),
	d_descramble(descramble)
{
        d_target_queue=target_queue;
        d_state=ST_LOOKING;
        d_bblen=(MAX_PACLEN+1)*BITS_PER_BYTE;
        d_bitbuf=new unsigned char [d_bblen];
        d_pktbuf=new unsigned char [MAX_PACLEN+1];
        d_bbi=0;
        d_avg=0.0;
        samplecounter=0;
        enter_looking();
}

gr_hdlc_correlator::~gr_hdlc_correlator() {
  delete [] d_bitbuf;
}
   
void gr_hdlc_correlator::enter_looking () {
  d_state=ST_LOOKING;
  for (int i=0;i<OVERSAMPLE;i++) {
    d_shift_reg[i]=0;
	lastbit[i]=0;
    d_g3ruh_desc[i]=0;
  }
  for (int i=0;i<AVG_PERIOD;i++) d_avgbuf[i]=0.0;
  d_osi=0;
  d_avbi=0;
  if (d_descramble)	// FIXME: Should have another multiplier variable for this
    d_avg=d_avg*0.5;
  d_accum=0;
#ifdef VERBOSE
  printf(">>> enter_looking d_avg:%f\n",d_avg);
#endif
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

static void packit (unsigned char *pktbuf, const unsigned char *bitbuf, int bitcount) {
  for (int i=0;i<bitcount;i++) pktbuf[i/8]=(pktbuf[i/8]>>1)|(bitbuf[i]<<7);
#ifdef VERBOSE
  for (int i=0;i<bitcount/8;i++) printf("%d %2x %c\n",i,pktbuf[i],pktbuf[i]>>1);
#endif
}

void gr_hdlc_correlator::update_avg(float x) {
  d_accum-=d_avgbuf[d_avbi];
  d_avgbuf[d_avbi]=x;
  d_accum+=x;
  d_avbi=(d_avbi+1)&(AVG_PERIOD-1);
}

char gr_hdlc_correlator::descrambler(char decision,int osi) {
  //G3RUH descrambler x=1+x12+x17
  d_g3ruh_desc[osi]=(d_g3ruh_desc[osi]<<1)|decision;
  return ((decision&0x01)^((d_g3ruh_desc[osi]>>5)&0x01)^((d_g3ruh_desc[osi]>>17)&0x01));
}

char *gr_hdlc_correlator::char2bin(char a) {
    static char str[9];
    int cnt=7;
    while (cnt > -1) {
        str[cnt--]=(a & 0x01)?'1':'0';
        a>>=1;
    } 
    return str;
} 
  
int gr_hdlc_correlator::work (int noutput_items,
				    gr_vector_const_void_star &input_items,
				    gr_vector_void_star &output_items)
{
  const float *in = (const float *) input_items[0];
 
  int n=0;
  int decision;
  int hamming_dist;
  int bit;

  while (n<noutput_items) {
    switch (d_state) {
        case ST_LOCKED_FLAG_IN:
            if (d_osi==d_center_osi) {
				if (d_descramble) {
                	d_bitbuf[d_bbi]=descrambler(slice(in[n]),d_center_osi);
				}
				else {
					d_bitbuf[d_bbi]=(lb==slice(in[n]))?1:0;
					lb=slice(in[n]);
				}
#ifdef VERBOSE
                printf("%d %d\n",samplecounter,d_bitbuf[d_bbi]);
#endif
                byte=(byte>>1)|(d_bitbuf[d_bbi]<<7);
                d_bbi++;
                if (d_bbi==8) {
                    if (byte==FLAG) {
                        d_bbi=0;
                        byte=0;
                        flagcounter++;
                    }
                    else {
#ifdef VERBOSE
                        printf("End of Start Flags (after %d flags got %x)\n",flagcounter,byte);
                        printf(">>> enter_locked\n");
#endif
                        ones=0;
                        d_state=ST_LOCKED;
                    }
                }
            }
            break;
        case ST_LOCKED:
	        if (d_osi==d_center_osi) {
				if (d_descramble) {
                	bit=descrambler(slice(in[n]),d_center_osi);
				}
				else {
					bit=(lb==slice(in[n]))?1:0;
					lb=slice(in[n]);
				}
                if (ones==5) {
                    if (bit==0) {
                        //destuffing, throw bit
#ifdef VERBOSE
                        printf("%d %d DESTUFFING\n",samplecounter,bit);
#endif
                    }
                    else {
                        //got end flag
                        d_bbi-=6;
#ifdef VERBOSE
                        printf("Got whole packet (%d bits)\n",d_bbi);
#endif
                        if (d_bbi%8 || d_bbi<MIN_PACLEN_BITS) {
#ifdef VERBOSE
                            printf("Packet discarded\n");
#endif
                            enter_looking();      //either odd bits or less than min
                        }
                        else {
                            bytes=d_bbi/BITS_PER_BYTE;
                            flagcounter=1;
                            packit(d_pktbuf, d_bitbuf, d_bbi);
                            unsigned short gfcs = d_pktbuf[bytes-1];
                            gfcs=(gfcs<<8)|d_pktbuf[bytes-2];
                            unsigned short cfcs = checkfcs(d_pktbuf,bytes);
                            printf("CRC %X %X\n",gfcs,cfcs);
                            if (gfcs==cfcs) {
                                bytes-=2;
                                gr_message_sptr msg=gr_make_message(0,0,0,bytes);  	    
                                memcpy(msg->msg(),d_pktbuf,bytes);
                                d_target_queue->insert_tail(msg);
                                msg.reset();
                            }
                            d_state=ST_LOCKED_FLAG_OUT;
                            //still missing last bit of flag, prepare vars for getting it
                            d_bbi=7;
                            byte=0xfc;
#ifdef VERBOSE
                            printf(">>> enter_locked_flag_out\n");
#endif
                        }
                    }
                }
                else {
                    d_bitbuf[d_bbi]=bit;
#ifdef VERBOSE
                    printf("%d %d\n",samplecounter,d_bitbuf[d_bbi]);
#endif
                    d_bbi++;
                }
                if (bit==1) ones++;
                else ones=0;
            }
            break;
        case ST_LOCKED_FLAG_OUT:
            if (d_osi==d_center_osi) {
				if (d_descramble) {
                	d_bitbuf[d_bbi]=descrambler(slice(in[n]),d_center_osi);
				}
				else {
					d_bitbuf[d_bbi]=(lb==slice(in[n]))?1:0;
					lb=slice(in[n]);
				}
#ifdef VERBOSE
                printf("%d %d\n",samplecounter,d_bitbuf[d_bbi]);
#endif
                byte=(byte>>1)|(d_bitbuf[d_bbi]<<7);
                d_bbi++;
                if (d_bbi==8) {
                    if (byte==FLAG) flagcounter++;
                    else {
#ifdef VERBOSE
                        printf("End of Tail Flags (after %d flags got %x)\n",flagcounter,byte);
#endif
                        enter_looking();

                    }
                    d_bbi=0;
                    byte=0;
                }
            }
            break;
        case ST_LOOKING:
        case ST_UNDER_THRESHOLD:
            update_avg(in[n]);
			if (d_descramble) {
            	decision=slice(in[n]);
			}
			else {
				decision=(slice(in[n])==lastbit[d_osi])?1:0;
				lastbit[d_osi]=slice(in[n]);
			}
            d_shift_reg[d_osi]=(d_shift_reg[d_osi]<<1)|descrambler(decision,d_osi);
            hamming_dist=gr_count_bits8(d_shift_reg[d_osi]^FLAG);
#ifdef VERBOSE
            printf("%d %f %2x %s %2d  %d\n",samplecounter, in[n],d_shift_reg[d_osi],char2bin(d_shift_reg[d_osi]),hamming_dist, d_osi);
#endif
            if (d_state==ST_LOOKING && hamming_dist<=THRESHOLD) {
#ifdef VERBOSE
                printf(">>> enter_under_threshold  d_osi= %d\n",d_osi);
#endif
                d_state=ST_UNDER_THRESHOLD;
                d_transition_osi=d_osi;
            }
            else if (d_state==ST_UNDER_THRESHOLD && hamming_dist>THRESHOLD) {
                d_state=ST_LOCKED_FLAG_IN;
                int delta=sub_index(d_osi,d_transition_osi);
                if (delta==0) delta=8;
                d_center_osi=add_index(d_transition_osi,delta/2);
                d_bbi=0;
#ifdef VERBOSE
                printf(">>> enter_locked_flag_in  d_center_osi = %d d_osi = %d\n",d_center_osi,d_osi);
#endif
                d_avg = std::max(-1.0, std::min(1.0, d_accum * (1.0/AVG_PERIOD)));
#ifdef VERBOSE
                printf(">>> enter_locked_flag_in  d_avg = %g\n", d_avg);
#endif
                byte=0;
                lb=lastbit[d_center_osi];
                flagcounter=0;
            }
            break;
        default:
            assert(0);
    }  
    d_osi=add_index(d_osi,1);
    samplecounter++;
    n++;
  }
  return noutput_items;
}
