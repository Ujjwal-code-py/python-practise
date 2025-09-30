import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import logging
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables (add this after imports)


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_columns(df):
    """Smart column analysis that works for ANY dataset"""
    if df.empty:
        logger.warning("DataFrame is empty")
        return {
            'numeric_cols': [],
            'categorical_cols': [],
            'suitable_for_grouping': [],
            'high_cardinality': [],
            'potential_metrics': [],
            'potential_dimensions': [],
            'datetime_cols': [],
            'boolean_cols': []
        }
    
    analysis = {
        'numeric_cols': [],
        'categorical_cols': [],
        'suitable_for_grouping': [],
        'high_cardinality': [],
        'potential_metrics': [],
        'potential_dimensions': [],
        'datetime_cols': [],
        'boolean_cols': []
    }
    
    for col in df.columns:
        col_type = df[col].dtype
        
        # Check for datetime columns
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            analysis['datetime_cols'].append(col)
            analysis['potential_dimensions'].append(col)
            continue
            
        # Check for boolean columns
        if col_type == 'bool' or df[col].nunique() == 2:
            analysis['boolean_cols'].append(col)
            analysis['suitable_for_grouping'].append(col)
            analysis['potential_dimensions'].append(col)
            continue
            
        # Numeric columns
        if col_type in ['int64', 'float64', 'int32', 'float32']:
            analysis['numeric_cols'].append(col)
            analysis['potential_metrics'].append(col)
        # Categorical columns
        else:
            analysis['categorical_cols'].append(col)
            unique_count = df[col].nunique()
            total_rows = len(df)
            
            if 2 <= unique_count <= 50 and unique_count < total_rows * 0.5:
                analysis['suitable_for_grouping'].append(col)
                analysis['potential_dimensions'].append(col)
            else:
                analysis['high_cardinality'].append(col)
    
    return analysis

def process_data(df, remove_duplicates=True, null_handling="Remove Rows with Missing Values",
                 custom_fill_values=None, drop_columns=None):
    """Process the data based on user selections"""

    if df.empty:
        logger.warning("Attempted to process empty DataFrame")
        return df.copy(), {}

    processed_df = df.copy()
    processing_stats = {
        'original_rows': len(processed_df),
        'duplicates_removed': 0,
        'null_rows_removed': 0,
        'null_values_filled': 0,
        'columns_dropped': 0
    }

    # Drop columns if requested
    if drop_columns:
        columns_to_drop = [col for col in drop_columns if col in processed_df.columns]
        processed_df = processed_df.drop(columns=columns_to_drop)
        processing_stats['columns_dropped'] = len(columns_to_drop)

    # Remove duplicates
    if remove_duplicates:
        duplicate_count = processed_df.duplicated().sum()
        processed_df = processed_df.drop_duplicates()
        processing_stats['duplicates_removed'] = duplicate_count

    # Handle missing values
    if null_handling == "Remove Rows with Missing Values":
        null_rows = processed_df.isnull().any(axis=1).sum()
        processed_df = processed_df.dropna()
        processing_stats['null_rows_removed'] = null_rows

    elif null_handling == "Fill with Average (Mean) – the usual value":
        numeric_cols = processed_df.select_dtypes(include=[np.number]).columns
        null_counts = processed_df[numeric_cols].isnull().sum().sum()
        processed_df[numeric_cols] = processed_df[numeric_cols].fillna(processed_df[numeric_cols].mean())
        processing_stats['null_values_filled'] = null_counts

    elif null_handling == "Fill with Middle Value (Median)":
        numeric_cols = processed_df.select_dtypes(include=[np.number]).columns
        null_counts = processed_df[numeric_cols].isnull().sum().sum()
        processed_df[numeric_cols] = processed_df[numeric_cols].fillna(processed_df[numeric_cols].median())
        processing_stats['null_values_filled'] = null_counts

    elif null_handling == "Fill with Most Common Value (Mode)":
        for col in processed_df.columns:
            null_count = processed_df[col].isnull().sum()
            mode_val = processed_df[col].mode()
            if not mode_val.empty:
                processed_df[col] = processed_df[col].fillna(mode_val[0])
            processing_stats['null_values_filled'] += null_count

    elif null_handling == "Custom Fill Values" and custom_fill_values:
        for col, value in custom_fill_values.items():
            if col in processed_df.columns:
                null_count = processed_df[col].isnull().sum()
                processed_df[col] = processed_df[col].fillna(value)
                processing_stats['null_values_filled'] += null_count

    processing_stats['final_rows'] = len(processed_df)
    logger.info(f"Data processing completed. Stats: {processing_stats}")
    return processed_df, processing_stats


def get_data_quality_stats(df):
    """Get data quality statistics"""
    if df.empty:
        return {
            'total_rows': 0,
            'total_cols': 0,
            'duplicate_rows': 0,
            'missing_values': 0,
            'completeness_percentage': 0
        }
    
    total_cells = df.size
    missing_values = df.isnull().sum().sum()
    completeness = ((total_cells - missing_values) / total_cells * 100) if total_cells > 0 else 0
    
    return {
        'total_rows': len(df),
        'total_cols': len(df.columns),
        'duplicate_rows': df.duplicated().sum(),
        'missing_values': missing_values,
        'completeness_percentage': round(completeness, 2)
    }

def get_preview_data(df, remove_duplicates=False, null_handling=None):
    """Get preview of data after processing"""
    if df.empty:
        return df
    
    preview_df = df.copy()

    if remove_duplicates:
        preview_df = preview_df.drop_duplicates()

    if null_handling == "Remove Rows with Missing Values":
        preview_df = preview_df.dropna()
    elif null_handling == "Fill with Average (Mean) – the usual value":
        numeric_cols = preview_df.select_dtypes(include=[np.number]).columns
        preview_df[numeric_cols] = preview_df[numeric_cols].fillna(preview_df[numeric_cols].mean())
    elif null_handling == "Fill with Middle Value (Median)":
        numeric_cols = preview_df.select_dtypes(include=[np.number]).columns
        preview_df[numeric_cols] = preview_df[numeric_cols].fillna(preview_df[numeric_cols].median())
    elif null_handling == "Fill with Most Common Value (Mode)":
        for col in preview_df.columns:
            mode_val = preview_df[col].mode()
            if not mode_val.empty:
                preview_df[col] = preview_df[col].fillna(mode_val[0])

    return preview_df.head()

def generate_insights(df, numeric_col, cat_col, aggfunc='mean'):
    if df.empty or numeric_col not in df.columns or cat_col not in df.columns:
        return ["⚠️ Cannot generate insights: Required columns not found or DataFrame is empty"]
    
    try:
        overall_agg = getattr(df[numeric_col], aggfunc)()  # e.g. mean(), sum()
        grouped = df.groupby(cat_col)[numeric_col].agg([aggfunc, 'count', 'std', 'min', 'max']).round(2)
        grouped.columns = ['AggregatedValue', 'Count', 'Std Dev', 'Minimum', 'Maximum']
        
        best = grouped['AggregatedValue'].idxmax()
        best_value = grouped['AggregatedValue'].max()
        worst = grouped['AggregatedValue'].idxmin()
        worst_value = grouped['AggregatedValue'].min()
        
        most_common = grouped['Count'].idxmax()
        most_common_count = grouped['Count'].max()
        
        cv = (grouped['Std Dev'] / grouped['AggregatedValue']).mean() * 100  # Coefficient of variation
        
        insights = [
            f"Highest {aggfunc.title()}: '{best}' has the highest {aggfunc} {numeric_col.replace('_', ' ')} at {best_value}",
            f"Lowest {aggfunc.title()}: '{worst}' has the lowest {aggfunc} {numeric_col.replace('_', ' ')} at {worst_value}",
            f"Most Frequent: '{most_common}' appears {most_common_count} times in the data",
            f"Range: {numeric_col.replace('_', ' ')} varies from {df[numeric_col].min()} to {df[numeric_col].max()}",
            f"Variability: Average coefficient of variation is {cv:.2f}% across categories"
        ]
        return insights
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return [f"❌ Error generating insights: {str(e)}"]

        
     

def generate_auto_insights(df, analysis=None):
    """Generate automatic insights for the dataset"""
    if df.empty:
        return ["⚠️ Dataset is empty - no insights available"]
    
    insights = []
    
    # If no analysis provided, perform it
    if analysis is None:
        analysis = analyze_columns(df)
    
    # Overall dataset insights
    quality_stats = get_data_quality_stats(df)
    insights.append(f"Dataset contains {len(df):,} records across {len(df.columns)} columns")
    
    if quality_stats['completeness_percentage'] < 100:
        insights.append(f"⚠️ Data completeness: {quality_stats['completeness_percentage']}% ({quality_stats['missing_values']} missing values)")
    
    if quality_stats['duplicate_rows'] > 0:
        insights.append(f"⚠️ Found {quality_stats['duplicate_rows']} duplicate rows")
    
    # Top insights from each numeric column
    for col in analysis['numeric_cols'][:3]:  # Limit to top 3 numeric columns
        try:
            avg_val = df[col].mean()
            max_val = df[col].max()
            min_val = df[col].min()
            median_val = df[col].median()
            insights.append(f"📈 {col.replace('_', ' ').title()}: Avg {avg_val:.2f}, Med {median_val:.2f}, Range {min_val:.2f}-{max_val:.2f}")
        except:
            continue
    
    # Category insights
    for col in analysis['suitable_for_grouping'][:2]:  # Limit to top 2 categorical columns
        try:
            value_counts = df[col].value_counts()
            top_cat = value_counts.index[0]
            top_count = value_counts.iloc[0]
            percentage = (top_count / len(df)) * 100
            unique_count = len(value_counts)
            insights.append(f"{col.replace('_', ' ').title()}: {unique_count} unique values, '{top_cat}' is most common ({percentage:.1f}%)")
        except:
            continue
    
    # Relationship insights
    if analysis['numeric_cols'] and analysis['suitable_for_grouping']:
        try:
            num_col = analysis['numeric_cols'][0]
            cat_col = analysis['suitable_for_grouping'][0]
            
            grouped = df.groupby(cat_col)[num_col].mean()
            top_performer = grouped.idxmax()
            top_value = grouped.max()
            bottom_performer = grouped.idxmin()
            bottom_value = grouped.min()
            
            insights.append(f"Performance: '{top_performer}' has highest {num_col.replace('_', ' ')} ({top_value:.2f})")
            insights.append(f"Performance: '{bottom_performer}' has lowest {num_col.replace('_', ' ')} ({bottom_value:.2f})")
        except:
            pass
    
    return insights

def create_chart_data(df, numeric_col, cat_col, chart_type, agg_func='mean'):
    """Prepare data for different chart types"""
    if df.empty or numeric_col not in df.columns:
        return None, None, "Error: Numeric column not found"
        
    if chart_type != "Distribution Plot" and cat_col not in df.columns:
        return None, None, "Error: Category column not found"
    
    try:
        if chart_type == "Bar Chart":
            if agg_func == 'mean':
                grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
            elif agg_func == 'sum':
                grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
            elif agg_func == 'count':
                grouped = df.groupby(cat_col)[numeric_col].count().reset_index()
            grouped.columns = [cat_col, numeric_col]
            return grouped, "bar", None
            
        elif chart_type == "Pie Chart":
            if agg_func == 'sum':
                grouped = df.groupby(cat_col)[numeric_col].sum().reset_index()
            elif agg_func == 'count':
                grouped = df[cat_col].value_counts().reset_index()
                grouped.columns = [cat_col, 'count']
                numeric_col = 'count'
            else:  # default to mean
                grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
            return grouped, "pie", None
            
        elif chart_type == "Box Plot":
            return df, "box", None
            
        elif chart_type == "Violin Plot":
            return df, "violin", None
            
        elif chart_type == "Scatter Plot":
            # For scatter plot, we need two numeric columns
            if cat_col in df.select_dtypes(include=[np.number]).columns:
                # If category column is numeric, use it for y-axis
                return df, "scatter", None
            else:
                return None, None, "Scatter plot requires two numeric columns"
                
        elif chart_type == "Line Chart":
            grouped = df.groupby(cat_col)[numeric_col].mean().reset_index()
            return grouped, "line", None
            
        elif chart_type == "Distribution Plot":
            # For distribution plot, we only need the numeric column
            return df, "distribution", None
            
        elif chart_type == "Heatmap":
            # For heatmap, we need to create a correlation matrix or pivot table
            if len(df.select_dtypes(include=[np.number]).columns) > 1:
                corr_matrix = df.select_dtypes(include=[np.number]).corr()
                return corr_matrix, "heatmap", None
            else:
                return None, None, "Heatmap requires multiple numeric columns"
                
    except Exception as e:
        logger.error(f"Error creating chart data: {str(e)}")
        return None, None, f"Error: {str(e)}"
    
    return None, None, "Unsupported chart type"
# Add these imports at the top
import requests
import json

# def generate_ollama_insights(df, analysis):
#     """Generate insights using Ollama"""
#     try:
#         # Prepare dataset summary
#         dataset_info = f"""
#         Dataset Analysis Request:
#         - Rows: {len(df)}
#         - Columns: {len(df.columns)}
#         - Column Names: {', '.join(df.columns.tolist())}
#         - Numeric Columns: {', '.join(analysis.get('numeric_cols', []))}
#         - Categorical Columns: {', '.join(analysis.get('suitable_for_grouping', []))}
#         - Sample Data: {df.head(2).to_dict()}
#         """
        
#         # Create prompt for the model
#         prompt = f"""You are a data analyst assistant. Analyze this dataset and provide 5-7 concise, actionable insights.
#         Focus on patterns, relationships, and business implications. Keep it under 300 words.

#         Dataset Information:
#         {dataset_info}

#         Key Insights:"""
        
#         # Make request to Ollama
#         response = requests.post(
#             "http://localhost:11434/api/generate",
#             json={
#                 "model": "llama2",  # Change to your preferred model
#                 "prompt": prompt,
#                 "stream": False,
#                 "options": {
#                     "temperature": 0.3,
#                     "top_p": 0.9,
#                     "num_predict": 500
#                 }
#             },
#             timeout=30  # 30 second timeout
#         )
        
#         if response.status_code == 200:
#             result = response.json()
#             insights = result.get("response", "").strip()
#             return insights if insights else generate_local_insights(df, analysis)
#         else:
#             logger.warning(f"Ollama API error: {response.status_code}")
#             return generate_local_insights(df, analysis)
            
#     except requests.exceptions.ConnectionError:
#         logger.warning("Ollama not running. Please start Ollama with: ollama serve")
#         return generate_local_insights(df, analysis)
#     except Exception as e:
#         logger.error(f"Ollama error: {str(e)}")
#         return generate_local_insights(df, analysis)

# # Update the main AI insights function
# def generate_ai_insights(df, analysis):
#     """
#     Generate AI insights using Ollama
#     """
#     # Check if we should use Ollama
#     use_ollama = os.getenv('USE_OLLAMA', 'false').lower() == 'true'
    
#     if use_ollama:
#         return generate_ollama_insights(df, analysis)
#     else:
#         # Fall back to DeepSeek or local insights
#         api_key = os.getenv('DEEPSEEK_API_KEY')
#         if api_key and api_key != "your_actual_deepseek_api_key_here":
#             # Your existing DeepSeek code here
#             pass
#         return generate_local_insights(df, analysis)

def generate_ollama_insights(df, analysis, model_name="phi3:mini"):
    """Generate insights using Ollama – model selectable"""
    try:
        # Prepare dataset summary
        dataset_info = f"""
        Dataset Analysis Request:
        - Rows: {len(df)}
        - Columns: {len(df.columns)}
        - Column Names: {', '.join(df.columns.tolist())}
        - Numeric Columns: {', '.join(analysis.get('numeric_cols', []))}
        - Categorical Columns: {', '.join(analysis.get('suitable_for_grouping', []))}
        - Sample Data: {df.head(2).to_dict()}
        """

        # Create prompt for the model
        prompt = f"""You are a data analyst assistant. Analyze this dataset and provide concise, actionable insights.
        Focus on patterns, relationships, and business implications. Keep it under 300 words.

        Dataset Information:
        {dataset_info}

        Key Insights:"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,      # <— dynamic model
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            },
            timeout=300
        )
        if response.status_code == 200:
            result = response.json()
            insights = result.get("response", "").strip()
            if insights:
                return insights
            else:
                raise Exception("Ollama returned empty response")
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise Exception("Ollama not running. Please start Ollama with: ollama serve")
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")


def generate_ai_insights(df, analysis, model_name="phi3:mini"):
    """
    Generate AI insights using Ollama – with local fallback
    """
    try:
        return generate_ollama_insights(df, analysis, model_name)
    except Exception as e:
        logger.warning(f"Falling back to local insights: {e}")
        return "Error with Ollama: " + str(e) + "\n\n" + generate_local_insights(df, analysis)

def validate_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if not models:
                return False, "Ollama running but no models found. Run: ollama pull phi3:mini"
            return True, "Ollama connected with models: " + ", ".join([m['name'] for m in models])
        return False, f"Ollama API error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Ollama not running. Start with: ollama serve"
    except Exception as e:
        return False, f"Ollama connection error: {str(e)}"


def generate_local_insights(df, analysis):
    """Generate insights without API - always works"""
    insights = []
    
    insights.append("## Data Insights")
    insights.append("")
    
    # Basic dataset info
    insights.append("### 📊 Dataset Overview")
    insights.append(f"- **Total Records:** {len(df):,}")
    insights.append(f"- **Total Columns:** {len(df.columns)}")
    insights.append(f"- **Missing Values:** {df.isnull().sum().sum()}")
    insights.append(f"- **Duplicate Rows:** {df.duplicated().sum()}")
    insights.append("")
    
    # Column analysis
    insights.append("### 🗂️ Data Structure")
    numeric_count = len(analysis.get('numeric_cols', []))
    categorical_count = len(analysis.get('suitable_for_grouping', []))
    
    insights.append(f"- **Numeric Columns:** {numeric_count}")
    insights.append(f"- **Categorical Columns:** {categorical_count}")
    insights.append("")
    
    # Sample findings
    insights.append("### 🔍 Key Findings")
    
    if numeric_count > 0:
        insights.append("- **Numerical data available** for statistical analysis")
        # Show stats for first numeric column
        numeric_cols = analysis.get('numeric_cols', [])
        if numeric_cols:
            col = numeric_cols[0]
            stats = df[col].describe()
            insights.append(f"  - {col}: Average {stats['mean']:.2f} (Range: {stats['min']:.2f}-{stats['max']:.2f})")
    
    if categorical_count > 0:
        insights.append("- **Categorical data available** for grouping analysis")
        # Show info for first categorical column
        cat_cols = analysis.get('suitable_for_grouping', [])
        if cat_cols:
            col = cat_cols[0]
            unique_count = df[col].nunique()
            insights.append(f"  - {col}: {unique_count} unique categories")
    
    insights.append("")
    insights.append("### 💡 Recommendations")
    insights.append("- Clean missing values to improve data quality")
    insights.append("- Explore relationships between variables")
    insights.append("- Create visualizations to uncover patterns")
    insights.append("- Consider segmenting data by categorical variables")
    
    insights.append("")
    insights.append("> *Tip: Add your DeepSeek API key for enhanced AI analysis*")
    
    return "\n".join(insights)
