import streamlit as st
import pandas as pd
import pickle
from catboost import CatBoostClassifier


@st.cache_resource
def load_model():
    with open('D:/vs code/Exercise/LearningPython/CreditRisk_Project/catboost_model.pkl', 'rb') as file:
        model = pickle.load(file)
    return model


def main():
    st.title(" Dự Đoán Rủi Ro Tín Dụng 🏦 ")
    st.write("Nhập thông tin của khách hàng để dự đoán khoản vay có khả năng vỡ nợ hay không")

    # Nhập thông tin cơ bản
    age = st.slider("Tuổi", min_value=20, max_value=80, value=30)
    income = st.number_input("Thu nhập hàng năm ($)", min_value=0, value=50000)
    loan_amount = st.number_input("Số tiền vay ($)", min_value=0, value=10000)
    employment_years = st.number_input("Số năm làm việc", min_value=0, max_value=50, value=5)
    loan_int_rate = st.number_input("Lãi suất khoản vay (%)", min_value=0.0, max_value=100.0, value=5.0)

    # Tính toán tỷ lệ thu nhập trên số tiền vay
    if loan_amount != 0:
        loan_percent_income = (loan_amount / income) * 100
    else:
        loan_percent_income = 0

    st.write(f"Tỷ lệ thu nhập trên số tiền vay: {loan_percent_income:.2f}%")
    cred_hist_length = st.number_input("Số năm lịch sử tín dụng", min_value=0, max_value=100, value=10)

    # Lựa chọn thông qua combobox
    home_ownership = st.selectbox(
        "Sở hữu nhà",
        options=["MORTGAGE", "OTHER", "OWN", "RENT"]
    )

    loan_intent = st.selectbox(
        "Mục đích vay",
        options=["DEBTCONSOLIDATION", "EDUCATION", "HOMEIMPROVEMENT", "MEDICAL", "PERSONAL", "VENTURE"]
    )

    loan_grade = st.selectbox(
        "Điểm tín dụng",
        options=["A", "B", "C", "D", "E", "F", "G"]
    )

    default_on_file = st.selectbox(
        "Lịch sử vỡ nợ",
        options=["N", "Y"]
    )

    # Tạo DataFrame từ đầu vào
    input_data = pd.DataFrame({
        'person_age': [age],
        'person_income': [income],
        'person_emp_length': [employment_years],
        'loan_amnt': [loan_amount],
        'loan_int_rate': [loan_int_rate],
        'loan_percent_income': [loan_percent_income],
        'cb_person_cred_hist_length': [cred_hist_length],
        'person_home_ownership': [home_ownership],
        'loan_intent': [loan_intent],
        'loan_grade': [loan_grade],
        'cb_person_default_on_file': [default_on_file]
    })

    # One-Hot Encoding các cột định tính
    input_data_encoded = pd.get_dummies(input_data)

    # Load model
    model = load_model()

    # Đảm bảo các đặc trưng phù hợp với mô hình
    expected_features = model.feature_names_
    for feature in expected_features:
        if feature not in input_data_encoded.columns:
            input_data_encoded[feature] = 0  # Thêm cột thiếu và gán giá trị 0
    input_data_encoded = input_data_encoded[expected_features]

    # Dự đoán
    if st.button("Dự Đoán"):
        prediction = model.predict(input_data_encoded)
        probability = model.predict_proba(input_data_encoded)[0]  # Lấy xác suất dự đoán

        if prediction[0] == 1:
            st.error(f"Khách hàng nằm trong nhóm nguy cơ cao vỡ nợ khoản vay (Xác suất: {probability[1]:.2%})")
        else:
            st.success(f"Khách hàng có nguy cơ thấp vỡ nợ khoản vay (Xác suất: {probability[0]:.2%})")


if __name__ == '__main__':
    main()
