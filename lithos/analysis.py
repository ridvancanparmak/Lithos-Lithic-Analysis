# -*- coding: utf-8 -*-
"""Bilingual descriptive statistics and Word reports.

No categorical value is machine-translated: original source values are retained
for auditability. Standard controlled codes can be rendered bilingually.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime
from pathlib import Path
import math
import csv
from functools import lru_cache
import re
import tempfile
import unicodedata

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from .schema import TABLE_MAP,field_label,term_label,VOCABULARY,canonical_table
from .repository import DataStore

TEXTS={
 'tr': {
  'title':'PALEOLİTİK YONTMATAŞ TOPLULUĞU','subtitle':'Teknolojik, tipolojik ve ölçüsel analiz raporu',
  'source':'Kaynak veritabanı','date':'Rapor tarihi','summary':'Veri özeti','methods':'Yöntem ve kapsam',
  'method1':'Bu rapor, Lithos veritabanındaki kayıtların betimleyici incelemesini sunar. Kayıtlar kaynak veritabanı değiştirilmeden okunmuştur.',
  'method2':'Frekanslar kayıtlı kategorilerden, yüzdeler ilgili değişkende geçerli değer bulunan kayıtlardan hesaplanmıştır. Noktalı virgülle ayrılmış çoklu değerlerin frekansları birlikte bulunma sıklığını gösterir ve toplamları %100’ü aşabilir.',
  'method3':'Ölçüsel analizlerde yalnızca geçerli sayısal değerler kullanılmıştır. Bulgular betimleyicidir; örüntülerden doğrudan kronolojik, kültürel ya da nedensel sonuç çıkarılmaz.',
  'table_coverage':'Tablo ve kayıt kapsamı','table':'Tablo','records':'Kayıt','fields':'Alan','unique':'Benzersiz kimlik',
  'data_quality':'Veri kalitesi','missing':'Eksik','valid':'Geçerli','duplicate':'Yinelenen kimlik',
  'frequencies':'Kategorik ve teknolojik değişkenler','metrics':'Ölçüsel değişkenler',
  'category':'Kategori','frequency':'Frekans','pct':'Geçerli kayıt (%)','n':'n',
  'mean':'Ortalama','median':'Medyan','sd':'Std. sapma','min':'Min.','max':'Maks.',
  'std':'Standart sapma','no_records':'Bu tabloda analiz edilebilir veri bulunmuyor.',
  'relations':'Değişkenler arası dağılımlar','observations':'Veri temelli gözlemler',
  'limit':'Sınırlılıklar ve tekrarlanabilirlik','source_file':'Kaynak dosya','read_only':'Kaynak veritabanı değiştirilmemiştir.',
  'generated':'Lithos v1.0 ile oluşturulmuştur','untranslated':'Kullanıcı tarafından girilen serbest metinler ve standart sözlük dışındaki kategori değerleri özgün dilinde korunur.',
  'highest':'En sık kaydedilen kategori','observed':'Kayıtlı geçerli değerler içinde',
  'multi':'Çoklu değerler bağımsız olarak sayılmıştır.','no_data':'Kayıt yok',
  'total':'Toplam kayıt','distinct':'Benzersiz kayıt kimliği','coverage_note':'Alt tablolardaki kayıtlar aynı buluntuyu temsil edebilir; tablo toplamları doğrudan toplanmamalıdır.',
  'cross_note':'Bu çapraz tablo birlikte kaydedilmiş kategorileri gösterir; nedensellik kanıtı değildir.',
  'all':'Tüm veriler','page':'Sayfa',
 },
 'en': {
  'title':'PALAEOLITHIC LITHIC ASSEMBLAGE','subtitle':'Technological, typological and metrical analysis report',
  'source':'Source database','date':'Report date','summary':'Data overview','methods':'Methods and scope',
  'method1':'This report provides a descriptive assessment of records in the Lithos database. The source database was read without modification.',
  'method2':'Frequencies are derived from recorded categories; percentages use the number of records with valid values in each variable as their denominator. Semicolon-delimited multiple values represent co-occurrence and their percentages may total more than 100%.',
  'method3':'Only valid numeric measurements are used for metrical analysis. Findings are descriptive: chronological, cultural or causal interpretations are not inferred from distributions alone.',
  'table_coverage':'Table and record coverage','table':'Table','records':'Records','fields':'Fields','unique':'Unique identifiers',
  'data_quality':'Data quality','missing':'Missing','valid':'Valid','duplicate':'Duplicate identifier',
  'frequencies':'Categorical and technological variables','metrics':'Metrical variables',
  'category':'Category','frequency':'Frequency','pct':'Valid records (%)','n':'n',
  'mean':'Mean','median':'Median','sd':'SD','min':'Min.','max':'Max.',
  'std':'Standard deviation','no_records':'No analyzable records in this table.',
  'relations':'Relationships between recorded variables','observations':'Data-derived observations',
  'limit':'Limitations and reproducibility','source_file':'Source file','read_only':'The source database has not been modified.',
  'generated':'Generated with Lithos v1.0','untranslated':'User-entered free text and category values outside the controlled vocabulary are preserved in their original language.',
  'highest':'Most frequently recorded category','observed':'Among valid recorded values',
  'multi':'Multiple values were counted separately.','no_data':'No records',
  'total':'Total records','distinct':'Unique record identifiers','coverage_note':'Records in subsidiary tables may refer to the same artifact; table totals must not simply be added together.',
  'cross_note':'This cross-tabulation represents recorded co-occurrence and does not establish causality.',
  'all':'All data','page':'Page',
 }
}
LEGACY_LABELS={
 'ozellikler':('Genel Özellikler','General Attributes'),
 'cekirdekler':('Çekirdekler','Cores'),
 'makrolitler':('Makrolitler','Macroliths'),
 'mikrolit':('Mikrolitler','Microliths'),
 'analiz_no':('Analiz No','Analysis No'),
 'buluntu_alani':('Buluntu Alanı','Find Area'),
 'cizim':('Çizim','Drawing'),
 'fotograf':('Fotoğraf','Photograph'),
 'yil':('Yıl','Year'),
 'cizim_no':('Çizim Numarası','Drawing Number'),
 'buluntu_grubu':('Buluntu Grubu','Artifact Group'),
 'hammadde':('Hammadde','Raw Material'),
 'hammadde_rengi':('Hammadde Rengi','Raw Material Colour'),
 'kabuk':('Kabuk','Cortex'),
 'ham_yuz':('Ham Yüz','Cortical Surface'),
 'patina':('Patina','Patina'),
 'kirik_kirik_alan':('Kırık / Kırık Alan','Breakage'),
 'tasimalik':('Taşımalık','Blank Type'),
 'topuk':('Topuk','Striking Platform'),
 'vurma_yumrusu':('Vurma Yumrusu','Bulb of Percussion'),
 'kopma_acisi':('Kopma Açısı','Angle of Detachment'),
 'tip':('Tip','Type'),
 'alt_tip':('Alt Tip','Subtype'),
 'tip_listesi':('Tip Listesi','Tool Type List'),
 'cikarim_yonu':('Çıkarım Yönü','Scar Direction'),
 'vurma_duzlemi':('Vurma Düzlemi','Striking Platform'),
 'son_alinan_urun':('Son Alınan Ürün','Last Removed Product'),
 'donem':('Dönem','Period'),
 'duzelti':('Düzelti','Retouch'),
 'duzeltinin_konumu':('Düzelti Konumu','Retouch Location'),
 'duzeltinin_kapladigi_alan':('Düzelti Yayılımı','Retouch Coverage'),
 'kullanim_izi':('Kullanım İzi','Use-Wear'),
 'uzunluk':('Uzunluk','Length'),
 'genislik':('Genişlik','Width'),
 'kalinlik':('Kalınlık','Thickness'),
 'kategori':('Kategori','Category'),
 'frekans':('Frekans','Frequency'),
 'yuzde':('Yüzde','Percentage'),
 'alınan_urun_sayisi':('Alınan Ürün Sayısı','Number of Removed Products'),
 'alinan_urun_sayisi':('Alınan Ürün Sayısı','Number of Removed Products'),
}

@lru_cache(maxsize=1)
def _original_gurbelen_labels():
    """Original field identifiers and their English presentation labels."""
    location=Path(__file__).resolve().parents[1]/'veri_sozlugu'/'GURBELEN18_alan_basliklari_TR_EN.csv'
    if not location.is_file():return {}
    with location.open(encoding='utf-8-sig',newline='') as stream:
        return {(r['Table'],r['Field']):r['EnglishCaption'] for r in csv.DictReader(stream)}

@lru_cache(maxsize=1)
def _original_gurbelen_lookups():
    """Controlled original dropdown choices translated; free text remains source language."""
    location=Path(__file__).resolve().parents[1]/'veri_sozlugu'/'GURBELEN18_lookup_TR_EN.csv'
    if not location.is_file():return {}
    with location.open(encoding='utf-8-sig',newline='') as stream:
        return {(r['Table'],r['Field'],r['Turkish']):r['English'] for r in csv.DictReader(stream)}

def norm(text):
    s=str(text).strip().casefold().replace('ı','i')
    s=unicodedata.normalize('NFKD',s)
    return re.sub('[^a-z0-9]+','_', ''.join(x for x in s if not unicodedata.combining(x))).strip('_')


def label(table,column,language):
    table=canonical_table(table)
    if column is None:
        return ''
    if table in TABLE_MAP:return field_label(table,column,language)
    if language=='en':
        translated=_original_gurbelen_labels().get((table,str(column)))
        if translated:return translated
    entry=LEGACY_LABELS.get(norm(column))
    return entry[0 if language=='tr' else 1] if entry else str(column).replace('_',' ')


def table_label(name,lang):
    name=canonical_table(name)
    t=TABLE_MAP.get(name)
    if t:return t.tr if lang=='tr' else t.en
    row=LEGACY_LABELS.get(norm(name))
    return row[0 if lang=='tr' else 1] if row else name


def clean(value):
    if value is None:return None
    try:
        if pd.isna(value):return None
    except (ValueError,TypeError):pass
    text=str(value).strip()
    return None if not text or text.casefold() in ('nan','none','null','-') else text


def frequency(df,col,table,lang):
    if col not in df.columns or df.empty:return pd.DataFrame(columns=['category','count','percent']),False,0
    vals=[clean(v) for v in df[col]]
    valid=[v for v in vals if v is not None]
    if not valid:return pd.DataFrame(columns=['category','count','percent']),False,0
    multi=any(';' in v for v in valid)
    values=[]
    for v in valid:
        segments=[s.strip() for s in v.split(';') if s.strip()]
        # prevent duplicate category within the same artifact
        values.extend(dict.fromkeys(segments))
    # Case variants of the same recorded category are merged without touching
    # Access (e.g. "Döküntü" and "döküntü"). Preserve >/< distinct values.
    grouped=Counter()
    display={}
    for value in values:
        category=canonical_source(value)
        key=category.casefold()
        grouped[key]+=1
        display.setdefault(key,category)
    fld=next((f for f in TABLE_MAP[table].fields if f.code==col),None) if table in TABLE_MAP else None
    result=[]
    for key,count in grouped.most_common():
        source=display[key]
        disp=(term_label(fld.lookup,source,lang) if fld and fld.lookup else
              localize_category(table,col,source,lang))
        result.append((disp,count,round(count/len(valid)*100,1)))
    return pd.DataFrame(result,columns=['category','count','percent']),multi,len(valid)



@lru_cache(maxsize=1)
def _supplemental_translations():
    path=Path(__file__).resolve().parents[1]/'veri_sozlugu'/'GURBELEN18_ek_serbest_terimler_TR_EN.csv'
    if not path.exists():return {}
    with path.open(encoding='utf-8-sig',newline='') as stream:
        return {str(r['Turkish']).strip().casefold():r['English'] for r in csv.DictReader(stream)}

@lru_cache(maxsize=1)
def _indexed_lookups():
    # An exact field match takes precedence; global fallback is allowed only for
    # consistently translated values across the source controlled vocabulary.
    exact={};global_candidates={}
    for (table,field,turkish),english in _original_gurbelen_lookups().items():
        key=(str(table).casefold(),str(field).casefold(),str(turkish).strip().casefold())
        exact[key]=english
        global_candidates.setdefault(str(turkish).strip().casefold(),set()).add(str(english))
    unique={k:next(iter(v)) for k,v in global_candidates.items() if len(v)==1}
    return exact,unique

def canonical_source(value):
    raw=str(value).strip()
    aliases={'makrolit parça':'Makrolit parçası','döküntü':'Döküntü',
             'makro çentikli':'Makro çentikli','kabuk çıkarma yongası':'Kabuk çıkarma yongası'}
    return aliases.get(raw.casefold(),raw)

def localize_category(table,col,value,lang):
    table=canonical_table(table)
    source=canonical_source(value)
    if lang!='en':return source
    exact,unique=_indexed_lookups()
    key=(str(table).casefold(),str(col).casefold(),source.casefold())
    if key in exact:return exact[key]
    if source.casefold() in _supplemental_translations():return _supplemental_translations()[source.casefold()]
    if source.casefold() in unique:return unique[source.casefold()]
    # Composite researcher-entered categories can combine known terms with '+' or ';'.
    # Translate only recognized components; unfamiliar scientific terms remain intact.
    if '+' in source or ';' in source:
        pieces=re.split(r'([;+])',source)
        converted=[]
        for piece in pieces:
            if piece in ('+',';'):
                converted.append(' '+piece+' ')
            else:
                core=piece.strip()
                converted.append(localize_category(table,col,core,lang) if core else '')
        return re.sub(r'\s+',' ',''.join(converted)).strip()
    return source

def eligible_categories(df,table):
    numbers=set(numeric_columns(df,table))
    skip={'id','project_id','context_id','artifact_id','core_id','macrolith_id','microlith_id',
          'image_id','term_id','inventory_no','notes','description','created_on','file_path',
          'analiz_no','aciklama','foto','cizim','yil','cizim_no','fotograf'}
    candidates=[]
    for col in df.columns:
        if col in numbers or norm(col) in skip:continue
        if not df.empty and sum(clean(v) is not None for v in df[col])==0:continue
        candidates.append(col)
    return candidates

def generate_observations(frames,lang='tr',max_per_table=None):
    """All nonempty categorical fields plus metrical and coverage findings.
    Each result is derived from the same frequency() used by Word tables/charts.
    """
    findings={}
    for name,df in frames.items():
        rows=[]
        if df.empty:
            findings[name]=rows;continue
        cols=eligible_categories(df,name)
        if max_per_table is not None:cols=cols[:max_per_table]
        for col in cols:
            freqs,multi,valid=frequency(df,col,name,lang)
            if freqs.empty:continue
            first=freqs.iloc[0]
            f=label(name,col,lang);v=first['category'];count=int(first['count']);pct=first['percent']
            if lang=='tr':
                line=f'{f}: {valid} geçerli kayıtta en sık “{v}” ({count}; %{pct:.1f}).'
            else:
                line=f'{f}: “{v}” is most frequent among {valid} valid records ({count}; {pct:.1f}%).'
            if len(freqs)>1:
                second=freqs.iloc[1]
                if lang=='tr':line+=f' İkinci sırada “{second.category}” ({int(second["count"])}; %{second["percent"]:.1f}) yer alır.'
                else:line+=f' Next is “{second.category}” ({int(second["count"])}; {second["percent"]:.1f}%).'
            if multi:
                line+=' Çoklu değerler nedeniyle yüzdeler %100’ü aşabilir.' if lang=='tr' else ' Percentages can exceed 100% for multiple responses.'
            if valid<len(df):
                miss=len(df)-valid
                line+=(f' {miss} kayıtta değer eksik.' if lang=='tr' else f' {miss} records are missing this value.')
            rows.append(line)
        for col in numeric_columns(df,name):
            series=pd.to_numeric(df[col],errors='coerce').dropna()
            if not len(series):continue
            unit=' mm' if any(w in norm(col) for w in ('uzunluk','genislik','kalinlik')) else ''
            f=label(name,col,lang)
            if lang=='tr':
                rows.append(f'{f}: n={len(series)}; ortalama {series.mean():.2f}{unit}, medyan {series.median():.2f}{unit}, aralık {series.min():.2f}–{series.max():.2f}{unit}.')
            else:
                rows.append(f'{f}: n={len(series)}; mean {series.mean():.2f}{unit}, median {series.median():.2f}{unit}, range {series.min():.2f}–{series.max():.2f}{unit}.')
        findings[name]=rows
    return findings

def numeric_columns(df,table):
    result=[]
    metadata=TABLE_MAP.get(table)
    if metadata:
        for f in metadata.fields:
            if f.kind in ('number','integer') and f.code in df.columns:result.append(f.code)
    else:
        for c in df.columns:
            key=norm(c)
            if any(k in key for k in ('uzunluk','genislik','kalinlik','agirlik','alinan_urun_sayisi')):
                result.append(c)
    return result


def analysis_tables(database):
    store=DataStore(database)
    frames=store.read_for_analysis()
    # exclude metadata/terms (handled by repository), but allow any legacy table.
    return frames,store.is_standard()


def compute_summary(frames,lang='tr'):
    msg=TEXTS[lang]
    result={}
    for name,df in frames.items():
        candidates=['artifact_id','analiz_no','Analiz_No','inventory_no']
        id_col=next((c for c in df.columns if norm(c) in [norm(x) for x in candidates]),None)
        unique=int(df[id_col].dropna().astype(str).nunique()) if id_col else len(df)
        duplicates=int(len(df[id_col].dropna())-unique) if id_col else 0
        fields=[]
        for col in df.columns:
            if norm(col) in ('notes','aciklama','caption_tr','caption_en','description','definition_tr','definition_en','file_path'):continue
            non_null=sum(clean(v) is not None for v in df[col])
            fields.append(dict(field=col,valid=non_null,missing=len(df)-non_null))
        result[name]={'rows':len(df),'columns':len(df.columns),'unique':unique,'duplicates':duplicates,'fields':fields}
    return result


def _document_table(doc,headers,rows,max_rows=35):
    if not rows:return
    table=doc.add_table(rows=1,cols=len(headers))
    table.style='Light Shading Accent 1'
    for i,h in enumerate(headers):table.rows[0].cells[i].text=str(h)
    for record in rows[:max_rows]:
        cells=table.add_row().cells
        for i,value in enumerate(record):cells[i].text=str(value)
    # Repeat the header on a new page; never split a scientific row across pages.
    for i,row in enumerate(table.rows):
        trPr=row._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))
        if i==0:trPr.append(OxmlElement('w:tblHeader'))
    doc.add_paragraph('')


def _setup_document(doc,lang):
    sec=doc.sections[0]
    sec.top_margin=Cm(2.2);sec.bottom_margin=Cm(2.0)
    sec.left_margin=Cm(2.5);sec.right_margin=Cm(2.5)
    normal=doc.styles['Normal'];normal.font.name='DejaVu Sans';normal.font.size=Pt(9)
    normal.paragraph_format.space_after=Pt(6)
    for kind,size in [('Title',19),('Heading 1',13),('Heading 2',11)]:
        st=doc.styles[kind];st.font.name='DejaVu Sans';st.font.size=Pt(size)
        st.font.color.rgb=RGBColor(25,58,92)
    foot=sec.footer.paragraphs[0]
    foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    foot.add_run('Lithos v1.0 | '+TEXTS[lang]['page']+' ')
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE')
    foot._p.append(field)


def _plot_frequency(freq,title,path,lang):
    top=freq.head(10).iloc[::-1]
    if top.empty:return None
    height=max(2.5,min(5.8,1.0+0.34*len(top)))
    fig,ax=plt.subplots(figsize=(9.2,height))
    ax.barh(top.category.astype(str),top['count'],color='#2468b4')
    ax.set_xlabel(TEXTS[lang]['frequency'])
    ax.set_title(title,fontsize=11)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout()
    fig.savefig(path,dpi=160,bbox_inches='tight')
    plt.close(fig)
    return path



# The pie charts below restore the analytical figures present in the original
# GURBELEN-18 report engine (main_duzeltilmis.py), which were lost in the 1.0 UI rewrite.
LEGACY_PIE_FIELDS={
    'cekirdekler':('tip','alt_tip'),
    'makrolitler': ('tip_listesi','alt_tip'),
    'mikrolit': ('tip','alt_tip'),
}
LEGACY_PIE_CROSSES={
    'cekirdekler':(('tip','son_alinan_urun'),('alt_tip','cikarim_yonu'),('alt_tip','vurma_duzlemi')), 
    'makrolitler':(('tip_listesi','tasimalik'),('tip_listesi','duzelti'),('alt_tip','tasimalik'),('tip_listesi','duzeltinin_konumu'),('tip_listesi','duzeltinin_kapladigi_alan')),
    'mikrolit':(('tip','alt_tip'),),
}

def _find_field(df, requested):
    return next((c for c in df.columns if norm(c)==norm(requested)),None)

def _pie_chart(counts,title,path,lang,max_slices=12):
    """Pie with readable outside legend; never chart invalid or single-value data."""
    series=[(str(k),int(v)) for k,v in counts if v and int(v)>0]
    if len(series)<2:return None
    series.sort(key=lambda kv:-kv[1])
    if len(series)>max_slices:
        rest=sum(n for _,n in series[max_slices-1:])
        other='Diğer' if lang=='tr' else 'Other'
        series=series[:max_slices-1]+[(other,rest)]
    labels=[x for x,_ in series]; values=[y for _,y in series]
    fig,ax=plt.subplots(figsize=(9,5.4))
    wedges,_,pct=ax.pie(values,autopct=lambda x: f'{x:.1f}%' if x>=3 else '',startangle=92,pctdistance=.78)
    for t in pct:t.set_fontsize(9)
    ax.legend(wedges,[f'{n}: {v}' for n,v in series],loc='center left',bbox_to_anchor=(1.02,.5),fontsize=8,frameon=False)
    ax.axis('equal'); ax.set_title(title,fontsize=11,pad=13)
    fig.tight_layout()
    fig.savefig(path,dpi=160,bbox_inches='tight')
    plt.close(fig)
    return path

def _split_pie(value):
    raw=clean(value)
    if raw is None:return []
    return list(dict.fromkeys(x.strip() for x in raw.split(';') if x.strip()))

def _legacy_pies(doc,name,df,lang,temp,charts,saved_charts,detailed=True):
    """Restore frequency pies and conditional cross-analysis pies on original fields."""
    if not charts or df.empty:return
    table_key=norm(name)
    for requested in LEGACY_PIE_FIELDS.get(table_key,()):
        col=_find_field(df,requested)
        if col is None:continue
        freq,multi,_=frequency(df,col,name,lang)
        if len(freq)<2:continue
        title=table_label(name,lang)+' — '+label(name,col,lang)
        path=temp/f'pie_{len(saved_charts)+1:03}.png'
        p=_pie_chart([(r.category,r['count']) for _,r in freq.iterrows()],title,path,lang)
        if p:
            doc.add_heading(('Pasta Grafik / Kategori Dağılımı' if lang=='tr' else 'Pie Chart / Category Distribution'),2)
            doc.add_paragraph(title)
            _insert_chart(doc,p);saved_charts.append(str(p))
            if multi:doc.add_paragraph(TEXTS[lang]['multi'])
    pairs=LEGACY_PIE_CROSSES.get(table_key,())
    max_per_pair=3 if detailed else 1
    total_cross=0
    for req_a,req_b in pairs:
        if total_cross>=20:break
        a=_find_field(df,req_a);b=_find_field(df,req_b)
        if not a or not b:continue
        # Count the distribution of B among records sharing A, keeping original categories.
        groups={}
        for av,bv in zip(df[a],df[b]):
            left=_split_pie(av);right=_split_pie(bv)
            for al in left:
                bucket=groups.setdefault(al,Counter())
                for br in right:bucket[br]+=1
        eligible=sorted(groups.items(),key=lambda item:-sum(item[1].values()))
        used=0
        for category,counter in eligible:
            if used>=max_per_pair or total_cross>=20:break
            if len([x for x in counter.values() if x>0])<2:continue
            rendered_category=localize_category(name,a,category,lang)
            title='%s — %s: %s / %s' % (
                table_label(name,lang),label(name,a,lang),rendered_category,label(name,b,lang))
            path=temp/f'cross_pie_{len(saved_charts)+1:03}.png'
            counts_for_chart=[(localize_category(name,b,k,lang), v)
                              for k,v in counter.most_common()]
            p=_pie_chart(counts_for_chart,title,path,lang)
            if p:
                if used==0:
                    doc.add_heading((f'{label(name,a,lang)} × {label(name,b,lang)} — çapraz pasta grafikler' if lang=='tr'
                                     else f'{label(name,a,lang)} × {label(name,b,lang)} — cross-analysis pie charts'),2)
                _insert_chart(doc,p);saved_charts.append(str(p));used+=1;total_cross+=1
        if used:
            doc.add_paragraph('Grafikler, ilgili kategoride kaydedilen birlikte görülme frekanslarını gösterir; nedensellik ifade etmez.' if lang=='tr'
                              else 'Charts show frequencies of recorded co-occurrences, not causality.')

def _type_hierarchy_report(doc,frames,lang):
    """Type/subtype as organizing axis, technology as the characteristic subset."""
    from .industry import build_industry_tree, flatten_tree, type_detail
    nodes=build_industry_tree(frames,lang)
    if not nodes:return
    doc.add_heading(('Endüstrinin tipolojik dağılımı' if lang=='tr' else
                     'Typological distribution of the assemblage'),1)
    doc.add_paragraph(('Yüzdeler her satırın üst grubunu esas alır; toplam endüstri oranı ayrı hesaplanır. '
                       'Çekirdek ve makrolit alt tablolarındaki kayıtlar örtüşebileceği için toplamları toplanmaz.'
                      if lang=='tr' else
                      'Percentages are calculated within each parent group; the assemblage share is separate. '
                      'Core and macrolith tables may overlap and their totals must not be added.'))
    rows=[]
    def visit(items,prefix=''):
        for i,node in enumerate(items,1):
            code=f'{prefix}.{i}' if prefix else str(i)
            rows.append((('  '*node['level'])+code+' '+node['name'],
                         node['count'],f"{node['parent_pct']:.1f}",f"{node['base_pct']:.1f}"))
            visit(node['children'],code)
    visit(nodes)
    _document_table(doc,['Tip / Alt tip' if lang=='tr' else 'Type / Subtype',
                         'Adet' if lang=='tr' else 'Count',
                         'Üst grup (%)' if lang=='tr' else 'Parent (%)',
                         'Topluluk (%)' if lang=='tr' else 'Assemblage (%)'],rows,max_rows=200)
    return nodes


def _typeled_details_report(doc,frames,name,tree,lang):
    """Each main core/tool type controls the comparisons. Subtypes inherit that scope."""
    from .industry import type_detail
    group=next((x for x in tree if x['table']==name),None)
    if not group or not group['count']:return
    doc.add_heading(('Tip merkezli teknolojik analiz' if lang=='tr' else
                     'Type-led technological analysis'),2)
    mains=group['children']
    if name=='MAKROLİTLER' and mains:mains=mains[0]['children']
    for main in mains:
        if not main['count']:continue
        doc.add_heading(f"{main['name']} (n={main['count']}; {main['parent_pct']:.1f}%)",3)
        detail=type_detail(frames,main,lang,max_fields=11)
        rows=[]
        for info in detail['fields']:
            if not info['options']:continue
            top=info['options'][0]
            rows.append([info['name'],f"{top['label']} ({top['count']}; {top['pct']:.1f}%)",
                         info['valid'],info['missing']])
        if rows:_document_table(doc,[('Özellik' if lang=='tr' else 'Variable'),
                                ('En sık gözlenen' if lang=='tr' else 'Most frequent'),
                                ('Geçerli' if lang=='tr' else 'Valid'),
                                ('Eksik' if lang=='tr' else 'Missing')],rows,max_rows=14)
        for metric in detail['metrics']:
            doc.add_paragraph((f"{metric['name']}: n={metric['n']}, ortalama {metric['mean']}, "
                               f"medyan {metric['median']}, min.–maks. {metric['min']}–{metric['max']}."
                              if lang=='tr' else
                              f"{metric['name']}: n={metric['n']}, mean {metric['mean']}, "
                              f"median {metric['median']}, min–max {metric['min']}–{metric['max']}."))
        # Every recorded subtype receives a separate data-derived summary.
        subtypes=list(main['children'])
        if not subtypes:continue
        doc.add_paragraph(('Alt tipler:' if lang=='tr' else 'Subtypes:'))
        def emit_child(node,prefix=''):
            if node['children']:
                for child in node['children']:emit_child(child,prefix)
                return
            child_detail=type_detail(frames,node,lang,max_fields=7)
            desc=[]
            for field in child_detail['fields']:
                if not field['options']:continue
                top=field['options'][0]
                desc.append(f"{field['name']}: {top['label']} ({top['count']}/{field['valid']}; {top['pct']:.1f}%)")
            line=f"{node['name']} — n={node['count']} ({node['parent_pct']:.1f}%): "+'; '.join(desc[:7])
            doc.add_paragraph(line,style='List Bullet')
        for node in subtypes:emit_child(node)


def _insert_chart(doc,chart_path):
    doc.add_picture(str(chart_path),width=Cm(14.5))
    doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER




def _write_translation_review(frames,report_path):
    """Flag unknown, possibly Turkish recorded categories rather than silently claiming full translation.
    This never edits user data. Controlled dropdown values are handled by the glossary.
    """
    watch_terms=re.compile(r'\b(?:yonga|dilgi|çekirdek|paleolitik|kazıyıcı|düzelti|çentikli|dişlemeli|makrolit|mikrolit)\b',re.I)
    unresolved=[]
    for table,df in frames.items():
        for col in eligible_categories(df,table):
            found=set()
            for value in df[col]:
                raw=clean(value)
                if raw is None:continue
                for choice in raw.split(';'):
                    choice=choice.strip()
                    if not choice or choice in found:continue
                    found.add(choice)
                    translated=localize_category(table,col,choice,'en')
                    turkish=any(ch in choice for ch in 'çğıöşüÇĞİÖŞÜ') or bool(watch_terms.search(choice))
                    if (choice==translated and turkish) or (choice in ('ADÇ','SB')):
                        unresolved.append((table,col,choice,translated))
    if not unresolved:return None
    out=Path(report_path).with_name(Path(report_path).stem+'_English_Review.csv')
    with out.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['OriginalTable','OriginalField','RecordedValue','CurrentEnglish','Status'])
        for table,col,value,translated in unresolved:
            w.writerow([table,col,value,translated,'Review scientific translation'])
    return out

def create_report(database_path,output_path,lang='tr',charts=True,progress=None,detailed=True):
    """Render fully authored bilingual document; user-entered category labels stay unchanged.
    Returns report metadata and created charts. Never edits the source database.
    """
    if lang not in TEXTS:raise ValueError('lang must be tr or en')
    t=TEXTS[lang]
    frames,standard=analysis_tables(database_path)
    output_path=Path(output_path); output_path.parent.mkdir(parents=True,exist_ok=True)
    doc=Document();_setup_document(doc,lang)
    title=doc.add_paragraph(style='Title');title.alignment=WD_ALIGN_PARAGRAPH.CENTER
    title.add_run('LITHOS\n'+t['title'])
    sub=doc.add_paragraph(t['subtitle']);sub.alignment=WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(t['source']+': '+Path(database_path).name)
    doc.add_paragraph(t['date']+': '+datetime.now().strftime('%Y-%m-%d %H:%M'))
    doc.add_page_break()
    doc.add_heading(t['summary'],1)
    stats=compute_summary(frames,lang)
    doc.add_heading(t['table_coverage'],2)
    _document_table(doc,[t['table'],t['records'],t['fields'],t['unique']],[[table_label(n,lang),r['rows'],r['columns'],r['unique']] for n,r in stats.items()])
    doc.add_paragraph(t['coverage_note'])
    doc.add_heading(t['methods'],1)
    for k in ['method1','method2','method3']:doc.add_paragraph(t[k])
    industry_tree=_type_hierarchy_report(doc,frames,lang) or []
    saved_charts=[]
    with tempfile.TemporaryDirectory() as tmp:
        temp=Path(tmp)
        count=max(1,len(frames))
        for index,(name,df) in enumerate(frames.items()):
            if progress:progress(20+round(index/count*70),table_label(name,lang))
            doc.add_heading(f'{index+1}. {table_label(name,lang)}',1)
            if df.empty:
                doc.add_paragraph(t['no_records'])
                continue
            doc.add_heading(t['data_quality'],2)
            s=stats[name]
            doc.add_paragraph(f"{t['records']}: {s['rows']} | {t['unique']}: {s['unique']} | {t['duplicate']}: {s['duplicates']}")
            missing=[(label(name,f['field'],lang),f['valid'],f['missing']) for f in s['fields'] if f['missing']]
            if missing:_document_table(doc,[t['table'] if False else t['fields'],t['valid'],t['missing']],missing,max_rows=18)
            numbers=numeric_columns(df,name)
            if numbers:
                doc.add_heading(t['metrics'],2)
                rows=[]
                for col in numbers:
                    series=pd.to_numeric(df[col].replace('',float('nan')),errors='coerce').dropna()
                    if series.empty:continue
                    rows.append([label(name,col,lang),len(series),round(float(series.mean()),2),round(float(series.median()),2),round(float(series.std(ddof=1)),2) if len(series)>1 else '—',round(float(series.min()),2),round(float(series.max()),2)])
                _document_table(doc,[t['fields'],t['n'],t['mean'],t['median'],t['sd'],t['min'],t['max']],rows)
            _typeled_details_report(doc,frames,name,industry_tree,lang)
            doc.add_heading(t['frequencies'],2)
            skip={'id','project_id','context_id','artifact_id','core_id','macrolith_id','microlith_id','image_id','term_id','inventory_no','notes','description','created_on','file_path'}
            legacy_skip={'analiz_no','aciklama','foto','cizim','yil','cizim_no'}
            eligible=[c for c in df.columns if c not in numbers and (norm(c) not in skip) and (norm(c) not in legacy_skip)]
            # Long free-text and numeric code fields are excluded from categorical inference.
            if name in TABLE_MAP:
                lookup={f.code:f.kind for f in TABLE_MAP[name].fields}
                eligible=[c for c in eligible if lookup.get(c) not in ('longtext','date')]
            # Categorical plots are capped to avoid gigantic documents.
            eligible=eligible[:22 if detailed else 7]
            for col in eligible:
                freq,multi,n=frequency(df,col,name,lang)
                if freq.empty:continue
                doc.add_heading(label(name,col,lang),3)
                _document_table(doc,[t['category'],t['frequency'],t['pct']],[(r.category,int(r['count']),r['percent']) for _,r in freq.iterrows()],max_rows=22)
                if multi:doc.add_paragraph(t['multi'])
                if charts and len(freq)>1 and len(freq)<=30:
                    filename=f'chart_{index}_{len(saved_charts)}.png'
                    p=_plot_frequency(freq,label(name,col,lang),temp/filename,lang)
                    if p:_insert_chart(doc,p)
            # Restore original Gürbelen frequency and cross-analysis PIE CHARTS.
            _legacy_pies(doc,name,df,lang,temp,charts,saved_charts,detailed=detailed)
            # Cross-tab only on standard artifact data; legacy cross-analysis is handled by old engine.
            if name=='artifacts' and all(c in df.columns for c in ('artifact_class','raw_material')):
                usable=df[['artifact_class','raw_material']].dropna()
                if not usable.empty:
                    pivot=pd.crosstab(usable.artifact_class,usable.raw_material)
                    if not pivot.empty and pivot.shape[0]<=15 and pivot.shape[1]<=15:
                        doc.add_heading(t['relations'],2)
                        rownames=[term_label('artifact_class',k,lang) for k in pivot.index]
                        colnames=[term_label('raw_material',k,lang) for k in pivot.columns]
                        values=[[rownames[i]]+[int(x) for x in row] for i,row in enumerate(pivot.to_numpy().tolist())]
                        _document_table(doc,[t['category']]+colnames,values,max_rows=18)
                        doc.add_paragraph(t['cross_note'])
            # Data-derived observations from ALL meaningful variables, not first five.
            if detailed:
                for_findings=generate_observations({name:df},lang)[name]
                if for_findings:
                    doc.add_heading(t['observations'],2)
                    for text in for_findings:doc.add_paragraph(text,style='List Bullet')
        # Distinct final analytical synthesis rather than a five-point boilerplate.
        doc.add_heading(('Genel veri temelli sonuçlar' if lang=='tr' else 'Overall data-derived findings'),1)
        all_findings=generate_observations(frames,lang)
        for table_name,results in all_findings.items():
            if not results:continue
            doc.add_heading(table_label(table_name,lang),2)
            for item in results:doc.add_paragraph(item,style='List Bullet')
        doc.add_heading(t['limit'],1)
        doc.add_paragraph(t['untranslated'])
        doc.add_paragraph(t['coverage_note'])
        doc.add_paragraph(t['source_file']+': '+str(Path(database_path).resolve()))
        doc.add_paragraph(t['read_only'])
        if progress:progress(94,t['generated'])
        doc.save(output_path)
        if lang=='en':_write_translation_review(frames,output_path)
    if progress:progress(100,'OK')
    return {'output':str(output_path),'tables':stats,'standard':standard,'language':lang}


def make_chart_preview(database_path,output_dir,lang='tr',max_charts=48):
    """Same original Gürbelen pie/cross analyses as Word, now available in GUI.

    Save persistent PNGs under a per-run directory, not under a temporary Word
    report directory (which is deleted before the GUI can display it).
    """
    frames,_=analysis_tables(database_path)
    root=Path(output_dir);root.mkdir(parents=True,exist_ok=True)
    out=root/datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    out.mkdir(parents=True,exist_ok=True)
    paths=[]
    def append_pie(pairs,title):
        if len(paths)>=max_charts:return
        path=out/f'{len(paths)+1:03d}_pie.png'
        if _pie_chart(pairs,title,path,lang):paths.append(str(path))
    from .industry import build_industry_tree
    trees=build_industry_tree(frames,lang)
    # First, show main tool/core type distributions and conditional characteristics.
    for root_node in trees:
        if len(paths)>=max_charts:break
        name=root_node['table'];df=frames[name]
        if df.empty:continue
        mains=root_node['children']
        if name=='MAKROLİTLER' and mains:mains=mains[0]['children']
        for group in mains[:9]:
            if len(paths)>=max_charts:break
            subset=df.iloc[group['indices']]
            if len(subset)<2:continue
            requested_fields=(('Cikarim_yonu','Vurma_düzlemi') if name=='ÇEKİRDEKLER' else
                              ('Tasimalik','Duzelti') if name=='MAKROLİTLER' else
                              ('Tasimalik','Duzelti'))
            for req in requested_fields:
                col=_find_field(subset,req)
                if col is None or len(paths)>=max_charts:continue
                freq,_,_=frequency(subset,col,name,lang)
                if len(freq)>1:
                    title=group['name']+' — '+label(name,col,lang)
                    append_pie([(r.category,int(r['count'])) for _,r in freq.iterrows()],title)
    for name,df in frames.items():
        if df.empty:continue
        for key in LEGACY_PIE_FIELDS.get(norm(name),()):
            c=_find_field(df,key)
            if c:
                freq,_,_=frequency(df,c,name,lang)
                if len(freq)>=2:
                    append_pie([(r.category,int(r['count'])) for _,r in freq.iterrows()],
                               table_label(name,lang)+' — '+label(name,c,lang))
        for a_key,b_key in LEGACY_PIE_CROSSES.get(norm(name),()):
            a=_find_field(df,a_key);b=_find_field(df,b_key)
            if not a or not b:continue
            groups={}
            for av,bv in zip(df[a],df[b]):
                for al in _split_pie(av):
                    counter=groups.setdefault(al,Counter())
                    for br in _split_pie(bv):counter[br]+=1
            n=0
            for category,counter in sorted(groups.items(),key=lambda item:-sum(item[1].values())):
                if n>=3 or len(paths)>=max_charts:break
                if len(counter)<2:continue
                title=f'{table_label(name,lang)} — {label(name,a,lang)}: {localize_category(name,a,category,lang)} / {label(name,b,lang)}'
                append_pie([(localize_category(name,b,v,lang),cnt) for v,cnt in counter.most_common()],title)
                n+=1
    # Include informative non-pie plots after the pie selection.
    for name,df in frames.items():
        if df.empty:continue
        for c in eligible_categories(df,name):
            if len(paths)>=max_charts:break
            freq,_,_=frequency(df,c,name,lang)
            if not 2<=len(freq)<=30:continue
            path=out/f'{len(paths)+1:03d}_bar.png'
            _plot_frequency(freq,table_label(name,lang)+' — '+label(name,c,lang),path,lang)
            if path.is_file():paths.append(str(path))
    return paths
