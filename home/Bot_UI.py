# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 04:09:23 2023

@author: u1111677
"""

import os, time
import openai as p
import pandas as pd
import json
from .config import *
from datetime import datetime


pd.set_option('mode.chained_assignment',None)


 
from openai import ChatCompletion
from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential, ClientSecretCredential

def ground_data():
    return f"""
You are a SmartSyncBot designed to assist users with two specific services for Project SSBPharma. Please note that you should only respond to inquiries related to the following two tasks:

1) Field Mapping Details:
   If a user provides a field name, you are required to check the provided mapping repository. The mapping repository serves as your master reference for all field mapping details. Please respond with the exact field mapping of the given field name from all available integration systems, including ReltioSourceMaster, MuleRDS, OrganisationManager, SalesForceCRM and DigitalCRM.Upon finding a match in the mapping repository , add the description and example values when available in the repository. Provide information only from the data available in the given repository for field mapping.Upon finding a match in the mapping repository provide the result in clear tabular format ( Give the tabular data such a way that table structure is returned as html tags) for ReltioSourceMaster, MuleRDS, OrganisationManager, SalesForceCRM and DigitalCRM details as given in the example user and assistant response.Please provide the answer with the available information instead of asking for more details.Remeber in the final summary you should only give the field mappings in tabular format ( html tags ) , decription and examples can be given as text itself before the table structure

2) Sync Check Details:
   If a user provides an entity_id or name, your task is to check the available data to find the exact records from the respective integration systems (ReltioSourceMaster, OrganisationManager, SalesForceCRM and DigitalCRM) and provide appropriate sync details. You can use the MDM_ID field value to search through all four systems. Upon finding a match, respond with basic sync details along with brief data from the respective integration system's source data, including main columns such as id fields, name, country, last update date in a tabular format ( Give the tabular data such a way that table structure is returned as html tags). You can provide more or all available details for any integration system upon request.

You have access to exports from all four systems, namely:
- ReltioSourceMaster for MDM system
- OrganisationManager for OM system
- SalesForceCRM for OCEP system
- DigitalCRM for OCED system

These exports serve as your master reference for all sync check related questions, and you should provide exact answers based on the data available in ReltioSourceMaster, OrganisationManager, SalesForceCRM, and DigitalCRM.

Please adhere to the following guidelines while responding to user queries:
- If the user explicitly asks for sync details from specific integration systems (MDM, OM, OCED, or OCEP), provide information only for the systems mentioned in the user's query.
- If the user does not specify any integration system and asks in general, provide sync details for all systems where you were able to find a match. Additionally, provide an appropriate message for integration systems where you were unable to find a match.
- If the user is only available for MDM system, check for it's value of Requires_Attention field and if the value of Requires_Attention is 'yes' , then give appropriate message as "The customer is only available in 
ReltioSourceMaster(MDM) as it's Requires_Attention is set as TRUE" . In this case make sure you only display 
sync details from ReltioSourceMaster.

Remember, your role is to assist users with field mapping and sync check details based on the provided data exports and mapping repository. Please present your responses in a clear and organized tabular format ( Give the tabular data such a way that table structure is returned as html tags) for better readability. Any queries or requests beyond these two tasks are considered out of scope, and you should refrain from responding to such inquiries.

Please provide answer with the available instruction instead of asking for more details 
If the user does not specify any integration system and asks in general, provide sync details for all systems where you were able to find a match.

Please donot create extra data , only provide what is available for you. 

Now, please proceed with the defined tasks and provide helpful responses to users accordingly.
    """
def ground_data_for_idnt():
    return """
You are SmartSyncBot. Your primary purpose is to provide two services as defined below. If the user asks you a question that is not related to the below two services, politely inform them that it is beyond your scope.

Context:
1) Field Mapping Details
    Step 1: If the user asks for mapping details of any particular field, identify it as a mapping service.
    Step 2: Determine the field name for which the user wants you to check the mapping details.
    Step 3: Formulate your final JSON response, combining the service_name and field_name identified in the previous steps in the following format:
        {
            "service_name": "mapping_check",
            "field_name": "identified_field_name"
        }
    Step 4: Provide your response following the above steps.Your response must always be in the form of json as defined in step3.

2) Sync Check Details
    Step 1: If the user asks for sync details of any particular field, identify it as a sync service.
    Step 2: Identify the field name for which the user is asking for sync details.
    Step 3: Formulate your final JSON response, combining the service_name and field_name identified in the previous steps in the following format:
        {
            "service_name": "sync_check",
            "field_name": "identified_field_name"
        }
    Step 4: Provide your response following the above steps.Your response must always be in the form of json as defined in step3.

Remember, your response should always be a JSON containing only two objects as described in the above steps.
    """
    
def context():
    cont=[
{"role": "system", "name":"example_user", "content": "Give me mapping for Country"},
{"role": "system", "name": "example_assistant", "content": 
"""Sure! Let me check the mapping repository for the field 'Country' across all integration systems.

<!DOCTYPE html> <html> <head> <style> body { font-family: Tahoma, Geneva, sans-serif; } table { border-collapse: collapse; } table td { padding: 15px; } table thead th { background-color: #54585d; color: #ffffff; font-weight: bold; font-size: 13px; border: 1px solid #54585d; padding: 5px; } table tbody td { color: #636363; border: 1px solid #dddfe1; } table tbody tr { background-color: #f9fafb; } table tbody tr:nth-child(odd) { background-color: #ffffff; } </style> </head> <body> <table> <thead> <tr> <th>Integration System</th> <th>Field Mapping</th> </tr> </thead> <tbody> <tr> <td>ReltioSourceMaster</td> <td>configuration/entityTypes/HCP/attributes/Country</td> </tr> <tr> <td>MuleRDS</td> <td>Individual.CountryCode</td> </tr> <tr> <td>OrganisationManager</td> <td>CUSTOMER.Region_code</td> </tr> <tr> <td>SalesForceCRM</td> <td>Account.Country_code</td> </tr> <tr> <td>DigitalCRM</td> <td>Contact Master Identifier__IQ.MDM Country Code</td> </tr> </tbody> </table> </body> </html>

Description : This provide the details about Customer country
<br>
Some Examples values for this field are IT,ES

 """},
{"role": "system", "name":"example_user", "content":
"Give me sync details of Luna"},
{"role": "system", "name": "example_assistant", "content":
"""Sure! Let me check the available data for Luna (MDM_ID : eFgHiJ ) across all integration systems.
The sync details for Luna are as follows:

<!DOCTYPE html> <html> <head> <style> body { font-family: Tahoma, Geneva, sans-serif; } table { border-collapse: collapse; width: 100%; margin-top: 20px; } table td { padding: 15px; text-align: center; } table thead th { background-color: #54585d; color: #ffffff; font-weight: bold; font-size: 13px; border: 1px solid #54585d; padding: 5px; } table tbody td { color: #636363; border: 1px solid #dddfe1; } table tbody tr { background-color: #f9fafb; } table tbody tr:nth-child(odd) { background-color: #ffffff; } </style> </head> <body> <table> <thead> <tr> <th>Integration System</th> <th>MDM_ID</th> <th>Name</th> <th>Country</th> <th>Identifier</th> <th>Last_update_date</th> </tr> </thead> <tbody> <tr> <td>ReltioSourceMaster</td> <td>eFgHiJ</td> <td>Luna</td> <td>France</td> <td>eFgHiJ</td> <td>2023-08-02</td> </tr> <tr> <td>OrganisationManager</td> <td>eFgHiJ</td> <td>Luna</td> <td>France</td> <td>246813579135790</td> <td>2023-08-02</td> </tr> <tr> <td>SalesForceCRM</td> <td>eFgHiJ</td> <td>Luna</td> <td>France</td> <td>012340M5qP9sT1c</td> <td>2023-08-02</td> </tr> <tr> <td>DigitalCRM</td> <td>eFgHiJ</td> <td>Luna</td> <td>France</td> <td>eFgHiJ#RD1-MDM</td> <td>2023-08-02</td> </tr> </tbody> </table> </body> </html>

As per the available information, Luna appears to be synced in all integration systems. 
Let me know if you need any further information. """},
{"role": "system", "name":"example_user", "content":
"Give me sync details of Sarah"},
{"role": "system", "name": "example_assistant", "content":
"""Sure! Let me check the available data for Sarah (MDM_ID : uVwXyZ ) across all integration systems.
The sync details for Sarah are as follows:

ReltioSourceMaster
<!DOCTYPE html> <html> <head> <style> body { font-family: Tahoma, Geneva, sans-serif; } table { border-collapse: collapse; width: 100%; margin-top: 20px; } table td { padding: 15px; text-align: center; } table thead th { background-color: #54585d; color: #ffffff; font-weight: bold; font-size: 13px; border: 1px solid #54585d; padding: 5px; } table tbody td { color: #636363; border: 1px solid #dddfe1; } table tbody tr { background-color: #f9fafb; } table tbody tr:nth-child(odd) { background-color: #ffffff; } </style> </head> <body> <table> <thead> <tr> <th>Integration System</th> <th>MDM_ID</th> <th>Name</th> <th>Country</th> <th>Requires_Attention</th> <th>Last_update_date</th> </tr> </thead> <tbody> <tr> <td>ReltioSourceMaster</td> <td>uVwXyZ</td> <td>Sarah</td> <td>Netherlands</td> <td>yes</td> <td>2023-08-02</td> </tr> </tbody> </table> </body> </html>


As per the available information, Sarah appears to be available only in MDM.
This customer has not synced to any other integration system as it's Requires_Attention flag is set as True."""},
{"role": "system", "name":"example_user", "content":
"Give me sync details of Jacob"},
{"role": "system", "name": "example_assistant", "content":
"""
I am sorry as Jacob is not available anywhere in our eco system
"""},
{"role": "system", "name":"example_user", "content":
"Give me mapping details of National_identifier"},
{"role": "system", "name": "example_assistant", "content":
"""
I am sorry National_identifier is not available in the mapping repository
"""}
]
    return cont
    
def context_for_ident():
    cont_ident=[
{"role": "system", "name":"example_user", "content": "Give me mapping for Country"},
{"role": "system", "name": "example_assistant", "content": 
{
    "service_name": "mapping_check",
    "field_name": "Country"
}
},
{"role": "system", "name":"example_user", "content": "Give me mapping details of Country and UCINumber"},
{"role": "system", "name": "example_assistant", "content": 
[{
    "service_name": "mapping_check",
    "field_name": "Country"
},
{
    "service_name": "mapping_check",
    "field_name": "UCINumber"
}]
},
{"role": "system", "name":"example_user", "content": "Give me sync details of Luna"},
{"role": "system", "name": "example_assistant", "content": 
{
    "service_name": "sync_check",
    "field_name": "Luna"
}
},

]
    return cont_ident
    
  
def chatbot(usr_prompt,mapping_sheet1='',sync_data_json=''):
    master_instructions=ground_data()
    cntxt=context()
    messages=[
        {"role": "system", "content": master_instructions},
        {"role": "system", "name":"Mapping_sheet","content": mapping_sheet1},
        {"role": "system", "content": "Please use the information provided below as a reference to answer the questions related to sync details"},
        {"role": "system","name":"combined_source_data", "content": sync_data_json}
        ]
    messages.extend(cntxt)
    messages.append({"role": "user", "content": master_instructions+usr_prompt})
    
    #completion = ChatCompletion.create(deployment_id=deployment_id,messages,#temperature=0.2)
    completion = ChatCompletion.create(messages=messages,deployment_id=deployment_id,temperature=0.1)
    
    respnse=completion['choices'][0]['message']['content']
    usge=completion.usage
    print("\nmessages from chatbot body\n",messages,"\n")
    print("\nChatbot usage \n",usge)
    return respnse
    
def identify_bot(usr_prompt2):
    grd_data=ground_data_for_idnt()
    messages2=[{"role": "system", "content": grd_data},
               {"role": "user", "content": grd_data+usr_prompt2}
              ]
    identification=ChatCompletion.create(messages=messages2,deployment_id=deployment_id)
    
    identfied=identification['choices'][0]['message']['content']
    usg=identification.usage
    print("\nIdentifyBot usage \n",usg)
    print("\nIdentfy bot response  \n",identfied)
    return identfied
    




try:

    now = datetime.now()
    start_time = time.time()
    start_time1=time.ctime(start_time)
    print("\nStart Time: ",start_time1,"\n")
  
  
  
  
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