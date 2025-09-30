import warnings
warnings.filterwarnings("ignore", message="Thread 'MainThread': missing ScriptRunContext!")
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")

import re
import time
from datetime import datetime
from io import StringIO, BytesIO

import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from auto_bi_backend import *

# ✅ Load custom CSS from external file
custom_css="""
/* ======================================================================
   GLOBAL & BASE STYLES
====================================================================== */

.stApp {
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}


.card,
.kpi-container,
.report-section,
.data-overview-box,
.insight-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.1);
}

.data-overview-box {
    padding: 1.5rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e3e8ee;
    box-shadow: 0 4px 12px rgba(44, 62, 80, 0.12);
}

.report-section,
.insight-card {
    border-left: 4px solid #3498db;
    margin-bottom: 1rem;
}

.insight-point {
    background: #f8f9fa;
    padding: 0.8rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    border-left: 3px solid #27ae60;
}

.warning-point {
    background: #fff3cd;
    padding: 0.8rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    border-left: 3px solid #ffc107;
}

/* ======================================================================
   TEXT & TYPOGRAPHY
====================================================================== */

.data-overview-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #2c3e50;
    text-align: center;
    margin-bottom: 1.2rem;
}

.report-header {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.insight-card {
    font-weight: 500;
    font-size: 1.1rem;
    color: #2c3e50;
    line-height: 1.5;
}

/* Bigger metrics */
.big-metric div[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #2980b9 !important;
}

.big-metric div[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}

/* ======================================================================
   METRICS & KPIs
====================================================================== */

.kpi-container {
    text-align: center;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border: 1px solid #e3e8ee;
}

.kpi-value {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    color: #2980b9;
}

.kpi-label {
    font-size: 0.9rem;
    margin-top: 0.5rem;
    color: #7f8c8d;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    font-weight: 600;
}

/* ======================================================================
   BUTTONS & CONTROLS
====================================================================== */

.stButton>button {
    background-color: #2980b9;
    color: white;
    border-radius: 4px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #2471a3;
    color: white;
}

.chart-controls {
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
    align-items: center;
}

.chart-control-button {
    padding: 4px 8px !important;
    font-size: 12px !important;
    min-width: 40px !important;
    height: 28px !important;
}

/* ======================================================================
   AGGREGATION CONTROLS
====================================================================== */

.agg-control {
    display: inline-flex;
    align-items: center;
    gap: 1px;
    background: #f0f2f6;
    padding: 4px 8px;
    border-radius: 4px;
    margin-bottom: 10px;
}

.agg-button {
    padding: 2px 6px !important;
    font-size: 11px !important;
    min-width: 35px !important;
    height: 24px !important;
}

.agg-button.active {
    background-color: #2980b9 !important;
    color: white !important;
}

/* ======================================================================
   TOGGLES & RADIO
====================================================================== */

.stRadio > div {
    flex-direction: row !important;
    gap: 10px !important;
}

/* Toggle Switch */
div[data-baseweb="toggle"] {
    background-color: #3396D3;
}

div[data-baseweb="toggle"]:hover {
    background-color: #2a7cb1;
}

div[data-baseweb="toggle"] div {
    background-color: white;
}

.stToggle label {
    color: white;
    font-weight: 600;
}

.stToggle input:checked + div {
    background-color: #3396D3;
}

/* ======================================================================
   DASHBOARD BUILDER
====================================================================== */

.dashboard-component {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-component-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0f0f0;
}

/* ======================================================================
   NEW CANVA-LIKE LAYOUT (ADDED)
====================================================================== */

/* Fixed-size dashboard canvas */
.dashboard-canvas {
    position: relative;
    margin: 20px auto;
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    overflow: hidden;
}

/* Preset sizes */
.canvas-a4 {
    width: 794px;   /* A4 width at ~96 DPI */
    height: 1123px; /* A4 height */
}

.canvas-slide {
    width: 1280px;
    height: 720px;
}

.canvas-custom {
    width: var(--canvas-width, 1000px);
    height: var(--canvas-height, 800px);
}

/* Dashboard items */
.dashboard-item {
    position: absolute;
    background: #ffffff;
    border: 1px solid #dcdcdc;
    border-radius: 6px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    padding: 10px;
    cursor: move;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.dashboard-item:hover {
    border-color: #3498db;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

/* Resize handle */
.dashboard-item::after {
    content: "";
    position: absolute;
    right: 4px;
    bottom: 4px;
    width: 12px;
    height: 12px;
    background: #3498db;
    border-radius: 2px;
    cursor: se-resize;
    opacity: 0.8;
}

/* Drag handle */
.drag-handle {
    width: 100%;
    height: 20px;
    position: absolute;
    top: 0;
    left: 0;
    cursor: grab;
    background: linear-gradient(to right, #f8f9fa, #e9ecef);
    border-bottom: 1px solid #e0e0e0;
    border-radius: 6px 6px 0 0;
}

.drag-handle:active {
    cursor: grabbing;
}

/* Export mode (clean download) */
.export-mode .dashboard-canvas {
    border: none;
    box-shadow: none;
}

.export-mode .dashboard-item {
    border: none;
    box-shadow: none;
}

"""
st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)


# Page configuration
st.set_page_config(
    page_title="Auto BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'original_df': None,
        'processed_df': None,
        'preprocessing_done': False,
        'analysis': None,
        'file_uploaded': False,
        'processing_stats': {},
        'current_tab': "🚀 Dashboard",
        'dashboard_agg_func': "mean",
        'chart_types': {},
        'dashboard_components': [],
        'current_dashboard': "Main Dashboard"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def handle_file_upload(uploaded_file):
    """Handle file upload with error handling and support for multiple formats"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None
            
        # Reset session state when new file is uploaded
        st.session_state.original_df = df.copy()
        st.session_state.processed_df = df.copy()
        st.session_state.preprocessing_done = False
        st.session_state.file_uploaded = True
        st.session_state.analysis = analyze_columns(df)
        st.session_state.uploaded_file_name = uploaded_file.name
        
        st.success("📁 File uploaded successfully! Go to the 🧹 Data Preprocessing tab to clean your data.")
        return df
        
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.info("Please make sure your file is properly formatted and try again.")
        return None

def show_data_preprocessing():
    """Show data cleaning options and perform preprocessing"""
    df = st.session_state.original_df.copy()

    st.markdown("## 🧹 Data Quality Check & Preprocessing")

    # Show data quality analysis
    show_data_quality_analysis(df)

    # Preprocessing options
    st.markdown("### ⚙️ Data Cleaning Options")
    st.markdown("Select the preprocessing steps you want to apply to your data")

    # Drop columns selection
    drop_cols = []
    with st.expander("Select Columns to Drop (optional)"):
        all_columns = df.columns.tolist()
        drop_cols = st.multiselect("Drop columns from dataset", options=all_columns, default=[])

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        remove_duplicates = st.checkbox(
            "🔄 Remove Duplicate Rows",
            help="Remove identical rows from your dataset",
            value=False
        )

    custom_fill_values = {}

    with col2:
        null_handling = st.selectbox(
            "❌ Handle Missing Values",
            options=[
                "Do Nothing",
                "Remove Rows with Missing Values",
                "Fill with Average (Mean) – the usual value",
                "Fill with Middle Value (Median)",
                "Fill with Most Common Value (Mode)",
                "Custom Fill Values"
            ],
            help="Choose how to handle missing values",
            index=0
        )

        if null_handling == "Custom Fill Values":
            st.info("Specify custom fill values for each column")
            for col in df.columns:
                if df[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(df[col]):
                        default_val = df[col].mean()
                    else:
                        default_val = df[col].mode()[0] if not df[col].mode().empty else ""
                    custom_val = st.text_input(f"Value for {col}", value=str(default_val))
                    try:
                        custom_fill_values[col] = float(custom_val) if custom_val.replace('.', '', 1).isdigit() else custom_val
                    except:
                        custom_fill_values[col] = custom_val

    with col3:
        if st.button("🚀 Process", type="primary", use_container_width=True):
            with st.spinner("Processing data..."):
                try:
                    processed_df, processing_stats = process_data(
                        df,
                        remove_duplicates,
                        null_handling,
                        custom_fill_values,
                        drop_columns=drop_cols
                    )
                    st.session_state.processed_df = processed_df
                    st.session_state.preprocessing_done = True
                    st.session_state.processing_stats = processing_stats
                    st.session_state.analysis = analyze_columns(processed_df)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing data: {str(e)}")

    # Show preview of what will happen
    if remove_duplicates or null_handling != "Do Nothing" or drop_cols:
        show_preprocessing_preview(df, remove_duplicates, null_handling, drop_columns=drop_cols)

def show_data_quality_analysis(df):
    """Analyze and display data quality issues"""
    st.markdown("### 📊 Data Quality Analysis")
    
    stats = get_data_quality_stats(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Rows", f"{stats['total_rows']:,}")
    with col2:
        st.metric("📊 Total Columns", stats['total_cols'])
    with col3:
        st.metric("🔄 Duplicate Rows", stats['duplicate_rows'])
    with col4:
        st.metric("❌ Missing Values", f"{stats['missing_values']:,}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if stats['duplicate_rows'] > 0:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"""
            **⚠️ Duplicate Rows Found**
            - {stats['duplicate_rows']} duplicate rows detected ({stats['duplicate_rows']/stats['total_rows']*100:.1f}% of data)
            - This may affect analysis accuracy
            - Consider removing duplicates for cleaner insights
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**✅ No Duplicate Rows**\nYour data is clean of duplicates!")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if stats['missing_values'] > 0:
            missing_by_col = df.isnull().sum()
            missing_by_col = missing_by_col[missing_by_col > 0]
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"""
            **⚠️ Missing Values Found**
            - {stats['missing_values']:,} missing values across {len(missing_by_col)} columns
            - {stats['missing_values']/(df.size)*100:.1f}% of all data points are missing
            """)
            
            if len(missing_by_col) <= 5:
                for col, count in missing_by_col.items():
                    st.markdown(f"- **{col}**: {count} missing ({count/stats['total_rows']*100:.1f}%)")
            else:
                st.markdown("- Multiple columns affected (see data summary for details)")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**✅ No Missing Values**\nYour data is complete!")
            st.markdown('</div>', unsafe_allow_html=True)
    
    if stats['missing_values'] > 0:
        with st.expander("📋 View Detailed Missing Values by Column"):
            missing_details = df.isnull().sum().reset_index()
            missing_details.columns = ['Column', 'Missing Values']
            missing_details = missing_details[missing_details['Missing Values'] > 0]
            missing_details['Percentage'] = (missing_details['Missing Values'] / len(df) * 100).round(2)
            st.dataframe(missing_details, use_container_width=True)

def show_preprocessing_preview(df, remove_duplicates, null_handling, drop_columns=None):
    preview_df = df.copy()

    if drop_columns:
        preview_df = preview_df.drop(columns=drop_columns, errors='ignore')

    if remove_duplicates:
        preview_df = preview_df.drop_duplicates()

    if null_handling == "Remove Rows with Missing Values":
        preview_df = preview_df.dropna()
    elif null_handling == "Fill with Average (Mean) – the usual value":
        preview_df = preview_df.fillna(preview_df.mean(numeric_only=True))
    elif null_handling == "Fill with Middle Value (Median)":
        preview_df = preview_df.fillna(preview_df.median(numeric_only=True))
    elif null_handling == "Fill with Most Common Value (Mode)":
        for col in preview_df.columns:
            mode_val = preview_df[col].mode()
            if not mode_val.empty:
                preview_df[col] = preview_df[col].fillna(mode_val[0])

    st.markdown("### 🔎 Preview of the dataset after these changes:")
    st.dataframe(preview_df.head(), use_container_width=True)

def create_smart_dashboard(df):
    """Create the main dashboard with conditional sidebar"""
    if st.session_state.analysis is None:
        st.session_state.analysis = analyze_columns(df)
    analysis = st.session_state.analysis

    # Initialize tab selection
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "🚀 Dashboard"

    # Clear and rebuild sidebar based on active tab
    st.sidebar.empty()
    with st.sidebar:
        if st.session_state.active_tab == "🎨 Custom Dashboard":
            show_custom_dashboard_sidebar()
        else:
            show_default_sidebar()

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Dashboard", "🔍 Custom Analysis", "📊 All Relationships", 
        "📈 Data Summary", "🎨 Custom Dashboard"
    ])

    # Track which tab is active using a hidden method
    # This uses the fact that only the active tab's content is rendered
    active_tab_detected = None

    with tab1:
        active_tab_detected = "🚀 Dashboard"
        create_dashboard_tab(df, analysis)

    with tab2:
        active_tab_detected = "🔍 Custom Analysis" 
        create_custom_analysis_tab(df, analysis)

    with tab3:
        active_tab_detected = "📊 All Relationships"
        create_relationship_explorer(df, analysis)

    with tab4:
        active_tab_detected = "📈 Data Summary"
        create_data_summary_tab(df, analysis)
        
    with tab5:
        active_tab_detected = "🎨 Custom Dashboard"
        create_custom_dashboard_tab(df, analysis)

    # Update the active tab if it changed
    if active_tab_detected and active_tab_detected != st.session_state.active_tab:
        st.session_state.active_tab = active_tab_detected
        st.rerun()
def show_default_sidebar():
    """Show the default app sidebar"""
    st.header("📁 Data Upload")
    
    uploaded_file = st.file_uploader(
        "Drag and drop file here",
        type=['csv', 'xlsx', 'xls'],
        help="Limit 200MB per file - CSV, XLSX, XLS"
    )
    
    if uploaded_file is not None:
        # Check if this is a new file or the same file
        current_file = st.session_state.get('uploaded_file_name')
        if current_file != uploaded_file.name:
            # New file uploaded
            df = handle_file_upload(uploaded_file)
            if df is not None:
                # Force rerun to update the UI
                st.rerun()
    
    st.divider()
    
    # ONLY ONE BACK BUTTON: Show it when user is in analysis mode
    if st.session_state.file_uploaded and st.session_state.preprocessing_done:
        if st.session_state.current_page == 'analysis':
            if st.button("← Back to Data Processing", 
                       key="single_back_button",
                       use_container_width=True):
                st.session_state.current_page = 'processing'
                st.rerun()
    
    # Rest of the sidebar content for processed data
    if st.session_state.file_uploaded and st.session_state.preprocessing_done:
        st.markdown("### Processed Data")
        st.metric("Clean Rows", f"{len(st.session_state.processed_df):,}")
        st.metric("Clean Columns", len(st.session_state.processed_df.columns))

        if 'processing_stats' in st.session_state and st.session_state.processing_stats:
            stats = st.session_state.processing_stats
            with st.expander("📈 Processing Statistics"):
                st.write(f"Original rows: {stats.get('original_rows', 'N/A')}")
                st.write(f"Duplicates removed: {stats.get('duplicates_removed', 'N/A')}")
                st.write(f"Null rows removed: {stats.get('null_rows_removed', 'N/A')}")
                st.write(f"Null values filled: {stats.get('null_values_filled', 'N/A')}")
                st.write(f"Final rows: {stats.get('final_rows', 'N/A')}")

        if st.button("🔄 Reset & Reprocess", 
                   key="reset_reprocess_button",
                   use_container_width=True):
            st.session_state.preprocessing_done = False
            st.session_state.current_page = 'processing'
            st.rerun()

        st.markdown("---")
        st.markdown("### 💾 Export Options")
        if st.button("📥 Download Processed Data", 
                   key="download_processed_data",
                   use_container_width=True):
            csv = st.session_state.processed_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # NEW: Add Upload New Dataset button to default sidebar too
    if st.session_state.file_uploaded:
        st.markdown("---")
        if st.button("📁 Upload New Dataset", 
                   key="upload_new_dataset_from_default",
                   use_container_width=True,
                   help="Upload a different dataset"):
            # Reset the application state to go back to upload page
            st.session_state.file_uploaded = False
            st.session_state.preprocessing_done = False
            st.session_state.original_df = None
            st.session_state.processed_df = None
            st.session_state.current_page = 'upload'
            st.session_state.dashboard_components = []  # Clear dashboard components
            st.rerun()
    
    st.divider()
    st.header("📋 About")
    st.write("This Auto BI Dashboard automatically:")
    st.write("- Analyzes your data structure")
    st.write("- Cleans and preprocesses data")
    st.write("- Generates smart insights")
    st.write("- Creates interactive visualizations")
    
    if st.session_state.dashboard_components:
        st.divider()
        st.markdown("### 🎨 Your Dashboard")
        comp_count = len(st.session_state.dashboard_components)
        kpi_count = len([c for c in st.session_state.dashboard_components if c['type'] == 'kpi'])
        chart_count = len([c for c in st.session_state.dashboard_components if c['type'] == 'chart'])
        st.write(f"**{comp_count} components ready:**")
        st.write(f"📊 {kpi_count} KPIs • 📈 {chart_count} Charts")
        st.write("Go to **Custom Dashboard** tab to build!")
def show_custom_dashboard_sidebar():
    """Show a visually distinct sidebar ONLY for Custom Dashboard with better visibility"""
    
    st.sidebar.empty()
    
    with st.sidebar:
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
        '>
            <h2 style='color: white; margin: 0; font-size: 1.4em;'>🎨 Dashboard Builder</h2>
            <p style='margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9em;'>Build your perfect dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎛️ Dashboard Controls")
        
        dashboard_name = st.text_input(
            "Dashboard Name", 
            value=st.session_state.current_dashboard,
            key="custom_dash_name"
        )
        st.session_state.current_dashboard = dashboard_name
        
        control_col1, control_col2 = st.columns(2)
        with control_col1:
            if st.button("💾 Save", use_container_width=True, 
                        help="Save current dashboard layout"):
                save_dashboard_layout(dashboard_name)
        with control_col2:
            if st.button("🔄 New", use_container_width=True, 
                        help="Start a new dashboard"):
                clear_dashboard_layout()
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 🧩 Component Library")
        
        if not st.session_state.dashboard_components:
            st.markdown("""
            <div style='
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #6c757d;
                border: 1px solid #dee2e6;
            '>
                <p style='margin: 0; color: #495057; font-size: 0.9em;'>
                    <strong>No components yet!</strong><br>
                    Add components from other tabs using <strong>＋</strong> buttons
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            total_comps = len(st.session_state.dashboard_components)
            kpi_count = len([c for c in st.session_state.dashboard_components if c['type'] == 'kpi'])
            chart_count = len([c for c in st.session_state.dashboard_components if c['type'] == 'chart'])
            
            st.markdown(f"""
            <div style='
                background: #d4edda;
                padding: 12px;
                border-radius: 8px;
                border-left: 4px solid #28a745;
                border: 1px solid #c3e6cb;
                margin-bottom: 15px;
            '>
                <div style='display: flex; justify-content: space-between; color: #155724;'>
                    <span><strong>Ready to build!</strong></span>
                    <span><strong>{total_comps} components</strong></span>
                </div>
                <div style='display: flex; justify-content: space-between; font-size: 0.9em; color: #155724;'>
                    <span>📊 {kpi_count} KPIs</span>
                    <span>📈 {chart_count} Charts</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📦 Your Components", expanded=True):
                display_custom_dashboard_components()
        
        st.markdown("---")
        
        st.markdown("### 💡 Building Guide")
        st.markdown("""
        <div style='
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            border: 1px solid #ffeaa7;
        '>
            <strong style='color: #856404;'>Quick Steps:</strong>
            <ol style='margin: 10px 0; padding-left: 20px; color: #856404; font-size: 0.9em;'>
                <li>Go to other tabs</li>
                <li>Click <strong>＋</strong> on components</li>
                <li>They appear here automatically</li>
                <li>Build your dashboard!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # NEW: Add button to go back to upload page
        st.markdown("---")
        if st.button("📁 Upload New Dataset", 
                   key="upload_new_dataset_from_custom",
                   use_container_width=True,
                   help="Go back to upload a new dataset"):
            # Reset the application state to go back to upload page
            st.session_state.file_uploaded = False
            st.session_state.preprocessing_done = False
            st.session_state.original_df = None
            st.session_state.processed_df = None
            st.session_state.current_page = 'upload'
            st.session_state.dashboard_components = []  # Clear dashboard components
            st.rerun()

def display_custom_dashboard_components():
    """Display components in the custom dashboard sidebar with distinct styling"""
    
    kpis = [c for c in st.session_state.dashboard_components if c['type'] == 'kpi']
    charts = [c for c in st.session_state.dashboard_components if c['type'] == 'chart']
    
    if kpis:
        st.markdown("**📊 Data KPIs**")
        for component in kpis:
            display_custom_dashboard_component(component)
    
    if charts:
        st.markdown("**📈 Visualization Charts**")
        for component in charts:
            display_custom_dashboard_component(component)

def display_custom_dashboard_component(component):
    """Display a single component with better text visibility and contrast"""
    
    # Better color combinations for contrast
    if component['type'] == 'kpi':
        bg_color = "#e3f2fd"  # Light blue
        border_color = "#1976d2"  # Dark blue
        text_color = "#0d47a1"  # Very dark blue
        subtitle_color = "#1565c0"  # Medium blue
    else:  # chart
        bg_color = "#f3e5f5"  # Light purple
        border_color = "#7b1fa2"  # Dark purple
        text_color = "#4a148c"  # Very dark purple
        subtitle_color = "#6a1b9a"  # Medium purple
    
    st.markdown(f"""
    <div style='
        background: {bg_color};
        border-left: 4px solid {border_color};
        border: 1px solid {border_color}33; /* Semi-transparent border */
        padding: 12px;
        margin: 8px 0;
        border-radius: 6px;
    '>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='flex: 1;'>
                <strong style='color: {text_color}; font-size: 14px; line-height: 1.2;'>{component['title']}</strong>
                <br>
                <small style='color: {subtitle_color}; font-size: 11px; font-weight: 500;'>{component['type'].title()}</small>
            </div>
            <div style='margin-left: 10px;'>
    """, unsafe_allow_html=True)
    
    # Remove button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("")  # Spacer
    with col2:
        if st.button("🗑️", key=f"sidebar_remove_{component['id']}", 
                    help=f"Remove {component['title']}",
                    use_container_width=True):
            remove_component_from_palette(component['id'])
            st.rerun()
    
    st.markdown("</div></div></div>", unsafe_allow_html=True)

def create_dashboard_tab(df, analysis):
    """Create the Dashboard tab with customizable charts"""
    
    if 'dashboard_agg_func' not in st.session_state:
        st.session_state.dashboard_agg_func = "mean"
    
    create_smart_kpis(df, analysis, st.session_state.dashboard_agg_func)
    
    # Aggregation header
    col1, col2 = st.columns([2, 1], vertical_alignment="center")

    with col1:
        current_agg = st.session_state.dashboard_agg_func
        if current_agg == "mean":
            agg_text = "Average"
        elif current_agg == "sum":
            agg_text = "Total"
        elif current_agg == "count":
            agg_text = "Count"
        else:
            agg_text = current_agg.title()

        st.markdown(f"### 📊 Key Relationships ({agg_text})")

    with col2:
        agg_options = ["Avg", "Sum"]
        agg_mapping = {"Avg": "mean", "Sum": "sum"}
        current_display = "Avg" if st.session_state.dashboard_agg_func == "mean" else "Sum"

        selected_agg_display = st.radio(
            "Aggregation Method",
            options=agg_options,
            index=agg_options.index(current_display),
            horizontal=True,
            label_visibility="collapsed",
            key="dashboard_agg_radio"
        )

        new_agg_func = agg_mapping[selected_agg_display]

        if new_agg_func != st.session_state.dashboard_agg_func:
            st.session_state.dashboard_agg_func = new_agg_func
            st.rerun()


    if analysis['numeric_cols'] and analysis['suitable_for_grouping']:
        insights_created = 0
        cols = st.columns(2)  # Create two columns for the charts
        
        for i, num_col in enumerate(analysis['numeric_cols'][:2]):
            for j, cat_col in enumerate(analysis['suitable_for_grouping'][:2]):
                with cols[insights_created % 2]:  # Alternate between columns
                    chart_key = f"dashboard_{num_col}_{cat_col}"
                    
                    if chart_key not in st.session_state.chart_types:
                        st.session_state.chart_types[chart_key] = "Bar Chart"
                    
                    # Create container for each chart with proper spacing
                    with st.container():
                        st.markdown("---")  # Separator between charts
                        create_dashboard_chart(
                            df, 
                            num_col, 
                            cat_col, 
                            chart_key,
                            st.session_state.chart_types[chart_key],
                            st.session_state.dashboard_agg_func
                        )
                        st.markdown("")  # Add some space below chart
                
                insights_created += 1
                if insights_created >= 4:  # Limit to 4 charts (2 per column)
                    break
            if insights_created >= 4:
                break
    else:
        st.warning("⚠️ Need both numeric and categorical columns for relationship charts")

def create_dashboard_chart(df, numeric_col, cat_col, key, chart_type, agg_func):
    """Create chart for dashboard with title that reflects chosen aggregation"""
    
    # Get the current aggregation function from session state
    current_agg_func = st.session_state.dashboard_agg_func
    
    # Create dynamic title based on chosen aggregation
    if current_agg_func == "mean":
        agg_display = "Average"
    elif current_agg_func == "sum":
        agg_display = "Total" 
    elif current_agg_func == "count":
        agg_display = "Count"
    else:
        agg_display = current_agg_func.title()
        
    chart_title = f"{agg_display} {numeric_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}"
    
    # Create a clean header with proper spacing
    header_col1, header_col2 = st.columns([2, 2])
    
    with header_col1:
        st.markdown(f"**{chart_title}**")
    
    with header_col2:
        # Chart type buttons in a compact row
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
        
        with btn_col1:
            is_active = st.session_state.chart_types[key] == "Bar Chart"
            if st.button("📊", key=f"{key}_bar", 
                       help="Bar chart",
                       use_container_width=True,
                       type="primary" if is_active else "secondary"):
                st.session_state.chart_types[key] = "Bar Chart"
                st.rerun()

        with btn_col2:
            is_active = st.session_state.chart_types[key] == "Pie Chart"
            if st.button("🥧", key=f"{key}_pie", 
                       help="Pie chart",
                       use_container_width=True,
                       type="primary" if is_active else "secondary"):
                st.session_state.chart_types[key] = "Pie Chart"
                st.rerun()

        with btn_col3:
            is_active = st.session_state.chart_types[key] == "Line Chart"
            if st.button("📈", key=f"{key}_line", 
                       help="Line chart",
                       use_container_width=True,
                       type="primary" if is_active else "secondary"):
                st.session_state.chart_types[key] = "Line Chart"
                st.rerun()
        
        with btn_col4:
            component_data = {
                'chart_type': chart_type,
                'numeric_col': numeric_col,
                'cat_col': cat_col,
                'agg_func': current_agg_func,
                'title': chart_title
            }
            is_added = get_component_status('chart', component_data)
            
            button_text = "－" if is_added else "＋"
            button_help = "Remove from dashboard" if is_added else "Add to dashboard"
            
            if st.button(button_text, 
                        key=f"toggle_{key}", 
                        help=button_help,
                        use_container_width=True):
                success, action = add_component_to_dashboard_handler('chart', component_data, chart_title)
                st.rerun()
    
    # Create the actual chart with current aggregation
    if chart_type == "Bar Chart":
        create_dashboard_bar_chart(df, numeric_col, cat_col, current_agg_func, key, chart_title)
    elif chart_type == "Pie Chart":
        create_dashboard_pie_chart(df, numeric_col, cat_col, current_agg_func, key, chart_title)
    elif chart_type == "Line Chart":
        create_dashboard_line_chart(df, numeric_col, cat_col, current_agg_func, key, chart_title)
def create_dashboard_bar_chart(df, numeric_col, cat_col, agg_func, key, chart_title=None):
    """Create bar chart with dynamic aggregation"""
    # Use session state aggregation function
    current_agg_func = st.session_state.dashboard_agg_func
    
    if current_agg_func == "mean":
        grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
    elif current_agg_func == "sum":
        grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
    elif current_agg_func == "count":
        grouped = df.groupby(cat_col)[numeric_col].count().reset_index()
    else:
        grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
    
    grouped.columns = [cat_col, numeric_col]
    grouped = grouped.nlargest(10, numeric_col)
    
    fig = px.bar(grouped, 
                x=cat_col, 
                y=numeric_col,
                color=numeric_col,
                color_continuous_scale='viridis')
    
    # Remove internal title and adjust layout
    fig.update_layout(
        height=350,  # Slightly reduced height
        showlegend=False, 
        margin=dict(t=20, b=40, l=40, r=20),  # Better margins
        
    )
    
    # Improve axis labels
    fig.update_xaxes(title_text=cat_col.replace('_', ' ').title())
    fig.update_yaxes(title_text=numeric_col.replace('_', ' ').title())
    
    st.plotly_chart(fig, use_container_width=True, key=key)

def create_dashboard_pie_chart(df, numeric_col, cat_col, agg_func, key, chart_title=None):
    """Create pie chart with dynamic aggregation"""
    current_agg_func = st.session_state.dashboard_agg_func
    
    if current_agg_func == "mean":
        grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
    elif current_agg_func == "sum":
        grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
    elif current_agg_func == "count":
        grouped = df.groupby(cat_col)[numeric_col].count().reset_index()
    else:
        grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
    
    grouped = grouped.nlargest(8, numeric_col)  # Limit to 8 for better pie chart
    
    fig = px.pie(grouped, values=numeric_col, names=cat_col)
    fig.update_layout(
        height=350,
        margin=dict(t=20, b=20, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True, key=key)

def create_dashboard_line_chart(df, numeric_col, cat_col, agg_func, key, chart_title=None):
    """Create line chart with dynamic aggregation"""
    current_agg_func = st.session_state.dashboard_agg_func
    
    if current_agg_func == "mean":
        grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
    elif current_agg_func == "sum":
        grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
    elif current_agg_func == "count":
        grouped = df.groupby(cat_col)[numeric_col].count().reset_index()
    else:
        grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
    
    grouped = grouped.nlargest(10, numeric_col)
    
    fig = px.line(grouped, x=cat_col, y=numeric_col)
    fig.update_layout(
        height=350,
        margin=dict(t=20, b=40, l=40, r=20),
    )
    
    # Improve axis labels
    fig.update_xaxes(title_text=cat_col.replace('_', ' ').title())
    fig.update_yaxes(title_text=numeric_col.replace('_', ' ').title())
    
    st.plotly_chart(fig, use_container_width=True, key=key)
def create_custom_analysis_tab(df, analysis):
    """Create custom analysis tab"""
   
    st.markdown(" ### *Choose any columns to explore their relationships*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if analysis['numeric_cols']:
            selected_numeric = st.selectbox(
                "📊 Numeric Column (What to measure)",
                options=analysis['numeric_cols'],
                help="Select the numeric value you want to analyze",
                key="custom_numeric"
            )
        else:
            selected_numeric = None
            st.warning("No numeric columns available")
    
    with col2:
        if analysis['suitable_for_grouping']:
            selected_category = st.selectbox(
                "Category Column (How to group)",
                options=analysis['suitable_for_grouping'],
                help="Select how you want to break down the data",
                key="custom_category"
            )
        else:
            selected_category = None
            st.warning("No suitable category columns available")
    
    with col3:
        chart_type = st.selectbox(
            "📈 Choose Chart Type",
            options=["Bar Chart", "Pie Chart", "Box Plot", "Violin Plot", "Scatter Plot", "Line Chart"],
            help="Select how you want to visualize the relationship",
            key="custom_chart_type"
        )
        
        if chart_type in ["Bar Chart", "Pie Chart", "Line Chart"]:
            agg_func = st.selectbox(
                "Aggregation Function",
                options=["mean", "sum", "count"],
                help="How to aggregate the numeric values",
                key="custom_agg_func"
            )
        else:
            agg_func = "mean"
    
    if selected_numeric and selected_category:
        st.markdown("### Analysis")
        create_custom_chart(df, selected_numeric, selected_category, chart_type, agg_func)
        
        insights = generate_insights(df, selected_numeric, selected_category, agg_func)
        for insight in insights:
            st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)
    
    if len(analysis['numeric_cols']) >= 2:
        st.markdown("#### Numeric Relationships")
        col1, col2 = st.columns(2)
        
        with col1:
            num_col1 = st.selectbox("X-axis", analysis['numeric_cols'], key="custom_x")
        with col2:
            num_col2 = st.selectbox("Y-axis", analysis['numeric_cols'], key="custom_y", index=1)
        
        if num_col1 != num_col2:
            create_correlation_chart(df, num_col1, num_col2)

def create_relationship_explorer(df, analysis):
    """Create relationship explorer tab"""
    st.markdown("### *Explore ALL possible relationships in your clean data*")
    
    if analysis['numeric_cols'] and analysis['suitable_for_grouping']:
        st.markdown("#### 🎯 All Numeric vs Category Relationships")
        
        relationship_count = 0
        for numeric_col in analysis['numeric_cols']:
            for cat_col in analysis['suitable_for_grouping']:
                if relationship_count % 3 == 0:
                    cols = st.columns(3)
                
                with cols[relationship_count % 3]:
                    with st.expander(f"📊 {numeric_col} by {cat_col}"):
                        create_mini_relationship_chart(df, numeric_col, cat_col, relationship_count)
                
                relationship_count += 1
        
        if len(analysis['numeric_cols']) >= 2:
            st.markdown("#### 🔗 Numeric Correlations")
            create_correlation_matrix(df, analysis['numeric_cols'])
    
    else:
        st.info("Upload data with both numeric and categorical columns to see relationships")

def create_data_summary_tab(df, analysis):
    """Show AI insights with proper error handling + PDF download"""
    ollama_url = "http://localhost:11434/api/tags"
    status_ok, status_msg = validate_ollama_connection()
    if status_ok:
        st.success(f"✅ {status_msg}")
    else:
        st.error(f"❌ {status_msg}")
        st.info("💡 Make sure Ollama is running and you've downloaded a model with: `ollama pull phi3:mini`")

    st.markdown("### 🤖 Data Insights")

    try:
        response = requests.get(ollama_url, timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            if model_names:
                selected_model = st.selectbox(
                    "🤖 Select AI Model",
                    options=model_names,
                    index=0,
                    help="Choose which local AI model to use for analysis"
                )
                st.session_state.selected_model = selected_model
        else:
            st.warning("⚠️ Ollama: Running but no models found")
    except requests.exceptions.ConnectionError:
        st.error("❌ Ollama: Not running. Start with: `ollama serve`")
    except Exception as e:
        st.error(f"❌ Ollama Error: {str(e)}")

    if st.button("✨ Generate Insights", key="generate_insights", use_container_width=True, type="primary"):
        with st.spinner("🔍 Analyzing your data..."):
            try:
                selected_model = st.session_state.get("selected_model", "phi3:mini")
                insights = generate_ai_insights(df, analysis, model_name=selected_model)
                st.session_state.ai_insights = insights
                st.session_state.insights_source = "Ollama AI"
                st.success("✅ Insights generated successfully!")
            except Exception as e:
                error_msg = f"❌ Failed to generate AI insights: {str(e)}"
                st.error(error_msg)
                st.info("🔄 Falling back to local insights...")
                local_insights = generate_local_insights(df, analysis)
                st.session_state.ai_insights = local_insights
                st.session_state.insights_source = "Local Analysis"
                st.success("✅ Local insights generated!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Insights", use_container_width=True):
            for k in ('ai_insights', 'ai_error', 'insights_source'):
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
    with col2:
        if st.button("🔄 Retry Connection", use_container_width=True):
            if 'ai_error' in st.session_state:
                del st.session_state.ai_error
            st.rerun()

    if 'ai_insights' in st.session_state and st.session_state.ai_insights:
        st.markdown("---")
        source = st.session_state.get('insights_source', 'AI Analysis')
        st.markdown(f"<h4 style='color:green;'>🔍 Generated Insights ({source})</h4>", unsafe_allow_html=True)
        st.markdown(st.session_state.ai_insights)

    st.markdown("---")

    col1, col2 = st.columns([1,4.5])
    
    with col1:
        download_format = st.selectbox(
            "Format",
            options=["Text", "PDF"],
            index=0,
            help="Select download format",
            label_visibility="collapsed"
        )
    
    with col2:
        download_content = st.session_state.get('ai_insights', '# AI Insights\n\nGenerate insights first to download.')
        download_filename = "ai_insights.txt"
        
        if download_format == "Text":
            st.download_button(
                label="📥 Download Insights",
                data=download_content,
                file_name=download_filename,
                mime="text/markdown",
                use_container_width=True,
                disabled=not st.session_state.get('ai_insights')
            )
        else:
            try:
                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer)
                styles = getSampleStyleSheet()
                
                if st.session_state.get('ai_insights'):
                    story = [Paragraph("<b>AI Data Insights</b>", styles['Title'])]
                    for line in st.session_state.ai_insights.split("\n"):
                        if line.strip():
                            story.append(Paragraph(line, styles['Normal']))
                    download_filename = "ai_insights.pdf"
                else:
                    story = [Paragraph("<b>AI Data Insights</b>", styles['Title'])]
                    story.append(Paragraph("Generate insights first to get detailed analysis.", styles['Normal']))
                    download_filename = "insights_template.pdf"
                
                doc.build(story)
                
                st.download_button(
                    label="📥 Download Insights",
                    data=pdf_buffer.getvalue(),
                    file_name=download_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error creating PDF: {str(e)}")

    st.markdown("---")
    st.markdown("### 📋 Dataset Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Records", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        missing_vals = df.isnull().sum().sum()
        st.metric("Missing Values", missing_vals)
    with col4:
        st.metric("Duplicate Rows", df.duplicated().sum())

    with st.expander("📊 Quick Data Overview"):
        st.write(f"**Numeric Columns:** {len(analysis.get('numeric_cols', []))}")
        st.write(f"**Categorical Columns:** {len(analysis.get('suitable_for_grouping', []))}")
        if analysis.get('numeric_cols'):
            st.write("**Top Numeric Columns:**", ", ".join(analysis['numeric_cols'][:3]))
        if analysis.get('suitable_for_grouping'):
            st.write("**Top Categories:**", ", ".join(analysis['suitable_for_grouping'][:3]))

def create_custom_dashboard_tab(df, analysis):
    """Main custom dashboard builder interface"""
    
    st.markdown("## 🎨 Custom Dashboard Builder")
    
    st.info("""
    💡 **Build your perfect dashboard:**
    - Add components from other tabs using **＋** buttons
    - Components appear automatically in the sidebar
    - Your dashboard builds here in real-time
    - Remove components anytime using 🗑️ buttons
    """)
    
    if st.session_state.dashboard_components:
        kpi_count = len([c for c in st.session_state.dashboard_components if c['type'] == 'kpi'])
        chart_count = len([c for c in st.session_state.dashboard_components if c['type'] == 'chart'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Components", len(st.session_state.dashboard_components))
        with col2:
            st.metric("KPIs", kpi_count)
        with col3:
            st.metric("Charts", chart_count)
    
    st.markdown("---")
    
    if st.session_state.dashboard_components:
        render_dashboard_canvas(df)
    else:
        show_empty_dashboard_state()

def show_empty_dashboard_state():
    """Show empty dashboard state with instructions"""
    
    st.markdown("### 🎨 Your Dashboard Canvas")
    
    empty_col1, empty_col2, empty_col3 = st.columns([1, 2, 1])
    
    with empty_col2:
        st.markdown("""
        <div style="text-align: center; padding: 40px; border: 2px dashed #ccc; border-radius: 10px; background: #f8f9fa;">
            <h3 style="color: #666;">🚀 Ready to Build Your Dashboard!</h3>
            <p>Your components will appear here as you add them.</p>
            <div style="font-size: 48px; margin: 20px 0;">📊 ➕ 📈</div>
            <p><strong>Check the sidebar for your component palette!</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **Quick Start Guide:**
        1. Go to the **🚀 Dashboard** or **🔍 Custom Analysis** tabs
        2. Click **＋** buttons on any KPIs or charts you want
        3. Return here - your components will be in the sidebar
        4. They'll automatically appear in this dashboard area
        """)
def get_component_status(component_type, component_data):
    """Check if a component is already in the dashboard"""
    component_id = f"{component_type}_{hash(str(component_data))}"
    existing_ids = [c['id'] for c in st.session_state.dashboard_components]
    return component_id in existing_ids

def add_component_to_dashboard_handler(component_type, component_data, title):
    """Handle adding/removing components to dashboard with toggle functionality"""
    component_id = f"{component_type}_{hash(str(component_data))}"
    
    # Check if component already exists
    existing_ids = [c['id'] for c in st.session_state.dashboard_components]
    
    if component_id in existing_ids:
        # Remove component if it exists (toggle off)
        remove_component_from_palette(component_id)
        return False, "removed"
    else:
        # Add component if it doesn't exist (toggle on)
        new_component = {
            'id': component_id,
            'type': component_type,
            'data': component_data,
            'title': title,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.dashboard_components.append(new_component)
        return True, "added"
def render_dashboard_canvas(df):
    """Render the dashboard canvas with components"""
    
    st.markdown("### 🎨 Your Dashboard")
    st.caption("Components you've added will appear here automatically")
    
    components = st.session_state.dashboard_components
    
    if not components:
        show_empty_dashboard_state()
        return
    
    num_columns = 2
    rows = [components[i:i + num_columns] for i in range(0, len(components), num_columns)]
    
    for row_index, row_components in enumerate(rows):
        cols = st.columns(len(row_components))
        
        for col_index, component in enumerate(row_components):
            with cols[col_index]:
                render_dashboard_component(df, component, row_index * num_columns + col_index)

def render_dashboard_component(df, component, index):
    """Render a single dashboard component"""
    
    st.markdown("<div style='border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 10px 0;'>", unsafe_allow_html=True)
    
    header_col1, header_col2 = st.columns([4, 1])
    
    with header_col1:
        icon = "📊" if component['type'] == 'kpi' else "📈"
        st.markdown(f"**{icon} {component['title']}**")
    
    with header_col2:
        if st.button("🗑️", key=f"remove_dash_{index}", help="Remove from dashboard"):
            remove_component_from_palette(component['id'])
            st.rerun()
    
    try:
        if component['type'] == 'kpi':
            render_kpi_in_dashboard(df, component)
        elif component['type'] == 'chart':
            render_chart_in_dashboard(df, component)
    except Exception as e:
        st.error(f"Error rendering component: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_kpi_in_dashboard(df, component):
    """Render a KPI component in the dashboard"""
    
    if component['data'].get('type') == 'total_records':
        value = len(df)
        display_value = f"{value:,}"
        label = "Total Records"
    else:
        col = component['data']['column']
        agg_func = component['data'].get('aggregation', 'mean')
        
        if agg_func == 'mean':
            value = df[col].mean()
            label = f"Avg {col.replace('_', ' ').title()}"
        else:
            value = df[col].sum()
            label = f"Total {col.replace('_', ' ').title()}"
        
        if value >= 1000000:
            display_value = f"{value/1000000:.1f}M"
        elif value >= 1000:
            display_value = f"{value/1000:.0f}K"
        else:
            display_value = f"{value:.1f}"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <div style="font-size: 2.5em; font-weight: bold; color: #2980b9;">{display_value}</div>
        <div style="font-size: 1.1em; color: #7f8c8d;">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_chart_in_dashboard(df, component):
    """Render a chart component in the dashboard"""
    
    data = component['data']
    chart_type = data.get('chart_type', 'Bar Chart')
    numeric_col = data.get('numeric_col')
    cat_col = data.get('cat_col')
    agg_func = data.get('agg_func', 'mean')
    
    if not numeric_col or numeric_col not in df.columns:
        st.warning("Chart data not available")
        return
    
    try:
        if chart_type == "Bar Chart":
            if agg_func == "mean":
                grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
            else:
                grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
            
            grouped.columns = [cat_col, numeric_col]
            grouped = grouped.nlargest(8, numeric_col)
            
            fig = px.bar(grouped, x=cat_col, y=numeric_col, color=numeric_col, color_continuous_scale='viridis')
            fig.update_layout(height=300, showlegend=False, margin=dict(t=20))
            
        elif chart_type == "Pie Chart":
            if agg_func == "mean":
                grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
            else:
                grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
            
            grouped = grouped.nlargest(8, numeric_col)
            fig = px.pie(grouped, values=numeric_col, names=cat_col)
            fig.update_layout(height=300, margin=dict(t=20))
            
        elif chart_type == "Line Chart":
            grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
            grouped = grouped.nlargest(8, numeric_col)
            fig = px.line(grouped, x=cat_col, y=numeric_col)
            fig.update_layout(height=300, margin=dict(t=20))
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")

def create_smart_kpis(df, analysis, agg_func=None):
    """Create smart KPIs that reflect chosen aggregation function"""
    
    # Use session state aggregation if not provided
    if agg_func is None:
        agg_func = st.session_state.dashboard_agg_func
    
    cols = st.columns(4)
    
    # Always show total records (not affected by aggregation)
    with cols[0]:
        kpi_col, plus_col = st.columns([5, 1])
        
        with kpi_col:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-value">{len(df):,}</div>
                <div class="kpi-label">Total Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with plus_col:
            component_data = {'type': 'total_records'}
            is_added = get_component_status('kpi', component_data)
            
            button_text = "－" if is_added else "＋"
            button_help = "Remove from dashboard" if is_added else "Add to dashboard"
            
            if st.button(button_text, 
                        key="toggle_total_records", 
                        help=button_help,
                        use_container_width=True):
                success, action = add_component_to_dashboard_handler('kpi', component_data, "Total Records")
                st.rerun()
    
    # Smart KPIs for numeric columns with dynamic aggregation
    for i, col in enumerate(analysis['numeric_cols'][:3]):
        with cols[i + 1]:
            kpi_col, plus_col = st.columns([5, 1])
            
            with kpi_col:
                if agg_func == "mean":
                    agg_val = df[col].mean()
                    label = f"Avg {col.replace('_', ' ').title()}"
                elif agg_func == "sum":
                    agg_val = df[col].sum()
                    label = f"Total {col.replace('_', ' ').title()}"
                elif agg_func == "count":
                    agg_val = df[col].count()
                    label = f"Count {col.replace('_', ' ').title()}"
                else:
                    agg_val = df[col].mean()  # Default to mean
                    label = f"Avg {col.replace('_', ' ').title()}"
                
                # Smart formatting
                if agg_val >= 1000000:
                    display_val = f"{agg_val/1000000:.1f}M"
                elif agg_val >= 1000:
                    display_val = f"{agg_val/1000:.0f}K"
                else:
                    display_val = f"{agg_val:.1f}"
                
                st.markdown(f"""
                <div class="kpi-container">
                    <div class="kpi-value">{display_val}</div>
                    <div class="kpi-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with plus_col:
                component_data = {
                    'column': col,
                    'aggregation': agg_func,
                    'title': label
                }
                is_added = get_component_status('kpi', component_data)
                
                button_text = "－" if is_added else "＋"
                button_help = "Remove from dashboard" if is_added else "Add to dashboard"
                
                button_key = f"toggle_kpi_{col}_{agg_func}"
                if st.button(button_text, 
                            key=button_key, 
                            help=button_help,
                            use_container_width=True):
                    success, action = add_component_to_dashboard_handler('kpi', component_data, label)
                    st.rerun()
def add_component_to_dashboard_handler(component_type, component_data, title):
    """Handle adding/removing components to dashboard with toggle functionality"""
    component_id = f"{component_type}_{hash(str(component_data))}"
    
    # Check if component already exists
    existing_ids = [c['id'] for c in st.session_state.dashboard_components]
    
    if component_id in existing_ids:
        # Remove component if it exists (toggle off)
        remove_component_from_palette(component_id)
        return False, "removed"
    else:
        # Add component if it doesn't exist (toggle on)
        new_component = {
            'id': component_id,
            'type': component_type,
            'data': component_data,
            'title': title,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.dashboard_components.append(new_component)
        return True, "added"

def get_component_status(component_type, component_data):
    """Check if a component is already in the dashboard"""
    component_id = f"{component_type}_{hash(str(component_data))}"
    existing_ids = [c['id'] for c in st.session_state.dashboard_components]
    return component_id in existing_ids

def remove_component_from_palette(component_id):
    """Remove component from dashboard palette"""
    st.session_state.dashboard_components = [
        c for c in st.session_state.dashboard_components if c['id'] != component_id
    ]

def save_dashboard_layout(dashboard_name):
    """Save the current dashboard layout"""
    st.success(f"✅ Dashboard '{dashboard_name}' layout saved!")

def clear_dashboard_layout():
    """Clear the current dashboard layout"""
    st.session_state.dashboard_components = []
    st.success("✅ Dashboard cleared!")

def create_custom_chart(df, numeric_col, cat_col, chart_type, agg_func='mean'):
    """Create custom chart based on type with toggle button"""
    try:
        chart_title = f"{agg_func.title()} {numeric_col} by {cat_col}"
        
        # Add toggle button for custom charts
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### {chart_title}")
        with col2:
            component_data = {
                'chart_type': chart_type,
                'numeric_col': numeric_col,
                'cat_col': cat_col,
                'agg_func': agg_func,
                'title': chart_title
            }
            is_added = get_component_status('chart', component_data)
            
            button_text = "－" if is_added else "＋"
            button_help = "Remove from dashboard" if is_added else "Add to dashboard"
            button_type = "secondary" if is_added else "primary"
            
            button_key = f"toggle_custom_{numeric_col}_{cat_col}"
            if st.button(button_text, key=button_key, help=button_help, type=button_type):
                success, action = add_component_to_dashboard_handler('chart', component_data, chart_title)
                if success:
                    st.success(f"✅ Added {chart_title} to dashboard!")
                else:
                    st.info(f"🗑️ Removed {chart_title} from dashboard")
                st.rerun()
        
        # Rest of the chart creation code
        if chart_type == "Bar Chart":
            chart_data = df.groupby(cat_col)[numeric_col].agg(agg_func).reset_index()
            fig = px.bar(chart_data, x=cat_col, y=numeric_col)
            fig.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
        elif chart_type == "Pie Chart":
            chart_data = df.groupby(cat_col)[numeric_col].agg(agg_func).reset_index()
            fig = px.pie(chart_data, values=numeric_col, names=cat_col)
        elif chart_type == "Box Plot":
            fig = px.box(df, x=cat_col, y=numeric_col)
        elif chart_type == "Violin Plot":
            fig = px.violin(df, x=cat_col, y=numeric_col)
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df, x=cat_col, y=numeric_col)
        elif chart_type == "Line Chart":
            chart_data = df.groupby(cat_col)[numeric_col].agg(agg_func).reset_index()
            fig = px.line(chart_data, x=cat_col, y=numeric_col)
        else:
            st.error("Invalid chart type")
            return
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")

def create_mini_relationship_chart(df, numeric_col, cat_col, key):
    """Create mini relationship chart with toggle button"""
    
    chart_title = f"{numeric_col} by {cat_col}"
    
    # Add toggle button for mini charts
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.write(f"**{chart_title}**")
    
    with col2:
        component_data = {
            'chart_type': 'Bar Chart',
            'numeric_col': numeric_col,
            'cat_col': cat_col,
            'agg_func': 'mean',
            'title': chart_title
        }
        is_added = get_component_status('chart', component_data)
        
        button_text = "－" if is_added else "＋"
        button_help = "Remove from dashboard" if is_added else "Add to dashboard"
        button_type = "secondary" if is_added else "primary"
        
        button_key = f"toggle_mini_{key}"
        if st.button(button_text, key=button_key, help=button_help, type=button_type):
            success, action = add_component_to_dashboard_handler('chart', component_data, chart_title)
            if success:
                st.success(f"✅ Added {chart_title} to dashboard!")
            else:
                st.info(f"🗑️ Removed {chart_title} from dashboard")
            st.rerun()
    
    # Original chart creation code
    grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
    grouped = grouped.nlargest(5, numeric_col)
    
    fig = px.bar(grouped, x=cat_col, y=numeric_col, title=chart_title)
    fig.update_layout(height=250, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key=f"mini_{key}")

def create_correlation_chart(df, col1, col2):
    """Create correlation chart"""
    st.markdown(f'### 🔗 {col1} vs {col2} Relationship')
    
    plot_df = df.sample(min(1000, len(df)))
    
    fig = px.scatter(plot_df, x=col1, y=col2, title=f"{col2} vs {col1}")
    
    correlation = df[col1].corr(df[col2])
    fig.add_annotation(
        text=f"Correlation: {correlation:.2f}",
        xref="paper", yref="paper",
        x=0.05, y=0.95, showarrow=False,
        bgcolor="white", bordercolor="black"
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def create_correlation_matrix(df, numeric_cols):
    """Create correlation matrix"""
    if len(numeric_cols) < 2:
        return
    
    corr_matrix = df[numeric_cols].corr()
    
    fig = px.imshow(corr_matrix, title="Correlation Matrix", color_continuous_scale='RdBu', aspect='auto')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_examples():
    """Show examples when no data is uploaded"""
    st.header("🎯 Universal Dashboard with Data Cleaning!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧹 New: Data Preprocessing")
        st.write("**After uploading, you can:**")
        st.write("- ✅ Remove duplicate rows")
        st.write("- ❌ Handle missing values in multiple ways")
        st.write("- 🔍 See detailed data quality analysis")
        st.write("- 👀 Preview cleaning impact")
        st.write("- ⚙️ Choose custom fill values")
        
        st.subheader("🚗 Example Use Cases:")
        st.write("- **Sales Data**: Analyze revenue by product category")
        st.write("- **Marketing Data**: Measure campaign performance")
        st.write("- **HR Data**: Explore salary distributions")
        st.write("- **Operations**: Track performance metrics")
    
    with col2:
        st.subheader("📊 Analysis Features")
        st.write("**4 Powerful Tabs:**")
        st.write("- 🚀 Auto Insights - Smart automated analysis")
        st.write("- 🔍 Custom Analysis - Full control over relationships")
        st.write("- 📊 All Relationships - Complete exploration matrix")
        st.write("- 📈 Data Summary - Detailed statistics overview")
        
        st.subheader("✨ Advanced Features:")
        st.write("- **Data Sampling** for large datasets")
        st.write("- **Multiple Chart Types** for different insights")
        st.write("- **Export Options** for results sharing")
        st.write("- **Responsive Design** for all devices")
    
    st.divider()
    st.subheader("🔧 Complete Workflow:")
    st.write("1. **📁 Upload CSV/Excel** - Any dataset, any domain")
    st.write("2. **🧹 Clean Data** - Handle duplicates and missing values")
    st.write("3. **🎯 Smart Analysis** - Automatic insights generation")
    st.write("4. **🔍 Custom Exploration** - Full control over analysis")
    st.write("5. **📊 Professional Results** - Clean, accurate dashboard")
    st.write("6. **💾 Export Options** - Download results and charts")
    
    st.info("**Upload your data or try a sample to experience the complete data-to-dashboard workflow! 🚀**")

def main():
    """Main application function"""
    initialize_session_state()

    if not st.session_state.file_uploaded:
        st.title("📊 Auto BI Dashboard")
        st.subheader("Upload, Clean, Analyze - All in One Place!")
        
        with st.sidebar:
            st.header("📁 Data Upload")
            uploaded_file = st.file_uploader(
                "Drag and drop file here",
                type=['csv', 'xlsx', 'xls'],
                help="Limit 200MB per file - CSV, XLSX, XLS"
            )
            
            if uploaded_file is not None:
                # Handle file upload and force UI update
                df = handle_file_upload(uploaded_file)
                if df is not None:
                    st.rerun()  # Force refresh to show preprocessing interface
            
            st.divider()
            st.header("📋 About")
            st.write("This Auto BI Dashboard automatically:")
            st.write("- Analyzes your data structure")
            st.write("- Cleans and preprocesses data")
            st.write("- Generates smart insights")
            st.write("- Creates interactive visualizations")
        
        # Only show examples if no file has been uploaded yet
        if not st.session_state.file_uploaded:
            show_examples()
    else:
        # File is uploaded, show the main dashboard interface
        dataset_name = st.session_state.get('uploaded_file_name', 'Dataset')
        formatted_name = re.sub(r'\s*\(\d+\)$', '', dataset_name)
        formatted_name = formatted_name.rsplit('.', 1)[0].replace('_', ' ').title()

        st.markdown(
            f"""
            <h2 style="
                color:#2980b9;
                background:#e8f4fc;
                padding:10px 15px;
                border-left:5px solid #3498db;
                border-radius:6px;
            ">
             {formatted_name} Dashboard
            </h2>
            """,
            unsafe_allow_html=True
        )
        
        if not st.session_state.preprocessing_done:
            show_data_preprocessing()
        else:
            create_smart_dashboard(st.session_state.processed_df)

if __name__ == "__main__":
    main()
