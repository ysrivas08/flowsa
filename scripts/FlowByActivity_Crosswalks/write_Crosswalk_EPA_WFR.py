# write_Crosswalk_EPA_WRF.py (scripts)
# !/usr/bin/env python3
# coding=utf-8

"""
Create a crosswalk linking the downloaded EPA Wasted Food Report activities to NAICS_Code_2012.
Created by selecting unique Activity Names and
manually assigning to NAICS

 Sector assignments are based off Table 4
    https://www.epa.gov/sites/default/files/2020-11/documents/2018_wasted_food_report-11-9-20_final_.pdf

 Definitions of the waste management pathways are in the Wasted food measurement
 methodology scoping memo
 https://www.epa.gov/sites/production/files/2020-06/documents/food_measurement_methodology_scoping_memo-6-18-20.pdf

"""
import pandas as pd
from flowsa.settings import crosswalkpath
from scripts.FlowByActivity_Crosswalks.common_scripts import unique_activity_names, order_crosswalk


def assign_naics(df):
    """
    Function to assign NAICS codes to each dataframe activity

    :param df: df, a FlowByActivity subset that contains unique activity names
    :return: df with assigned Sector columns
    """

    # Activities producing the food waste
    # Activities with NAICS defined in Table 4 of the report
    df.loc[df['Activity'] == 'Correctional Facilities', 'Sector'] = \
        pd.Series([['92214', '5612']]*df.shape[0])
    df.loc[df['Activity'] == 'Food Banks', 'Sector'] = '62421'
    df.loc[df['Activity'] == 'Hospitals', 'Sector'] = '622'
    df.loc[df['Activity'] == 'Hotels', 'Sector'] = '7211'
    df.loc[df['Activity'] == 'Manufacturing/Processing', 'Sector'] = \
        pd.Series([['3112', '3113', '3114', '3115', '3116', '3117', '3118',
                    '3119', '312111', '31212', '31213', '31214']]*df.shape[0])
    df.loc[df['Activity'] == 'Nursing Homes', 'Sector'] = '623'
    df.loc[df['Activity'] == 'Restaurants/Food Services', 'Sector'] = \
        pd.Series([['7225', '72232', '72233']]*df.shape[0])
    df.loc[df['Activity'] == 'Retail', 'Sector'] = \
        pd.Series([['4451', '4452', '45291']]*df.shape[0])
    df.loc[df['Activity'] == 'Wholesale', 'Sector'] = '4244'

    # Activities where NAICS are not defined in T4 of report
    # method for colleges based on 4 year colleges
    # todo: assign to 4 year colleges only? (method results based on) or all
    #  related higher ed? junior colleges? trade schools?
    df.loc[df['Activity'] == 'Colleges & Universities', 'Sector'] = '6113'
    df.loc[df['Activity'] == 'K-12 Schools', 'Sector'] = '6111'
    df.loc[df['Activity'] == 'Military Installations', 'Sector'] = '92811'
    # use office building sector assignments identified by EIA CBECS
    # TODO: List currently duplicates some of the other assignments - modify
    #  list when other sectors finalized
    df.loc[df['Activity'] == 'Office Buildings', 'Sector'] = \
        pd.Series([['423', '424', '441', '454', '481', '482', '483', '484',
                    '485', '486', '487', '488', '492', '493', '511', '512',
                    '515', '516', '517', '518', '519', '521', '522', '523',
                    '524', '525', '531', '532', '533', '541', '551', '561',
                    '562', '611', '621', '624', '711', '712', '713', '811',
                    '813', '921', '922', '923', '924', '925', '926', '927',
                    '928']]*df.shape[0])
    # Household code
    df.loc[df['Activity'] == 'Residential', 'Sector'] = 'F010'
    # todo: reassess - currently assigned to food service contractors
    df.loc[df['Activity'] == 'Sports Venues', 'Sector'] = '722310'


    # Activities consuming the food waste Diverting material from the food
    # supply chain (directly or after processing) to animals
    df.loc[df['Activity'] == 'Animal Feed', 'Sector'] = '3111'
    df = pd.concat([df, pd.DataFrame(
        [['EPA_WFR', 'Animal Feed Collection', '5621191']],
        columns=['ActivitySourceName', 'Activity', 'Sector'])])

    # Converting material into industrial products. Ex. creating fibers for
    # packaging material, bioplastics , feathers (e.g., for pillows),
    # and rendering fat, oil, or grease into a raw material to make products
    # such as soaps, biodiesel, or cosmetics. “Biochemical processing” does
    # not refer to anaerobic digestion or production of bioethanol through
    # fermentation.
    # todo: update assignment to be inclusive of 31-33?
    df.loc[df['Activity'] == 'Bio-based Materials/Biochemical Processing',
           'Sector'] = '3131'
    df = pd.concat([df, pd.DataFrame(
        [['EPA_WFR', 'Bio-based Materials/Biochemical Processing '
                     'Collection', '5621192']],
        columns=['ActivitySourceName', 'Activity', 'Sector'])])

    # Breaking down material via bacteria in the absence of oxygen.
    # Generates biogas and nutrient-rich matter. This destination includes
    # fermentation (converting carbohydrates via microbes into alcohols in
    # the absence of oxygen to create products such as biofuels).
    df.loc[df['Activity'] == 'Codigestion/Anaerobic Digestion', 'Sector'] = \
        '5622191' # Subnaics 1 for AD

    # Composting refers to the production of organic material (via aerobic
    # processes) that can be used as a soil amendment
    df.loc[df['Activity'] ==
           'Composting/Aerobic Processes', 'Sector'] = \
        '5622192'  # Subnaics 2 for Compost

    # Sending material to a facility that is specifically designed for
    # combustion in a controlled manner, which may include some form of
    # energy recovery
    df.loc[df['Activity'] == 'Controlled Combustion', 'Sector'] = '562213'

    # collection and redistribution of unspoiled excess food to feed people
    # through food pantries, food banks and other food rescue programs
    df.loc[df['Activity'] == 'Food Donation', 'Sector'] = '624210'

    # Spreading, spraying, injecting, or incorporating organic material onto or
    # below the surface of the land to enhance soil quality
    df.loc[df['Activity'] == 'Land Application', 'Sector'] = '115112'
    df = pd.concat([df, pd.DataFrame(
        [['EPA_WFR', 'Land Application Collection', '5621193']],
        columns=['ActivitySourceName', 'Activity', 'Sector'])])

    # Sending material to an area of land or an excavated site that is
    # specifically designed and built to receive wastes
    df.loc[df['Activity'] == 'Landfill', 'Sector'] = '5622121'
    # Subnaics 1 for MSW Landfill

    # Sending material down the sewer (with or without prior treatment),
    # including that which may go to a facility designed to treat wastewater
    df.loc[df['Activity'] == 'Sewer/Wastewater Treatment', 'Sector'] = '22132'

    # break each sector into separate line
    df = df.explode('Sector')

    return df


if __name__ == '__main__':
    # select years to pull unique activity names
    years = ['2018']
    # assign datasource
    datasource = 'EPA_WFR'
    # df of unique ers activity names
    df_list = []
    for y in years:
        dfy = unique_activity_names(datasource, y)
        df_list.append(dfy)
    df = pd.concat(df_list, ignore_index=True).drop_duplicates()
    # add manual naics 2012 assignments
    df = assign_naics(df)
    # assign sector source name
    df['SectorSourceName'] = 'NAICS_2012_Code'
    # drop any rows where naics12 is 'nan'
    # (because level of detail not needed or to prevent double counting)
    df.dropna(subset=["Sector"], inplace=True)
    # assign sector type
    df['SectorType'] = "I"
    # sort df
    df = order_crosswalk(df)
    # save as csv
    df.to_csv(f"{crosswalkpath}NAICS_Crosswalk_{datasource}.csv",
              index=False)
