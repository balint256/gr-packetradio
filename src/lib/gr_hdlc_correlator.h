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

#define VERBOSE

#ifndef INCLUDED_GR_HDLC_CORRELATOR_H
#define INCLUDED_GR_HDLC_CORRELATOR_H

#include <gr_sync_block.h>
#include <gr_msg_queue.h>
#include <assert.h>

//#define	DEBUG_HDLC_CORRELATOR

class gr_hdlc_correlator;
typedef boost::shared_ptr<gr_hdlc_correlator> gr_hdlc_correlator_sptr;

gr_hdlc_correlator_sptr gr_make_hdlc_correlator (gr_msg_queue_sptr target_queue, bool descramble = true);

class gr_hdlc_correlator : public gr_sync_block {
  static const int OVERSAMPLE=8;
  static const int AVG_PERIOD=512;		            // must be power of 2 (for freq offset correction)
  static const unsigned char FLAG=0x7e;
  static const unsigned char NRZI_FLAG=0x81;
  static const int MAX_PACLEN=1+70+1+1+256+2+1;     //flag,address,control,pid,payload,fcs,flag
  static const int MIN_PACLEN_BITS=112+8+16;        //address+control+fcs
  static const int BITS_PER_BYTE=8;
  static const int THRESHOLD=0;

  enum state_t { ST_LOOKING, ST_UNDER_THRESHOLD, ST_LOCKED, ST_LOCKED_FLAG_IN, ST_LOCKED_FLAG_OUT };
  state_t	             d_state;
  gr_msg_queue_sptr      d_target_queue;
  bool					 d_descramble;
  unsigned int	         d_osi;				        // over sample index [0,OVERSAMPLE-1]
  unsigned int	         d_transition_osi;		    // first index where Hamming dist < thresh
  unsigned int	         d_center_osi;			    // center of bit
  unsigned int           d_pre_osi;
  unsigned int           d_post_osi;
  unsigned char          d_shift_reg[OVERSAMPLE],lastbit[OVERSAMPLE];
  unsigned char          d_g3ruh_desc[OVERSAMPLE];
  int		             d_bblen;		            // length of bitbuf
  unsigned char	         *d_bitbuf;			        // demodulated bits
  unsigned char          *d_pktbuf;
  int		             d_bbi;	     	            // bitbuf index
  int	                 d_avbi;                    // average buffer index
  float	                 d_avgbuf[AVG_PERIOD];
  float                  d_avg;
  float                  d_accum;

  unsigned char          byte,lb;
  int                    samplecounter,flagcounter;
  unsigned short         bytes;
  unsigned short         ones;

  
#ifdef DEBUG_HDLC_CORRELATOR
  FILE		*d_debug_fp;			                // binary log file
#endif

  friend gr_hdlc_correlator_sptr gr_make_hdlc_correlator(gr_msg_queue_sptr target_queue, bool descramble);
  gr_hdlc_correlator(gr_msg_queue_sptr target_queue, bool descramble = true);

  inline int slice (float x) {
    return x >= d_avg ? 1 : 0;
  }

  void update_avg(float x);
  void enter_looking ();
  char descrambler(char, int);
  
  static int add_index (int a, int b)
  {
    int t = a + b;
    if (t >= OVERSAMPLE) t -= OVERSAMPLE;
    assert (t >= 0 && t < OVERSAMPLE);
    return t;
  }

  static int sub_index (int a, int b)
  {
    int t = a - b;
    if (t < 0) t += OVERSAMPLE;
    assert (t >= 0 && t < OVERSAMPLE);
    return t;
  }

  char *char2bin(char);

  
 public:
  ~gr_hdlc_correlator ();

  int work (int noutput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_GR_HDLC_CORRELATOR_H */
