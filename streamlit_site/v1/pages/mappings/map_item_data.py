import streamlit as st

item_info_column_config = {
    "mainKey": st.column_config.NumberColumn("Item ID", format="%.0f"),
    "name": st.column_config.TextColumn("Item Name"),
    "grade": st.column_config.NumberColumn("Grade", format="%.0f"),
    "isGodrAyed": st.column_config.TextColumn("Godr-Ayed?"),
    "main_category": st.column_config.TextColumn("Main Category"),
    "sub_category": st.column_config.TextColumn("Sub Category"),
    "main_category_id": st.column_config.NumberColumn("Main Category ID", format="%.0f"),
    "sub_category_id": st.column_config.NumberColumn("Sub Category ID", format="%.0f"),
}
