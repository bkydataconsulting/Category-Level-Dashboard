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
    Format the hierarchy into a readable string with proper indentation
    """
    result = []
    for key, value in hierarchy.items():
        result.append('  ' * level + key)
        if value:
            result.extend(format_hierarchy(value, level + 1))
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

def main():
    st.title("Category Hierarchy Generator")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            # Process the file directly from the uploaded file object
            result = process_file(uploaded_file)
            
            if result:
                # Display the result
                st.text_area("Hierarchy", result, height=400)
                
                # Add copy button
                if st.button("Copy to Clipboard"):
                    pyperclip.copy(result)
                    st.success("Copied to clipboard!")
                
                # Add download button
                if st.button("Download as TXT"):
                    with open("hierarchy.txt", "w") as f:
                        f.write(result)
                    st.success("Downloaded as hierarchy.txt!")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main() 