import pandas as pd
import streamlit as st
from pathlib import Path
import pyperclip
import io

def build_hierarchy(df):
    """
    Build a hierarchical dictionary from the DataFrame
    """
    hierarchy = {}
    
    for _, row in df.iterrows():
        current = hierarchy
        for col in df.columns:
            value = str(row[col]).strip()
            if value and value.lower() != 'nan':
                if value not in current:
                    current[value] = {}
                current = current[value]
    
    return hierarchy

def format_hierarchy(hierarchy, level=0):
    """
    Format the hierarchy into a readable string with proper indentation (4 spaces per level)
    """
    result = []
    for key, value in hierarchy.items():
        result.append('    ' * level + key)  # 4 spaces per level
        if value:
            result.extend(format_hierarchy(value, level + 1))
    return result

def format_hierarchy_styled(hierarchy, level=0):
    """
    Format the hierarchy into a readable string with 8 spaces per level and different colors/sizes for each level.
    """
    # Define styles for up to 5 levels (add more if needed)
    styles = [
        'color:#ffffff; font-size:22px; font-weight:bold;',   # Level 0
        'color:#ffd700; font-size:20px; font-weight:bold;',   # Level 1
        'color:#00ffcc; font-size:18px;',                     # Level 2
        'color:#ff69b4; font-size:16px;',                     # Level 3
        'color:#87ceeb; font-size:15px;',                     # Level 4
        'color:#cccccc; font-size:14px;',                     # Level 5+
    ]
    result = []
    for key, value in hierarchy.items():
        style = styles[level] if level < len(styles) else styles[-1]
        indent = '&nbsp;' * 8 * level  # 8 spaces per level
        result.append(f'<div style="{style}">{indent}{key}</div>')
        if value:
            result.extend(format_hierarchy_styled(value, level + 1))
    return result

def format_hierarchy_for_expander(hierarchy, level=0):
    """
    Format the hierarchy as indented colored HTML for display inside an expander.
    """
    styles = [
        'color:#ffd700; font-size:18px; font-weight:bold;',   # Level 1
        'color:#00ffcc; font-size:16px;',                     # Level 2
        'color:#ff69b4; font-size:15px;',                     # Level 3
        'color:#87ceeb; font-size:14px;',                     # Level 4
        'color:#cccccc; font-size:13px;',                     # Level 5+
    ]
    result = []
    for key, value in hierarchy.items():
        style = styles[level-1] if level-1 < len(styles) else styles[-1]
        indent = '&nbsp;' * 4 * level
        result.append(f'<div style="{style}">{indent}{key}</div>')
        if value:
            result.extend(format_hierarchy_for_expander(value, level + 1))
    return result

def process_file(uploaded_file):
    """
    Process the uploaded file and return the formatted hierarchy
    """
    try:
        # Read file directly from the uploaded file object
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.write("Successfully read CSV file")
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.write("Successfully read Excel file")
        else:
            st.error(f"Unsupported file type: {uploaded_file.name}")
            return None
        
        # Display column names for debugging
        st.write("Columns found:", df.columns.tolist())
        
        # Build and format hierarchy
        hierarchy = build_hierarchy(df)
        formatted = format_hierarchy(hierarchy)
        return '\n'.join(formatted)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def display_top_level_expanders(hierarchy):
    """
    Only use expanders for top-level categories. Show subcategories as indented colored text inside.
    """
    for key, value in hierarchy.items():
        with st.expander(key, expanded=False):
            if value:
                html = '<br>'.join(format_hierarchy_for_expander(value, level=1))
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.markdown(f'<span style="color:#ffd700; font-size:16px;">{key}</span>', unsafe_allow_html=True)

def main():
    st.title("Category Hierarchy Generator")
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            uploaded_file.seek(0)
            result = process_file(uploaded_file)
            if result:
                uploaded_file.seek(0)
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                hierarchy = build_hierarchy(df)
                st.subheader("Expandable Hierarchy View (Top Level Only)")
                display_top_level_expanders(hierarchy)
                st.subheader("Plain Text Hierarchy (for copy/paste)")
                st.text_area("Plain Text Hierarchy", result, height=400)
                if st.button("Copy to Clipboard"):
                    pyperclip.copy(result)
                    st.success("Copied to clipboard!")
                if st.button("Download as TXT"):
                    with open("hierarchy.txt", "w") as f:
                        f.write(result)
                    st.success("Downloaded as hierarchy.txt!")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main() 