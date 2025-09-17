import streamlit as st
import boto3
import jwt
import os

USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")

def login(username, password):
    client = boto3.client("cognito-idp", region_name=REGION)
    try:
        resp = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password}
        )
        id_token = resp["AuthenticationResult"]["IdToken"]
        st.session_state["user"] = jwt.decode(id_token, options={"verify_signature": False})
        return True
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

def is_logged_in():
    return "user" in st.session_state
