import streamlit as st
import pandas as pd
import altair as alt

st.title("🏡 Mortgage Calculator")

def calculate_monthly_payment(loan_amount: float, annual_interest_rate: float, loan_term_years: int) -> float:
    """
    Calculate the monthly payment using the PMT formula.
    """
    monthly_rate = (annual_interest_rate / 100) / 12
    num_payments = loan_term_years * 12
    if monthly_rate > 0:
        payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    else:
        payment = loan_amount / num_payments
    return payment

def generate_amortization_schedule(loan_amount: float, monthly_rate: float, num_payments: int, monthly_payment: float) -> pd.DataFrame:
    """
    Generate an amortization schedule as a DataFrame.
    """
    schedule = []
    balance = loan_amount
    for month in range(1, num_payments + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        # Correct small rounding errors on the final payment
        if balance < 1e-5:
            balance = 0
        schedule.append({
            "Month": month,
            "Payment": monthly_payment,
            "Interest": interest_payment,
            "Principal": principal_payment,
            "Balance": balance
        })
    return pd.DataFrame(schedule)

# User Inputs in two columns
col1, col2 = st.columns(2)
with col1:
    loan_amount = st.number_input("Loan Amount ($)", min_value=0.0, value=200000.0, step=1000.0)
    loan_term = st.number_input("Loan Term (years)", min_value=1, value=30, step=1)
with col2:
    interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=5.0, step=0.1)

# Calculation values
monthly_rate = (interest_rate / 100) / 12
num_payments = int(loan_term * 12)
monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, loan_term)

# Display Summary Results
st.markdown("### 💰 Monthly Payment")
st.success(f"${monthly_payment:,.2f}")

total_paid = monthly_payment * num_payments
total_interest = total_paid - loan_amount

st.markdown("### 🏠 Total Cost of Home After All Payments")
st.success(f"${total_paid:,.2f}")

st.markdown("### 📉 Total Interest Paid Over Loan Term")
st.success(f"${total_interest:,.2f}")

# Generate Amortization Schedule
df_schedule = generate_amortization_schedule(loan_amount, monthly_rate, num_payments, monthly_payment)

# Expandable Amortization Table
with st.expander("View Amortization Schedule"):
    st.dataframe(df_schedule.style.format({
        "Payment": "${:,.2f}",
        "Interest": "${:,.2f}",
        "Principal": "${:,.2f}",
        "Balance": "${:,.2f}"
    }))

# Chart: Principal and Interest Over Time
st.markdown("### 📈 Principal & Interest Over Time")
df_melted = df_schedule.melt(id_vars=["Month"], value_vars=["Principal", "Interest"], 
                             var_name="Payment Type", value_name="Amount")

chart = alt.Chart(df_melted).mark_line().encode(
    x=alt.X("Month", title="Month"),
    y=alt.Y("Amount", title="Amount ($)"),
    color=alt.Color("Payment Type", title="Payment Type"),
    tooltip=["Month", "Payment Type", alt.Tooltip("Amount", format="$.2f")]
).properties(
    width=900,
    height=450,
    title="Principal vs. Interest Over Time"
)
st.altair_chart(chart, use_container_width=True)

# Option to download the amortization schedule as CSV
st.download_button(
    label="Download Amortization Schedule as CSV",
    data=df_schedule.to_csv(index=False),
    file_name='amortization_schedule.csv',
    mime='text/csv'
)
