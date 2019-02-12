#! /usr/bin/env bash
# Parse iCESM POP and CAM files.
# Be sure you've run `conda activate icesm_parse` before running this script.

### script to run a serial job using one core on htc using queue windfall or standard

### beginning of line, three pound/cross-hatch characters indicate comment
### beginning of line #PBS indicates an active PBS command/directive
### use ###PBS and #PBS to deactivate and activate (respectively PBS lines without removing them from script

### Refer to UA Batch System website for system and queue specific limits (max values)
### Minimize resource requests (ncpus, mem, walltime, cputime, etc) to minimize queue wait delays

### Set the job name
#PBS -N icesm_parser

### Request email when job begins and ends
#PBS -m bea

### Specify email address to use for notification.
#PBS -M malevich@email.arizona.edu

### Specify the PI group for this job
### List of PI groups available to each user can be found with "va" command
#PBS -W group_list=jesst

### Set the queue for this job as windfall or standard (adjust ### and #)
#PBS -q standard
####PBS -q windfall

### Set the number of cores (cpus) and memory that will be used for this job
### When specifying memory request slightly less than 2GB memory per ncpus for standard node
### Some memory needs to be reserved for the Linux system processes
#PBS -l select=1:ncpus=28:mem=168gb

### Important!!! Include this line for your 1p job.
### Without it, the entire node, containing 12 core, will be allocated
#PBS -l place=pack:shared

### Specify "wallclock time" required for this job, hhh:mm:ss
#PBS -l walltime=06:00:00

### Specify total cpu time required for this job, hhh:mm:ss
### total cputime = walltime * ncpus
#PBS -l cput=168:00:00

### Load required modules/libraries if needed (blas example)
### Use "module avail" command to list all available modules
### NOTE: /usr/share/Modules/init/csh -CAPITAL M in Modules

conda activate icesm_parse

CASENAME="b.e12.B1850C5.f19_g16.i21ka.03"
IN_DIR="/xdisk/malevich/$CASENAME"
OUT_DIR="/rsgrps/jesst/icesm/$CASENAME"

date

mkdir -p $OUT_DIR

# atm output
python make_ts.py \
    --ts_glob "$IN_DIR/*.TS.*.nc" \
    --ts_str "ts" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.ts.nc"

python make_tas.py \
    --trefht_glob "$IN_DIR/*.TREFHT.*.nc" \
    --tas_str "tas" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.tas.nc"

python make_pr.py \
    --precc_glob "$IN_DIR/*.PRECC.*.nc" \
    --precl_glob "$IN_DIR/*.PRECL.*.nc" \
    --precsc_glob "$IN_DIR/*.PRECSC.*.nc" \
    --precsl_glob "$IN_DIR/*.PRECSL.*.nc" \
    --pr_str "pr" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.pr.nc"

python make_d18op.py \
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

python make_omega.py \
    --omega_glob "$IN_DIR/*.OMEGA.*.nc" \
    --ps_glob "$IN_DIR/*.PS.*.nc" \
    --omega_str "omega" \
    --outfl "$OUT_DIR/$CASENAME.cam.h0.omega.nc"

python make_ddp.py \
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
python make_tos.py \
  --temp_glob "$IN_DIR/*.TEMP.*.nc" \
  --salt_glob "$IN_DIR/*.SALT.*.nc" \
  --tos_str "tos" \
  --outfl "$OUT_DIR/$CASENAME.pop.h.tos.nc"

python make_sos.py \
  --salt_glob "$IN_DIR/*.SALT.*.nc" \
  --sos_str "sos" \
  --outfl "$OUT_DIR/$CASENAME.pop.h.sos.nc"

python make_d18osw.py \
    --r18o_glob "$IN_DIR/*.R18O.*.nc" \
    --d18osw_str "d18osw" \
    --outfl "$OUT_DIR/$CASENAME.pop.h.d18osw.nc"

python make_toga.py \
  --temp_glob "$IN_DIR/*.TEMP.*.nc" \
  --salt_glob "$IN_DIR/*.SALT.*.nc" \
  --toga_str "toGA" \
  --outfl "$OUT_DIR/$CASENAME.pop.h.toGA.nc"

date
