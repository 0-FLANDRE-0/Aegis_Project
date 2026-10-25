"""Run exactly one product-RF near-vertical shot in a fresh process."""
from pathlib import Path
import argparse,gzip,json
from playwright.sync_api import sync_playwright
from run_product_near_vertical import run_variant

H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--variant',choices=['BASE','FINAL'],required=True);p.add_argument('--seed-index',type=int,choices=range(1,6),required=True);p.add_argument('--tag',default='primary');a=p.parse_args()
errors=[]
with sync_playwright() as pw:row=run_variant(pw,a.variant,errors,[a.seed_index-1])[0]
out={'row':row,'errors':errors};dest=H/'product-rf-parts'/f'{a.variant}-S{a.seed_index}-{a.tag}.json.gz';dest.parent.mkdir(exist_ok=True);dest.write_bytes(gzip.compress(json.dumps(out,separators=(',',':')).encode(),9,mtime=0));print(dest)
raise SystemExit(0 if not errors else 1)
