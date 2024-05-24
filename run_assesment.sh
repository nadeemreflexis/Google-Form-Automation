# Usage
# For just assessment from filtered logs (cloud assessment) - ./run_assesment.sh --from-filtered-log
# For generating filtered logs first before assessment (local assessment) - ./run_assesment.sh

if [[ "$1" != "--from-filtered-log" ]] 
then 
    python3 assesment/assess.py build/reports/checkstyle/test.xml build/chromedriver.log build/reports/tests/test/testng-results.xml assesment/INSTRUCTIONS.json
else
    python3 assesment/assess.py assesment/assets/test.xml assesment/assets/chromedriver.log assesment/assets/testng-results.xml assesment/INSTRUCTIONS.json
fi