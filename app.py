
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

def load_data(file):
    df = pd.read_csv(file)
    return df

def find_date_column(df):
    date_columns = df.select_dtypes(include=['datetime64']).columns
    if len(date_columns) > 0:
        return date_columns[0]
    
    # If no datetime column found, look for columns with 'date' in the name
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    if len(date_columns) > 0:
        return date_columns[0]
    
    # If still no date column found, return the first column as a fallback
    return df.columns[0]

def create_chart(df, x_column, y_column, annotations):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_column], y=df[y_column], mode='lines', name='Stock Price'))
    
    for ann in annotations:
        fig.add_trace(go.Scatter(
            x=[ann['x']],
            y=[ann['y']],
            mode='markers+text',
            marker=dict(
                symbol='triangle-up' if ann['label'] == 'Buy' else 'triangle-down',
                size=15,  # Increased arrow size here
                color='green' if ann['label'] == 'Buy' else 'red'
            ),
            text=[ann['label']],
            textposition='top center' if ann['label'] == 'Buy' else 'bottom center',
            showlegend=False
        ))
    
    fig.update_layout(
        title='Stock Price Chart with Buy/Sell Annotations',
        xaxis_title=x_column,
        yaxis_title=y_column,
        height=600,
        # width=1000
    )
    return fig

st.title('Interactive Stock Data Labeler')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.write(df.head())

    x_column = find_date_column(df)
    st.write(f"Automatically selected date column: {x_column}")

    y_column = st.selectbox('Select Y-axis (Price)', options=[col for col in df.columns if col != x_column])

    label_mode = st.radio("Label Mode", ('None', 'Buy', 'Sell'))

    if 'annotations' not in st.session_state:
        st.session_state.annotations = []

    fig = create_chart(df, x_column, y_column, st.session_state.annotations)

    clicked = plotly_events(fig)
    if clicked and label_mode != 'None':
        point = clicked[0]
        x, y = point['x'], point['y']
        st.session_state.annotations.append({'x': x, 'y': y, 'label': label_mode})
        st.experimental_rerun()

    # st.plotly_chart(fig)

    if st.button('Clear All Annotations'):
        st.session_state.annotations = []
        st.experimental_rerun()

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Save Buy Points'):
            buy_points = [ann for ann in st.session_state.annotations if ann['label'] == 'Buy']
            buy_df = pd.DataFrame(buy_points)
            buy_csv = buy_df.to_csv(index=False)
            st.download_button(
                label="Download Buy points as CSV",
                data=buy_csv,
                file_name="buy_points.csv",
                mime="text/csv",
            )

    with col2:
        if st.button('Save Sell Points'):
            sell_points = [ann for ann in st.session_state.annotations if ann['label'] == 'Sell']
            sell_df = pd.DataFrame(sell_points)
            sell_csv = sell_df.to_csv(index=False)
            st.download_button(
                label="Download Sell points as CSV",
                data=sell_csv,
                file_name="sell_points.csv",
                mime="text/csv",
            )
