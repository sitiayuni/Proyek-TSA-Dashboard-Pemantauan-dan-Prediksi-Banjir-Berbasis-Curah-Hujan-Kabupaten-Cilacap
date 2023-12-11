import streamlit as st
from streamlit_option_menu import option_menu

import home, forecast, predict, about

st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)
    
class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        # Sidebar
        with st.sidebar:        
            app = option_menu(
                menu_title='Dashboard',
                options=['Home','Forecast','Prediction','About'],
                icons=['house-fill','cloud-lightning-rain-fill','bi-water','info-circle-fill'],
                menu_icon='bi-cast',
                default_index=0,
                styles={
                        "container": {"padding": "5!important","background-color":'black'},
                        "icon": {"color": "white", "font-size": "23px"}, 
                        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
                        "nav-link-selected": {"background-color": "#02ab21"},}
                )

        # Menu
        if app == "Home":
            home.app()
        if app == "Forecast":
            forecast.app()    
        if app == "Prediction":
            predict.app()        
        if app == 'About':
            about.app()     
             
          
             
    run()            