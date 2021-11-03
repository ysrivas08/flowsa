# USGS_MYB_ManufacturedAbrasive.py (flowsa)
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

Table T2

SourceName: USGS_MYB_ManufacturedAbrasive
https://www.usgs.gov/centers/nmic/manufactured-abrasives-statistics-and-information

Minerals Yearbook, xls file, tab T2:
ESTIMATED PRODUCTION OF CRUDE SILICON CARBIDE AND FUSED ALUMINUM OXIDE IN THE UNITED STATES AND CANADA

Data for: Manufactured Abrasive

Years = 2017+
"""
SPAN_YEARS = "2017-2018"


def usgs_ma_url_helper(build_url, config, args):
    """Used to substitute in components of usgs urls"""
    url = build_url
    return [url]


def usgs_ma_call(url, usgs_response, args):
    """TODO."""
    df_raw_data = pd.io.excel.read_excel(io.BytesIO(usgs_response.content), sheet_name='T2')# .dropna()
    df_data = pd.DataFrame(df_raw_data.loc[6:7]).reindex()
    df_data = df_data.reset_index()
    del df_data["index"]

    if len(df_data.columns) > 9:
        for x in range(9, len(df_data.columns)):
            col_name = "Unnamed: " + str(x)
            del df_data[col_name]


    if len(df_data. columns) == 9:
        df_data.columns = ["Product", "space_1", "quality_year_1", "space_2", "value_year_1", "space_3",
                           "quality_year_2", "space_4", "value_year_2"]
    elif len(df_data. columns) == 9:
        df_data.columns = ["Product", "space_1", "quality_year_1", "space_2", "value_year_1", "space_3",
                           "quality_year_2", "space_4", "value_year_2"]

    col_to_use = ["Product"]
    col_to_use.append("quality_" + usgs_myb_year(SPAN_YEARS, args["year"]))
    for col in df_data.columns:
        if col not in col_to_use:
            del df_data[col]

    return df_data


def usgs_ma_parse(dataframe_list, args):
    """Parsing the USGS data into flowbyactivity format."""
    data = {}
    row_to_use = ["Silicon carbide"]
    name = usgs_myb_name(args["source"])
    des = name
    dataframe = pd.DataFrame()
    for df in dataframe_list:
        for index, row in df.iterrows():
            remove_digits = str.maketrans('', '', digits)
            product = df.iloc[index]["Product"].strip().translate(remove_digits)
            if product in row_to_use:
                data = usgs_myb_static_varaibles()
                data["SourceName"] = args["source"]
                data["Year"] = str(args["year"])
                data['FlowName'] = "Silicon carbide"
                data["ActivityProducedBy"] = "Silicon carbide"
                data["Unit"] = "Metric Tons"
                col_name = "quality_" + usgs_myb_year(SPAN_YEARS, args["year"])
                col_name_array = col_name.split("_")
                data["Description"] = product + " " + col_name_array[0]
                data["FlowAmount"] = str(df.iloc[index][col_name])
                dataframe = dataframe.append(data, ignore_index=True)
                dataframe = assign_fips_location_system(dataframe, str(args["year"]))
    return dataframe
