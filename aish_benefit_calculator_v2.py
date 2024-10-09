import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
import requests
import yaml
from yaml.loader import SafeLoader

def render_calculation_results(aish_living_allowance, child_supplement, employment_income_deduction, family_benefit_amount):
  # Page title
  st.subheader("Calculation Results")

  # Benefits Section
  st.write("### Benefits")

  # Create two columns: Item and Amount
  col1, col2 = st.columns([2, 1])

  # First row - AISH Living Allowance
  col1.write("AISH Living Allowance (Single or Family)")
  col2.write(f"${aish_living_allowance:,}")

  # Second row - Child Supplement
  col1.write("Child Supplement")
  col2.write(f"${child_supplement:,}")

  # Deductions Section
  st.write("### Deductions")

  # Create two columns again
  col1, col2 = st.columns([2, 1])

  # First row - Employment Income above exemption
  col1.write("Employment Income above exemption")
  col2.write(f"${employment_income_deduction:,}")

  # Net Benefit Section
  col1.write("### Net Benefits")
  col1, col2 = st.columns([2, 1])

  # First row - Employment Income above exemption
  col1.write("**Net Benefits**")
  col2.write(f"**${family_benefit_amount:,}**")
 
with open('./config.yaml') as file:
  config = yaml.load(file, Loader=SafeLoader)
    
stauth.Hasher.hash_passwords(config['credentials'])

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Login widget
authenticator.login("main", fields={'Form name': 'AISH Benefit Calculator MVP v2'})

if st.session_state['authentication_status']:
  authenticator.logout()

  # Set up the main section layout
  st.title("AISH Family Benefit Calculator")

  # Footer for the interface
  st.write("This is a simple benefit calculator for family based on employment income.")

  # Table for AISH Living Allowance for different years
  tab1, tab3, tab4 = st.tabs(["Calculator", "Decision Model", "Camunda API"])

  with tab1:
    # Section: AISH Policy Data
    st.subheader("AISH Policy Data")
    # Read-only inputs for AISH Policy Data
    aish_living_allowance = st.number_input("AISH Living Allowance (Single or Family)", value=1863.0, format="%.2f")
    child_supplement = st.number_input("Child Supplement", value=222.0, format="%.2f")
    family_employment_income_threshold = st.number_input("Family Employment Income Exemption Threshold", value=2612.0, format="%.2f")
    family_employment_exemption_max_threshold = st.number_input("Family Employment Income Max Exemption Threshold", value=2981.0, format="%.2f")

    st.subheader("Client Data")

    # Inputs for Income
    head_of_house_employment_income = st.number_input("Employment Income - Head of Household", format="%.2f")
    
    spouse_partner_employment_income = st.number_input("Employment Income - Cohabitating Partner", format="%.2f")

    # Total Income Calculation
    # total_income = employment_income + partially_exempt_income + non_exempt_income
    # st.write(f"**Total Income: ${total_income:,}**")

    def call_rest_api(family_employment_income_threshold, family_employment_exemption_max_threshold, aish_living_allowance, child_supplement, head_of_house_employment_income, spouse_partner_employment_income):
      server_url = "http://wwcamunda7.canadacentral.azurecontainer.io:8080/engine-rest/decision-definition"
      dmn_resource_id = "family_net_benefit:2:3e3bdba5-865f-11ef-bf10-00155d5e4df5"
      url = f"{server_url}/{dmn_resource_id}/evaluate"
      payload = {
        "variables": {
          "p_aish_living_allowance": {"value": aish_living_allowance, "type": "Double"},
          "p_child_supplement": {"value": child_supplement, "type": "Double"},
          "p_family_employment_income_threshold": {"value": family_employment_income_threshold, "type": "Double"},
          "p_family_employment_exemption_max_threshold": {"value": family_employment_exemption_max_threshold, "type": "Double"},
          "c_head_of_house_employment_income": {"value": head_of_house_employment_income, "type": "Double"},
          "c_spouse_partner_employment_income": {"value": spouse_partner_employment_income, "type": "Double"},
        }
      }
      response = requests.post(url, json=payload)
      if response.status_code == 200:
        result = response.json()
        # st.write("API Response:", result[0])
        estimated_benefit = result[0]['ro_family_net_benefits']['value']
        employment_employment_exemption = result[0]['ro_family_final_employment_exemption']['value']
        employment_employment_deduction = result[0]['ro_family_employment_deduction']['value']
        total_employment_income = result[0]['ro_family_total_employment_income']['value']
        
      else:
        st.error("Error in API call")
        estimated_benefit = 0
        employment_employment_exemption = 0
        employment_employment_deduction = 0
        total_employment_income = 0
      return estimated_benefit, employment_employment_exemption, employment_employment_deduction, total_employment_income

    if st.button("Calculate Benefit", key="calculate_benefit", type="primary"):
      estimated_benefit, employment_employment_exemption, employment_employment_deduction, total_employment_income = call_rest_api(family_employment_income_threshold, family_employment_exemption_max_threshold, aish_living_allowance, child_supplement, head_of_house_employment_income, spouse_partner_employment_income)
      st.divider()
      render_calculation_results(aish_living_allowance, child_supplement, employment_employment_deduction, estimated_benefit)
      
      results = {
        "Total employment income": f"${total_employment_income:,}",
        "Deduction due to employment income above exemption": f"${employment_employment_deduction:,}",
        "Employment income exemption": f"${employment_employment_exemption:,}",
      }
      with st.expander("Calculation Details"):
        st.table([{"Intermediate Item": k, "Amount": v} for k, v in results.items()])

  # with tab2:
  #   st.write("#### AISH Living Allowance")
  #   aish_data = {
  #     "Year": ["Jan 2024", "Jan 2023", "Mar 2019", "Jan 2019", "Apr 2012"],
  #     "AISH Living Allowance": ["$1,863", "$1,787", "$1,685", "$1,685", "$1,588"],
  #   }
  #   st.table(aish_data)

  #   st.write("#### Employment Income Threshold")
  #   income_exemption_data = {
  #     "Year": ["Jan 2024", "Jan 2023", "Mar 2019", "Jan 2019", "Apr 2012"],
  #     "Employment Income Threshold": ["$1,072", "$1,072", "$1,072", "$1,072", "$800"],
  #   }
  #   st.table(income_exemption_data)

  #   st.write("#### Employment Income Allowed Exemption Threshold")
  #   income_allowed_exemption_data = {
  #     "Year": ["Jan 2024", "Jan 2023", "Mar 2019", "Jan 2019", "Apr 2012"],
  #     "Employment Income Allowed Exemption Threshold": ["$1,541", "$1,541", "$1,541", "$1,541", "$1,150"],
  #   }
  #   st.table(income_allowed_exemption_data)

  #   st.write("#### Partially Exempt Income Exemption Threshold")
  #   partially_exempt_income = {
  #     "Year": ["Jan 2024", "Jan 2023", "Mar 2019", "Jan 2019", "Apr 2012"],
  #     "Partially Exempt Income Exemption Threshold": ["$300", "$300", "$300", "$300", "$200"],
  #   }
  #   st.table(partially_exempt_income)

  with tab3:
    
    st.subheader("Decision Model")
    st.image("images/DMN_v2.png", caption="Decision Model", use_column_width=True)
    
  with tab4:
    st.subheader("Camunda API - Evaluate Decision")

    st.write("### URI")
    st.code("POST http://<server-url>/engine-rest/decision-definition/<dicision-id>/evaluate", language="text")

    st.write("### Request Body")
    
    st.code('''{
      "variables": {
        "p_aish_living_allowance" : { "value" : 1863, "type" : "Double" },
        "p_child_supplement" : { "value" : 222, "type" : "Double" },
        "p_family_employment_income_threshold" : { "value" : 2612, "type" : "Double" },
        "p_family_employment_exemption_max_threshold" : { "value" : 2981, "type" : "Double" },
        "c_head_of_house_employment_income" : { "value" : 1000, "type" : "Double" },
        "c_spouse_partner_employment_income" : { "value" : 500, "type" : "Double" }
      }
    }''', language="json")

    st.write("### Response Body")
    st.code('''[
        {
        "ro_family_final_employment_exemption": {
            "type": "Double",
            "value": 1500.0,
            "valueInfo": {}
        },
        "ro_family_employment_deduction": {
            "type": "Double",
            "value": 0.0,
            "valueInfo": {}
        },
        "ro_family_total_employment_income": {
            "type": "Double",
            "value": 1500.0,
            "valueInfo": {}
        },
        "ro_family_net_benefits": {
            "type": "Double",
            "value": 2085.0,
            "valueInfo": {}
        }
      }
    ]''', language="json")
elif st.session_state['authentication_status'] is False:
  st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
  st.warning('Please enter your username and password')
  
  
