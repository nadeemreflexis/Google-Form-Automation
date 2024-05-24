"""
INTERNAL DO NOT MODIFY
"""

import json
import os, shutil, re
import sys
import traceback
import xml.etree.ElementTree as ET

"""
copy kwargs from wherever they are in user project to ./assets/ dir
kwargs can be 'chrome_logs' 'testng_report' and 'checkstyle_report'
"""
def copy_and_arrange(**kwargs):
    assets_dir = os.path.join('assesment','assets')
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    for key, src_path in kwargs.items():
        if os.path.exists(src_path):
            dest_path = os.path.join(assets_dir, os.path.basename(src_path))
            shutil.copy(src_path, dest_path)
        else:
            print(f"Source file {src_path} not found for {key}.")

"""
read kwargs['checkstyle_report'] and create a json report
assess on the basis of kwargs['instructions'] -> inst

initialize empty dict report

for each of keys comments, waits, sleep, sopls in inst (keys):
    check if occurances of key['indicator'] occurs between key['min_limit'] and key['max_limit']
    unless key['min/max limit'] is None, in which case test for the one that is not None
        if true and key['is_enabled'] is true, report[key['out']] = 'TEST_STATUS_SUCCESS'
        else if false and key['is_enabled'] is true, report[key['out']] = 'TEST_STATUS_FAILURE'
        else report[key['out']] = 'TEST_STATUS_SKIPPED'

        Note: 'out' is in format `You used {} waits, requirement is between {} > {}`, needs to be
            populated with occurances, min_limit and max_limit
return report
"""
def checkstyle_assess(**kwargs):
    report = {}
    hints = []
    
    try:
        with open(kwargs['checkstyle_report'], 'r') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}

    instructions = kwargs.get('instructions', [])
    for inst in instructions:
        if not inst['is_enabled']:
            report[inst['out'].format('NA', inst['min_limit'], inst['max_limit'])] = 'TEST_STATUS_SKIPPED'
            continue

        occurrences = len(re.findall(inst['indicator'], content))
        
        min_limit = inst.get('min_limit', None)
        max_limit = inst.get('max_limit', None)
        
        if min_limit is not None and max_limit is not None:
            test_result = min_limit <= occurrences <= max_limit
        elif min_limit is not None:
            test_result = occurrences >= min_limit
        elif max_limit is not None:
            test_result = occurrences <= max_limit
        else:
            test_result = True

        if test_result:
            report[inst['out'].format(occurrences, min_limit if min_limit is not None else 'No limit', max_limit if max_limit is not None else 'No limit')] = 'TEST_STATUS_SUCCESS'
        else:
            report[inst['out'].format(occurrences, min_limit if min_limit is not None else 'No limit', max_limit if max_limit is not None else 'No limit')] = 'TEST_STATUS_FAILURE'
            hints.append(inst['out'].format(occurrences, min_limit if min_limit is not None else 'No limit', max_limit if max_limit is not None else 'No limit').split('.')[1])

    return report, hints

"""
taken from generatefilteredlogs (previously written script)
"""
def construct_log_json(log_text):
    LOG= {
    "actions":[]
    }
    log_frame=""
    log_object_frame={"COMMAND":None, "RESPONSE":None}
    selector = None
    for line in open(log_text):
        if('[INFO]' in line and 'COMMAND' in line ):
            if ("COMMAND ExecuteScript" not in str(log_object_frame)):
                LOG["actions"].append(log_object_frame)
            selector = "COMMAND"
            log_object_frame={"COMMAND":None, "RESPONSE":None}
            log_frame=""
        elif('[INFO]' in line and 'RESPONSE' in line ):
            selector = "RESPONSE"
        

        if(selector is not None):
            if(line.startswith('[') and log_frame == "" ):
                log_frame = log_frame+line
                log_object_frame[selector]=log_frame
            elif(line.startswith('[') and log_frame != ""):
                log_frame=""
                selector = None
            else:
                log_frame=log_frame+line
                log_object_frame[selector]=log_frame
    json.dump(LOG , open(os.path.join('assesment','assets','filtered_logs.json'),'w+'),indent=4)
    return LOG

"""
read kwargs['log_path'] and create a json report
assess on the basis of log_assessment_instruction -> kwargs['chrome_log_assessment']

for each val in log_assessment_instruction['validations'] check
    if in the entire document of log, there is a key val['object_notation']('COMMAND'/'Response') that contains/does not 
    contain (depending on val['operation']) value val['expected_value']

    if log_assessment_instruction['join'] is "AND", then all should be true, else if "OR" then only 1 value needs be true

if passed, return a key value pair response[log_assessment_instruction['success_out']] = "TEST_STATUS_SUCCESS"
else "TEST_STATUS_FAILURE"
"""
def chromelog_validation_assess(**kwargs):
    log_path = kwargs.get('log_path')
    chrome_log_assessments = kwargs.get('chrome_log_assessment')
    if not log_path or not chrome_log_assessments:
        print(f"Internal error, check instructions or connect with support - {str(e)}")
        quit()
    
    test_suite=kwargs.get('test_suite')
    hints = []

    try:
        with open(log_path, 'r') as file:
            log_content = file.read()
        logs = json.loads(log_content) 
        validations = chrome_log_assessments

        response = {}

        for validation in validations:
            join_type = validation['join']
            results = []

            for val in validation['validations']:
                operation = val['operator']
                object_notation = val['object_notation'] 
                expected_value = val['expected_value']
                
                validation_passed = False
                for entry in logs['actions']:

                    if operation == 'contains' and expected_value in safe_string_fetch(entry[object_notation]):
                        validation_passed = True
                    elif operation == 'does not contain' and expected_value not in safe_string_fetch(entry[object_notation]):
                        validation_passed = True

                    if validation_passed and join_type == "OR":
                        break

                results.append(validation_passed)

            if join_type == "AND":
                final_result = all(results)
            else: 
                final_result = any(results)

            result_key = validation['success_out']
            if final_result:
                response[f"{test_suite}.{result_key}"]= "TEST_STATUS_SUCCESS" 
            else:
                response[f"{test_suite}.{result_key}"]= "TEST_STATUS_FAILURE"
                hints.append(validation['hint'])
        return response, hints

    except Exception as e:
        print(f"Internal error, check instructions or connect with support - {str(e)}")
        quit()
    
"""
read report -> kwargs['testng_report_path'] and create a json report
assess on the basis of testng_instructions -> kwargs['testng_assessment']

for each of test -> kwargs['testng_assessment']
    if test['is_enabled'] is true, then
        look at all of report (xml) and look for test-method element with attribute `name` and 
        if `status` is PASS 
            then send test['chrome_log_assessment'] to method chromelog_validation_assess 
            with path to filtered_log -> kwargs['filtered_log'], store the data as test['test_case_fe'] = result_of_chromelog_validation
        else if `status` is FAIL
            test['test_case_fe'] = "TEST_STATUS_FAILURE"
    else
        test['test_case_fe'] = "TEST_STATUS_SKIPPED"
"""
def testng_validation_assess(**kwargs):
    testng_report_path = kwargs.get('testng_report_path')
    testng_assessment = kwargs.get('testng_assessment')
    filtered_log_path = kwargs.get('filtered_log')
    response = {}
    hints_all = []

    try:
        tree = ET.parse(testng_report_path)
        root = tree.getroot()
        for test in testng_assessment:
            if not test['is_enabled']:
                response[test['test_case_fe']] = "TEST_STATUS_SKIPPED"
                continue
            tree = root.findall(".//test-method[@name='%s']" % test['testng_test_name'])
            if not tree:
                result = {f"{test['test_case_fe']}.TestNG Test Method '{test['testng_test_name']}' is not Implemented":"TEST_STATUS_FAILURE"}
                hints = [f"Implement TestNG Test Method '{test['testng_test_name']}' for assessment to register it!"]
                response = {**response, **result}
                hints_all+=hints
                continue
            for test_method in tree:
                status = test_method.get('status')
                if status == 'PASS':
                    result, hints = chromelog_validation_assess(
                        log_path=filtered_log_path,
                        chrome_log_assessment=test['chrome_log_assessment'],
                        test_suite=test['test_case_fe']
                    )
                elif status == 'FAIL':
                    response[test['test_case_fe']] = "TEST_STATUS_FAILURE"
                
                response = {**response, **result}
                hints_all+=hints
        return response, hints_all
    except Exception as e:
        print(f"Internal error, check instructions or connect with support - {str(e)}")
        quit()


    return response

# Utility
def safe_string_fetch(val):
    return val if val != None else ""

# main call
if __name__ == "__main__":
    try:
        sys.argv[1]
        sys.argv[2]
        sys.argv[3]
        sys.argv[4]
    except:
        print("Oops! Do not modify the run assessment file!")
        quit()
    
    checkstyle_file = sys.argv[1]
    chromelog_file = sys.argv[2]
    testngreport_file = sys.argv[3]
    
    try:
        copy_and_arrange(checkstyle_file=checkstyle_file,chromelog_file=chromelog_file,testngreport_file=testngreport_file)
    except Exception as e:
        pass

    checkstyle_path = os.path.join(os.getcwd(),'assesment','assets',os.path.basename(checkstyle_file))
    chromelog_path = os.path.join(os.getcwd(),'assesment','assets',os.path.basename(chromelog_file))
    testngreport_path = os.path.join(os.getcwd(),'assesment','assets',os.path.basename(testngreport_file))

    with open(sys.argv[4], 'r') as file:
        assessment_instructions = json.load(file)

    checkstyle_result, hints_checkstyle = checkstyle_assess(checkstyle_report=checkstyle_path, 
                                          instructions=assessment_instructions['quality_eval'])
    
    construct_log_json(chromelog_path)
    log_path = os.path.join(os.getcwd(),'assesment','assets','filtered_logs.json')

    result, hints = testng_validation_assess(testng_report_path=testngreport_path, 
                                      filtered_log=log_path, 
                                      testng_assessment=assessment_instructions['instruction_set'])
    
    result = {**checkstyle_result, **result}
    hints+=hints_checkstyle

    json.dump(result,open("assesment_result.json",'w+'), indent=4)
    print("\033[33m\nAssessment Successful.\033[0m")
    if len(hints)!=0:
        print("\033[91m\nHere are some violations to check in automation:\033[0m")
        counter = 1
        for i in hints:
            print(f"\t{counter} - {i}")
            counter = counter+1
        print()
    else:
        print("\033[32m\nAll Checks Passed! Please commit and push code.\033[0m")