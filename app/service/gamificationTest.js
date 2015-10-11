'use strict';

describe('redmineGamification.service gamification', function () {
    beforeEach(module('redmineGamification.service'));

    it('should return array with user points daily and in total', inject(function (gamificationService) {

        // Arrange
        var data = {
            "points": {
                "1": {}
            },
            "user_names": {
                "1": "John Doe"
            }
        };

        var date = new Date().toISOString().slice(0, 10);
        data.points[1][date] = {
            "time_points": {
                "reasons": [
                    "Penalty for logging more than 8 hours",
                    "Reward for logging time on multiple issues"
                ],
                "sum": 0.7084745762711865
            },
            "update_points": {
                "reasons": [
                    "Reward for attaching files",
                    "Reward for nicely formatted comments",
                    "Reward for being a story teller"
                ],
                "sum": 0.47892156862745094
            }
        };

        // Act
        var result = gamificationService.parseData(data);

        // Assert
        expect(result instanceof Array).toBe(true);
        expect(result.length).toBe(1);
        expect(result[0].name).toBe("John Doe");
        expect(result[0].days).toBeDefined();
        expect(Object.keys(result[0].days)).toContain(date);
        expect(result[0].update_points).toBeDefined();
        expect(result[0].update_points).toBeCloseTo(48);
        expect(result[0].days[date]["update_points"]).toBeCloseTo(48);
    }));

    it('should ignore absent days when calculating sum', inject(function (gamificationService) {

        // Arrange
        var data = {
            "points": {
                1: {}
            },
            "user_names": {
                "1": "John Doe"
            }
        };

        var date = new Date().toISOString().slice(0, 10);
        data["points"][1][date] = {
            "time_points": {sum: -1},
            "update_points": {sum: -1},
        };

        // Act
        var result = gamificationService.parseData(data);

        // Assert
        expect(result[0].update_points).toBeCloseTo(0);
    }));
});