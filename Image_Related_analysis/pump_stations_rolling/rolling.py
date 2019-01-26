df = df_4120
df_rolling = {}
for hour in ['6H','12H','24H']:
	df_rolling = df.set_index('TimeStamp').rolling(hour).mean().reset_index()
	data_plot = []
	data_plot.append(go.Scatter(x=df['TimeStamp'],y=df['Value'],name='Original value'))
	data_plot.append(go.Scatter(
						x=df_rolling['TimeStamp'],
						y=df_rolling['Value'],
						name='Rolling by '+hour))
	layout = go.Layout(
	    title='Station 4120 with ' + hour + ' mean rolling',
	    xaxis=dict(     
	        rangeslider=dict(
	            visible = True
	        ),
	        type='date'
	    ),
	    yaxis=dict(
	        title='Flow (m3/h)'
	    )
	)
	fig = dict(data=data_plot, layout=layout)
	py.iplot(fig)