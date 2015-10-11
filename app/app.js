'use strict';

angular.module('redmineGamification', [
  'ngRoute',
  'redmineGamification.directive',
  'redmineGamification.service',
  'redmineGamification.view'
]).
config(['$routeProvider', function($routeProvider) {
  $routeProvider.otherwise({redirectTo: '/view'});
}]);
