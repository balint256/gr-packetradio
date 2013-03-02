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

#ifndef INCLUDED_GR_HDLC_FRAMER_H
#define INCLUDED_GR_HDLC_FRAMER_H

#undef VERBOSE

#include <gr_sync_block.h>
#include <gr_msg_queue.h>
#include <assert.h>

#define MAX_PACKET_LEN 16384
#define MIN_PACKET_LEN 17
#define FLAG 0x7e

class gr_hdlc_framer;
typedef boost::shared_ptr<gr_hdlc_framer> gr_hdlc_framer_sptr;

gr_hdlc_framer_sptr gr_make_hdlc_framer (gr_msg_queue_sptr target_queue, bool mode);

class gr_hdlc_framer : public gr_sync_block {
  enum state_t { STARTFLAG, PACKET, ENDFLAG, LASTFLAGBIT, END };
  state_t	            state;
  gr_msg_queue_sptr     target_queue;
  bool					mode;
  unsigned char			sr,*pktbuf,*pktptr,bitctr,ones,prevbit,bit,rbit;
  unsigned int			bytectr,descr,flagctr;

  friend gr_hdlc_framer_sptr gr_make_hdlc_framer (gr_msg_queue_sptr target_queue, bool mode);
  gr_hdlc_framer (gr_msg_queue_sptr target_queue, bool mode);

 public:
  int work (int noutput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};


#endif /* INCLUDED_GR_HDLC_FRAMER_H */
