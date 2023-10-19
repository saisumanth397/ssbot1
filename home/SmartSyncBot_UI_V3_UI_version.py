# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 04:09:23 2023
name of original code : SmartSyncBot_V9_making_fn_for_UI
@author: u1111677
"""

import os, time
import openai as p
import pandas as pd
import json
from .config import *
from datetime import datetime
from .input_db_v2 import *
from .Bot_UI import *
pd.set_option('mode.chained_assignment',None)


 
from openai import ChatCompletion
from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential, ClientSecretCredential


    

def search_mapping(mp_sheet,srch_field): 

    #result_df = mp_sheet[mp_sheet.applymap(lambda x: str(x).lower() == srch_field.lower()).any(axis=1)]
    result_df = mp_sheet[mp_sheet.applymap(lambda x: any(segment.lower() == srch_field.lower() for segment in str(x).split('/') + str(x).split('.'))).any(axis=1)]
    if result_df.empty:
        print("\nNo matching records found.") # comment this later
        result_df=pd.DataFrame()
        return result_df
        
    else:
        print("\nMatching records found:") # comment this later
        print(result_df)                    # comment this later
        return result_df
        
        
def get_mdm_data(id_fld):
	return f"""select * from ReltioSourceMaster
               where mdm_id='{id_fld}' 
               or lower(name)=lower('{id_fld}') """
        
def get_om_data(id_nam):
    return f""" select * from OrganisationManager
                where mdm_id='{id_nam}'
            """
def get_ocep_data(id_nam):
    return f""" select * from SalesForceCRM
                where mdm_id='{id_nam}'
            """
            
def get_oced_data(id_nam):
    return f""" select * from DigitalCRM
                where mdm_id='{id_nam}'
            """
        
def sync_details_fetch(srch_fld):
    mdm_result = pd.DataFrame({'Source_system_name': ['ReltioSourceMaster']})
    om_result = pd.DataFrame({'Source_system_name': ['OrganisationManager']})
    ocep_result = pd.DataFrame({'Source_system_name': ['SalesForceCRM']})
    oced_result = pd.DataFrame({'Source_system_name': ['DigitalCRM']})
    
    
    connct=sqlite3.connect(DB_Name)
    
    mdm_qry=get_mdm_data(srch_fld)
    mdm_result=pd.read_sql_query(mdm_qry,connct)
    
    
    
    if mdm_result.empty:
        print("\nNo match in MDM for ",srch_fld)
        #mdm_result = pd.DataFrame({'Source_system_name': ['MDM']})
        mdm_result['Source_system_name']=['ReltioSourceMaster']
    else:
        mdm_id_fund=mdm_result["MDM_ID"].iloc[0]
        print("\nMatch found for MDM ID : ",mdm_id_fund,"\n")
        print(mdm_result)
        
        om_qry=get_om_data(mdm_id_fund)
        oced_qry=get_oced_data(mdm_id_fund)
        ocep_qry=get_ocep_data(mdm_id_fund)
        om_result=pd.read_sql_query(om_qry,connct)
        oced_result=pd.read_sql_query(oced_qry,connct)
        ocep_result=pd.read_sql_query(ocep_qry,connct)
    
    if om_result.empty:
        om_result['Source_system_name']=['OrganisationManager']
    if oced_result.empty:
        oced_result['Source_system_name']=['DigitalCRM']
    if ocep_result.empty:
        ocep_result['Source_system_name']=['SalesForceCRM']
    
    mdm_result['Source_system_name']=['ReltioSourceMaster']
    om_result['Source_system_name']=['OrganisationManager']
    oced_result['Source_system_name']=['DigitalCRM']
    ocep_result['Source_system_name']=['SalesForceCRM']
    
    sync_db=pd.concat([mdm_result,om_result,oced_result,ocep_result],axis=0)
    sync_db=sync_db.reset_index(drop=True)
    
    print("\nFinal sync_db\n",sync_db)
    
    connct.close()
    
    return sync_db
    
def smartsyncbot(user_prompt):   
        
    #Calling identify_bot
    
    #user_prompt_ident=input("\nSmart_Sync_Bot : How can I help you today?\n\nUser : ")
    response_intial=identify_bot(user_prompt)
    
    if  "service_name" in response_intial:
        print("\nI have reached till here\n")
        response_intial=json.loads(response_intial)
        print("\nI have reached till here2\n")
        print("\nService Identified :" , response_intial["service_name"])
        print("SmartSyncBot checking .....\n")
        print(response_intial)
        #print("\nidentify_bot Usage\n",usage_ident,"\n")
    else:
        print("\nI am here\n")
        print("\nService not identified\nidnetifyBot Response\n")
        print(response_intial)
        
        return response_intial
        #print("\nidentify_bot Usage\n",usage_ident,"\n")
    
    #Calling chatbot
    
    if  isinstance(response_intial, dict):
        if response_intial["service_name"]=='sync_check':
            sync_db_df=sync_details_fetch(response_intial["field_name"]) #search function to get the necessary imports from systems
            print("\nReturned sycing result\n" , sync_db_df)
            #print("Type : ",type(sync_db_df))
            sync_db_df=sync_db_df.to_json(orient='records')
            #print("Type : ",type(sync_db_df))
            response=chatbot(user_prompt,sync_data_json=sync_db_df)
            print("\nSmart_Sync_Bot :" ,response )
            #print("\nChat_bot Usage\n",usage,"\n")
            f1=feedback(user_prompt,response)
            messages.extend(f1)
            print("\Messages getting appended inside funtiocn\n",messages)
        
        elif response_intial["service_name"]=='mapping_check':
            mp_sht=search_mapping(mp_sheet,response_intial["field_name"])
            print("\nReturned mapping result\n" , mp_sht)
            #print("Type : ",type(mp_sht))
            mp_sht2=mp_sht.to_json(orient='records')
            #print("Type : ",type(mp_sht2))
            response=chatbot(user_prompt,mapping_sheet1=mp_sht2)
            print("\nSmart_Sync_Bot :" ,response )
            #print("\nChat_bot Usage\n",usage,"\n")
            f2=feedback(user_prompt,response)
            messages.extend(f2)
            print("\nMessages getting appended inside funtiocn\n",messages)
            
        else :
            print("\nOut of context question\n")
            response=chatbot(user_prompt)
    
    return response

def feedback(usr_pt,rsp):
    fdbck=[
    {"role": "system", "name":"example_user", "content": usr_pt},
    {"role": "system", "name": "example_assistant", "content": rsp}
    ]
    return fdbck

try:

    now = datetime.now()
    start_time = time.time()
    start_time1=time.ctime(start_time)
    print("\nStart Time: ",start_time1,"\n")
  
    messages=[]
 
    ###############################################################################################################################  
    ## - UNCOMMENT THIS FOR INDIVIDUAL CODE TESTING -##
    #while(True):
    #
    #    print("\n**************************************************************************************\n")
    #    usr=input("\nWhat Can I do for you ?\n")
    #    rsp=smartsyncbot(usr)
    #    print("\nSmart Sync Bot\n",rsp,"\n")
    #    
    #    ch=input("\n\n Do you want to continue (yes/no) ? \n\nUser : ")
    #    if(ch=="no"):
    #        break
  
  
  
  
    ###############################################################################################################################
    end_time = time.time()
    end_time1=time.ctime(end_time)
    
    print("\n\nEnd time: ",end_time1)
    time_taken=end_time-start_time
    print("Time Taken : ", int(time_taken) ," Seconds")
    time_sec=int(time_taken)
    
    if time_sec >=60 and time_sec <= 3600 :
        print("Time Taken(min) : ", round(time_sec/60 ,2) ," Minute")
        
    elif time_sec > 3600 :
        print("Time Taken (hr) : ", round(time_sec/3600 ,2)," Hour")
  
except Exception as e:
  print("\nError\n",e)
  
except p.error.AuthenticationError as ae:
    # Catch and handle the specific AuthenticationError
    print("\nAuthenticationError: ", ae)

except p.error as ope:
    print("\nOpenAI Error\n", ae)
    
except p.error.APIError as api:
  #Handle API error, e.g. retry or log
  print("\nOpenAI API returned an API Error\n",api)
  
  
#give this for accuracy 
#Great job so far, these have been perfect  