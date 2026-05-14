import os
import streamlit as st
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier

DATA_PATH = 'CSI_7_MAL_2324_CW_resit_data(Data).csv'
MODEL_PATH = 'models/top_features_model.pkl'
TARGET_COLUMN = 'Test_data'

IMPORTANT_FEATURES = [
    'Age',
    'Ventricles',
    'Volume (Cortical Parcellation) of LeftPosteriorCingulate',
    'Cortical Thickness Standard Deviation of LeftSuperiorFrontal',
    'Volume (Cortical Parcellation) of LeftCaudalMiddleFrontal',
    'Cortical Thickness Standard Deviation of LeftParsTriangularis',
    'Surface Area of LeftParahippocampal',
    'Cortical Thickness Standard Deviation of LeftSupramarginal',
    'Surface Area of LeftIsthmusCingulate',
    'Cortical Thickness Standard Deviation of LeftFrontalPole',
]


def clean_numeric_series(series):
    return pd.to_numeric(series.astype(str).str.replace(',', '').str.strip(), errors='coerce')


def prepare_features(df):
    df = df.copy()
    for col in df.columns:
        df[col] = clean_numeric_series(df[col])
        df[col] = df[col].fillna(df[col].mean())
    return df


def load_or_train_model(data_df):
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as file:
            return pickle.load(file)

    train_df = prepare_features(data_df[IMPORTANT_FEATURES])
    target = data_df[TARGET_COLUMN]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(train_df, target)

    with open(MODEL_PATH, 'wb') as file:
        pickle.dump(model, file)

    return model


# Load the dataset
data_df = pd.read_csv(DATA_PATH)

# Load or train the simplified model
model = load_or_train_model(data_df)

# Streamlit UI
st.title("Alzheimer's Disease Detection")

st.write("This app uses the top 10 most important features for prediction.")

# Add background image CSS
st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://via.placeholder.com/1920x1080/87CEEB/000000?text=Medical+Background');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create form
with st.form("prediction_form"):
    inputs = {}
    cols = st.columns(3)

    for i, feature in enumerate(IMPORTANT_FEATURES):
        col = cols[i % 3]
        min_val = float(clean_numeric_series(data_df[feature]).min())
        max_val = float(clean_numeric_series(data_df[feature]).max())
        mean_val = float(clean_numeric_series(data_df[feature]).mean())

        inputs[feature] = col.number_input(
            f"{feature}",
            min_value=min_val,
            max_value=max_val,
            value=mean_val,
            step=(max_val - min_val) / 100 if max_val != min_val else 0.01,
        )

    submitted = st.form_submit_button("Predict")

# Prediction
if submitted:
    try:
        input_df = pd.DataFrame([inputs])
        processed_df = prepare_features(input_df)
        prediction = model.predict(processed_df)[0]

        if prediction == 0:
            result = "Normal"
        else:
            result = "Alzheimer's Disease"

        st.success(f"Prediction: {result}")
    except Exception as e:
        st.error(f"Error: {e}")