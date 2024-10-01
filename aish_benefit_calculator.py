import streamlit as st
import requests

# Set up the main section layout
st.title("Single Person - Benefit Calculator")

# Footer for the interface
st.write("This is a simple benefit calculator for a single person based on inputs provided.")

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

# Estimated Benefit Calculation (Total Needs - Total Income)
# estimated_benefit = total_needs - total_income

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
  st.write(f"**Estimated Benefit Amount: ${estimated_benefit:,.2f}**")
  results = {
      "Income Exemption": f"${income_exemption:,}",
      "Employment Exemption": f"${employment_exemption:,}",
      "Total Income": f"${total_income:,}",
      "Total Needs": f"${total_needs:,}"
  }
  st.table([{"Intermediate Item": k, "Amount": v} for k, v in results.items()])
