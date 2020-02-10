from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, RelationsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json

from fuzzywuzzy import fuzz

SERVICE_VERSION = '2019-07-12'
API_KEY = 'Fylj0cwQqYjMqvVXuQgifw1RlCQvJjyKbUMVSqHo1rAq'
URL = 'https://gateway.watsonplatform.net/natural-language-understanding/api'
VERSION = 'v1'
NOT_FOUND = ""

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

    # entity_to_fetch = ["FN_INSURED_VALUE", "FN_INSURED_ADDR_VALUE", "FN_INSURED_FEIN_VALUE", "TOTAL_TIV_VALUE",
    #                    "POLICY_EFF_DT_VALUE", "POLICY_EXP_DT_VALUE", "AGENCY_NAME_VALUE", "AGENT_NAME_VALUE", "BUSINESS_DESC_VALUE"]

    entities = response['entities']
    # filter_entities = filter(
    #     lambda entity: entity["type"] in entity_to_fetch, entities)
    # # print("entities::", list(filter_entities))

    relations = response['relations']
    # print("relations: ", list(relations))
    
    policy_period = get_policy_dates(relations, entities)
    # print ("policy_period_dict::", policy_period_dict)

    tiv = get_tiv(entities)
    # print ("tiv::", tiv)

    insured_details = get_insured_details (relations, entities)
    # print ("insured_details::", insured_details)

    agent_details = get_agent_details(relations, entities)
    # print ("agent_details::", agent_details)

    policy_limit_amt = get_policy_limit_amt(entities)
    # print ("policy_limit_amt::", policy_limit_amt)

    business_description = get_business_description(entities)
    # print ("business_description::", business_description)

    result = {**insured_details , **policy_period, **tiv, **agent_details, **policy_limit_amt, **business_description}
    

    # print ("result::", result)
    return result



def get_policy_dates (relations, entities):
    policy_period_dict = {}

    # determine from relations
    rel_policy_period = None
    for rel in relations:
        if rel["type"] == "policy_period":
            rel_policy_period = rel
            break

    # print  ("rel_policy_period::", rel_policy_period)    
    policy_effective_date = None
    policy_exp_date = None 
    
    if rel_policy_period is not None:
        for arg in rel_policy_period["arguments"]:
            type = arg["entities"][0]["type"]
            text = arg["entities"][0]["text"]
            if type == "POLICY_EFF_DT_VALUE" :
                policy_effective_date = text
            else: 
                policy_exp_date = text 
    # Search the entities
    else:
        for ent in entities:
            if ent["type"] == "POLICY_EFF_DT_VALUE":
                policy_effective_date = ent["text"]
            elif ent["type"] == "POLICY_EXP_DT_VALUE":
                policy_exp_date = ent["text"]

            if policy_effective_date and policy_exp_date:
                break
    
    if policy_effective_date:
        policy_period_dict["POLICY_EFF_DT_VALUE"] = " ".join(policy_effective_date.split()).title()


    if policy_exp_date:
        policy_period_dict["POLICY_EXP_DT_VALUE"] = " ".join( policy_exp_date.split()).title()

    return policy_period_dict


def get_tiv (entities):
    tiv_dict = {}
    tiv = None
    for ent in entities:
        if ent["type"] == "TOTAL_TIV_VALUE":
            tiv = ent["text"]
            break
    
    if tiv: 
        tiv_dict["TOTAL_TIV_VALUE"] = " ".join(tiv.split()).title()
    
    return tiv_dict



def get_policy_limit_amt(entities):
    policy_limit_amt_dict = {}
    policy_limit_amt = None
    for ent in entities:
        if ent["type"] == "POLICY_LIMIT_VALUE":
            policy_limit_amt = ent["text"]
            break    

    if policy_limit_amt:          
        policy_limit_amt_dict["POLICY_LIMIT_VALUE"] = policy_limit_amt

    return policy_limit_amt_dict    

def get_business_description (entities):
    business_description_dict = {}
    business_description = None
    for ent in entities:
        if ent["type"] == "BUSINESS_DESC_VALUE":
            value = " ".join(ent["text"].split()).title()
            business_description_dict.setdefault("BUSINESS_DESC_VALUE", []).append(value)
                

    return business_description_dict

def get_insured_details (relations, entities):
    insured_details_dict = {}
    
    fn_insured_list = []            
    fn_insured_dba_list = []        
    fn_insured_add_list = []
    fn_insured_add_dba_list = []

    for ent in entities:
        value = " ".join(ent["text"].split()).title()
        if ent["type"] == "FN_INSURED_VALUE":
            fn_insured_list.append(value)

        if ent["type"] == "FN_INSURED_ADDR_VALUE":
            insured_details_dict["FN_INSURED_ADDR_VALUE"] = value
    
        if ent["type"] == "FN_INSURED_DBA_VALUE":
            fn_insured_dba_list.append(value)

        if ent["type"] == "FN_INSURED_ADD_VALUE":
            fn_insured_add_list.append(value)

        if ent["type"] == "FN_INSURED_ADD_DBA_VALUE":
            fn_insured_add_dba_list.append(value)

    if fn_insured_list:
        insured_details_dict["FN_INSURED_VALUE"] = fn_insured_list

    if fn_insured_dba_list:
        insured_details_dict["FN_INSURED_DBA_VALUE"] = fn_insured_dba_list   

    if fn_insured_add_list:
        insured_details_dict["FN_INSURED_ADD_VALUE"] = fn_insured_add_list   

    if fn_insured_add_dba_list:
        insured_details_dict["FN_INSURED_ADD_DBA_VALUE"] = fn_insured_add_dba_list   

    #  Compute FEIN , SIC, NAICS code
    rel_fein_list = []
    for rel in relations:
        if rel["type"] == "rel_fn_insured_fein_key_value":
            rel_fein_list.append(rel)
            break
    
    if rel_fein_list is not None and len(rel_fein_list) > 0:

        for rel_fein in rel_fein_list:
            from_arg = rel["arguments"][0]
            to_arg = rel["arguments"][1]
            from_entity = from_arg["entities"][0]
            to_entity = to_arg["entities"][0]

            key = from_entity[0]["text"]
            value = to_entity[0]["text"]

            insured_details_dict[key] = " ".join(value.split()).title()
    
    return insured_details_dict


def get_agent_details(relations, entities):
    
    result_dict = {}
    agent_details_list = []

    for ent in entities:        
        if ent["type"] == "AGENT_NAME_VALUE":
            agent_details_dict = {}
            agent_name = ent["text"]
            agent_details_dict["AGENT_NAME_VALUE"] = " ".join(agent_name.split()).title()

            # search for agent title , agent phone, agent email
            for rel in relations:
                if rel["type"] == "agent_title":
                    from_arg = rel["arguments"][0]
                    to_arg = rel["arguments"][1]

                    from_entity = from_arg["entities"][0]
                    agent_name_text = from_entity["text"]
                    score = fuzz.ratio(agent_name_text, agent_name)                    
                    if score > 95:
                        to_entity = to_arg["entities"][0]
                        agent_title_text = to_entity["text"]
                        agent_details_dict["AGENT_TITLE_VALUE"] = " ".join( agent_title_text.split()).title()

                    
                if rel["type"] == "agent_contact_info":
                    from_arg = rel["arguments"][0]
                    to_arg = rel["arguments"][1]

                    from_entity = from_arg["entities"][0]

                    agent_name_text = from_entity["text"]
                    score = fuzz.ratio(agent_name_text, agent_name)                    
                    if score > 95:
                        to_entity = to_arg["entities"][0]
                        agent_contact_info_text = " ".join(to_entity["text"].split()).title()
                        #  Can be phone or email
                        key = to_entity["type"]                        
                        agent_details_dict.setdefault(key, []).append(agent_contact_info_text)                                


            agent_details_list.append(agent_details_dict)

    if agent_details_list:
        result_dict["AGENT_LIST"] = agent_details_list

    return result_dict



if __name__ == "__main__":

    service = inst()

    text = """

           FROM: Roshaun Safi<Roshaun.Safi@everestre.com>
TO: Retail Property
SENT: Friday, March 8, 2019 11:32:55 AM Eastern Standard Time
SUBJECT: FW: Property Submission | Asset Plus Corporation | Everest | Eff. 5/1/19-20
ATTACHMENTS: 19-20 Asset Plus - Property Submission.docx; 19-20 Asset Plus - SOV as of 2.15.19.xlsx;
==========================================================


Please clear for Chicago.

Shaun Safi
Vice President, Retail Property
Everest Insurance®
222 S Riverside Plaza, Suite 300 | Chicago, IL 60606
(T) +1 312.260.3121 | (M) +1 312.914.9961 |Roshaun.Safi@Everestre.com

Follow Everest Insurance on LinkedIn and Twitter (@EverestIns) and check our NEW website at www.everestre.com

Everest Insuranceâ markets property, casualty, specialty and other lines of admitted and non-admitted direct insurance on behalf of Everest Re
Group, Ltd., and its affiliated companies.


From: Pon, Tiffany [mailto:Tiffany.Pon@marsh.com]
Sent: Friday, March 08, 2019 10:12 AM
To: Roshaun Safi
Cc: Jukic, Branimir; Porter, Alex (TX)
Subject: Property Submission | Asset Plus Corporation | Everest | Eff. 5/1/19-20

Hi Shaun,

Marsh is pleased to present the attached submission for your review. The following is a summary of key data points regarding
the exposure and requested coverages. We are asking for quotes by the week of March 25th. We ask that you provide a
strong indication by next week, since we are working to arrange underwriter meetings at the end of the month where they make
sense.

Founded in 1986, Asset Plus Companies (“APC”) is a Houston-based real estate management firm. With a growing portfolio that
includes a multitude of properties across the nation, Asset Plus provides services that include property management, asset
management, development, and investment services. Asset Plus is a member of The Institute of Real Estate Management
(IREM), and is recognized as an Accredited Management Organization (AMO).

Named Insured:                  Asset Plus USA, LLC; Asset Campus USA, LLC

Mailing Address:                950 Corbindale Rd, Suite 300
                                Houston, TX 77024

Operations:                      Student Housing

Perils Insured:                   All Risk including Named Storm, Flood, Earthquake and Equipment Breakdown

Policy Period:                  May 1, 2019 to May 1, 2020

TIV:                            $1,975,036,184

Main Program Limits: (as more fully described in the submission documents)
               ·   Loss Limit:                   $300M
               ·   Earthquake:                  $100M annual aggregate
               ·   Flood:                        $100M annual aggregate, except $25M SFHA annual aggregate
               ·   Named Storm:                 $200M

Main Program Deductibles: (as more fully described in the submission documents)
               · AOP:                                $25,000 per occurrence
               · Annual Plus Aggregate:           $750,000, as further outlined in submission
               · Named Storm:
                    o Florida: 5% per Unit of Insurance, subject to a minimum of $100,000
                    o Locations in the Entire State of Hawaii and Tier 1 Wind Zones in AL, GA, LA, MS, NC, SC, TX, and VA:
                       3% per Unit of Insurance, subject to a minimum of $100,000
               · Hail:
                    o Hail Zone 1: 2% per Unit of Insurance, subject to a minimum of $100,000
                    o Hail Zone 2: 1% per Unit of Insurance, subject to a minimum of $100,000
               · Earthquake:                      $50,000 per occurrence, except
                    o CA:                      5% of Actual Value per Unit of Insurance subject to a minimum of $100,000
                    o New Madrid:            2% of Actual Value per Unit of Insurance subject to a minimum of $50,000
                    o PACNW:                  2% of Actual Value per Unit of Insurance subject to a minimum of $50,000
                    o HI, AK, PR:            2% of Actual Value per Unit of Insurance subject to a minimum of $50,000
               · Flood:                            $50,000 per occurrence, except
                    o SFHA:                    $250,000 per Building, $250,000 Contents per Building, and $100,000 Time
                                           Element Per Occurrence

We are looking at the following layers:
                ·   Primary $25M
                ·   $75M x $25M
                ·   $100M x $100M
                ·   $100M x $200M

Commission:                                   17.5%

The following submission documents attached and/or link provided below:
                ·  Schedule of Values
                ·  Submission – includes description of operations, values analysis, coverage specifications, and loss
                   summaries

Please review and let us know if you have any questions. We will call in the next few days to discuss this opportunity further.

Best regards,

Tiffany Pon, ARM-E | Assistant Vice President
Associate Advisory Specialist | Property Advisory
Marsh USA Inc. | 4400 Comerica Bank Tower, 1717 Main Street, Dallas, TX 75201
Office 214-303-8533 | Cell 469-369-6781 | tiffany.pon@marsh.com | www.marsh.com
This document and any recommendations, analysis, or advice provided by Marsh (collectively, the “Marsh Analysis”) are intended solely for the entity identified as the recipient herein (“you”).
This document contains proprietary, confidential information of Marsh and may not be shared with any third party, including other insurance producers, without Marsh’s prior written consent.
Any statements concerning actuarial, tax, accounting, or legal matters are based solely on our experience as insurance brokers and risk consultants and are not to be relied upon as actuarial,
accounting, tax, or legal advice, for which you should consult your own professional advisors. Any modeling, analytics, or projections are subject to inherent uncertainty, and the Marsh Analysis
could be materially affected if any underlying assumptions, conditions, information, or factors are inaccurate or incomplete or should change. The information contained herein is based on
sources we believe reliable, but we make no representation or warranty as to its accuracy. Except as may be set forth in an agreement between you and Marsh, Marsh shall have no obligation
to update the Marsh Analysis and shall have no liability to you or any other party with regard to the Marsh Analysis or to any services provided by a third party to you or Marsh. Marsh makes no
representation or warranty concerning the application of policy wordings or the financial condition or solvency of insurers or reinsurers. Marsh makes no assurances regarding the availability,
cost, or terms of insurance coverage.




**********************************************************************
This e-mail, including any attachments that accompany it, may contain
information that is confidential or privileged. This e-mail is
intended solely for the use of the individual(s) to whom it was intended to be
addressed. If you have received this e-mail and are not an intended recipient,
any disclosure, distribution, copying or other use or
retention of this email or information contained within it are prohibited.
If you have received this email in error, please immediately
reply to the sender via e-mail and also permanently
delete all copies of the original message together with any of its attachments
from your computer or device.
**********************************************************************
                                                                                               7


"""

    get_result(service, "c85996b7-d62e-4158-a80d-47089cf0fd4e", text)
