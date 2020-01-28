from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, RelationsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
from fuzzywuzzy import fuzz

SERVICE_VERSION = '2019-07-12'
API_KEY = 'Fylj0cwQqYjMqvVXuQgifw1RlCQvJjyKbUMVSqHo1rAq'
URL = 'https://gateway.watsonplatform.net/natural-language-understanding/api'
VERSION = 'v1'


def inst():

    authenticator = IAMAuthenticator(API_KEY)
    service = NaturalLanguageUnderstandingV1(
        version=SERVICE_VERSION, authenticator=authenticator)
    service.set_service_url(URL)

    return service


def get_result(service, model_id, text_val):
    response = service.analyze(
        text=text_val,
        features=Features(entities=EntitiesOptions(model=model_id),
                          relations=RelationsOptions(model=model_id)
                          )).get_result()

    entity_to_fetch = ["FN_INSURED_VALUE", "FN_INSURED_ADDR_VALUE", "FN_INSURED_FEIN_VALUE", "TOTAL_TIV_VALUE",
                       "POLICY_EFF_DT_VALUE", "POLICY_EXP_DT_VALUE", "AGENCY_NAME_VALUE", "AGENT_NAME_VALUE", "BUSINESS_DESC_VALUE"]

    entities = response['entities']
    filter_entities = filter(
        lambda entity: entity["type"] in entity_to_fetch, entities)
    # print("entities::", list(filter_entities))

    relations = response['relations']
    # print("relations: ", relations)

    result_dict = {}
    # value_dict = {}

    insured_info_dict = {}
    agent_info_list = []

    for entity in filter_entities:
        key = entity["type"]
        value = entity["text"]
        print("########value::", value)
        # result_dict.setdefault(key, []).append(value)

        if key == "FN_INSURED_VALUE":
            insured_info_dict.setdefault("FN_INSURED_VALUE", []).append(value)
        
        if key == "AGENT_NAME_VALUE":
            agent_info_dict = get_agent_info (relations, value)
            agent_info_list.append(agent_info_dict)
        
        if key == "BUSINESS_DESC_VALUE":
            insured_info_dict.setdefault("BUSINESS_DESC_VALUE", []).append(value)

        if key == "TOTAL_TIV_VALUE":
            insured_info_dict.setdefault("TOTAL_TIV_VALUE", []).append(value)      

        # Calculate policy date
        # 
        #       

    result_dict.setdefault(
        "AGENT_INFO", []).append(agent_info_list)

    print("result_dict::{}", result_dict)

    return result_dict

# Returns the agent info
def get_agent_info (relations, value):
    agent_info_list = []
    agent_info_dict = {}
    agent_info_dict["AGENT_NAME_VALUE"] = value

    filter_relations_by_agent_title = list(filter(
        lambda relation: relation["type"] in "agent_title", relations))

    filter_relations_by_agent_phone = list(filter(
        lambda relation: relation["type"] in "agent_contact_info", relations))

    # 1... search relations to get the agent title    
    if filter_relations_by_agent_title is not None:        
        found_relation = None
        for relation in filter_relations_by_agent_title:
            arguments_arr = relation["arguments"]
            for argument in arguments_arr:
                entities_arr = argument["entities"]
                # print("entities_arr", entities_arr)
                for entity in entities_arr:
                    agent_name_text = entity["text"]
                    score = fuzz.ratio(agent_name_text, value)
                    # print("agent_name_text::{} value::{} score::{}", {agent_name_text,value, score})
                    if score > 95:
                        found_relation = relation
                        agent_title = found_relation["arguments"][1]["text"]
                        print("agent_title", agent_title)
                        agent_info_dict["AGENT_TITLE_VALUE"] = agent_title
                        
                        break

    # 2... search relations to get the agent contact
    if filter_relations_by_agent_phone is not None:        
        found_relation = None
        for relation in filter_relations_by_agent_phone:
            arguments_arr = relation["arguments"]
            for argument in arguments_arr:
                entities_arr = argument["entities"]
                # print("entities_arr", entities_arr)
                for entity in entities_arr:
                    agent_name_text = entity["text"]
                    score = fuzz.ratio(agent_name_text, value)
                    # print("agent_name_text::{} value::{} score::{}", {agent_name_text,value, score})
                    if score > 95:
                        found_relation = relation
                        agent_contact_key = found_relation["arguments"][1]["entities"][0]["type"]
                        agent_contact = found_relation["arguments"][1]["entities"][0]["text"]
                        print("agent_contact", agent_contact)
                        agent_info_dict.setdefault(
                            agent_contact_key, []).append(agent_contact)
                        

                        break

    
    return agent_info_dict

if __name__ == "__main__":

    service = inst()

    text = """2019 PROPERTY SUBMISSION                                                  BLUE BELL CREAMERIES, L.P.




1
CONFIDENTIALITY NOTICE
This submission contains information, some of which is in summary form, which may be useful
to underwriters in analyzing the Insured's risks. The information contained herein does not
purport to represent or explain all of the Insured's activities or exposures, which may not be
possible in any event given its size, complexity and diversity.

The underwriting information you are receiving, and any supplemental information that may be
provided to you at any time, whether orally or in writing, includes confidential information of the
Insured, and should be treated as such by you and your company.

We feel this submission will provide you with the needed information in order to provide your
quotation on this Property Insurance Program and look forward to receiving your quote no later
than the week of February 1st and/or sooner would be greatly appreciated.

Marsh Contacts:

Randy Amberg
Property Advisory Specialist
Phone 214-303-8255

Tiffany Pon
Associate Advisory Specialist
Phone 214-303-8533

Alex Porter
Property TRAC Associate
Phone 214-303-8057




MARSH """

    get_result(service, "0e2be798-0ef3-426d-a01e-c5110f0ecd5e", text)
