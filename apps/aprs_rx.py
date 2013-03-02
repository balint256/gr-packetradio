#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: APRS Receiver
# Generated: Fri Mar  1 19:23:22 2013
##################################################

from gnuradio import analog
from gnuradio import blks2
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import packetradio
from gnuradio import uhd
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.gr import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from gnuradio.wxgui import scopesink2
from gnuradio.wxgui import waterfallsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import math
import wx

class aprs_rx(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="APRS Receiver")

		##################################################
		# Variables
		##################################################
		self.space = space = 1200
		self.mark = mark = 2200
		self.xlate_decim = xlate_decim = 8
		self.xlate_bandwidth = xlate_bandwidth = 1200*6
		self.sym_dev = sym_dev = (mark-space)/2
		self.samp_rate = samp_rate = 1e6
		self.quad_rate = quad_rate = 96000
		self.gain = gain = 10
		self.freq_offset = freq_offset = 390e3
		self.freq = freq = 144e6
		self.baud = baud = 1200
		self.audio_rate = audio_rate = 48000
		self.audio_mul = audio_mul = 1
		self.aprs_rate = aprs_rate = 12000
		self.ant = ant = 'TX/RX'

		##################################################
		# Message Queues
		##################################################
		ax25_hdlc_framer_b_0_msgq_out = ax25_print_frame_0_msgq_in = gr.msg_queue(2)

		##################################################
		# Blocks
		##################################################
		self.nb = self.nb = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
		self.nb.AddPage(grc_wxgui.Panel(self.nb), "Baseband")
		self.nb.AddPage(grc_wxgui.Panel(self.nb), "Waterfall")
		self.nb.AddPage(grc_wxgui.Panel(self.nb), "Signal")
		self.nb.AddPage(grc_wxgui.Panel(self.nb), "Slicer")
		self.nb.AddPage(grc_wxgui.Panel(self.nb), "Eye")
		self.Add(self.nb)
		_gain_sizer = wx.BoxSizer(wx.VERTICAL)
		self._gain_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_gain_sizer,
			value=self.gain,
			callback=self.set_gain,
			label="RF Gain",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._gain_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_gain_sizer,
			value=self.gain,
			callback=self.set_gain,
			minimum=0,
			maximum=50,
			num_steps=50,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.Add(_gain_sizer)
		_freq_offset_sizer = wx.BoxSizer(wx.VERTICAL)
		self._freq_offset_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_freq_offset_sizer,
			value=self.freq_offset,
			callback=self.set_freq_offset,
			label="Freq Offset",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._freq_offset_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_freq_offset_sizer,
			value=self.freq_offset,
			callback=self.set_freq_offset,
			minimum=-500e3,
			maximum=500e3,
			num_steps=1000,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.Add(_freq_offset_sizer)
		self._freq_text_box = forms.text_box(
			parent=self.GetWin(),
			value=self.freq,
			callback=self.set_freq,
			label="Freq",
			converter=forms.float_converter(),
		)
		self.Add(self._freq_text_box)
		_audio_mul_sizer = wx.BoxSizer(wx.VERTICAL)
		self._audio_mul_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_audio_mul_sizer,
			value=self.audio_mul,
			callback=self.set_audio_mul,
			label="Audio",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._audio_mul_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_audio_mul_sizer,
			value=self.audio_mul,
			callback=self.set_audio_mul,
			minimum=0,
			maximum=10,
			num_steps=1000,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.Add(_audio_mul_sizer)
		self._ant_chooser = forms.drop_down(
			parent=self.GetWin(),
			value=self.ant,
			callback=self.set_ant,
			label="Antenna",
			choices=['TX/RX', 'RX2'],
			labels=[],
		)
		self.Add(self._ant_chooser)
		self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
			self.nb.GetPage(1).GetWin(),
			baseband_freq=0,
			dynamic_range=50,
			ref_level=-65,
			ref_scale=2.0,
			sample_rate=aprs_rate,
			fft_size=512,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="Waterfall Plot",
		)
		self.nb.GetPage(1).Add(self.wxgui_waterfallsink2_0.win)
		self.wxgui_scopesink2_0_0_0 = scopesink2.scope_sink_f(
			self.nb.GetPage(4).GetWin(),
			title="Scope Plot",
			sample_rate=aprs_rate/10,
			v_scale=0.5,
			v_offset=0,
			t_scale=0.002,
			ac_couple=False,
			xy_mode=False,
			num_inputs=1,
			trig_mode=gr.gr_TRIG_MODE_AUTO,
			y_axis_label="Counts",
		)
		self.nb.GetPage(4).Add(self.wxgui_scopesink2_0_0_0.win)
		self.wxgui_scopesink2_0_0 = scopesink2.scope_sink_f(
			self.nb.GetPage(3).GetWin(),
			title="Scope Plot",
			sample_rate=aprs_rate,
			v_scale=0.5,
			v_offset=0,
			t_scale=0.002,
			ac_couple=False,
			xy_mode=False,
			num_inputs=1,
			trig_mode=gr.gr_TRIG_MODE_AUTO,
			y_axis_label="Counts",
		)
		self.nb.GetPage(3).Add(self.wxgui_scopesink2_0_0.win)
		self.wxgui_scopesink2_0 = scopesink2.scope_sink_f(
			self.nb.GetPage(2).GetWin(),
			title="Scope Plot",
			sample_rate=aprs_rate,
			v_scale=0.05,
			v_offset=0,
			t_scale=0.002,
			ac_couple=False,
			xy_mode=False,
			num_inputs=1,
			trig_mode=gr.gr_TRIG_MODE_AUTO,
			y_axis_label="Counts",
		)
		self.nb.GetPage(2).Add(self.wxgui_scopesink2_0.win)
		self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
			self.nb.GetPage(0).GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=-20,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=1024,
			fft_rate=15,
			average=True,
			avg_alpha=0.5,
			title="FFT Plot",
			peak_hold=False,
		)
		self.nb.GetPage(0).Add(self.wxgui_fftsink2_0.win)
		def wxgui_fftsink2_0_callback(x, y):
			self.set_freq_offset(x)
		
		self.wxgui_fftsink2_0.set_callback(wxgui_fftsink2_0_callback)
		self.uhd_usrp_source_0 = uhd.usrp_source(
			device_addr="",
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_source_0.set_samp_rate(samp_rate)
		self.uhd_usrp_source_0.set_center_freq(freq, 0)
		self.uhd_usrp_source_0.set_gain(gain, 0)
		self.uhd_usrp_source_0.set_antenna(ant, 0)
		self.low_pass_filter_0 = gr.fir_filter_ccf(1, firdes.low_pass(
			1, aprs_rate, 2e3, 600, firdes.WIN_HAMMING, 6.76))
		self.gr_single_pole_iir_filter_xx_0 = gr.single_pole_iir_filter_ff(0.0001, 1)
		self.gr_null_sink_0 = gr.null_sink(gr.sizeof_float*1)
		self.gr_multiply_xx_0 = gr.multiply_vcc(1)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vff((audio_mul, ))
		self.gr_agc_xx_1 = gr.agc_ff(1e-3, 0.8, 0.1, 10.0)
		self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(xlate_decim, (firdes.low_pass(1, samp_rate, xlate_bandwidth/2, 1000)), freq_offset, samp_rate)
		self.digital_clock_recovery_mm_xx_0 = digital.clock_recovery_mm_ff(10, .25 * (0.05)**2, 0.5, 0.005, 0.005)
		self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
		self.blocks_sub_xx_0 = blocks.sub_ff(1)
		self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
		self.blks2_rational_resampler_xxx_0_0 = blks2.rational_resampler_ccc(
			interpolation=quad_rate,
			decimation=int(samp_rate/xlate_decim),
			taps=None,
			fractional_bw=None,
		)
		self.blks2_rational_resampler_xxx_0 = blks2.rational_resampler_ccc(
			interpolation=aprs_rate,
			decimation=quad_rate,
			taps=None,
			fractional_bw=None,
		)
		self.blks2_nbfm_rx_0_0 = blks2.nbfm_rx(
			audio_rate=audio_rate,
			quad_rate=quad_rate,
			tau=75e-6,
			max_dev=25000,
		)
		self.blks2_nbfm_rx_0 = blks2.nbfm_rx(
			audio_rate=aprs_rate,
			quad_rate=quad_rate,
			tau=75e-6,
			max_dev=3e3,
		)
		self.ax25_print_frame_0 = packetradio.queue_watcher_thread(ax25_print_frame_0_msgq_in)
		self.ax25_hdlc_framer_b_0 = packetradio.hdlc_framer(ax25_hdlc_framer_b_0_msgq_out, False)
		self.analog_sig_source_x_0 = analog.sig_source_c(aprs_rate, analog.GR_SIN_WAVE, -(min(mark,space)+sym_dev), 1, 0)
		self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(aprs_rate/(2*math.pi*sym_dev))
		self.analog_pwr_squelch_xx_0_0_0 = analog.pwr_squelch_cc(-70, 1e-1, 0, False)
		self.analog_pwr_squelch_xx_0_0 = analog.pwr_squelch_cc(-70, 1e-1, 0, False)

		##################################################
		# Connections
		##################################################
		self.connect((self.uhd_usrp_source_0, 0), (self.wxgui_fftsink2_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_0_0, 0), (self.blks2_rational_resampler_xxx_0, 0))
		self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blks2_rational_resampler_xxx_0_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.wxgui_waterfallsink2_0, 0))
		self.connect((self.uhd_usrp_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
		self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
		self.connect((self.blocks_sub_xx_0, 0), (self.digital_clock_recovery_mm_xx_0, 0))
		self.connect((self.gr_single_pole_iir_filter_xx_0, 0), (self.blocks_sub_xx_0, 1))
		self.connect((self.analog_quadrature_demod_cf_0, 0), (self.gr_single_pole_iir_filter_xx_0, 0))
		self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blocks_sub_xx_0, 0))
		self.connect((self.low_pass_filter_0, 0), (self.analog_quadrature_demod_cf_0, 0))
		self.connect((self.gr_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
		self.connect((self.analog_sig_source_x_0, 0), (self.gr_multiply_xx_0, 1))
		self.connect((self.blocks_float_to_complex_0, 0), (self.gr_multiply_xx_0, 0))
		self.connect((self.blks2_nbfm_rx_0, 0), (self.blocks_float_to_complex_0, 0))
		self.connect((self.blks2_nbfm_rx_0, 0), (self.blocks_float_to_complex_0, 1))
		self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.wxgui_scopesink2_0_0_0, 0))
		self.connect((self.digital_binary_slicer_fb_0, 0), (self.ax25_hdlc_framer_b_0, 0))
		self.connect((self.blks2_nbfm_rx_0, 0), (self.wxgui_scopesink2_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_0_0, 0), (self.analog_pwr_squelch_xx_0_0, 0))
		self.connect((self.analog_pwr_squelch_xx_0_0_0, 0), (self.blks2_nbfm_rx_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_0_0, 0), (self.analog_pwr_squelch_xx_0_0_0, 0))
		self.connect((self.analog_quadrature_demod_cf_0, 0), (self.wxgui_scopesink2_0_0, 0))
		self.connect((self.blks2_nbfm_rx_0_0, 0), (self.gr_agc_xx_1, 0))
		self.connect((self.analog_pwr_squelch_xx_0_0, 0), (self.blks2_nbfm_rx_0_0, 0))
		self.connect((self.gr_agc_xx_1, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.gr_null_sink_0, 0))

	def get_space(self):
		return self.space

	def set_space(self, space):
		self.space = space
		self.set_sym_dev((self.mark-self.space)/2)
		self.analog_sig_source_x_0.set_frequency(-(min(self.mark,self.space)+self.sym_dev))

	def get_mark(self):
		return self.mark

	def set_mark(self, mark):
		self.mark = mark
		self.set_sym_dev((self.mark-self.space)/2)
		self.analog_sig_source_x_0.set_frequency(-(min(self.mark,self.space)+self.sym_dev))

	def get_xlate_decim(self):
		return self.xlate_decim

	def set_xlate_decim(self, xlate_decim):
		self.xlate_decim = xlate_decim

	def get_xlate_bandwidth(self):
		return self.xlate_bandwidth

	def set_xlate_bandwidth(self, xlate_bandwidth):
		self.xlate_bandwidth = xlate_bandwidth
		self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(1, self.samp_rate, self.xlate_bandwidth/2, 1000)))

	def get_sym_dev(self):
		return self.sym_dev

	def set_sym_dev(self, sym_dev):
		self.sym_dev = sym_dev
		self.analog_sig_source_x_0.set_frequency(-(min(self.mark,self.space)+self.sym_dev))
		self.analog_quadrature_demod_cf_0.set_gain(self.aprs_rate/(2*math.pi*self.sym_dev))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
		self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(1, self.samp_rate, self.xlate_bandwidth/2, 1000)))
		self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate)

	def get_quad_rate(self):
		return self.quad_rate

	def set_quad_rate(self, quad_rate):
		self.quad_rate = quad_rate

	def get_gain(self):
		return self.gain

	def set_gain(self, gain):
		self.gain = gain
		self._gain_slider.set_value(self.gain)
		self._gain_text_box.set_value(self.gain)
		self.uhd_usrp_source_0.set_gain(self.gain, 0)

	def get_freq_offset(self):
		return self.freq_offset

	def set_freq_offset(self, freq_offset):
		self.freq_offset = freq_offset
		self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.freq_offset)
		self._freq_offset_slider.set_value(self.freq_offset)
		self._freq_offset_text_box.set_value(self.freq_offset)

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.uhd_usrp_source_0.set_center_freq(self.freq, 0)
		self._freq_text_box.set_value(self.freq)

	def get_baud(self):
		return self.baud

	def set_baud(self, baud):
		self.baud = baud

	def get_audio_rate(self):
		return self.audio_rate

	def set_audio_rate(self, audio_rate):
		self.audio_rate = audio_rate

	def get_audio_mul(self):
		return self.audio_mul

	def set_audio_mul(self, audio_mul):
		self.audio_mul = audio_mul
		self._audio_mul_slider.set_value(self.audio_mul)
		self._audio_mul_text_box.set_value(self.audio_mul)
		self.gr_multiply_const_vxx_0.set_k((self.audio_mul, ))

	def get_aprs_rate(self):
		return self.aprs_rate

	def set_aprs_rate(self, aprs_rate):
		self.aprs_rate = aprs_rate
		self.wxgui_waterfallsink2_0.set_sample_rate(self.aprs_rate)
		self.analog_sig_source_x_0.set_sampling_freq(self.aprs_rate)
		self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.aprs_rate, 2e3, 600, firdes.WIN_HAMMING, 6.76))
		self.analog_quadrature_demod_cf_0.set_gain(self.aprs_rate/(2*math.pi*self.sym_dev))
		self.wxgui_scopesink2_0.set_sample_rate(self.aprs_rate)
		self.wxgui_scopesink2_0_0_0.set_sample_rate(self.aprs_rate/10)
		self.wxgui_scopesink2_0_0.set_sample_rate(self.aprs_rate)

	def get_ant(self):
		return self.ant

	def set_ant(self, ant):
		self.ant = ant
		self.uhd_usrp_source_0.set_antenna(self.ant, 0)
		self._ant_chooser.set_value(self.ant)

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = aprs_rx()
	tb.Run(True)

