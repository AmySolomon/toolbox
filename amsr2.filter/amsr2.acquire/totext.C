#include <cstdio>
#include <cstdlib>
#include <cmath>

#include "amsr2.h"
#include "ncepgrids.h"

#define land 0
void scanner(FILE *fin, FILE *fout, metricgrid<unsigned char> &mgrid, grid2<amsr2_hrpt> &hrgrid, grid2<amsr2_lrpt> &lrgrid) ;

#define ntargets 2

int main(int argc, char *argv[]) {
  FILE *fin, *fout[ntargets];
  char fname[90];

// declare target grids:
  northhigh<unsigned char> nhh;
  southhigh<unsigned char> shh;

// vectors of grids for working on/with:
  mvector<metricgrid<unsigned char>* > mgrids(ntargets);
  grid2<amsr2_hrpt>  hrgrids;
  grid2<amsr2_lrpt>  lrgrids;

  mgrids[0] = &nhh;
  mgrids[1] = &shh;

// Open data files:
  fin = fopen(argv[1], "r");
  if (fin == (FILE*) NULL) {
    printf("failed to open input satellite data file %s\n",argv[1]);
    return 1;
  }
  for (int i = 0; i < ntargets; i++) {
    sprintf(fname, "%s.%d",argv[2],i);
    fout[i] = fopen(fname, "w");
    if (fout[i] == (FILE*) NULL) {
      printf("failed to open output satellite data file %s %d\n",argv[2], i);
      return 1;
    }
  }

// Now read (scan) the input files for data to work with on the given
//   grids.
// Scanner does its own rewind, and writes out data used for each grid --
//   could/should really change fout to also being one each

  for (int i = 0 ; i < ntargets; i++) {
    hrgrids.resize(mgrids[i]->xpoints(), mgrids[i]->ypoints() );
    lrgrids.resize(mgrids[i]->xpoints(), mgrids[i]->ypoints() );
    scanner(fin, fout[i], *mgrids[i], hrgrids, lrgrids);
    fclose(fout[i]);
  }

  fclose(fin);

  return 0;
}

void scanner(FILE *fin, FILE *fout, metricgrid<unsigned char> &mgrid, grid2<amsr2_hrpt> &hrgrid, grid2<amsr2_lrpt> &lrgrid) {
  amsr2head  x;
  amsr2_hrpt hr;
  amsr2_lrpt lr;
  amsr2_spot s[12];

  int i, nobs, gridskip = 0, nuse = 0, nread = 0;
  int tindex;
  float sum;
  fijpt loc;
  ijpt iloc;
  latpt ll;

  rewind(fin);
  while (!feof(fin)) {
    fread(&x, sizeof(x), 1, fin);
    nobs = x.nspots;

    fread(&s[0], sizeof(amsr2_spot), nobs, fin);
    if (feof(fin)) continue;

// look at land fractions, land == 0
    sum = 0;
    for (i = 0; i < nobs; i++) { sum += s[i].alfr; }

    nread += 1;
    if (x.clat < 25 && x.clat > -40.0) continue;
    if (sum == land) continue;

    if (nobs == 2) {
      hr.head = x;
      for (i = 0; i < nobs; i++) { hr.obs[i] = s[i]; }
    }
    else {
      lr.head = x;
      for (i = 0; i < nobs; i++) { lr.obs[i] = s[i]; }
    }

    ll.lat = (float) x.clat;
    ll.lon = (float) x.clon;
    loc = mgrid.locate(ll);
    iloc.i = rint(loc.i);
    iloc.j = rint(loc.j);
    if (mgrid.in(loc)) {
      nuse += 1;
      // do something useful
      if (nobs == 2) {
        fprintf(fout, "hr ");
        hrgrid[loc] = hr;
      }
      else {
        fprintf(fout, "lr ");
        lrgrid[loc] = lr;
      }
      // Header:
      //fprintf(fout, "%f %f %3d %3d %4.2f ",ll.lat, ll.lon, iloc.i, iloc.j, s[0].alfr );
      fprintf(fout, "%f %f  ",ll.lat, ll.lon);
      // tb
      for (tindex = 0; tindex < nobs; tindex++) {
	fprintf(fout, "%6.2f ",s[tindex].tmbr);
      }
      fprintf(fout, "\n");
    }
    else {
      gridskip += 1;
    }
  }

  printf("nread = %d nuse = %d gridskip = %d\n",nread, nuse, gridskip);

  return ;
}
