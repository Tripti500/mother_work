import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from io import BytesIO

# Title of the Streamlit app
st.title("Streamlit Dataset with Filters and Charts")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file is not None:
    # Read the uploaded file
    df = pd.read_excel(uploaded_file)
    
    # Booking Date Filter (Date Range Picker)
    st.subheader("Select Booking Duration")
    start_date = st.date_input("Start Date", pd.to_datetime(df["BOOKING_DATE"].min()))
    end_date = st.date_input("End Date", pd.to_datetime(df["BOOKING_DATE"].max()))

    # Branch Filter with "All" option for multiple selection
    branch_options = ['All'] + df['BRANCH'].unique().tolist()
    selected_branches = st.multiselect("Select Branches", branch_options, default=['All'])

    # Product Filter with "All" option for multiple selection
    product_options = ['All'] + df['PRODUCT'].unique().tolist()
    selected_products = st.multiselect("Select Products", product_options, default=['All'])

    # Status Filter with "All" option for multiple selection
    status_options = ['All'] + df['STATUS'].unique().tolist()
    selected_statuses = st.multiselect("Select Statuses", status_options, default=['All'])

    # Filter the dataframe based on the selected criteria
    filtered_df = df[
        (pd.to_datetime(df["BOOKING_DATE"]) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(df["BOOKING_DATE"]) <= pd.to_datetime(end_date))
    ]

    # Apply additional filters for branch, product, and status (handling 'All' option)
    if 'All' not in selected_branches:
        filtered_df = filtered_df[filtered_df['BRANCH'].isin(selected_branches)]

    if 'All' not in selected_products:
        filtered_df = filtered_df[filtered_df['PRODUCT'].isin(selected_products)]

    if 'All' not in selected_statuses:
        filtered_df = filtered_df[filtered_df['STATUS'].isin(selected_statuses)]

    # Display filtered data (optionally allow users to see raw data)
    show_raw_data = st.checkbox("Show Raw Data", value=False)
    if show_raw_data:
        st.subheader("Filtered Raw Data")
        st.dataframe(filtered_df)

    # Group the data by branch and product, summing the amount
    grouped_data = filtered_df.groupby(["BRANCH", "PRODUCT"])["AMOUNT"].sum().reset_index()

    # Bar Chart: Amount by Branch and Product
    st.subheader("Bar Chart: Amount by Branch and Product")
    if not grouped_data.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_data = grouped_data.pivot(index="BRANCH", columns="PRODUCT", values="AMOUNT")
        bar_data.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title("Amount by Branch and Product")
        ax.set_xlabel("Branch")
        ax.set_ylabel("Amount")
        st.pyplot(fig)
    else:
        st.warning("No numeric data to plot for Bar Chart.")

    # Pie Chart: Amount by Branch
    st.subheader("Pie Chart: Amount by Branch")
    pie_data = grouped_data.groupby("BRANCH")["AMOUNT"].sum()
    if not pie_data.empty:
        fig, ax = plt.subplots()
        ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)
    else:
        st.warning("No numeric data to plot for Pie Chart.")

    # Line Chart: Amount Over Time
    st.subheader("Line Chart: Amount Over Time")
    line_data = filtered_df.groupby("BOOKING_DATE")["AMOUNT"].sum().reset_index()
    if not line_data.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(line_data["BOOKING_DATE"], line_data["AMOUNT"], marker='o', color='b')
        ax.set_title("Amount Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount")
        st.pyplot(fig)
    else:
        st.warning("No numeric data to plot for Line Chart.")

    # 3D Bar Chart: Amount by Branch and Product
    st.subheader("3D Bar Chart: Amount by Branch and Product")
    if not grouped_data.empty:
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')

        x = range(len(grouped_data["BRANCH"].unique()))
        y = range(len(grouped_data["PRODUCT"].unique()))
        z = [0] * len(grouped_data)

        dx = dy = 0.5
        dz = grouped_data["AMOUNT"].values

        ax.bar3d(x, y, z, dx, dy, dz, color='b', zsort='average')
        ax.set_xlabel('Branch')
        ax.set_ylabel('Product')
        ax.set_zlabel('Amount')
        ax.set_xticks(x)
        ax.set_xticklabels(grouped_data["BRANCH"].unique())
        ax.set_yticks(y)
        ax.set_yticklabels(grouped_data["PRODUCT"].unique())
        ax.set_title("3D Bar Chart: Amount by Branch and Product")
        st.pyplot(fig)
    else:
        st.warning("No numeric data to plot for 3D Bar Chart.")

    # Download Filtered Data
    st.subheader("Download Filtered Data")
    # Create an in-memory buffer for the Excel file
    buffer = BytesIO()
    # Write the filtered DataFrame to this buffer
    filtered_df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)  # Reset the buffer's position to the beginning

    # Add a download button to allow the user to download the filtered data
    st.download_button(
        label="Download Filtered Data as Excel",
        data=buffer,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Please upload an Excel file to proceed.")
