let ready;
async function boot(){
  importScripts('https://cdn.jsdelivr.net/pyodide/v0.29.4/full/pyodide.js');
  const py=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.29.4/full/'});
  const [wheel,source]=await Promise.all([fetch('/python/sgp4-2.27-py3-none-any.whl'),fetch('/python/orbit_engine.py')]);
  if(!wheel.ok||!source.ok)throw Error('Prediction files could not be loaded.');
  py.FS.writeFile('/sgp4.whl',new Uint8Array(await wheel.arrayBuffer()));
  await py.runPythonAsync("import zipfile, sys\nzipfile.ZipFile('/sgp4.whl').extractall('/home/pyodide/packages')\nsys.path.insert(0, '/home/pyodide/packages')");
  py.globals.set('__name__','orbit_engine');await py.runPythonAsync(await source.text());return py;
}
onmessage=async({data:p})=>{
 try{
  postMessage({type:'loading'});const py=await(ready??=boot());
  const all=[];let skipped=0;
  for(let i=0;i<p.rows.length;i++){
   py.globals.set('request_json',JSON.stringify({...p,row:p.rows[i],rows:undefined}));
   const result=JSON.parse(py.runPython('predict_json(request_json)'));
   all.push(...result.passes);skipped+=result.skipped;
   if(i%10===0||i===p.rows.length-1)postMessage({type:'progress',done:i+1,total:p.rows.length,passes:[...all].sort((a,b)=>a.entry-b.entry),skipped});
   await new Promise(r=>setTimeout(r,0));
  }
  postMessage({type:'done',passes:all.sort((a,b)=>a.entry-b.entry),skipped});
 }catch(e){postMessage({type:'error',error:'Pass prediction could not complete. Check your connection and retry.'});}
};
