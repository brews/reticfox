#! /usr/bin/env bash
# Parse iCESM POP and CAM files.
# Be sure you've run `conda activate icesm_parse` before running this script.

#PBS -N parse_icesm
#PBS -m bea
#PBS -M malevich@email.arizona.edu
#PBS -W group_list=jesst
#PBS -q standard
#PBS -l select=1:ncpus=28:mem=168gb
### Consider using `pvmem` if have mem problems ^
#PBS -l place=pack:shared
#PBS -l walltime=24:00:00
### total cputime = walltime * ncpus:
#PBS -l cput=672:00:00

source ~/miniconda3/etc/profile.d/conda.sh
conda activate icesm_parse

CASENAME="b.e12.B1850C5.f19_g16.i21ka.03"
IN_DIR="/xdisk/malevich/$CASENAME"
OUT_DIR="/rsgrps/jesst/icesm/$CASENAME"

date

mkdir -p $OUT_DIR

# atm output
reticfox make_ts \
    --ts_glob "$IN_DIR/*.TS.*.nc" \
    --ts_str "ts" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.ts.nc"

reticfox make_tas \
    --trefht_glob "$IN_DIR/*.TREFHT.*.nc" \
    --tas_str "tas" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.tas.nc"

reticfox make_pr \
    --precc_glob "$IN_DIR/*.PRECC.*.nc" \
    --precl_glob "$IN_DIR/*.PRECL.*.nc" \
    --pr_str "pr" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.pr.nc"

reticfox make_d18op \
    --precrl_h216o_glob "$IN_DIR/*.PRECRL_H216OR.*.nc" \
    --precrc_h216o_glob "$IN_DIR/*.PRECRC_H216Or.*.nc" \
    --precsc_h216o_glob "$IN_DIR/*.PRECSC_H216Os.*.nc" \
    --precsl_h216o_glob "$IN_DIR/*.PRECSL_H216OS.*.nc" \
    --precrc_h218o_glob "$IN_DIR/*.PRECRC_H218Or.*.nc" \
    --precrl_h218o_glob "$IN_DIR/*.PRECRL_H218OR.*.nc" \
    --precsc_h218o_glob "$IN_DIR/*.PRECSC_H218Os.*.nc" \
    --precsl_h218o_glob "$IN_DIR/*.PRECSL_H218OS.*.nc" \
    --d18op_str "d18op" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.d18op.nc"

reticfox make_omega \
    --omega_glob "$IN_DIR/*.OMEGA.*.nc" \
    --ps_glob "$IN_DIR/*.PS.*.nc" \
    --omega_str "omega" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.omega.nc"

reticfox make_ddp \
    --precrl_h2o_glob "$IN_DIR/*.PRECRL_H2OR.*.nc" \
    --precrc_h2o_glob "$IN_DIR/*.PRECRC_H2Or.*.nc" \
    --precsc_h2o_glob "$IN_DIR/*.PRECSC_H2Os.*.nc" \
    --precsl_h2o_glob "$IN_DIR/*.PRECSL_H2OS.*.nc" \
    --precrc_hdo_glob "$IN_DIR/*.PRECRC_HDOr.*.nc" \
    --precrl_hdo_glob "$IN_DIR/*.PRECRL_HDOR.*.nc" \
    --precsc_hdo_glob "$IN_DIR/*.PRECSC_HDOs.*.nc" \
    --precsl_hdo_glob "$IN_DIR/*.PRECSL_HDOS.*.nc" \
    --ddp_str "ddp" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.ddp.nc"

# pop output
reticfox make_sos \
    --salt_glob "$IN_DIR/*.SALT.*.nc" \
    --sos_str "sos" \
    --outfl "$OUT_DIR/$CASENAME.pop.h.sos.nc"

reticfox make_d18osw \
    --r18o_glob "$IN_DIR/*.R18O.*.nc" \
    --d18osw_str "d18osw" \
    --outfl "$OUT_DIR/$CASENAME.pop.h.d18osw.nc"

# Now we're doing gamma-average T and SST slice-by-slice to avoid memory problems
# from calculating in-situ temperatures.
slice_names=( "000101-009912" "010001-019912" "020001-029912" "030001-039912" "040001-049912" "050001-059912" "060001-069912" "070001-079912" "080001-090012")
for i in "${slice_names[@]}"
do
    reticfox make_tos \
        --temp_glob "$IN_DIR/$CASENAME.pop.h.TEMP.$i.nc" \
        --salt_glob "$IN_DIR/$CASENAME.pop.h.SALT.$i.nc" \
        --tos_str "tos" \
        --outfl "$IN_DIR/$CASENAME.pop.h.tos.$i.nc"

    reticfox make_toga \
        --temp_glob "$IN_DIR/$CASENAME.pop.h.TEMP.$i.nc" \
        --salt_glob "$IN_DIR/$CASENAME.pop.h.SALT.$i.nc" \
        --toga_str "toGA" \
        --outfl "$IN_DIR/$CASENAME.pop.h.toGA.$i.nc"
done

reticfox combine_netcdf_glob \
  --nc_glob "$IN_DIR/*.tos.*.nc" \
  --sortby "time" \
  --outfl "$OUT_DIR/$CASENAME.pop.h.tos.nc"

reticfox combine_netcdf_glob \
  --nc_glob "$IN_DIR/*.toGA.*.nc" \
  --sortby "time" \
  --outfl "$OUT_DIR/$CASENAME.pop.h.toGA.nc"


date
