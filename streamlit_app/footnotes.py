import streamlit as st

def display_legend_footnotes() -> None:
    st.markdown(
        """
        <hr>
        <p style="font-size: 10px;">
        <strong>Filing Type:</strong><br>
        <strong>- A</strong> - Amended filing<br>
        <strong>- D</strong> - Derivative transaction in filing (usually option exercise)<br>
        <strong>- E</strong> - Error detected in filing<br>
        <strong>- M</strong> - Multiple transactions in filing; earliest reported transaction date and weighted average transaction price<br>
        <br>
        <strong>Trade Type</strong><br>
        <strong>- S - Sale</strong> - Sale of securities on an exchange or to another person<br>
        <strong>- S - Sale+OE</strong> - Sale of securities on an exchange or to another person (after option exercise)<br>
        <strong>- F - Tax</strong> - Payment of exercise price or tax liability using portion of securities received from the company<br>
        <strong>- P - Purchase</strong> - Purchase of securities on an exchange or from another person<br>
        </p>
        """,
        unsafe_allow_html=True
    )