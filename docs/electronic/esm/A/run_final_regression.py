#!/usr/bin/env python3
"""Run the single final MAX_THREAT broad regression for ESM_A."""
from __future__ import annotations
import importlib.util,os
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
HARNESS_ROOT=Path(os.environ.get('AEGIS_HARNESS_ROOT','/workspace/emcon-b-final-harness')).resolve()
HARNESS=ROOT/'docs/missile/asm-seeker/A/asm_seeker_regression_runner.py'
PRODUCT=ROOT/'Aegis_SIM_v48_WIP_ESM_A.html'
BASELINE=ROOT/'Aegis_SIM_v48_WIP_EMCON_B.html'
PRODUCT_SHA='1f0b041b8c353f0b9014b8dd46cf144041ecb73d22698f938b1b15c87548209e'
BASELINE_SHA='50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee'

spec=importlib.util.spec_from_file_location('esm_a_final_regression',HARNESS);assert spec and spec.loader
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
runner.P=HERE;runner.R=HARNESS_ROOT;runner.E=HERE/'evidence/final-regression';runner.HTML=PRODUCT;runner.BASE=BASELINE;runner.EXPECTED=PRODUCT_SHA;runner.BASE_SHA=BASELINE_SHA

def environment():
  return {**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','NODE_PATH':os.environ.get('NODE_PATH',str(HARNESS_ROOT/'node_modules')),
    'B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':str(PRODUCT),'B2_OUT':str(runner.E),
    'PYTHONPATH':str(HARNESS_ROOT/'docs/gun/B2/phase1b/test_support'),'B2_ALLOW_AUTO':'0','THREAT_ASSUMPTION_MODE':'MAX_THREAT'}
runner.environment=environment

if __name__=='__main__':runner.main()
