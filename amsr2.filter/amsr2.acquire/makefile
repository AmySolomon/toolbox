#Robert Grumbine 27 May 2016

include makeall.mk

#LIBS=   -L/nwprod/lib -lw3nco_v2.0.3_d -lbufr_v10.2.3_d_64 -lbacio_v2.0.1_4
LIBS = ${W3NCO_LIBd} ${BUFR_LIBd} ${BACIO_LIB4}

OBJS = scan.o

all : seaice_totext

seaice_l1b_scan :  $(OBJS)
	$(CPPLD) $(CPPLDFLAGS) $(OBJS) -o $(@) $(MMAB_LIBF4) 

seaice_totext : totext.o
	$(CPPLD) $(CPPLDFLAGS) $< -o $(@) $(MMAB_LIBF4)
