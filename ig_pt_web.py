#!/usr/bin/env python3
"""Generate ig_pt_web.html — interactive 3D IG periodic table (Three.js)."""

import json, shutil
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from ig_periodic_table import ELEMENTS, PRIM_LABEL, FDE_CLASS, ORGANIC_THREAD, METALLIC_THREAD
from ig_pt_3d_utils import ICO_VERTS, ICO_EDGES, PRIM_VERT, ico_element_positions, ORGANIC_SET, METALLIC_SET

WS = 3.5  # world-space scale

def build_data():
    pos3d = ico_element_positions()
    elements = {}
    for sym, (Z, per, col, blk) in ELEMENTS.items():
        p = pos3d.get(sym, [0, 0, 0])
        elements[sym] = {
            'Z': Z, 'period': per, 'block': blk,
            'prim': PRIM_LABEL.get(sym, 'Ħ'),
            'fde': FDE_CLASS.get(sym, 'B'),
            'pos': [round(c * WS, 4) for c in p],
            'thread': ('organic' if sym in ORGANIC_SET else
                       'metallic' if sym in METALLIC_SET else None),
        }
    primitives = {}
    for prim, vi in PRIM_VERT.items():
        v = ICO_VERTS[vi]
        primitives[prim] = {
            'pos': [round(c * 6.5 * WS, 4) for c in v],
            'empty': prim in ('Omega', 'R', 'Gamma', 'f') or prim in ('Ŋ', 'Ř', 'Γ', 'ƒ'),
        }
    # Correct empty check using actual prim names
    EMPTY_PRIMS = {'Omega', 'R', 'Gamma', 'f'}
    for prim in primitives:
        primitives[prim]['empty'] = (prim in ('Ω', 'Ř', 'Γ', 'ƒ'))
    return {
        'elements': elements,
        'primitives': primitives,
        'organic_thread':  list(ORGANIC_THREAD),
        'metallic_thread': list(METALLIC_THREAD),
        'ico_verts': [[round(c * 2.2 * WS, 4) for c in v] for v in ICO_VERTS],
        'ico_edges': [[i, j] for i, j in ICO_EDGES],
    }


_HTML_PRE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>IG Periodic Table &#x2014; 3D</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#07090f;overflow:hidden}
#tip{position:absolute;pointer-events:none;background:rgba(6,9,18,.93);color:#bcc9d9;
  border:1px solid #253045;border-radius:7px;padding:9px 13px;font-size:13px;
  line-height:1.7;display:none;max-width:240px;font-family:system-ui,sans-serif}
#hdr{position:absolute;top:14px;left:50%;transform:translateX(-50%);
  color:#2e4460;font-size:12px;font-family:system-ui,sans-serif;letter-spacing:.04em;
  pointer-events:none;white-space:nowrap}
#leg{position:absolute;bottom:18px;left:18px;background:rgba(6,9,18,.88);
  border:1px solid #182030;border-radius:8px;padding:10px 14px;color:#6b7d8e;
  font-size:11.5px;font-family:system-ui,sans-serif;line-height:1.85}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px;vertical-align:middle}
#lbl{position:absolute;top:0;left:0;pointer-events:none;width:100%;height:100%}
</style>
</head>
<body>
<div id="tip"></div>
<div id="hdr">IG Periodic Table &nbsp;&#xB7;&nbsp; 3D &nbsp;|&nbsp; drag: rotate &nbsp;&#xB7;&nbsp; scroll: zoom &nbsp;&#xB7;&nbsp; right-drag: pan &nbsp;&#xB7;&nbsp; hover: inspect &nbsp;&#xB7;&nbsp; R: reset</div>
<div id="leg">
<div><span class="dot" style="background:#2d8a3e"></span>T &#x2014; always Frobenius</div>
<div><span class="dot" style="background:#d4621a"></span>B &#x2014; context Frobenius</div>
<div><span class="dot" style="background:#5a5a5a"></span>F &#x2014; no &#x3B4;</div>
<div><span class="dot" style="background:#c8c8c8"></span>N &#x2014; no stable role</div>
<div style="margin-top:7px;border-top:1px solid #182030;padding-top:7px">
<span style="color:#cc4444">&#x2500;&#x2500;</span> organic &nbsp;
<span style="color:#4466cc">&#x2500;&#x2500;</span> metallic &nbsp;
<span style="color:#9944cc">&#x2500;&#x2500;</span> bridge</div>
</div>
<div id="lbl"></div>
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.155.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.155.0/examples/jsm/"}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const D = """

_HTML_MID = """\
;

const FC={T:'#2d8a3e',B:'#d4621a',F:'#5a5a5a',N:'#c8c8c8'};
const FE={T:'#1a5228',B:'#7c3410',F:'#2a2a2a',N:'#808080'};
const FN={T:'always Frobenius',B:'context Frobenius',F:'no &delta;',N:'no stable role'};

const W=innerWidth,H=innerHeight;
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x07090f);
scene.fog=new THREE.FogExp2(0x07090f,.013);

const cam=new THREE.PerspectiveCamera(46,W/H,.1,400);
cam.position.set(0,3,30);

const rdr=new THREE.WebGLRenderer({antialias:true});
rdr.setSize(W,H);
rdr.setPixelRatio(Math.min(devicePixelRatio,2));
document.body.appendChild(rdr.domElement);

const ctrl=new OrbitControls(cam,rdr.domElement);
ctrl.enableDamping=true;ctrl.dampingFactor=.055;
ctrl.minDistance=4;ctrl.maxDistance=90;
ctrl.autoRotate=true;ctrl.autoRotateSpeed=.35;
rdr.domElement.addEventListener('mousedown',()=>ctrl.autoRotate=false);

scene.add(new THREE.AmbientLight(0xffffff,.45));
const sun=new THREE.PointLight(0xffffff,1.3,200);
sun.position.set(14,10,14);scene.add(sun);
const fill=new THREE.PointLight(0x334499,.7,120);
fill.position.set(-10,-6,-10);scene.add(fill);

// Icosahedron wireframe
{
  const pts=[];
  for(const[i,j]of D.ico_edges)pts.push(...D.ico_verts[i],...D.ico_verts[j]);
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(pts,3));
  scene.add(new THREE.LineSegments(g,new THREE.LineBasicMaterial({color:0x1a2d55,opacity:.45,transparent:true})));
}

// Primitive axis lines from origin
for(const info of Object.values(D.primitives)){
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,...info.pos],3));
  scene.add(new THREE.Line(g,new THREE.LineBasicMaterial({color:info.empty?0x0d1520:0x182840,opacity:.5,transparent:true})));
}

// Thread tubes
function mkTube(syms,col,r){
  r=r||.07;
  const pts=syms.map(s=>new THREE.Vector3(...D.elements[s].pos));
  const crv=new THREE.CatmullRomCurve3(pts);
  const geo=new THREE.TubeGeometry(crv,syms.length*8,r,7,false);
  return new THREE.Mesh(geo,new THREE.MeshPhongMaterial({color:col,emissive:col,emissiveIntensity:.22,shininess:60}));
}
scene.add(mkTube(D.organic_thread,0xcc3333));
scene.add(mkTube(D.metallic_thread,0x3355cc));

// Bridge: last organic -> first metallic
{
  const a=D.elements[D.organic_thread[D.organic_thread.length-1]].pos;
  const b=D.elements[D.metallic_thread[0]].pos;
  const crv=new THREE.CatmullRomCurve3([new THREE.Vector3(...a),new THREE.Vector3(...b)]);
  const geo=new THREE.TubeGeometry(crv,8,.09,7,false);
  scene.add(new THREE.Mesh(geo,new THREE.MeshPhongMaterial({color:0x9933aa,emissive:0x4a1060,emissiveIntensity:.4})));
}

// Element spheres
const gSm=new THREE.SphereGeometry(.21,10,7);
const gLg=new THREE.SphereGeometry(.46,14,10);
const mC={};
function sMat(fde,th){
  const k=fde+''+th;
  if(!mC[k])mC[k]=new THREE.MeshPhongMaterial({
    color:new THREE.Color(FC[fde]),emissive:new THREE.Color(FE[fde]),
    emissiveIntensity:th?.52:.12,shininess:th?90:35,
    transparent:!th,opacity:th?1:.80
  });
  return mC[k];
}

const meshes=[],byM=new Map();
for(const[sym,el]of Object.entries(D.elements)){
  const isT=el.thread!==null;
  const m=new THREE.Mesh(isT?gLg:gSm,sMat(el.fde,isT));
  m.position.set(...el.pos);scene.add(m);
  meshes.push(m);byM.set(m,{sym,...el});
  if(isT){
    // glow sphere behind thread element
    const gc=el.thread==='organic'?0xdd3333:0x4466dd;
    const gm=new THREE.Mesh(
      new THREE.SphereGeometry(.68,10,7),
      new THREE.MeshBasicMaterial({color:gc,transparent:true,opacity:.13,side:THREE.BackSide})
    );
    gm.position.set(...el.pos);scene.add(gm);
  }
}

// Primitive labels projected onto screen via HTML overlay
const lblDiv=document.getElementById('lbl');
const pLbls=[];
for(const[prim,info]of Object.entries(D.primitives)){
  const sp=document.createElement('span');
  sp.textContent=prim;
  sp.style.cssText='position:absolute;font-size:16px;font-family:system-ui,sans-serif;'
    +'pointer-events:none;transform:translate(-50%,-50%);'
    +(info.empty
      ?'color:rgba(70,100,150,.27);'
      :'color:rgba(120,165,235,.72);text-shadow:0 0 10px rgba(80,130,220,.3);');
  lblDiv.appendChild(sp);
  pLbls.push({sp,v:new THREE.Vector3(...info.pos)});
}

// Hover
const ray=new THREE.Raycaster();
const mse=new THREE.Vector2();
const tip=document.getElementById('tip');
let mx=0,my=0;
rdr.domElement.addEventListener('mousemove',e=>{
  mx=e.clientX;my=e.clientY;
  mse.set((e.clientX/W)*2-1,-(e.clientY/H)*2+1);
});

// R key resets camera and re-enables auto-rotation
window.addEventListener('keydown',e=>{
  if(e.key==='r'||e.key==='R'){
    cam.position.set(0,3,30);ctrl.target.set(0,0,0);ctrl.autoRotate=true;
  }
});

// Render loop
const tv=new THREE.Vector3();
(function loop(){
  requestAnimationFrame(loop);
  ctrl.update();
  ray.setFromCamera(mse,cam);
  const hits=ray.intersectObjects(meshes);
  if(hits.length){
    const el=byM.get(hits[0].object);
    tip.innerHTML='<b style="font-size:14px">'+el.sym+'</b>&nbsp;<span style="color:#5a6a7a">Z='+el.Z+'</span><br>'
      +'Period&nbsp;'+el.period+'&nbsp;&middot;&nbsp;Block&nbsp;'+el.block+'<br>'
      +'Primitive:&nbsp;<b>'+el.prim+'</b><br>'
      +el.fde+'&nbsp;&mdash;&nbsp;'+FN[el.fde]
      +(el.thread?'<br><span style="color:#ffcc77">&#x2299;&nbsp;thread&nbsp;('+el.thread+')</span>':'');
    tip.style.display='block';
    tip.style.left=(mx+15)+'px';
    tip.style.top=(my-10)+'px';
  }else{
    tip.style.display='none';
  }
  for(const{sp,v}of pLbls){
    tv.copy(v).project(cam);
    sp.style.left=((tv.x*.5+.5)*W)+'px';
    sp.style.top=((-tv.y*.5+.5)*H)+'px';
    sp.style.opacity=tv.z<1?'1':'0';
  }
  rdr.render(scene,cam);
})();

window.addEventListener('resize',()=>{
  cam.aspect=innerWidth/innerHeight;
  cam.updateProjectionMatrix();
  rdr.setSize(innerWidth,innerHeight);
});
</script>
</body>
</html>"""


if __name__ == '__main__':
    data = build_data()
    data_json = json.dumps(data, separators=(',', ':'))
    html = _HTML_PRE + data_json + _HTML_MID

    out_dir  = Path(__file__).parent
    html_path = out_dir / 'ig_pt_web.html'
    html_path.write_text(html, encoding='utf-8')
    print(f'Wrote {html_path}')

    pdfs = out_dir / 'pdfs'
    if pdfs.exists():
        shutil.copy(html_path, pdfs / 'ig_pt_web.html')
        print(f'Copied -> pdfs/ig_pt_web.html')
