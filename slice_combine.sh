#! /usr/bin/env bash
# 2018-01-25
# Parse iCESM POP potential temperature files.
# Slice off top layers and combine to single netCDF.


MATCHGLOB="*.nc"
SLICE_APPEND_NAME=".500-30000cm.nc"
MERGED_NC_NAME="b.e12.B1850C5.f19_g16.i21ka.03.pop.h.TEMP$SLICE_APPEND_NAME"


module load nco


## For each file, slice ocean depth <= 30000 cm and output to new netCDF.
#for filename in $MATCHGLOB; do
    #echo `date '+%Y-%m-%d %H:%M:%S'`" - slicing file: $filename"
    #ncks -d z_t,,30000.0 "$filename" "$(basename "$filename" .nc)$SLICE_APPEND_NAME"
    #echo `date '+%Y-%m-%d %H:%M:%S'`" - done slicing file"
#done

## Merge new slices into single netCDF.
#echo `date '+%Y-%m-%d %H:%M:%S'`" - combining files"
#ncecat *$SLICE_APPEND_NAME -O "$MERDGED_NC_NAME"
#echo `date '+%Y-%m-%d %H:%M:%S'`" - done combining files"


