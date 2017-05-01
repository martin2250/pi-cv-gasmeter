var apiurl = 'gasmeter.csv.php';

var graph = {};

Date.prototype.dayOfYear= function(){
    var j1= new Date(this);
    j1.setMonth(0, 0);
    return Math.round((this-j1)/8.64e7);
}

function parseDate(input)
{
	var t = input.split(/[- :]/);
	return Date.UTC(t[0], t[1]-1, t[2], t[3], t[4], t[5]);
}

function updateGraph(csv)
{
	var title = 'Gasverbrauch ' + $('#MonthInput').val() + '.' + $('#YearInput').val();
	graph.setTitle({text: title});

	var zahlerstand = [];
	var verbrauch = [];

	var lines = csv.split('\n');

	for(lineindex in lines)
	{
		var split = lines[lineindex].split(';');

		if(split.length != 2)
			continue;

		var date = parseDate(split[0]);
		var reading = parseFloat(split[1]);

		zahlerstand.push([date, reading]);
	}


	if(zahlerstand.length == 0)
	{
		graph.series[0].setData([]);
		graph.series[1].setData([]);

		alert('no data for selected time range');
		return;
	}

	var eodreadings = [];
	var eoddates = [];

	var lastDate = new Date(zahlerstand[0][0]);
	lastDate.setUTCHours(12, 0, 0, 0);
	var lastReading = zahlerstand[0][1];

	for (index in zahlerstand)
	{
		var stand = zahlerstand[index];
		var date = new Date(stand[0]);
		date.setUTCHours(12,0,0,0);
		var reading = stand[1];

		//if((date.getDate()) > lastDate.getDate())
		if((date.getUTCFullYear() * 370 + date.dayOfYear()) > (lastDate.getUTCFullYear() * 370 + lastDate.dayOfYear()))
		{
			eodreadings.push(lastReading);
			eoddates.push(lastDate);

			lastDate = date;
		}
		lastReading = reading;
	}

	eodreadings.push(lastReading);
	eoddates.push(lastDate);

	for (var i = 1; i < eodreadings.length; i++)
	{
		var diff = eodreadings[i] - eodreadings[i - 1];
		verbrauch.push([eoddates[i].getTime(), diff]);
	}

	var start = new Date(zahlerstand[0][0]);
	start.setUTCHours(0, 0, 0, 0);
	var end = new Date(zahlerstand[zahlerstand.length - 1][0]);
	end.setUTCHours(23, 59, 59, 0);

	graph.xAxis[0].setExtremes( start, end, false);

	graph.series[0].setData(zahlerstand);
	graph.series[1].setData(verbrauch);
}

function refresh()
{
	var url = apiurl + '?years=';
	url += $('#fromYearInput').val();
	url += '&months=';
	url += $('#fromMonthInput').val();
	url += '&yeare';
	url += $('#toYearInput').val();
	url += '&monthe=';
	url += $('#toMonthInput').val();

	$.get(url , function(data, status){
		if (status != 'success')
		{
			alert('could not access server: ' + status);
			return;
		}

		updateGraph(data);
	});
}

$(document).ready(function(){
	graph.chart = {
		zoomType: 'x',
		renderTo: 'graph'
	};
	graph.title = {
		text: 'Gasverbrauch 4.2017'
	};
	graph.subtitle = {
		text: document.ontouchstart === undefined ?
		'Click and drag in the plot area to zoom in' :
		'Pinch the chart to zoom in'
	};
	graph.xAxis = {
		type: 'datetime',
		minRange: 3 * 24 * 3600000 //3 days
	};
	graph.yAxis = [{
		title: { text: 'Zaehlerstand' }
	},{
		title: { text: 'Verbrauch' },
		opposite: true
	}];
	graph.legend = {
		enabled: false
	};
	graph.plotOptions = {
		area: {
			fillColor: {
				linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
				stops: [
					[0, Highcharts.getOptions().colors[0]],
					[1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
				]
			},
			marker: {
				radius: 2
			},
			lineWidth: 1,
			states: {
				hover: {
					lineWidth: 1
				}
			},
			threshold: null
		}
	};
	graph.series = [{
		type: 'area',
		name: 'Zahlerstand',
		yAxis: 0,
		zIndex: 2,
		data: []
	},{
		type: 'column',
		name: 'Verbrauch',
		yAxis: 1,
		pointRange: 1000*3600*24,
		pointPadding: 0.1,
		groupPadding: 0.1,
		data : []
	}];

	graph = new Highcharts.Chart(graph);

	var now = new Date();

	$('#toYearInput').val(now.getUTCFullYear());
	$('#toMonthInput').val(now.getUTCMonth() + 1);

	now.setMonth(now.getMonth() - 3);

	$('#fromYearInput').val(now.getUTCFullYear());
	$('#fromMonthInput').val(now.getUTCMonth() + 1);

	refresh();
});
