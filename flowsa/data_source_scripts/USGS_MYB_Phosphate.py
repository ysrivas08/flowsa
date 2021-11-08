# USGS_MYB_Phosphate.py (flowsa)
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
SourceName: USGS_MYB_Phosphate
https://www.usgs.gov/centers/nmic/phosphate-rock-statistics-and-information

Minerals Yearbook, xls file, tab T1:

Data for: Phosphate Rock; marketable


Years = 2014+
There is no export for Phosphate.
"""

SPAN_YEARS = "2014-2018"

def usgs_phosphate_url_helper(build_url, config, args):
    """Used to substitute in components of usgs urls"""

    url = build_url
    return [url]


def usgs_phosphate_call(url, usgs_response, args):
    """Calls the excel sheet for nickel and removes extra columns"""
    df_raw_data_one = pd.io.excel.read_excel(io.BytesIO(usgs_response.content), sheet_name='T1')  # .dropna()
    df_data_one = pd.DataFrame(df_raw_data_one.loc[7:9]).reindex()
    df_data_one = df_data_one.reset_index()
    del df_data_one["index"]

    df_data_two = pd.DataFrame(df_raw_data_one.loc[19:21]).reindex()
    df_data_two = df_data_two.reset_index()
    del df_data_two["index"]

    if len(df_data_one.columns) > 11:
        for x in range(11, len(df_data_one.columns)):
            col_name = "Unnamed: " + str(x)
            del df_data_one[col_name]
            del df_data_two[col_name]

    if len(df_data_one. columns) == 11:
        df_data_one.columns = ["Production", "space_1", "year_1", "space_3", "year_2",
                               "space_4", "year_3", "space_5", "year_4", "space_6", "year_5"]
        df_data_two.columns = ["Production", "space_1", "year_1", "space_3", "year_2",
                               "space_4", "year_3", "space_5", "year_4", "space_6", "year_5"]

    col_to_use = ["Production"]
    col_to_use.append(usgs_myb_year(SPAN_YEARS, args["year"]))

    for col in df_data_one.columns:
        if col not in col_to_use:
            del df_data_one[col]
            del df_data_two[col]

    frames = [df_data_one, df_data_two]
    df_data = pd.concat(frames)
    df_data = df_data.reset_index()
    del df_data["index"]

    return df_data


def usgs_phosphate_parse(dataframe_list, args):
    """
    Combine, parse, and format the provided dataframes
    :param dataframe_list: list of dataframes to concat and format
    :param args: dictionary, used to run flowbyactivity.py ('year' and 'source')
    :return: df, parsed and partially formatted to flowbyactivity specifications
    """
    data = {}
    row_to_use = ["Gross weight", "Quantity, gross weight"]
    prod = ""
    name = usgs_myb_name(args["source"])
    des = name
    dataframe = pd.DataFrame()
    col_name = usgs_myb_year(SPAN_YEARS, args["year"])
    for df in dataframe_list:
        for index, row in df.iterrows():
            if df.iloc[index]["Production"].strip() == "Marketable production:":
                prod = "production"
            elif df.iloc[index]["Production"].strip() == "Imports for consumption:3":
                prod = "import"

            if df.iloc[index]["Production"].strip() in row_to_use:
                product = df.iloc[index]["Production"].strip()
                data = usgs_myb_static_varaibles()
                data["SourceName"] = args["source"]
                data["Year"] = str(args["year"])
                data["Unit"] = "Thousand Metric Tons"
                data["FlowAmount"] = str(df.iloc[index][col_name])
                if str(df.iloc[index][col_name]) == "W":
                    data["FlowAmount"] = withdrawn_keyword
                data["Description"] = des
                data["ActivityProducedBy"] = name
                data['FlowName'] = name + " " + prod
                dataframe = dataframe.append(data, ignore_index=True)
                dataframe = assign_fips_location_system(dataframe, str(args["year"]))
    return dataframe
