# -*- coding: utf-8 -*-
"""Type-led techno-typological analysis of the ORIGINAL GURBELEN-18 columns.

No inferred artifact classifications, no mutation of source data. This module
operates only on the type/subtype values that were actually entered by researchers.
Percent denominators and missingness are explicit at each hierarchy level.
"""
from __future__ import annotations
from collections import defaultdict
from .schema import TABLES

CORE='ÇEKİRDEKLER'; MACRO='MAKROLİTLER'; MICRO='MİKROLİT'
FEATURES={
 CORE:('Alt_tip','Cikarim_yonu','Vurma_düzlemi','Vd/Ry_Acisi','Son_alinan_urun',
       'Alinan_urun_sayisi','Donem','Hammadde','Kabuk','Patina'),
 MACRO:('Alt_tip','Tasimalik','Topuk','Vurma_yumrusu','Kopma_acisi','Cikarim_yonu',
        'Duzelti','Duzeltinin_konumu','Duzeltinin_kapladigi_alan','Kullanim_izi',
        'Budama','Sap_duzeltisi','Hammadde','Kabuk','Patina','Donem'),
 MICRO:('Alt_tip','Tasimalik','Topuk','Vurma_yumrusu','Kopma_Acisi',
        'Duzelti','Duzeltinin_konumu','Duzeltinin_kapladigi_alan','Donem')
}

def _engine():
    # Late import prevents cyclic dependencies with report generation.
    from . import analysis
    return analysis

def _col(df,code):
    from .analysis import norm
    target=norm(code)
    return next((x for x in df.columns if norm(x)==target),None)

def _groups(df,indices,col):
    """Disjoint, one-artifact-per-type groups; unspecified labels remain visible."""
    a=_engine()
    result=defaultdict(list)
    for i in indices:
        raw=a.clean(df.iloc[i][col]) if col else None
        if raw is None:
            label='__missing__'
        else:
            label=a.canonical_source(raw)
        result[label.casefold()].append(i)
    return sorted(((k,v) for k,v in result.items()),key=lambda z:(-len(z[1]),z[0]))

def _node(table,raw,indices,parent_count,base_count,lang,level,field='',children=None):
    a=_engine();src=raw
    if raw=='__missing__':display='Belirtilmemiş' if lang=='tr' else 'Unspecified'
    elif raw=='__typed__':display='Tiplendirilmiş aletler' if lang=='tr' else 'Classified tools'
    elif raw=='__levallois__':display='Levallois çekirdekler' if lang=='tr' else 'Levallois cores'
    else:display=a.localize_category(table,field,raw,lang) if field else a.table_label(raw,lang)
    return {'table':table,'name':str(display),'raw':raw,'count':len(indices),
            'parent_total':int(parent_count),'base_total':int(base_count),
            'parent_pct':round(100*len(indices)/parent_count,1) if parent_count else 0.0,
            'base_pct':round(100*len(indices)/base_count,1) if base_count else 0.0,
            'indices':list(indices),'level':level,'children':children or [],'field':field}

def build_industry_tree(frames,lang='tr'):
    """Return tree with type -> subtype branches and reproducible record indices.

    General Attributes is the assemblage denominator; Cores/Macroliths are
    subsidiary and may overlap, thus root percentages must not be added.
    """
    a=_engine()
    base=len(frames.get('ÖZELLİKLER',[]))
    if not base:base=max((len(x) for x in frames.values()),default=0)
    result=[]
    for table in (CORE,MACRO,MICRO):
        df=frames.get(table)
        if df is None:continue
        all_rows=list(range(len(df)))
        root=_node(table,table,all_rows,base,base,lang,0)
        root['children']=[]
        type_field=_col(df,'Tip_listesi' if table==MACRO else 'Tip')
        sub_field=_col(df,'Alt_tip')
        if not type_field:
            result.append(root);continue
        if table==MACRO:
            selected=[i for i in all_rows if a.clean(df.iloc[i][type_field])]
            typed=_node(table,'__typed__',selected,len(df),base,lang,1)
            root['children'].append(typed)
            parent=typed
        else:parent=root;selected=all_rows
        for key,idxs in _groups(df,selected,type_field):
            raw= a.canonical_source(a.clean(df.iloc[idxs[0]][type_field])) if key!='__missing__' else '__missing__'
            main=_node(table,raw,idxs,len(selected),base,lang,parent['level']+1,type_field)
            parent['children'].append(main)
            if not sub_field:continue
            subgroups=_groups(df,idxs,sub_field)
            levallois=[(k,ids) for k,ids in subgroups if 'levallois' in k and k!='__missing__']
            other=[(k,ids) for k,ids in subgroups if (k,ids) not in levallois]
            if table==CORE and len(levallois)>1:
                lev_ids=[i for _,part in levallois for i in part]
                lev=_node(table,'__levallois__',lev_ids,len(idxs),base,lang,main['level']+1,sub_field)
                for k,sids in levallois:
                    rawsub=a.canonical_source(a.clean(df.iloc[sids[0]][sub_field]))
                    lev['children'].append(_node(table,rawsub,sids,len(lev_ids),base,lang,lev['level']+1,sub_field))
                main['children'].append(lev)
            else:other=levallois+other
            for k,sids in other:
                rawsub=a.canonical_source(a.clean(df.iloc[sids[0]][sub_field])) if k!='__missing__' else '__missing__'
                main['children'].append(_node(table,rawsub,sids,len(idxs),base,lang,main['level']+1,sub_field))
        result.append(root)
    return result

def flatten_tree(nodes):
    for node in nodes:
        yield node
        yield from flatten_tree(node['children'])

def type_detail(frames,node,lang='tr',max_fields=None):
    """Analyze characteristics WITHIN a selected type or subtype, never vice versa."""
    import pandas as pd
    a=_engine();table=node['table'];df=frames[table].iloc[node['indices']]
    fields=[]
    candidates=list(FEATURES.get(table,()))
    for extra in a.eligible_categories(df,table):
        if a.norm(extra) not in {a.norm(c) for c in candidates}:candidates.append(extra)
    own=a.norm(node['field'])
    numerical={a.norm(x) for x in a.numeric_columns(df,table)}
    for requested in candidates:
        col=_col(df,requested)
        if col is None or a.norm(col)==own or a.norm(col) in numerical:continue
        freq,multi,valid=a.frequency(df,col,table,lang)
        if freq.empty:continue
        records=[{'label':str(r.category),'count':int(r['count']),'pct':float(r['percent'])}
                 for _,r in freq.iterrows()]
        fields.append({'name':a.label(table,col,lang),'valid':valid,'missing':len(df)-valid,
                       'multi':bool(multi),'options':records,'field':col})
        if max_fields and len(fields)>=max_fields:break
    numbers=[]
    for col in a.numeric_columns(df,table):
        s=pd.to_numeric(df[col],errors='coerce').dropna()
        if s.empty:continue
        numbers.append({'name':a.label(table,col,lang),'n':len(s),'mean':round(float(s.mean()),2),
                        'median':round(float(s.median()),2),'min':round(float(s.min()),2),'max':round(float(s.max()),2)})
    return {'fields':fields,'metrics':numbers,'count':len(df)}
