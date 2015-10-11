'use strict';

angular.module('redmineGamification.service', []).service('gamificationService', function ($http) {
    var parseData = function (data) {

        var result = [];

        for (var userId in data["user_names"]) {
            var row = {
                "name": data["user_names"][userId],
                "days": {}
            };

            for (var day in data["points"][userId]) {
                row["days"][day] = {}
                for (var pointingType in data["points"][userId][day]) {
                    var point = data["points"][userId][day][pointingType];

                    var value = Math.round(point.sum * 100);

                    row[pointingType] = (row[pointingType] || 0) + Math.max(0.0, value);
                    row["days"][day][pointingType] = value;
                }
            }

            var today = new Date();
            today.setDate(today.getDate());
            var isoString = today.toISOString().slice(0, 10);

            if (row["days"][isoString] !== undefined) {
                row["today"] = {
                    "day": isoString,
                    "points": row["days"][isoString],
                    "reasons": data["points"][userId][isoString]
                };
            }

            result.push(row);
        }

        result.sort(function (a, b) {
            return b.update_points + b.time_points - a.update_points - a.time_points;
        });

        return result;
    };

    var getData = function (url) {
        url = url || "data/data.json";

        return $http.get(url).then(function (response) {
            return parseData(response.data);
        });
    };

    return {
        parseData: parseData,
        getData: getData
    };
});