let cached: {time:number; data:unknown[]}|null=null;
let pending: Promise<Response>|null=null;
export async function GET(){
 if(cached&&Date.now()-cached.time<7200000)return Response.json({data:cached.data,fetchedAt:cached.time});
 if(pending)return (await pending).clone();
 pending=(async()=>{try{
 const r=await fetch('https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json',{signal:AbortSignal.timeout(20000),headers:{'User-Agent':'OrbitWatch/1.0'},cf:{cacheTtl:7200,cacheEverything:true}} as RequestInit);
 if(!r.ok)throw Error('upstream');const data=await r.json();if(!Array.isArray(data)||!data.length||!data[0].NORAD_CAT_ID)throw Error('format');cached={time:Date.now(),data};return Response.json({data,fetchedAt:cached.time});
 }catch{return Response.json({error:'The satellite catalog is temporarily unavailable. Try again later. No simulated positions are shown.'},{status:503});}})();
 try{return (await pending).clone();}finally{pending=null;}
}
