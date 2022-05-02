import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.header(" Wealth Progression Experiment")

def run_experiment(initial_wealth, fast_growth_pct, slow_growth_pct):
    # num of time steps
    t_N = 60

    # num of people
    p_N = 1000

    evt_data = {}
    wealth_data = {}

    data_load_state = st.text('Running Experiment ...')

    # generate data for every individual
    for i in range(p_N):
        # start with initial amount 
        wealth = initial_wealth
        
        # generate random events of faster / slower growth for N time steps
        evts = np.random.binomial(1,sl_probability_faster_growth,size=t_N)
        
        # temp state store for interim gains
        interim_wealth = [wealth]
        
        # calc gain progression
        for e in evts:
            if e == 0:
                wealth = (wealth *(1 + slow_growth_pct/100))
            else:
                wealth = (wealth * (1 + fast_growth_pct/100))
            
            interim_wealth.append(wealth)
            
            
        # append gain data - events, gain progression, to a dictionary
        evt_data[f"p_evt_{i+1}"] = evts
        wealth_data[f"p_wealth_{i+1}"] = interim_wealth
    df_wealth = pd.DataFrame(wealth_data)
    df_wealth = df_wealth.reset_index()

    df_wealth = pd.melt(df_wealth,id_vars=['index'],var_name='Individual')
    df_ens = pd.DataFrame()
    df_ens["ens_avg"] = df_wealth.groupby(['index']).mean()
    df_end_wealth=df_wealth[(df_wealth['index']==60)]
    End_Wealth_Top75_Percentile=df_end_wealth.quantile(.75)
    End_Wealth_Maximum=df_end_wealth.quantile(1.0)    
    End_Wealth_Minimum=df_end_wealth.quantile(0.0)

    df_ens = df_ens.reset_index()

    st.subheader('Ensemble Average')
    chart1=alt.Chart(df_ens).mark_line().configure_axis(grid=False).encode(                             
    alt.X('index',title='Timestep'),
    alt.Y('ens_avg',title='Ensemble avg. at timestep')
    ).configure_view(strokeWidth=0)
    st.altair_chart(chart1,use_container_width=True)

    data_load_state.text('Experiment Completed! Rendering Visualization')
    
    
    st.subheader('End Wealth Distribution')
    chart2= alt.Chart(df_end_wealth).transform_joinaggregate(
                                 total='count(Individual)'
                               ).transform_calculate(
                                 pct='1/datum.total'
                               ).mark_bar().encode(        
                                 alt.X('value:Q',title="End Wealth (Mean marked in RED)" ,bin=alt.Bin(extent=[End_Wealth_Minimum[1],End_Wealth_Maximum[1]],step=(End_Wealth_Maximum[1]-End_Wealth_Minimum[1])/10)),                              
                                 alt.Y('sum(pct):Q',axis=alt.Axis(format='%',title='Percentage of Total Individuals',grid=False))
                                 )
                                 
   
    chart3=alt.Chart(df_end_wealth).mark_rule(color='red').encode(x="mean(value):Q")

    chart4=(chart2+chart3).configure_view(strokeWidth=0)
    st.altair_chart(chart4,use_container_width=True)

    st.subheader('Wealth Distribution Progression')
    chart5=alt.Chart(df_wealth).mark_line().encode(        
                                                 alt.X('index:O',title='Progression of Time',axis=alt.Axis(grid=False,values=[0,5,10,15,20,25,30,35,40,45,50,55,60])),
                                                 alt.Y('value',title='Wealth',axis=alt.Axis(grid=False)),
                                                 alt.Color('Individual',legend=None)
                                                  ).configure_view(strokeWidth=0)

    st.altair_chart(chart5,use_container_width=True)



sl_initial_wealth = st.sidebar.slider('Initial Wealth',1000, 1000000,1000)
sl_fast_growth_pct = st.sidebar.slider('Faster Growth %', 0.0, 100.0, 20.0,1.0)
sl_slow_growth_pct = st.sidebar.slider('Slower Growth %', -100.0, 100.0,2.0,1.0)
sl_probability_faster_growth = st.sidebar.slider('Probability of Faster Growth',0.0, 1.0,0.05)
st.write(f"""
## Experiment Parameters

* Initial Wealth = ${sl_initial_wealth}
* Faster Growth Percentage = {sl_fast_growth_pct}%
* Slower Growth Percentage = {sl_slow_growth_pct}%
* Time Steps = 60
* Number of Individuals = 1000
* Probability of Faster Growth = {sl_probability_faster_growth}
""")

if st.sidebar.button("Run Experiment"):
    run_experiment(sl_initial_wealth, sl_fast_growth_pct, sl_slow_growth_pct)

