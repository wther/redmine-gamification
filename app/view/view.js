'use strict';

angular.module('redmineGamification.view', ['ngRoute'])
        .config(['$routeProvider', function ($routeProvider) {
                $routeProvider.when('/view', {
                    templateUrl: 'view/view.html',
                    controller: 'ViewCtrl'
                });
            }])

        .controller('ViewCtrl', function (gamificationService, $scope) {

            gamificationService.getData().then(function (data) {
                $scope.data = data;
            });
        });