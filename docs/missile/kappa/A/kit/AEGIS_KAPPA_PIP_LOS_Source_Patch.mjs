#!/usr/bin/env node
/**
 * AEGIS v48 game: isolated Kappa PIP-LOS terminal heading patch.
 *
 * Usage:
 *   node AEGIS_KAPPA_PIP_LOS_Source_Patch.mjs INPUT.js OUTPUT.js
 *   node AEGIS_KAPPA_PIP_LOS_Source_Patch.mjs GAME.html OUTPUT-unpacked-patched.js
 *
 * This utility emits UNPACKED JS ONLY. It does not repack the HTML, regenerate
 * the game's detached diagnostic capsule, or certify existing range tables.
 * Ask Codex to rebuild and revalidate those separately.
 */
import fs from 'node:fs';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import path from 'node:path';

const OLD = [
  '    // First experimental terminal-vector policy: level, head-on horizontal direction.',
  '    // This matches the ADD sea-skimmer geometry (gamma_f≈0) and keeps the high-diver adaptation minimal.',
  '    let hx=-targetState.velMps.x,hy=-targetState.velMps.y;',
  '    let hm=Math.hypot(hx,hy);',
  '    if(hm<1){hx=dx;hy=dy;hm=Math.max(1,Math.hypot(hx,hy));}',
  '    hx/=hm;hy/=hm;'
].join('\n');

const NEW = [
  '    // Game terminal-vector heading follows the observed/estimated PIP LOS.',
  '    // Do not automatically reverse a retreating/crossing target\'s heading.',
  '    let hx=dx,hy=dy;',
  '    let hm=Math.max(1,Math.hypot(hx,hy));',
  '    hx/=hm;hy/=hm;'
].join('\n');

function occurrences(haystack, needle) {
  return haystack.split(needle).length - 1;
}
function sha(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }

export function applyKappaPipLosSourcePatch(src) {
  if (!src.includes('function _wip79KappaPipState(m,targetState){'))
    throw Error('Required _wip79KappaPipState definition not found. Check selected build.');
  const oldCount = occurrences(src, OLD);
  const newCount = occurrences(src, NEW);
  if (oldCount === 0 && (newCount === 1 || newCount === 2))
    throw Error('Patch already present; refusing duplicate application.');
  if (newCount !== 0 || (oldCount !== 1 && oldCount !== 2))
    throw Error(`Unexpected matching blocks: old=${oldCount} new=${newCount}. Stop; inspect branch manually.`);
  // Exact multi-line match prevents accidentally editing JS string literals of
  // the detached diagnostic capsule, which need separate regeneration.
  const patched = src.split(OLD).join(NEW);
  if (occurrences(patched, NEW) !== oldCount || occurrences(patched, OLD) !== 0)
    throw Error('Patch postcondition failed');
  // Prove the edit is strictly the replacement, not a general rewrite.
  if (patched.split(NEW).join(OLD) !== src)
    throw Error('Unexpected unrelated changes in patch');
  return {patched, changedBlocks:oldCount, inputSha256:sha(src), outputSha256:sha(patched)};
}

function loadInput(filename) {
  const raw = fs.readFileSync(filename, 'utf8');
  if (filename.toLowerCase().endsWith('.html')) {
    const chunks = [...raw.matchAll(/<script\b[^>]*data-c55-index="13"[^>]*>([\s\S]*?)<\/script>/g)];
    if (chunks.length !== 1) throw Error('Expected exactly one packed c55-index=13 script.');
    const packed = Buffer.from(chunks[0][1].trim(), 'base64');
    if (packed.length === 0) throw Error('Empty embedded game script');
    const src = zlib.gunzipSync(packed).toString('utf8');
    return {src, fromHtml:true};
  }
  if (/data-c55-index="13"/.test(raw))
    throw Error('Packed HTML detected but extension is not .html. Rename the input.');
  return {src:raw, fromHtml:false};
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  const [, , input, output] = process.argv;
  if (!input || !output || path.resolve(input) === path.resolve(output)) {
    console.error('Usage: node AEGIS_KAPPA_PIP_LOS_Source_Patch.mjs INPUT.{js,html} OUTPUT.js');
    process.exit(2);
  }
  if (output.toLowerCase().endsWith('.html')) {
    console.error('Output must be an unpacked .js file; Codex must regenerate the diagnostic capsule and repack HTML.');
    process.exit(2);
  }
  try {
    const {src,fromHtml} = loadInput(input);
    const p = applyKappaPipLosSourcePatch(src);
    fs.writeFileSync(output, p.patched, {flag:'wx'}); // refuse destructive overwrite
    console.log(JSON.stringify({input,output,fromHtml,changedBlocks:p.changedBlocks,
      inputSha256:p.inputSha256,outputSha256:p.outputSha256,
      warning:'UNPACKED SOURCE ONLY. Rebuild HTML, regenerate diagnostics and hashes; previous ENV_C tables are stale.'},null,2));
  } catch (e) { console.error(String(e?.stack ?? e)); process.exitCode=1; }
}
