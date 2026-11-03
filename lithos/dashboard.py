# -*- coding: utf-8 -*-
"""Data-driven visual dashboard. The values are never baked into the GUI.

Source frames are never modified. Charts deliberately distinguish record counts
in overlapping subsidiary tables from distinct artifact inventory totals.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from .industry import build_industry_tree

PALETTE=['#2794ff','#6bafff','#91caff','#4778bd','#657b9d','#aab8d0','#516785','#95a6c0']


def dashboard_counts(frames,lang='tr'):
    total=len(frames.get('ÖZELLİKLER',[]))
    roots=build_industry_tree(frames,lang)
    by_table={r['table']:r for r in roots}
    core=by_table.get('ÇEKİRDEKLER')
    macro=by_table.get('MAKROLİTLER')
    micro=by_table.get('MİKROLİT')
    typed=macro['children'][0] if macro and macro['children'] and macro['children'][0]['raw']=='__typed__' else None
    counts={'total':total,'tools':typed['count'] if typed else 0,'cores':core['count'] if core else 0,
            'microliths':micro['count'] if micro else 0}
    # Distinct artifact count denominator originates solely in the general inventory.
    return counts,roots


def make_dashboard_charts(frames,dir_path,lang='tr',theme='dark'):
    """Create 2–4 elegant plots from actual typed/core/source variable distributions.

    Returns [(title, png_file)] and creates no fake data plots. Plots are safe
    for datasets with zero records, a single category, or overlapping tables.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from .analysis import frequency, label, table_label

    counts,roots=dashboard_counts(frames,lang)
    by_table={node['table']:node for node in roots}
    out=Path(dir_path);out.mkdir(parents=True,exist_ok=True)
    dark=theme!='light'; fg='#e7edf9' if dark else '#253652'; muted='#a5b6d1' if dark else '#5c6e86';bg='#132238' if dark else '#ffffff'
    titles={
      'tr':('Alet tipleri dağılımı','Tablolara göre kayıtlar','Taşımalık dağılımı','Çekirdek alt tipleri'),
      'en':('Tool-type distribution','Records by table','Blank-type distribution','Core subtypes'),
    }[lang]
    files=[]
    def base():
        fig,ax=plt.subplots(figsize=(5.4,3.15),dpi=136)
        fig.patch.set_facecolor(bg);ax.set_facecolor(bg)
        return fig,ax
    def finish(fig,ax,title,idx):
        fig.savefig(out/f'dashboard_{idx}.png',dpi=136,facecolor=bg,bbox_inches='tight',pad_inches=.13)
        plt.close(fig)
        files.append((title,str(out/f'dashboard_{idx}.png')))
    def donut(pairs,title,idx):
        pairs=[(str(n),int(c)) for n,c in pairs if int(c)>0]
        if not pairs:return
        pairs=sorted(pairs,key=lambda pair:-pair[1])
        if len(pairs)>6:
            others=sum(n for _,n in pairs[5:]);pairs=pairs[:5]+[('Diğer' if lang=='tr' else 'Other',others)]
        fig,ax=base();values=[n for _,n in pairs]
        wedges,_=ax.pie(values,colors=PALETTE[:len(pairs)],radius=.97,startangle=90,
                        wedgeprops={'width':.38,'edgecolor':bg,'linewidth':1.6})
        ax.text(0,.10,str(sum(values)),ha='center',va='center',fontsize=20,color=fg,fontweight='bold')
        ax.text(0,-.19,'n',ha='center',fontsize=10,color=muted)
        ax.legend(wedges,[f'{name}: {n}' for name,n in pairs],loc='center left',
                  bbox_to_anchor=(.94,.5),frameon=False,fontsize=7.5,labelcolor=fg)
        ax.set_aspect('equal');finish(fig,ax,title,idx)
    def bars(pairs,title,idx):
        pairs=[(str(n),int(c)) for n,c in pairs if int(c)>0]
        if not pairs:return
        fig,ax=base();labels=[p[0] for p in pairs]; values=[p[1] for p in pairs]
        ax.bar(range(len(pairs)),values,color=PALETTE[:len(pairs)],width=.58)
        ax.set_xticks(list(range(len(pairs))),labels,fontsize=8,color=fg)
        ax.tick_params(axis='y',colors=muted,length=0,labelsize=8)
        ax.tick_params(axis='x',colors=muted,length=0)
        ax.grid(axis='y',alpha=.13,color=muted);ax.set_axisbelow(True)
        for side in ax.spines.values():side.set_visible(False)
        for i,value in enumerate(values):ax.text(i,value+max(values)*.03,str(value),ha='center',va='bottom',color=fg,fontsize=9)
        ax.set_ylim(0,max(values)*1.23)
        finish(fig,ax,title,idx)
    macro=by_table.get('MAKROLİTLER')
    if macro and macro['children']:
        typed=macro['children'][0]
        if typed['raw']=='__typed__':donut([(n['name'],n['count']) for n in typed['children']],titles[0],1)
    # Table membership is overlapping; chart explicitly says records by table.
    bars([(table_label(t,lang),len(frames.get(t,[]))) for t in ('ÇEKİRDEKLER','MAKROLİTLER','MİKROLİT')],titles[1],2)
    df=frames.get('MAKROLİTLER')
    if df is not None and not df.empty:
        col=next((c for c in df.columns if c.casefold().replace('_','')=='tasimalik'),None)
        if col:
            counts_df,_,_=frequency(df,col,'MAKROLİTLER',lang)
            donut([(str(r.category),r['count']) for _,r in counts_df.iterrows()],titles[2],3)
    core=by_table.get('ÇEKİRDEKLER')
    if core and core['children']:
        children=[]
        for node in core['children']:
            children.extend(node['children'])
        if children:donut([(n['name'],n['count']) for n in children],titles[3],4)
    return files
