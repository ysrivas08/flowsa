# USGS_MYB_SodaAsh.py (flowsa)
# !/usr/bin/env python3
# coding=utf-8

import io
from flowsa.common import *
from flowsa.flowbyfunctions import assign_fips_location_system


"""
Projects
/
FLOWSA
/

FLOWSA-314

Import USGS Mineral Yearbook data

Description

Table T1

SourceName: USGS_MYB_Barite
https://www.usgs.gov/centers/nmic/barite-statistics-and-information

Minerals Yearbook, xls file, tab T1 

Data for: Barite; sold or used, mine

Years = 2014+
"""

def year_name_barite(year):
    if int(year) == 2014:
        return_val = "year_1"
    elif int(year) == 2015:
        return_val = "year_2"
    elif int(year) == 2016:
        return_val = "year_3"
    elif int(year) == 2017:
        return_val = "year_4"
    elif int(year) == 2018:
        return_val = "year_5"
    return return_val


def usgs_barite_url_helper(build_url, config, args):
    """Used to substitute in components of usgs urls"""
    # URL Format, replace __year__ and __format__, either xls or xlsx.
    url = build_url
    return [url]


def usgs_barite_call(url, usgs_response, args):
    """TODO."""
    df_raw_data = pd.io.excel.read_excel(io.BytesIO(usgs_response.content), sheet_name='T1')# .dropna()
    df_data = pd.DataFrame(df_raw_data.loc[7:14]).reindex()
    df_data = df_data.reset_index()
    del df_data["index"]


    if len(df_data. columns) == 11:
        df_data.columns = ["Production", "space_1", "year_1", "space_2", "year_2", "space_3",
                             "year_3", "space_4", "year_4", "space_5", "year_5"]

    col_to_use = ["Production"]
    col_to_use.append(year_name_barite(args["year"]))
    for col in df_data.columns:
        if col not in col_to_use:
            del df_data[col]

    return df_data


def usgs_barite_parse(dataframe_list, args):
    """Parsing the USGS data into flowbyactivity format."""
    data = {}
    row_to_use = ["Quantity"]
    dataframe = pd.DataFrame()
    for df in dataframe_list:
        for index, row in df.iterrows():
            if df.iloc[index]["Production"].strip() == "Imports for consumption:3":
                product = "imports"
            elif df.iloc[index]["Production"].strip() == "Crude, sold or used by producers:":
                product = "production"
            elif df.iloc[index]["Production"].strip() == "Exports:2":
                product = "exports"



            if df.iloc[index]["Production"].strip() in row_to_use:
                data["Class"] = "Geological"
                data['FlowType'] = "ELEMENTARY_FLOWS"
                data["Location"] = "00000"
                data["Compartment"] = "ground"
                data["SourceName"] = "USGS_MYB_Titanium"
                data["Year"] = str(args["year"])
                data["Unit"] = "Metric Tons"
                data['FlowName'] = "Barite " + product
                data["Context"] = None
                data["ActivityConsumedBy"] = None
                data["Description"] = "Barite"
                data["ActivityProducedBy"] = "Barite"
                col_name = year_name_barite(args["year"])
                if str(df.iloc[index][col_name]) == "--" or str(df.iloc[index][col_name]) == "(3)":
                    data["FlowAmount"] = str(0)
                else:
                    data["FlowAmount"] = str(df.iloc[index][col_name])
                dataframe = dataframe.append(data, ignore_index=True)
                dataframe = assign_fips_location_system(dataframe, str(args["year"]))
    return dataframe

