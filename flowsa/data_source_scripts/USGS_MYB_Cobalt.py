# USGS_MYB_Cobalt.py (flowsa)
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
Table T1 and T8

SourceName: USGS_MYB_Cobalt
https://www.usgs.gov/centers/nmic/cobalt-statistics-and-information

Minerals Yearbook, xls file, tab T1 and T8:
United States, sulfide ore, concentrate

Data for: Cobalt; cobalt content

Years = 2013+
"""
SPAN_YEARS = "2013-2017"

def usgs_cobalt_url_helper(build_url, config, args):
    """Used to substitute in components of usgs urls"""
    url = build_url
    return [url]


def usgs_cobalt_call(url, usgs_response, args):
    """Calls the excel sheet for nickel and removes extra columns"""
    df_raw_data = pd.io.excel.read_excel(io.BytesIO(usgs_response.content), sheet_name='T8')# .dropna()


    df_raw_data_two = pd.io.excel.read_excel(io.BytesIO(usgs_response.content), sheet_name='T1')  # .dropna()

    df_data_1 = pd.DataFrame(df_raw_data_two.loc[6:11]).reindex()
    df_data_1 = df_data_1.reset_index()
    del df_data_1["index"]

    df_data_2 = pd.DataFrame(df_raw_data.loc[23:23]).reindex()
    df_data_2 = df_data_2.reset_index()
    del df_data_2["index"]

    if len(df_data_2.columns) > 11:
        for x in range(11, len(df_data_2.columns)):
            col_name = "Unnamed: " + str(x)
            del df_data_2[col_name]

    if len(df_data_1. columns) == 12:
        df_data_1.columns = ["Production", "space_6", "space_1", "year_1", "space_2", "year_2", "space_3",
                           "year_3", "space_4", "year_4", "space_5", "year_5"]
    if len(df_data_2. columns) == 11:
        df_data_2.columns = ["Production", "space_1", "year_1", "space_2", "year_2", "space_3",
                           "year_3", "space_4", "year_4", "space_5", "year_5"]

    col_to_use = ["Production"]
    col_to_use.append(usgs_myb_year(SPAN_YEARS, args["year"]))
    for col in df_data_1.columns:
        if col not in col_to_use:
            del df_data_1[col]
    for col in df_data_2.columns:
        if col not in col_to_use:
            del df_data_2[col]
    frames = [df_data_1, df_data_2]
    df_data = pd.concat(frames)
    df_data = df_data.reset_index()
    del df_data["index"]
    return df_data


def usgs_cobalt_parse(dataframe_list, args):
    """
    Combine, parse, and format the provided dataframes
    :param dataframe_list: list of dataframes to concat and format
    :param args: dictionary, used to run flowbyactivity.py ('year' and 'source')
    :return: df, parsed and partially formatted to flowbyactivity specifications
    """
    data = {}
    name = usgs_myb_name(args["source"])
    des = name
    row_to_use = ["United Statese, 16, 17", "Mine productione", "Imports for consumption", "Exports"]
    dataframe = pd.DataFrame()
    for df in dataframe_list:

        for index, row in df.iterrows():
            prod = "production"
            # if df.iloc[index]["Production"].strip() == "Mine productione":
            #   prod = "mine production"
            if df.iloc[index]["Production"].strip() == "United Statese, 16, 17":
                prod = "production"
            elif df.iloc[index]["Production"].strip() == "Imports for consumption":
                prod = "imports"
            elif df.iloc[index]["Production"].strip() == "Exports":
                prod = "exports"


            if df.iloc[index]["Production"].strip() in row_to_use:
                remove_digits = str.maketrans('', '', digits)
                product = df.iloc[index]["Production"].strip().translate(remove_digits)
                data = usgs_myb_static_varaibles()



                data["SourceName"] = args["source"]
                data["Year"] = str(args["year"])



                data["Unit"] = "Thousand Metric Tons"
                col_name = usgs_myb_year(SPAN_YEARS, args["year"])
                data["Description"] = des
                data["ActivityProducedBy"] = name
                data['FlowName'] = name + " " + prod

                data["FlowAmount"] = str(df.iloc[index][col_name])
                remove_rows = ["(18)", "(2)"]
                if data["FlowAmount"] not in remove_rows:
                    dataframe = dataframe.append(data, ignore_index=True)
                    dataframe = assign_fips_location_system(dataframe, str(args["year"]))
    return dataframe

