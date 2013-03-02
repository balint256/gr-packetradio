# Copyright 2011 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

add_library(gnuradio-packetradio SHARED
	gr_hdlc_correlator.cc
	gr_hdlc_framer.cc
)
target_link_libraries(gnuradio-packetradio ${Boost_LIBRARIES} ${GRUEL_LIBRARIES} ${GNURADIO_CORE_LIBRARIES})
set_target_properties(gnuradio-packetradio PROPERTIES DEFINE_SYMBOL "gnuradio_packetradio_EXPORTS")

########################################################################
# Install built library files
########################################################################
install(TARGETS gnuradio-packetradio
    LIBRARY DESTINATION lib${LIB_SUFFIX} # .so/.dylib file
    ARCHIVE DESTINATION lib${LIB_SUFFIX} # .lib file
    RUNTIME DESTINATION bin              # .dll file
)

########################################################################
# Build and register unit test
########################################################################
find_package(Boost COMPONENTS unit_test_framework)

include(GrTest)
set(GR_TEST_TARGET_DEPS gnuradio-packetradio)
#turn each test cpp file into an executable with an int main() function
add_definitions(-DBOOST_TEST_DYN_LINK -DBOOST_TEST_MAIN)

#add_executable(qa_howto_square_ff qa_howto_square_ff.cc)
#target_link_libraries(qa_howto_square_ff gnuradio-howto ${Boost_LIBRARIES})
#GR_ADD_TEST(qa_howto_square_ff qa_howto_square_ff)

#add_executable(qa_howto_square2_ff qa_howto_square2_ff.cc)
#target_link_libraries(qa_howto_square2_ff gnuradio-howto ${Boost_LIBRARIES})
#GR_ADD_TEST(qa_howto_square2_ff qa_howto_square2_ff)

########################################################################
# Python/SWIG ##########################################################
########################################################################

########################################################################
# Include swig generation macros
########################################################################
find_package(SWIG)
find_package(PythonLibs)
if(NOT SWIG_FOUND OR NOT PYTHONLIBS_FOUND)
    return()
endif()
include(GrSwig)
include(GrPython)

########################################################################
# Setup swig generation
########################################################################
foreach(incdir ${GNURADIO_CORE_INCLUDE_DIRS})
    list(APPEND GR_SWIG_INCLUDE_DIRS ${incdir}/swig)
endforeach(incdir)

foreach(incdir ${GRUEL_INCLUDE_DIRS})
    list(APPEND GR_SWIG_INCLUDE_DIRS ${incdir}/gruel/swig)
endforeach(incdir)

set(GR_SWIG_LIBRARIES gnuradio-packetradio)
#set(GR_SWIG_DOC_FILE ${CMAKE_CURRENT_BINARY_DIR}/packetradio_doc.i)	# howto_packetradio_doc
#set(GR_SWIG_DOC_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/../include)

GR_SWIG_MAKE(packetradio packetradio.i) # packetradio_swig packetradio_swig.i

########################################################################
# Install the build swig module
########################################################################
GR_SWIG_INSTALL(TARGETS packetradio DESTINATION ${GR_PYTHON_DIR}${PACKETRADIO_PYTHON_SUBDIR}/packetradio)	# packetradio_swig

########################################################################
# Install swig .i files for development
########################################################################
install(
    FILES
    packetradio.i # packetradio_swig.i
#    ${CMAKE_CURRENT_BINARY_DIR}/packetradio_doc.i # packetradio_swig_doc.i
    DESTINATION ${GR_INCLUDE_DIR}/packetradio/swig	# Not adding ${PACKETRADIO_PYTHON_SUBDIR} here
)

