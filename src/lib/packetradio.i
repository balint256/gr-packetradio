/* -*- c++ -*- */

%feature("autodoc", "1");		// generate python docstrings

%{
#include <cstddef>
%}

%include "exception.i"
%import "gnuradio.i"			// the common stuff

%{
#include "gnuradio_swig_bug_workaround.h"	// mandatory bug fix
#include <gr_msg_queue.h>
#include "gr_hdlc_correlator.h"
#include "gr_hdlc_framer.h"
#include <stdexcept>
%}

// ----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC(gr,hdlc_correlator);

gr_hdlc_correlator_sptr gr_make_hdlc_correlator (gr_msg_queue_sptr target_queue, bool descramble = true);

class gr_hdlc_correlator : public gr_sync_block
{
private:
  gr_hdlc_correlator (gr_msg_queue_sptr target_queue, bool descramble = true);
};

GR_SWIG_BLOCK_MAGIC(gr,hdlc_framer);

gr_hdlc_framer_sptr gr_make_hdlc_framer (gr_msg_queue_sptr target_queue, bool mode);

class gr_hdlc_framer : public gr_sync_block
{
private:
  gr_hdlc_framer (gr_msg_queue_sptr target_queue, bool mode);
};

