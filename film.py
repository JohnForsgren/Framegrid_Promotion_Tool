"""Horizontal promotion: six matched transformations plus authentic app proof.
Existing gallery images and captured UI; editorial movement is not app behavior.
"""
from pathlib import Path
from functools import lru_cache
import argparse, json, subprocess, hashlib, sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'.packages'))
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import imageio_ffmpeg

R=Path(__file__).resolve().parent; P=R.parent; O=R/'output'; O.mkdir(exist_ok=True)
from config import load_content, load_assets
CONTENT=load_content(); I,ASSET_CONFIG=load_assets(); W,H,FPS=1920,1080,30
T=json.loads((R/'timings.json').read_text(encoding='utf-8-sig'))
def valid_seconds(v,lo,hi):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi:
        raise ValueError(f'Timing must be a finite number between {lo} and {hi}')
if not isinstance(T,dict) or set(T)!={'opening','references','prompt','result','closing','chapters'}: raise ValueError('Invalid timing keys')
if not isinstance(T['chapters'],list): raise ValueError('chapters must be a list')
for k in ['opening','references','prompt','result','closing']: valid_seconds(T[k],.5,60)
if len(T['chapters'])!=6: raise ValueError('Six chapters required')
for chapter_timing in T['chapters']:
    if not isinstance(chapter_timing,dict) or set(chapter_timing)!={'input','reveal','hold'}: raise ValueError('Invalid chapter timing keys')
    for k in ['input','reveal','hold']: valid_seconds(chapter_timing[k],.3,30)
# Round boundaries to frames, so even fractional controls export deterministically.
SEGMENTS=[('opening',T['opening'])]+[(str(i),sum(T['chapters'][i][k] for k in ['input','reveal','hold'])) for i in range(6)]+[(k,T[k]) for k in ['references','prompt','result','closing']]
TIMELINE=[]; cursor=0
for key,seconds in SEGMENTS:
    count=round(seconds*FPS); TIMELINE.append((key,cursor/FPS,count/FPS)); cursor+=count
FRAMES=cursor; SECONDS=FRAMES/FPS
VIDEOS=R/'Videos'; VIDEOS.mkdir(exist_ok=True)
BG=(8,14,23); WHITE=(247,245,238); BLUE=(157,201,255); MUTED=(183,200,219)

def ease(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)
def mix(a,b,q): return a+(b-a)*q
@lru_cache(None)
def font(n,b=True): return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
def text(c,s,x,y,n=48,col=WHITE):
    width=562-x if x<582 and y>=600 else 1888-x
    if y==157 and x==32: width=530
    while n>16 and font(n).getlength(s)>width: n-=1
    ImageDraw.Draw(c).text((round(x),round(y)),s,font=font(n),fill=col,spacing=7)
def base(): return Image.new('RGB',(W,H),BG)
@lru_cache(maxsize=100)
def fitted(k,w,h,mode='contain'):
    im=I[k]
    p=(ImageOps.fit if mode=='cover' else ImageOps.contain)(im,(w,h),Image.Resampling.LANCZOS)
    t=Image.new('RGB',(w,h),BG); t.paste(p,((w-p.width)//2,(h-p.height)//2)); return t
def pic(c,k,box,mode='contain'):
    x,y,w,h=map(round,box); c.paste(fitted(k,w,h,mode),(x,y))
def label(c,s,x,y):
    d=ImageDraw.Draw(c); n=29; width=220 if x in (38,312) else 500
    while n>16 and font(n).getlength(s)>width: n-=1
    wid=font(n).getlength(s)+30
    d.rounded_rectangle((x,y,x+wid,y+46),radius=7,fill=BG)
    d.text((x+15,y+2),s,font=font(n),fill=WHITE)


CHAPTERS=[
 ('COMPLEX SCENES',CONTENT['chapter_1_title'],'Bring your references into one scene.','scene','env'),
 ('PRODUCT CONCEPTS',CONTENT['chapter_2_title'],'Explore how your design could look.','jewel','sketch'),
 ('THUMBNAILS',CONTENT['chapter_3_title'],'Keep your composition. Add the impact.','thumb','thumbsketch'),
 ('MOVIE POSTERS',CONTENT['chapter_4_title'],'Your characters. Your story. Your title.','poster','face1'),
 ('INTERIOR CONCEPTS',CONTENT['chapter_5_title'],'Try your layout before changing the room.','room','plan'),
 ('CHARACTER DESIGN',CONTENT['chapter_6_title'],'Develop the look of a character for your story.','char_output','char_input')]

@lru_cache(maxsize=6)
def source_panel(i):
    c=base()
    if i==0:
        pic(c,'env',(32,208,530,292)); label(c,CONTENT['environment'],44,444)
        pic(c,'cat_single',(32,526,250,470),'cover'); pic(c,'woman',(306,526,256,470),'cover')
        label(c,CONTENT['character_1'],38,943); label(c,CONTENT['character_2'],312,943)
    elif i==1:
        pic(c,'sketch',(32,208,530,704)); text(c,CONTENT['a_simple_drawing'],42,940,34)
    elif i==2:
        pic(c,'thumbsketch',(32,208,530,382)); text(c,CONTENT['your_direction'],42,639,36,BLUE)
        text(c,CONTENT['1000_mph'],42,707,55); text(c,CONTENT['cinematic_fire'],42,801,40); text(c,CONTENT['keep_the_composition'],42,864,37)
    elif i==3:
        pic(c,'face1',(32,208,530,356)); pic(c,'face2',(32,601,530,395))
        label(c,CONTENT['character_1'],44,508); label(c,CONTENT['character_2'],44,940)
    elif i==4:
        pic(c,'plan',(32,208,530,414)); label(c,CONTENT['your_layout'],44,565)
        for j,k in enumerate(['sofa','rug','table']): pic(c,k,(32+j*180,694,170,240))
        text(c,CONTENT['your_furniture'],44,949,34)
    else:
        pic(c,'char_input',(32,208,530,788)); label(c,CONTENT['your_drawing'],44,940)
    return c.crop((0,200,582,1000))

@lru_cache(maxsize=12)
def result_panel(i,after=True):
    c=base(); k=CHAPTERS[i][3 if after else 4]
    # One complete result; the product source is a diptych, so use its single wrist image.
    if after and i==1: k='wrist'
    pic(c,k,(600,208,1288,788))
    return c.crop((600,208,1888,996))

def chapter(i,t):
    c=base(); name,title,purpose,_,_=CHAPTERS[i]
    # Approved long opening copy remains large enough to read and within the safe edge.
    n=55 if i==0 else 64
    text(c,title,32,60,n)
    text(c,CONTENT['your_input'],32,157,30,MUTED)
    timing=T['chapters'][i]
    q=ease((t-timing['input'])/timing['reveal'])
    text(c,CONTENT['generated_result'] if t>=timing['input'] else CONTENT['start_with_your_idea'],600,157,30,BLUE)
    c.paste(source_panel(i),(0,200))
    a=result_panel(i,False); b=result_panel(i,True)
    if q<=0: p=a
    elif q>=1: p=b
    else:
        # Visible editorial transformation between the actual input and actual result.
        x=np.arange(1288)[None,:]; y=np.arange(788)[:,None]
        if i==1: field=np.sqrt(((x-644)/1100)**2+((y-394)/850)**2)
        elif i==3: field=x/1288 + .07*np.sin(np.floor(x/258)*1.7)
        else: field=(x/1288)*.90+(y/788)*.10
        mask=Image.fromarray((np.clip((q*1.2-field)/.12,0,1)*255).astype('uint8')).resize((1288,788))
        p=Image.composite(b,a,mask)
    c.paste(p,(600,208))
    # Hold the complete result; no zoom that trims titles or portrait faces.
    return c

def opening(t):
    c=base()
    # Actual results form a dense image wall, resolving from staggered horizontal strips.
    for j,k in enumerate(['scene','wrist','thumb','poster_detail_v6','room','character_detail_v6']):
        x=(j%3)*640; y=(j//3)*540
        tile=fitted(k,640,540,'cover'); shift=round((1-ease((t-j*.07)/.7))*140)
        c.paste(tile,(x+shift,y))
    overlay=Image.new('RGB',(W,H),BG); c=Image.blend(c,overlay,.53)
    text(c,CONTENT['realise_your_ideas'],74,369,116)
    text(c,CONTENT['your_images_your_imagination'],82,526,53)
    text(c,CONTENT['opening_brand'],84,84,37,BLUE)
    return c

def ui(t):
    # Filled with exact crop geometry after inspection of the existing captures.
    return ui_frame(t)

def closing(t):
    c=base(); q=ease(t/.85)
    for j,k in enumerate(['scene','wrist','thumb','poster','room','char_output']):
        x=32+(j%3)*372; y=160+(j//3)*390
        pic(c,k,(x,y+round(90*(1-q)),356,368),'contain')
    text(c,CONTENT['make_your'],1200,266,76); text(c,CONTENT['next_idea_real'],1200,361,76)
    text(c,CONTENT['explore_the_examples'],1204,514,37,MUTED)
    text(c,CONTENT['make_them_your_own'],1204,568,37,MUTED)
    text(c,CONTENT['closing_guidance'],1204,626,32,MUTED)
    logo=I['logo'].copy(); logo.thumbnail((137,112),Image.Resampling.LANCZOS)
    c.paste(logo,(1200,716),logo)
    text(c,CONTENT['framegrid'],1370,717,66); text(c,CONTENT['framegrid_ai'],1204,858,62,BLUE)
    return c

def segment_frame(key,t):
    if key=='opening': return opening(t*3/T['opening'])
    if key=='closing': return closing(t*4/T['closing'])
    if key.isdigit(): return chapter(int(key),t)
    return simple_demo(key,t,T,I,CONTENT)

def clean_frame(t):
    for j,(key,start,duration) in enumerate(TIMELINE):
        if t<start+duration or j==len(TIMELINE)-1:
            u=max(0,t-start); c=segment_frame(key,u)
            # Demo stages share a canvas and should not flash between states.
            if j and u<.24 and key not in ['prompt','result']:
                prev,_,pd=TIMELINE[j-1]
                return Image.blend(segment_frame(prev,max(0,pd-1/FPS)),c,ease(u/.24))
            return c

def frame(t,demo=False):
    c=clean_frame(t)
    if demo:
        key,start,duration=next(((k,s,d) for k,s,d in TIMELINE if t<s+d),TIMELINE[-1])
        local=max(0,t-start); phase=key; config_key=key
        if key.isdigit():
            i=int(key); v=T['chapters'][i]
            phase='input' if local<v['input'] else 'reveal' if local<v['input']+v['reveal'] else 'hold'
            config_key=f'chapters[{i}].{phase}'
        ImageDraw.Draw(c).rectangle((0,0,1920,48),fill=(0,0,0))
        text(c,f'DEMO | segment {key} | {phase} | {local:.2f}/{duration:.2f}s | video {t:.2f}s | timings.json: {config_key}',20,5,27)
    return c

def previews():
    sh=Image.new('RGB',(1920,4*360),BG)
    for j,(key,start,duration) in enumerate(TIMELINE):
        t=start+max(0,duration-.35); p=frame(t)
        p.save(O/f'review-{key}.jpg',quality=94)
        sh.paste(p.resize((640,360)),((j%3)*640,(j//3)*360))
    sh.save(O/'storyboard.jpg',quality=95); opening(1.4).save(O/'poster.jpg',quality=95)
    trans=Image.new('RGB',(1920,1080),BG)
    samples=[TIMELINE[1][1]+T['chapters'][0]['input']+q*T['chapters'][0]['reveal'] for q in [.1,.5,.9]]
    samples += [TIMELINE[8][1]+T['prompt']*q for q in [.1,.5,.9]]
    samples += [TIMELINE[9][1]+T['result']*q for q in [.1,.5,.9]]
    for j,t in enumerate(samples): trans.paste(frame(t).resize((640,360)),((j%3)*640,(j//3)*360))
    trans.save(O/'transitions.jpg',quality=94)

def render(demo=False):
    ff=imageio_ffmpeg.get_ffmpeg_exe(); tmp=O/'main.partial.mp4'; dest=VIDEOS/('framegrid_main_horizontal_v8_demo.mp4' if demo else 'framegrid_main_horizontal_v8.mp4')
    with (O/'encoder.log').open('w') as log:
        proc=subprocess.Popen([ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],stdin=subprocess.PIPE,stderr=log)
        for i in range(FRAMES):
            proc.stdin.write(frame(i/FPS,demo=demo).tobytes())
            if i%180==0: print(f'{i}/{FRAMES}',flush=True)
        proc.stdin.close(); assert proc.wait()==0
    rd=imageio_ffmpeg.read_frames(str(tmp)); meta=next(rd); n=sum(1 for _ in rd)
    assert n==FRAMES and meta['size']==(W,H) and meta['fps']==FPS and abs(meta['duration']-SECONDS)<.06
    chk=subprocess.run([ff,'-v','error','-i',str(tmp),'-f','null','-'],capture_output=True,text=True)
    assert chk.returncode==0 and not chk.stderr
    tmp.replace(dest)
    (O/('validation_demo.json' if demo else 'validation.json')).write_text(json.dumps({'frames':n,'metadata':meta,'full_decode':'passed','bytes':dest.stat().st_size,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'timings':T,'content':CONTENT,'assets':ASSET_CONFIG,'project':json.loads((R/'project.json').read_text()),'demo':demo,'timeline':TIMELINE,'video':str(dest)},indent=2))
    print('COMPLETE',str(dest),flush=True)

# UI composition is kept in a separate file so its source crops stay auditable.
from simple_demo import simple_demo
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--render',action='store_true'); ap.add_argument('--demo',action='store_true'); args=ap.parse_args(); previews()
    if args.render: render(demo=args.demo)
