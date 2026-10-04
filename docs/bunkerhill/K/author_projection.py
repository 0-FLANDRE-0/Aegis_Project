#!/usr/bin/env python3
"""Bake display-only CG-52 orthographic views from the exact indexed source."""
from pathlib import Path
import base64, gzip, hashlib, io, json
import numpy as np
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
meta=json.loads((HERE/'asset-meta.json').read_text())
packed=(HERE/'asset-geo.gz').read_bytes();buf=gzip.decompress(packed)
palette=np.array([tuple(bytes.fromhex(p['color'].lstrip('#'))) for p in meta['palette']],dtype=np.uint8)
faces=[];colors=[];line_rows=[]
def collect(m,offset):
    q=np.frombuffer(buf,dtype='<u2',count=m['pos'][1],offset=m['pos'][0]).reshape(-1,3)
    v=(q*np.asarray(m['qscale'])+m['qmin']+offset).astype(np.float32)
    pid=np.frombuffer(buf,dtype='u1',count=m['pid'][1],offset=m['pid'][0])
    if m.get('idx'):
        ix=np.frombuffer(buf,dtype='<u4'if m['i32']else'<u2',count=m['idx'][1],offset=m['idx'][0]).reshape(-1,3)
        faces.append(v[ix]);colors.append(palette[pid[ix[:,0]]])
    elif m.get('lines'):
        line_rows.append((v.reshape(-1,2,3),palette[pid[::2]]))
def node(rec,offset):
    offset=offset+np.asarray(rec['local'])
    for m in rec['meshes']:collect(m,offset)
    for child in rec['children']:node(child,offset)
for stat in meta['statics']:
    for m in stat['meshes']:collect(m,np.zeros(3))
for asm in meta['assemblies']:node(asm['root'],np.zeros(3))
tri=np.concatenate(faces);color=np.concatenate(colors)
assert len(tri)==740819
PPM=10
def clip_rectangles(alpha,bounds):
    active={};finished=[]
    for row,a in enumerate(alpha):
        edges=np.flatnonzero(np.diff(np.r_[False,a>0,False].astype(np.int8)))
        spans={(int(x),int(y))for x,y in edges.reshape(-1,2)}
        for span in list(active):
            if span not in spans:finished.append((*span,*active.pop(span),row))
        for span in spans:
            if span not in active:active[span]=(row,)
    for span,start in active.items():finished.append((*span,*start,len(alpha)))
    x0,second0,x1,second1=bounds
    return [[round(x0+a/PPM,4),round(x0+b/PPM,4),round(second1-d/PPM,4),round(second1-c/PPM,4)]
            for a,b,c,d in finished]
def projection(name,axes,depth_axis):
    low=tri[:,:,axes].min(axis=(0,1));high=tri[:,:,axes].max(axis=(0,1))
    low=np.floor(low*PPM-1)/PPM;high=np.ceil(high*PPM+1)/PPM
    width,height=np.rint((high-low)*PPM).astype(int)
    image=Image.new('RGBA',(int(width),int(height)),(0,0,0,0));draw=ImageDraw.Draw(image)
    coords=tri[:,:,axes].copy();coords[:,:,0]=(coords[:,:,0]-low[0])*PPM;coords[:,:,1]=(high[1]-coords[:,:,1])*PPM
    a,b,c=coords[:,0],coords[:,1],coords[:,2]
    area=np.abs((b[:,0]-a[:,0])*(c[:,1]-a[:,1])-(b[:,1]-a[:,1])*(c[:,0]-a[:,0]))
    # Raster presentation only. Subpixel faces still contribute via neighbouring
    # authored faces; the physics and 3D indexed geometry remain untouched.
    ids=np.flatnonzero(area>.02);depth=tri[:,:,depth_axis].mean(axis=1)
    ids=ids[np.argsort(depth[ids],kind='stable')]
    for i in ids:
        draw.polygon([tuple(p)for p in coords[i]],fill=tuple(int(v)for v in color[i])+(255,))
    # Preserve source line fittings, clipped to the opaque source projection so
    # hidden underside/wire lines do not cut through the rendered silhouette.
    lines=Image.new('RGBA',image.size,(0,0,0,0));ld=ImageDraw.Draw(lines)
    for v,cs in line_rows:
        pts=v[:,:,axes].copy();pts[:,:,0]=(pts[:,:,0]-low[0])*PPM;pts[:,:,1]=(high[1]-pts[:,:,1])*PPM
        for p,col in zip(pts,cs):ld.line([tuple(q)for q in p],fill=tuple(int(x)for x in col)+(255,),width=1)
    image.alpha_composite(Image.composite(lines,Image.new('RGBA',image.size),image.getchannel('A')))
    raw=io.BytesIO();image.save(raw,format='PNG',optimize=True);png=raw.getvalue()
    bounds=[float(low[0]),float(low[1]),float(high[0]),float(high[1])]
    image.save(HERE/f'cg52-projection-{name}.png')
    return {'bounds':bounds,'width':int(width),'height':int(height),'pixelsPerM':PPM,
            'image':'data:image/png;base64,'+base64.b64encode(png).decode(),
            'imageSha256':hashlib.sha256(png).hexdigest(),'clipRects':clip_rectangles(np.asarray(image)[:,:,3],bounds),
            'rasterizedFaces':len(ids),'opaquePixels':int(np.count_nonzero(np.asarray(image)[:,:,3]))}
result={'schema':'AEGIS_CG52_SOURCE_2D_PROJECTION_V1','profileId':'CG_52_LATE_TICONDEROGA',
        'sourceHtmlSha256':'402814f3d59fcec1e656cca7c825f5dd4f16c61db42be9913e8af87dfba996cc',
        'assetGeoSha256':hashlib.sha256(packed).hexdigest(),'indexedSourceTriangles':len(tri),
        'coordinateFrame':'SHIP_LOCAL_METRES_X_BOW_Y_STARBOARD_Z_UP','physicsFeedback':False,
        'top':projection('top',[0,2],1),'side':projection('side',[0,1],2)}
(HERE/'projection.json').write_text(json.dumps(result,separators=(',',':')))
print(json.dumps({'output':'projection.json','bytes':(HERE/'projection.json').stat().st_size,
                  'sha256':hashlib.sha256((HERE/'projection.json').read_bytes()).hexdigest(),
                  'views':{name:{k:v for k,v in result[name].items()if k not in ['image','clipRects']}for name in ['top','side']}}))
