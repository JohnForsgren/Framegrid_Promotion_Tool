"""Illustrated explanation, not a recording. Uses matched gallery images."""
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageOps
BG=(8,14,23); PANEL=(18,29,43); WHITE=(247,245,238); BLUE=(157,201,255); MUTED=(183,200,219)
@lru_cache(None)
def font(n): return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',n)
def txt(c,s,x,y,n=44,col=WHITE):
    width=1874-x
    if y==338: width=80
    elif y in [755,762]: width=1423
    elif y==758: width=230
    elif y==569: width=540
    while n>16 and font(n).getlength(s)>width: n-=1
    ImageDraw.Draw(c).text((x,y),s,font=font(n),fill=col,spacing=10)
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
@lru_cache(None)
def fit_image(k,w,h): return ImageOps.contain(IMAGES[k],(w,h),Image.Resampling.LANCZOS)
def pic(c,k,x,y,w,h):
    im=fit_image(k,w,h); c.paste(im,(int(x+(w-im.width)/2),int(y+(h-im.height)/2)))
def pointer(c,x,y,click=False):
    d=ImageDraw.Draw(c)
    if click: d.ellipse((x-24,y-24,x+24,y+24),outline=BLUE,width=4)
    d.polygon([(x,y),(x+7,y+37),(x+15,y+26),(x+28,y+24)],fill=WHITE,outline=BG,width=2)

def simple_demo(stage,t,timings,images,content):
    global IMAGES, CONTENT
    IMAGES=images; CONTENT=content
    c=Image.new('RGB',(1920,1080),BG); d=ImageDraw.Draw(c)
    titles={'references':CONTENT['demo_references_title'],'prompt':CONTENT['demo_prompt_title'],'result':CONTENT['demo_result_title']}
    txt(c,titles[stage],46,48,65)
    if stage=='result':
        pic(c,'scene',360,182,1200,710)
        c=Image.blend(Image.new('RGB',c.size,BG),c,ease(t/min(.65,timings['result']*.25)))
        txt(c,CONTENT['generated_result'],46,170,31,BLUE)
        txt(c,CONTENT['ready_made_blueprints_and_prompt_help_make_it_easy'],46,950,43)
        txt(c,CONTENT['illustrated_example_generation_wait_omitted'],46,1025,25,MUTED)
        return c
    if stage=='references': t=t*3/timings['references']
    for j,(key,label) in enumerate(zip(['env','cat_single','woman'],[CONTENT['environment'],CONTENT['character_1'],CONTENT['character_2']])):
        x=46+j*608; y=180
        d.rounded_rectangle((x,y,x+580,y+451),18,fill=PANEL)
        if stage=='prompt' or t>j*.38:
            drop=round(35*(1-ease((t-j*.38)/.5))) if stage=='references' else 0
            pic(c,key,x+14,y+14+drop,552,359)
            txt(c,label,x+20,y+389,32,MUTED)
        else: txt(c,CONTENT['add_reference'],x+265,y+158,70,BLUE)
    d.rounded_rectangle((46,694,1525,876),18,fill=PANEL,outline=BLUE if stage=='prompt' else (59,76,96),width=3)
    d.rounded_rectangle((1560,694,1870,876),18,fill=BLUE)
    txt(c,CONTENT['generate'],1610,758,45,BG)
    prompt=CONTENT['demo_prompt']
    if stage=='references':
        txt(c,CONTENT['describe_the_scene_you_imagine'],74,755,42,MUTED); pointer(c,1740,590)
    else:
        progress=t/timings['prompt']
        count=round(len(prompt)*max(0,min(1,(progress-.16)/.59)))
        visible=prompt[:count]; prompt_size=39
        while prompt_size>16 and font(prompt_size).getlength(prompt)>1423: prompt_size-=1
        txt(c,visible,74,762,prompt_size)
        if .16<=progress<.79 and int(t*3)%2==0:
            cx=74+font(prompt_size).getlength(visible); d.line((cx,765,cx,811),fill=WHITE,width=3)
        if progress<.16:
            q=ease(progress/.16); pointer(c,1740+(88-1740)*q,590+(770-590)*q,progress>.12)
        elif progress<.8: pointer(c,88,820)
        else:
            q=ease((progress-.8)/.13); pointer(c,88+(1700-88)*q,820+(788-820)*q,progress>.94)
    txt(c,CONTENT['ready_made_blueprints_and_prompt_help_make_it_easy'],46,950,43)
    txt(c,CONTENT['illustrated_example'],46,1025,25,MUTED)
    return c
