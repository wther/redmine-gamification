'use strict';

/**
 * Directive for gauge chart
 *
 * See: http://www.amcharts.com/demos/angular-gauge/#
 */
angular.module("redmineGamification.directive", []).directive("chart", function () {
    return {
        scope: {
            chart: "="
        },
        link: function (scope, element) {
            element.addClass('chartdiv');
            scope.$watch("chart", function (newValue) {
                var gaugeChart = AmCharts.makeChart(element[0], {
                    "type": "gauge",
                    "theme": "light",
                    "axes": [{
                            "axisThickness": 1,
                            "axisAlpha": 0.2,
                            "tickAlpha": 0.2,
                            "valueInterval": 20,
                            "bands": [{
                                    "color": "#84b761",
                                    "endValue": 100,
                                    "startValue": 30
                                }, {
                                    "color": "#fdd400",
                                    "endValue": 30,
                                    "startValue": -20
                                }, {
                                    "color": "#cc4748",
                                    "endValue": -20,
                                    "innerRadius": "95%",
                                    "startValue": -100
                                }],
                            "bottomText": "0 pts",
                            "bottomTextYOffset": -20,
                            "startValue": -100,
                            "endValue": 100
                        }],
                    "arrows": [{}],
                    "export": {
                        "enabled": true
                    }
                });

                // Add some animation effect, by starting the gauges with offset
                setTimeout(setValue, Math.random() * 1000);

                function setValue() {
                    if (gaugeChart) {
                        if (gaugeChart.arrows) {
                            if (gaugeChart.arrows[ 0 ]) {
                                if (gaugeChart.arrows[ 0 ].setValue) {
                                    gaugeChart.arrows[ 0 ].setValue(newValue);
                                    gaugeChart.axes[ 0 ].setBottomText(newValue + " pts");
                                }
                            }
                        }
                    }
                }
            });
        }
    };
});