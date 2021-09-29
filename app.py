import json
import pandas as pd
import streamlit as st
from streamlit_player import st_player


st.sidebar.title('VidSitu Dataset Browser')

ANNOT_FILES = {
    'train': 'vidsitu_annotations/vseg_ann_files/vsann_train_lb.json',
    'val': 'vidsitu_annotations/vseg_ann_files/vsann_valid_lb.json',
}

def read_annots(split):
    if split in ANNOT_FILES:
        with open(ANNOT_FILES[split], 'r') as fid:
            annots = json.load(fid)
        st.sidebar.write(f'Split: `{split}` has {len(annots)} annotations')
    return annots

st.sidebar.write('### Pick a split')
split = st.sidebar.radio(label="Splits", options=["train", "val"], index=0)
annots = read_annots(split)


def draw_line():
    st.markdown("""---""")


def process_evrel(n, value):
    # n is already k+1
    if n < 3:
        if value in ['Causes', 'Enables']:
            return f'Ev{n} {value} Ev3'
        else:
            return f'Ev3 {value} Ev{n}'
    elif n > 3:
        if value in ['Causes', 'Enables']:
            return f'Ev3 {value} Ev{n}'
        else:
            return f'Ev{n} {value} Ev3'

    return 'Something fishy!'

def display_annot(sample):
    # get video start/end information
    try:
        # v_hTzUYt__ogY_seg_5_15
        vid_uid, t_start_end = sample['Ev1']['vid_seg_int'].split('_seg_')
        vid_uid = vid_uid[2:]
        t_start, t_end = t_start_end.split('_')
        t_start, t_end = int(t_start), int(t_end)
        st.write(f'Playing video: `{vid_uid}` at {t_start}-{t_end}s')
        st_player(f'https://www.youtube.com/embed/{vid_uid}?start={t_start}&end={t_end}')

        # parse the annotation
        for k, (event) in enumerate(sample.values()):
            st.write(f'#### Video {k+1}')
            # add verb
            d = {'verb/arg': [], 'value': []}
            d['verb/arg'].append(event['VerbID'])
            d['value'].append(event['Verb'])
            # add ev-rel
            d['verb/arg'].append('EvRel')
            d['value'].append(process_evrel(k+1, event['EvRel']) if 'EvRel' in event else '-')
            # noun/arguments
            for arg_key, arg_value in event['Args'].items():
                d['verb/arg'].append(arg_key)
                d['value'].append(arg_value)
            # create dataframe and show
            df = pd.DataFrame(data=d)
            st.dataframe(df)
    
    except:
        st.write('Encountered error. See JSON below')

    draw_line()
    st.write('#### JSON Dump')
    st.text(json.dumps(sample))


st.sidebar.write('### Pick a sample')
imultiplier = 200
index2 = st.sidebar.slider(label=f"Multiplier {imultiplier}x", min_value=0, max_value=(len(annots) // imultiplier))
index1 = st.sidebar.slider(label="Sample", min_value=0, max_value=imultiplier - 1)
index = imultiplier * index2 + index1

st.write(f'Showing sample `{index}`')
display_annot(annots[index])

