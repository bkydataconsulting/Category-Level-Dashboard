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

def format_hierarchy_styled(hierarchy, level=0):
    """
    Format the hierarchy into a readable string with different colors/sizes for each level.
    """
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
        result.append(f'<div style="{style}">{key}</div>')
        if value:
            result.extend(format_hierarchy_styled(value, level + 1))
    return result

def show_parent_master_only(df):
    """
    Show only unique Parent/Master category pairs with indentation format, grouped by parent.
    """
    if 'PARENT CATEGORY' in df.columns and 'MASTER CATEGORY' in df.columns:
        lines = []
        # Group by Parent Category
        for parent in df['PARENT CATEGORY'].unique():
            if pd.isna(parent):
                continue
            lines.append(parent)
            # Get all master categories for this parent
            masters = df[df['PARENT CATEGORY'] == parent]['MASTER CATEGORY'].unique()
            for master in sorted(masters):
                if pd.isna(master):
                    continue
                lines.append('    ' + master)  # 4 spaces indentation
            lines.append('')  # Add blank line between parents
        return '\n'.join(lines).strip()
    else:
        return 'Columns not found!'

def show_master_sub1_pairs(df):
    """
    Show Master/Subcategory 1 pairs with indentation format, grouped by master.
    """
    if 'MASTER CATEGORY' in df.columns and 'SUBCATEGORY 1' in df.columns:
        lines = []
        # Group by Master Category
        for master in df['MASTER CATEGORY'].unique():
            if pd.isna(master):
                continue
            lines.append(master)
            # Get all subcategory 1 items for this master
            sub1s = df[
                (df['MASTER CATEGORY'] == master) & 
                (df['SUBCATEGORY 1'].notna()) & 
                (df['SUBCATEGORY 1'] != '')
            ]['SUBCATEGORY 1'].unique()
            for sub1 in sorted(sub1s):
                lines.append('    ' + sub1)  # 4 spaces indentation
            lines.append('')  # Add blank line between masters
        return '\n'.join(lines).strip()
    else:
        return 'Columns not found!'

def process_file(uploaded_file):
    """
    Process the uploaded file and return the DataFrame
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.write("Successfully read CSV file")
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.write("Successfully read Excel file")
        else:
            st.error(f"Unsupported file type: {uploaded_file.name}")
            return None
        
        st.write("Columns found:", df.columns.tolist())
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def format_hierarchy_for_expander(items, level=0):
    """
    Format items for display inside an expander with proper styling and indentation.
    """
    styles = [
        'color:#ffffff; font-size:20px; font-weight:bold;',   # Level 0 (Parent)
        'color:#ffd700; font-size:18px; font-weight:bold;',   # Level 1 (Master)
        'color:#00ffcc; font-size:16px;',                     # Level 2 (Sub1)
        'color:#ff69b4; font-size:15px;',                     # Level 3 (Sub2)
    ]
    
    result = []
    indent = '&nbsp;' * 4 * level
    style = styles[level] if level < len(styles) else styles[-1]
    
    for item in items:
        result.append(f'<div style="{style}">{indent}{item}</div>')
    
    return result

def get_hierarchy_by_parent(df):
    """
    Organize the hierarchy by parent category with all subcategories.
    """
    hierarchies = {}
    
    for parent in df['PARENT CATEGORY'].unique():
        if pd.isna(parent):
            continue
            
        parent_data = df[df['PARENT CATEGORY'] == parent]
        hierarchy = {
            'parent': parent,
            'masters': []
        }
        
        for master in parent_data['MASTER CATEGORY'].unique():
            if pd.isna(master):
                continue
                
            master_data = parent_data[parent_data['MASTER CATEGORY'] == master]
            master_dict = {
                'name': master,
                'sub1': []
            }
            
            # Get Subcategory 1 items
            sub1_data = master_data['SUBCATEGORY 1'].dropna().unique()
            for sub1 in sub1_data:
                if pd.isna(sub1) or sub1 == '':
                    continue
                    
                sub1_dict = {
                    'name': sub1,
                    'sub2': []
                }
                
                # Get Subcategory 2 items if they exist
                if 'SUBCATEGORY 2' in master_data.columns:
                    sub2_data = master_data[
                        (master_data['SUBCATEGORY 1'] == sub1) & 
                        (master_data['SUBCATEGORY 2'].notna()) & 
                        (master_data['SUBCATEGORY 2'] != '')
                    ]['SUBCATEGORY 2'].unique()
                    
                    sub1_dict['sub2'] = list(sub2_data)
                
                master_dict['sub1'].append(sub1_dict)
            
            hierarchy['masters'].append(master_dict)
        
        hierarchies[parent] = hierarchy
    
    return hierarchies

def display_hierarchy_by_parent(df):
    """
    Display the hierarchy using expandable sections by parent category.
    """
    hierarchies = get_hierarchy_by_parent(df)
    
    for parent, hierarchy in hierarchies.items():
        with st.expander(parent, expanded=False):
            # Display masters under this parent
            for master in hierarchy['masters']:
                # Display master category
                master_html = format_hierarchy_for_expander([master['name']], level=1)
                st.markdown('<br>'.join(master_html), unsafe_allow_html=True)
                
                # Display subcategories
                for sub1 in master['sub1']:
                    # Display Subcategory 1
                    sub1_html = format_hierarchy_for_expander([sub1['name']], level=2)
                    st.markdown('<br>'.join(sub1_html), unsafe_allow_html=True)
                    
                    # Display Subcategory 2 if it exists
                    if sub1['sub2']:
                        sub2_html = format_hierarchy_for_expander(sub1['sub2'], level=3)
                        st.markdown('<br>'.join(sub2_html), unsafe_allow_html=True)

def main():
    st.title("Category Hierarchy Generator")
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            df = process_file(uploaded_file)
            
            if df is not None:
                # 1. Colored Expandable Hierarchy View
                st.subheader("Category Hierarchy")
                display_hierarchy_by_parent(df)
                
                # Create two columns for the text sections
                col1, col2 = st.columns(2)
                
                # 2. Parent/Master Text Copy in first column
                with col1:
                    st.subheader("Parent/Master Categories")
                    parent_master = show_parent_master_only(df)
                    st.text_area("Parent/Master Categories", parent_master, height=400)
                    if st.button("Copy Parent/Master"):
                        pyperclip.copy(parent_master)
                        st.success("Parent/Master copied to clipboard!")
                
                # 3. Master/Sub1 Text Copy in second column
                with col2:
                    st.subheader("Master/Subcategory 1 Pairs")
                    master_sub1 = show_master_sub1_pairs(df)
                    st.text_area("Master/Subcategory 1 Pairs", master_sub1, height=400)
                    if st.button("Copy Master/Sub1"):
                        pyperclip.copy(master_sub1)
                        st.success("Master/Sub1 copied to clipboard!")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main() 