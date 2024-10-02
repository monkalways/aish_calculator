import streamlit as st
import requests
import os

# Set up the main section layout
st.title("Single Person - Benefit Calculator")

# Footer for the interface
st.write("This is a simple benefit calculator for a single person based on inputs provided.")

# Table for AISH Living Allowance for different years
tab1, tab2, tab3, tab4 = st.tabs(["Calculator", "AISH Policy Data Change", "Decision Model", "Camunda API"])

with tab1:
  # Section: AISH Policy Data
  st.subheader("AISH Policy Data")
  # Read-only inputs for AISH Policy Data
  aish_living_allowance = st.number_input("AISH Living Allowance", value=1863.0, format="%.2f")
  per_diem = st.number_input("Per Diem", value=426.0, format="%.2f")
  employment_income_threshold = st.number_input("Employment Income Threshold", value=1072.0, format="%.2f")
  employment_income_allowed_exemption_threshold = st.number_input("Employment Income Allowed Exemption Threshold", value=1541.0, format="%.2f")
  partially_exempt_income_threshold = st.number_input("Partially Exempt Income Threshold", value=300.0, format="%.2f")

  # Section: Income
  st.subheader("Client Data")

  # Inputs for Income
  employment_income = st.number_input("Employment Income", value=1000.0, format="%.2f")
  partially_exempt_income = st.number_input("Partially Exempt Income", value=200.0, format="%.2f")
  non_exempt_income = st.number_input("Non-Exempt Income", value=30.0, format="%.2f")

  # Total Income Calculation
  total_income = employment_income + partially_exempt_income + non_exempt_income
  st.write(f"**Total Income: ${total_income:,}**")

  def call_rest_api(employment_income_threshold, employment_income_allowed_exemption_threshold, partially_exempt_income_threshold, aish_living_allowance, per_diem, employment_income, partially_exempt_income, non_exempt_income):
    server_url = "http://wwcamunda7.canadacentral.azurecontainer.io:8080/engine-rest/decision-definition"
    dmn_resource_id = "bafdcba3-803d-11ef-bf10-00155d5e4df5"
    url = f"{server_url}/{dmn_resource_id}/evaluate"
    payload = {
      "variables": {
        "p_living_allowance": {"value": aish_living_allowance, "type": "Double"},
        "p_per_diem": {"value": per_diem, "type": "Double"},
        "p_employment_income_threshold": {"value": employment_income_threshold, "type": "Double"},
        "p_employment_income_allowed_exemption_threshold": {"value": employment_income_allowed_exemption_threshold, "type": "Double"},
        "p_pe_income_threshold": {"value": partially_exempt_income_threshold, "type": "Double"},
        "c_employment_income": {"value": employment_income, "type": "Double"},
        "c_pe_income": {"value": partially_exempt_income, "type": "Double"},
        "c_ne_income": {"value": non_exempt_income, "type": "Double"}
      }
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
      result = response.json()
      # st.write("API Response:", result[0])
      estimated_benefit = result[0]['single_person_benefit_amount']['value']
      income_exemption = result[0]['income_exemption']['value']
      employment_exemption = result[0]['employment_exemption']['value']
      total_income = result[0]['o_total_income']['value']
      total_needs = result[0]['o_total_needs']['value']
      
    else:
      st.error("Error in API call")
      estimated_benefit = 0
      income_exemption = 0
      employment_exemption = 0
      total_income = 0
      total_needs = 0
    return estimated_benefit, income_exemption, employment_exemption, total_income, total_needs

  if st.button("Calculate Benefit"):
    estimated_benefit, income_exemption, employment_exemption, total_income, total_needs = call_rest_api(employment_income_threshold, employment_income_allowed_exemption_threshold, partially_exempt_income_threshold, aish_living_allowance, per_diem, employment_income, partially_exempt_income, non_exempt_income)
    st.write("### Calculation Results")
    st.write(f"#### Estimated Benefit Amount: ${estimated_benefit:,.2f}")
    results = {
        "Income Exemption": f"${income_exemption:,}",
        "Employment Exemption": f"${employment_exemption:,}",
        "Total Income": f"${total_income:,}",
        "Total Needs": f"${total_needs:,}"
    }
    with st.expander("Show Calculation Details"):
      st.table([{"Intermediate Item": k, "Amount": v} for k, v in results.items()])

with tab2:
  st.write("#### AISH Living Allowance")
  aish_data = {
    "Year": ["Jan 2024", "Jan 2023", "Mar 2019", "Jan 2019", "Apr 2012"],
    "AISH Living Allowance": ["$1,863", "$1,787", "$1,685", "$1,685", "$1,588"],
  }
  st.table(aish_data)

  st.write("#### Employment Income Threshold")
  income_exemption_data = {
    "Year": ["Jan 2024", "Jan 2023", "Mar 2019", "Jan 2019", "Apr 2012"],
    "Employment Income Threshold": ["$1,072", "$1,072", "$1,072", "$1,072", "$800"],
  }
  st.table(income_exemption_data)

  st.write("#### Employment Income Allowed Exemption Threshold")
  income_allowed_exemption_data = {
    "Year": ["Jan 2024", "Jan 2023", "Mar 2019", "Jan 2019", "Apr 2012"],
    "Employment Income Allowed Exemption Threshold": ["$1,541", "$1,541", "$1,541", "$1,541", "$1,150"],
  }
  st.table(income_allowed_exemption_data)

  st.write("#### Partially Exempt Income Exemption Threshold")
  partially_exempt_income = {
    "Year": ["Jan 2024", "Jan 2023", "Mar 2019", "Jan 2019", "Apr 2012"],
    "Partially Exempt Income Exemption Threshold": ["$300", "$300", "$300", "$300", "$200"],
  }
  st.table(partially_exempt_income)

with tab3:
  
  st.subheader("Decision Model")

  # Get list of all images in the 'images' folder
  image_folder = "images"
  image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

  # Display each image with its filename as caption
  for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    st.image(image_path, caption=image_file, use_column_width=True)
  
with tab4:
  st.subheader("Camunda API - Evaluate Decision")

  st.write("### URI")
  st.code("POST http://<server-url>/engine-rest/decision-definition/<dicision-id>/evaluate", language="text")

  st.write("### Request Body")
  
  st.code('''{
    "variables": {
      "p_living_allowance": {"value": 1863, "type": "Double"},
      "p_per_diem": {"value": 426, "type": "Double"},
      "p_employment_income_threshold": {"value": 1072, "type": "Double"},
      "p_employment_income_allowed_exemption_threshold": {"value": 1541, "type": "Double"},
      "p_pe_income_threshold": {"value": 300, "type": "Double"},
      "c_employment_income": {"value": 1000, "type": "Double"},
      "c_pe_income": {"value": 200, "type": "Double"},
      "c_ne_income": {"value": 30, "type": "Double"}
    }
  }''', language="json")

  st.write("### Response Body")
  st.code('''[
      {
          "income_exemption": {
              "type": "Double",
              "value": 200.0,
              "valueInfo": {}
          },
          "o_total_income": {
              "type": "Double",
              "value": 1230.0,
              "valueInfo": {}
          },
          "employment_exemption": {
              "type": "Double",
              "value": 1000.0,
              "valueInfo": {}
          },
          "o_total_needs": {
              "type": "Double",
              "value": 2637.0,
              "valueInfo": {}
          },
          "single_person_benefit_amount": {
              "type": "Double",
              "value": 1407.0,
              "valueInfo": {}
          }
      }
  ]''', language="json")

