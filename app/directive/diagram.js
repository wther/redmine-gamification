'use strict';

/**
 * Directive for gauge chart
 *
 * See: http://www.amcharts.com/demos/smoothed-line-chart/#
 */
angular.module("redmineGamification.directive").directive("diagram", function () {
    return {
        scope: {
            diagram: "="
        },
        link: function (scope, element) {
            element.addClass('diagramdiv');
            scope.$watch("diagram", function (newValue) {
                var chartData = [];
                for (var day in newValue) {
                    chartData.push({
                        date: day,
                        time: newValue[day]["time_points"],
                        update: newValue[day]["update_points"]
                    });
                }


                var chart = AmCharts.makeChart(element[0], {
                    "type": "serial",
                    "theme": "light",
                    "marginRight": 80,
                    "autoMarginOffset": 20,
                    "dataDateFormat": "YYYY-MM-DD HH:NN",
                    "dataProvider": chartData,
                    "valueAxes": [{
                            "axisAlpha": 0,
                            "guides": [{
                                    "fillAlpha": 0.1,
                                    "fillColor": "#888888",
                                    "lineAlpha": 0,
                                    "toValue": 16,
                                    "value": 10
                                }],
                            "position": "left",
                            "tickLength": 0,
                        }],
                    "graphs": [{
                            "balloonText": "[[category]]<br><b><span style='font-size:14px;'>Update points:[[value]]</span></b>",
                            "bullet": "round",
                            "colorField": "color",
                            "valueField": "update",
                            "lineColor": '#50a424',
                            "negativeLineColor": "#f1606d",
                            "type": "smoothedLine"
                        },{
                            "balloonText": "[[category]]<br><b><span style='font-size:14px;'>Time points:[[value]]</span></b>",
                            "bullet": "round",
                            "colorField": "color",
                            "valueField": "time",
                            "lineColor": '#30a444',
                            "negativeLineColor": "#f1653d",
                            "type": "smoothedLine"
                        }
                    ],
                    "categoryField": "date",
                    "categoryAxis": {
                        "parseDates": true,
                        "axisAlpha": 0,
                        "gridAlpha": 0.1,
                        "minorGridAlpha": 0.1,
                        "minorGridEnabled": true
                    }
                });

                chart.addListener("dataUpdated", zoomChart);

                function zoomChart() {
                    chart.zoomToDates(new Date(2012, 0, 2), new Date(2012, 0, 13));
                }
            });
        }
    };
});