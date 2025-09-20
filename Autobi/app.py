import warnings
warnings.filterwarnings("ignore", message="Thread 'MainThread': missing ScriptRunContext!")
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from auto_bi_backend import *
import time
from io import StringIO
import plotly.io as pio
from io import BytesIO
from auto_bi_backend import generate_ai_insights
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import requests
import os
# Page configuration
st.set_page_config(
    page_title="Auto BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS for visibility
# Add to your existing CSS in app.py
st.markdown("""
<style>
/* Report-specific styling */
.report-section {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #3498db;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.1);
}

.report-header {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
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
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* ========== GLOBAL STYLES ========== */
.stApp {
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}

/* ========== INSIGHTS BOX ========== */
.insight-card {
    background: #f8f9fa;
    border-left: 4px solid #3498db;
    border-radius: 8px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.1);
    font-weight: 500;
    font-size: 1.1rem;
    color: #2c3e50;
    line-height: 1.5;
}

/* ========== KPI STYLING ========== */
.kpi-container {
    background: white;
    border-radius: 8px;
    padding: 1.2rem;
    text-align: center;
    margin-bottom: 1rem;
    border: 1px solid #e3e8ee;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.1);
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

/* ========== BUTTONS ========== */
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

/* ========== TOGGLE STYLING ========== */
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

.stToggle label p {
    color: white;
}

.stToggle input:checked + div {
    background-color: #3396D3;
}

/* ========== CARD STYLING ========== */
.card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #e3e8ee;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.1);
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'original_df': None,
        'processed_df': None,
        'preprocessing_done': False,
        'analysis': None,
        'file_uploaded': False,
        'processing_stats': {},
        'current_tab': "🚀 Auto Insights",
        'chart_config': {},
        'data_sample_size': 10000
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
            return
            
        # Reset session state when new file is uploaded
        st.session_state.original_df = df.copy()
        

        st.session_state.processed_df = df.copy()
        st.session_state.preprocessing_done = False
        st.session_state.file_uploaded = True
        st.session_state.analysis = analyze_columns(df)
        st.success("File uploaded successfully!")
        
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        st.info("Please make sure your file is properly formatted and try again.")

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
            value=True
        )

    custom_fill_values = {}  # Initialize here to always be defined

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
            index=1
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
                        # Convert to float if numeric string, else keep as string
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
    
    # Get data quality stats from backend
    stats = get_data_quality_stats(df)
    
    # Basic stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Rows", f"{stats['total_rows']:,}")
    with col2:
        st.metric("📊 Total Columns", stats['total_cols'])
    with col3:
        color = "red" if stats['duplicate_rows'] > 0 else "green"
        st.metric("🔄 Duplicate Rows", stats['duplicate_rows'])
    with col4:
        color = "red" if stats['missing_values'] > 0 else "green"
        st.metric("❌ Missing Values", f"{stats['missing_values']:,}")
    
    # Detailed analysis
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
            # Show missing values by column
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
    
    # Show detailed missing values in expander
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
    """Create the main dashboard with processed data"""
    if st.session_state.analysis is None:
        st.session_state.analysis = analyze_columns(df)
    
    analysis = st.session_state.analysis
    
    # Show processing summary in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Processed Data")
        st.metric("Clean Rows", f"{len(df):,}")
        st.metric("Clean Columns", len(df.columns))
        
        if 'processing_stats' in st.session_state and st.session_state.processing_stats:
            stats = st.session_state.processing_stats
            with st.expander("📈 Processing Statistics"):
                st.write(f"Original rows: {stats.get('original_rows', 'N/A')}")
                st.write(f"Duplicates removed: {stats.get('duplicates_removed', 'N/A')}")
                st.write(f"Null rows removed: {stats.get('null_rows_removed', 'N/A')}")
                st.write(f"Null values filled: {stats.get('null_values_filled', 'N/A')}")
                st.write(f"Final rows: {stats.get('final_rows', 'N/A')}")
        
        if st.button("🔄 Reset & Reprocess", use_container_width=True):
            st.session_state.preprocessing_done = False
            st.rerun()
            
        # Add export options
        st.markdown("---")
        st.markdown("### 💾 Export Options")
        if st.button("📥 Download Processed Data", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Dashboard header
    st.markdown("#### Data Overview")
    
    # Data overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Clean Records", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Numeric", len(analysis['numeric_cols']))
    with col4:
        st.metric("Categories", len(analysis['suitable_for_grouping']))
    
    # Create tabs for different analysis types
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Dashboard", "🔍 Custom Analysis", "📊 All Relationships", "📈 Data Summary"])
    
    # Store current tab in session state
    if tab1:
        st.session_state.current_tab = "🚀 Dashboard"
    elif tab2:
        st.session_state.current_tab = "🔍 Custom Analysis"
    elif tab3:
        st.session_state.current_tab = "📊 All Relationships"
    elif tab4:
        st.session_state.current_tab = "📈 Data Summary"
    
    with tab1:
        create_auto_insights_tab(df, analysis)
    
    with tab2:
        create_custom_analysis_tab(df, analysis)
    
    with tab3:
        create_relationship_explorer(df, analysis)
    
    with tab4:
        create_data_summary_tab(df, analysis)

def create_auto_insights_tab(df, analysis):
    """Create auto insights tab"""
    # st.markdown("### 🚀 Automatic Insights")
    # st.markdown("*Smart analysis based on your clean data patterns*")
    
    # Auto-generated KPIs
    create_smart_kpis(df, analysis)
    
    # Auto-generated charts
    if analysis['numeric_cols'] and analysis['suitable_for_grouping']:
        st.markdown("##### Key Relationships")
        
        # Create up to 4 automatic insights
        insights_created = 0
        
        for i, numeric_col in enumerate(analysis['numeric_cols'][:2]):
            for j, cat_col in enumerate(analysis['suitable_for_grouping'][:2]):
                if insights_created >= 4:
                    break
                    
                if insights_created % 2 == 0:
                    col1, col2 = st.columns(2)
                
                with col1 if insights_created % 2 == 0 else col2:
                    create_relationship_chart(df, numeric_col, cat_col, f"auto_{insights_created}")
                
                insights_created += 1
        
        # # Auto insights text
        # insights = generate_auto_insights(df, analysis)
        # for insight in insights:
        #     st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ Need both numeric and categorical columns for relationship analysis")
        if analysis['numeric_cols']:
            show_numeric_distributions(df, analysis['numeric_cols'][:4])
        elif analysis['suitable_for_grouping']:
            show_category_distributions(df, analysis['suitable_for_grouping'][:4])

def create_custom_analysis_tab(df, analysis):
    """Create custom analysis tab"""
    st.markdown("### 🔍 Custom Relationship Explorer")
    st.markdown("*Choose any columns to explore their relationships*")
    
    # User controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Select numeric column for analysis
        if analysis['numeric_cols']:
            selected_numeric = st.selectbox(
                "📊 Choose Numeric Column (What to measure)",
                options=analysis['numeric_cols'],
                help="Select the numeric value you want to analyze",
                key="custom_numeric"
            )
        else:
            selected_numeric = None
            st.warning("No numeric columns available")
    
    with col2:
        # Select categorical column for grouping  
        if analysis['suitable_for_grouping']:
            selected_category = st.selectbox(
                "🏷️ Choose Category Column (How to group)",
                options=analysis['suitable_for_grouping'],
                help="Select how you want to break down the data",
                key="custom_category"
            )
        else:
            selected_category = None
            st.warning("No suitable category columns available")
    
    with col3:
        # Select chart type
        chart_type = st.selectbox(
            "📈 Choose Chart Type",
            options=["Bar Chart", "Pie Chart", "Box Plot", "Violin Plot", "Scatter Plot", "Line Chart"],
            help="Select how you want to visualize the relationship",
            key="custom_chart_type"
        )
        
        # Additional options based on chart type
        if chart_type in ["Bar Chart", "Pie Chart"]:
            agg_func = st.selectbox(
                "Aggregation Function",
                options=["mean", "sum", "count"],
                help="How to aggregate the numeric values",
                key="custom_agg_func"
            )
        else:
            agg_func = "mean"
    
    # Generate custom chart
    if selected_numeric and selected_category:
        st.markdown("### 📊 Your Custom Analysis")
        create_custom_chart(df, selected_numeric, selected_category, chart_type, agg_func)
        
        # Show insights for this specific relationship
        insights = generate_insights(df, selected_numeric, selected_category, agg_func)

        for insight in insights:
            st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)
    
    # Additional analysis options
    if len(analysis['numeric_cols']) >= 2:
        st.markdown("### 🔗 Numeric Relationships")
        col1, col2 = st.columns(2)
        
        with col1:
            num_col1 = st.selectbox("X-axis", analysis['numeric_cols'], key="custom_x")
        with col2:
            num_col2 = st.selectbox("Y-axis", analysis['numeric_cols'], key="custom_y", index=1)
        
        if num_col1 != num_col2:
            create_correlation_chart(df, num_col1, num_col2)

def create_relationship_explorer(df, analysis):
    """Create relationship explorer tab"""
    st.markdown("### 📊 Complete Relationship Matrix")
    st.markdown("*Explore ALL possible relationships in your clean data*")
    
    if analysis['numeric_cols'] and analysis['suitable_for_grouping']:
        
        # Show all combinations
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
        
        # Correlation matrix for numeric columns
        if len(analysis['numeric_cols']) >= 2:
            st.markdown("#### 🔗 Numeric Correlations")
            create_correlation_matrix(df, analysis['numeric_cols'])
    
    else:
        st.info("Upload data with both numeric and categorical columns to see relationships")
def create_data_summary_tab(df, analysis):
    """Show AI insights with proper error handling + PDF download"""
    status_ok, status_msg = validate_ollama_connection()
    if status_ok:
        st.success(f"✅ {status_msg}")
    else:
        st.error(f"❌ {status_msg}")
        st.info("💡 Make sure Ollama is running and you've downloaded a model with: `ollama pull phi3:mini`")

    st.markdown("### 🤖 AI Data Insights (Ollama)")

    # Fetch available models
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
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

    # Generate insights button
    if st.button("✨ Generate AI Insights",
                 key="generate_insights",
                 use_container_width=True,
                 type="primary"):

        with st.spinner("🔍 Analyzing your data with AI..."):
            try:
                selected_model = st.session_state.get("selected_model", "phi3:mini")
                insights = generate_ai_insights(df, analysis, model_name=selected_model)
                st.session_state.ai_insights = insights
                st.session_state.insights_source = "Ollama AI"
                st.success("✅ AI insights generated successfully!")
            except Exception as e:
                error_msg = f"❌ Failed to generate AI insights: {str(e)}"
                st.error(error_msg)
                st.session_state.ai_error = error_msg
                if 'ai_insights' in st.session_state:
                    del st.session_state.ai_insights

    # Show error message if exists
    if 'ai_error' in st.session_state:
        st.error(st.session_state.ai_error)

    # Clear / retry buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Insights", use_container_width=True):
            for k in ('ai_insights', 'ai_error'):
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
    with col2:
        if st.button("🔄 Retry Connection", use_container_width=True):
            if 'ai_error' in st.session_state:
                del st.session_state.ai_error
            st.rerun()

    # Display insights if available
    if 'ai_insights' in st.session_state:
        st.markdown("---")
        st.markdown(f"<h4 style='color:green;'>🔍 AI-Generated Insights</h4>", unsafe_allow_html=True)

        # Show formatted insights
        st.markdown(st.session_state.ai_insights)

        # Download options (Markdown + PDF)
        st.download_button(
            label="📥 Download Insights (Markdown)",
            data=st.session_state.ai_insights,
            file_name="ai_insights.md",
            mime="text/markdown",
            use_container_width=True
        )

        # PDF download
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer)
        styles = getSampleStyleSheet()
        story = [Paragraph("<b>AI Data Insights</b>", styles['Title'])]
        for line in st.session_state.ai_insights.split("\n"):
            if line.strip():
                story.append(Paragraph(line, styles['Normal']))
        doc.build(story)
        st.download_button(
            label="📥 Download Insights as PDF",
            data=pdf_buffer.getvalue(),
            file_name="ai_insights.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # Always show dataset summary
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

def create_smart_kpis(df, analysis):
    """Create smart KPIs"""
    
    
    cols = st.columns(4)
    
    # Always show total records
    with cols[0]:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value">{len(df):,}</div>
            <div class="kpi-label">Total Records</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Smart KPIs for numeric columns
    for i, col in enumerate(analysis['numeric_cols'][:3]):
        with cols[i + 1]:
            avg_val = df[col].mean()
            
            # Smart formatting
            if avg_val >= 1000000:
                display_val = f"{avg_val/1000000:.1f}M"
                label = f"Avg {col.replace('_', ' ').title()}"
            elif avg_val >= 1000:
                display_val = f"{avg_val/1000:.0f}K"
                label = f"Avg {col.replace('_', ' ').title()}"
            else:
                display_val = f"{avg_val:.1f}"
                label = f"Avg {col.replace('_', ' ').title()}"
            
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-value">{display_val}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def create_relationship_chart(df, numeric_col, cat_col, key):
    """Create relationship chart"""
    st.markdown(f'### 📊 {numeric_col.replace("_", " ").title()} by {cat_col.replace("_", " ").title()}')
    
    # Group and calculate averages
    grouped = df.groupby(cat_col)[numeric_col].agg(['mean', 'count']).reset_index()
    grouped.columns = [cat_col, 'average', 'count']
    
    # Sort by average and take top 10
    grouped = grouped.nlargest(10, 'average')
    
    fig = px.bar(grouped, 
                x=cat_col, 
                y='average',
                color='average',
                color_continuous_scale='viridis',
                title=f"Average {numeric_col} by {cat_col}")
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key=key)

def create_custom_chart(df, numeric_col, cat_col, chart_type, agg_func='mean'):
    """Create custom chart based on type"""
    try:
        if chart_type == "Bar Chart":
            chart_data = df.groupby(cat_col)[numeric_col].agg(agg_func).reset_index()
            fig = px.bar(chart_data, x=cat_col, y=numeric_col, 
                        title=f"{agg_func.title()} {numeric_col} by {cat_col}")
            # Adjust layout for long labels
            fig.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
        elif chart_type == "Pie Chart":
            chart_data = df.groupby(cat_col)[numeric_col].agg(agg_func).reset_index()
            fig = px.pie(chart_data, values=numeric_col, names=cat_col,
                        title=f"{agg_func.title()} {numeric_col} by {cat_col}")
        elif chart_type == "Box Plot":
            fig = px.box(df, x=cat_col, y=numeric_col,
                        title=f"Distribution of {numeric_col} by {cat_col}")
        elif chart_type == "Violin Plot":
            fig = px.violin(df, x=cat_col, y=numeric_col,
                        title=f"Distribution of {numeric_col} by {cat_col}")
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df, x=cat_col, y=numeric_col,
                            title=f"{numeric_col} by {cat_col}")
        elif chart_type == "Line Chart":
            chart_data = df.groupby(cat_col)[numeric_col].agg(agg_func).reset_index()
            fig = px.line(chart_data, x=cat_col, y=numeric_col,
                        title=f"{agg_func.title()} {numeric_col} by {cat_col}")
        else:
            st.error("Invalid chart type")
            return
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add chart download button with error handling
        try:
            buf = BytesIO()
            pio.write_image(fig, buf, format="png", engine="kaleido")
            st.download_button(
                label="Download Chart as PNG",
                data=buf.getvalue(),
                file_name=f"{chart_type}_{numeric_col}_by_{cat_col}.png",
                mime="image/png",
                key=f"download_{chart_type}_{numeric_col}_{cat_col}"
            )
        except Exception as e:
            st.warning("Chart download is not available. Please install kaleido with: pip install kaleido")
        
        # Add chart configuration options
        with st.expander("⚙️ Chart Options"):
            col1, col2 = st.columns(2)
            with col1:
                show_data = st.checkbox("Show Data Table", value=False, key=f"show_data_{chart_type}_{numeric_col}_{cat_col}")
            with col2:
                # Additional options can be added here
                pass
                
            if show_data:
                if chart_type in ["Bar Chart", "Pie Chart", "Line Chart"]:
                    st.dataframe(chart_data, use_container_width=True)
                else:
                    st.dataframe(df[[cat_col, numeric_col]], use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")

def create_mini_relationship_chart(df, numeric_col, cat_col, key):
    """Create mini relationship chart"""
    # Create smaller version for the matrix view
    grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
    grouped = grouped.nlargest(5, numeric_col)
    
    fig = px.bar(grouped, x=cat_col, y=numeric_col,
                title=f"{numeric_col} by {cat_col}")
    fig.update_layout(height=250, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key=f"mini_{key}")

def create_correlation_chart(df, col1, col2):
    """Create correlation chart"""
    st.markdown(f'### 🔗 {col1} vs {col2} Relationship')
    
    # Sample data if too large
    plot_df = df.sample(min(1000, len(df)))
    
    fig = px.scatter(plot_df, x=col1, y=col2,
                    title=f"{col2} vs {col1}")
    
    # Add correlation coefficient
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
    
    fig = px.imshow(corr_matrix,
                    title="Correlation Matrix",
                    color_continuous_scale='RdBu',
                    aspect='auto')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_numeric_distributions(df, cols):
    """Show numeric distributions"""
    st.markdown("### 📊 Numeric Distributions")
    cols_layout = st.columns(min(4, len(cols)))
    
    for i, col in enumerate(cols):
        with cols_layout[i % len(cols_layout)]:
            fig = px.histogram(df, x=col, title=f"{col} Distribution")
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

def show_category_distributions(df, cols):
    """Show category distributions"""
    st.markdown("### 🏷️ Category Distributions")
    cols_layout = st.columns(min(4, len(cols)))
    
    for i, col in enumerate(cols):
        with cols_layout[i % len(cols_layout)]:
            counts = df[col].value_counts().head(10)
            fig = px.bar(x=counts.index, y=counts.values, title=f"{col} Distribution")
            fig.update_layout(height=250)
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

    # Sidebar - file upload
    with st.sidebar:
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Drag and drop file here",
            type=['csv', 'xlsx', 'xls'],
            help="Limit 200MB per file - CSV, XLSX, XLS"
        )
        
        if uploaded_file is not None:
            # Only reload if new file
            if not st.session_state.file_uploaded or uploaded_file.name != st.session_state.get('uploaded_file_name', ''):
                handle_file_upload(uploaded_file)
                st.session_state.uploaded_file_name = uploaded_file.name
        
        st.divider()
        st.header("📋 About")
        st.write("This Auto BI Dashboard automatically:")
        st.write("- Analyzes your data structure")
        st.write("- Cleans and preprocesses data")
        st.write("- Generates smart insights")
        st.write("- Creates interactive visualizations")

    # 🟢 Header logic:
    if not st.session_state.file_uploaded:
        st.title("📊 Auto BI Dashboard")
        st.subheader("Upload, Clean, Analyze - All in One Place!")
    else:
        
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


        

    # 🟢 Main content area:
    if st.session_state.file_uploaded:
        if not st.session_state.preprocessing_done:
            show_data_preprocessing()
        else:
            create_smart_dashboard(st.session_state.processed_df)
    else:
        show_examples()


if __name__ == "__main__":
    main()