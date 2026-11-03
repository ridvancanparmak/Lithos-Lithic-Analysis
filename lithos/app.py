# -*- coding: utf-8 -*-
"""Lithos 1.0.2 visual desktop GUI / PySide6.
Responsive layouts, TR/EN UI, system-aware light/dark theme, editable standard DB,
read-only analysis of original Gürbelen Access, bilingual reports and visualizations.
"""
from __future__ import annotations
import os
import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt,QSettings,QThread,Signal,QTimer,QUrl,QSize,QPointF,QRect
from PySide6.QtGui import QColor,QIcon,QPainter,QPolygonF,QPixmap,QDesktopServices,QFont,QAction
from PySide6.QtWidgets import (
 QApplication,QMainWindow,QWidget,QFrame,QScrollArea,QVBoxLayout,QHBoxLayout,
 QGridLayout,QStackedWidget,QTabWidget,QLabel,QPushButton,QComboBox,QCheckBox,
 QProgressBar,QMessageBox,QFileDialog,QTextBrowser,QTableWidget,QTableWidgetItem,
 QHeaderView,QSplitter,QDialog,QFormLayout,QLineEdit,QDoubleSpinBox,QSpinBox,
 QDialogButtonBox,QSizePolicy,QGraphicsDropShadowEffect,QGraphicsOpacityEffect,QAbstractItemView,QPlainTextEdit,QTreeWidget,QTreeWidgetItem,QToolButton,
)

from .i18n import tr
from .repository import DataStore,create_database,DatabaseError
from .schema import TABLES
from .analysis import create_report,compute_summary,make_chart_preview,generate_observations,table_label,label as report_label
from .industry import build_industry_tree,flatten_tree,type_detail
from .dashboard import dashboard_counts,make_dashboard_charts

EMAIL='ridvancanparmak@yandex.com'

def resource(name):
    if getattr(sys,'frozen',False):
        root=Path(getattr(sys,'_MEIPASS',Path(sys.executable).parent))
        return root/'assets'/name
    return Path(__file__).resolve().parent.parent/'assets'/name


def documents():
    from PySide6.QtCore import QStandardPaths
    path=QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
    return Path(path) if path else Path.home()


def windows_theme():
    if sys.platform!='win32':return 'dark'
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize') as key:
            return 'light' if winreg.QueryValueEx(key,'AppsUseLightTheme')[0] else 'dark'
    except Exception:return 'dark'


PALETTES={
 'dark':dict(bg='#0b1320',surface='#111e31',side='#131f32',line='#35455e',text='#f5f8fe',muted='#afbed4',blue='#1687ff',soft='#1b365b',field='#1d2a40',shadow='#080d18'),
 'light':dict(bg='#f1f5fb',surface='#ffffff',side='#fafcff',line='#cbd4e2',text='#19243a',muted='#5e6b80',blue='#246ad1',soft='#e0edff',field='#eef3fb',shadow='#d9e0ee')
}

def stylesheet(theme):
    p=PALETTES[theme]
    return f"""
    * {{ font-family:'Segoe UI'; font-size:10pt; color:{p['text']}; }}
    QMainWindow,QWidget#root,QWidget#page {{background:{p['bg']};}}
    QFrame#header {{background:{p['surface']};border-bottom:1px solid {p['line']};}}
    QLabel#brand {{font-family:Georgia,'Times New Roman';font-size:33pt;font-style:italic;font-weight:bold;}}
    QLabel#brandSub {{color:{p['muted']};font-size:10pt;}}
    QLabel#credit {{font-size:8pt;color:{p['muted']};}}
    QFrame#panel,QFrame#status,QFrame#card,QFrame#dropArea {{background:{p['side']};border:1px solid {p['line']};border-radius:11px;}}
    QFrame#status {{background:{p['surface']};}}
    QFrame#metricCard,QFrame#chartCard,QFrame#dashboardCard {{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {p['soft']},stop:0.3 {p['side']},stop:1 {p['surface']});border:1px solid {p['line']};border-radius:11px;}}
    QFrame#metricCard {{border-left:2px solid {p['blue']};}}
    QLabel#metricNumber {{font-size:23pt;font-weight:800;color:{p['text']};}}
    QLabel#metricLabel {{font-size:9pt;color:{p['muted']};}}
    QLabel#metricShare {{font-size:9pt;color:#63b1ff;font-weight:700;}}
    QLabel#chartHeading {{font-size:10pt;font-weight:700;}}
    QFrame#status[complete="true"] {{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1a3c41,stop:1 #233c63);border:1px solid {p['blue']};}}
    QFrame#dropArea {{border:2px dashed {p['muted']};}}
    QLabel#sectionTitle {{font-weight:700;font-size:12pt;}}
    QLabel#muted,QLabel#hint,QLabel#small {{color:{p['muted']};}}
    QLabel#small {{font-size:9pt;}}
    QLabel#pageTitle {{font-size:21pt;font-weight:750;}}
    QLabel#introHeading {{font-size:15pt;font-weight:bold;}}
    QLabel#percent {{font-size:20pt;font-weight:700;color:{p['blue']};}}
    QScrollArea {{background:transparent;border:none;}}
    QScrollArea>QWidget>QWidget {{background:transparent;}}
    QTabWidget::pane {{background:{p['surface']};border:1px solid {p['line']};border-radius:9px;}}
    QTabBar::tab {{background:{p['side']};color:{p['muted']};padding:11px 17px;border:1px solid {p['line']};border-bottom:none;min-width:92px;}}
    QTabBar::tab:selected {{background:{p['soft']};color:{p['text']};border-bottom:2px solid {p['blue']};}}
    QTabBar::tab:first {{border-top-left-radius:9px;}}
    QTabBar::tab:last {{border-top-right-radius:9px;}}
    QPushButton {{background:{p['field']};border:1px solid {p['line']};border-radius:7px;padding:8px 12px;font-weight:600;}}
    QPushButton:hover {{background:{p['soft']};border-color:{p['blue']};}}
    QPushButton:disabled {{color:{p['muted']};background:{p['side']};}}
    QPushButton#nav {{background:transparent;border:none;color:{p['muted']};padding:12px 5px;min-height:26px;font-size:10pt;}}
    QPushButton#nav:checked {{background:{p['soft']};color:{p['text']};border-bottom:3px solid {p['blue']};border-radius:7px;}}
    QPushButton#primary {{background:{p['blue']};color:white;border-color:{p['blue']};font-size:11pt;padding:12px;}}
    QPushButton#primary:hover {{background:#4195fa;}}
    QToolButton#nav {{background:transparent;border:1px solid transparent;border-radius:10px;padding:7px 4px;color:{p['text']};font-size:10pt;font-weight:600;}}
    QToolButton#nav:checked {{background:{p['soft']};border:1px solid {p['blue']};border-bottom:3px solid {p['blue']};}}
    QToolButton#nav:hover {{background:{p['soft']};border-color:{p['line']};}}
    QToolButton#langFlag {{background:transparent;border:1px solid transparent;border-radius:7px;padding:3px;color:{p['muted']};font-size:8pt;font-weight:700;}}
    QToolButton#langFlag:checked {{background:{p['soft']};border-color:{p['blue']};color:{p['text']};}}
    QToolButton#langFlag:hover {{border-color:{p['blue']};}}
    QLabel#flagSeparator {{font-size:16pt;color:{p['muted']};}}
    QTreeWidget {{background:{p['surface']};border:1px solid {p['line']};border-radius:8px;alternate-background-color:{p['side']};}}
    QTreeWidget::item {{padding:4px;}}
    QTreeWidget::item:selected {{background:{p['soft']};color:{p['text']};}}
    QPushButton#plain {{background:transparent;border:none;color:{p['blue']};}}
    QComboBox,QLineEdit,QDoubleSpinBox,QSpinBox {{background:{p['field']};border:1px solid {p['line']};border-radius:7px;padding:8px;selection-background-color:{p['blue']};}}
    QComboBox QAbstractItemView {{background:{p['surface']};color:{p['text']};selection-background-color:{p['blue']};}}
    QCheckBox {{spacing:10px;}}
    QCheckBox::indicator {{width:18px;height:18px;}}
    QTextBrowser,QTableWidget {{background:{p['surface']};border:1px solid {p['line']};border-radius:8px;selection-background-color:{p['soft']};gridline-color:{p['line']};}}
    QTextBrowser {{padding:14px;}}
    QHeaderView::section {{background:{p['field']};border:none;border-bottom:1px solid {p['line']};padding:8px;font-weight:700;}}
    QTableCornerButton::section {{background:{p['field']};}}
    QProgressBar {{border:1px solid {p['line']};background:{p['field']};border-radius:5px;height:13px;text-align:center;}}
    QProgressBar::chunk {{background:{p['blue']};border-radius:5px;}}
    QSplitter::handle {{background:{p['bg']};}}
    QDialog,QMessageBox {{background:{p['surface']};}}
    QToolTip {{background:{p['surface']};color:{p['text']};border:1px solid {p['line']};}}
    """


class Header(QFrame):
    """Photographic high-DPI mountain panorama, positioned without stretching."""
    def __init__(self):
        super().__init__()
        self.setObjectName('header')
        self.mountain=QPixmap(str(resource('mountain_header_hidpi.png')))

    def paintEvent(self,event):
        super().paintEvent(event)
        if self.width()<850 or self.mountain.isNull():
            return
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,True)
        # The image is a pre-cropped 6:1 panorama. Never resize its axes independently.
        source_width=self.mountain.width()
        source_height=self.mountain.height()
        height=max(1,self.height())
        width=round(source_width * height / source_height)
        # Keep the photo anchored to the right; left side has an alpha gradient.
        target=QRect(self.width()-width,0,width,height)
        painter.drawPixmap(target,self.mountain)
        painter.end()

class DropZone(QFrame):
    dropped=Signal(str)
    clicked=Signal()
    def __init__(self):
        super().__init__();self.setObjectName('dropArea');self.setAcceptDrops(True);self.setCursor(Qt.CursorShape.PointingHandCursor)
    def dragEnterEvent(self,e):
        paths=[p.toLocalFile() for p in e.mimeData().urls()]
        if any(Path(x).suffix.lower() in ('.accdb','.mdb') for x in paths):e.acceptProposedAction()
    def dropEvent(self,e):
        for u in e.mimeData().urls():
            path=u.toLocalFile()
            if Path(path).suffix.lower() in ('.accdb','.mdb'):
                self.dropped.emit(path);e.acceptProposedAction();break
    def mousePressEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton:self.clicked.emit()
        super().mousePressEvent(e)

class ReportWorker(QThread):
    stage=Signal(int,str)
    completed=Signal(object)
    failure=Signal(str)
    def __init__(self,path,out,lang,with_report=True,with_charts=True,detailed=True,visual_theme="dark"):
        super().__init__();self.path=path;self.out=out;self.lang=lang
        self.with_report=with_report;self.with_charts=with_charts;self.detailed=detailed;self.visual_theme=visual_theme
    def run(self):
        try:
            store=DataStore(self.path)
            frames=store.read_for_analysis()
            self.stage.emit(8,'Analyzing source database' if self.lang=='en' else 'Veritabanı analiz ediliyor')
            stats=compute_summary(frames,self.lang)
            observations=generate_observations(frames,self.lang)
            output=None;charts=[];dashboard=[]
            if self.with_report:
                out=Path(self.out);out.mkdir(parents=True,exist_ok=True)
                suffix='EN' if self.lang=='en' else 'TR'
                output=out/f'{Path(self.path).stem}_Lithos_{suffix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
                create_report(self.path,output,self.lang,self.with_charts,lambda x,s:self.stage.emit(x,s),detailed=self.detailed)
            if self.with_charts:
                self.stage.emit(95,'Preparing chart previews' if self.lang=='en' else 'Grafikler hazırlanıyor')
                chart_dir=Path(self.out)/'_charts_preview'
                charts=make_chart_preview(self.path,chart_dir,self.lang)
                dashboard=make_dashboard_charts(frames,chart_dir/'dashboard',self.lang,self.visual_theme)
            self.stage.emit(100,'Complete' if self.lang=='en' else 'Tamamlandı')
            self.completed.emit({'stats':stats,'observations':observations,'frames':frames,'report':str(output) if output else None,'charts':charts,'dashboard':dashboard})
        except Exception as exc:self.failure.emit(f'{type(exc).__name__}: {exc}')


class LithosWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings=QSettings('Lithos','Lithos')
        self.lang=self.settings.value('lang','tr')
        if self.lang not in ('tr','en'):self.lang='tr'
        self.theme_choice=self.settings.value('theme','auto')
        if self.theme_choice not in ('auto','dark','light'):self.theme_choice='auto'
        self.theme_now='dark'
        self.path=None;self.last_report=None;self.chart_paths=[];self.dashboard_chart_paths=[];self.worker=None;self._analysis_frames={};self._tree_nodes=[]
        self.output_dir=Path(self.settings.value('output_dir',str(documents()/'Lithos Raporlar')))
        self.resize(1490,870);self.setMinimumSize(680,500)
        if resource('lithos_v102.ico').exists():self.setWindowIcon(QIcon(str(resource('lithos_v102.ico'))))
        self.setWindowTitle('Lithos')
        self._make_ui();self.apply_theme();self.retranslate();self.switch_page(0)
        timer=QTimer(self);timer.setInterval(2500);timer.timeout.connect(self.check_auto_theme);timer.start()

    def T(self,key):return tr(key,self.lang)
    def _make_ui(self):
        root=QWidget();root.setObjectName('root');self.setCentralWidget(root)
        main=QVBoxLayout(root);main.setContentsMargins(0,0,0,0);main.setSpacing(0)
        self.header=Header();self.header.setFixedHeight(132)
        header=QHBoxLayout(self.header);header.setContentsMargins(23,7,20,7);header.setSpacing(10)
        self.logo=QLabel();self.logo.setFixedSize(85,105)
        pix=QPixmap(str(resource('handaxe_realistic.png')))
        if not pix.isNull():self.logo.setPixmap(pix.scaled(82,101,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        header.addWidget(self.logo)
        brandcol=QVBoxLayout();brandcol.setSpacing(0)
        self.brand=QLabel('Lithos');self.brand.setObjectName('brand')
        brandcol.addWidget(self.brand)
        self.brand_sub=QLabel();self.brand_sub.setObjectName('brandSub');self.brand_sub.setWordWrap(True)
        brandcol.addWidget(self.brand_sub);brandcol.addStretch(1)
        brandbox=QWidget();brandbox.setLayout(brandcol);brandbox.setMaximumWidth(265)
        header.addWidget(brandbox,2)
        nav=QHBoxLayout();nav.setSpacing(5)
        self.navs=[]
        for i,(key,symbol) in enumerate(zip(['analysis','reports','database','settings','about'],
                ['analysis','reports','database','settings','info'])):
            btn=QToolButton();btn.setObjectName('nav');btn.setCheckable(True)
            btn.setIcon(QIcon(str(resource('icon_'+symbol+'.svg'))));btn.setIconSize(QSize(28,28))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.clicked.connect(lambda checked,x=i:self.switch_page(x))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred)
            btn.setMinimumWidth(52);btn.setMaximumWidth(110);btn.setMinimumHeight(76)
            self.navs.append((btn,key));nav.addWidget(btn,1)
        header.addLayout(nav,5)
        header.addStretch(1)
        rights=QVBoxLayout();rights.setSpacing(5)
        self.top_credit=QLabel('by Rıdvan Can PARMAK');self.top_credit.setObjectName('credit')
        rights.addWidget(self.top_credit,0,Qt.AlignmentFlag.AlignRight)
        langrow=QHBoxLayout();langrow.setSpacing(1)
        self.lang_tr_btn=QToolButton();self.lang_en_btn=QToolButton()
        for button,language,flag,label in ((self.lang_tr_btn,'tr','flag_tr.png','TR'),
                                            (self.lang_en_btn,'en','flag_en.png','ENG')):
            button.setObjectName('langFlag');button.setText(label)
            button.setIcon(QIcon(str(resource(flag))));button.setIconSize(QSize(34,21))
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            button.setCheckable(True);button.setFixedSize(54,64)
            button.clicked.connect(lambda checked,l=language:self.set_language(l))
            langrow.addWidget(button)
            if language=='tr':
                separator=QLabel('|');separator.setObjectName('flagSeparator')
                separator.setAlignment(Qt.AlignmentFlag.AlignCenter);langrow.addWidget(separator)
        rights.addLayout(langrow)
        header.addLayout(rights)
        main.addWidget(self.header)
        self.pages=QStackedWidget();main.addWidget(self.pages,1)
        self.pages.addWidget(self._analysis_page());self.pages.addWidget(self._reports_page())
        self.pages.addWidget(self._database_page());self.pages.addWidget(self._settings_page())
        self.pages.addWidget(self._about_page())
        self.footer=QFrame();self.footer.setObjectName('status');self.footer.setFixedHeight(37)
        foot=QHBoxLayout(self.footer);foot.setContentsMargins(16,5,16,5)
        self.connection_label=QLabel();self.connection_label.setObjectName('small');foot.addWidget(self.connection_label)
        foot.addSpacing(14);self.count_label=QLabel('');self.count_label.setObjectName('small');foot.addWidget(self.count_label)
        foot.addStretch()
        self.clock_label=QLabel();self.clock_label.setObjectName('small');foot.addWidget(self.clock_label)
        self.time_timer=QTimer(self);self.time_timer.timeout.connect(self.update_clock)
        self.time_timer.start(30000);self.update_clock()
        foot.addSpacing(16);self.version_label=QLabel('v1.0.1');self.version_label.setObjectName('small');foot.addWidget(self.version_label)
        main.addWidget(self.footer)

    def update_clock(self):
        self.clock_label.setText(datetime.now().strftime('%d.%m.%Y  %H:%M'))

    def _analysis_page(self):
        page=QWidget();page.setObjectName('page');overall=QVBoxLayout(page)
        overall.setContentsMargins(13,9,13,9);overall.setSpacing(7)
        self.splitter=QSplitter(Qt.Orientation.Horizontal);self.splitter.setChildrenCollapsible(False)
        side_container=QFrame();side_container.setObjectName('panel');side_container.setMinimumWidth(208)
        side_column=QVBoxLayout(side_container);side_column.setContentsMargins(9,9,9,9);side_column.setSpacing(7)
        side=QScrollArea();side.setObjectName('leftScroll');side.setWidgetResizable(True)
        side.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        pane=QWidget();sidebar=QVBoxLayout(pane);sidebar.setContentsMargins(7,7,7,7);sidebar.setSpacing(12)
        self.file_title=QLabel();self.file_title.setObjectName('sectionTitle');sidebar.addWidget(self.file_title)
        self.zone=DropZone();self.zone.setMinimumHeight(115)
        zbox=QVBoxLayout(self.zone);zbox.setContentsMargins(10,11,10,11)
        self.drop_icon=QLabel();self.drop_icon.setPixmap(QIcon(str(resource('icon_reports.svg'))).pixmap(36,36))
        self.drop_icon.setAlignment(Qt.AlignmentFlag.AlignCenter);zbox.addWidget(self.drop_icon)
        self.drop_msg=QLabel();self.drop_msg.setWordWrap(True);self.drop_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zbox.addWidget(self.drop_msg,1)
        self.select_button=QPushButton();self.select_button.clicked.connect(self.choose_db)
        zbox.addWidget(self.select_button,0,Qt.AlignmentFlag.AlignHCenter)
        self.zone.clicked.connect(self.choose_db);self.zone.dropped.connect(self.load_db)
        sidebar.addWidget(self.zone)
        self.selected_title=QLabel();self.selected_title.setObjectName('small');sidebar.addWidget(self.selected_title)
        self.path_label=QLabel();self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.path_label.setObjectName('muted');sidebar.addWidget(self.path_label)
        sep=QFrame();sep.setFrameShape(QFrame.Shape.HLine);sidebar.addWidget(sep)
        self.opt_title=QLabel();self.opt_title.setObjectName('sectionTitle');sidebar.addWidget(self.opt_title)
        self.report_check=QCheckBox();self.report_check.setChecked(True);sidebar.addWidget(self.report_check)
        self.chart_check=QCheckBox();self.chart_check.setChecked(True);sidebar.addWidget(self.chart_check)
        self.output_label=QLabel();self.output_label.setObjectName('small');sidebar.addWidget(self.output_label)
        outrow=QHBoxLayout();outrow.setSpacing(4)
        self.output_path=QLineEdit(str(self.output_dir));self.output_path.setReadOnly(True)
        self.output_path.setMinimumWidth(35);self.output_path.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Fixed)
        self.output_path.setToolTip(str(self.output_dir));outrow.addWidget(self.output_path,1)
        self.browse_out=QPushButton();self.browse_out.setMinimumWidth(77);self.browse_out.setMaximumWidth(95)
        self.browse_out.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.browse_out.clicked.connect(self.choose_out);outrow.addWidget(self.browse_out,0)
        sidebar.addLayout(outrow);sidebar.addStretch(1)
        side.setWidget(pane);side_column.addWidget(side,1)
        self.start_button=QPushButton();self.start_button.setObjectName('primary');self.start_button.clicked.connect(self.start_analysis)
        self.start_button.setMinimumHeight(51);side_column.addWidget(self.start_button,0)
        self.splitter.addWidget(side_container)
        right=QWidget();rbox=QVBoxLayout(right);rbox.setContentsMargins(2,0,2,0)
        self.tabs=QTabWidget()
        result_tab=QWidget();rcontent=QVBoxLayout(result_tab);rcontent.setContentsMargins(7,8,7,8)
        self.results_stack=QStackedWidget()
        empty_results=QWidget();empty_layout=QVBoxLayout(empty_results)
        empty_layout.addStretch(2)
        self.result_msg=QLabel();self.result_msg.setObjectName('muted');self.result_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_msg.setWordWrap(True);self.result_msg.setMinimumHeight(80)
        empty_layout.addWidget(self.result_msg);empty_layout.addStretch(3)
        self.results_stack.addWidget(empty_results)
        # Results dashboard: metric cards, typology tree, actual visualizations and observations.
        dashboard_scroll=QScrollArea();dashboard_scroll.setWidgetResizable(True)
        dashboard=QWidget();self.dashboard_layout=QVBoxLayout(dashboard)
        self.dashboard_layout.setContentsMargins(4,4,4,4);self.dashboard_layout.setSpacing(10)
        self.metrics_grid=QGridLayout();self.metrics_grid.setHorizontalSpacing(10);self.metrics_grid.setVerticalSpacing(8)
        self.metric_cards=[];self.metric_titles=[];self.metric_counts=[];self.metric_shares=[]
        for key,symbol in [('total','layers'),('tools','tools'),('cores','cube'),('microliths','pie')]:
            card=QFrame();card.setObjectName('metricCard')
            row=QHBoxLayout(card);row.setContentsMargins(11,10,11,10);row.setSpacing(8)
            ico=QLabel();ico.setPixmap(QIcon(str(resource('icon_'+symbol+'.svg'))).pixmap(33,33));row.addWidget(ico)
            col=QVBoxLayout();col.setSpacing(1)
            cap=QLabel();cap.setObjectName('metricLabel');col.addWidget(cap)
            num=QLabel('—');num.setObjectName('metricNumber');col.addWidget(num)
            row.addLayout(col,1)
            share=QLabel('');share.setObjectName('metricShare');row.addWidget(share,0,Qt.AlignmentFlag.AlignBottom)
            card.setMinimumHeight(81)
            self.metric_cards.append(card);self.metric_titles.append((cap,key));self.metric_counts.append(num);self.metric_shares.append(share)
        self.reflow_cards(4)
        self.dashboard_layout.addLayout(self.metrics_grid)
        self.dashboard_splitter=QSplitter(Qt.Orientation.Horizontal);self.dashboard_splitter.setChildrenCollapsible(False)
        left_panel=QFrame();left_panel.setObjectName('dashboardCard')
        left_lay=QVBoxLayout(left_panel);left_lay.setContentsMargins(12,11,12,11);left_lay.setSpacing(7)
        self.tree_title=QLabel();self.tree_title.setObjectName('sectionTitle');left_lay.addWidget(self.tree_title)
        self.table_note=QLabel();self.table_note.setWordWrap(True);self.table_note.setObjectName('small');left_lay.addWidget(self.table_note)
        self.industry_tree=QTreeWidget();self.industry_tree.setColumnCount(4)
        self.industry_tree.setAlternatingRowColors(True);self.industry_tree.setUniformRowHeights(True)
        self.industry_tree.setMinimumHeight(230);self.industry_tree.setHeaderHidden(False)
        self.industry_tree.itemSelectionChanged.connect(self.on_industry_selection)
        left_lay.addWidget(self.industry_tree,3)
        self.selected_detail_title=QLabel();self.selected_detail_title.setObjectName('sectionTitle');left_lay.addWidget(self.selected_detail_title)
        self.result_details=QTextBrowser();self.result_details.setOpenExternalLinks(False)
        self.result_details.setMinimumHeight(145);left_lay.addWidget(self.result_details,2)
        self.table_toggle=QPushButton();self.table_toggle.setCheckable(True)
        self.table_toggle.toggled.connect(lambda shown:self.result_table.setVisible(shown))
        left_lay.addWidget(self.table_toggle)
        self.result_table=QTableWidget(0,4);self.result_table.setVisible(False)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.result_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.result_table.setMaximumHeight(145);left_lay.addWidget(self.result_table)
        self.dashboard_splitter.addWidget(left_panel)
        right_panel=QFrame();right_panel.setObjectName('dashboardCard')
        right_lay=QVBoxLayout(right_panel);right_lay.setContentsMargins(11,11,11,11);right_lay.setSpacing(9)
        self.graph_header=QLabel();self.graph_header.setObjectName('sectionTitle');right_lay.addWidget(self.graph_header)
        self.graph_grid=QGridLayout();self.graph_grid.setHorizontalSpacing(8);self.graph_grid.setVerticalSpacing(8)
        self.dashboard_graph_cards=[];self.dashboard_graph_headers=[];self.dashboard_graph_images=[]
        for i in range(4):
            card=QFrame();card.setObjectName('chartCard')
            block=QVBoxLayout(card);block.setContentsMargins(8,9,8,8);block.setSpacing(2)
            heading=QLabel();heading.setObjectName('chartHeading');heading.setWordWrap(True);block.addWidget(heading)
            img=QLabel();img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img.setMinimumHeight(110);img.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
            block.addWidget(img,1)
            self.dashboard_graph_cards.append(card);self.dashboard_graph_headers.append(heading);self.dashboard_graph_images.append(img)
        self.reflow_graph_cards(2)
        right_lay.addLayout(self.graph_grid,3)
        self.observations_heading=QLabel();self.observations_heading.setObjectName('sectionTitle');right_lay.addWidget(self.observations_heading)
        self.observations_browser=QTextBrowser();self.observations_browser.setMinimumHeight(155)
        right_lay.addWidget(self.observations_browser,2)
        self.dashboard_splitter.addWidget(right_panel)
        self.dashboard_splitter.setStretchFactor(0,3);self.dashboard_splitter.setStretchFactor(1,4)
        self.dashboard_splitter.setSizes([480,730])
        self.dashboard_layout.addWidget(self.dashboard_splitter,1)
        dashboard_scroll.setWidget(dashboard);self.results_stack.addWidget(dashboard_scroll)
        rcontent.addWidget(self.results_stack,1);self.tabs.addTab(result_tab,'')
        graphs=QScrollArea();graphs.setWidgetResizable(True)
        graphs_container=QWidget();self.graphs_layout=QVBoxLayout(graphs_container)
        self.graphs_layout.setContentsMargins(14,14,14,14);self.graphs_layout.setSpacing(14)
        self.charts_info=QLabel();self.charts_info.setWordWrap(True);self.charts_info.setObjectName('muted')
        self.graphs_layout.addWidget(self.charts_info);self.graphs_layout.addStretch(1)
        graphs.setWidget(graphs_container);self.tabs.addTab(graphs,'')
        self.preview_browser=QTextBrowser();self.tabs.addTab(self.preview_browser,'')
        rbox.addWidget(self.tabs,1);self.splitter.addWidget(right)
        self.splitter.setStretchFactor(0,0);self.splitter.setStretchFactor(1,1)
        self.splitter.setSizes([310,1050]);overall.addWidget(self.splitter,1)
        self.status_panel=QFrame();self.status_panel.setObjectName('status');self.status_panel.setProperty('complete',False)
        status=QVBoxLayout(self.status_panel);status.setContentsMargins(13,7,13,7);status.setSpacing(3)
        sr=QHBoxLayout();self.progress_title=QLabel();self.progress_title.setObjectName('sectionTitle');sr.addWidget(self.progress_title)
        sr.addStretch();self.progress_pct=QLabel('0%');self.progress_pct.setObjectName('percent');sr.addWidget(self.progress_pct)
        status.addLayout(sr)
        self.progressbar=QProgressBar();self.progressbar.setRange(0,100)
        self.progressbar.setValue(0);self.progressbar.setTextVisible(False);status.addWidget(self.progressbar)
        bottom=QHBoxLayout();self.status_text=QLabel();self.status_text.setWordWrap(True);bottom.addWidget(self.status_text,1)
        self.open_report_btn=QPushButton();self.open_report_btn.clicked.connect(self.open_report)
        self.open_report_btn.setEnabled(False);bottom.addWidget(self.open_report_btn);status.addLayout(bottom)
        overall.addWidget(self.status_panel)
        return page

    def reflow_cards(self,columns):
        for card in self.metric_cards:self.metrics_grid.removeWidget(card)
        for i,card in enumerate(self.metric_cards):self.metrics_grid.addWidget(card,i//columns,i%columns)

    def reflow_graph_cards(self,columns):
        for card in self.dashboard_graph_cards:self.graph_grid.removeWidget(card)
        for i,card in enumerate(self.dashboard_graph_cards):self.graph_grid.addWidget(card,i//columns,i%columns)

    def _reports_page(self):
        page=QWidget();page.setObjectName('page');lay=QVBoxLayout(page);lay.setContentsMargins(24,18,24,18)
        self.reports_heading=QLabel();self.reports_heading.setObjectName('pageTitle');lay.addWidget(self.reports_heading)
        row=QHBoxLayout();self.report_folder_button=QPushButton();self.report_folder_button.clicked.connect(self.open_report_folder)
        row.addWidget(self.report_folder_button);self.choose_existing_report=QPushButton();self.choose_existing_report.clicked.connect(self.choose_report)
        row.addWidget(self.choose_existing_report);row.addStretch();lay.addLayout(row)
        self.report_detail=QTextBrowser();lay.addWidget(self.report_detail,1)
        return page

    def _database_page(self):
        page=QWidget();page.setObjectName('page');lay=QVBoxLayout(page);lay.setContentsMargins(24,16,24,18);lay.setSpacing(10)
        heading=QHBoxLayout();self.db_heading=QLabel();self.db_heading.setObjectName('pageTitle');heading.addWidget(self.db_heading)
        heading.addStretch();self.new_db_btn=QPushButton();self.new_db_btn.clicked.connect(self.new_database)
        heading.addWidget(self.new_db_btn);self.open_db_btn=QPushButton();self.open_db_btn.clicked.connect(self.choose_db)
        heading.addWidget(self.open_db_btn);lay.addLayout(heading)
        self.db_intro=QLabel();self.db_intro.setObjectName('muted');self.db_intro.setWordWrap(True);lay.addWidget(self.db_intro)
        row=QHBoxLayout();self.table_select=QComboBox();self.table_select.currentIndexChanged.connect(self.refresh_database)
        row.addWidget(self.table_select,1)
        self.refresh_btn=QPushButton();self.refresh_btn.clicked.connect(self.refresh_database);row.addWidget(self.refresh_btn)
        self.add_btn=QPushButton();self.edit_btn=QPushButton();self.delete_btn=QPushButton()
        self.external_edit_btn=QPushButton();self.external_edit_btn.clicked.connect(self.open_in_access)
        row.addWidget(self.external_edit_btn)
        lay.addLayout(row)
        self.db_table=QTableWidget();self.db_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.db_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.db_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.db_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.db_table.horizontalHeader().setMinimumSectionSize(115)
        lay.addWidget(self.db_table,1)
        self.db_info=QLabel();self.db_info.setObjectName('small');lay.addWidget(self.db_info)
        return page

    def _settings_page(self):
        page=QWidget();page.setObjectName('page');v=QVBoxLayout(page);v.setContentsMargins(25,20,25,20);v.setSpacing(13)
        self.settings_heading=QLabel();self.settings_heading.setObjectName('pageTitle');v.addWidget(self.settings_heading)
        card=QFrame();card.setObjectName('card');card.setMaximumWidth(680)
        form=QFormLayout(card);form.setContentsMargins(25,24,25,24);form.setSpacing(16)
        self.settings_lang_label=QLabel();self.settings_lang_help=QLabel()
        self.settings_lang_help.setWordWrap(True)
        form.addRow(self.settings_lang_label,self.settings_lang_help)
        self.theme_label=QLabel();self.theme_combo=QComboBox()
        self.theme_combo.addItem('','auto');self.theme_combo.addItem('','dark');self.theme_combo.addItem('','light')
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        form.addRow(self.theme_label,self.theme_combo)
        self.settings_info=QLabel();self.settings_info.setObjectName('muted');self.settings_info.setWordWrap(True)
        form.addRow(self.settings_info)
        v.addWidget(card);v.addStretch(1)
        return page

    def _about_page(self):
        page=QWidget();page.setObjectName('page');lay=QVBoxLayout(page);lay.setContentsMargins(24,10,24,10)
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        content=QWidget();v=QVBoxLayout(content);v.setContentsMargins(8,12,8,14);v.setSpacing(12)
        self.about_heading=QLabel();self.about_heading.setObjectName('pageTitle');v.addWidget(self.about_heading)
        hero=QFrame();hero.setObjectName('card');hero_row=QHBoxLayout(hero);hero_row.setContentsMargins(20,14,20,14)
        image=QLabel();im=QPixmap(str(resource('handaxe_realistic.png')))
        if not im.isNull():image.setPixmap(im.scaled(88,110,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        hero_row.addWidget(image)
        tit=QVBoxLayout();ttl=QLabel('Lithos');ttl.setObjectName('brand');tit.addWidget(ttl)
        self.about_subtitle=QLabel();self.about_subtitle.setObjectName('muted');tit.addWidget(self.about_subtitle)
        ver=QLabel('Version / Sürüm 1.0');tit.addWidget(ver);tit.addStretch()
        hero_row.addLayout(tit,1);v.addWidget(hero)
        bio=QFrame();bio.setObjectName('card');bv=QVBoxLayout(bio);bv.setContentsMargins(20,16,20,16)
        self.about_name=QLabel('Rıdvan Can PARMAK');self.about_name.setObjectName('introHeading');bv.addWidget(self.about_name)
        self.about_role=QLabel();self.about_role.setObjectName('muted');self.about_role.setWordWrap(True);bv.addWidget(self.about_role)
        self.about_bio=QLabel();self.about_bio.setWordWrap(True);bv.addWidget(self.about_bio)
        self.contact_label=QLabel();self.contact_label.setOpenExternalLinks(True)
        self.contact_label.setTextFormat(Qt.TextFormat.RichText);bv.addWidget(self.contact_label)
        about_buttons=QHBoxLayout()
        self.guide_btn=QPushButton();self.guide_btn.clicked.connect(self.open_guide)
        self.release_btn=QPushButton();self.release_btn.clicked.connect(self.show_release_notes)
        about_buttons.addWidget(self.guide_btn);about_buttons.addWidget(self.release_btn);about_buttons.addStretch()
        bv.addLayout(about_buttons)
        v.addWidget(bio)
        purpose=QFrame();purpose.setObjectName('card');pv=QVBoxLayout(purpose);pv.setContentsMargins(20,16,20,16)
        self.purpose_title=QLabel();self.purpose_title.setObjectName('sectionTitle');pv.addWidget(self.purpose_title)
        self.purpose_text=QLabel();self.purpose_text.setWordWrap(True);pv.addWidget(self.purpose_text)
        self.tech_info=QLabel();self.tech_info.setWordWrap(True);self.tech_info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        pv.addWidget(self.tech_info);v.addWidget(purpose)
        self.copyright=QLabel();self.copyright.setObjectName('small');self.copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self.copyright);v.addStretch(1);scroll.setWidget(content);lay.addWidget(scroll)
        return page

    def switch_page(self,index):
        self.pages.setCurrentIndex(index)
        for i,(btn,_) in enumerate(self.navs):btn.setChecked(i==index)
        if index==2:self.refresh_database()
        if index==1:self.update_reports_page()

    def set_language(self,language):
        if language not in ('tr','en'):return
        if language!=self.lang:
            self.lang=language;self.settings.setValue('lang',language)
            self.retranslate()
            if self.path:self.refresh_database()
            if self._analysis_frames:
                self.update_summary(compute_summary(self._analysis_frames,self.lang),
                                    generate_observations(self._analysis_frames,self.lang))
                if self.chart_paths:
                    self.chart_paths=[];self.update_graphs()
                    self.charts_info.setText(self.T('rerun_charts'))
                    self.dashboard_chart_paths=[];self.update_dashboard_graphs()
        else:self._refresh_flag_buttons()

    def _refresh_flag_buttons(self):
        self.lang_tr_btn.setChecked(self.lang=='tr')
        self.lang_en_btn.setChecked(self.lang=='en')
        self.lang_tr_btn.setToolTip('Türkçe')
        self.lang_en_btn.setToolTip('English')

    def change_theme(self):
        theme=self.theme_combo.currentData()
        if theme in ('auto','light','dark'):
            self.theme_choice=theme;self.settings.setValue('theme',theme);self.apply_theme()

    def check_auto_theme(self):
        if self.theme_choice=='auto':
            mode=windows_theme()
            if mode!=self.theme_now:self.apply_theme()

    def apply_theme(self):
        theme=windows_theme() if self.theme_choice=='auto' else self.theme_choice
        self.theme_now=theme
        QApplication.instance().setStyleSheet(stylesheet(theme))
        if hasattr(self,'dashboard_chart_paths') and self.dashboard_chart_paths:self.redraw_dashboard_graphs()

    def retranslate(self):
        T=self.T
        self._refresh_flag_buttons()
        self.brand_sub.setText(T('subtitle'))
        self._compact_navigation()
        self.file_title.setText(T('file_selection'))
        self.drop_msg.setText(T('select_drop'))
        self.select_button.setText(T('select_db'))
        self.selected_title.setText(T('selected_file'))
        self.path_label.setText(str(self.path) if self.path else T('none'))
        self.opt_title.setText(T('options'))
        self.report_check.setText(T('detailed_report'))
        self.chart_check.setText(T('charts'))
        self.output_label.setText(T('choose_output'))
        self.browse_out.setText(T('browse')+'…')
        self.output_path.setToolTip(str(self.output_dir))
        self.start_button.setText('▶  '+T('start'))
        self.tabs.setTabText(0,T('results'))
        self.tabs.setTabText(1,T('visuals'))
        self.tabs.setTabText(2,T('preview'))
        if not self.path:self.result_msg.setText(T('results_empty')+'\n'+T('results_hint'))
        if not self.chart_paths:self.charts_info.setText(T('visuals_empty'))
        if not self.last_report:self.preview_browser.setPlainText(T('preview_empty'))
        self.progress_title.setText(T('progress'))
        if not self.worker or not self.worker.isRunning():
            self.status_text.setText(T('finished_info') if self.last_report else T('ready'))
        self.open_report_btn.setText(T('view_report'))
        self.reports_heading.setText(T('reports'))
        self.report_folder_button.setText(T('open_folder'))
        self.choose_existing_report.setText(T('view_report')+'…')
        self.db_heading.setText(T('database'))
        self.db_intro.setText(T('db_hint'))
        self.new_db_btn.setText('＋ '+T('create_db'))
        self.open_db_btn.setText(T('open_db'))
        self.refresh_btn.setText('↻ '+T('refresh'))
        self.add_btn.setText('＋ '+T('add_record'))
        self.edit_btn.setText(T('edit_record'))
        self.delete_btn.setText(T('delete_record'))
        self.external_edit_btn.setText('↗  '+('Microsoft Access ile düzenle' if self.lang=='tr' else 'Edit in Microsoft Access'))
        self.settings_heading.setText(T('settings_title'))
        self.settings_lang_label.setText(T('language'))
        self.settings_lang_help.setText(T('language_flags_hint'))
        self.tree_title.setText(T('industry_hierarchy'))
        self.selected_detail_title.setText(T('selected_type_details'))
        self.graph_header.setText(T('dashboard_charts'))
        self.observations_heading.setText(T('scientific_findings'))
        self.table_toggle.setText(T('table_coverage'))
        for label,key in self.metric_titles:label.setText(T('metric_'+key))
        self.industry_tree.setHeaderLabels([T('type_subtype'),T('count_short'),T('parent_share'),T('overall_share')])
        self.theme_label.setText(T('theme'))
        for i,key in enumerate(('theme_auto','theme_dark','theme_light')):self.theme_combo.setItemText(i,T(key))
        self.settings_info.setText(T('settings_note'))
        self.theme_combo.blockSignals(True);self.theme_combo.setCurrentIndex(['auto','dark','light'].index(self.theme_choice));self.theme_combo.blockSignals(False)
        self.about_heading.setText(T('about_title'))
        self.about_subtitle.setText(T('subtitle'))
        self.about_role.setText(T('about_role'))
        self.about_bio.setText(T('bio'))
        self.contact_label.setText(f'{T("about_contact")}: <a href="mailto:{EMAIL}">{EMAIL}</a>')
        self.guide_btn.setText('▤  '+T('manual'))
        self.release_btn.setText('ⓘ  '+T('release_notes'))
        self.purpose_title.setText(T('about_purpose_title'))
        self.purpose_text.setText(T('about_purpose'))
        self.tech_info.setText(f'{T("programming")}: Python   |   {T("technology")}: PySide6 / Qt\n'
                               f'{T("languages")}: Türkçe / English   |   {T("platform")}: Windows 10 / 11\n'
                               f'{T("database")}: Microsoft Access (GURBELEN-18)   |   {T("report_format")}: Word (.docx)')
        self.copyright.setText(T('about_credits'))
        self.connection_label.setText(T('db_connected') if self.path else T('db_disconnected'))
        if self.path:self._update_count_text()
        self._repopulate_table_names()
        self.result_table.setHorizontalHeaderLabels([T('table_caption'),T('records'),T('fields_caption'),T('unique_caption')])
        if self.path and self.last_report:self.update_reports_page()

    def _update_count_text(self):
        if not self.path:return
        try:
            store=DataStore(self.path);counts=store.counts()
            if store.is_standard():num=counts.get('ÖZELLİKLER',0)
            else:
                # Legacy overlapping tables are not double counted.
                try:
                    data=store.get_table('ÖZELLİKLER')
                    num=len(data)
                except Exception:num=max(counts.values(),default=0)
            self.count_label.setText(f'{self.T("records_count")}: {num}')
        except Exception:self.count_label.setText('')

    def _repopulate_table_names(self):
        previous=self.table_select.currentData()
        self.table_select.blockSignals(True);self.table_select.clear()
        if self.path:
            try:
                for name in DataStore(self.path).tables():
                    txt=table_label(name,self.lang)
                    self.table_select.addItem(txt,name)
                ix=self.table_select.findData(previous)
                if ix>=0:self.table_select.setCurrentIndex(ix)
            except Exception:pass
        self.table_select.blockSignals(False)

    def _message(self,text,error=False):
        msg=QMessageBox(self)
        msg.setWindowTitle(self.T('error') if error else 'Lithos')
        msg.setIcon(QMessageBox.Icon.Critical if error else QMessageBox.Icon.Information)
        msg.setText(text);msg.exec()

    def open_guide(self):
        if getattr(sys,'frozen',False):
            path=Path(sys.executable).resolve().parent/'KULLANIM_TR_EN.txt'
        else:
            path=Path(__file__).resolve().parents[1]/'KULLANIM_TR_EN.txt'
        if path.is_file():QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else:self._message('User guide not found / Kullanım kılavuzu bulunamadı: '+str(path),True)

    def show_release_notes(self):
        text=('Lithos v1.0\n\n'
              '• Bilingual UI and descriptive Word reports / İki dilli arayüz ve raporlar\n'
              '• Responsive Qt desktop layout / Pencereye uyumlu arayüz\n'
              '• GURBELEN-18 original Access schema / Gürbelen özgün Access şeması\n'
              '• Dark/light/automatic theme / Açık, koyu ve otomatik tema\n'
              '• Portable/installer build scripts / Kurulum derleme dosyaları\n\n'
              'Access creation requires Windows with ACE/Access. Windows builds require verification.')
        self._message(text)

    def choose_db(self):
        path,_=QFileDialog.getOpenFileName(self,self.T('select_db'),str(documents()),
                'Microsoft Access (*.accdb *.mdb)')
        if path:self.load_db(path)

    def load_db(self,path):
        try:
            store=DataStore(path)
            counts=store.counts()
            if not counts:raise DatabaseError('No readable tables')
        except Exception as exc:
            self._message(str(exc),True);return
        self.path=str(Path(path).resolve());self.settings.setValue('last_db',self.path)
        self.path_label.setText(self.path);self.path_label.setToolTip(self.path)
        self.result_msg.setText(self.T('results_hint'))
        self.results_stack.setCurrentIndex(0)
        self.connection_label.setText(self.T('db_connected'))
        self.last_report=None;self.chart_paths=[];self.dashboard_chart_paths=[];self._analysis_frames={}
        self.industry_tree.clear()
        self.open_report_btn.setEnabled(False)
        self.progressbar.setValue(0);self.progress_pct.setText('0%')
        self.status_text.setText(self.T('ready'))
        self._update_count_text();self._repopulate_table_names()
        self.refresh_database()

    def choose_out(self):
        path=QFileDialog.getExistingDirectory(self,self.T('choose_output'),str(self.output_dir))
        if path:
            self.output_dir=Path(path);self.settings.setValue('output_dir',path)
            self.output_path.setText(path);self.output_path.setToolTip(path)
            self.output_path.setCursorPosition(len(path))

    def start_analysis(self):
        if not self.path:
            self._message(self.T('db_no_data'),True);return
        if self.worker and self.worker.isRunning():return
        self.start_button.setEnabled(False);self.open_report_btn.setEnabled(False)
        self.lang_tr_btn.setEnabled(False);self.lang_en_btn.setEnabled(False)
        self.progressbar.setValue(0);self.progress_pct.setText('0%')
        self.status_text.setText(self.T('running'))
        self.status_panel.setProperty('complete',False);self.status_panel.style().unpolish(self.status_panel);self.status_panel.style().polish(self.status_panel)
        self.worker=ReportWorker(self.path,str(self.output_dir),self.lang,self.report_check.isChecked(),self.chart_check.isChecked(),detailed=True,visual_theme=self.theme_now)
        self.worker.stage.connect(self._progress)
        self.worker.failure.connect(self._failed)
        self.worker.completed.connect(self._completed)
        self.worker.start()

    def _progress(self,n,msg):
        self.progressbar.setValue(n);self.progress_pct.setText(str(n)+'%');self.status_text.setText(msg)

    def _failed(self,msg):
        self.start_button.setEnabled(True);self.status_text.setText(msg)
        self.lang_tr_btn.setEnabled(True);self.lang_en_btn.setEnabled(True)
        self._message(msg,True)

    def _completed(self,payload):
        self.start_button.setEnabled(True)
        self.lang_tr_btn.setEnabled(True);self.lang_en_btn.setEnabled(True)
        self.last_report=payload.get('report');self.chart_paths=payload.get('charts',[])
        self.dashboard_chart_paths=payload.get('dashboard',[])
        self._analysis_frames=payload.get('frames',{})
        self.status_text.setText(self.T('finished_info'))
        self.open_report_btn.setEnabled(bool(self.last_report))
        self.update_summary(payload['stats'],payload.get('observations',{}))
        self.update_graphs();self.update_dashboard_graphs();self.update_preview();self.tabs.setCurrentIndex(0)
        self.status_panel.setProperty('complete',True);self.status_panel.style().unpolish(self.status_panel);self.status_panel.style().polish(self.status_panel)

    def update_summary(self,stats,observations=None):
        import html
        self.table_note.setText(self.T('finished')+' — '+self.T('test_note'))
        self.results_stack.setCurrentIndex(1)
        self.result_table.setRowCount(len(stats))
        for i,(name,entry) in enumerate(stats.items()):
            for j,value in enumerate((table_label(name,self.lang),entry['rows'],entry['columns'],entry['unique'])):
                self.result_table.setItem(i,j,QTableWidgetItem(str(value)))
        self.result_table.resizeRowsToContents()
        contents=['<h2>'+html.escape(self.T('scientific_findings'))+'</h2>']
        for table,statements in (observations or {}).items():
            if not statements:continue
            contents.append('<h3>'+html.escape(table_label(table,self.lang))+'</h3><ul>')
            for statement in statements:
                contents.append('<li>'+html.escape(statement)+'</li>')
            contents.append('</ul>')
        self._observation_html=''.join(contents)
        self.observations_browser.setHtml(self._observation_html)
        self.result_details.setHtml('<p>'+html.escape(self.T('type_selection_hint'))+'</p>')
        counts,_=dashboard_counts(self._analysis_frames,self.lang)
        for i,key in enumerate(('total','tools','cores','microliths')):
            count=counts[key];self.metric_counts[i].setText(str(count))
            pct=(100.0*count/counts['total']) if counts['total'] else 0.0
            self.metric_shares[i].setText(('' if key=='total' else f'{pct:.1f}%'))
        self._populate_industry_tree(build_industry_tree(self._analysis_frames,self.lang))

    def _populate_industry_tree(self,nodes):
        self._tree_nodes=nodes
        self.industry_tree.blockSignals(True);self.industry_tree.clear()
        def append(parent,node,prefix):
            number=(prefix+'.' if prefix else '')
            text=number+' '+node['name']
            count=str(node['count'])
            parent_pct=('%0.1f %%'%node['parent_pct']) if node['parent_total'] else '—'
            overall_pct=('%0.1f %%'%node['base_pct']) if node['base_total'] else '—'
            item=QTreeWidgetItem([text,count,parent_pct,overall_pct])
            item.setData(0,Qt.ItemDataRole.UserRole,node)
            if parent is None:self.industry_tree.addTopLevelItem(item)
            else:parent.addChild(item)
            for i,child in enumerate(node['children'],1):append(item,child,number+str(i))
        for n,node in enumerate(nodes,1):append(None,node,str(n))
        self.industry_tree.expandToDepth(1)
        self.industry_tree.setColumnWidth(0,max(280,self.industry_tree.width()//2))
        self.industry_tree.setColumnWidth(1,58)
        self.industry_tree.setColumnWidth(2,90)
        self.industry_tree.setColumnWidth(3,88)
        self.industry_tree.blockSignals(False)

    def _overview_html(self):
        return getattr(self,'_observation_html','')

    def on_industry_selection(self):
        import html
        selected=self.industry_tree.selectedItems()
        if not selected or not self._analysis_frames:return
        node=selected[0].data(0,Qt.ItemDataRole.UserRole)
        if not node:return
        detail=type_detail(self._analysis_frames,node,self.lang)
        t=self.T
        lines=[f'<h2>{html.escape(node["name"])} — n={node["count"]}</h2>',
               f'<p>{html.escape(t("parent_share"))}: {node["parent_pct"]:.1f}% &nbsp; | &nbsp; {html.escape(t("overall_share"))}: {node["base_pct"]:.1f}%</p>']
        for field in detail['fields']:
            lines.append(f'<h3>{html.escape(field["name"])} (n={field["valid"]})</h3><table width="100%" cellspacing="4">')
            for row in field['options'][:15]:
                lines.append(f'<tr><td>{html.escape(row["label"])}</td><td>{row["count"]}</td><td>{row["pct"]:.1f}%</td></tr>')
            lines.append('</table>')
            if field['missing']:lines.append(f'<p>{html.escape(t("missing"))}: {field["missing"]}</p>')
            if field['multi']:lines.append(f'<p>{html.escape(t("multi_warning"))}</p>')
        if detail['metrics']:
            lines.append('<h3>'+html.escape(t('measurements'))+'</h3>')
            for metric in detail['metrics']:
                lines.append(f'<p>{html.escape(metric["name"])}: n={metric["n"]}, {html.escape(t("mean"))} {metric["mean"]}, {html.escape(t("range"))} {metric["min"]}–{metric["max"]}</p>')
        self.result_details.setHtml(''.join(lines))

    def update_dashboard_graphs(self):
        for i,(card,heading,picture) in enumerate(zip(self.dashboard_graph_cards,self.dashboard_graph_headers,self.dashboard_graph_images)):
            if i<len(self.dashboard_chart_paths):
                title,path=self.dashboard_chart_paths[i]
                card.setVisible(True);heading.setText(title)
                picture.setProperty('imagepath',path)
            else:
                # Empty datasets never display invented placeholder numbers/charts.
                card.setVisible(False);picture.setProperty('imagepath','')
        self.redraw_dashboard_graphs()

    def redraw_dashboard_graphs(self):
        if not self.dashboard_chart_paths:return
        columns=1 if self.width()<950 else 2
        cell_width=max(170,int(self.dashboard_splitter.width()/max(columns,1))-100)
        for picture in self.dashboard_graph_images:
            path=picture.property('imagepath')
            if not path:continue
            image=QPixmap(str(path))
            if image.isNull():picture.setText(self.T('no_charts'));continue
            picture.setPixmap(image.scaled(QSize(cell_width,230),Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation))

    def update_graphs(self):
        while self.graphs_layout.count()>2:
            item=self.graphs_layout.takeAt(1)
            if item.widget():item.widget().deleteLater()
        if self.chart_paths:
            self.charts_info.setText(f'{self.T("visuals")} · {len(self.chart_paths)}')
            for path in self.chart_paths:
                label=QLabel();label.setObjectName('graphPicture')
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred)
                label.setProperty('imagepath',path)
                label.setMinimumHeight(200)
                self.graphs_layout.insertWidget(self.graphs_layout.count()-1,label)
            self.redraw_graphs()
        else:self.charts_info.setText(self.T('no_charts'))

    def redraw_graphs(self):
        try:target=max(200,min(820,self.tabs.width()-65))
        except Exception:target=680
        for i in range(1,self.graphs_layout.count()-1):
            label=self.graphs_layout.itemAt(i).widget()
            if not label:continue
            img=QPixmap(label.property('imagepath'))
            if not img.isNull():
                scaled=img.scaledToWidth(target,Qt.TransformationMode.SmoothTransformation)
                label.setPixmap(scaled)
                label.setMinimumHeight(scaled.height()+8)

    def update_preview(self):
        if not self.last_report:
            self.preview_browser.setPlainText(self.T('preview_empty'));return
        from docx import Document
        try:
            doc=Document(self.last_report)
            snippet=[]
            for para in doc.paragraphs:
                if para.text.strip():snippet.append(para.text.strip())
                if len(snippet)>=30:break
            import html
            body=''.join(f'<p>{html.escape(x)}</p>' for x in snippet)
            self.preview_browser.setHtml('<h2>'+self.T('preview_doc')+'</h2><p>'+html.escape(self.last_report)+'</p>'+body)
        except Exception as exc:self.preview_browser.setPlainText(str(exc))

    def open_report(self):
        if self.last_report:QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.last_report).resolve())))

    def open_report_folder(self):
        self.output_dir.mkdir(parents=True,exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.output_dir.resolve())))

    def choose_report(self):
        file,_=QFileDialog.getOpenFileName(self,self.T('view_report'),str(self.output_dir),'Word (*.docx)')
        if file:self.last_report=file;self.update_reports_page()

    def update_reports_page(self):
        if not self.last_report:self.report_detail.setPlainText(self.T('no_report'));return
        self.report_detail.setHtml('<h2>'+self.T('preview_doc')+'</h2><p>'+str(Path(self.last_report).name)+'</p>')
        self.update_preview()
        # Reports page has a dedicated preview; preserve paragraph structure.
        try:
            from docx import Document
            import html
            doc=Document(self.last_report)
            chunks=[]
            for p in doc.paragraphs[:90]:
                if p.text.strip():
                    tag='h3' if p.style.name.startswith('Heading') else 'p'
                    chunks.append('<'+tag+'>'+html.escape(p.text)+'</'+tag+'>')
            self.report_detail.setHtml('<h2>'+self.T('preview_doc')+'</h2>'+''.join(chunks))
        except Exception:pass

    def _language_choice(self):
        """Choose the Access TEMPLATE language independently from the current UI language."""
        dlg=QDialog(self)
        dlg.setWindowTitle('Veritabanı Dili / Database Language')
        dlg.setMinimumWidth(340)
        layout=QVBoxLayout(dlg)
        message=QLabel('Yeni Access veritabanının dili / Language of your new Access database')
        message.setWordWrap(True)
        layout.addWidget(message)
        row=QHBoxLayout()
        options={}
        for code,caption,flag in (('tr','Türkçe','flag_tr.png'),('en','English','flag_en.png')):
            button=QPushButton(caption)
            button.setIcon(QIcon(str(resource(flag))))
            button.setIconSize(QSize(34,22))
            button.setCheckable(True)
            button.setMinimumHeight(48)
            button.setChecked(code==self.lang)
            row.addWidget(button)
            options[code]=button
            button.clicked.connect(lambda checked,x=code: [b.setChecked(k==x) for k,b in options.items()])
        layout.addLayout(row)
        actions=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        actions.accepted.connect(dlg.accept)
        actions.rejected.connect(dlg.reject)
        layout.addWidget(actions)
        if dlg.exec()!=QDialog.DialogCode.Accepted:
            return None
        return 'en' if options['en'].isChecked() else 'tr'

    def new_database(self,checked=False,language=None):
        """One choice of TR/EN template; never infer DB language from interface flag."""
        language=language if language in ('tr','en') else self._language_choice()
        if language is None:
            return
        from .repository import template_path
        if template_path(language) is None:
            self._message('Lithos Access templates are missing. / Lithos Access şablonları bulunamadı. '
                          'The installer must contain both original-schema blank .accdb files. '
                          'Run 01_ACCESS_SABLONLARI_OLUSTUR.bat before packaging. '
                          'Kurulum öncesi 01_ACCESS_SABLONLARI_OLUSTUR.bat çalıştırılmalıdır.',True)
            return
        filename=('Lithos_GURBELEN18_Blank_EN.accdb' if language=='en'
                  else 'Lithos_GURBELEN18_Bos_TR.accdb')
        path,_=QFileDialog.getSaveFileName(self,self.T('create_db'),str(documents()/filename),'Access (*.accdb)')
        if not path:
            return
        if not path.lower().endswith('.accdb'):
            path+='.accdb'
        try:
            created=create_database(path,lang=language)
            self.load_db(str(created))
            self.switch_page(2)
            self._message(self.T('success_db'))
        except Exception as exc:
            self._message(str(exc),True)

    def refresh_database(self):
        table=self.table_select.currentData()
        if not self.path or not table:
            self.db_table.setRowCount(0);self.db_table.setColumnCount(0)
            self.db_info.setText(self.T('db_no_data'))
            self._toggle_db_edit(False)
            return
        try:
            store=DataStore(self.path)
            df=store.get_table(table,limit=500)
            self.db_table.setRowCount(len(df));self.db_table.setColumnCount(len(df.columns))
            self.db_table.setHorizontalHeaderLabels([report_label(table,x,self.lang) for x in df.columns])
            for i,row in enumerate(df.itertuples(index=False,name=None)):
                for j,value in enumerate(row):
                    item=QTableWidgetItem('' if value is None else str(value))
                    item.setToolTip(str(value) if value is not None else '')
                    self.db_table.setItem(i,j,item)
            self.db_table.resizeColumnsToContents()
            max_width=240
            for i in range(self.db_table.columnCount()):
                self.db_table.setColumnWidth(i,min(max_width,max(120,self.db_table.columnWidth(i))))
            total=store.counts().get(table,len(df))
            self.db_info.setText(f'{table_label(table,self.lang)}: {len(df)} / {total} {self.T("records")}')
            editable=False  # Original Access records are edited in Microsoft Access, not in Lithos
            self._toggle_db_edit(editable)
        except Exception as exc:self.db_info.setText(str(exc));self._toggle_db_edit(False)

    def _toggle_db_edit(self,enabled):
        for btn in (self.add_btn,self.edit_btn,self.delete_btn):btn.setEnabled(enabled)

    def open_in_access(self):
        if self.path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.path).resolve())))

    def _compact_navigation(self):
        if not hasattr(self,'navs'):return
        narrow=self.width()<955
        for btn,key in self.navs:
            btn.setText(self.T(key))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly if narrow
                                   else Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setMinimumWidth(44 if narrow else 74)
            btn.setMaximumWidth(60 if narrow else 110)
        if hasattr(self,'logo'):
            self.logo.setFixedWidth(53 if narrow else 85)
            pix=QPixmap(str(resource('handaxe_realistic.png')))
            if not pix.isNull():self.logo.setPixmap(pix.scaled(48 if narrow else 82,
                     75 if narrow else 101,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        if hasattr(self,'brand_sub'):self.brand_sub.setVisible(self.width()>=750)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._compact_navigation()
        if hasattr(self,'splitter'):
            narrow=self.width()<950
            # Main input panel stacks above the analysis only on genuinely narrow windows.
            orientation=Qt.Orientation.Vertical if narrow else Qt.Orientation.Horizontal
            if self.splitter.orientation()!=orientation:
                self.splitter.setOrientation(orientation)
                self.splitter.setSizes([265,600] if narrow else [306,1010])
        if hasattr(self,'dashboard_splitter'):
            cols=2 if self.width()<1180 else 4
            if getattr(self,'_last_metric_cols',None)!=cols:
                self.reflow_cards(cols);self._last_metric_cols=cols
            graphcols=1 if self.width()<955 else 2
            if getattr(self,'_last_graph_cols',None)!=graphcols:
                self.reflow_graph_cards(graphcols);self._last_graph_cols=graphcols
            direction=Qt.Orientation.Vertical if self.width()<1160 else Qt.Orientation.Horizontal
            if self.dashboard_splitter.orientation()!=direction:
                self.dashboard_splitter.setOrientation(direction)
                self.dashboard_splitter.setSizes([360,500] if direction==Qt.Orientation.Vertical else [450,690])
            self.redraw_dashboard_graphs()
        if hasattr(self,'top_credit'):self.top_credit.setVisible(self.width()>=940)
        if hasattr(self,'tabs') and self.chart_paths:self.redraw_graphs()


def launch():
    app=QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(resource('lithos_v102.ico'))))
    app.setOrganizationName('Lithos');app.setApplicationName('Lithos')
    app.setStyle('Fusion')
    win=LithosWindow();win.show()
    return app.exec()

if __name__=='__main__':raise SystemExit(launch())
