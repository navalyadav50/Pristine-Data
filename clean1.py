import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Function to display summary of data types
def summary(df):
    if df is not None:
        dt = pd.DataFrame(df.dtypes).reset_index()
        dt.columns = ['Column', 'Data Type']
        return dt

# Function to convert DataFrame to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to provide a download link for the CSV
def get_download_link(df, filename="updated_data.csv"):
    csv = convert_df_to_csv(df)
    st.sidebar.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# Function to reset session state
def reset_session_state():
    st.session_state.clear()

# Button CSS for uniform styling
st.markdown("""
<style>
.stButton > button {
    width: 150px;
    height: 50px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# Sidebar for file upload and reset button
st.sidebar.header('📤 Upload your CSV file here')
file = st.sidebar.file_uploader("", type="csv")

st.sidebar.write("> *Click the Reset button to undo all changes*")
if st.sidebar.button('Reset'):
    reset_session_state()

st.title("Pristine Data")

# Main app logic
if file is None:
    st.warning('Please upload a CSV file.')
else:
    try:
        if 'last_uploaded_file' not in st.session_state or st.session_state.last_uploaded_file != file:
            reset_session_state()
        st.session_state.last_uploaded_file = file

        # Read CSV file
        df = pd.read_csv(file)

        # Initialize session state for modified columns
        if 'modified_columns' not in st.session_state:
            st.session_state.modified_columns = df.columns.tolist()

        st.title('File Overview')
        st.write(f'Rows: {df.shape[0]} | Columns: {df.shape[1]}')
        st.write(summary(df))

        # **Edit Column Names**
        st.write("### Edit Column Names")
        new_column_names = []
        for col in st.session_state.modified_columns:
            new_name = st.text_input(f"Rename column '{col}'", value=col)
            new_column_names.append(new_name)
        df.columns = new_column_names
        st.session_state.modified_columns = new_column_names

        # **Edit Data Values**
        st.write("### Edit Data")
        selected_column = st.selectbox("Select column to edit", df.columns)
        if selected_column:
            selected_row = st.selectbox("Select row to edit", range(len(df)))
            current_value = df.at[selected_row, selected_column]
            new_value = st.text_input(f"Edit value for '{selected_column}' at row {selected_row}", value=current_value)
            if st.button("Update Value"):
                df.at[selected_row, selected_column] = new_value
                st.success("Value updated successfully!")

        # Handle duplicates
        st.write("### Duplicate Rows")
        duplicate_count = df.duplicated().sum()
        st.write(f"No. of Duplicate rows: {duplicate_count}")
        if st.button('Delete Duplicates'):
            df.drop_duplicates(inplace=True)
            st.success('Duplicates deleted')

        # **Highlight Missing Values**
        st.write('### Data Preview with Missing Values Highlighted')
        missing_values_style = df.style.applymap(
            lambda x: 'background-color: skyblue' if pd.isnull(x) else ''
        )
        st.dataframe(missing_values_style)

        # **Handle Missing Values**
        st.write("### Handle Missing Values")
        missing_summary = df.isnull().sum()
        st.write(missing_summary[missing_summary > 0])
        fill_na_columns = st.multiselect("Select columns to fill missing values", df.columns)
        fill_value = st.text_input("Enter value to fill missing data")
        if st.button('Fill Missing Values'):
            df[fill_na_columns] = df[fill_na_columns].fillna(fill_value)
            st.success('Missing values filled')

        # Visualization Options
        st.write("## Data Visualization")
        visualization_type = st.selectbox("Choose Visualization Type", ["Pie Chart", "Bar Graph", "Histogram", "Comparison Graph"])

        if visualization_type == "Pie Chart":
            categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            pie_chart_col = st.selectbox("Select column for Pie Chart", options=categorical_columns)
            if pie_chart_col:
                pie_data = df[pie_chart_col].value_counts()
                plt.figure(figsize=(8, 6))
                plt.pie(
                    pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90,
                    colors=sns.color_palette("pastel", len(pie_data))
                )
                plt.title(f"Distribution of {pie_chart_col}")
                st.pyplot(plt)

        elif visualization_type == "Bar Graph":
            bar_col = st.selectbox("Select column for Bar Graph", options=df.columns)
            if bar_col:
                plt.figure(figsize=(10, 6))
                sns.countplot(x=bar_col, data=df)
                plt.xticks(rotation=45)
                plt.title(f"Bar Graph of {bar_col}")
                st.pyplot(plt)

        elif visualization_type == "Histogram":
            numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            hist_col = st.selectbox("Select column for Histogram", options=numeric_columns)
            if hist_col:
                plt.figure(figsize=(10, 6))
                plt.hist(df[hist_col], bins=20, color='skyblue', edgecolor='black')
                plt.title(f"Histogram of {hist_col}")
                st.pyplot(plt)

        elif visualization_type == "Comparison Graph":
            numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            col_x = st.selectbox("Select X-axis", options=numeric_columns)
            col_y = st.selectbox("Select Y-axis", options=numeric_columns)
            if col_x and col_y:
                plt.figure(figsize=(10, 6))
                sns.scatterplot(x=col_x, y=col_y, data=df)
                plt.title(f"Comparison of {col_x} vs {col_y}")
                st.pyplot(plt)

        # Provide download link for the updated dataframe
        st.sidebar.write("## 🗂️ Download Updated Data")
        get_download_link(df)

    except Exception as e:
        st.error(f"An error occurred: {e}")
