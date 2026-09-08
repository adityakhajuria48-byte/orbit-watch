import {build} from 'esbuild';
await build({entryPoints:['tracker/worker.js'],outfile:'public/tracker-worker.js',bundle:true,format:'iife',platform:'browser',minify:true});

import {copyFileSync} from 'node:fs';
copyFileSync('python/orbit_engine.py','public/python/orbit_engine.py');
