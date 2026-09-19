import json, math
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
CONTENT_DEFAULTS={'your_input': 'Your input', 'realise_your_ideas': 'Realise your ideas', 'your_images_your_imagination': 'Your images. Your imagination.', 'framegrid': 'Framegrid', 'make_your': 'Discover what', 'next_idea_real': 'is possible.', 'explore_the_examples': 'Make the most of the latest', 'make_them_your_own': 'AI image generation technology.', 'framegrid_ai': 'framegrid.ai', 'environment': 'Environment', 'character_1': 'Character 1', 'character_2': 'Character 2', 'a_simple_drawing': 'A simple drawing', 'your_direction': 'Your direction', '1000_mph': '“1000 MPH”', 'cinematic_fire': 'Cinematic fire', 'keep_the_composition': 'Keep the composition', 'your_layout': 'Your layout', 'your_furniture': 'Your furniture', 'your_drawing': 'Your drawing', 'generate': 'Generate', 'ready_made_blueprints_and_prompt_help_make_it_easy': 'Ready-made blueprints and prompt help make it easy.', 'illustrated_example': 'Illustrated example', 'generated_result': 'Generated Result', 'illustrated_example_generation_wait_omitted': 'Illustrated example · generation wait omitted', 'describe_the_scene_you_imagine': 'Describe the scene you imagine…', 'add_reference': '+', 'chapter_1_title': 'Create complex scenes using your own input images', 'chapter_2_title': 'Turn a sketch into a product concept', 'chapter_3_title': 'Make a thumbnail from your rough idea', 'chapter_4_title': 'Give your characters a movie poster', 'chapter_5_title': 'Visualise a room with your own furniture', 'chapter_6_title': 'Bring your character drawing to life', 'demo_references_title': '1. Add your reference images', 'demo_prompt_title': '2. Describe your idea', 'demo_result_title': '3. Generate your image', 'demo_prompt': 'Place the woman on the sofa with the lion-cat on her lap.', 'start_with_your_idea': 'Start with your idea', 'closing_guidance': 'With examples and prompt guidance.', 'opening_brand': 'FRAMEGRID'}
ASSET_KEYS={'face2', 'face1', 'sofa', 'cat', 'sketch', 'env', 'cat_single', 'poster', 'logo', 'poster_detail_v6', 'thumb', 'wrist', 'woman', 'char_input', 'scene', 'plan', 'actor2', 'actor1', 'table', 'character_detail_v6', 'rug', 'jewel', 'thumbsketch', 'room', 'char_output'}

def validate_content(data):
    if not isinstance(data,dict) or set(data)!=set(CONTENT_DEFAULTS):
        raise ValueError('content.json must contain exactly the documented text keys')
    for key,value in data.items():
        limit=120 if key.endswith('_title') or key=='demo_prompt' else 80
        if not isinstance(value,str) or not value.strip() or len(value)>limit or any(ord(c)<32 for c in value):
            raise ValueError(f'{key}: enter one nonempty line, at most {limit} characters')
    from PIL import ImageFont
    minimum=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',22)
    narrow={'environment','character_1','character_2','a_simple_drawing','your_direction','1000_mph','cinematic_fire','keep_the_composition','your_layout','your_furniture','your_drawing','your_input'}
    for key,value in data.items():
        width=80 if key=='add_reference' else 220 if key in {'generate','character_1','character_2'} else 500 if key in narrow else 650 if key in {'make_your','next_idea_real','explore_the_examples','make_them_your_own','closing_guidance','framegrid_ai'} else 460 if key=='framegrid' else 1423
        if minimum.getlength(value)>width: raise ValueError(f'{key}: text is too wide; shorten it to fit this layout')
    return data

def load_content():
    return validate_content(json.loads((ROOT/'content.json').read_text(encoding='utf-8-sig')))

def load_assets():
    project=json.loads((ROOT/'project.json').read_text(encoding='utf-8-sig'))
    if set(project)!={'asset_root'} or not isinstance(project['asset_root'],str): raise ValueError('project.json requires asset_root')
    root=(ROOT/project['asset_root']).resolve()
    specs=json.loads((ROOT/'assets.json').read_text(encoding='utf-8-sig'))
    if set(specs)!=ASSET_KEYS: raise ValueError('assets.json must preserve all asset keys')
    images={}; loading=set()
    def load(key):
        if key in images: return images[key]
        if key in loading: raise ValueError('Asset source cycle: '+key)
        loading.add(key); spec=specs[key]
        if not isinstance(spec,dict) or set(spec)-{'path','source','thumbnail','crop_fraction','mode'}: raise ValueError('Invalid asset '+key)
        if ('path' in spec)==('source' in spec): raise ValueError('Asset needs exactly one path or source: '+key)
        mode=spec.get('mode','RGB')
        if mode not in ['RGB','RGBA']: raise ValueError('Asset mode must be RGB or RGBA')
        if 'path' in spec:
            with Image.open(root/spec['path']) as source: im=source.convert(mode)
        else: im=load(spec['source']).copy().convert(mode)
        if 'thumbnail' in spec:
            dims=spec['thumbnail']
            if not isinstance(dims,list) or len(dims)!=2 or any(type(v)!=int or not 1<=v<=8192 for v in dims): raise ValueError('Invalid thumbnail '+key)
            im.thumbnail(tuple(dims))
        if 'crop_fraction' in spec:
            box=spec['crop_fraction']
            if not isinstance(box,list) or len(box)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in box) or not(box[0]<box[2] and box[1]<box[3]): raise ValueError('Invalid crop '+key)
            im=im.crop(tuple(int(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(box)))
            if min(im.size)<1: raise ValueError('Empty crop '+key)
        images[key]=im; loading.remove(key); return im
    for key in specs: load(key)
    return images,specs
