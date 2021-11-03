# USGS_MYB_Titanium.py (flowsa)
# !/usr/bin/env python3
# coding=utf-8

import io
from flowsa.flowbyfunctions import assign_fips_location_system
from flowsa.data_source_scripts.USGS_MYB_Common import *

"""
Projects
/
FLOWSA
/

FLOWSA-314

Import USGS Mineral Yearbook data

Description

Table T1

SourceName: USGS_MYB_Titanium
https://www.usgs.gov/centers/nmic/titanium-statistics-and-information

Minerals Yearbook, xls file, tab T1

Data for: Titanium and Titanium Dioxide; mineral concentrate

Years = 2012+
"""
SPAN_YEARS = "2013-2017"



def usgs_titanium_url_helper(build_url, config, args):
    """Used to substitute in components of usgs urls"""
    url = build_url
    return [url]


def usgs_titanium_call(url, usgs_response, args):
    """TODO."""
    df_raw_data = pd.io.excel.read_excel(io.BytesIO(usgs_response.content), sheet_name='T1')# .dropna()
    df_data_1 = pd.DataFrame(df_raw_data.loc[4:7]).reindex()
    df_data_1 = df_data_1.reset_index()
    del df_data_1["index"]

    df_data_2 = pd.DataFrame(df_raw_data.loc[12:15]).reindex()
    df_data_2 = df_data_2.reset_index()
    del df_data_2["index"]

    if len(df_data_1. columns) == 13:
        df_data_1.columns = ["Production", "space_1", "Unit", "space_6", "year_1", "space_2", "year_2", "space_3",
                             "year_3", "space_4", "year_4", "space_5", "year_5"]
        df_data_2.columns = ["Production", "space_1", "Unit", "space_6", "year_1", "space_2", "year_2", "space_3",
                             "year_3", "space_4", "year_4", "space_5", "year_5"]

    col_to_use = ["Production"]
    col_to_use.append(usgs_myb_year(SPAN_YEARS, args["year"]))
    for col in df_data_2.columns:
        if col not in col_to_use:
            del df_data_2[col]
            del df_data_1[col]

    frames = [df_data_1, df_data_2]
    df_data = pd.concat(frames)
    df_data = df_data.reset_index()
    del df_data["index"]
    return df_data


def usgs_titanium_parse(dataframe_list, args):
    """Parsing the USGS data into flowbyactivity format."""
    data = {}
    row_to_use = ["Production2", "Production", "Imports for consumption"]
    dataframe = pd.DataFrame()
    name = ""

    for df in dataframe_list:
        for index, row in df.iterrows():
            if df.iloc[index]["Production"].strip() == "Imports for consumption":
                product = "imports"
            elif df.iloc[index]["Production"].strip() == "Production2" or df.iloc[index]["Production"].strip() == "Production":
                product = "production"
            if df.iloc[index]["Production"].strip() == "Mineral concentrates:":
                name = "Titanium"
            elif df.iloc[index]["Production"].strip() == "Titanium dioxide pigment:":
                name = "Titanium dioxide"


            if df.iloc[index]["Production"].strip() in row_to_use:
                data = usgs_myb_static_varaibles()
                data["SourceName"] = args["source"]
                data["Year"] = str(args["year"])
                data["Unit"] = "Metric Tons"
                data['FlowName'] = name + " " + product
                data["Description"] = name
                data["ActivityProducedBy"] = name
                col_name = usgs_myb_year(SPAN_YEARS, args["year"])
                if str(df.iloc[index][col_name]) == "--" or str(df.iloc[index][col_name]) == "(3)":
                    data["FlowAmount"] = str(0)
                else:
                    data["FlowAmount"] = str(df.iloc[index][col_name])
                dataframe = dataframe.append(data, ignore_index=True)
                dataframe = assign_fips_location_system(dataframe, str(args["year"]))
    return dataframe
