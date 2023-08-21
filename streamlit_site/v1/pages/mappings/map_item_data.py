import streamlit as st
import enum

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

item_categories = {
    "1 - Main Weapon": {
        "category_id": 1,
    },
    "5 - Sub Weapon": {
        "category_id": 5,
    },
    "10 - Awakening Weapon": {
        "category_id": 10,
    },
    "15 - Armor": {
        "category_id": 15,
    },
    "20 - Accessory": {
        "category_id": 20,
    },
    "25 - Material": {
        "category_id": 25,
    },
    "30 - Enhancement Material": {
        "category_id": 30,
    },
    "35 - Consumable": {
        "category_id": 35,
    },
    "40 - Life Tools": {
        "category_id": 40,
    },
    "45 - Alchemy Stone": {
        "category_id": 45,
    },
    "50 - Magic Crystal": {
        "category_id": 50,
    },
    "55 - Pearl Item": {
        "category_id": 55,
    },
    "60 - Dyes": {
        "category_id": 60,
    },
    "65 - Mount": {
        "category_id": 65,
    },
    "70 - Ship": {
        "category_id": 70,
    },
    "75 - Wagon": {
        "category_id": 75,
    },
    "80 - Furniture": {
        "category_id": 80,
    },
}
